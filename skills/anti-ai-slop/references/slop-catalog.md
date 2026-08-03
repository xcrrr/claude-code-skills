# The slop catalog

Each entry: the tell, why it reads as cheap, and what to do instead.

---

## Color

**Purple→blue gradient hero.** `#6366F1 → #A855F7`, usually diagonal, usually
behind white 800-weight text. The single most recognizable machine-made
signature on the web — it was the default in a generation of templates, so it
now signals "nobody chose this."
→ Flat warm ground. If the hero needs weight, give it a large serif headline
and space, not a background.

**Gradient-clipped text.** `background-clip: text` on a heading.
→ Solid `--text`. Emphasize one word with the accent or an italic serif if you
need contrast.

**Neon on near-black.** Cyan/magenta/lime on `#0A0A0F`, often with a grid or
starfield. Reads as a crypto landing page from 2021.
→ Warm charcoal `#1A1A18`, cream text, one earthy accent.

**Five accent colors.** Every card, icon, and badge in a different hue.
→ One accent. Differentiate with type and space instead.

**Pure `#FFFFFF` and `#000000`.** No real brand system ships either as the
primary pair.
→ `#FAF9F5` and `#141413`.

---

## Effects

**Glassmorphism.** `backdrop-filter: blur(12px)` on a translucent white card
over a colorful blob field.
→ Opaque surface, hairline border, no blur.

**Accent glow shadows.** `box-shadow: 0 0 40px rgba(139,92,246,0.5)`. Nothing
in the physical world glows in its own brand color.
→ `0 1px 2px rgba(20,20,19,0.06)`, or a border instead.

**Floating animated blobs / aurora / particles.** Decoration that carries no
information and never stops moving.
→ Delete. Whitespace does the job better.

**Everything animates on scroll.** Every section fading and rising 40px.
→ Reserve motion for state changes. If you keep entrance animation: opacity
only, once, 200ms, and respect `prefers-reduced-motion`.

**Hover: scale(1.05) + shadow bloom.** Cards inflating under the cursor.
→ Border color shift or a 2px translate. Subtle beats springy.

---

## Typography

**Sans-serif at 800 for every heading.** Usually Inter or Poppins. Loud, not
confident.
→ Serif display at 400. The contrast between serif headline and sans body is
the fastest quality signal available.

**One typeface for everything.**
→ Three roles: display serif, body sans, mono for labels.

**Body text at 14px, line-height 1.3.** Cramped and hard to read.
→ 17px, line-height 1.6, measure ≤ 75ch.

**Centered everything.** Every heading, every paragraph, every section, at
every breakpoint. Centered text has no spine.
→ Left-align body copy. Center only short display lines, deliberately.

**No small-caps mono labels anywhere.** The missing detail that separates
editorial pages from templates.
→ Add `.label`: mono, 12px, uppercase, `+0.08em` tracking, secondary color.

---

## Layout & content

**Emoji as icons.** 🚀 for speed, ✨ for AI, 💡 for ideas, 🔥 for popular. Emoji
render differently on every platform and read as a placeholder for an icon
nobody drew.
→ A consistent line-icon set, or no icons. Most feature lists are better
without them.

**The `✨ AI-Powered` badge pill** above the headline.
→ Delete it. If the product is AI, the copy says what it does, not what it is
built from.

**Three identical feature cards.** Icon, three-word title, two lines of
filler, equal weight, equal size.
→ Give one feature real prominence with real copy. Unequal is more honest and
more readable.

**Bento grid of equal rounded boxes.** A grid with no hierarchy is a grid with
no argument.
→ Vary size by importance, or use a plain editorial stack.

**Filler copy.** "Supercharge your workflow." "Unleash the power of AI." "10x
your productivity." "Seamlessly integrate." "Take your X to the next level."
These say nothing, which is why a model reaches for them.
→ Write what the thing actually does, in specifics. "Converts a 40-page PDF to
structured JSON in about nine seconds" beats every superlative.

**Generic 3D abstract hero art.** Floating glass spheres, iridescent shapes.
→ A real screenshot, real photography, or nothing.

**Fake social proof.** Invented logos, made-up testimonials, "Trusted by
10,000+ teams" with no basis. Beyond looking cheap, it is a fabricated claim —
do not generate it.
→ Real logos with permission, or omit the section.

**Stat rows of round invented numbers.** "99.9% uptime · 10M+ users · 24/7".
→ Only real, sourced numbers. Otherwise cut the row.

---

## Quick self-check

Before calling any UI done:

1. Any gradient on the page? Justify it or remove it.
2. Any color that could be called neon? Replace it.
3. Are the headings serif? If not, is there a real reason?
4. Any emoji in the interface? Remove.
5. Is any heading weight ≥ 800? Drop to 400–600.
6. Is the ground pure white or pure black? Warm it.
7. Could you double the section padding and have it look better? Then do.
8. Read the copy aloud. Does it say anything specific? If not, rewrite before
   restyling.
9. Any invented logo, testimonial, or statistic? Remove it — that is a
   fabrication problem, not a taste problem.
10. Body ≥ 16px, contrast ≥ 4.5:1, visible focus states?
