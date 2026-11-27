# The daily cycle

keel can run planning and building as a daily cycle. You spend one evening session deciding, agents plan overnight, and agents build during the day. This chapter explains how the cycle works and why it is shaped that way. It also gives the prompts that [start each part of the cycle](#starting-each-part-of-the-cycle) and that [run keel without it](#running-keel-without-the-cycle). For more prompts to copy, see [Recipes and pitfalls](./10-recipes-and-pitfalls.md).

The cycle is optional. Bug fixes, quick changes and investigations still go straight through [`/lead`](./02-lead.md) to a playbook. The cycle is for objectives that need a plan.

## The four shifts

| Shift | Time | Who | What happens |
|---|---|---|---|
| Evening | 7 PM to midnight | You and the lead | You QA the PRs that were verified today and land them. You pick the next objective and answer the product questions about it. |
| Night | Overnight | Agents alone | Agents research, design and prototype. They write the spec and draft a slice plan sized to one day. They create no tickets. |
| Morning | When you wake | You | You read a one-screen brief and answer "Go". The lead then creates the tickets. |
| Day | Until 7 PM | Agents | Agents build each ticket and verify the work. They leave verified PRs for the evening. |

The shifts repeat. The evening session reads what the day produced and feeds the next night.

## Where you are in the loop

You touch the cycle at three points, and nowhere else.

1. **The evening session.** You decide what lands, what goes back for a fix, and what the next objective is. This is the only time agents ask you questions.
2. **The morning "Go".** You read the brief and approve the ticket list. Nothing is created in Linear before you say it.
3. **Promotion.** Backlog tickets are never promoted automatically. You promote them in the evening session, or with your Go on a morning brief that lists `promote <id> from Backlog`.

Everything between those points runs without you. Agents that need a human decision during the night or the day do not ask. The night run applies the recommended answer and lists it as an assumption in the brief. A day builder hands the ticket back with the label `needs-alex`, and you see it at 7 PM.

## The three playbooks

Each shift has a [playbook](../../skills/lead/playbooks/). The lead reads the playbook and follows its steps.

**[Evening session](../../skills/lead/playbooks/evening-session.md).** The lead lists the day's verified PRs and each verifier's verdict as `ketchup` action items: land, fix, or hand back. It lands the passes with the [Shipping](../../skills/lead/playbooks/shipping.md) playbook. A PR that fails your QA sends its ticket back to Ready, unassigned, and counts as a fix round. The lead also shows the tickets labelled `needs-alex`. Once the day build has stopped, the lead also releases any ticket it left In Progress with nobody working on it, such as one the 7 PM stop cut off or one whose session died. Only tickets listed in the last day build's decision log are released, so a ticket you claimed by hand stays as it is. The ticket goes back to Ready and unassigned, so the next day build reuses its branch. If the day build is still working, or the lead finds no decision log, it leaves those tickets alone. The lead then shows the project's `Discovered work` document, where you promote items into the next objective or drop them. You then name the next objective. The lead proposes a mode and you confirm it. It grills the decisions and starts the night run with `claude --bg`.

**[Night plan](../../skills/lead/playbooks/night-plan.md).** A background lead session runs with nobody present. It researches with `Explore` subagents and writes facts to arcflux-memory. It designs the change and prototypes the technical choices. For an Initiative it charts the open decisions. It writes the spec, drafts the slice plan, and ends with the morning brief. It creates no tickets.

**[Day build](../../skills/lead/playbooks/day-build.md).** After your "Go", the lead creates the tickets. It then runs the [Autopilot-stack](../../skills/lead/playbooks/autopilot-stack.md) playbook over the brief's tickets that are Ready and not blocked. Those include the carried-over tickets, which [Night plan](../../skills/lead/playbooks/night-plan.md) step 6 defines. Carried-over tickets count toward the day's size, so a full day gets no new slices. The lead leaves any other Ready ticket alone and names it in the reply. Each ticket gets its own `keel:ponytail` builder in its own worktree, and the lead claims it first. One batched `keel:critic` pass reviews all of the day's PRs together. A verified PR moves its ticket to In QA. Nothing merges.

### Overrides the day build applies

Autopilot-stack and the playbooks under it were written for a different setting, so the day build changes four of their rules in each builder's kickoff. `worker.md` says that "the bar in your kickoff is the whole bar", and that is what makes an override work without editing the original file.

- **Discovered work goes to the lead.** A builder never opens a PR for something it finds outside its ticket. It reports the finding, and the lead alone appends it to the discovered-work document. You decide in the evening whether it becomes a ticket.
- **Two fix rounds, then a hand-back.** A ticket gets at most two fix rounds. After that it carries `needs-alex`, because a third round on the same ticket rarely converges.
- **Linear writes are part of the run.** Claiming a ticket, moving its state and commenting are not messages to someone outside the run.
- **The queue is Linear.** The queue comes from Linear, not from GitHub, and one critic pass covers every PR instead of one review per PR.

## Choosing a mode

When you name an objective in the evening session, the lead proposes one of three modes and you confirm it. The test is how many agent sessions it takes to hold the whole objective.

| Mode | Test | What the night produces |
|---|---|---|
| Quick | One small change, one ticket. | A single ticket, with no spec. |
| Feature | One session can hold it, and it needs several tickets. | A one-page spec and a day-sized slice plan. |
| Initiative | It takes more than one session, or the route is unclear. | A chart of open decisions, resolved research items, and a spec once the chart clears. |

## The five planning skills

keel adapts five planning skills from [Matt Pocock's skills](https://github.com/mattpocock/skills). The playbooks call them at fixed points. You can also run each one yourself.

- **[`/keel:grilling`](../../skills/grilling/SKILL.md)** interviews you in rounds. Each question comes with a recommended answer, so you can approve a round quickly. It runs in the evening session, and it never runs overnight.
- **[`/keel:domain-modeling`](../../skills/domain-modeling/SKILL.md)** records confirmed terms and decisions in arcflux-memory, so the night run starts from what you settled.
- **[`/keel:wayfinder`](../../skills/wayfinder/SKILL.md)** charts an Initiative's open decisions in one Linear document. Research items resolve overnight. Questions for you wait for the evening.
- **[`/keel:to-spec`](../../skills/to-spec/SKILL.md)** writes the one-page spec: the outcome, what is out of scope, the pass predicates that fail on today's trunk, and where to verify.
- **[`/keel:to-tickets`](../../skills/to-tickets/SKILL.md)** splits the spec into one-day slices. Each slice is one ticket and one PR, and no ticket has a parent. It drafts at night and creates tickets only after your "Go".

## Starting each part of the cycle

Start every session from the target repo, the repo that the tickets change.

- **The evening session.** At 7 PM, open Claude Code and type `/keel:lead evening session for <project>`, with the Linear project's name. The lead runs the Evening session playbook. To plan something overnight, start an evening session this way, whatever the time. Asking the lead to plan something overnight, for example "plan the export feature overnight", also starts an evening session.
- **The night run.** You do not start it yourself. The evening session starts it as its last step, in a background session named `night-<YYYY-MM-DD>`, and gives you the two morning commands.
- **The morning.** Read the brief with `claude logs night-<YYYY-MM-DD>`. Open the session with `claude attach night-<YYYY-MM-DD>` and type "Go". That session then runs Day build.
- **A day build after the night session is gone.** Open a new lead session and give it the decision log path from the brief, for example `/keel:lead day build for <project> from the decision log at <path>. Go.` It reads the saved list from that log.
- **A night run that died before its brief.** Night plan has no restart step. Reopen the evening session with `claude --resume`, which lists past sessions, and ask the lead to start a new night run under a new name, such as `night-<YYYY-MM-DD>-2`. Use that name in the morning commands. The new run updates any `Spec:` or `Chart:` document the first run wrote instead of creating a second one.
- **Stopping a session.** `claude stop` takes the session id, not its name, and `claude agents` lists the ids. A stopped session keeps its conversation, and `claude attach <id>` resumes it. `claude attach` and `claude logs` also accept part of the session name.

## Running keel without the cycle

Everything in keel also runs by hand, in the session you are in. Only an objective for the cycle gets a [mode proposal](#choosing-a-mode), and any other request goes straight to its playbook. When the lead cannot tell which you mean, it runs the work by hand. If that work looks Initiative-sized, it also mentions the cycle in one line.

To ask for work now, end the request with "now, in this session":

```text
/keel:lead add a --json flag to this command, now, in this session
```

Initiative-sized work that you run by hand goes to [`/keel:figure-it-out`](../../skills/figure-it-out/SKILL.md), which designs the run's phases and keeps a decision log. For a plan of small PRs that you approve before anything is built, ask for the [Multi-phase plan](../../skills/lead/playbooks/multi-phase-plan.md) playbook. It writes a plan file and stops, and building starts on your go.

```text
/keel:lead move every service to the new config loader, now, in this session
/keel:lead write a multi-phase plan for moving billing to the new ledger
```

Each planning skill also runs on its own:

- `/keel:grilling the retry policy for the webhook sender` interviews you in rounds until every decision is settled. It needs only you. It writes nothing but throwaway prototypes in a scratch directory, which settle technical forks. Run domain-modeling next to it to record the answers.
- `/keel:domain-modeling settle what "refund" means in <project>` needs the arcflux-memory server. It writes terms to the `org/arcflux/proj/<project>` scope and decisions to `org/arcflux/proj/<project>/decisions`, and it creates no files.
- `/keel:wayfinder chart the move to multi-region for <project>` needs a Linear project or Initiative and arcflux-memory. It grills you for the destination and the first open decisions, then writes one `Chart: <initiative>` document. It creates no tickets and no code.
- `/keel:to-spec for <objective> in <project>` needs decisions that are already settled, because it asks you nothing. It writes or updates the `Spec: <objective>` document on the Linear project, or on the Initiative when there is no project.
- `/keel:to-tickets create the tickets for Spec: <objective> in <project>` needs the `Spec:` document, except for a Quick change. It shows a numbered list of slices and, only after you reply "Go", creates the new ones as Ready tickets with their blocking links. An existing ticket it edits keeps its state. Without "create", it drafts the list and writes nothing.

## Why it is shaped this way

The cycle puts the human's attention where it is scarce. Judgment calls, such as what to build and whether the result is right, cost you the most and happen in one session. Reading code, trying options and writing tickets cost agents little and happen while you are away.

The morning brief is the other design choice. It fits one screen, so a "Go" is a light decision. It holds the outcome, a link to the spec, the numbered slices, the carried-over tickets, at most three assumptions and anything blocked. If the brief runs longer, the night run decided too much without you.

The two-fix-round cap, the no-PR rule for discovered work and the single "Go" gate are guesses about what keeps a day's work reviewable. The evening review is how you measure them. If a day regularly leaves more than you can QA, shrink the slice plan.

## What the cycle needs

- A Linear project, whose team owns the tickets. States are matched by type: Ready is the `unstarted` state.
- The `needs-alex` label on that team.
- The arcflux-memory server, for the facts and decisions.
- A repo you can start `claude --bg` sessions from.

Next: back to the [guide index](./README.md).
