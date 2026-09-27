#!/usr/bin/env python3
import json, os, subprocess, sys, tempfile, unittest

GUARD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "git-guard.py")

BLOCKED = [
    "git push --force origin main",
    "cd x && git push -f origin main",
    "git reset --hard HEAD~1",
    'bash -c "git push --force origin main"',
    "sh -c 'git reset --hard'",
    "sudo sh -c 'git clean -fdx'",
    'eval "git reset --hard"',
    'bash -c "git commit -m \\"wip\\" && git push --force origin main"',
    "(git push --force origin main)",
    "{ git reset --hard; }",
    "`git clean -fdx`",
    "echo $(git reset --hard)",
    'echo "$(git reset --hard)"',
    "command git push --force origin main",
    "exec git reset --hard",
    "nohup git push --force origin main",
    "time git reset --hard",
    "timeout 60 git push --force origin main",
    "nice -n 5 git reset --hard",
    "sudo git reset --hard",
    "env GIT_TRACE=1 git reset --hard",
    "GIT_TRACE=1 git reset --hard",
    "/usr/bin/git push --force origin main",
    "eval git push --force origin main",
    "echo x | xargs git push --force origin main",
    "if true; then git reset --hard; fi",
    "for b in a; do git push --force origin $b; done",
    "true & git reset --hard",
    "git push \\\n  --force origin main",
    "git push --force-with-lease origin main",
    'bash -c "git push --force-with-lease origin main"',
]

ALLOWED = [
    'echo "git push --force"',
    'git commit -m "docs: explain git push --force"',
    'git commit -m "docs: explain \\`git reset --hard\\`"',
    "git commit -m 'docs: explain `git reset --hard`'",
    "cat > notes.md <<'EOF'\nNever run git reset --hard here.\nEOF",
    "git commit -m \"$(cat <<'EOF'\ndocs: explain git reset --hard\nEOF\n)\"",
    'grep -n "reset --hard" hooks/git-guard.py',
    'bash -c "echo hi"',
    "git status",
    "git push origin my-branch",
    "git push --force-with-lease origin my-branch",
    'bash -c "git push --force-with-lease origin my-branch"',
]

AI_TRAILER_COMMIT = 'git commit -m "fix: x\n\nCo-authored-by: Claude <noreply@anthropic.com>"'


def decision(command, **env):
    payload = json.dumps({"tool_input": {"command": command}, "cwd": tempfile.gettempdir()})
    base = {k: v for k, v in os.environ.items() if k != "KEEL_BLOCK_AI_TRAILERS"}
    out = subprocess.run([sys.executable, GUARD], input=payload, capture_output=True, text=True,
                         env={**base, **env}, check=True).stdout
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out.strip() else "allow"


class GitGuardTest(unittest.TestCase):
    def test_blocks_destructive_git_through_shell_wrappers(self):
        for command in BLOCKED:
            with self.subTest(command=command):
                self.assertEqual(decision(command), "deny")

    def test_allows_safe_git_and_prose_that_mentions_it(self):
        for command in ALLOWED:
            with self.subTest(command=command):
                self.assertEqual(decision(command), "allow")

    def test_blocks_ai_trailer_only_when_opted_in(self):
        self.assertEqual(decision(AI_TRAILER_COMMIT), "allow")
        self.assertEqual(decision(AI_TRAILER_COMMIT, KEEL_BLOCK_AI_TRAILERS="1"), "deny")


if __name__ == "__main__":
    unittest.main()
