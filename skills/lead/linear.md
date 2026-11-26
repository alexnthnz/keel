# Linear conventions

Shared reference for `to-spec`, `to-tickets`, and any playbook that reads or writes Linear. The conventions below apply to the On-call team, key `ARC`. Check them with `list_issue_statuses` before relying on them for another team.

## States

| State | Meaning |
|---|---|
| Backlog | Not ready. Nobody builds it. |
| Todo | Ready. The ticket is complete and unclaimed. |
| In Progress | Claimed. A builder is working on it. |
| In Review | In QA. A verified PR exists and waits for the operator. |
| Done | The PR has landed. |
| Canceled, Duplicate | Closed without work. |

## Labels

`needs-alex` marks a ticket handed back after two fix rounds, or a question only the operator can answer. The label does not exist yet. If it is missing, report that to the lead, leave the ticket In Progress, and add a comment saying it needs Alex. The lead creates the label on Alex's go. No subagent ever asks a person.

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
