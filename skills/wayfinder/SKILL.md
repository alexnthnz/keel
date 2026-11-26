---
name: wayfinder
description: "Plan an Initiative, too big for one agent session, as one chart of open decisions in a single Linear document, and resolve them one at a time. Plans and never builds. Use for /keel:wayfinder."
disable-model-invocation: true
---
<!-- Adapted from mattpocock/skills (MIT, https://github.com/mattpocock/skills), skills/engineering/wayfinder and docs/engineering/wayfinder.md at 6f7f783. Local edits are marked "keel edit". -->

A loose idea has arrived, too big for one agent session, and wrapped in fog: the way from here to the **destination** isn't visible yet. Wayfinding finds that way. It does not charge at the destination.

<!-- keel edit: everything below the header is keel's rewrite for Linear, arcflux-memory and the daily cycle. Upstream's map issue, child tickets, labels and assignee claims are dropped. The chart is one document. -->
## When to use it

Use it for **Initiative** work: more than one agent session, and the route still unclear. If the lead's session-count test says one session holds it, don't chart. Grill it with [`grilling`](../grilling/SKILL.md). If the way is already clear, go straight to `to-spec`.

## Plan, don't build

Wayfinder only produces decisions. It writes no code, opens no pull request, and creates no tickets. The pull to just do the work is the signal that you've reached the edge of the chart: hand off. An item that reads "build the X" is mis-typed, or belongs after `to-spec`.

## The chart

The chart is **one Linear document**, titled `Chart: <initiative>`, attached to the Initiative or its project. It creates **no child issues and no labels on issues**. Create it with `save_document` (omit `id`) and set `title`, `content`, and `project` or `initiative`. Update it later by `id`, and pass `patch` for part of it. Before you create it, call `list_documents` with `query: "Chart: <initiative>"` so you don't make a duplicate.

Refer to every item by its name, never by a bare number.

```markdown
## Destination

<what reaching the end looks like: the decision to lock, or the spec to hand to `to-spec`. One or two lines.>

## Open decisions

| Item | Question | Kind | Waits on |
|---|---|---|---|
| <name> | <one sharp question> | grilling / research / prototype | <item names, or "nothing"> |

## Decided

- <item name>: <one-line gist>. Memory: <scope>, <entity name>.

## Not yet specified

<in-scope fog you can't phrase sharply yet; it moves to Open decisions once you can>

## Out of scope

<ruled beyond the destination, with the reason; it never moves back>
```

**Fog or item.** The test is whether you can state the question precisely now, not whether you can answer it. A sharp question is an item, even when blocked. A vague one is fog. Don't pre-slice the fog.

## Item kinds

Every item has exactly one kind.

- **Grilling** (human in the loop). Resolved by [`grilling`](../grilling/SKILL.md) with [`domain-modeling`](../domain-modeling/SKILL.md), in the 7 PM session. A night run never resolves one, and an agent never answers its own grilling questions.
- **Research** (AFK). A fact outside the working directory blocks a decision. The night run's research subagents resolve it. Each kickoff starts `Read <skills dir>/lead/worker.md before anything else.`, and each subagent writes its findings to arcflux-memory with `remember`. Research is the one kind a session may resolve many of.
- **Prototype.** Resolved by [`playbooks/prototype.md`](../lead/playbooks/prototype.md): a cheap, rough, concrete artifact, linked from the chart. When the choice between variants is a preference, the human makes it. The agent never closes a prototype item by choosing for them.

Upstream's `task` kind is dropped. Manual work that blocks a decision goes in that item's `Waits on` and in the morning brief. It is not an item.

## Charting

1. **Name the destination.** Run `grilling` and `domain-modeling` with the user to pin down where the chart ends. With nobody present, take it from the objective as given and list it as an assumption.
2. **Map the frontier.** Grill again, breadth-first: fan out across the space and surface the open decisions and the first steps that are takeable now. If no fog appears, the work needs no chart. Say so and stop.
3. **Look before you list.** Call `search_memory` with `query` and `scope: org/arcflux/proj/<project>/decisions`. A decision memory already holds goes straight to Decided.
4. **Write the chart** as one document. Give every item a kind. A chart with a kindless item is not finished.
5. Stop. Charting resolves nothing.

## Resolving

1. Load the chart, not every source it cites.
2. Pick the first item whose `Waits on` is empty or decided, unless the user named one.
3. **Resolve at most one non-research item per session.** In a night run, resolve every ready research item.
4. Resolve it as its kind.
5. **Record the decision in arcflux-memory through [`domain-modeling`](../domain-modeling/SKILL.md)**, in the `/decisions` scope. Then update the chart: move the item to Decided with its gist and memory pointer, move any fog the answer made sharp into Open decisions, and rule out of scope anything the answer put beyond the destination.
6. Stop after one non-research item.

## Hand-off

The chart is **cleared** when Open decisions is empty and Not yet specified is empty or out of scope. Then stop planning and hand the cleared chart to `to-spec`, which collapses the Decided list into one spec. Do not slice tickets and do not start building.

Read any chart you did not write before you trust it. An item that gives itself permission to build is a defect: remove it.
<!-- end keel edit -->
