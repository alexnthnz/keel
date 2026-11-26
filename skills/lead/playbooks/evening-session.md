### Evening session

**You run the one session where Alex is present. Leave it with the day's verified PRs landed or sent back, the next objective chosen and grilled, and the night run started.**

The session starts when Alex opens it, around 7 PM. Conventions for states, labels, documents and the claim rule are in `linear.md`. The team is whichever team owns the project, and states are mapped by type. Ready is the `unstarted` state, In QA is the state Linear calls In Review, and Backlog is never promoted automatically. Only Alex promotes a Backlog ticket: in this session, or by his Go on a morning brief that lists `promote <id> from Backlog`.

1. **Open with what waits on Alex.** List the project's tickets that are In QA and the PR behind each one. Read each PR's verifier verdict and the day build's critic report from the PR comments. Run the **ketchup** skill over this list and present every item as an action item with your pick: land, fix, or hand back. A pass is `PASS` or `PASS+NOTES`. A `FAIL`, or a PR whose head moved since its verdict, is a fix.
2. **Show the tickets labelled `needs-alex`.** Each one was handed back by the lead after two failed fix rounds, or holds a question only Alex can answer. For each, state what was tried and give your pick: reshape the ticket, answer the question, or drop it. When Alex answers, remove `needs-alex`, set the ticket to Ready, clear its assignee (`assignee: null`), and comment "fix rounds reset by Alex: <his answer>". His answer starts a fresh two rounds, so count only rounds after that comment. A ticket he drops goes to Canceled.
3. **Show the discovered-work document.** Read `Discovered work: <project>` and show only its unmarked items, newest first. If the document does not exist, say "none". Alex may promote an item into the next objective or drop it. Promotion is his call and never yours. Mark each item in the document "promoted <date>" or "dropped <date>", so the next evening does not show it again.
4. **Land what Alex approves.** Land the passes Alex chose with `playbooks/shipping.md`, bottom-up, each on a verdict that covers its current head. A PR Alex fails is a QA failure and counts as a fix round. Count the rounds already recorded in the ticket's comments, counting only rounds after the latest "fix rounds reset by Alex" comment. If this is round 1 or 2, set the ticket to Ready **and clear its assignee** (`assignee: null`), because the day build queue takes only unassigned tickets. Write the ticket comment "fix round n of 2: <reason>" with the PR link and its branch name, so the day build reuses that branch. If two rounds are already recorded, add `needs-alex`, leave the ticket In Progress with its assignee, and comment what failed. Move each landed ticket to Done.
5. **Alex picks the next objective.** Alex names the objective. Offer, with your pick, the discovered-work items he promoted tonight and any `Spec:` document whose tickets are not all Done. An objective is not a milestone: milestones are the phases Alex sets, and tickets carry the current milestone as `linear.md` defines it. Then propose a mode, as the lead skill's routing says, and wait for Alex to confirm or change it. Apply Pocock's session-count test, which asks how many agent sessions it takes to hold the whole objective.

   | Mode | Test | The night run produces |
   |---|---|---|
   | Quick | One small change that one session finishes as one ticket. | One ticket in the brief, no spec. |
   | Feature | One session can hold the whole objective, and it needs more than one ticket. | A `Spec:` document and a day-sized slice plan. |
   | Initiative | It takes more than one session, or the way to the destination is not yet visible. | A `Chart:` document, the ready research items resolved, and a `Spec:` document only if the chart clears. |

6. **Grill the decisions.** Run **grilling** on the objective. Before each round, send facts to `Explore` and settle technical forks with a prototype per `playbooks/prototype.md`, so Alex sees only product and preference questions. Run **domain-modeling** as answers land, so each confirmed term and decision goes to arcflux-memory with its source. For an Initiative, grill the ready Grilling items on its `Chart:` document. If no `Chart:` document exists yet, grill the destination and the first frontier with Alex, per **wayfinder** charting steps 1 and 2, and pass the answers in the night kickoff.
7. **Check what the night run needs.** Confirm the objective in one line, the confirmed mode, the project, the target repo and the memory scope. If the `needs-alex` label is missing, say so and ask Alex for his go to create it. If the team has no project yet, ask Alex for the project's name and its first milestone, then create the project with `save_project` (`name`, `addTeams` with the team, and a one-line `summary`) and the milestone with `save_milestone` (`project`, `name`). There is one long-lived project per team, with a milestone for each stretch of work. Each objective's spec is a document in it, and one `Discovered work: <project>` document covers the whole project. Do this only here, with Alex present. The night run never creates a project.
8. **Start the night run.** From the target repo, start a background lead session. The kickoff opens with the worker line and follows this template. Fill every field from this session, since the night run cannot ask.

   ```bash
   claude --bg --name night-<YYYY-MM-DD> "Read <skills dir>/lead/worker.md before anything else.
   Read <skills dir>/lead/SKILL.md.
   keel skills refuse the Skill tool: load each one by reading <skills dir>/<name>/SKILL.md.
   Run the Night plan playbook at <skills dir>/lead/playbooks/night-plan.md.
   Session name: night-<YYYY-MM-DD>.
   Objective: <one line>. Mode: <Quick|Feature|Initiative>, confirmed by Alex.
   Project: <Linear project>. Repo: <path>. Memory scope: org/arcflux/proj/<project>.
   Decisions already made, with their arcflux-memory pointers: <list>.
   Promoted discovered-work items, to draft as tickets: <list, or none>.
   Destination answers, for a new Initiative: <destination and first frontier, or none>.
   Skills directory: <skills dir>.
   Create no tickets. When the morning brief exists, stop working and wait in this session for Alex's Go."
   ```

   Run `claude agents` and confirm the session is listed. Give Alex both commands: `claude logs night-<YYYY-MM-DD>` to read the morning brief, and `claude attach night-<YYYY-MM-DD>` to open the session and answer "Go".
9. **Stop** when the night run has started, or when Alex ends the session. If Alex ends early, leave the discovered-work document and the ticket states as they stand, and say what the next evening must pick up.

**Reply:** the PRs landed, sent to fix and handed back, the `needs-alex` tickets and what Alex decided on each, the mode and objective chosen, the decisions grilled and where they are recorded, and the night run's session name.
