# The daily cycle

keel can run planning and building as a daily cycle. You spend one evening session deciding, agents plan overnight, and agents build during the day. This chapter explains how the cycle works and why it is shaped that way. It does not teach a task step by step. For prompts to copy, see [Recipes and pitfalls](./10-recipes-and-pitfalls.md).

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

**[Evening session](../../skills/lead/playbooks/evening-session.md).** The lead lists the day's verified PRs and each verifier's verdict as `ketchup` action items: land, fix, or hand back. It lands the passes with the [Shipping](../../skills/lead/playbooks/shipping.md) playbook. A PR that fails your QA sends its ticket back to Ready, unassigned, and counts as a fix round. The lead also shows the tickets labelled `needs-alex` and the project's `Discovered work` document, where you promote items into the next objective or drop them. You then name the next objective. The lead proposes a mode and you confirm it. It grills the decisions and starts the night run with `claude --bg`.

**[Night plan](../../skills/lead/playbooks/night-plan.md).** A background lead session runs with nobody present. It researches with `Explore` subagents and writes facts to arcflux-memory. It designs the change and prototypes the technical choices. For an Initiative it charts the open decisions. It writes the spec, drafts the slice plan, and ends with the morning brief. It creates no tickets.

**[Day build](../../skills/lead/playbooks/day-build.md).** After your "Go", the lead creates the tickets. It then runs the [Autopilot-stack](../../skills/lead/playbooks/autopilot-stack.md) playbook over the brief's tickets that are Ready and not blocked. Those are the new and edited slices, the Backlog tickets you promoted, and the carried-over tickets, which were already Ready when the brief was written. A Ready ticket that the brief does not list is left alone and named in the reply. Each ticket gets its own `keel:ponytail` builder in its own worktree, and the lead claims it first. One batched `keel:critic` pass reviews all of the day's PRs together. A verified PR moves its ticket to In QA. Nothing merges.

### Overrides the day build applies

Autopilot-stack and the playbooks under it were written for a different setting, so the day build changes four of their rules in each builder's kickoff. `worker.md` says that "the bar in your kickoff is the whole bar", and that is what makes an override work without editing the original file.

- **Discovered work goes to the lead.** A builder never opens a PR for something it finds outside its ticket. It reports the finding, and the lead alone appends it to the discovered-work document. You decide in the evening whether it becomes a ticket.
- **Two fix rounds, then a hand-back.** A ticket gets at most two fix rounds. After that it carries `needs-alex`, because a third round on the same ticket rarely converges.
- **Linear writes are part of the run.** Claiming a ticket, moving its state and commenting are not messages to someone outside the run.
- **The queue is Linear.** The queue comes from the brief's tickets in the Linear project, not from GitHub, and one critic pass covers every PR instead of one review per PR.

## Choosing a mode

When you name an objective for the cycle, in the evening session or as work to plan overnight, the lead proposes one of three modes and you confirm it. Work you ask for in the session you are in gets no mode proposal. The test is how many agent sessions it takes to hold the whole objective.

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
