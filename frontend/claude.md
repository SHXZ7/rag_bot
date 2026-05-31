# CLAUDE.md — Creator Lens Frontend Design Spec

> This file governs every UI decision in this project.
> Any AI or developer touching the frontend must read this first.
> Do not deviate from these rules. Do not default to "safe" choices.

---

## Project Identity

**Creator Lens** is a RAG-powered video analytics tool for content creators.
It ingests two social videos, computes engagement data, and lets creators have
a conversation with their content — asking why one video outperformed another,
comparing hooks, getting improvement suggestions.

The aesthetic direction: **Dark editorial. Data-forward. Feels like a Bloomberg
terminal met a creative studio.**

Not a SaaS dashboard. Not a startup landing page. Not another shadcn/Tailwind
cookie-cutter. This is a tool for creators who take their craft seriously.

---

## Aesthetic Direction

### The Vibe
- Think: A24 meets data journalism. Serious, precise, a little cinematic.
- Dark backgrounds. High contrast type. Deliberate use of colour as signal.
- Feels hand-built, not auto-generated.
- Every element has a reason to exist. Nothing decorative without purpose.

### What It Should NOT Look Like
- No purple gradients on white
- No rounded-everything cards with drop shadows
- No Inter/Roboto/system-ui anywhere
- No glowing neon "glassmorphism" effects
- No generic hero sections with a gradient blob
- No "✨ AI-powered" badge styling
- No blue primary buttons with border-radius: 8px

---

## Colour System

```css
:root {
  /* Backgrounds — layered depth */
  --bg-base:       #0A0A0A;   /* true near-black canvas */
  --bg-surface:    #111111;   /* cards, panels */
  --bg-elevated:   #1A1A1A;   /* hover states, inputs */
  --bg-overlay:    #222222;   /* tooltips, dropdowns */

  /* Borders — barely there but structural */
  --border-subtle:  #1F1F1F;
  --border-default: #2A2A2A;
  --border-strong:  #3A3A3A;

  /* Text — strict hierarchy */
  --text-primary:   #F0EDE6;   /* warm off-white, not pure white */
  --text-secondary: #8A8680;   /* muted, for labels */
  --text-tertiary:  #4A4845;   /* very muted, for timestamps */
  --text-inverse:   #0A0A0A;

  /* Accent — ONE dominant colour, used sparingly */
  --accent:         #D4FF00;   /* electric lime — the signal colour */
  --accent-dim:     #9AB800;   /* hover/pressed state */
  --accent-glow:    rgba(212, 255, 0, 0.08);  /* subtle bg tint */

  /* Semantic colours — data signals only */
  --signal-up:    #4ADE80;   /* positive engagement, good metrics */
  --signal-down:  #F87171;   /* lower metric */
  --signal-mid:   #FBBF24;   /* neutral / comparable */

  /* Video A vs B identity */
  --video-a:      #60A5FA;   /* cool blue for Video A */
  --video-b:      #F472B6;   /* warm pink for Video B */
}
```

### Colour Rules
1. `--accent` (#D4FF00) is used for ONE thing at a time — the primary CTA,
   or the active state. Never as decoration.
2. Text is always `--text-primary` or `--text-secondary`. Never pure #FFFFFF.
3. Video A is always blue (`--video-a`). Video B is always pink (`--video-b`).
   These colours are consistent EVERYWHERE — badges, chart lines, citations.
4. Backgrounds never go lighter than `--bg-overlay` (#222222) in normal use.
5. No box-shadow with colour. Depth is created through layered backgrounds only.

---

## Typography

```css
/* Import in globals.css */
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Syne:wght@400;600;700;800&family=Instrument+Serif:ital@0;1&display=swap');
```

| Role | Font | Weight | Usage |
|------|------|--------|-------|
| Display / Headlines | `Syne` | 700–800 | Page titles, section headers |
| Body / UI | `DM Mono` | 400–500 | All body text, labels, inputs |
| Accent / Italic | `Instrument Serif` italic | 400 | Pull quotes, video titles, names |
| Data / Numbers | `DM Mono` | 500 | All numbers, percentages, stats |

### Typography Rules
- Headlines are `Syne`. Nothing else goes that large.
- ALL body text, labels, inputs, buttons, metadata — `DM Mono`.
  This gives the UI a consistent terminal/editorial feel.
- Numbers (engagement rate, views, likes) are always `DM Mono` with
  `font-variant-numeric: tabular-nums` so they don't shift width.
- Video titles use `Instrument Serif italic` — a small humanising moment
  in an otherwise technical interface.
- Letter-spacing: display text gets `letter-spacing: -0.02em`.
  Body mono text gets `letter-spacing: 0.01em`.
- Line heights: 1.2 for display, 1.6 for body.

---

## Layout

### Grid
```
Full page = 12-column grid with 24px gutters.
Max content width: 1400px. Centred.

Desktop:
  Left panel (video cards + metadata): 5 cols
  Right panel (chat): 7 cols
  Gap: 2px — panels nearly touch, separated by a 1px border

Mobile (< 768px):
  Stack vertically. Video cards first. Chat below.
```

### Spacing Scale
Use multiples of 4px. Never arbitrary values.
```
4px   — tight internal padding
8px   — between related elements
12px  — inside compact components
16px  — default internal padding
24px  — between distinct sections
32px  — major section gaps
48px  — page-level breathing room
```

### Panel Design
- Panels have NO border-radius. Sharp corners everywhere.
  Radius = 0px. This is intentional and differentiating.
- Panel borders are `1px solid var(--border-default)`.
- No box shadows. Use background layering for depth.
- Panels feel like physical surfaces, not floating cards.

---

## Component Patterns

### Buttons
```
Primary CTA (Analyse / Submit):
  background: var(--accent)
  color: var(--text-inverse)
  font: DM Mono 500 13px
  padding: 10px 20px
  border-radius: 0
  border: none
  text-transform: uppercase
  letter-spacing: 0.08em
  transition: background 150ms

  Hover: background: var(--accent-dim)
  No box-shadow. No glow.

Secondary / Ghost:
  background: transparent
  color: var(--text-secondary)
  border: 1px solid var(--border-default)
  Same sizing as primary.

  Hover: border-color: var(--border-strong), color: var(--text-primary)
```

### Input Fields
```
background: var(--bg-elevated)
border: 1px solid var(--border-default)
border-radius: 0
color: var(--text-primary)
font: DM Mono 400 13px
padding: 10px 12px

Focus: border-color: var(--accent), outline: none
Placeholder: var(--text-tertiary)

NEVER: rounded corners, box-shadow on focus, floating labels
```

### Video A / B Badges
```
Inline pill showing which video a citation comes from.
Video A: background: rgba(96, 165, 250, 0.12), color: var(--video-a), border: 1px solid rgba(96, 165, 250, 0.3)
Video B: background: rgba(244, 114, 182, 0.12), color: var(--video-b), border: 1px solid rgba(244, 114, 182, 0.3)
font: DM Mono 500 11px
padding: 2px 8px
border-radius: 0
text: "A" or "B" only — never the full video title inline
```

### Metric Cards (views, likes, engagement rate)
```
No card borders. Just a label + value stacked.
Label: DM Mono 400 11px, --text-tertiary, uppercase, letter-spacing 0.1em
Value: DM Mono 500 24px, --text-primary, tabular-nums
Unit: DM Mono 400 13px, --text-secondary (e.g. "%" or "views")

Engagement rate gets --accent colour on the value when it's the winner.
```

### Citation Tooltip
```
When user hovers a [A] or [B] badge in chat:
  Show tooltip with the actual chunk text (max 3 lines, truncated)
  background: var(--bg-overlay)
  border: 1px solid var(--border-strong)
  border-radius: 0
  font: DM Mono 400 12px
  max-width: 320px
  padding: 10px 12px
  No arrow. Just positioned above.
```

### Chat Messages
```
User messages:
  No bubble. Right-aligned text.
  font: DM Mono 400 14px, --text-secondary
  padding-left: 20% (pushes text right)

Assistant messages:
  No bubble. Left-aligned.
  font: DM Mono 400 14px, --text-primary
  Citations as inline [A] [B] badges after relevant sentences.
  Streaming cursor: blinking 2px block (not a pipe |)

Message separator: nothing. Just 24px vertical gap.
NEVER: chat bubbles with border-radius, avatar icons, timestamp on every message
```

---

## Motion & Interaction

### Principles
- Transitions are 150ms ease for state changes (hover, focus).
- Page-level animations are 400–600ms with staggered delays.
- Nothing bounces. Nothing springs. Everything is linear or ease.

### Specific Animations
```
Page load:
  URL input section fades up (opacity 0→1, translateY 12px→0) at 0ms
  Video cards fade up at 100ms delay
  Chat panel fades up at 200ms delay

Ingest loading:
  A horizontal progress bar using --accent colour.
  Indeterminate animation (sliding highlight).
  NOT a spinner. NOT a skeleton loader with shimmer.

Streaming text:
  Tokens appear one by one. No animation on each token.
  Just a blinking block cursor at the end while streaming.

Citation hover:
  Tooltip appears at 100ms delay (prevents flicker on pass-through).
  opacity 0→1, 150ms ease. No scale transform.
```

---

## What Makes This Unforgettable

1. **The colour identity system** — Video A is always blue, Video B always pink.
   These colours echo through EVERYTHING: the video card border, the engagement
   bar, every citation badge. The user learns the language in 10 seconds.

2. **Zero border-radius** — every edge is sharp. In a world of rounded cards,
   this feels architectural, intentional, different.

3. **DM Mono everywhere** — body text in a monospace font gives the whole UI
   a data-terminal personality. Not aggressive like a hacker aesthetic — just
   precise and editorial.

4. **The accent is electric lime** (#D4FF00) — not blue, not purple, not teal.
   Used only for the primary action and the winning metric. Feels like a
   highlight marker on a dark page.

5. **No bubbles in chat** — text floats directly on the panel. Citations are
   inline. The conversation reads like an article, not a messaging app.

---

## File Structure

```
frontend/
├── app/
│   ├── globals.css       ← all CSS variables + base resets live here
│   ├── layout.tsx        ← font imports, metadata
│   └── page.tsx          ← root layout (URL input → then split view)
├── components/
│   ├── video/
│   │   ├── VideoCard.tsx
│   │   ├── MetricRow.tsx
│   │   └── EngagementBar.tsx
│   ├── chat/
│   │   ├── ChatPanel.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── CitationBadge.tsx
│   │   └── StreamingCursor.tsx
│   └── shared/
│       ├── UrlInputForm.tsx
│       └── IngestProgress.tsx
├── hooks/
│   ├── useChat.ts
│   └── useIngest.ts
├── lib/
│   ├── api.ts
│   └── types.ts
└── store/
    ├── videoStore.ts
    └── chatStore.ts
```

---

## globals.css — Required Base Reset

```css
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  background: var(--bg-base);
  color: var(--text-primary);
  font-family: 'DM Mono', monospace;
  font-size: 14px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Remove all default browser styling from inputs and buttons */
input, textarea, button, select {
  font-family: inherit;
  font-size: inherit;
  background: none;
  border: none;
  outline: none;
  appearance: none;
}

/* Scrollbars — thin, dark */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-strong); }
::-webkit-scrollbar-thumb:hover { background: var(--text-tertiary); }

/* Selection */
::selection {
  background: var(--accent-glow);
  color: var(--accent);
}
```

---

## Tailwind Config Rules

```js
// tailwind.config.ts
// Map every CSS variable to a Tailwind token.
// NEVER use default Tailwind colours (blue-500, purple-400 etc) directly.
// Always use the semantic tokens below.

theme: {
  extend: {
    colors: {
      'bg-base':      'var(--bg-base)',
      'bg-surface':   'var(--bg-surface)',
      'bg-elevated':  'var(--bg-elevated)',
      'text-primary': 'var(--text-primary)',
      'text-secondary':'var(--text-secondary)',
      'text-tertiary':'var(--text-tertiary)',
      'accent':       'var(--accent)',
      'accent-dim':   'var(--accent-dim)',
      'video-a':      'var(--video-a)',
      'video-b':      'var(--video-b)',
      'border-subtle':'var(--border-subtle)',
      'border-default':'var(--border-default)',
      'signal-up':    'var(--signal-up)',
      'signal-down':  'var(--signal-down)',
    },
    fontFamily: {
      mono:    ['DM Mono', 'monospace'],
      display: ['Syne', 'sans-serif'],
      serif:   ['Instrument Serif', 'serif'],
    },
    borderRadius: {
      DEFAULT: '0px',   // Force zero radius everywhere
      none:    '0px',
    },
  }
}
```

---

## Do / Don't Quick Reference

| ✅ Do | ❌ Don't |
|-------|---------|
| Sharp corners (0px radius) everywhere | Rounded cards, inputs, buttons |
| DM Mono for all body text | Inter, Roboto, system-ui |
| #D4FF00 accent sparingly | Multiple accent colours |
| Blue for Video A, Pink for Video B | Swapping or mixing these |
| Flat backgrounds, no shadows | box-shadow with colour |
| Inline citations in chat text | Separate citation section below answer |
| Indeterminate progress bar for loading | Spinners, skeleton shimmer |
| 150ms transitions max | Spring animations, bounces |
| Warm off-white (#F0EDE6) text | Pure #FFFFFF text |
| Syne only for page-level headlines | Syne for body text |