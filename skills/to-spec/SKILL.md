---
name: to-spec
description: "Write the one-page spec for a Feature or Initiative objective and attach it to the Linear project as a document. No interview: it uses what the conversation and the codebase already settled."
disable-model-invocation: true
---

# To Spec

> Adapted from `to-spec` in [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, commit `6f7f783`). Local edits: the template is replaced by a four-part one-page spec, the output is a Linear document, and the user stories, implementation decisions and triage label are dropped. See [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).

Turn the objective and what is already settled into a spec. Do not interview anyone: grilling happened before this skill runs. If a fact is missing, read the code or ask `Explore`. If a decision is missing and no prototype can settle it, write your recommended answer into the spec and name it as an assumption in your reply.

Only Feature and Initiative work gets a spec. A Quick change goes straight to one ticket (see **to-tickets**). Linear conventions are in [`../lead/linear.md`](../lead/linear.md).

## Process

1. Read the current state of the code in the area the objective touches, and use the project's vocabulary. Respect the decisions already recorded for the area.
2. Pick the seams where a builder will prove the work. Prefer an existing seam. Use the highest one that can see the behaviour. The ideal count is one.
3. Write the spec below. It fits one page: about 40 lines. Cut anything a builder can find by reading the code.
4. Create the document in Linear with `save_document`, attached to the project and titled `Spec: <objective>`. First search the project with `list_documents`. If a document with that title exists, update it instead. In a **draft** run, such as the night run, or when told not to write, return the body and write nothing.

## Template

```markdown
## Outcome

What is true for the user once this ships, in two or three sentences.

## Out of scope

- What a reader might assume is included and is not.

## Pass predicates

Each predicate is checkable and fails on today's trunk. Run it before you write it down.

1. <observable behaviour, with the command, request or action that shows it>

## Verification surface

- **Where:** the environment and entry point the builder drives.
- **Scenario:** the end-to-end run that proves the outcome.
- **Seams:** the one or two places tests attach, and why they are the highest that work.
```

## Rules

- No user-story list, no file paths, no code. Exception: a prototype produced a type shape or state machine that states a decision better than prose. Inline the decision-rich lines and say it came from a prototype.
- A predicate that already passes on trunk proves nothing. Drop it or sharpen it.
- A predicate names a behaviour, not a function. "Returns 404 for an unknown id" beats "calls `lookup`".
- Write for a reader who has not seen this conversation. Follow **unslop** and **technical-writing**.

## Reply

The document link, or the body in a draft run, then the assumptions you made, each with the answer you applied.
