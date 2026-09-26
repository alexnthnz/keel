---
name: reflect
description: Spawn three parallel review subagents over the active transcript, surface learnings, and route each to a concrete edit on an existing skill. Use when the user says reflect.
disable-model-invocation: true
---

# Reflect

Other keel skills named here sit beside this one at `${CLAUDE_SKILL_DIR}/../<name>/SKILL.md`, and a principle at `principle-<name>`. The Skill tool refuses them, so read the file and follow it.

Mine the current conversation for durable learnings, then route them into skill edits.

## When to invoke

Invoke when the user says "reflect" or "/keel:reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## Process

### 1. Locate the active transcript

The parent finds its own transcript file before fanning out. Claude Code keeps this project's transcripts in `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/<cwd-slug>/`, where `<cwd-slug>` is the session's starting directory with every character other than a letter or digit turned into `-` (so `/Users/you/proj` becomes `-Users-you-proj`). Use that directory only. Do not glob across `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/*/`. That crosses project boundaries and reads private chats from unrelated projects.

```bash
ls -t ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/<cwd-slug>/${CLAUDE_SESSION_ID}.jsonl ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/<cwd-slug>/*.jsonl 2>/dev/null | head -10
```

Two transcript layouts: the session (`<session-id>.jsonl`, one event per line) and its subagents (`<session-id>/subagents/agent-<id>.jsonl`). The current session's file is `${CLAUDE_SESSION_ID}.jsonl`. If that variable shows unexpanded, take the newest candidates.

For each candidate, find the first event with `"type":"user"` and check that its `message.content` contains the conversation's opening user prompt. Take the matching path. If no path resolves, write a tight digest of the session and pass that instead.

### 2. Spawn three reviewers in parallel

One message, three Agent calls, `subagent_type: general-purpose`, with `model` set as below. Reviewers need MCP access for context lookups (tickets, chat threads, observability traces referenced in the transcript). Claude Code subagents inherit the parent's MCP tools, so they have it.

Each reviewer and the synthesizer name a role line in `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/keel-models.md` and a default. Read `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/keel-models.md` if it exists; use the role's line, else the default. Pass that value as the Agent call's `model`. Omit `model` when the value is `inherit`, `inherit-parent`, or `auto`. If the Agent tool rejects a value, use the default and say so. If it rejects the default, omit `model` and say so.

| Lens | Role line | Default `model` | Prompt template |
|---|---|---|---|
| Judgment | `reflect judgment, divergent, synthesizer` | `opus` | `references/judgment-reviewer.md` |
| Tooling | `reflect tooling` | `sonnet` | `references/tooling-reviewer.md` |
| Divergent | `reflect judgment, divergent, synthesizer` | `opus` | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest where marked. Reviewers return findings in their final report.

### 3. Synthesize

One Agent call, `subagent_type: general-purpose`, with `model` from the `reflect judgment, divergent, synthesizer` line (default `opus`). The synthesizer's quality check includes spot-verifying citations, which can require MCP access. It inherits the parent's MCP tools. Use `references/synthesizer.md` verbatim, with each reviewer's full output inlined where marked. The synthesizer returns a structured Accepted / Rejected / Backlog list.

### 4. Structural enforcement check

Sanity-check the synthesizer's Accepted list. For any item that would be enforced more reliably by a lint rule, script, metadata flag, or runtime check, move it from Accepted to Backlog. See the **encode-lessons-in-structure** principle skill.

### 5. Apply

Before applying any Accepted edit, present the synthesizer's full Accepted/Rejected/Backlog output to the user and wait for explicit approval. The user picks which subset to apply and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

Backlog items file to whatever devex / backlog tracker your team uses automatically. Only the Accepted list waits for approval.

For each approved Accepted item, follow the Routing field exactly:

- Trivial existing-skill edit (a one-line bullet, a tightened sentence, a stale fact corrected): parent does directly.
- Substantive existing-skill edit (a new section, a new pattern table, more than ~10 lines): hand to the `anthropic-skills:skill-creator` skill and run its draft / test / iterate loop. Without it, follow the lead skill's Authoring a skill playbook (`${CLAUDE_SKILL_DIR}/../lead/playbooks/authoring-a-skill.md`).
- `tune description: <skill path>` (the skill exists but didn't trigger when it should have): hand to `skill-creator` and run its description-optimization loop.
- `new skill via skill-creator: <kebab-name>`: hand creation to `skill-creator`. Do not invent the shape ad hoc.

If your environment ships a SKILL.md validator, run it on every touched skill before declaring done. Inside a Claude Code plugin, `claude plugin validate <plugin-dir>` is one. Skip this step if there is none.

### 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog filed to the devex tracker: `<issue title>` (`<tags>`). One line each.
- Dropped: one line per rejected finding + reason from the synthesizer.
