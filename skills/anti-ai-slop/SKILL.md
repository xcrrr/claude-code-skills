---
name: anti-ai-slop
description: >
  Design rules for building websites, apps, landing pages, dashboards, and UI
  that do not look AI-generated. Load BEFORE writing any HTML, CSS, Tailwind,
  React component, landing page, or design system — and before choosing any
  color, font, or gradient. Replaces the default purple-gradient-neon-glass
  aesthetic with editorial design: warm neutral grounds, serif display type,
  one muted accent, real whitespace, almost no effects.
when_to_use: >
  Any request to build, style, redesign, or improve the look of a website, web
  app, landing page, marketing site, dashboard, component, or artifact. Also
  when asked to make something "look better", "look professional", "look
  premium", or "not look AI-made".
---

# Anti-AI-slop design

There is a house style that image and code models fall into by default, and
everyone can now recognize it on sight. It reads as cheap because it is
free — it costs no decisions. This skill is a standing instruction to spend
the decisions.

**The rule underneath every rule below: subtract.** Slop is additive — one more
gradient, one more glow, one more emoji, one more floating blob. Good design is
what survives removal. If an element has no job, delete it rather than style it.

## The look you are producing instead

Editorial, not futuristic. Think a well-set magazine or a serious print annual
report rendered for screen: warm paper-toned ground, a real typographic
hierarchy carrying the page, generous margins, one restrained accent, and
almost no effects. Confident enough to be quiet.

Quality lives in **type, spacing, and restraint** — never in effects.

## Six rules

### 1. Warm neutral ground. Never pure white, never pure black.

`#FFFFFF` and `#000000` are the tells. Real design systems sit on warm
off-whites and near-blacks that still carry a hue.

- Page: a cream or warm ivory (`#FAF9F5`, `#F7F6F2`)
- Raised surface: one step warmer/darker (`#F0EEE6`, `#EBE9E1`)
- Text: a near-black with warmth (`#141413`, `#1A1A18`) — not `#000`
- Secondary text: a warm mid-grey (`#6B6A63`, `#87867F`) — not `#999`

Dark mode is a warm charcoal (`#1A1A18`) with cream text, never a blue-black
"space" background.

### 2. Exactly one accent, and make it earthy.

One accent color. Not a palette of five. Not a gradient between two.

Reach for clay, terracotta, rust, ochre, moss, deep teal, oxblood — colors with
some grey and warmth in them (`#D97757`, `#C4622D`, `#5A6B4F`, `#1F4D4A`).

Never: electric purple `#8B5CF6`, indigo `#6366F1`, hot magenta, cyan, lime, or
anything that reads as neon. Purple-to-blue is the single most recognizable AI
signature — treat it as forbidden.

Use the accent for *one* thing per screen: the primary action, or a rule, or a
small mark. If it appears everywhere it stops meaning anything.

### 3. Serif for display, sans for body, mono for labels.

**Serif titles are the highest-signal move in this entire skill.** They
instantly separate a page from the sans-everywhere default.

- Display/headings: a real serif with personality — a transitional or
  old-style face. Web-safe fallback chain ending in `Georgia, serif`.
- Body: a clean neutral sans at comfortable size (17–19px, not 14px).
- Eyebrows, labels, metadata, captions: monospace, small, uppercase, with
  positive letter-spacing (`0.08em`). This one detail does enormous work.

Weights: live at **300 and 400**. Use 500/600 for emphasis. Reserve 700 for
rare moments. **Never 800 or 900** — ultrabold everywhere is a slop marker.

Tracking: tighten large display type (`-0.02em` to `-0.03em`). Leave body at
normal. Loosen only small uppercase labels.

Line-height: `1.05–1.15` for display, `1.5–1.65` for body. Never set body at 1.2.

### 4. Effects budget: near zero.

A serious brand stylesheet of ~280 KB will contain roughly **five** gradients
total, one radial, and zero backdrop-filters. That is the target ratio, and it
should feel restrictive.

- **Gradients**: default to none. A barely-perceptible tonal wash between two
  neighbouring neutrals is the only acceptable use. Never accent-to-accent,
  never on text, never on a hero.
- **Glows**: never. A shadow tinted with the accent color is pure slop.
- **Glassmorphism** (`backdrop-filter: blur()` + translucent panel): never.
- **Shadows**: sparing, soft, neutral, low-opacity —
  `0 1px 2px rgba(20,20,19,0.06)`. Prefer a **1px hairline border** in a warm
  grey over a shadow. Borders are more editorial than elevation.
- **Animation**: micro only — opacity and 2–4px translate, 150–250ms, ease-out.
  No floating blobs, no aurora, no parallax, no scroll-jacking, no
  spring-bouncing cards.

### 5. Radius stays modest.

`4px` small, `8px` default, `16px` large, or a **full pill** (`999px`) for
buttons and tags. Nothing in between reads as considered — the 20–28px blob
radius on every card is a slop marker. Many of the best surfaces are `0`.

Pick one radius scale and use it everywhere. Mixed radii look accidental.

### 6. Whitespace is the design.

Space is the main tool, not a leftover. Section padding should feel almost
uncomfortable — `96–160px` vertical on desktop. Measure caps at `65–75ch`.

Build on a real spacing scale (4/8/12/16/24/32/48/64/96/128) and never
freehand a margin.

Layout should be **editorial and asymmetric**: a strong left-aligned column,
generous outer margins, content that breathes. Not everything centered. Not
three identical icon-title-paragraph cards in a row.

## Before you write any markup

Answer these three, in one line each. If you can't, you're about to produce
slop:

1. **What is the ground?** (the exact off-white or charcoal)
2. **What is the one accent, and what single job does it do?**
3. **What is the display face, and does it contrast with the body face?**

## The slop tells

If any of these are present, the work is not done. Full catalog with fixes in
`references/slop-catalog.md`.

- Purple/indigo→blue gradient anywhere, especially a hero
- Gradient-clipped heading text
- Dark "space" background with neon accents
- Glassmorphic translucent blurred cards
- Accent-colored glow shadows
- Emoji used as feature icons or section markers (🚀 ✨ 💡 🔥)
- Copy like "Supercharge your workflow", "Unleash the power of", "10x your"
- An `✨ AI-Powered` badge pill above the hero headline
- A bento grid of equal rounded cards with no hierarchy
- Everything centered, at every breakpoint
- Sans-serif at weight 800 for every heading
- Floating animated blobs, aurora washes, or particle fields
- Generic 3D abstract shapes as hero art
- Three feature cards, each icon + three-word title + two lines of filler

## Content, not decoration

Slop decorates because it has nothing to say. Write the real words first —
real product names, real numbers, real copy — then set them well. A page with
honest content and plain type beats a beautiful shell around lorem ipsum.

If you must use imagery: real photography, a real screenshot, or restrained
line/editorial illustration. Never generic 3D gradient abstractions.

Accessibility is part of the look: body text ≥ 16px, contrast ≥ 4.5:1, real
focus states, and semantic HTML. Warm neutrals make this easy — verify anyway.

## Working with the other skills

- **`agent-orchestration`**: when delegating UI work to a subagent, preload
  this skill into it — add `skills: [anti-ai-slop]` to the agent's frontmatter,
  or restate the ground/accent/typeface decisions in the delegation prompt.
  A subagent does **not** inherit this skill by default, and an un-briefed
  design agent will produce the exact slop this skill exists to prevent.
- **Terse output modes** (such as caveman-style compression): those govern
  *chat prose only*. Code, CSS, and design tokens are always written in full,
  properly formatted, with no compression. Never let a terseness mode shorten a
  stylesheet or drop accessibility attributes.

## Reference material

- `references/tokens.md` — copy-paste palettes, type scales, spacing scale,
  and a starter CSS custom-property block for both light and dark.
- `references/slop-catalog.md` — every tell above, why it reads as cheap, and
  the specific replacement.
