---
name: agent-orchestration
description: >
  How to delegate work to subagents well — when to spawn one, how many, which
  model and effort level, how to write the delegation prompt, and when NOT to
  delegate. Load before starting any non-trivial task: research, codebase
  investigation, multi-file work, migrations, reviews, or anything that will
  read a lot of files. Also load when the user says "use agents", "delegate",
  "spawn subagents", "in parallel", "orchestrate", or asks why a delegation
  went badly.
when_to_use: >
  Any task with more than one independent piece of work, any task that will
  read many files, any request to parallelize, and any time you are about to
  do a lot of exploration inline.
---

# Agent orchestration

Your context window is the scarce resource, not tokens and not time. Every file
a subagent reads costs you nothing; every file *you* read costs you the rest of
the session. Delegation is context management first and parallelism second.

But delegation is not free. A subagent starts blind — it sees none of your
conversation — so it must re-derive context from scratch. Anthropic measured
multi-agent systems at **~15× the tokens of a chat interaction** (single agents:
~4×). That spend is justified only when the task is big enough, parallel enough,
or context-heavy enough to earn it.

## The decision, in order

Run these four gates before spawning anything.

**Gate 1 — Is it self-contained?**
A subagent cannot ask you or the user a question (`AskUserQuestion` is stripped
from every subagent). If the task needs a judgment call mid-flight, either
decide it now and put the decision in the prompt, or keep the work inline.

**Gate 2 — Is the output smaller than the input?**
Delegate when the work reads a lot and reports a little: test runs, log
trawls, grep sweeps, dependency audits, "where is X used". Do not delegate
when the work reads a little and writes a lot — you will pay cold-start cost
for nothing.

**Gate 3 — Are the pieces independent?**
Anthropic's own finding: multi-agent is ineffective for "domains requiring all
agents to share the same context or involve many dependencies between agents,"
and "most coding tasks lack sufficient parallelizable work." Two agents editing
the same call chain will conflict and duplicate. Split by *file boundary* or by
*question*, never by "half the feature."

**Gate 4 — Would you rather have the finding than the files?**
If yes, delegate. If you need the file contents in your own context to make the
next decision, read them yourself.

If any gate fails, do the work inline. Say so and move on — do not spawn an
agent to look busy.

## How many, and how hard

Scale the fleet to the question, not to your enthusiasm. Anthropic's published
scaling rule:

| Task shape | Agents | Tool calls each |
|---|---|---|
| Simple fact-find ("where is X defined") | 1 | 3–10 |
| Direct comparison ("how do A and B differ") | 2–4 | 10–15 |
| Broad research / audit / migration survey | 10+, responsibilities explicitly divided | as needed |

A lead agent spawning **3–5 workers in parallel** is the workhorse shape.
Parallel tool calling cut research time by up to 90% in Anthropic's testing.

Launch parallel agents in **one message with multiple Agent calls**. Sequential
spawns give you the cost of multi-agent with none of the speed.

## Model and effort

Two separate dials, and confusing them is the most common routing mistake:

- **Model = capability ceiling.** What the agent is able to figure out.
- **Effort = thoroughness.** How many files it reads, tools it runs, steps it
  takes before it stops. Not merely "thinking time."

Diagnose failure to pick the dial:

- Agent had all the context, clearly tried, and was still **wrong** → raise the
  **model**. Knowledge gap.
- Agent skipped a file, didn't run the tests, stopped early, didn't check its
  work → raise the **effort**. Thoroughness gap.

Routing defaults:

| Work | Model | Effort |
|---|---|---|
| Mechanical, precisely describable edits; questions about code already located | `haiku` / `sonnet` | `low`–`medium` |
| Ordinary implementation, feature work, research, most delegation | `sonnet` | inherit (default `high`) |
| Real architecture calls, subtle bugs, ambiguous or high-stakes judgment | `opus` | `high`–`xhigh` |
| Final adversarial verification of a risky change | `opus` | `xhigh` |

Effort levels are `low`, `medium`, `high`, `xhigh`, `max`. Default is `high` on
every supporting model (Opus 4.7 defaults to `xhigh`). Use `max` sparingly —
it is "prone to overthinking" and shows diminishing returns.

Omitting `model` means the agent inherits your session model. That is usually
right. Only override when you are confident a different tier fits — a cheap
worker for mechanical scanning, a strong one for the judgment call.

**Local rules win.** If `CLAUDE.md` or user instructions restrict which models
may be used, obey that over this table without comment.

## Writing the delegation prompt

A subagent receives its own system prompt, your delegation message, `CLAUDE.md`,
and git status. It receives **nothing else** — not your conversation, not the
files you read, not the skills you loaded, not the decisions you made three
turns ago. (`Explore` and `Plan` skip even `CLAUDE.md` and git status.)

So every delegation prompt carries four things. Missing any one is the usual
cause of a bad agent result:

1. **Objective** — the question to answer or the change to make, stated so it
   can be answered without asking you anything.
2. **Output format** — exactly what to return and how long. This is the only
   lever you have on how much of your context the result eats.
3. **Tools and sources** — where to look, what to use, what to ignore
   (`vendor/`, `node_modules/`, generated files).
4. **Boundaries** — what is out of scope, and which *other* agents own the
   neighbouring pieces. Explicit division of labour is what stops five agents
   running the same grep.

Vague prompts cause duplicated and missed work. `references/prompt-contract.md`
has the template and worked examples.

## What comes back

The agent's final message is injected into your context verbatim, and the user
never sees it. Two consequences:

- **Bound the output in the prompt.** "Return a file:line table, max 20 rows,
  no prose" costs a fraction of "report your findings." Ten agents each
  returning two pages of prose defeats the entire purpose of delegating.
- **Relay what matters yourself.** The user sees only your text. Summarize the
  finding; never say "the agent reported" and stop there.

Do not fabricate or predict a pending background agent's result. If asked
before it lands, say it is still running.

## Verification

The agent that did the work is the wrong one to grade it. For anything risky,
spawn a fresh reviewer that sees the diff and the criteria but not the
reasoning that produced them.

Prompt reviewers to flag only gaps that affect **correctness or stated
requirements**. A reviewer told to find problems will find some regardless, and
chasing all of them produces defensive over-engineering.

## Anti-patterns

- **Delegating the small thing.** A one-file edit you can already describe is
  cheaper inline than a cold-start agent.
- **"Investigate X" with no boundaries.** Unscoped exploration reads hundreds
  of files and returns mush. Scope it or don't send it.
- **Splitting coupled work.** Two agents on one call chain conflict.
- **Sending an agent to a file you haven't located.** Locate first (one cheap
  read-only agent), then hand exact paths to the worker.
- **Expecting questions back.** It cannot ask. Under-specified means it guesses.
- **Unbounded returns.** See above — the return is your context.
- **Assuming it knows your rules.** Restate the constraint that matters in the
  prompt, especially for `Explore`/`Plan`, which never see `CLAUDE.md`.
- **Worktree isolation by default.** `isolation: "worktree"` costs setup time
  and disk. Use it only when parallel agents write to the same files.

## Reference material

- `references/prompt-contract.md` — delegation prompt template, good and bad
  examples, output-format recipes.
- `references/patterns.md` — the orchestration shapes: parallel scout, locate→
  fix→verify pipeline, adversarial verify, writer/reviewer, fan-out migration,
  loop-until-dry.
- `references/mechanics.md` — hard limits, tool filters, what loads into a
  subagent, resuming agents, custom agent frontmatter spec.
