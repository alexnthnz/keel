# Security policy

## Supported versions

Security fixes go into the latest release of keel. Update with `claude plugin update keel@keel`.

## Reporting a vulnerability

Please report security problems privately through
[GitHub's private vulnerability reporting](https://github.com/alexnthnz/keel/security/advisories/new),
not in a public issue.

Include what you found, how to reproduce it, and which keel and Claude Code versions you used. You will get a reply
as soon as the maintainer can look at it, and credit in the release notes if you want it.

## Scope

keel runs locally inside Claude Code. The parts most worth a security review are:

- [`hooks/git-guard.py`](./hooks/git-guard.py), which decides which git commands an agent may run;
- [`hooks/lead-reminder.sh`](./hooks/lead-reminder.sh);
- the scripts under [`skills/lead/scripts/`](./skills/lead/scripts/), which call the GitHub CLI.

keel sends nothing anywhere itself. Its playbooks use the GitHub CLI and, optionally, the Codex CLI, under your own
accounts.
