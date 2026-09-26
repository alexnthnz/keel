---
name: interrogate
description: "Use for \"interrogate\", \"adversarial review\", \"multi-model review\", \"challenge this\", \"stress test this code\", \"find blind spots\", or \"tear this apart\". Multiple LLM reviewers challenge changes from independent angles."
disable-model-invocation: true
---

# Interrogate

Run one `keel:critic` reviewer per configured model to adversarially review code changes, plus the `codex` lane when it is configured. Each model gets the same prompt and rubric. The adversarial signal comes from model diversity, not assigned personas.

The deliverable is a synthesized verdict. Do NOT auto-apply changes.

## Step 1, Determine Scope

Identify what to review from context:

- If the user points at specific files or a diff, use that
- If on a feature branch, run `git diff main...HEAD` (or the appropriate base branch) for the full changeset
- If the user's message references recent work, gather the relevant files

Package the diff (or file contents) plus any surrounding context files the reviewers need to understand the code.

## Step 2, State the Intent

Before spawning reviewers, state the intent explicitly. Derive this from:

- The user's message
- Commit messages
- PR description if one exists
- The code itself

Write one clear paragraph. If you're unsure about the intent, ask the user before proceeding.

## Step 3, Spawn Reviewers

Launch all reviewers at once. Claude reviewers are Agent calls in a single message. The `codex` reviewer is a Bash command started in the same message. Read `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/keel-models.md` if it exists; use the role's line, else the default. The role line is `interrogate reviewers`, one reviewer per entry, extending or shrinking the Reviewer A/B/C/D labels below to the configured entry count.

| Reviewer | Default model | Runs as |
|----------|---------------|---------|
| Reviewer A | `opus` | `keel:critic` subagent |
| Reviewer B | `fable` | `keel:critic` subagent |
| Reviewer C | `sonnet` | `keel:critic` subagent |
| Reviewer D | `codex` | Bash, OpenAI Codex CLI |

For each Claude reviewer:
- `subagent_type`: `keel:critic`
- `model`: the configured `interrogate reviewers` entry, or the table default with no configured line. For an `inherit`, `inherit-parent`, or `auto` entry, omit `model` so that reviewer runs on the parent model.
- The prompt opens with "Read-only: do not edit files. Lens: correctness, through the interrogate rubric and code-quality lens below. Use the brief's severity scale."

If the Agent tool rejects a configured entry, run that reviewer on Reviewer A's default and say so. If it rejects a table default, omit `model` for that reviewer, say so, and open a separate PR to update the default table. Do not block the review on the model issue. Never treat an alias entry as a rejected model or apply either fallback to it.

The `codex` entry is a cross-vendor lane, not a subagent. Run `command -v codex` first. If it fails, skip the lane and name it as skipped in the Reviewers list. Otherwise write the filled template below to a file and run Codex read-only from the repository root, in the background so it runs alongside the subagents:

```bash
codex exec --sandbox read-only --ephemeral --cd "$(git rev-parse --show-toplevel)" \
  --output-last-message "$tmp/codex-review.md" - < "$tmp/reviewer-brief.md"
```

`$tmp` is a scratch directory you create for the run. The brief goes in on stdin because `codex exec review --base <branch>` refuses a custom prompt, and every reviewer gets the same brief. When the command finishes, read `$tmp/codex-review.md` and treat it like any other reviewer's output.

Read `references/reviewer-prompt.md` and fill in the template with:
1. The stated intent
2. The diff or file contents
3. The review rubric from `references/rubric.md`
4. The code-quality lens from `references/code-quality-review.md`

The same filled template goes to all reviewers, so every model applies the code-quality lens.

## Step 4, Synthesize

As results come back, build a unified picture:

1. **Parse all findings** from the reviewers
2. **Identify consensus**. Findings raised by 2+ models independently are highest signal.
3. **Identify lone-model findings**. Still worth reading, but weight accordingly.
4. **Deduplicate**. Different models may describe the same issue differently. Merge these and note which models raised it.
5. **Note disagreements**. If one model flags something and another explicitly says the opposite, that's useful context for the verdict.

## Step 5, Lead Judgment

You are the lead reviewer, a pragmatic senior engineer, not a neutral aggregator.

Read `references/lead-judgment.md` for the full framework.

Categorize every finding using these buckets:

- **Act on**. Real issues affecting correctness, security, or maintainability given the actual goals. These would block a real PR.
- **Consider**. Legitimate points, but you're not sure they outweigh the cost of addressing them right now. Worth the user's attention.
- **Noted**. Technically valid but not actionable. Context-dependent, premature optimization, or low-impact given the current stage.
- **Dismissed**. Wrong, nitpicky, or missing context. Brief explanation why.

For each finding, include:
- Which model(s) raised it
- The category (act on / consider / noted / dismissed)
- A one-line rationale for the categorization

## Output Format

Present the verdict in this structure:

### Intent
> [The stated intent paragraph from Step 2]

### Reviewers
- Reviewer [label]: [model name], [N findings] (one bullet per reviewer)

### Act On
[Findings that should be addressed. For each: description, which models raised it, why it matters.]

### Consider
[Findings worth thinking about. For each: description, which models raised it, tradeoff involved.]

### Noted
[Valid but low-priority. Brief list.]

### Dismissed
[Rejected findings with brief rationale.]

### Agreement Map
[Where did models agree, where did they diverge, and what does the pattern of agreement/disagreement tell us?]
