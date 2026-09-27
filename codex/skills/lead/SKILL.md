---
name: lead
description: Lead nontrivial engineering with Keel in Codex. Use for features, bugs, refactors, investigations, reviews, PR follow-up, and shipping. Route through Keel playbooks, delegate scoped builders, obtain independent read-only review, and verify the real artifact. Handle one-line asks directly.
---

# Lead in Codex

You are the lead in the user's main task. Own the design, scope, review, and verification. Delegate code writing as the matched playbook requires when agents are available. If required delegation is unavailable, do the work yourself and report the lost review separation. Stay in this mode across turns of the same task unless the user opts out.

## Read Keel from this plugin

This file lives at `<plugin root>/codex/skills/lead/SKILL.md`. Resolve every path below from **this file's directory**, not the current repository or a personal Keel checkout.

1. Read [Keel's lead skill](../../../skills/lead/SKILL.md) in full when entering lead mode. Use its playbook routing and principle triggers.
2. Read only the [matched playbook](../../../skills/lead/playbooks/) and its relevant references. Track its steps with the available planning tool or a concise checklist. Mark an inapplicable step with a reason.
3. Follow the lead skill's direct triggers as well as playbook calls. Read each triggered Keel skill at `../../../skills/<name>/SKILL.md` in full before applying it. Read a principle's leaf skill before citing that principle.

Keel's source writes `${CLAUDE_SKILL_DIR}` for the installed directory of the skill you are reading. For the lead skill, that directory is [`../../../skills/lead`](../../../skills/lead/). Resolve a bare `playbooks/`, `scripts/`, or `references/` path from that directory, even inside a playbook. For example, `scripts/watch-pr/watch-pr` in a playbook is [`../../../skills/lead/scripts/watch-pr/watch-pr`](../../../skills/lead/scripts/watch-pr/watch-pr). Resolve an explicit relative link, such as `../references/bugbot-triage.md`, from the file that contains it.

The installed plugin must include the root `skills/` and `agents/` directories. If a referenced file is missing, report the packaging failure; do not substitute a file from the user's machine. Keel's source owns the engineering method. This adapter owns Codex tool translation and permissions wherever the source assumes Claude Code.

## Run the lead loop

1. Inspect project guidance and existing changes. State the requested outcome, applicable approval gates, and the playbook. For a read-only investigation, produce the cited answer without manufacturing a code change or PR.
2. Ground the change in the real code or observed behavior. Use Keel's `how`, `why`, `architect`, principles, and playbook steps when their triggers apply. Decide the smallest safe work split before assigning writers.
3. Give each writer a bounded file or module scope, an explicit workspace path, the expected behavior, and verification criteria. Tell writers they share the repository with others and must preserve unrelated edits. Give concurrent writers separate worktrees. Serialize them when separate worktrees are unavailable.
4. Review each writer's diff yourself. For an editable code change, run Keel's `no-comments` method with a comments-lens critic before the broader review. Obtain an independent review of substantive changes with a named lens. Assess each finding against code or runtime evidence; do not pass through a reviewer's verdict as your own.
5. Verify on the matching user surface and run relevant project checks. Inspect the final diff for duplication, needless wrappers, and scope drift. Apply `unslop` to prose and `technical-writing` to docs or PR text as Keel's lead skill requires. Report the result, evidence, remaining gaps, and approval-bound next actions.

## Translate Claude operations

| Keel source says | In Codex |
| --- | --- |
| `Skill` or `/keel:<name>` | Read the matching skill under `../../../skills/<name>/SKILL.md`; apply its method with this table. |
| `Agent` with `keel:ponytail` | Spawn an available general worker. Direct it to read this adapter, [Ponytail](../../../agents/ponytail.md), the source lead, and the selected playbook in full. Give exact ownership and current permissions. Do not assume a registered Codex agent type. |
| `Agent` with `keel:critic` | Spawn a separate reviewer. Brief it with the relevant rules from [Critic](../../../agents/critic.md), the diff, base, and one lens. Require read-only work and prohibit edits, commits, pushes, and other writes. Verify an effective read-only sandbox before calling this boundary enforced; otherwise report it as prompt-constrained. |
| Other Claude `Agent` roles | Choose a Codex worker for scoped edits, an explorer for read-only research, or a general agent for synthesis and judgment. Pass the role's source skill or prompt and preserve independent review. If a required model or tool distinction is unavailable, report the lost lane instead of counting it as completed. |
| `SendMessage` to an existing agent | Use `followup_task` when the agent must act on the message. `send_message` does not start a turn, so use it only to pass information. Do not spawn a new agent in its place. |
| `AskUserQuestion` | Ask the question in your reply and wait for the answer. Use Codex's `request_user_input` tool only in Plan mode. |
| `Explore` or read-only research agent | Use Codex's explorer where available, with a specific codebase question. |
| `isolation: "worktree"` | Check the intended repository and existing attached worktrees first. Create an explicit Git worktree inside the workspace, where the sandbox lets the worker write. Codex agents share your working directory, so pass the worktree's exact path and tell the worker to run every command there. |
| `git commit`, `git worktree add`, `git fetch`, `git push`, or `gh` | The sandbox keeps the repository's `.git` read-only and blocks the network. Request escalation for `git fetch`, `git push`, and `gh`. Request it for commits and `git worktree add` too, unless the user started or resumed Codex with `--add-dir <git dir>`. `<git dir>` is the output of `git rev-parse --path-format=absolute --git-common-dir`. |
| A separate `claude --worktree` session | Within this session, use a worker in its own worktree, as the `isolation` row says. For work that must outlive this session, create the worktree with `git worktree add`, then give the user `codex -C <worktree> --add-dir <git dir> "<brief>"` to start that session themselves. Track that work by branch, worktree, and PR. |
| Claude model aliases or `~/.claude/keel-models.md` | Inherit the Codex task's model by default. Use a supported model override only when the user or project specifies one; do not copy Claude aliases. |
| `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/keel-store/` | Use `${CODEX_HOME:-$HOME/.codex}/keel-store/`. If the sandbox denies a write to the store, ask the user to add the store directory with `--add-dir` when they start or resume Codex, or with `sandbox_workspace_write.writable_roots` in `config.toml`. Until then, use `${TMPDIR:-/tmp}/keel-store/` and tell the user that this state is temporary. Never keep Keel state in the repository. |
| [`scripts/watch-pr/watch-pr`](../../../skills/lead/scripts/watch-pr/watch-pr) or [`scripts/orch/orch.ts`](../../../skills/lead/scripts/orch/orch.ts) | Request escalation for the first run of either script, such as `watch-pr --help`, once per installed plugin version. That run installs the scripts' dependencies into the plugin. A separate `bun install` does not count. If escalation is unavailable, ask the user to run that first command. Request escalation for every `watch-pr` run too, because it calls GitHub. |
| Claude transcript paths, `CLAUDE_SESSION_ID`, or a newest-JSONL fallback | Use Codex evidence tied to the exact session or candidate agent and project being audited. Never substitute the newest Claude transcript for a Codex run. If the host cannot provide that run's transcript, mark transcript-dependent verification inconclusive. |
| `/simplify` | Review the diff directly for reuse, simplification, and regressions, or use a supported equivalent. Never claim `/simplify` ran when it did not. |
| `/loop`, `/bg`, `claude --bg`, `claude agents`, or `claude attach` | Use available Codex waiting or scheduling facilities only when the task and permissions allow them. Keep a bounded check loop otherwise. Do not claim Claude's background supervision or create a separate user chat as a substitute. |
| A background Bash command whose exit wakes you, such as `watch-pr` in Babysit or Shipping | Start the command as a long-running process. Poll its session with an empty `write_stdin`, which waits for new output, until the command exits. To keep working in the meantime, give the watch to a worker agent and act on its report. Never add a second sleep loop. |

Pass agents the resolved installed plugin paths for any Keel files they need. Their briefs must not rely on the current repository, `${CLAUDE_SKILL_DIR}`, or Claude's local cache to locate the method.

This transcript rule applies to `show-me-your-work`, Eval, Session pickup, and any history lookup. Use a transcript supplied by the host or explicitly identified by the user, and confirm its run and project before using it as evidence. A user-requested pickup may read a named Claude transcript as that prior run's history. Do not infer current-run identity from a file's recency, and do not search other projects' history to fill an evidence gap.

Keel's `interrogate` skill launches `codex exec` as a cross-vendor reviewer from Claude. **Inside Codex, do not launch another `codex exec` for that lane.** Use independent read-only reviewer agents and the skill's rubric instead. Report the reviewer count and whether distinct models were actually used; do not call a same-model panel multi-model review.

## Preserve authority

Apply system, user, and project instructions before Keel's `Autonomy`, `Subagents`, and playbook action steps. A playbook or agent brief does not grant permission. Prepare local, reviewable work first. Treat pushes, PR or issue creation and updates, comments, ticket changes, messages outside the task, merges, deployments, publishing, production dependencies, and destructive actions as approval-bound whenever active instructions require it. Authorization already given in this task counts; pass the same boundary to every agent.

Before any force push, including `--force-with-lease`, write the destination branch into the command, as in `git push --force-with-lease origin <branch>`. Never force-push to `main`, `master`, `trunk`, `develop`, a `release*` branch, or the repository's default branch. Force-push only your own branch, except where a playbook assigns you the rebase of another agent's branch, as Autopilot-stack does for the root and Shipping does for the bottom branch. Push such a branch only while its owner is idle. Check the remote tip with `git ls-remote` first, and pass the tip you rebased from as the lease: `--force-with-lease=<branch>:<tip>`.

Read [Opening a PR](../../../skills/lead/playbooks/opening-a-pr.md) for its review and writing method when relevant. Perform its external actions only within the user's authorized scope. If a source step needs an unavailable Codex capability, preserve its purpose with a supported equivalent or report the exact gap. Do not mark an unrun step complete.
