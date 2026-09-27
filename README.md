# keel

keel is an engineering loop for [Claude Code](https://code.claude.com) and Codex. The main session you talk to is the lead, `ponytail` builds, and `critic` reviews.

> **keel is adapted from [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan ([poteto](https://x.com/poteto)).**
> pstack's method, skills, playbooks, principles and writing are hers, released under the MIT license, apart from material pstack itself adapted from others, which [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md) credits. keel ports them from Cursor to Claude Code and Codex and reorganizes the agents around them, so the credit for how keel works belongs to pstack first. keel is an independent project and is not affiliated with or endorsed by Lauren Tan, Cursor, Anthropic or OpenAI. See [credits and license](#credits-and-license).
> In this README, lowercase passages are pstack's original text, lightly adapted. Sentence-case passages are keel's.

## what it is

- **The lead** is the main session. For real engineering work it loads the [Claude Code](./skills/lead/SKILL.md) or [Codex](./codex/skills/lead/SKILL.md) lead skill, routes the task to one of 23 playbooks, and owns the design, plan, review and verification. Small asks it just does.
- **ponytail** ([Claude agent](./agents/ponytail.md)) owns one slice or pull request end to end: build, test, prove it on the real artifact, commit. In Codex, the lead gives that brief to a worker. A ponytail owner merges only under autopilot or when its brief says to land it.
- **critic** ([Claude agent](./agents/critic.md)), generalized from pstack's comment-review persona, Comment Sicko, reviews a diff through one lens: comments by default, or correctness, security, simplicity, tests or user impact. Codex gives the same brief to an independent reviewer.

keel keeps 46 of pstack's 47 skills (its 23 principles are among them) and all 23 playbooks. [Differences from pstack](#differences-from-pstack) lists what changed.

## install

### Claude Code

keel needs Claude Code, `git`, the GitHub CLI `gh` (signed in), `python3` for the git guard and `bun` for the playbook scripts. Optional: the Codex CLI for the cross-model review lane, `tmux` for driving interactive terminal apps, and Graphite (`gt`) for the Orchestrate playbook's stacks.

```bash
claude plugin marketplace add alexnthnz/keel
claude plugin install keel@keel
```

To try it for one session without installing, clone the repository and run `claude --plugin-dir ./keel`.

Skills run as `/keel:<name>`, and the agents are `keel:ponytail` and `keel:critic`. The main session loads `lead` on its own when a task needs it, or you type `/keel:lead`. The other keel skills are user-invoked, so `lead` reads them by path when a step needs one.

### Codex

Codex needs its CLI with plugin support, `git`, and `bun` for Keel's playbook scripts. Playbooks that use GitHub also need the GitHub CLI `gh` signed in. Add the keel marketplace, then install the plugin:

```bash
codex plugin marketplace add alexnthnz/keel
codex plugin add keel@keel
```

Start a new Codex session after installation. Ask for nontrivial engineering work or invoke `$keel:lead` directly. The Codex lead reads the same playbooks and principles from the installed plugin. It delegates scoped work to Codex workers and uses independent reviewers with keel's critic brief. Codex does not install Claude Code's named agents or model aliases.

Codex's workspace-write sandbox blocks the network, allows writes only in the workspace and temporary directories, and keeps the repository's `.git` read-only. The lead asks you to approve each command that needs more:

- Network calls, such as `git fetch`, `git push`, `gh`, and each `watch-pr` run.
- Writes outside the workspace, such as the first run of keel's playbook scripts, which installs their dependencies into the plugin.
- Git writes, such as commits and `git worktree add`.

To allow git writes for a whole session, start or resume Codex with `--add-dir` and the repository's `.git` directory. Sandboxed commands can then also change that repository's Git config and hooks. The Orchestrate and multi-phase plan playbooks keep their state in `keel-store/` in your Codex home (`~/.codex` by default). To let the lead write there, add `--add-dir "${CODEX_HOME:-$HOME/.codex}/keel-store"`, or add that directory's absolute path to `sandbox_workspace_write.writable_roots` in the home's `config.toml`. Otherwise the lead keeps that state in a temporary directory.

Codex asks you to review the lead reminder in `/hooks` before it runs. The Codex plugin does not load Claude Code's Git guard. That guard is a best-effort check of the command text, so do not rely on it as a Codex safety check.

For Claude Code, keel ships two hooks:

- [`hooks/git-guard.py`](./hooks/git-guard.py), adapted from Matt Pocock's [git guardrails](https://github.com/mattpocock/skills) (MIT), blocks force-pushes, deleting a protected branch on the remote, `reset --hard`, `clean -f`, `filter-branch`, `filter-repo`, and commands that discard the whole working tree, such as `git checkout .` and `git checkout -f`. The protected branches are `main`, `master`, `trunk`, `develop` and `release*`. The one exception is `--force-with-lease` onto a branch that the command names and that is not protected, so an owner can publish its own rebased branch with `git push --force-with-lease origin <branch>`. The guard catches the common forms an agent types by accident, including commands wrapped in `bash -c`, `eval`, `$(...)`, subshells, heredocs fed to a shell, launchers such as `sudo` or `xargs`, and abbreviated options. It skips quoted text, so a commit message that mentions `git push --force` still runs, but it blocks an unquoted mention such as `echo git reset --hard`. It is not a sandbox. Deliberate constructions get past it, such as brace or glob expansion in the command name, git-core helper paths, plumbing commands, inline `-c` config, and pathspec magic. A git alias, a script file, a heredoc piped into a shell, a flag built at run time, and a command string passed to `ssh` or another language also get past it. To protect a branch, turn on your forge's branch protection. On GitHub, add a ruleset that blocks force pushes and deletion. Set `KEEL_BLOCK_AI_TRAILERS=1` to also block commits whose message carries an AI attribution trailer.
- [`hooks/lead-reminder.sh`](./hooks/lead-reminder.sh) re-injects one line on every prompt, as pstack's sticky reminder does in Cursor: a new task that needs rigor loads `keel:lead`. Set `KEEL_REMINDER=off` to silence it.

## get started

For Claude Code:

1. Run [`/keel:setup`](./skills/setup/SKILL.md) to choose models. It writes `keel-models.md` in the active Claude config directory, `${CLAUDE_CONFIG_DIR:-$HOME/.claude}`, so each profile keeps its own.
2. Give the main session real engineering work, or start with [`/keel:lead`](./skills/lead/SKILL.md). Once entered, lead mode stays on across turns.

Subagents live only as long as their session. Before you close the terminal on running work, type `/bg` to move the session to the background. Start unattended work with `claude --bg`. keel runs subagents inside subagents, so don't cap `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` below its default of 20.

New here? The [keel guide](./docs/guide/README.md), adapted from pstack's guide, walks through a first real task.

### models

Claude Code subagents take a model alias, not a vendor slug. keel's defaults:

| role | pstack default (Cursor) | keel default |
|---|---|---|
| code delegates: feature, refactoring, bug fix, perf, hillclimb | `grok-4.7-xhigh-fast` | `inherit` (the lead's model) |
| judgment, prose, hardest tasks | `claude-opus-5-5-max` | `inherit` |
| explorers, investigators, swarm workers, reflect tooling | `grok-4.7-xhigh-fast`, `gpt-5.6-sol-max` | `sonnet` |
| synthesizers, explainers, reflect's judgment and divergent reviewers | `claude-opus-5-5-max` | `opus` |
| arena runners, architect runners, arena cross-judge pool | opus / sol / grok | `opus, fable, sonnet` |
| interrogate reviewers | opus / sol / grok | `opus, fable, sonnet, codex` |

`codex` is not a subagent: `interrogate` runs `codex exec --sandbox read-only` from bash with the same brief as the other reviewers, and skips that lane when the Codex CLI is not installed.

## usage

The examples below use Claude Code slash commands. In Codex, use `$keel:lead` or give the lead a nontrivial engineering task.

use [`/keel:lead`](./skills/lead/SKILL.md) at the start of a task. it reads your request, picks from a set of playbooks, and runs the other skills as the steps need them.

### just use [`/keel:lead`](./skills/lead/SKILL.md)

this skill is the main shortcut. use it whenever you need the agent to do rigorous engineering work. it comes with twenty-three playbooks:

```
/keel:lead this pr has a subtle bug where the scroll drifts every 750ms even when idle. repro
first, then fix and verify.
```

```
/keel:lead i'm going to bed. land the stack even if ci flakes. i want everything merged by
morning.
```

<details>
<summary>the twenty-three playbooks</summary>

| playbook | for |
|---|---|
| [investigation](./skills/lead/playbooks/investigation.md) | a read-only question. how does x work, why was y built this way, are we sure. |
| [bug fix](./skills/lead/playbooks/bug-fix.md) | reproduce a defect, root-cause it, and fix with runtime evidence. |
| [perf](./skills/lead/playbooks/perf-issue.md) | trace a measured slowness and improve it against a baseline. |
| [hillclimb](./skills/lead/playbooks/hillclimb.md) | sustained, scientific improvement of one metric against a target, looping hypotheses with before/after measurement and one commit per accepted win. |
| [runtime forensics](./skills/lead/playbooks/runtime-forensics.md) | diagnose a live symptom (leak, idle-cpu spin, glitch) from instrumentation. |
| [trace forensics](./skills/lead/playbooks/trace-forensics.md) | diagnose a captured profiling artifact (cpuprofile, trace, spindump, heap snapshot). |
| [feature](./skills/lead/playbooks/feature.md) | new or changed behavior, built from a named data shape. |
| [refactoring](./skills/lead/playbooks/refactoring.md) | a behavior-preserving change to structure or shape. |
| [prototype](./skills/lead/playbooks/prototype.md) | a throwaway sketch to make a design or behavioral decision cheaply, or to settle an empirical fork by observing it. |
| [visual parity](./skills/lead/playbooks/visual-parity.md) | pixel-exact ui equivalence between two implementations. |
| [authoring a skill](./skills/lead/playbooks/authoring-a-skill.md) | writing or editing a SKILL.md. |
| [eval](./skills/lead/playbooks/eval.md) | test how a skill or prompt change affects agent behavior, blinded. |
| [babysit](./skills/lead/playbooks/babysit.md) | drive a pr or a stack to merge-ready: conflicts, review threads, ci. |
| [shipping](./skills/lead/playbooks/shipping.md) | independently verify a green stack, then land the contiguous verified run bottom-up through github. |
| [autonomous run](./skills/lead/playbooks/autonomous-run.md) | drive a long task to completion without stopping. |
| [orchestrate](./skills/lead/playbooks/orchestrate.md) | a standing project handed to one coordinator chat: multi-day, many stacked prs, fleets of subagents. |
| [autopilot-full](./skills/lead/playbooks/autopilot-full.md) | run independent prs to merged with one owner per pr and a root swarm verdict on each round, from the code-ready head on. |
| [autopilot-stack](./skills/lead/playbooks/autopilot-stack.md) | build and verify one linear base-branch stack for the operator to review and land. |
| [session pickup](./skills/lead/playbooks/session-pickup.md) | resume or take over a prior agent's in-flight work. |
| [pause safely](./skills/lead/playbooks/pause-safely.md) | suspend in-flight work cleanly so it can be resumed later. |
| [multi-phase plan](./skills/lead/playbooks/multi-phase-plan.md) | work that spans phases or stacked PRs. |
| [worktree cleanup](./skills/lead/playbooks/worktree-cleanup.md) | reclaim disk by pruning merged or abandoned worktrees and stale ios simulators, safety-gated. |
| [opening a pr](./skills/lead/playbooks/opening-a-pr.md) | open a ready pr from small ordered commits with a conventional commits title and a briefing-style body. invoked at the end of every other playbook. |

</details>

when invoked it:

1. matches your task to a [playbook](./skills/lead/playbooks/) and opens a todo list whose first items are its steps, copied in verbatim.
2. routes to the other skills as the steps fire.
3. writes unslopped replies framed for the consumer and the maintainer.

the full rules and playbooks live in [`skills/lead/SKILL.md`](./skills/lead/SKILL.md).

[`/keel:lead`](./skills/lead/SKILL.md) is also a sticky mode: once entered it stays on across turns, applying itself when a playbook matches or the task needs rigor and staying out of the way otherwise. opt out any time by saying so.

[`/keel:lead`](./skills/lead/SKILL.md) works extremely well with claude code's `/loop` command. you can make claude code work for many hours without sacrificing rigor.

## skills

[`/keel:lead`](./skills/lead/SKILL.md) runs most of these for you when a step needs them (`how`, `why`, `architect`, `arena`, `swarm`, `interrogate`, `unslop`, `no-comments`, `technical-writing`, `tdd`, and the principles). the table below is for when you want one directly:

```
/keel:how do we cancel runs? do we have an n+1 when we look up every run to cancel?
```

```
/keel:interrogate review this pr.
```

<details>
<summary>all skills</summary>

| skill | use it when |
|---|---|
| [`/keel:lead`](./skills/lead/SKILL.md) | default entry point for any non-trivial task. the main session also loads it on its own. |
| [`/keel:how`](./skills/how/SKILL.md) | you want a walkthrough of how a subsystem works. |
| [`/keel:why`](./skills/why/SKILL.md) | you want to know why something was built this way. discovers available MCPs at run time and queries each evidence category in parallel (source control, issue tracker, long-form docs, real-time chat, infra observability, error tracking, analytics warehouse). |
| [`/keel:recall`](./skills/recall/SKILL.md) | you're starting or resuming work and want your recent context on a topic rebuilt from your own chat history and the shared record, handed back as a tight current-state brief. |
| [`/keel:blast-radius`](./skills/blast-radius/SKILL.md) | you have a small-looking change and want to know what else it could break, with the one fact it's safe because of proven by running code, not asserted. |
| [`/keel:architect`](./skills/architect/SKILL.md) | you're about to write code that crosses a function boundary and want the caller's usage, types, and module shape settled first. |
| [`/keel:arena`](./skills/arena/SKILL.md) | you want N parallel attempts at the same thing, then to grab the best parts of each. |
| [`/keel:swarm`](./skills/swarm/SKILL.md) | you want N parallel workers across different slices or races, then one aggregated report. |
| [`/keel:interrogate`](./skills/interrogate/SKILL.md) | you have a diff and want several different models to try to break it, including a strict code-quality lens. |
| [`/keel:automate-me`](./skills/automate-me/SKILL.md) | you want your own `-mode` skill, drafted from how you've actually worked. |
| [`/keel:setup`](./skills/setup/SKILL.md) | you want to pick which models keel uses per role. checks for the codex cli and writes `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/keel-models.md`. |
| [`/keel:reflect`](./skills/reflect/SKILL.md) | a long task landed and you want the recipe captured as a skill edit. |
| [`/keel:teach`](./skills/teach/SKILL.md) | you want to actually understand a change or subsystem, not just have it summarized. runs how + why and weaves one plain explanation, built up diagram by diagram. |
| [`/keel:tdd`](./skills/tdd/SKILL.md) | you're fixing a bug and there's a cheap local test path. write the failing test first, then the fix. |
| [`/keel:no-comments`](./skills/no-comments/SKILL.md) | strip comments before review; spawns critic with the comments lens, carries out accepted kills, fixes accepted findings, offers encodings for claimed constraints. |
| [`/keel:typescript-best-practices`](./skills/typescript-best-practices/SKILL.md) | you're reading or editing typescript. grounds the type-system-discipline principle in syntax. |
| [`/keel:figure-it-out`](./skills/figure-it-out/SKILL.md) | no bundled playbook fits. designs a rigorous, auditable playbook for the task. |
| [`/keel:show-me-your-work`](./skills/show-me-your-work/SKILL.md) | you want a reviewable decision trail. logs decisions to a tsv you can commit. |
| [`/keel:create-verification-skill`](./skills/create-verification-skill/SKILL.md) | your project has no scripted way to prove app behavior. generates a project-local verify skill with a feature map, for any language or platform. |
| [`/keel:maintain-verification-skill`](./skills/maintain-verification-skill/SKILL.md) | your verify skill's feature map has drifted from the app. source wave + one live pass, at most one PR of proven corrections. |
| [`/keel:unslop`](./skills/unslop/SKILL.md) | you're cleaning up writing. removes AI tells. |
| [`/keel:bro`](./skills/bro/SKILL.md) | you want the last message restated in plain human language, no jargon. |
| [`/keel:technical-writing`](./skills/technical-writing/SKILL.md) | layered doc standard (Diátaxis + Google developer style + STE + Global English) for docs, RFCs, readmes, PR descriptions, commit messages. |

</details>

### examples

mostly you give the lead a task, or type [`/keel:lead`](./skills/lead/SKILL.md) at its start, and let it route to a playbook. the other skills fire as the steps need them. a few are worth reaching for directly.

<details>
<summary>all the examples</summary>

```
bug fix:           /keel:lead this pr has a subtle bug where the scroll drifts every 750ms even
                   when idle. repro first, then fix and verify.
perf:              /keel:lead a big list takes a second or two to load even though we virtualize.
                   run a cpu trace and tell me why.
feature:           /keel:lead build a small feature behind a feature flag. verify it really works.
prototype:         /keel:lead build two prototypes of the markdown renderer so we can compare.
                   spawn an agent for each.
multi-phase:       /keel:lead open source these skills as a plugin. nothing internal leaks, work
                   in a temp dir, show me the dependency graph first.
overnight run:     /keel:lead i'm going to bed. land the stack even if ci flakes. i want
                   everything merged by morning.
babysit:           /keel:lead check on pr 123. anything outstanding?
visual parity:     /keel:lead the row spacing is too tall when this flag is on. the second image
                   is correct. repro and fix until it matches.
figure it out:     /keel:lead i'm stepping away. migrate every caller from the synchronous store
                   to the new async one, keeping behavior identical. i want to trust it was done
                   right when i'm back.
how:               /keel:how do we cancel runs? do we have an n+1 when we look up every run to cancel?
why:               /keel:why is this feature flag not on yet?
architect:         design this instrumentation to be high signal with no false positives. /keel:architect
                   this first.
arena:             /keel:arena take my prompt to the arena verbatim. i want to compare their proposals
                   with yours.
swarm:             /keel:swarm check every package under packages/ against its check.sh. one worker per
                   package. one report.
interrogate:       /keel:interrogate review this pr.
tdd:               /keel:tdd implement
unslop:            can we unslop and tighten the new changes?
reflect:           /keel:reflect that took too long. capture what we learned so the next run doesn't
                   repeat it.
show-me-your-work: /keel:show-me-your-work keep a decision trail i can review when i'm back.
automate-me:       /keel:automate-me
```

</details>

## ponytail and critic

The lead delegates code-writing to [`keel:ponytail`](./agents/ponytail.md). ponytail reads `lead` in full, including its principles index, before any work, so the lead and its builders share one set of rules. It runs on the lead's model unless the lead passes another, keeps user-scope memory, may spawn its own subagents within Claude Code's depth limit, and merges its own pull request only under autopilot, after a clean review with CI green on a freshly rebased head, or when its brief says to land it. It never bypasses a review or check the forge enforces. The lead passes `isolation: "worktree"` when two or more builders share a repository.

[`keel:critic`](./agents/critic.md) is the read-only reviewer, one lens per spawn. Its default comments lens keeps poteto's comment-hating persona from pstack. Use it through [`/keel:no-comments`](./skills/no-comments/SKILL.md), which carries out the deletions critic recommends, or through [`/keel:interrogate`](./skills/interrogate/SKILL.md), which spawns one critic per configured model plus the Codex lane.

## principles

twenty-three short skills, one principle each. `lead` indexes them inline and reads that index at task start. the standalone files are there so other skills can reference a principle by name, and so the index can point at the full rule for each.

<details>
<summary>all twenty-three principles</summary>

| principle | group | rule |
|---|---|---|
| [laziness-protocol](./skills/principle-laziness-protocol/SKILL.md) | core | Bias toward deletion and the smallest change that solves the problem. |
| [foundational-thinking](./skills/principle-foundational-thinking/SKILL.md) | core | Apply before writing logic: choosing core types and data structures, sequencing scaffold-vs-feature work, asking what concurrent actors share. Get the data structures right so downstream code becomes obvious. |
| [redesign-from-first-principles](./skills/principle-redesign-from-first-principles/SKILL.md) | core | Redesign as if the requirement had been a foundational assumption from day one, instead of bolting it on. |
| [attack-the-premise](./skills/principle-attack-the-premise/SKILL.md) | core | Apply when two or more fixes that share one premise have failed the same gate. Take a census of which actors hold the imbalance before the next fix, then question the premise instead of writing another fix that assumes it. |
| [subtract-before-you-add](./skills/principle-subtract-before-you-add/SKILL.md) | core | Remove dead weight, redundant validators, and stub references first, then build on the simpler base. |
| [minimize-reader-load](./skills/principle-minimize-reader-load/SKILL.md) | core | Count layers between question and answer, and hidden state in the reader's head; collapse one-caller wrappers and shrink mutable scope. |
| [outcome-oriented-execution](./skills/principle-outcome-oriented-execution/SKILL.md) | core | Apply during planned rewrites and migrations with explicit phase boundaries. Converge on the target architecture; don't preserve smooth intermediate states with throwaway compatibility code. |
| [experience-first](./skills/principle-experience-first/SKILL.md) | core | Choose user delight over implementation convenience; ship fewer polished features over more rough ones. |
| [exhaust-the-design-space](./skills/principle-exhaust-the-design-space/SKILL.md) | core | Build 2-3 competing prototypes and compare side by side before committing. |
| [build-the-lever](./skills/principle-build-the-lever/SKILL.md) | core | Apply to any non-trivial work, not just bulk work: edits, migrations, analyses, checks. Build the tool that does it or proves it (codemod, script, generator, or a skill your subagents follow) instead of working by hand. The tool is the artifact a reviewer can rerun. |
| [model-the-domain](./skills/principle-model-the-domain/SKILL.md) | architecture | Encode the domain in a structure instead of scattered conditionals. |
| [boundary-discipline](./skills/principle-boundary-discipline/SKILL.md) | architecture | Concentrate guards at system boundaries (CLI, config, network, external APIs); trust internal types and keep business logic in pure functions. |
| [type-system-discipline](./skills/principle-type-system-discipline/SKILL.md) | architecture | Make illegal states unrepresentable, brand semantic primitives, parse external data at boundaries, refuse to lie to the compiler, exhaust variants, derive from authoritative schemas. |
| [make-operations-idempotent](./skills/principle-make-operations-idempotent/SKILL.md) | architecture | Converge to the same end state regardless of partial prior runs. |
| [migrate-callers-then-delete-legacy-apis](./skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md) | architecture | Migrate callers and delete the old API in the same wave instead of preserving compatibility layers. |
| [separate-before-serializing-shared-state](./skills/principle-separate-before-serializing-shared-state/SKILL.md) | architecture | Eliminate the sharing first; serialize structurally only when one shared writer is a real invariant. |
| [prove-it-works](./skills/principle-prove-it-works/SKILL.md) | verification | Apply after completing a task, before declaring done. Verify against the real artifact (run the feature, read the actual value, inspect the diff), not a proxy, self-report, or 'it compiles'. |
| [fix-root-causes](./skills/principle-fix-root-causes/SKILL.md) | verification | Trace each symptom to its root cause and fix it there; reproduce first, ask why until you reach it, resist nil-check guards that silence crashes. |
| [sequence-verifiable-units](./skills/principle-sequence-verifiable-units/SKILL.md) | verification | Apply to multi-step work (sweeps, migrations, runs of similar edits) and to how you stack commits and PRs. Break work into small units that each end in a verifiable state, check each before the next, and order delivery so the sequence proves itself to a reviewer. |
| [test-behavior-not-implementation](./skills/principle-test-behavior-not-implementation/SKILL.md) | verification | Apply when you write, change, or keep a test. Call the code the way its users do and assert the result they observe against a literal expected value. If the test would still pass when every imported function returns undefined, rewrite the assertion or delete the test. |
| [guard-the-context-window](./skills/principle-guard-the-context-window/SKILL.md) | delegation | Route bulk to subagents; keep summaries in the main thread, not raw payloads. |
| [never-block-on-the-human](./skills/principle-never-block-on-the-human/SKILL.md) | delegation | Proceed, present the result, let the human course-correct after the fact; reserve confirmation for irreversible actions. |
| [encode-lessons-in-structure](./skills/principle-encode-lessons-in-structure/SKILL.md) | meta | Encode the rule as a lint, metadata flag, runtime check, or script instead of more text. |

</details>

## differences from pstack

keel changes how pstack runs, not what it teaches.

- **Platform.** Cursor's tools become their Claude Code equivalents. The Task tool becomes the Agent tool, Cursor cloud agents become background subagents in worktrees, and pull request operations go through `gh` (the Orchestrate playbook also uses Graphite, `gt`, for stacks). cursor-team-kit's slop and control skills become Claude Code's `/simplify`, Bash (tmux for interactive TUIs) and the browser skills, and Cursor's `create-skill` becomes `anthropic-skills:skill-creator`.
- **Names.** `poteto-mode`, `poteto-agent`, Comment Sicko and `setup-pstack` become `lead`, `ponytail`, `critic` and `setup`.
- **Models.** Claude Code has no grok. Review panels use Opus, Fable and Sonnet, and `interrogate` adds a Codex lane.
- **Shape.** The lead is a skill loaded by the main session, because running a session as an agent replaces Claude Code's own instructions. critic is read-only, ponytail keeps memory, and keel adds the git guard and the lead reminder.
- **Removed.** The benny Slack automation pack, the `make-bot-ui` skill, Cursor's plugin manifest, and pstack's logo and illustrations. They are Cursor-only or pstack's own branding.

[`UPSTREAM.md`](./UPSTREAM.md) has the full translation and rename tables and how to pull future pstack changes.

## why are there no planning skills?

Claude Code already has a plan mode, and it works well with keel. pstack leaves out planning skills on purpose; its README says "personally, i don't believe in planning. the best spec is code." If you do want a plan, [`/keel:lead`](./skills/lead/SKILL.md) covers it, but it's not a default.

## make it yours

`lead` is adapted from poteto-mode and carries much of poteto's style. You may not want exactly that.

type [`/keel:automate-me`](./skills/automate-me/SKILL.md). it mines your recent transcripts, drafts a `<your-name>-mode` skill from how you've actually worked, and routes through keel underneath. you keep keel as the base and end up with your own routing skill alongside `lead`.

models are configurable too. type [`/keel:setup`](./skills/setup/SKILL.md). it checks for the codex cli and writes `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/keel-models.md`, a small file mapping each role (code, judgment, the review panels) to a model. claude code has no always-applied rule outside CLAUDE.md, so every skill that spawns a subagent reads that file itself and falls back to sensible defaults when it is absent. you override only what you want.

pstack's Cursor model rule file does not carry over. Run `/keel:setup` once in Claude Code. A rerun keeps any role whose model differs from the default.

## credits and license

- **pstack** by Lauren Tan ([poteto](https://x.com/poteto)), from [cursor/plugins](https://github.com/cursor/plugins/tree/main/pstack) at commit `12d587d` (pstack 0.15.5), MIT. keel's skills, playbooks, principles, references, scripts, guide and both agents are adapted from it.
- **Git guardrails** by Matt Pocock, from [mattpocock/skills](https://github.com/mattpocock/skills), MIT. `hooks/git-guard.py` is adapted from it.
- **keel's changes** by [alexnthnz](https://github.com/alexnthnz), MIT.

[`LICENSE`](./LICENSE) keeps Lauren Tan's copyright notice alongside keel's, and [`THIRD_PARTY_NOTICES.md`](./THIRD_PARTY_NOTICES.md) reproduces each upstream license. keel is not affiliated with or endorsed by Lauren Tan, Matt Pocock, Cursor or Anthropic.
