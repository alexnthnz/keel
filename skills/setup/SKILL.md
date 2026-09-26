---
name: setup
description: Configure which models keel uses per role. Checks for the Codex CLI, offers Claude Code's model aliases, and writes keel-models.md in the active Claude config directory, which every keel skill reads to override its defaults. Use for /keel:setup, "configure keel models", or changing keel's model choices.
disable-model-invocation: true
---

# Setup keel

Write `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/keel-models.md`, a plain file that sets keel's model per role. Claude Code has no always-applied rule outside CLAUDE.md, so each keel skill that spawns a subagent reads this file itself.

The file lives in the active Claude config directory, so each profile run through `CLAUDE_CONFIG_DIR` keeps its own models. Resolve the path in Bash with `echo "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/keel-models.md"` and never hard-code `~/.claude`.

## Steps

### 1. Detect available models

Claude Code subagents take a model alias, not a vendor slug. The valid values are `opus`, `sonnet`, `haiku`, and `fable`. The aliases `inherit`, `inherit-parent`, and `auto` are always valid and all mean the same thing: omit the Agent call's `model` so the role runs on the parent model. That is how a user who picks the model per session keeps that choice.

Then check the cross-vendor lane with `command -v codex`. When it succeeds, `codex` is also a valid panel entry. It is not a subagent. The **interrogate** skill runs it from Bash with the OpenAI Codex CLI. When the check fails, leave `codex` out of every list and say so.

### 2. Load current state

The default role-to-model mapping is the file shape shown in step 5 below. If `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/keel-models.md` already exists, read it and treat its role values as the current choices. Otherwise start from those defaults. A line whose role is not in step 5, such as `how critics`, is from a retired role. Drop it. A `# budget` line is from the Cursor version. Drop it too, since Claude Code subagents have no reasoning budget to set.

### 3. Map and confirm

**(a) Build the table.** Start from the skill defaults, and on a re-run keep any role the user changed. A value that is not one of the aliases in step 1 (such as a vendor slug copied from the Cursor rule) needs a choice. Suggest the default for that role.

**(b) Show the roles and confirm.** Show every role with its model, marking any value that needs a choice. Also list each line step 2 dropped. Ask whether to accept as-is or change specific roles, offering `opus`, `sonnet`, `haiku`, `fable`, and `inherit`, plus `codex` for panel roles when step 1 found it. Prefer AskUserQuestion over free text. It takes at most four options per question and adds an "Other" choice itself, so put the four most likely values first. For panel roles (arena runners, architect runners, interrogate reviewers) the value is a list, and one reviewer runs per entry, alias entries included, so the list length sets the count. Three different Claude models give a panel its diversity. `codex` belongs only in `interrogate reviewers`, since arena and architect runners must write files through the Agent tool. `arena cross-judge pool` is also a list, but Arena selects one value from it that differs from the parent's model when possible. `swarm workers` is the default model for every worker unless a race or comparison assigns another model per arm.

### 4. Validate

Every value written must be `opus`, `sonnet`, `haiku`, `fable`, `inherit`, `inherit-parent`, or `auto`, or `codex` inside `interrogate reviewers` when step 1 found it. If a chosen value is not valid, stop and ask again.

### 5. Write the file

Write `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/keel-models.md` with one line per role, using the same labels the lead skill uses. Overwrite the whole file so re-runs stay idempotent. Shape:

```
# keel model configuration. One line per role. Delete a line to fall back to the skill default.
# Values: opus, sonnet, haiku, fable. `inherit` (or `inherit-parent`, `auto`): the role runs on the parent model (omit the Agent call's `model`). Alias entries in a panel list still count toward its fan-out.
# `codex` (interrogate reviewers only): a cross-vendor reviewer run from Bash with the OpenAI Codex CLI.
feature, refactoring: inherit
bug-fix: inherit
perf-issue: inherit
hillclimb: inherit
judgment and prose: inherit
hardest tasks: inherit
how explorer: sonnet
how explainer: opus
why investigators: sonnet
why synthesizer: opus
reflect tooling: sonnet
reflect judgment, divergent, synthesizer: opus
arena runners: opus, fable, sonnet
arena cross-judge pool: opus, fable, sonnet
swarm workers: sonnet
architect runners: opus, fable, sonnet
interrogate reviewers: opus, fable, sonnet, codex
```

When step 1 found no `codex`, write `interrogate reviewers: opus, fable, sonnet`.

### 6. Confirm

Tell the user the file was written and that keel skills read it on their next spawn, in this session and new ones. Re-running this skill updates it.

### 7. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /keel:create-verification-skill." On yes, run the **create-verification-skill** skill. The Skill tool refuses keel skills, so read `${CLAUDE_SKILL_DIR}/../create-verification-skill/SKILL.md` and follow it. On no, move on without pushing.
