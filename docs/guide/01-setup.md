# Set up keel

In this page you install the plugin, pick which models keel uses, and run your first task. Once the tools below are on your machine, setup is one command plus a short conversation.

## Before you install

keel needs these tools on your machine:

- Claude Code and `git`.
- The GitHub CLI `gh`, signed in. Opening, babysitting, and shipping a PR all go through it.
- `python3`, which runs keel's git guard before each Bash command.
- `bun`, which runs the playbook scripts, such as the PR watcher that Babysit and Shipping use.
- `node`, which runs the plan checker in the Multi-phase plan playbook.

Two more are optional. The OpenAI Codex CLI adds a cross-vendor reviewer to `/interrogate`, as [Pick your models](#pick-your-models) explains. `tmux` lets agents drive interactive terminal apps.

## Install the plugin

Add the repository as a plugin marketplace and install keel from it:

```bash
claude plugin marketplace add alexnthnz/keel
claude plugin install keel@keel
```

To try keel for one session without installing, clone the repository and start Claude Code with the plugin directory:

```bash
git clone https://github.com/alexnthnz/keel
claude --plugin-dir ./keel
```

`/plugin` inside Claude Code lists keel once it is loaded. Every keel skill runs as `/keel:<name>`.

## Pick your models

Run:

```text
/keel:setup
```

[`/keel:setup`](../../skills/setup/SKILL.md) checks whether the OpenAI Codex CLI is installed, shows you each role (code delegates, judgment, the review panels) with its model alias (`opus`, `sonnet`, `haiku`, or `fable`), and asks what you want. Answer the questions. It writes `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/keel-models.md`, a small file every keel skill reads before it spawns a subagent.

You only override what you care about. A role with no line in the file keeps the skill's default. To restore a default, delete that role's line. A rerun of `/keel:setup` keeps any role whose model differs from the default. When a default changes, a file written before the change still pins the old default, so delete those role lines, or delete the file, then run `/keel:setup` again.

You might be wondering how to keep the model you picked for the session. Set a role to `inherit` and keel omits the subagent `model` field, so the subagent inherits your parent model. `inherit-parent` and `auto` mean the same thing. When the Codex CLI is installed, the `interrogate reviewers` panel also gets a `codex` entry, a cross-vendor reviewer that runs from Bash rather than as a subagent. For a panel role the value is a list, and one subagent runs per entry, so the list length sets the panel size. Setup also configures `swarm workers`, the default model for every `/swarm` worker unless a race names a model for each arm.

## Accept the verification offer, or don't

At the end of setup, `/setup` looks for a way to prove app behavior in your project, either a `verify-*` skill or an existing harness. If it finds neither, it offers once to generate one with [`/create-verification-skill`](../../skills/create-verification-skill/SKILL.md).

Say yes and it writes `.claude/skills/verify-<app>/`, a project-local skill that teaches agents to drive your app the way a user does. It proves the skill works once before handing it over. Say no and setup moves on. You can run `/create-verification-skill` yourself any time. [Verify and ship](./06-verify-and-ship.md#create-a-project-verification-skill) covers it in depth.

If you're new to keel, say yes. An agent that can check its own work keeps going until the check passes. An agent that can't hands every result back to you to check by hand. Of everything in this guide, the verification skill pays off the most.

keel skills read the model file each time they spawn a subagent, so the new choices apply right away.

## Keep the cost in check

keel spends extra tokens on subagents and review panels. That's the price of the rigor. To spend fewer:

- Rerun `/keel:setup` and pick cheaper models. A strong model in the main session with cheaper, faster models such as `sonnet` or `haiku` in the code roles is a good split.
- Shorten a panel list. Each entry runs one subagent.
- Save `/lead` for work that needs rigor. A small, obvious edit doesn't.

## Run your first task

Pick something real but small, and describe it the way you'd describe it to a colleague:

```text
/lead add a --json flag to this command. text output stays byte-identical. verify both.
```

Watch the todo list. Its first items are the matched playbook's steps copied in, the Feature playbook for this prompt. If `/lead` skips a step, the step stays in the list with `skip: <reason>`, so you can see what it chose not to do.

From here you can type normal follow-ups. `/lead` is sticky. It stays on for the conversation until you opt out by saying so.

Next: [Route work through `/lead`](./02-lead.md).
