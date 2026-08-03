# Claude Code Skills

Skills that change how Claude Code *works*, not what it knows.

Three skills, three subagents, a guard hook, and three scripts that measure and
remove real token costs. No configuration, no wrappers, no MCP server, no
service. Drop the folders in `~/.claude/` and Claude picks them up.

Everything here is either traceable to published Anthropic material or measured
on this machine, with the numbers printed so you can check them.

---

## What's in it

| | Name | Does |
|---|---|---|
| **skill** | `agent-orchestration` | When to delegate to subagents, how many, which model and effort — and when not to |
| **skill** | `anti-ai-slop` | Stops the purple-gradient-neon-glass default; produces editorial design instead |
| **skill** | `preflight` | The verification gate before calling work done or deploying |
| **agent** | `scout` | Read-only code locator, compressed `file:line` output |
| **agent** | `gate` | Runs typecheck/build/lint, returns the verdict and failing lines only |
| **agent** | `design-critic` | Audits UI against the anti-slop rules |
| **hook** | `guard-scope` | Locks edits to one directory when you want it |
| **script** | `delegation-audit.py` | Measures the real leverage of every delegation you have run |
| **script** | `warm-start.py` | Removes a subagent's orientation cost with a computed repo map |
| **script** | `install-briefings.sh` | Rolls that out across every repo, refreshed on commit |

## Install

```bash
git clone https://github.com/xcrrr/claude-code-skills.git
cd claude-code-skills
cp -r skills/* ~/.claude/skills/
cp -r agents/*.md ~/.claude/agents/
```

Restart once if `~/.claude/skills/` or `~/.claude/agents/` did not exist before.
For a single project, copy into `.claude/` in the repo instead.

Optional, and recommended if you delegate a lot:

```bash
bash skills/agent-orchestration/scripts/install-briefings.sh ~/repos
```

---

## The skills

### `agent-orchestration`

Out of the box Claude delegates inconsistently — forty files read inline
burning your context, then five agents spawned for a job that needed one. This
gives it a decision procedure: four gates before spawning, a fleet-sizing
table, model-versus-effort routing, a four-part prompt contract, and an
anti-pattern list.

It also ships the two tools below, because advice about token economy is
unfalsifiable unless you can check it.

#### It measures itself

Claude Code writes every subagent transcript to disk with per-message token
usage. That is enough to compute the only ratio that matters:

```
leverage = tokens the agent processed / tokens it returned to you
```

`python3 scripts/delegation-audit.py` — real output from the session that built
this repository:

```
  agent           model        tools    absorbed  returned  leverage
  a5d36db1e601a1  sonnet-5         5     105,191       996      106x
  aa37d70412f433  sonnet-5        12     269,572     2,158      125x
  a746bb6bd995e2  sonnet-5        32     222,308     1,144      194x
  abc92aa8581bc0  haiku-4-5        17     318,210        29    10973x

  TOTAL                                  915,281     4,327      212x

  Worth changing:
    a5d36db1e601a1  unbounded return (996 tok): cap the output format
    aa37d70412f433  unbounded return (2158 tok): cap the output format
    a746bb6bd995e2  unbounded return (1144 tok): cap the output format
```

Four delegations absorbed **915,281 tokens** and charged the main conversation
**4,327**. The tool then flagged three of those four for uncapped returns —
exactly the mistake this repo's own skill warns about. It criticizes its author
with real data; that is the reason to ship it instead of another table of
estimates.

Below 10× the work belonged inline. Above 100× the delegation earned its cold
start.

#### It deletes the cold start

A subagent's first ten to thirty tool calls are usually not the work. They are
orientation: what stack is this, where does the source live, how do I build it.
Every agent in a fleet re-derives that same map separately — and **none of it
needs a model.** Where files live is a fact you can compute.

```bash
python3 scripts/warm-start.py     # writes .claude/briefing.md
```

Measured on a real 97-file TanStack/Vite repo:

| | Cost | Answers |
|---|---|---|
| Bare `find` of source files | ~745 tok | paths only |
| `.claude/briefing.md` | **~315 tok** | stack, package manager, build/test/lint commands, layout, entry points, traps |

Less than half the tokens of the crudest possible orientation call, and unlike
that call it answers the questions the agent was about to ask.

Two properties stop it from merely relocating the cost. It is **deterministic**
— a briefing that costs an LLM call has just moved the cold start elsewhere.
And it is **byte-stable**: everything is sorted, so an unchanged repo
regenerates identically and stays prompt-cache friendly rather than
invalidating on every run. Verify by hashing two consecutive runs.

`install-briefings.sh` rolls it across every repo in a directory and adds a
post-commit hook to keep it current. The ignore goes in `.git/info/exclude`,
which is local and untracked — so ten repositories gain a generated file with
**no tracked file modified**, no diff noise, and nothing for a collaborator to
see. `--uninstall` reverses all of it.

### `anti-ai-slop`

Stops the aesthetic everyone now recognizes on sight: purple-to-blue gradients,
neon on near-black, glassmorphic cards, glow shadows, emoji as icons,
800-weight sans headings over "Supercharge your workflow".

Replaces it with an editorial one — warm paper grounds, **serif display type**,
a single muted earthy accent, modest radii, and an effects budget near zero.

The rules are derived, not asserted. Reading the real stylesheets of design
systems that get this right gives hard numbers: in ~280 KB of one such brand
CSS there are **5 linear-gradients, 1 radial, and 0 backdrop-filters**, with
font weights living at 300–400 and radii between 4 and 16px. That ratio is the
target, and it should feel restrictive.

`references/tokens.md` has copy-paste palettes, type scales and starter CSS;
`references/slop-catalog.md` lists every tell with its replacement.

### `preflight`

The gate before "done": typecheck → build → lint → tests, stop at the first
failure, plus the traps that hide in scaffolded projects — the missing build-output
entry in `eslint.config.js` ignores that turns an 8-second lint into a
multi-minute hang, two lockfiles, undeclared transitive dependencies. And four
checks before any deploy, including that nothing fabricated ships.

---

## The agents

Naming an agent is a token optimization as much as an organizational one. Its
system prompt loads into the **subagent's** context, so your main conversation
pays only the one-line description, and the delegation message shrinks from a
written contract to a sentence.

| | Main context | Subagent context |
|---|---|---|
| Listing entry, per agent | 90–108 tok | — |
| System prompt | **0** | 551–624 tok |
| Delegation message, inline contract | ~131 tok | — |
| Delegation message, named agent | **~19 tok** | — |

### Their returns are compressed on purpose

Nobody reads an agent's return as prose — it goes machine-to-machine. So the
output formats strip articles, bullets, backticks, em-dashes and sentences.
Measured on a realistic 12-row locator result:

| Format | Cost | vs baseline |
|---|---|---|
| Prose rows with backticks and dashes | 103 tok | — |
| Space-separated tagged rows | 64 tok | **−38%** |
| Bare `path:line` lines | 21 tok | **−80%** |

`scout` takes a *paths only* request and drops to the third row. Combined
return budgets across the three agents fell from 1,000 to 750 tokens.

**Two things are never compressed:** identifiers and evidence. File paths, line
numbers, symbol names, quoted compiler errors and exit codes stay verbatim —
a shortened path is a wrong answer and a paraphrased error is unusable. The
agents say so explicitly, because a model told to "be terse" will otherwise
tidy an error message.

All three are read-or-report only. None edits, deploys, or pushes.

---

## Honest accounting

### It does not save tokens. It saves your context window.

Delegating **increases** total spend — Anthropic measured multi-agent systems at
roughly **15× the tokens of a chat interaction**; single agents about **4×**.
The subagent still reads everything, and you pay for a cold start on top.

What you buy is the scarce resource. Claude Code's own docs put it flatly:
"Claude's context window fills up fast, and performance degrades as it fills."
The audit above is what that purchase looks like measured: 915,281 tokens of
material for 4,327 tokens of context.

**Delegate to protect context, not to save money.** If your goal is a lower
bill, delegate less and prompt better — and check your session's model and
effort defaults before blaming anything here.

### Quality: strong evidence for the technique, none for these skills

Anthropic's published result: an **Opus lead with Sonnet subagents outperformed
single-agent Opus by 90.2%** on their internal research eval; token usage alone
explained **80% of performance variance** on BrowseComp. Those measure
orchestration done well, in their harness. **They are not a measurement of this
repository.** No controlled A/B has been run here, and saying so beats implying
a number nobody produced.

For `anti-ai-slop` there is no metric at all and no honest way to invent one —
only the derivation, with counts stated so you can check them.

### The limits, stated

Anthropic is blunt about where this fails, and the skill repeats it rather than
burying it:

> Multi-agent systems are ineffective for domains requiring all agents to share
> the same context or involving many dependencies between agents. **Most coding
> tasks lack sufficient parallelizable work.**

So a skill about delegation spends a third of its length saying *don't*. Four
gates must pass. Tightly-coupled implementation stays inline.

The cold-start measurement compares the briefing against the cheapest
alternative; it is not a controlled before/after on tool-call counts. And the
briefing cannot supply task context — what you learned three turns ago still
has to go in the prompt.

### What it costs to install

| State | Context cost |
|---|---|
| A skill installed and idle | ~180 tok |
| Loaded for a task | ~2,100 tok |
| Plus a reference file when needed | +1,300–2,600 tok |
| An agent, idle | 90–108 tok |

One avoided inline file-read pays for all of it.

---

## How they compose

- `agent-orchestration` decides **whether** work is delegated; `anti-ai-slop`
  decides **what the output looks like**; `preflight` decides **whether it is
  done**. Different axes.
- A subagent inherits **no** skills by default. `gate` and `design-critic`
  therefore preload theirs with the `skills:` field. Without it an un-briefed
  agent silently drops the standard you assumed was enforced — the most common
  way a good decision is lost across a delegation.
- Terse-output modes elsewhere in your setup compress **chat prose only**. Every
  skill here states that code, CSS, accessibility attributes and error text are
  written in full.

## Companion stacks

Two MIT-licensed projects pair well and are recommended rather than absorbed —
install from source so you get their maintenance, not a stale copy. Attribution
and reasoning in [CREDITS.md](CREDITS.md).

- **[caveman](https://github.com/JuliusBrussee/caveman)** (Julius Brussee) —
  compresses conversational output. Its exclusion of code and security warnings
  is what makes it safe alongside `anti-ai-slop`.
- **[gstack](https://github.com/garrytan/gstack)** (Garry Tan) — a large
  opinionated setup. Nothing was copied: an inventory of its 62 skills found
  most coupled to its own toolchain, Supabase-backed memory, telemetry or
  Codex, and the self-contained ones run 37–127 KB each. The `guard-scope` hook
  here is a clean reimplementation of its `freeze` pattern, credited.

## Sources

- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) — orchestrator-worker pattern, the 15× and 90.2% figures, fleet sizing, failure modes
- [Claude Code best practices](https://code.claude.com/docs/en/best-practices) — context as the binding constraint, verification, adversarial review
- [Subagents](https://code.claude.com/docs/en/sub-agents) — frontmatter, limits, tool filters, context isolation, transcript paths
- [Model configuration](https://code.claude.com/docs/en/model-config) — effort levels
- [Choosing a model and effort level](https://claude.com/blog/claude-model-and-effort-level-in-claude-code) — model vs effort as separate dials
- [Skills](https://code.claude.com/docs/en/skills) — the SKILL.md format

## Contributing

Corrections welcome, especially where Claude Code has moved on — the mechanics
reference is version-sensitive and pinned to v2.1.219. If a limit, default or
tool filter has changed, open an issue with the version you are on.

Each addition has to clear the same bar: a real practice, traceable to evidence
or measured on a real repo, with the costs stated as plainly as the benefits.

## License

MIT
