# Roadmap

keel's goal is one engineering loop that runs on any project. A project brings its facts (its `CLAUDE.md`) and its
own know-how (skills in `.claude/skills/`); the method, the agents and the guardrails come from keel.

## Next

- Add the Codex review lane to `arena` and `architect`, not only `interrogate`.
- Try Claude Code's `/goal` for autopilot runs, the way pstack uses it in Cursor.
- Make `watch-pr` count review passes from any review bot, not only Bugbot, and teach `worktree-audit.sh` to read
  Claude Code transcripts instead of Cursor's.
- Write a "use keel on a new project" guide: a facts-only `CLAUDE.md`, project skills, and a generated verify skill.
- Pull pstack updates as they land, re-applying the tables in `UPSTREAM.md`.

## Decided

- "Go" builds to open, ready pull requests. Merging happens only under "autopilot" or when asked to land or ship.
- The lead is a skill loaded by the main session, kept sticky by a reminder hook on every prompt.
- ponytail inherits the lead's model, may spawn its own subagents, and never bypasses a review or check the forge
  enforces.
- Subagents live only as long as their session: move a session to the background with `/bg` before closing it.
- Subagent concurrency stays at Claude Code's default of 20, because keel fans out in layers.
