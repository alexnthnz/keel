---
name: domain-modeling
description: "Build and sharpen a project's domain model. Use when discussing codebase terminology, defining a glossary term, or recording a decision. Terms and decisions go to arcflux-memory. Use for /keel:domain-modeling."
disable-model-invocation: true
---
<!-- Adapted from mattpocock/skills (MIT, https://github.com/mattpocock/skills), skills/engineering/domain-modeling at 6f7f783. Local edits are marked "keel edit". -->

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline: challenging terms, inventing edge-case scenarios, and writing terms and decisions down the moment they crystallise. Merely reading the glossary for vocabulary is not this skill. This skill is for when you are changing the model.

<!-- keel edit: storage. Upstream writes GLOSSARY.md, GLOSSARY-MAP.md and docs/adr/. keel writes arcflux-memory and creates none of those files. -->
## Where it lives

**keel edit.** Never create `GLOSSARY.md`, `GLOSSARY-MAP.md` or ADR files. Glossary terms and decisions live in arcflux-memory. Load the tool schemas first with ToolSearch: `select:mcp__arcflux-memory__search_memory,mcp__arcflux-memory__remember,mcp__arcflux-memory__add_source`.

| What | Scope |
|---|---|
| Glossary terms | `org/arcflux/proj/<project>`, for example `org/arcflux/proj/oncall` |
| Decisions | `org/arcflux/proj/<project>/decisions`, for example `org/arcflux/proj/oncall/decisions` |

Scopes are paths with no trailing slash. A multi-context project uses one scope per context, `org/arcflux/proj/<project>/<context>`.

**Read before you write.** Call `search_memory` with `query` (the term or decision) and `scope`. It returns current facts first, each with a quote, a trust label and a source, then passages. Set `history: true` to see past values and `related: true` for facts one relation away. Open a hit with `read_facts` or `read_source` before you treat it as settled.

**Trust.** Everything you write is stored with `agent_note` trust and credited to your key's owner. It is never stored as the user's own words. A term is settled only when the user confirmed it in this session. Say so in the note, for example "Alex confirmed on <date>". The server cannot check that, so the note is the record.

Every write is one change and `undo_change` reverses it. When the brief says the run makes no memory writes, report the payload instead of sending it.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with a term in memory, call it out immediately. "Memory defines 'cancellation' as X, but you seem to mean Y. Which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account': do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

Stress-test relationships with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible. Which is right?"

### Write a term when it resolves

Capture each term as it resolves. Don't batch. Call `remember` with:

- `scope`: the project scope.
- `text`: the note, in plain words, that holds every quote you cite. Include who confirmed the term and when.
- `claims`: one entry per fact. For the definition: `entity_type: "term"`, `entity_name` (the canonical term), `key: "definition"`, `value` (one or two sentences: what it IS, not what it does), `quote` (verbatim from `text`), `standing` (`agreed_design`, or `proposed` when unconfirmed). Put the words to avoid in a second claim with `key: "avoid"`.
- `relations`: one per term the definition mentions. `subject_type: "term"`, `subject_name`, `type` (for example `part_of`), `object_type: "term"`, `object_name`, `quote`.
- `declared_status` and `link`: pass them only when a merged pull request or a completed Linear issue confirms the term.

A quote the server cannot find in `text` is stored unchecked, so copy it exactly.

Definition rules: be opinionated and pick one word per concept. Keep it to one or two sentences. Include only terms specific to this project, not general programming concepts. A term holds no implementation detail and no spec.

### Write a decision sparingly

Record a decision only when all three hold:

1. **Hard to reverse**: changing your mind later costs something.
2. **Surprising without context**: a future reader will wonder why.
3. **The result of a real trade-off**: there were real alternatives and you picked one for stated reasons.

If any of the three is missing, skip it.

Call `remember` with `scope` set to the `/decisions` scope. Put the context, the choice, the reason and the rejected options in `text`. Add a claim with `entity_type: "decision"`, `entity_name` (a short title), `key: "value"` (the choice) and `quote`, and a second claim with `key: "owner"` for who decided. To store a whole document, call `add_source` with `scope`, `title`, and `text` or a `link` to a Linear or GitHub item. A decision that supersedes an earlier one retires the old value with a claim of `kind: "remove"`, never a silent overwrite.
<!-- end keel edit -->
