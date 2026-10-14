# Upstream

keel is a fork of pstack by Lauren Tan (poteto), MIT. keel first made its own Claude Code port of pstack (the translation table below), then renamed and reorganized it (the rename table).

- Upstream: <https://github.com/cursor/plugins>, directory `pstack/`.
- Base: `cursor/plugins@12d587d`, pstack 0.15.5.
- The first commit in this repository is an unmodified copy of `pstack/` at the base. Everything after it is keel.

Removed as Cursor-only or pstack branding: `.cursor-plugin/`, `assets/` (pstack's logo), `docs/guide/images/` (pstack's illustrations), `automations/benny/` and `skills/make-bot-ui/`. Two later upstream additions are removed too:

- `plugin.json` at the root, the Agent Plugins v1 manifest. Claude Code reads `.claude-plugin/plugin.json`, and `codex/scripts/validate-package.py` rejects a root manifest.
- `skills/poteto-help/`, a help skill about pstack in Cursor. keel's README and guide cover the same ground.

`bin/upstream-diff.sh --apply` skips all of these on every sync.

Every change after the first commit applies two tables and nothing else. The translation table turns Cursor into Claude Code. The rename table then turns pstack into keel. **Re-apply both on every upstream sync, translation first, then rename.** poteto's content, voice, rules, and structure stay as they are.

## Rename table

| Upstream | Claude Code port | keel |
|---|---|---|
| plugin `pstack` | `pstack`, marketplace `pstack-local` | `keel`, marketplace `keel` |
| `skills/poteto-mode/`, `name: Poteto Mode`, `/poteto-mode` | `poteto-mode`, `/pstack:poteto-mode` | `skills/lead/`, `name: lead`, `/keel:lead`. No `disable-model-invocation`, so the main session loads it with the Skill tool. Its opening makes the main session the lead. Its Subagents section adds the `isolation: "worktree"` rule, the critic rule, and the session-lifetime (`/bg`) rule |
| `agents/poteto-agent.md` | `pstack:poteto-agent` | `agents/ponytail.md`, `keel:ponytail`. The builder and owner, with `model: inherit` and `memory: user`. It may spawn its own subagents and merges only under autopilot or when its brief says to land, plus Working method, subagent and merging sections |
| `agents/comment-sicko.md`, `name: Comment Sicko` | `pstack:comment-sicko` | `agents/critic.md`, `keel:critic`. A read-only reviewer with a named lens and `disallowedTools: Edit, Write, NotebookEdit, Agent`. Comment Sicko's text is its default comments lens |
| `skills/setup-pstack/`, `/setup-pstack` | `/pstack:setup-pstack` | `skills/setup/`, `/keel:setup` |
| `~/.cursor/rules/pstack-models.mdc` | `~/.claude/pstack-models.md` | `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/keel-models.md` |
| the agent's store | `~/.claude/pstack-store/<project-slug>/` | `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/keel-store/<project-slug>/` |
| `~/.cursor/projects/`, user skills, plugin cache | `~/.claude/projects/`, `~/.claude/skills/`, `~/.claude/plugins/cache/*/pstack/*/` | the same under `${CLAUDE_CONFIG_DIR:-$HOME/.claude}`, cache glob `*/keel/*/` |
| `/<name>` | `/pstack:<name>` | `/keel:<name>` |
| "pstack" naming this plugin in prose, `pstack/...` paths | "pstack", `<pstack>/...` | "keel", `<keel>/...` |
| `docs/guide/02-poteto-mode.md` | same | `docs/guide/02-lead.md` |
| interrogate reviewers on `generalPurpose` | `general-purpose` | `keel:critic` with the correctness lens, one per configured model. The `codex` lane is unchanged |
| no-comments spawns Comment Sicko, which deletes comments itself | same, as `pstack:comment-sicko` | spawns `keel:critic` with the comments lens. critic only reports, and no-comments carries out the kills |
| Orchestrate sub-coordinator as `generalPurpose` or `poteto-agent` | `general-purpose` or `pstack:poteto-agent` | `keel:ponytail`, which has the Agent tool |

Every `~/.claude/...` path keel writes uses `${CLAUDE_CONFIG_DIR:-$HOME/.claude}`, so each Claude Code profile keeps its own model file, store, and transcripts. Project paths such as `.claude/skills/` stay as they are.

keel additions with no upstream counterpart: `hooks/git-guard.py` (adapted from Matt Pocock's MIT-licensed git guardrails), `hooks/lead-reminder.sh`, `hooks/hooks.json`, `THIRD_PARTY_NOTICES.md`, `ROADMAP.md` and `bin/upstream-diff.sh`.

Kept on purpose:

- "pstack" and "poteto" where they credit or describe upstream: the README, `THIRD_PARTY_NOTICES.md`, the guide's credit line, source notes in a few skills and agents, and this file.
- The upstream `pstack/` path and the upstream file names in `bin/upstream-diff.sh`, which turns them into keel's.
- The bun scripts' code under `skills/lead/scripts/`, apart from the package name (now `keel-lead-tools` in `package.json` and `bun.lock`) and the install-key file name in `bootstrap.ts`.

## Translation table

The Claude Code column shows the port's names. The rename table above maps them to keel's.

| Cursor | Claude Code |
|---|---|
| Task tool, `Task` call | Agent tool, Agent call |
| `subagent_type: generalPurpose` | `general-purpose`, or `Explore` for read-only explorers |
| `subagent_type: "poteto-agent"`, `"Comment Sicko"` | `"pstack:poteto-agent"`, `"pstack:comment-sicko"` |
| `readonly: true/false`, agent mode | Removed. Subagents inherit MCP tools. Read-only work says "read-only: do not edit files" in the prompt or uses `Explore` |
| `run_in_background: true` | Removed. Subagents run in the background and the parent is notified on completion, so never poll or sleep-wait |
| `is_background: true` (agent frontmatter) | Removed |
| `AskQuestion` | `AskUserQuestion` (1 to 4 questions, 2 to 4 options each) |
| `name: Poteto Mode`, `name: Comment Sicko`, `name: Make Bot UI` | `poteto-mode`, `comment-sicko`, `make-bot-ui` (persona text unchanged) |
| Frontmatter `mode`, `reminder`, `icon`, `color` | Removed. The `reminder` text moved into the poteto-mode body as the stay-on rule |
| `/poteto-mode`, `/how`, and other pstack slash references | `/pstack:poteto-mode`, `/pstack:how`, and so on |
| pstack skill invocation | pstack skills set `disable-model-invocation`, so the Skill tool refuses them. Agents read `<pstack>/skills/<name>/SKILL.md` instead. poteto-mode names the directory through `${CLAUDE_SKILL_DIR}` |
| `claude-opus-5-5-max` (synthesizers, explainers, reflect reviewers) | `opus` |
| `claude-opus-5-5-max` (judgment, prose, hardest tasks) | `inherit` in keel (the port used `opus`) |
| `grok-4.7-xhigh-fast` (code delegates) | `inherit` in keel (the port used `sonnet`) |
| `grok-4.7-xhigh-fast` (explorers, investigators, swarm workers) | `sonnet` |
| `gpt-5.6-sol-max` (reflect tooling) | `sonnet` |
| Panels (arena runners, architect runners, arena cross-judge pool) | `opus, fable, sonnet`. "Different family" becomes "a different model from the parent" |
| interrogate reviewers | `opus, fable, sonnet, codex`. `codex` runs `codex exec --sandbox read-only` from Bash with the shared reviewer brief, and is skipped when `command -v codex` fails |
| `inherit-parent`, `auto` | Kept, plus `inherit`. All omit `model` |
| Effort suffixes and the budget step | Removed |
| Model family prefixes (`claude-*`, `gpt-*`, `grok-*`) | The aliases `opus`, `sonnet`, `haiku`, `fable`, plus `codex` |
| `~/.cursor/rules/pstack-models.mdc` (always applied) | `~/.claude/pstack-models.md`, a plain file. Each skill says "Read `~/.claude/pstack-models.md` if it exists; use the role's line, else the default." |
| `deslop` from `cursor-team-kit` | Claude Code's built-in `/simplify`, plus pstack's `unslop` for prose |
| `control-cli` | Drive the CLI or TUI directly through Bash, with tmux for interactive TUIs |
| `control-ui` | `anthropic-skills:chrome-browser`, `anthropic-skills:built-in-browser`, or `anthropic-skills:computer-use` when available, else Playwright via Bash |
| `create-skill` | `anthropic-skills:skill-creator` when available, else the Authoring a skill playbook |
| `/visualize` charts, Mermaid diagrams, and generated images (ketchup's visuals) | A small box diagram or a text chart in a fenced code block, or a screenshot or recording that already exists, linked by its path. ketchup stays read-only and posts nothing, so it publishes no Artifact |
| Cursor's built-in `/babysit` | Dropped. pstack's Babysit playbook is the only one |
| `/loop` in dynamic mode, cloud-sleeper wake chain | `/loop` with no interval (self-paced), or `/loop 1h <tick prompt>` for an audit tick. The multi-phase plan template keeps the literal `/loop 1h`, because `check-plan.mjs` requires it |
| Cursor cloud agent, `environment: "cloud"`, `cloud_base_branch` | A background subagent with `isolation: "worktree"`, or a separate `claude --worktree` session. "Assume the VM dies" becomes "assume the session dies" |
| Origin forge, `origin pr ...`, and the run's built-in PR tool | `gh` only |
| Bugbot | Automated PR review bots (Bugbot, Claude Code review, CodeRabbit, etc.). `references/bugbot-triage.md` keeps its filename |
| The agent's store (path in the system prompt) | `~/.claude/pstack-store/<project-slug>/`, exported as `ORCH_STORE` for `orch` |
| `agent-transcripts/` under `~/.cursor/projects/<slug>/` | `~/.claude/projects/<cwd-slug>/<session-id>.jsonl`, one event per line, subagents under `<session-id>/subagents/`. `<cwd-slug>` replaces every non-alphanumeric character of the path with `-` |
| Cursor restart | Session restart or context compaction |
| Cursor as the product the user runs | Claude Code |
| `pstack/skills/...` monorepo paths, `git show origin/main:pstack/...` | The installed plugin's own files, `<pstack>/skills/...` |
| `.cursor/skills/`, `.cursor/worktrees/` | `.claude/skills/`, `.claude/worktrees/` |

## Not ported

- `automations/benny/` runs on Cursor automations and Slack. Removed.
- `skills/make-bot-ui/` drives Cursor's bot routines (`update_state`, `SendToUser`, `api2.cursor.sh`). Removed.
- `docs/guide/` got a light pass only: install, the model file, `/simplify`, `/loop`, and `.claude/skills/` paths. Its `/name` examples keep upstream spelling under a note that they run as `/keel:name`.

## Scripts left as upstream wrote them

`skills/lead/scripts/` is unchanged apart from the package name. Its Cursor-specific parts:

- `worktree-audit.sh` reads chat transcripts from `~/.cursor/projects/<slug>/agent-transcripts`, so its `LAST_CHAT` column is always `-` on Claude Code. The Worktree cleanup playbook tells the agent to scan `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/` itself and to treat every `safe` row as `verify-recent-chat` until that scan clears it.
- `worktree-audit.sh` fills its PR column from `origin pr list` when the Origin CLI can read the repository, and from `gh` otherwise. keel uses `gh` only, so without Origin installed the script takes the `gh` path.
- `orch frontier set` takes `--forge origin` for Origin. keel's Orchestrate playbook calls it without the flag, so it reads PR chains through `gh`.
- `watch-pr` treats a completed `Code Review Gate` check run whose conclusion is `ACTION_REQUIRED` as the owner-approval gate. That check name comes from Cursor's own review setup.
- `watch-pr/github.ts` counts review passes only for Bugbot, detected by the author `bugbot` or the `cursor` app with `CURSOR_AUTOMATION_ID` markers. Other review bots show no pass count. The Babysit playbook counts their passes from review history.
- `check-plan.mjs` requires the literal markers `git show origin/main:` and `/loop 1h` in a plan's Program checklist. The plan template keeps both.
- The package was named `@cursor-skill/poteto-mode-tools`; keel renamed it `keel-lead-tools`.

## Sync with upstream

A sync applies upstream's diff to keel rather than merging an import. The repository squash-merges every PR, so an import commit on a sync branch never reaches `main`, and the next `git merge` would fall back to the first import as its merge base. A 3-way apply needs only the base blobs, and the script copies in any that keel's history lacks.

1. See what changed since the base. `KEEP=1` keeps the clone and prints its path, so you can read full diffs and reuse it.

   ```bash
   KEEP=1 bin/upstream-diff.sh
   ```

2. Apply the change on a branch from `main`. With `--apply`, the script diffs `pstack/` from the base to the upstream ref, moves renamed paths per the rename table, skips the removed paths, copies any missing base blobs into this repository, and runs `git apply --3way`. `CLONE=<dir>` reuses the kept clone. The ref must be one `git fetch` accepts: a branch, a tag, or a full SHA.

   ```bash
   git switch -c sync/pstack-<version> origin/main
   CLONE=<kept clone> bin/upstream-diff.sh --apply <full upstream SHA>
   ```

   Files that apply cleanly come out staged. A conflict leaves markers in the file, a `U <path>` line in the output, and exit status 1. If the output says `does not exist in index`, the apply wrote nothing, because the diff changes a file keel lacks. Add its path to the rename table and the script's `awk` program, or to the script's `removed` list, then run the script again.

3. Resolve every conflict by re-applying the translation table, then the rename table, to the new upstream text, and `git add` the file. A new upstream file under a renamed directory already lands at its keel path.

4. Re-apply both tables to the upstream lines that applied cleanly. Start from the two residual scans, which should print only the lines listed as deliberate.

   ```bash
   grep -rnIE 'Task tool|generalPurpose|AskQuestion\b|\.cursor/|cursor-team-kit|deslop|grok|gpt-5\.6|claude-opus-5-5|is_background|readonly:|origin pr|/goal' skills agents README.md
   grep -rnIE 'poteto-mode|poteto-agent|comment-sicko|setup-pstack|pstack-models|/pstack:|pstack:(poteto|comment)|~/\.claude/' skills agents docs README.md
   ```

5. Validate, then record the new base: `base` in `bin/upstream-diff.sh`, the base line at the top of this file, and the source lines in `README.md` and `THIRD_PARTY_NOTICES.md`. Bump keel's version in a separate release commit.

   ```bash
   claude plugin validate .
   claude plugin validate .claude-plugin/plugin.json
   claude --plugin-dir . plugin details keel
   ```

Deliberate residual-scan hits. The first scan prints the model mapping table and the differences list in `README.md`, the `/goal` line in the multi-phase plan template, and the Cursor-path lines inside the unported scripts. The second prints the credit line in `README.md` and the `poteto-mode` names inside the bun scripts under `skills/lead/scripts/`.
