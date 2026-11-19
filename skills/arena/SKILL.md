---
name: arena
description: "Spawn N parallel candidates at the same task, pick a base, graft the strongest parts of the losers into it. Use for /keel:arena, 'arena this', 'throw it in the arena', or when one attempt at a non-trivial artifact would lock in the wrong shape."
disable-model-invocation: true
---

# Arena

Other keel skills named here sit beside this one at `${CLAUDE_SKILL_DIR}/../<name>/SKILL.md`, and a principle at `principle-<name>`. The Skill tool refuses them, so read the file and follow it.

Open a todolist with one entry per phase (Frame, Fan out, Cross-judge, Pick, Graft, Verify) before launching anything.

## Phase A: Frame

Every candidate gets the same prompt, so the prompt is the contract.

1. State the artifact each candidate is producing.
2. Derive the rubric, 3-6 concrete gradeable criteria for what success looks like on *this* task. It is the picker's tool in Phase D. Candidates only see the task.
3. Pick the runners from the `arena runners` line. Read `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/keel-models.md` if it exists; use the role's line, else the default, one runner each on `opus`, `fable`, and `sonnet`, each at effort `high`. Three different Claude models give the panel its diversity. An `inherit`, `inherit-parent`, or `auto` entry is the parent model, so omit `model` for it. If the Agent tool rejects an entry, drop that seat, keep at least two runners, and say so. Spawn more for multiple design directions, and repeat one model when the work is generation-bound, not judgment-sensitive. Pick each subagent's effort for the job, per the Subagents section of the **lead** skill.
4. Give each candidate its own output location (a git worktree where possible, via `isolation: "worktree"` on its Agent call, otherwise `/tmp/arena-<slug>/candidate-<n>/`), per the **separate-before-serializing-shared-state** principle skill.

## Phase B: Fan out

Spawn all N subagents in one message, each with the task, the path to the shared grounding, its own output path, and instructions to produce the artifact and a short rationale naming the alternatives it considered and what it rejected.

Subagents run in the background and the parent is notified as each completes, so never poll or sleep-wait. If a candidate produces no output, proceed with N-1 and note the dropout.

## Phase C: Cross-judge

After all Phase B candidates complete, choose one model from the `arena cross-judge pool` line. Read `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/keel-models.md` if it exists; use the role's line, else the default pool of `opus` and `sonnet`. Spawn one read-only judge subagent, its prompt opening with "Read-only: do not edit files." The judge is never on the parent's model. Try only the entries that name a different model from the parent's, in pool order. An `inherit`, `inherit-parent`, or `auto` entry is the parent model, so it never judges. If the Agent tool rejects an entry, move to the next one. If no entry runs, try the default pool's entries other than the parent's model the same way. If none of those runs, skip the judge, pick the base alone in Phase D, and say so. If you do not know the parent's model, use the first entry and say that the parent-model check did not run. While you read in Phase D, the judge scores each candidate, by path label, on each rubric criterion and recommends a base.

## Phase D: Pick a base

Read every candidate end to end before picking. Score each against the rubric criterion by criterion, not on holistic feel, and compare with the cross-judge when Phase C ran one. Agreement on the base confirms the pick. Disagreement means one of you is biased or the rubric was ambiguous. Read both rationales before deciding.

Pick the base a future maintainer can extend most easily without breaking invariants. When two feel tied, prefer the cleaner boundary or smaller API, per the Laziness Protocol.

## Phase E: Graft

Walk each losing candidate once more for what is worth porting into the base, usually one or two things per candidate, not most of it. Fold each graft in by hand, per the **redesign-from-first-principles** principle skill, so the result stays coherent under one mental model. Don't paste mechanically.

If the candidates converge on one shape, that is strong agreement. Note it and ship the consensus shape. No graft is needed. If they wildly diverge, Phase A was under-specified. Reframe and re-run rather than averaging the divergence.

## Phase F: Verify

Verify the synthesized artifact like any other output, per the **prove-it-works** principle skill. If verification finds a problem the arena missed, either Phase A was wrong (re-frame and re-run) or a candidate caught it and you missed the graft (go back to Phase E). Don't paper over it.

## Outputs

One synthesized artifact, with a short synthesis note alongside naming the base and why, the cross-judge's verdict or that Phase C skipped the judge, each graft with its source candidate, what was rejected and why, any convergence or dropouts, and the verification result.
