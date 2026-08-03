# Agents

Three named subagents. Naming an agent is a token optimization as much as an
organizational one: the system prompt below loads into the **subagent's**
context, so your main conversation pays only the one-line `description` in the
agent listing, and the delegation message shrinks from a full written contract
(~130 tokens) to a sentence (~20).

Measured on this set:

| | Main context | Subagent context |
|---|---|---|
| Listing entry, per agent | 90–108 tok | — |
| System prompt | **0** | 416–489 tok |

| Agent | Job | Returns |
|---|---|---|
| `scout` | Read-only code locator | `file:line` table, max 25 rows |
| `gate` | Runs typecheck/build/lint | `PASS`, or the failing lines only |
| `design-critic` | Audits UI against the anti-slop rules | One line per finding + verdict |

`gate` preloads the `preflight` skill and `design-critic` preloads
`anti-ai-slop` via the `skills:` field, so neither needs its standards
restated in the delegation prompt. Subagents inherit no skills by default —
without that field the standard silently does not apply.

All three are read-or-report only. None edits, deploys, or pushes: those stay
in the main thread where a human is watching.

## Install

```bash
cp agents/*.md ~/.claude/agents/       # all projects
# or, for one repo:
cp agents/*.md .claude/agents/
```

Claude Code picks them up within seconds — no restart needed, unless this is
the first file in a newly created `agents/` directory.

Invoke by naming them (`use scout to find every call site of X`), or
`@`-mention to force the choice.

`gate` and `design-critic` reference this repo's `preflight` and
`anti-ai-slop` skills. `scout` is standalone.
