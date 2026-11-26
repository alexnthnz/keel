# Linear conventions

Shared reference for `to-spec`, `to-tickets`, and any playbook that reads or writes Linear. The conventions below apply to any Linear team. The team is whichever team owns the project.

## States

At the start of a run, call `list_issue_statuses` for the project's team and map the states by type and name:

| Role | State | Meaning |
|---|---|---|
| Ready | the `unstarted` state (Todo) | The ticket is complete and unclaimed. |
| In Progress | the `started` state named "In Progress" | Claimed. A builder is working on it. |
| In QA | the `started` state named "In Review" | A verified PR exists and waits for the operator. |
| Done | the `completed` state | The PR has landed. |

If a state that a mapping needs is missing, report that to the lead and stop. Never create states.

Backlog (type `backlog`) means not ready: nobody builds it. Backlog is never promoted automatically. Only Alex promotes a Backlog issue, and only in the 7 PM session. Canceled and Duplicate are closed without work.

## Labels and milestones

When the project uses module labels or milestones, each ticket carries its module label and the current milestone. Still no `parentId`.

`needs-alex` marks a ticket handed back after two fix rounds, or a question only the operator can answer. The lead creates it once per team, on Alex's go. If it is missing, report that to the lead, leave the ticket In Progress, and add a comment saying it needs Alex. No subagent ever asks a person.

## Documents

Documents attach to the project or Initiative, never to an issue.

| Title | Written by | Holds |
|---|---|---|
| `Spec: <objective>` | `to-spec` | The one-page spec for a Feature or Initiative objective. |
| `Chart: <initiative>` | `wayfinder` | The open-decision chart for an Initiative. |
| `Discovered work: <project>` | the lead | Findings that surfaced during a run and belong to no ticket. One document per project, appended to. |

## The claim rule

Before work starts on a ticket, set its state to In Progress and its assignee. Skip every ticket that is already In Progress or already has an assignee. Claim first, then spawn the builder, so two lanes never take the same ticket.

## Blocking

Order uses Linear's native `blockedBy` and `blocks`. Never set `parentId`: one slice is one issue, and one issue is one PR.

Linear's blocked-by data can go stale during a run. If a ticket looks blocked by a ticket that is already Done, or looks free while its blocker is open, trust the PR state, and track blocking in `keel-store` for the rest of the run.

## The two-layer contract

A ticket has two layers.

**The durable ticket** stays true for days. It holds the outcome, the link to the spec, current and desired behaviour, interfaces and data shape, pass predicates that fail at the base commit, what is out of scope, and the verification surface. It holds no file paths. `to-tickets` writes it.

**The kickoff** is written by the lead when it dispatches the builder, and ends with the run. It adds:

- file paths, found by reading the code at dispatch time
- the base branch
- the merge policy: stop at verified, never merge
- the fix cap: two fix rounds, then label the ticket `needs-alex` and stop (if the label is missing, leave the ticket In Progress and comment that it needs Alex)
- the discovered-work rule: report anything found outside the ticket to the lead, which appends it to the discovered-work document. Never open a PR for it.
- a note that Linear writes on this project (claim, state moves, comments) count as part of the run, so `worker.md`'s stop before "a message to someone outside the run" does not apply to them

## Writing to Linear

Check for an existing issue or document with the same title before creating one. Send markdown with real newlines. Put long agent-only detail in a collapsible `+++ Agent notes` section at the end of the description.
