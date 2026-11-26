### Evening session

**You run the one session where Alex is present. Leave it with the day's verified PRs landed or sent back, the next objective chosen and grilled, and the night run started.**

The session starts when Alex opens it, around 7 PM. Conventions for states, labels, documents and the claim rule are in `linear.md`. The team is whichever team owns the project, and states are mapped by type. Ready is the `unstarted` state, In QA is the state Linear calls In Review, and Backlog is never promoted automatically. Only Alex promotes a Backlog ticket, and only in this session.

1. **Open with what waits on Alex.** List the project's tickets that are In QA and the PR behind each one. Read each PR's verifier verdict from the PR comments and from the day build's critic report. Run the **ketchup** skill over this list and present every item as an action item with your pick: land, fix, or hand back. A pass is `PASS` or `PASS+NOTES`. A `FAIL`, or a PR whose head moved since its verdict, is a fix.
2. **Show the tickets labelled `needs-alex`.** Each one was handed back after two fix rounds or holds a question only Alex can answer. For each, state what was tried and give your pick: reshape the ticket, answer the question, or drop it.
3. **Show the discovered-work document.** Read `Discovered work: <project>` and show its items, newest first. Alex may promote an item to Ready, fold it into the next objective, or drop it. Promotion is his call and never yours.
4. **Land what Alex approves.** Land the passes Alex chose with `playbooks/shipping.md`, bottom-up, each on a verdict that covers its current head. A PR Alex fails is a QA failure: move its ticket back to Ready, record Alex's reason on the ticket as a comment, and count it as a fix round. A ticket whose second fix round fails gets `needs-alex`. Move each landed ticket to Done.
5. **Alex picks the next objective.** Offer the discovered-work items Alex promoted and the next unstarted objective in the project, with your pick. Then propose a mode, as the lead skill's routing says, and wait for Alex to confirm or change it. Apply Pocock's session-count test, which asks how many agent sessions it takes to hold the whole objective.

   | Mode | Test | The night run produces |
   |---|---|---|
   | Quick | One small change that one session finishes as one ticket. | One ticket in the brief, no spec. |
   | Feature | One session can hold the whole objective, and it needs more than one ticket. | A `Spec:` document and a day-sized slice plan. |
   | Initiative | It takes more than one session, or the way to the destination is not yet visible. | A `Chart:` document, the ready research items resolved, and a `Spec:` document only if the chart clears. |

6. **Grill the decisions.** Run **grilling** on the objective. Before each round, send facts to `Explore` and settle technical forks with a prototype per `playbooks/prototype.md`, so Alex sees only product and preference questions. Run **domain-modeling** as answers land, so each confirmed term and decision goes to arcflux-memory with its source. For an Initiative, also grill the ready Grilling items on its `Chart:` document.
7. **Check what the night run needs.** Confirm the objective in one line, the confirmed mode, the project, the target repo and the memory scope. If the `needs-alex` label is missing, say so and ask Alex for his go to create it.
8. **Start the night run.** From the target repo, start a background lead session. The kickoff opens with the worker line and follows this template. Fill every field from this session, since the night run cannot ask.

   ```bash
   claude --bg "Read <skills dir>/lead/worker.md before anything else.
   Run the Night plan playbook at <skills dir>/lead/playbooks/night-plan.md.
   Objective: <one line>. Mode: <Quick|Feature|Initiative>, confirmed by Alex.
   Project: <Linear project>. Repo: <path>. Memory scope: org/arcflux/proj/<project>.
   Decisions already made, with their arcflux-memory pointers: <list>.
   Skills directory: <skills dir>.
   Create no tickets. Stop when the morning brief exists."
   ```

   Run `claude agents` and confirm the session is listed. Give Alex its id and the `claude logs <id>` command.
9. **Stop** when the night run has started, or when Alex ends the session. If Alex ends early, leave the discovered-work document and the ticket states as they stand, and say what the next evening must pick up.

**Reply:** the PRs landed, sent to fix and handed back, the `needs-alex` tickets and what Alex decided on each, the mode and objective chosen, the decisions grilled and where they are recorded, and the night run's session id.
