#!/usr/bin/env python3
import json, os, subprocess, sys, tempfile, unittest

GUARD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "git-guard.py")

FORCE, RESET, CLEAN = "force-push", "destructive reset", "git clean"
DISCARD, HISTORY, TRAILER = "whole working tree", "history rewriting", "attribution trailer"
DELETE = "deleting a protected branch"

DENIED = {
    FORCE: [
        "git push --force origin main",
        "cd x && git push -f origin main",
        'bash -c "git push --force origin main"',
        'bash -c "git commit -m \\"wip\\" && git push --force origin main"',
        "(git push --force origin main)",
        "command git push --force origin main",
        "nohup git push --force origin main",
        "timeout 60 git push --force origin main",
        "arch -arm64 git push --force origin main",
        "/usr/bin/git push --force origin main",
        "eval git push --force origin main",
        "echo x | xargs git push --force origin main",
        "for b in a; do git push --force origin $b; done",
        "git push \\\n  --force origin main",
        "# don't force-push\ngit push --force origin main\n# it's blocked",
        'echo "see <<EOF"\ngit push --force origin main',
        "git push \\--force origin main",
        "git push -uf origin main",
        "git push -fu origin main",
        "git push -vf origin main",
        "git push -fn origin main",
        "git push origin +main",
        "git push --mirror origin",
        "git push --force-with-lease origin main",
        'bash -c "git push --force-with-lease origin main"',
        "git push --force-with-lease --all origin",
        "git push --force-with-lease --branches origin",
        "git push --force-with-lease --mirror origin",
        "git push --force-with-lease origin 'refs/heads/*:refs/heads/*'",
        "git push --force-with-lease --repo=origin HEAD:main",
        "git push --force-with-lease origin",
        "git push --force-with-lease origin releases",
        'git push --force-with-lease origin "$(git branch --show-current)"',
    ],
    RESET: [
        "git reset --hard HEAD~1",
        "git reset -q --hard HEAD~1",
        "git reset --har",
        "git reset --h HEAD~1",
        "sudo -u git -H git reset --hard",
        'sudo -u git sh -c "git reset --hard"',
        "eval eval eval git reset --hard",
        "sh -c 'git reset --hard'",
        'eval "git reset --hard"',
        'eval "git reset" "--hard"',
        "{ git reset --hard; }",
        "echo $(git reset --hard)",
        'echo "$(git reset --hard)"',
        'out="$(git -C "$repo" reset --hard)"',
        'echo "$(echo $(true); git reset --hard)"',
        "diff <(git reset --hard) /dev/null",
        "git reset <(true) --hard",
        'echo "${x:-$(git reset --hard)}"',
        "exec git reset --hard",
        "time git reset --hard",
        "nice -n 5 git reset --hard",
        "sudo git reset --hard",
        "env GIT_TRACE=1 git reset --hard",
        "GIT_TRACE=1 git reset --hard",
        "if true; then git reset --hard; fi",
        "true & git reset --hard",
        "git reset --\\hard",
        "git rese\\t --hard",
        "g\\it reset --hard",
        "'/usr/bin/git' reset --hard",
        "# <<EOF\ngit reset --hard",
        "bash <<'EOF'\ngit reset --hard\nEOF",
        "sh -s <<EOF\ngit reset --hard\nEOF",
        "cat <<EOF\n$(git reset --hard)\nEOF",
        "cat <<123\n`git reset --hard`\n123",
        "dash -c 'git reset --hard'",
        "ksh -c 'git reset --hard'",
        "/bin/zsh -c 'git reset --hard'",
        "bash --norc --noprofile -c 'git reset --hard'",
        "bash -o pipefail -c 'git reset --hard'",
        "bash -O extglob -c 'git reset --hard'",
        "bash -euo pipefail -c 'git reset --hard'",
        "bash -ce 'git reset --hard'",
        "bash -c -- 'git reset --hard'",
        "bash -c $'git reset --hard'",
        "su -c 'git reset --hard'",
        "su root -c 'git reset --hard'",
        "su --command='git reset --hard'",
    ],
    CLEAN: [
        "sudo sh -c 'git clean -fdx'",
        "`git clean -fdx`",
        "git clean -d -f",
        "git clean --force -d",
        "git clean --forc -d",
    ],
    DISCARD: [
        "git checkout .",
        "git checkout -- .",
        "git restore --source=HEAD .",
        "git checkout HEAD -- .",
        "git checkout -- . >/dev/null",
        "git checkout -- '*'",
        "git checkout -f",
        "git checkout --force main",
        "git switch -f main",
        "git switch --discard-changes main",
    ],
    DELETE: [
        "git push origin --delete main",
        "git push origin -d main",
        "git push origin :main",
        "git push origin :refs/heads/main",
        "git push origin --delete master",
        "git push origin -d trunk",
        "git push origin :develop",
        "git push origin --delete release/1.0",
        "git push --delete origin my-branch main",
        'bash -c "git push origin --delete main"',
    ],
    HISTORY: [
        "git filter-branch --tree-filter 'rm -f secrets' HEAD",
        "git filter-repo --path secrets --invert-paths",
    ],
}

ALLOWED = [
    'echo "git push --force"',
    'git commit -m "docs: explain git push --force"',
    'git commit -m "docs: explain \\`git reset --hard\\`"',
    "git commit -m 'docs: explain `git reset --hard`'",
    'git commit -m "fix: tidy\n\nAgents must never run git reset --hard here."',
    "git commit -m 'fix: tidy\n\nAgents must never run git reset --hard here.'",
    'gh pr create --title t --body "Summary\n- stop using git push --force on main"',
    "git commit -m \"$(cat <<'EOF'\ndocs: explain git reset --hard\nEOF\n)\"",
    "gh pr create --title t --body \"$(cat <<'EOF'\n## Why\nStop git push --force on main.\nEOF\n)\"",
    "git commit -F - <<'EOF'\nfix: tidy\n\nnever git push --force\nEOF",
    "cat > notes.md <<'EOF'\nNever run git reset --hard here.\nEOF",
    "cat <<123\ngit reset --hard\n123",
    'grep -n "reset --hard" hooks/git-guard.py',
    'bash -c "echo hi"',
    'bash -c "git commit -m \\"docs: explain git reset --hard\\""',
    "brew install git && git status",
    "rg -n git hooks/ | head",
    "which git; command -v git",
    "git log --oneline | grep push",
    "man git-reset",
    "git status",
    "git clean -n",
    "git restore --staged .",
    "git checkout -- README.md",
    "git checkout main",
    "git checkout -b feature",
    "git switch main",
    "git switch -c feature",
    "git clean -e fixtures -n",
    "git push origin my-branch",
    "git push origin --delete fix/x",
    "git push origin -d my-branch",
    "git push origin :fix/x",
    "git push --force-with-lease origin my-branch",
    "git push --force-with-lease origin HEAD:my-branch",
    "git push --force-with-lease origin refs/heads/my-branch",
    'bash -c "git push --force-with-lease origin my-branch"',
]

TRAILER_COMMITS = [
    'git commit -m "fix: x\n\nCo-authored-by: Claude <noreply@anthropic.com>"',
    '/usr/bin/git commit -m "fix: x\n\nCo-authored-by: Claude <noreply@anthropic.com>"',
    "bash -c \"git commit -m 'fix: x Generated with Claude Code'\"",
    "git commit -m \"$(cat <<'EOF'\nfix: x\n\nCo-authored-by: Claude <noreply@anthropic.com>\nEOF\n)\"",
    "git commit -F - <<'EOF'\nfix: x\n\nGenerated with Claude Code\nEOF",
    'git commit -F <(printf "Co-authored-by: Claude")',
    "git commit -m 'fix: x' --trailer 'Co-authored-by=Claude <noreply@anthropic.com>'",
]

TRAILER_MENTIONS = [
    "gh pr create --body \"Policy example: git commit -m 'Generated with Claude Code'\"",
    'git commit -m "fix: x"',
]


def setUpModule():
    global REPOS, REPO_ON_MAIN, REPO_ON_MY_BRANCH
    REPOS = tempfile.TemporaryDirectory()
    REPO_ON_MAIN, REPO_ON_MY_BRANCH = (os.path.join(REPOS.name, name) for name in ("main", "my-branch"))
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false"]
    for path in (REPO_ON_MAIN, REPO_ON_MY_BRANCH):
        subprocess.run([*git, "init", "-q", "-b", "main", path], check=True)
        subprocess.run([*git, "-C", path, "commit", "-q", "--allow-empty", "-m", "init"], check=True)
    subprocess.run([*git, "-C", REPO_ON_MY_BRANCH, "switch", "-q", "-c", "my-branch"], check=True)


def tearDownModule():
    REPOS.cleanup()


def hook_output(command, cwd=None, **env):
    cwd = cwd or REPO_ON_MY_BRANCH
    base = {k: v for k, v in os.environ.items() if k != "KEEL_BLOCK_AI_TRAILERS"}
    return subprocess.run([sys.executable, GUARD], input=json.dumps({"tool_input": {"command": command}, "cwd": cwd}),
                          capture_output=True, text=True, cwd=cwd, env={**base, **env}, check=True).stdout


class GitGuardTest(unittest.TestCase):
    def assertDenied(self, command, reason, **kwargs):
        out = hook_output(command, **kwargs)
        self.assertNotEqual(out, "", "the hook allowed the command")
        decision = json.loads(out)["hookSpecificOutput"]
        self.assertEqual((decision["hookEventName"], decision["permissionDecision"]), ("PreToolUse", "deny"))
        self.assertIn(reason, decision["permissionDecisionReason"])

    def assertAllowed(self, command, **kwargs):
        self.assertEqual(hook_output(command, **kwargs), "")

    def test_denies_destructive_git_with_its_reason(self):
        for reason, commands in DENIED.items():
            for command in commands:
                with self.subTest(command=command):
                    self.assertDenied(command, reason)

    def test_lease_onto_head_is_denied_from_a_checkout_on_my_branch(self):
        for command in ("git push --force-with-lease", "git push --force-with-lease origin HEAD",
                        "cd ../main && git push --force-with-lease origin HEAD"):
            with self.subTest(command=command):
                self.assertDenied(command, FORCE, cwd=REPO_ON_MY_BRANCH)

    def test_allows_safe_git_and_prose_that_mentions_it(self):
        for command in ALLOWED:
            with self.subTest(command=command):
                self.assertAllowed(command)

    def test_blocks_ai_trailer_only_when_opted_in(self):
        for command in TRAILER_COMMITS:
            with self.subTest(command=command):
                self.assertAllowed(command)
                self.assertDenied(command, TRAILER, KEEL_BLOCK_AI_TRAILERS="1")
        for command in TRAILER_MENTIONS:
            with self.subTest(command=command):
                self.assertAllowed(command, KEEL_BLOCK_AI_TRAILERS="1")


if __name__ == "__main__":
    unittest.main()
