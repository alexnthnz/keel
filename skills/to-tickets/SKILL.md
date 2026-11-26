---
name: to-tickets
description: "Break a spec or objective into day-sized, one-PR Linear tickets as tracer-bullet slices with blocking links. Draft mode writes nothing; create mode runs only after the operator says Go."
disable-model-invocation: true
---

# To Tickets

> Adapted from `to-tickets` and `triage/AGENT-BRIEF.md` in [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, commit `6f7f783`). Local edits: Linear only, two modes, one issue per PR with no sub-issues, a plan sized to one day shift, a numbered preview before any write, and a ticket body built from the agent brief with no file paths. See [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).

Break an objective into **tickets**: tracer-bullet vertical slices, each with the tickets that block it. One slice is one Linear issue and one issue is one PR. Conventions are in [`../lead/linear.md`](../lead/linear.md).

## Modes

- **Draft.** For the night run and any run without the operator. Do every step up to the numbered list. Write nothing to Linear. Return the list.
- **Create.** Runs only after the operator says "Go" to a list you showed. Create exactly what the list said.

Without a clear mode, use draft.

## Process

### 1. Gather context

Load the team's labels with `list_issue_labels` (`team`, `includeGroups: true`) and the project's milestones with `list_milestones`. For each slice, choose the module label whose description best matches the slice's area. Put every unclear pick in the assumptions.

Read the spec document (`Spec: <objective>`) from the project, or the objective itself for Quick work with no spec. If a Feature or Initiative has no `Spec:` document, stop and report it. Do not create tickets with a dead link. Read the issues already in the project with `list_issues`, so the plan reuses or edits a matching ticket instead of duplicating it.

### 2. Explore and prefactor

Read the code the work touches. Look for a change that makes the real one easy ("make the change easy, then make the easy change") and put it first.

### 3. Draft vertical slices

- Each slice cuts a narrow but complete path through every layer: vertical, not one layer.
- A finished slice is demoable or verifiable on its own and fits one PR.
- Size the whole plan to one day shift. Start at 3 to 5 slices. That number is a guess to tune: the evening review shows whether it was right.
- Prefactoring goes first.
- Give each slice its blocking edges. Use `blockedBy` only for a real gate: the blocked ticket cannot be built or verified without the other.
- Quick work is one ticket and no spec.

**Wide refactors** are the exception to vertical slicing: one mechanical change that fans across the whole codebase. Follow **principle-migrate-callers-then-delete-legacy-apis**: migrate the callers and delete the legacy API in one wave. Use expand and contract (add the new form, migrate callers in batches, delete the old form) only when callers cannot change in one deploy. The ticket then states that reason.

### 4. Show the list

Present a numbered list. For each slice:

- **Title**
- **Outcome**: one line
- **Blocked by**: slice numbers, or none
- **Module**: the module label, as `linear.md` says

When an existing ticket is bigger than one slice, narrow it to one slice and list the rest as new slices. A matched ticket that sits in Backlog is marked `promote <id> from Backlog`: it moves to Ready only if Alex approves the list. Then the counts: new issues, narrowed or otherwise edited issues, promotions from Backlog, and the size of the backlog afterwards. The counts show every narrowing. In draft mode, stop here and return it. In create mode, wait for "Go". Revise on any answer other than "Go". Only the lead shows the list and waits for "Go". A subagent runs create mode only when the approved list is pasted into its kickoff, and it creates exactly that list.

### 5. Create

Only after "Go". Create tickets in dependency order, so each blocker has its identifier before the ticket it blocks.

- Read the team's states with `list_issue_statuses` and find Ready by the mapping in `linear.md`. If it is missing, report that and stop.
- Call `save_issue` with the team, the project, the Ready state, and `blockedBy` set to the blocker identifiers. Also pass `labels` (the module label) and, when the project has milestones, `milestone` (the current one), as `linear.md` says. Both parameters exist on `save_issue`: `labels` replaces the full label set, so on an existing issue use `addLabels`.
- Never set `parentId`. Never apply `needs-alex`.
- Edit a matching existing issue instead of creating a duplicate. Editing does not change an existing issue's state. After "Go", move exactly the issues the list marked `promote <id> from Backlog` to Ready, and no other Backlog issue.
- Do not close or modify any other issue.

Report the identifiers and the blocking edges you set.

## Ticket body

The body stays true for days while the code changes. Describe interfaces, types and behaviour. Leave out file paths, line numbers and the current code structure. Paths belong to the lead's kickoff.

```markdown
**Outcome:** one line.

**Spec:** link to the `Spec: <objective>` document.

**Current behaviour:** what happens now, or the status quo this builds on.

**Desired behaviour:** what happens after, including edge cases and errors.

**Interfaces and data shape:** the types, signatures, config or schema that change, and why.

**Pass predicates**
- [ ] Each checkable, and each failing at the base commit. Run it before you write it.

**Out of scope**
- Adjacent work this ticket must not touch.

**Verification surface:** where and how the builder proves it, and the scenario.
```

A prototype snippet that states a decision better than prose may go in the interfaces section. Say that it came from a prototype.

## Reply

The numbered list and counts, then the assumptions you made. In create mode, the identifiers instead of the list.
