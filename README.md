# Claude Code Skills

Skills that change how Claude Code *works*, not what it knows.

Each skill here encodes a working practice — distilled from Anthropic's own
published research and docs — into a form Claude loads automatically when it's
relevant. No configuration, no wrappers, no MCP server. Drop a folder in
`~/.claude/skills/` and Claude picks it up.

---

## Skills

### `agent-orchestration`

Teaches Claude Code to delegate to subagents deliberately: **when** to spawn one,
**how many**, **which model and effort level**, **how to write the delegation
prompt** — and, just as importantly, **when not to delegate at all**.

Out of the box, Claude delegates inconsistently. It will read forty files inline
and burn your context, then spawn five agents for a task that needed one. This
skill gives it a decision procedure instead of an instinct.

**What it contains**

| File | Loads | Purpose |
|---|---|---|
| `SKILL.md` | when the task is non-trivial | 4-gate delegation decision, fleet-sizing table, model/effort routing, prompt contract, anti-patterns |
| `references/prompt-contract.md` | on demand | Delegation prompt template, before/after examples, output-format recipes |
| `references/patterns.md` | on demand | 8 orchestration shapes: parallel scout, locate→act→verify, pipeline, adversarial verify, writer/reviewer, fan-out migration, loop-until-dry, completeness critic |
| `references/token-economics.md` | on demand | What delegation costs and the six levers that cut main-context spend, ranked |
| `references/mechanics.md` | on demand | Hard limits, tool filters, what actually loads into a subagent, resuming, custom agent frontmatter |
| `scripts/delegation-audit.py` | on request | Measures the real leverage of every delegation you have run |

#### It measures itself

Most advice about token economy is unfalsifiable. This skill ships a script that
checks whether the advice worked, using Claude Code's own subagent transcripts —
which record per-message token usage on disk.

```
leverage = tokens the agent processed / tokens it returned to you
```

Run `python3 scripts/delegation-audit.py`. Real output from the session that
built this repository:

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

Four delegations absorbed **915,281 tokens** of material and charged the main
conversation **4,327** — a 212× ratio. And the tool immediately flagged three of
those four as having returns that were never capped, which is exactly the
mistake this repo's own skill warns about. It criticizes its author with real
data; that is the point of shipping it.

Leverage below 10× means the work belonged inline. Above 100× means the
delegation earned its cold start.

### `anti-ai-slop`

Stops Claude from producing the aesthetic everyone now recognizes on sight:
purple-to-blue gradients, neon on near-black, glassmorphic cards, glow shadows,
emoji as icons, and 800-weight sans headings over "Supercharge your workflow".

It replaces that default with an editorial one — warm paper-toned grounds,
**serif display type**, a single muted earthy accent, modest radii, and an
effects budget close to zero. Quality carried by type, spacing, and restraint
instead of decoration.

The rules aren't taste assertions. They were derived by reading the actual
stylesheets of design systems that get this right: in ~280 KB of one such brand
CSS there are **5 linear-gradients, 1 radial, and 0 backdrop-filters**, with
font weights living at 300–400 and border radii between 4 and 16px. That ratio
is the target, and it should feel restrictive.

| File | Loads | Purpose |
|---|---|---|
| `SKILL.md` | before any UI/CSS/markup work | Six rules, the pre-flight questions, the tells, content-over-decoration |
| `references/tokens.md` | on demand | Palettes, type scale, spacing, radius/shadow systems, starter CSS and Tailwind config |
| `references/slop-catalog.md` | on demand | Every tell, why it reads as cheap, and the specific replacement |

---

## Install

```bash
git clone https://github.com/xcrrr/claude-code-skills.git
cp -r claude-code-skills/skills/* ~/.claude/skills/
```

Restart Claude Code once if `~/.claude/skills/` didn't exist before. That's it —
Claude loads the skill on its own when a task calls for it, or you can invoke it
directly with `/agent-orchestration`.

For a single project instead of globally, copy into `.claude/skills/` in the
repo.

---

## Does it actually help? An honest accounting

Three separate questions get conflated in every "AI agents" pitch. Here they are
separated, with the evidence labelled by how strong it is.

### It does **not** save tokens. It saves your context window.

This is the part most agent tooling gets wrong or hides.

Delegating work to subagents **increases total token spend.** Anthropic measured
their multi-agent research system at roughly **15× the tokens of a chat
interaction**; single agents run about **4×**. The subagent still reads every
file — you're paying for that reading, plus the cold-start cost of an agent that
begins with none of your context.

What you buy for that is the scarce resource: **the main conversation's context
window.** Claude Code's own best-practices doc puts it flatly — "Claude's context
window fills up fast, and performance degrades as it fills." A subagent reads in
its own window and hands back a summary. The files never touch yours.

**Measured on a mid-size Python codebase** (~9 relevant files, private repo,
paths withheld):

| Approach | Main-context cost |
|---|---|
| Answer one architecture question by reading the relevant files inline | **~43,000 tokens** |
| Same question, delegated with this skill's bounded output contract | **~400 tokens** |

That's roughly **100× less main-context consumption for that question** — and it
is a measurement of *input volume*, not of answer quality. The reading still
happened; it just happened somewhere that doesn't cost you the rest of your
session.

If you take one thing from this repo: **delegate to protect context, not to save
money.** If your goal is a lower bill, delegate less and prompt better.

### Quality: strong evidence for the technique, none yet for this skill

Anthropic's published result, on their internal research eval: a multi-agent
system with an **Opus lead and Sonnet subagents outperformed single-agent Opus by
90.2%**. They also found **token usage alone explains 80% of performance
variance** on BrowseComp, and that parallel tool calling cut research time by
**up to 90%**.

Those numbers measure *orchestration done well*, in Anthropic's harness, on
research tasks. They are the reason this skill exists. **They are not a
measurement of this skill.** No controlled A/B of Claude Code with and without it
has been run here, and saying so beats implying a number nobody produced.

What the skill demonstrably does is make the technique *reachable*: the routing
rules, the fleet-sizing table, and the prompt contract are exactly the practices
those results came from, written where the model will actually read them.

### And for `anti-ai-slop`: no metric, by nature

Design quality isn't measurable the way context consumption is, and no number
here would be honest. What the skill *does* have is derivation: its rules come
from reading the real stylesheets of design systems that are widely agreed to
be good, and the counts are stated so you can check them yourself — 5
gradients in 280 KB, weights at 300–400, radii 4–16px. The taste claim is that
those systems are worth imitating. Judge that one by eye.

### The honest limits

The same Anthropic post is blunt about where this fails, and the skill repeats it
rather than burying it:

> Multi-agent systems are ineffective for domains requiring all agents to share
> the same context or involving many dependencies between agents. **Most coding
> tasks lack sufficient parallelizable work.**

So a skill whose whole job is delegation spends a third of its length telling
Claude *not* to delegate. Four gates have to pass first. Tightly-coupled
implementation work stays inline, and the skill says so plainly.

If you were hoping for "spawn 10 agents, go 10× faster" — that isn't the finding,
and this isn't that repo.

### What it costs you to install

Progressive disclosure means the skill is nearly free until it's used:

| State | Context cost |
|---|---|
| Installed, idle (description in the skill listing) | **~180 tokens** |
| Loaded for a task | **~2,100 tokens** (`SKILL.md`) |
| Plus a reference file, when a detail is needed | +1,300–2,600 tokens |

One avoided inline file-read pays for it many times over. The whole repo is 29 KB
and never loads at once.

---

## How the skills work together

They're designed to compose rather than collide:

- `agent-orchestration` decides **whether and how** work gets delegated.
  `anti-ai-slop` decides **what the output looks like**. Different axes.
- A subagent inherits **no** skills by default. So `anti-ai-slop` explicitly
  tells you to preload it into any design-related subagent
  (`skills: [anti-ai-slop]` in the agent frontmatter, or restate the ground,
  accent, and typeface decisions in the delegation prompt). An un-briefed
  design agent produces exactly the slop the skill exists to prevent — this is
  the most common way a good design decision gets lost across a delegation.
- Terse-output modes (see companion stacks below) compress **chat prose only**.
  Both skills state that code, CSS, and accessibility attributes are always
  written in full.

---

## Companion stacks

Two other MIT-licensed projects pair well with these, and are recommended
rather than absorbed — install them from source so you get their maintenance
instead of a stale copy. Full attribution and the reasoning in
[CREDITS.md](CREDITS.md).

- **[caveman](https://github.com/JuliusBrussee/caveman)** (Julius Brussee, MIT)
  — compresses conversational output to cut tokens, and ships `cavecrew`
  subagents whose compressed reports make delegation returns cheaper. Its
  compression deliberately excludes code and security warnings, which is what
  makes it safe next to `anti-ai-slop`.
- **[gstack](https://github.com/garrytan/gstack)** (Garry Tan, MIT) — a large
  opinionated setup covering planning, review, QA, and release. Nothing was
  copied from it here: an inventory of its 62 skills found most are coupled to
  its own `bin/` toolchain, Supabase-backed memory, telemetry, or Codex, and
  the self-contained ones run 37–127 KB each — the spec skill alone is roughly
  32,000 tokens, which is the opposite of this repo's cheap-loading premise.
  Run the two side by side instead. CREDITS.md explains the call in full.

---

## Why a skill and not a CLAUDE.md rule

`CLAUDE.md` loads on **every** conversation, so everything in it competes for
attention with everything else — and Claude Code's docs warn that a bloated
`CLAUDE.md` causes Claude to ignore the rules inside it. A skill loads only when
the work calls for it. Orchestration guidance is exactly the kind of content that
matters intensely for some tasks and is noise for the rest.

If you want it applied unconditionally, add one line to `~/.claude/CLAUDE.md`:

```markdown
Before any task with more than one independent piece of work, load the
`agent-orchestration` skill and follow its delegation gates.
```

---

## Sources

Everything in these skills traces to published Anthropic material. No invented
numbers, no folklore.

- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) — orchestrator-worker pattern, the 15× and 90.2% figures, fleet-sizing rules, failure modes
- [Claude Code best practices](https://code.claude.com/docs/en/best-practices) — context as the binding constraint, verification loops, adversarial review
- [Subagents](https://code.claude.com/docs/en/sub-agents) — frontmatter spec, limits, tool filters, context isolation
- [Model configuration](https://code.claude.com/docs/en/model-config) — effort levels and their semantics
- [Choosing a Claude model and effort level](https://claude.com/blog/claude-model-and-effort-level-in-claude-code) — model vs effort as separate dials
- [Skills](https://code.claude.com/docs/en/skills) — the SKILL.md format itself

---

## Contributing

Corrections welcome, especially where Claude Code's behavior has moved on — the
mechanics reference is version-sensitive and pinned to v2.1.219. If a limit,
default, or tool filter has changed, open an issue with the version you're on.

More skills are planned. Each one has to clear the same bar: a real practice,
traceable to evidence, with the costs stated as plainly as the benefits.

## License

MIT
