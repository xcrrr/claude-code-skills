# Killing the cold start

Delegation's worst tax is the one nobody itemizes. A subagent begins knowing
nothing about your repository, so before it can do the work you asked for, it
spends tool calls discovering things that were never in question.

## Cold start is three costs, not one

**1. Orientation.** What stack is this, where does the source live, how do I
build and test it, where are the entry points. Typically ten to thirty tool
calls per agent.

**2. Convention.** How this codebase does things, what is forbidden. Non-Explore
subagents get the full `CLAUDE.md` hierarchy automatically, so this is mostly
solved — but `Explore` and `Plan` skip it, and restating the one rule that
matters is on you.

**3. Task context.** What the orchestrator already learned this session. This
cannot be computed; it has to go in the delegation prompt.

Only (3) is irreducible. **(1) is the expensive one, and it is pure repeated
waste** — every agent in a fleet re-derives the same map, in parallel,
separately, and none of that derivation needed a language model. Where files
live is a fact.

## The fix: compute the map, don't discover it

`scripts/warm-start.py` walks the repository and writes `.claude/briefing.md` —
stack, package manager, real build/test/lint commands, a directory map with
file counts, entry points, and detected traps.

```bash
python3 scripts/warm-start.py            # writes .claude/briefing.md
python3 scripts/warm-start.py --stdout   # inspect without writing
```

Then one line in each agent's system prompt:

> First action, always: if `.claude/briefing.md` exists, read it. Never `find`
> or `ls -R` the repo to orient yourself.

Orientation collapses from a search loop to a single Read.

### Measured

On a real 97-file TanStack/Vite repo:

| | Cost | Answers |
|---|---|---|
| Bare `find` of source files | **~745 tokens** | paths only |
| `.claude/briefing.md` | **~315 tokens** | stack, package manager, build/lint/dev commands, layout with counts, entry points, traps, branch |

Less than half the tokens of the crudest possible orientation call, and unlike
that call it actually answers the questions the agent was going to ask next.
That is before counting the round-trips saved: each avoided grep costs a tool
call, its result, and a turn.

## Why it has to be deterministic and sorted

Two properties do the real work, and both are easy to lose:

**Deterministic** — no model builds it, so generating it is free and
reproducible. A briefing that costs an LLM call to produce has just moved the
cold start somewhere else.

**Byte-stable** — every list is sorted, so regenerating an unchanged repo
produces a byte-identical file. This matters more than it looks: identical
content across agents and across runs stays prompt-cache friendly, while a
briefing that reorders itself on every run invalidates the cache and quietly
charges full price each time. The script reports `unchanged` when this holds.

Verify it yourself:

```bash
python3 scripts/warm-start.py --stdout | sha256sum   # run twice, compare
```

**Small** — hard-capped at ~2000 tokens (`--max-tokens`). A briefing larger
than the search it replaces is not a fix. Real repos land at 300–800.

## The cache variant, for fleets

A subagent's cacheable prefix is its system prompt region, not its tool
results. So reading the briefing as a file costs each agent full price for
those ~315 tokens.

If you are spawning many agents against one repo, preload instead: put the
generated briefing in a project skill and name it in agent frontmatter.

```yaml
skills: [repo-briefing]
```

Now the briefing lands in the prefix rather than in a tool result, and the
second and later agents in a fleet hit warm cache for it. The tradeoff is a
missing skill breaks the agent, so the file-read form is the safer default and
the preload form is the optimization for a known repo.

## Keeping it fresh

The briefing describes structure, which changes slowly — a stale layout is
usually still a useful layout. Regenerate when directories move, dependencies
change, or a script is added. A post-commit hook is the obvious home if you
want it automatic; it takes well under a second on a normal repo.

If a briefing is wrong, that is worse than missing: an agent trusts it. The
script only reports facts it computed from the filesystem — no inference, no
guessing — for exactly this reason.

## What this does not solve

Task context. The agent still does not know what you learned three turns ago,
and the briefing cannot tell it. Scout once, then put the concrete paths in the
delegation prompt — a map plus exact coordinates beats either alone.
