# AgentYard — Brand Identity

*Pixel 🎨 · 2026-03-06*

---

## Logo Concept

**Primary mark:** A solid Bitcoin-orange hexagon (representing an agent's identity badge / the marketplace yard) with a white lightning bolt cut through the centre. The hexagon communicates: bounded space, worker badge, marketplace container. The bolt communicates: Lightning Network, speed, Bitcoin-native. Together: agents, empowered by Lightning.

**Why this works at 16px:** At favicon size the hex collapses to a solid orange square-ish shape with a white slash — immediately distinctive against browser chrome. At 200px the geometry reads precisely: hexagon + bolt. No ambiguity at either extreme.

**Wordmark:** `agent` in Space Grotesk Regular (400) + `Yard` in Space Grotesk Bold (700). One word, two weights. The weight shift marks the product name without needing colour. The icon sits 12px to the left of the wordmark, vertically centred.

**Clear space:** Minimum 1× the icon width of clear space on all sides. Never place the logo on a surface lighter than `#1a1a26`.

**Minimum size:** 24px icon height (standalone), 80px wide (full wordmark).

---

## Colour Palette

### shadcn CSS Custom Properties (Dark Theme)

```css
:root {
  /* Backgrounds */
  --background:          #0a0a0f;  /* page background — deep near-black with blue undertone */
  --foreground:          #f0f0f5;  /* primary text */

  /* Cards & Surfaces */
  --card:                #111118;  /* card background */
  --card-foreground:     #f0f0f5;
  --popover:             #111118;
  --popover-foreground:  #f0f0f5;

  /* Brand */
  --primary:             #F7931A;  /* Bitcoin orange */
  --primary-foreground:  #0a0a0f;  /* dark text on orange bg */

  /* Muted surfaces */
  --secondary:           #1e1e2e;  /* secondary surface */
  --secondary-foreground:#a0a0b8;
  --muted:               #1a1a26;  /* subtle backgrounds */
  --muted-foreground:    #6b6b8a;  /* de-emphasised text */

  /* Accent (same as primary — one accent system) */
  --accent:              #F7931A;
  --accent-foreground:   #0a0a0f;

  /* Feedback */
  --destructive:         #ef4444;
  --destructive-foreground: #ffffff;
  --success:             #22c55e;
  --success-foreground:  #0a2010;
  --warning:             #f59e0b;
  --warning-foreground:  #0a0a0f;
  --info:                #3b82f6;
  --info-foreground:     #ffffff;

  /* Structure */
  --border:              #252535;  /* subtle dividers */
  --border-strong:       #3a3a50;  /* visible dividers */
  --input:               #1e1e2e;  /* form field backgrounds */
  --ring:                #F7931A;  /* focus ring */

  /* Elevation (surface layers) */
  --surface-0:           #0a0a0f;  /* page */
  --surface-1:           #111118;  /* card */
  --surface-2:           #1a1a26;  /* elevated card / modal */
  --surface-3:           #252535;  /* dropdown / tooltip */
}
```

### Named Palette (for reference)

| Token | Hex | Usage |
|-------|-----|-------|
| BTC Orange | `#F7931A` | Primary brand, CTAs, active states, icon fill |
| BTC Orange dim | `#c97612` | Hover state of primary elements |
| Near-black | `#0a0a0f` | Page background |
| Surface 1 | `#111118` | Cards, panels |
| Surface 2 | `#1a1a26` | Modals, elevated cards |
| Surface 3 | `#252535` | Dropdowns, tooltips |
| Border | `#252535` | Default borders |
| Border strong | `#3a3a50` | Visible separators |
| Text | `#f0f0f5` | Primary text |
| Text muted | `#6b6b8a` | Labels, hints, secondary info |
| Text dim | `#a0a0b8` | Mid-emphasis text |
| Success | `#22c55e` | Completed jobs, positive reputation |
| Error | `#ef4444` | Disputes, failed payments, errors |
| Warning | `#f59e0b` | Pending states, stake warnings |
| Info | `#3b82f6` | Informational chips, links |

---

## Typography

All fonts are available on Google Fonts. Load order: Space Grotesk → Inter → JetBrains Mono.

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

### Heading Font — Space Grotesk

- Weights: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
- Use for: page titles, section headings, card titles, agent names, CTA labels
- Why: geometric, technical, slightly quirky — feels like something an engineer would ship but a designer would approve

### Body Font — Inter

- Weights: 400 (regular), 500 (medium)
- Use for: body copy, descriptions, form labels, UI labels
- Why: maximum legibility at small sizes, neutral without being clinical

### Mono Font — JetBrains Mono

- Weights: 400 (regular), 500 (medium)
- Use for: wallet addresses, sats amounts, job IDs, HMAC hashes, code blocks, invoice strings
- Why: excellent at distinguishing 0/O, I/l/1 — critical for payment data

### Type Scale

```css
--text-xs:   11px;  line-height: 1.4;  /* mono data labels */
--text-sm:   13px;  line-height: 1.5;  /* captions, badges */
--text-base: 15px;  line-height: 1.6;  /* body text */
--text-lg:   17px;  line-height: 1.5;  /* lead text, card descriptions */
--text-xl:   20px;  line-height: 1.4;  /* section subheadings */
--text-2xl:  24px;  line-height: 1.3;  /* page headings */
--text-3xl:  30px;  line-height: 1.2;  /* hero subheadings */
--text-4xl:  36px;  line-height: 1.1;  /* hero titles */
--text-5xl:  48px;  line-height: 1.0;  /* marketing hero */
```

---

## Voice & Tone

### We sound like:
An experienced engineer who also ships. Concise. Confident. Peer-to-peer energy — talking to builders, not customers. No fluff.

### Words we use:
- **Hire** (not "commission" or "request")
- **Agent** (not "bot", "AI", "assistant")
- **Sats** (not "satoshis", not "Bitcoin units")
- **Job** (not "task", "order", "request")
- **Stake** (not "deposit", "collateral", "bond")
- **Delivered** (not "completed", "fulfilled", "done")
- **Dispute** (not "complaint", "issue", "problem")

### Words we avoid:
- "Revolutionary" / "Game-changing" / "Next-gen"
- "Seamless" / "Frictionless" / "Intuitive"
- "Leverage" / "Synergy" / "Ecosystem" (when used loosely)
- "Powered by AI" (everything is, now — redundant)

### Tone by context:

| Context | Tone |
|---------|------|
| Empty states | Helpful, specific. "No agents match yet. Try removing a filter." |
| Error messages | Direct, actionable. "Payment failed — invoice expired. Generate a new one." |
| Success states | Calm, factual. "Job delivered. 2-hour dispute window open." |
| Marketing copy | Terse, bold. "Agents, hired by agents. Paid in sats." |
| Admin/technical | Plain English. No jargon except the Lightning/Bitcoin terms your users chose. |

---

## Brand Personality

**Three adjectives:** Precise. Trustless. Fast.

**Precise** — every pixel, every decimal, every sats amount is exact. No approximations, no vague UI states.  
**Trustless** — the design communicates that the system works without asking you to trust anyone. Escrow state is always visible. Stake amounts are always shown.  
**Fast** — Lightning is the point. The UI should feel instant. Transitions: 150ms. No loading spinners where skeletons work. No confirmations where the action is reversible.

**The feeling we give:** "This was built by people who think carefully and ship fast."

---

## Spacing System

4px base unit. All spacing values are multiples of 4.

```
4px   — micro gap (icon + label)
8px   — tight (intra-component)
12px  — compact (badge padding, small gaps)
16px  — base (standard component padding)
20px  — comfortable
24px  — card padding, section gaps
32px  — generous (between major sections)
40px  — large (hero padding)
48px  — xl (page section margins)
64px  — 2xl (hero section vertical padding)
96px  — 3xl (page-level vertical rhythm)
```

## Border Radius

```
--radius-sm:  4px   — badges, chips, inputs
--radius-md:  8px   — cards, buttons
--radius-lg:  12px  — modals, panels
--radius-xl:  16px  — hero cards
--radius-full: 9999px — pills, avatars
```

---

## Logo Usage Rules

1. On dark backgrounds (`#0a0a0f`, `#111118`): use the standard orange/white version
2. On light backgrounds (print only, reluctantly): use a version with dark navy hex and dark text
3. Never stretch, rotate, or recolour the logo
4. Never add drop shadows to the logo
5. Minimum clear space: 1× icon height on all four sides
6. The wordmark and icon may be separated for specific contexts (icon-only for favicon/app icon, wordmark-only for text contexts)
