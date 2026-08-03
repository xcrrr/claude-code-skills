# Credits and third-party licenses

This repository's skills are original work. It also recommends, and documents
interoperation with, the following independent projects. Both are MIT
licensed, which permits use, modification, and redistribution provided the
copyright and license notice are preserved.

Neither project is vendored into this repository. Install them from their own
sources so you get their maintenance and updates, not a stale copy.

---

## caveman

- Repository: https://github.com/JuliusBrussee/caveman
- Author: Julius Brussee
- License: MIT — `Copyright (c) 2026 Julius Brussee`

A Claude Code plugin that compresses conversational output to cut token usage.
Ships several skills (`/caveman`, `/caveman-commit`, `/caveman-review`,
`/caveman-stats`, `/caveman-compress`) plus a `cavecrew` set of
caveman-compressed subagents.

Install:

```
/plugin marketplace add JuliusBrussee/caveman
/plugin install caveman
```

**Interoperation with this repo:** caveman's compression governs *chat prose*.
It explicitly does not apply to code, commits, or security warnings. That
boundary is what makes it safe to run alongside `anti-ai-slop`, which needs
stylesheets and markup written in full. `cavecrew`'s compressed subagent output
also pairs well with `agent-orchestration`'s rule that a delegation's return
value is the thing that costs you context — a compressed report is a smaller
return.

---

## gstack

- Repository: https://github.com/garrytan/gstack
- Author: Garry Tan
- License: MIT — `Copyright (c) 2026 Garry Tan`

A large, opinionated Claude Code setup — 60+ skills plus a substantial
supporting toolchain, covering planning, review, QA, release, and persistent
project memory.

**What this repo took from it:** nothing, by deliberate choice, and the reason
is worth stating.

gstack is a *system*, not a skill collection. Most of its skills are coupled to
its own infrastructure: a `bin/` directory of 70+ custom CLI tools, a
Supabase-backed persistent memory service ("gbrain"), telemetry and analytics
sync, and Codex integration. An inventory of its 62 `SKILL.md` files found the
majority depend on at least one of those, so copying them here would produce
files that silently do not work.

The handful that *are* self-contained — its spec-writing, diff-review,
diagramming, and PDF-generation skills — are also very large (37 KB to 127 KB
each; the spec skill alone is roughly 32,000 tokens). Vendoring them would
contradict the cheap-progressive-disclosure principle this repo is built on,
and would make this repository a stale partial fork of a well-maintained
project rather than something with its own argument.

**So the recommendation is to run gstack alongside this repo, not to absorb
it.** Install it from source and the two coexist: gstack brings workflow
machinery, these skills bring orchestration judgment and design taste. If you
want its spec or review workflow, take it from the original where it stays
current.

If you would rather have adapted copies vendored here despite the above, the
license permits it — open an issue and say which ones.

---

## Notes on attribution

If any content from these projects is ever added to this repository, it must
arrive with its MIT notice intact and be marked as modified where modified.
That has not been necessary so far, since nothing has been copied.
