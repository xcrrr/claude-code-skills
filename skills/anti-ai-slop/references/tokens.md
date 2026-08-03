# Tokens

Copy-paste starting points. Change the accent to fit the brand; keep the
structure.

## Palettes

### Warm paper (default — editorial, safe, works for almost anything)

| Role | Hex |
|---|---|
| Page ground | `#FAF9F5` |
| Raised surface | `#F0EEE6` |
| Sunken / inset | `#EBE9E1` |
| Hairline border | `#DDDAD0` |
| Text primary | `#141413` |
| Text secondary | `#6B6A63` |
| Text muted | `#8F8E86` |
| Accent (clay) | `#C4622D` |
| Accent hover | `#A64F22` |

### Cool paper (a colder, more architectural variant)

Ground `#F8F8F6` · surface `#EFEFEC` · border `#DCDCD6` · text `#17181A` ·
secondary `#65686B` · accent (deep teal) `#1F4D4A`.

### Warm dark (never a blue-black "space" background)

Ground `#1A1A18` · surface `#242422` · border `#33332F` · text `#EDEBE4` ·
secondary `#A3A199` · accent `#D97757` (accents lighten in dark mode).

### Accent options

Clay `#C4622D` · terracotta `#D97757` · rust `#9C4221` · ochre `#B8873A` ·
moss `#5A6B4F` · forest `#2F4A38` · deep teal `#1F4D4A` · oxblood `#6E2639` ·
ink blue `#2A3F5F`.

**Banned:** `#8B5CF6`, `#6366F1`, `#A855F7`, `#EC4899`, `#06B6D4`, `#22D3EE`,
`#84CC16`, and every neon relative. Any two-stop gradient between them.

## Type

```css
--font-display: 'Tiempos Headline', 'Canela', 'Freight Display',
                'Playfair Display', Georgia, 'Times New Roman', serif;
--font-body:    'Inter', 'Söhne', -apple-system, BlinkMacSystemFont,
                'Helvetica Neue', Arial, sans-serif;
--font-mono:    'JetBrains Mono', 'IBM Plex Mono', ui-monospace,
                SFMono-Regular, Menlo, monospace;
```

Free serif display faces that don't look like defaults: **Fraunces**,
**Instrument Serif**, **Newsreader**, **Source Serif 4**, **Libre Caslon
Display**, **EB Garamond**. Avoid Playfair Display if you want to avoid the
"template" read — it is heavily overused.

### Scale (1.25 major third, rounded)

| Token | Size | Line-height | Tracking | Face |
|---|---|---|---|---|
| `display` | 4.0rem | 1.05 | −0.03em | display serif |
| `h1` | 3.0rem | 1.1 | −0.02em | display serif |
| `h2` | 2.25rem | 1.15 | −0.02em | display serif |
| `h3` | 1.5rem | 1.25 | −0.01em | display serif |
| `body-lg` | 1.1875rem | 1.6 | 0 | sans |
| `body` | 1.0625rem | 1.6 | 0 | sans |
| `small` | 0.9375rem | 1.5 | 0 | sans |
| `label` | 0.75rem | 1.4 | **+0.08em**, uppercase | mono |

Clamp display sizes for fluid type:
`font-size: clamp(2.5rem, 1.5rem + 4vw, 4rem);`

Weights: 300 and 400 carry the page. 500/600 for emphasis. 700 rarely. Never
800/900.

## Spacing

`4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96 · 128 · 160` (px). Never freehand.

Section padding: `96px` mobile → `160px` desktop. Content measure: `65–75ch`.
Container max-width `1200px` with `24px` (mobile) / `48px` (desktop) gutters.

## Radius, borders, shadows

```css
--radius-sm: 4px;
--radius:    8px;
--radius-lg: 16px;
--radius-pill: 999px;

--border: 1px solid #DDDAD0;

--shadow-sm: 0 1px 2px rgba(20, 20, 19, 0.06);
--shadow:    0 2px 8px rgba(20, 20, 19, 0.08);
```

That is the entire shadow system. There is no `--shadow-xl`, and no shadow
carries the accent hue. Prefer the hairline border over any shadow.

## Starter block

```css
:root {
  --ground: #FAF9F5;
  --surface: #F0EEE6;
  --border-color: #DDDAD0;
  --text: #141413;
  --text-secondary: #6B6A63;
  --accent: #C4622D;
  --accent-hover: #A64F22;

  --font-display: 'Fraunces', Georgia, serif;
  --font-body: 'Inter', -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;

  --radius: 8px;
  --measure: 68ch;
}

@media (prefers-color-scheme: dark) {
  :root {
    --ground: #1A1A18;
    --surface: #242422;
    --border-color: #33332F;
    --text: #EDEBE4;
    --text-secondary: #A3A199;
    --accent: #D97757;
  }
}

body {
  background: var(--ground);
  color: var(--text);
  font-family: var(--font-body);
  font-size: 1.0625rem;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

h1, h2, h3 {
  font-family: var(--font-display);
  font-weight: 400;
  letter-spacing: -0.02em;
  line-height: 1.1;
}

.label {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-secondary);
}
```

## Buttons

Primary: solid accent, cream text, `--radius` or pill, `12px 24px` padding,
weight 500. Hover darkens the fill — it does not glow, lift, or scale.

Secondary: transparent with a hairline border, text in `--text`. Hover fills
with `--surface`.

Tertiary: text only with a 1px underline offset `0.2em`.

No gradient fills. No `transform: scale()` on hover. No shadow bloom.

## Tailwind equivalent

```js
theme: {
  extend: {
    colors: {
      ground: '#FAF9F5', surface: '#F0EEE6',
      ink: '#141413', muted: '#6B6A63', accent: '#C4622D',
    },
    fontFamily: {
      display: ['Fraunces', 'Georgia', 'serif'],
      sans: ['Inter', 'sans-serif'],
      mono: ['JetBrains Mono', 'monospace'],
    },
    borderRadius: { DEFAULT: '8px', lg: '16px' },
  },
}
```

Then never reach for `bg-gradient-to-r`, `from-purple-500`, `backdrop-blur`,
`shadow-2xl`, `drop-shadow-glow`, or `font-black`.
