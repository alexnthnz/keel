#!/usr/bin/env python3
"""PreToolUse guard for Bash. Adapted from mattpocock/skills git-guardrails-claude-code (MIT).
Local edits: only real git command segments are inspected (not prose or heredoc bodies that mention git);
plain push and branch -D stay allowed; destructive working-tree and history ops are blocked.
Blocking AI attribution trailers in commit messages is opt-in: set KEEL_BLOCK_AI_TRAILERS=1."""
import json, os, re, sys
from collections import namedtuple

try:
    cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
except Exception:
    sys.exit(0)

def deny(msg):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": "deny", "permissionDecisionReason": msg}}))
    sys.exit(0)

METACHARACTERS = " \t\n;&|()<>"
PLAIN = re.compile(r"""[^%s\\'"$`]+""" % re.escape(METACHARACTERS))
REDIRECT = re.compile(r"&>>?|<<<|<<-?|<>|[<>]&|>>|>\||[<>](?!\()")
PLAIN_UNTIL = {end: re.compile(r"[^\\$`%s]+" % re.escape(end or "")) for end in ('"', "}", None)}

class Scanner:
    def __init__(self, src, out):
        self.s, self.i, self.out = src, 0, out

    def commands(self, closer=False):
        s, argv, stdin, heredocs, depth = self.s, [], [], [], 0

        def end():
            nonlocal argv, stdin
            if argv:
                self.out.append((argv, stdin))
            argv, stdin = [], []

        while self.i < len(s):
            c = s[self.i]
            if c in " \t":
                self.i += 1
            elif s.startswith("\\\n", self.i):
                self.i += 2
            elif c == "#":
                j = s.find("\n", self.i)
                self.i = len(s) if j < 0 else j
            elif c == "\n":
                self.i += 1
                end()
                self.read_heredocs(heredocs)
                heredocs = []
            elif m := REDIRECT.match(s, self.i):
                self.i = m.end()
                while s[self.i:self.i + 1] in (" ", "\t"):
                    self.i += 1
                target, quoted = self.word()
                if m.group() == "<<<":
                    stdin.append(target)
                elif m.group().startswith("<<"):
                    heredocs.append((target, quoted, m.group() == "<<-", stdin))
            elif c == "(":
                end()
                depth += 1
                self.i += 1
            elif c == ")":
                end()
                self.i += 1
                if depth == 0 and closer:
                    return
                depth -= 1
            elif c in ";&|":
                end()
                self.i += 1
            else:
                word, _ = self.word()
                if not (word.isdigit() and s[self.i:self.i + 1] in ("<", ">")):
                    argv.append(word)
        end()

    def word(self):
        s, buf, quoted = self.s, [], False
        while self.i < len(s):
            c = s[self.i]
            if s.startswith(("<(", ">("), self.i):
                buf.append(self.expansion())
            elif c in METACHARACTERS:
                break
            elif c == "\\":
                if s[self.i + 1:self.i + 2] != "\n":
                    buf.append(s[self.i + 1:self.i + 2])
                    quoted = True
                self.i += 2
            elif c == "'":
                j = s.find("'", self.i + 1)
                j = len(s) if j < 0 else j
                buf.append(s[self.i + 1:j])
                self.i, quoted = j + 1, True
            elif c == '"':
                self.i += 1
                buf.append(self.double_quoted('"'))
                quoted = True
            elif s.startswith("$'", self.i):
                j = self.skip_escaped(self.i + 2, "'")
                buf.append(s[self.i + 2:j].encode("latin-1", "backslashreplace").decode("unicode_escape", "replace"))
                self.i, quoted = j + 1, True
            elif c in "$`":
                buf.append(self.expansion())
            else:
                m = PLAIN.match(s, self.i)
                buf.append(m.group())
                self.i = m.end()
        return "".join(buf), quoted

    def double_quoted(self, end):
        s, buf, plain = self.s, [], PLAIN_UNTIL[end]
        while self.i < len(s) and s[self.i] != end:
            c = s[self.i]
            if c == "\\":
                nxt = s[self.i + 1:self.i + 2]
                buf.append(nxt if nxt in ("$", "`", '"', "\\") else "" if nxt == "\n" else c + nxt)
                self.i += 2
            elif c in "$`":
                buf.append(self.expansion())
            else:
                m = plain.match(s, self.i)
                buf.append(m.group())
                self.i = m.end()
        self.i += 1
        return "".join(buf)

    def expansion(self):
        s, start = self.s, self.i
        if s.startswith(("$(", "<(", ">("), start):
            self.i += 2
            self.commands(closer=True)
        elif s.startswith("${", start):
            self.i += 2
            self.double_quoted("}")
        elif s[start] == "`":
            self.i = self.skip_escaped(start + 1, "`")
            Scanner(re.sub(r"\\([$`\\])", r"\1", s[start + 1:self.i]), self.out).commands()
            self.i += 1
        else:
            self.i += 1
        return s[start:self.i]

    def skip_escaped(self, start, closer):
        return re.compile(r"[^\\%s]*(?:\\.[^\\%s]*)*" % (closer, closer), re.S).match(self.s, start).end()

    def read_heredocs(self, heredocs):
        for delimiter, quoted, strip_tabs, stdin in heredocs:
            line = re.compile("^" + r"\t*" * strip_tabs + re.escape(delimiter) + "$", re.M).search(self.s, self.i)
            stdin.append(self.s[self.i:line.start() - 1 if line else len(self.s)])
            self.i = line.end() + 1 if line else len(self.s)
            if not quoted:
                Scanner(stdin[-1], self.out).double_quoted(None)

SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "mksh", "ash", "yash", "fish", "csh", "tcsh"}
LAUNCHERS = SHELLS | {"git", "eval", "su"}
# Each launcher word rescans the words after it, so a cap keeps one command's cost linear.
MAX_LAUNCHERS = 32

def after_c(word):
    return word[word.index("c") + 1:] if word[:1] == "-" and word[1:2] != "-" and "c" in word else None

def shell_command(args):
    has_c, j = False, 0
    while j < len(args):
        a = args[j]
        j += 1
        if a in ("-", "--"):
            break
        if a in ("--rcfile", "--init-file"):
            j += 1
        elif a[:1] in "-+" and len(a) > 1:
            has_c = has_c or after_c(a) is not None
            if a[1:].isalpha():
                j += a.count("o") + a.count("O")
        else:
            j -= 1
            break
    return args[j] if has_c and j < len(args) else None

def su_command(args):
    for j, a in enumerate(args):
        text = a.partition("=")[2] if a.startswith("--command") else after_c(a)
        if text is not None:
            return text or next(iter(args[j + 1:]), "")
    return None

def git_invocations(src):
    out, found = [], []
    Scanner(src, out).commands()
    for argv, stdin in out:
        names = [os.path.basename(word) for word in argv]
        if sum(name in LAUNCHERS for name in names) > MAX_LAUNCHERS:
            deny("the command has too many git or shell words for the git guard to check")
        scripts = []
        for k, name in enumerate(names):
            if name not in LAUNCHERS:
                continue
            rest = argv[k + 1:]
            if name == "git":
                found.append((rest, stdin))
            # eval over plain words parses back to the same words, which this loop already scans; reparsing
            # only quoted or expanded words keeps eval chains linear.
            elif name == "eval" and not all(PLAIN.fullmatch(w) and w[0] != "#" for w in rest):
                scripts.append(" ".join(rest))
                break
            elif name != "eval":
                code = su_command(rest) if name == "su" else shell_command(rest)
                scripts += stdin if code is None else [code]
        for script in dict.fromkeys(scripts):
            found += git_invocations(script)
    return found

GLOBAL_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env", "--super-prefix"}
# The options the rules read: each entry lists its spellings, canonical name last, and ends in "=" when it takes a value.
OPTIONS = {
    "push": ["-f --force", "-d --delete", "--mirror", "--all", "--branches", "--tags", "--force-with-lease", "--force-if-includes",
             "--repo=", "-o --push-option=", "--receive-pack=", "--exec="],
    "reset": ["--hard"],
    "clean": ["-f --force", "-e --exclude="],
    "checkout": ["-f --force", "-b=", "-B=", "--orphan="],
    "switch": ["-f --force", "--discard-changes", "-c --create=", "-C --force-create=", "--orphan="],
    "restore": ["-W --worktree", "-S --staged", "-s --source="],
}
Git = namedtuple("Git", "sub opts operands text")

def parse_git(args, stdin):
    j = 0
    while j < len(args) and args[j].startswith("-"):
        j += 2 if args[j] in GLOBAL_OPTS_WITH_VALUE else 1
    sub = args[j] if j < len(args) else None
    spellings = {name: (option.rstrip("=").split()[-1], option.endswith("="))
                 for option in OPTIONS.get(sub, []) for name in option.rstrip("=").split()}
    opts, operands, rest = set(), [], iter(args[j + 1:])
    for a in rest:
        if a == "--":
            operands += rest
        elif a.startswith("--"):
            name = a.partition("=")[0]
            meant = [spellings[name]] if name in spellings else \
                [spellings[n] for n in spellings if n.startswith(name) and n.startswith("--") and len(name) > 2]
            opts.update(canonical for canonical, _ in meant or [(name, False)])
            if len(meant) == 1 and meant[0][1] and "=" not in a:
                next(rest, None)
        elif a.startswith("-") and len(a) > 1:
            for k, ch in enumerate(a[1:], 2):
                canonical, takes_value = spellings.get("-" + ch, ("-" + ch, False))
                opts.add(canonical)
                if takes_value:
                    if k == len(a):
                        next(rest, None)
                    break
        else:
            operands.append(a)
    return Git(sub, opts, operands, "\n".join(args + stdin))

PROTECTED = re.compile(r"main|master|trunk|develop|release.*")
BRANCH = re.compile(r"[\w.-]+(/[\w.-]+)*")
FORCE_BLOCKED = ("force-push is blocked; add a commit instead. Only --force-with-lease onto a named branch that is not "
                 "protected is allowed, as in git push --force-with-lease origin <branch>")
DELETE_BLOCKED = "deleting a protected branch on the remote is blocked; the human does this deliberately"
WHOLE_TREE = {".", "./", ":/", "*"}
DISCARD = "discarding the whole working tree is blocked; restore specific paths"
HISTORY = "history rewriting is blocked in agent sessions; the human does this deliberately"
TRAILER = re.compile(r"Co-authored-by\s*[:=]\s*(Codex|Claude)|Generated with \[?(Codex|Claude Code)", re.I)
block_trailers = os.environ.get("KEEL_BLOCK_AI_TRAILERS", "").lower() in ("1", "true", "on", "yes")

def named_branch(dest):
    return bool(BRANCH.fullmatch(dest)) and dest != "HEAD" and not dest.startswith("refs/") \
        and not PROTECTED.fullmatch(dest)

def push_rule(git):
    if git.opts & {"--force", "--mirror"} or any(p.startswith("+") for p in git.operands):
        return FORCE_BLOCKED
    refspecs = git.operands if "--repo" in git.opts else git.operands[1:]
    dests = [r.split(":")[-1].removeprefix("refs/heads/") for r in refspecs]
    deleted = dests if "--delete" in git.opts else [d for r, d in zip(refspecs, dests) if r.startswith(":")]
    if any(PROTECTED.fullmatch(d) for d in deleted):
        return DELETE_BLOCKED
    if not git.opts & {"--force-with-lease", "--force-if-includes"}:
        return None
    if git.opts & {"--all", "--branches", "--tags"} or not dests or not all(map(named_branch, dests)):
        return FORCE_BLOCKED
    return None

RULES = {
    "push": push_rule,
    "reset": lambda git: "destructive reset is blocked; use git stash or a new branch" if "--hard" in git.opts else None,
    "clean": lambda git: "git clean with -f is blocked" if "--force" in git.opts else None,
    "checkout": lambda git: DISCARD if "--force" in git.opts or WHOLE_TREE & set(git.operands) else None,
    "switch": lambda git: DISCARD if git.opts & {"--force", "--discard-changes"} else None,
    "restore": lambda git: DISCARD if WHOLE_TREE & set(git.operands) and
                           ("--worktree" in git.opts or "--staged" not in git.opts) else None,
    "filter-branch": lambda git: HISTORY,
    "filter-repo": lambda git: HISTORY,
    "commit": lambda git: "commit message carries an AI attribution trailer; commit again without it "
                          "(KEEL_BLOCK_AI_TRAILERS is on)" if block_trailers and TRAILER.search(git.text) else None,
}

try:
    invocations = git_invocations(cmd)
except RecursionError:
    deny("the command nests too deeply for the git guard to check")
for args, stdin in invocations:
    git = parse_git(args, stdin)
    reason = RULES.get(git.sub, lambda git: None)(git)
    if reason:
        deny(reason)
sys.exit(0)
