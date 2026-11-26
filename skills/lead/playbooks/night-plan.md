### Night plan

**You run with nobody present. Turn one confirmed objective into a spec, a draft slice plan and a one-screen brief, and create no ticket.**

This runs in a `claude --bg` lead session that the Evening session started. The same session runs Day build after Alex's "Go", so it stays alive when the brief is written. Nobody answers questions, so never grill and never ask. When a decision is open, apply the recommended answer and record it as an assumption. Conventions for documents and labels are in `linear.md`. The team is whichever team owns the project.

1. **Read the kickoff.** It names the objective, the mode, the project, the repo, the memory scope, the decisions already made, the promoted discovered-work items and, for a new Initiative, the destination answers that start the chart. Read those decisions from arcflux-memory with `search_memory` and `read_facts`, and treat them as settled. Open a decision log with **show-me-your-work**.
2. **Research.** Send read-only `Explore` subagents at the facts the work needs, one question each. Each kickoff opens with `Read <skills dir>/lead/worker.md before anything else.` Write each fact that matters to arcflux-memory with `remember`, with its source. Label each fact measured, inferred or guessed.
3. **Architect.** Name the data shape first, per the lead skill. For a change across a function boundary, use **architect**. List the technical forks that remain.
4. **Prototype the forks.** Settle each technical fork by running something, per `playbooks/prototype.md`, instead of choosing on paper. When two variants differ only by taste, apply your recommended one and list it as an assumption.
5. **Initiative only: chart or resolve.** Run **wayfinder**. If no `Chart:` document exists, chart one. Otherwise resolve every ready research item and record each result in arcflux-memory with `standing: proposed`. Never resolve a Grilling item, because it waits for the Evening session. If the chart does not clear, skip steps 6 and 7 and put the open Grilling items in the brief as blocked.
6. **Spec.** For a Feature, or an Initiative whose chart cleared, run **to-spec**. It writes the `Spec:` document, because the tickets' links need it. A Quick objective has no spec.
7. **Draft the tickets.** Run **to-tickets** in draft mode. It sizes the plan to one day shift and returns the numbered list and counts. Include every promoted discovered-work item from the kickoff in the draft. Each slice maps to one PR and has no parent. It creates nothing.
8. **Write the morning brief.** Write it with **show-me-your-work** beside the decision log, and make it the session's last message, so `claude logs <id>` shows it. Alex reads it there, or after `claude attach <id>`, and types "Go" in the attached session. It fits one screen, about 25 lines, and holds only:
   - the outcome, in one or two sentences
   - a link to the `Spec:` document, or "no spec, Quick" for a Quick objective
   - the numbered slices, each as `1. <title>: <outcome> (blocked by: none)`, then the counts: new tickets, edited tickets, and the backlog size afterwards
   - at most three assumptions, each with the answer you applied. If more than three arose, keep the three that change the plan most and record the rest in the decision log
   - anything blocked, which waits for 7 PM

   Also write the full draft list, the **to-tickets** draft output, into the decision log under `keel-store`, so it survives if this session dies. The brief names the log's path.

   It ends with the line `Attach with claude attach <id> and reply Go to create these tickets.`, with the real session id filled in.
9. **Wait** when the brief exists. Do not exit and do not start Day build on your own. Create no ticket, add no label, change no state, and write nothing to Linear except the `Spec:` and `Chart:` documents.

**Reply:** the brief, the link to the spec, and the decision log path. Day build starts only when Alex attaches with `claude attach <id>` and types "Go". This same session then runs `playbooks/day-build.md`.
