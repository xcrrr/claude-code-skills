# Token economics of delegation

Delegation raises *total* token spend. What you are optimizing is the main
conversation's context window, because that is what degrades as it fills. The
levers below are ordered by how much main context they actually save.

Do not reach for a weaker model as your first move — a cheaper agent that
returns two pages of prose costs more main context than a stronger one that
returns a table.

---

## 1. Bound the return. (Largest single lever.)

A subagent's final message is injected into your context verbatim. That return
is the entire bill for the delegation, and it is the one thing you fully
control from the prompt.

| Return style | Main-context cost |
|---|---|
| "Report your findings" → prose | ~1,500–2,500 tokens |
| "Return a file:line table, max 20 rows, no prose" | ~200–300 tokens |
| "Return one word: PASS or FAIL, plus failing lines only" | ~30–80 tokens |

Always state the format and a hard cap. An unbounded return from ten parallel
agents will exhaust the context you delegated to protect.

---

### Compress the return itself

Nobody reads an agent's return as prose. It goes machine-to-machine: the
orchestrator parses it and acts. So grammar in a return is pure waste.

Strip articles, bullets, backticks, em-dashes and full sentences from the
format you ask for. Measured on a realistic 12-row locator result:

| Format | Cost | vs baseline |
|---|---|---|
| Prose rows with backticks and em-dashes | 103 tok | — |
| Space-separated tagged rows | 64 tok | **−38%** |
| Bare `path:line` lines | 21 tok | **−80%** |

Across thirty locator delegations that is roughly 1,200 tokens saved by format
alone, before touching what the agent actually did.

**Two hard exceptions.** Never compress identifiers or evidence: file paths,
line numbers, symbol names, quoted error text, exit codes. A shortened path is
a wrong answer, and a paraphrased compiler error is unusable to whoever greps
for it. Compress the agent's own words; never its payload.

Offer a second, cheaper tier for when coordinates are all you need — "paths
only" is the single largest format saving available and covers most locator
calls.

## 2. Hand off through disk, not through context.

For anything whose output is larger than a screen, have the agent **write a
file and return the path**.

```
Write your full findings to notes/audit-<area>.md. Return only: the path, a
one-line verdict, and the three highest-severity items. Nothing else.
```

Cost of the return drops from ~2,000 tokens to ~40. The full work still exists
— you read the slice you need, when you need it, with an offset. Ten agents
writing ten files cost you ten paths, not twenty pages.

This is also how findings survive the session. A report in context dies at the
next `/clear`; a report on disk is still there tomorrow, and can be committed,
diffed, and linked from a notes vault. If you keep a knowledge base, point the
agents at it: durable notes are the cheapest possible memory, because they cost
nothing until read.

**Rule of thumb:** if the output would exceed ~500 tokens, it belongs in a file.

---

## 3. Name your agents. Amortize the prompt.

A named agent's system prompt lives in `.claude/agents/<name>.md` and loads
into the **subagent's** context. Your side pays only its `description` in the
agent listing.

Measured on a real three-agent set:

| | Main context | Subagent context |
|---|---|---|
| Agent listing (per agent, always loaded) | 90–108 tokens | — |
| Agent system prompt | **0** | 416–489 tokens |
| Delegation message, full inline contract | ~131 tokens | — |
| Delegation message, named agent | **~19 tokens** | — |

The output contract, tool restrictions, scope rules, refusals, model, and
effort all move into the file. Saving is ~110 tokens per delegation — about
2,200 over twenty — and the quality goes *up*, because a written contract is
more complete than one improvised per call.

Define an agent as soon as you have spawned the same kind of worker twice.

---

## 4. Preload skills instead of restating rules.

`skills: [my-skill]` in agent frontmatter injects the skill's full content into
the agent at startup. Without it you must restate the rules in every delegation
prompt, at your own expense, less completely each time.

Subagents inherit **no** skills by default. This is also a correctness fix, not
only a saving: an un-briefed agent silently drops the standard you thought you
were enforcing.

---

## 5. Nest, so intermediate output never surfaces.

A subagent can spawn its own subagents (three layers deep by default). Only the
top-level agent's summary returns to you.

A reviewer that dispatches one verifier per finding keeps every verifier's
reasoning inside the reviewer's context. You receive one verdict list instead
of N verification transcripts. For a fan-out of eight verifiers this is the
difference between ~60 tokens and several thousand.

---

## 6. Give agents persistent memory.

`memory: user | project | local` in agent frontmatter gives an agent
cross-session recall. A reviewer that already knows your conventions does not
need them re-explained every session.

Related: `SendMessage` resumes an existing agent with its full history intact,
rather than paying a cold start to re-derive context it already had. Resume
when continuing the same thread of work; spawn fresh when the task is genuinely
new.

---

## 7. Prefer the cheap cold start where it is safe.

`Explore` skips `CLAUDE.md` and git status, which makes it cheaper to start —
at the cost of not knowing your project rules. Fine for pure location lookups.
Not fine when a project rule affects the answer; restate the rule or use an
agent that loads it.

---

## What not to do

- **Do not downgrade the model as a first resort.** Right-size it — mechanical
  scanning genuinely suits a small model — but a weak agent that misunderstands
  the task costs a re-run, which is the most expensive outcome available.
- **Do not delegate to save money.** It does not. Delegate to protect context.
- **Do not spawn agents whose returns you have not bounded.** That is the one
  mistake that makes delegation strictly worse than doing the work inline.

## Ranked summary

1. Bound the return format and cap it.
2. Route large output through disk; return a path.
3. Name recurring agents so the contract stops living in the prompt.
4. Preload skills rather than restating them.
5. Nest fan-outs so intermediate work never surfaces.
6. Use agent memory and resume instead of re-deriving context.
