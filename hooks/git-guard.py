#!/usr/bin/env python3
"""PreToolUse guard for Bash. Adapted from mattpocock/skills git-guardrails-claude-code (MIT).
Local edits: only real git command segments are inspected (not prose or heredoc bodies that mention git);
plain push and branch -D stay allowed; destructive working-tree and history ops are blocked.
keel edit: `--force-with-lease` is allowed onto a branch that is not protected (the owner publishing its own
rebased branch, as pstack's Autopilot owners do); every other force-push stays blocked. Blocking AI attribution
trailers in commit messages is opt-in: set KEEL_BLOCK_AI_TRAILERS=1."""
import json, os, re, subprocess, sys

try:
    hook_input = json.load(sys.stdin)
    cmd = hook_input.get("tool_input", {}).get("command", "")
    hook_cwd = hook_input.get("cwd") or None
except Exception:
    sys.exit(0)

# drop heredoc bodies
lines, out, term = cmd.split("\n"), [], None
for l in lines:
    if term is not None:
        if l.strip() == term:
            term = None
        continue
    m = re.search(r"<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?", l)
    out.append(l)
    if m:
        term = m.group(1)
text = "\n".join(out)

def deny(msg):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": "deny", "permissionDecisionReason": msg}}))
    sys.exit(0)

# Attribution trailers: inspected on segments that ARE a `git commit` (raw, quotes intact, since the trailer
# lives inside the -m message). Commands that merely mention the trailer (tests, docs) start with something else.
if os.environ.get("KEEL_BLOCK_AI_TRAILERS", "").lower() in ("1", "true", "on", "yes"):
    # Check the raw command, heredoc bodies included: a commit message often arrives through one.
    if re.search(r"(^|[\s;&|(])git\s+(-C\s+\S+\s+)?commit\b", cmd) and re.search(r"Co-authored-by:\s*(Codex|Claude)|Generated with \[?(Codex|Claude Code)", cmd, re.I):
        deny("commit message carries an AI attribution trailer; commit again without it (KEEL_BLOCK_AI_TRAILERS is on)")

PROTECTED = re.compile(r"^(main|master|trunk|develop|release([/-].*)?)$")
FORCE_BLOCKED = "force-push is blocked; add a commit instead. Only --force-with-lease onto your own non-main branch is allowed"

def current_branch(cwd):
    try:
        r = subprocess.run(["git", "-C", cwd or ".", "rev-parse", "--abbrev-ref", "HEAD"],
                           capture_output=True, text=True, timeout=2)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""

def push_violation(args):
    """None when the push is allowed, else the reason to deny it."""
    m = re.search(r"(?:^|\s)push\b(.*)$", args)
    if not m:
        return None
    rest = m.group(1)
    if re.search(r"(^|\s)(--force(?![-\w])|-f\b|--mirror\b|\+\S)", rest):
        return FORCE_BLOCKED
    if not re.search(r"--force-with-lease|--force-if-includes", rest):
        return None
    cwd_flag = re.search(r"(?:^|\s)-C\s+(\S+)", args[: m.start()])
    cwd = cwd_flag.group(1) if cwd_flag else hook_cwd
    positional = [t for t in rest.split() if not t.startswith("-")]
    dests = [t.split(":")[-1].removeprefix("refs/heads/") for t in positional[1:]]
    dests = [current_branch(cwd) if d in ("", "HEAD") else d for d in dests] or [current_branch(cwd)]
    if not all(dests) or any(PROTECTED.match(d) for d in dests):
        return FORCE_BLOCKED
    return None

RULES = [
    (r"reset\s+--hard", "destructive reset is blocked; use git stash or a new branch"),
    (r"clean\s+-\w*f", "git clean with -f is blocked"),
    (r"(checkout|restore)\s+(--\s+)?\.\s*$", "discarding the whole working tree is blocked; restore specific paths"),
    (r"filter-(branch|repo)\b", "history rewriting is blocked in agent sessions; the human does this deliberately"),
]

RUNS_AS_CODE = r"(?<![\w-])(?:\w*sh\s+(?:-\w+\s+)*-\w*c|eval)\s+"
QUOTED = re.compile(rf"""\\.|({RUNS_AS_CODE})?(?:'([^'\n]*)'|"((?:\\.|[^"\\\n])*)")""")
SUBSTITUTION = re.compile(r"\$\(([^)]*)\)|`([^`]*)`")
SEPARATORS = re.compile(r"[\n;&|(){}`]")
GIT = re.compile(r"(?:^|\s)(?:\S*/)?git\s+(.*)")

def git_args(text) -> list[str]:
    nested = []

    def blank_prose_collect_code(quoted):
        runs_as_code, single, double = quoted.groups()
        if runs_as_code:
            nested.append(single if single is not None else re.sub(r'\\([\\"$`])', r"\1", double))
        elif double:
            nested.extend(a or b for a, b in SUBSTITUTION.findall(re.sub(r"\\.", "", double)))
        return "''"

    unquoted = QUOTED.sub(blank_prose_collect_code, text.replace("\\\n", " "))
    found = [m.group(1) for seg in SEPARATORS.split(unquoted) if (m := GIT.search(seg))]
    return found + [args for code in nested for args in git_args(code)]

for args in git_args(text):
    reason = push_violation(args)
    if reason:
        deny(reason)
    for pat, msg in RULES:
        if re.search(pat, args):
            deny(msg)
sys.exit(0)
