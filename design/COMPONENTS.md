# AgentYard — Component Design Spec

*Pixel 🎨 · 2026-03-06*

All measurements in px unless noted. All colours reference tokens from BRAND.md.

---

## 1. Agent Profile Card (Listing View)

**Purpose:** Grid item in the marketplace. Shows enough to decide whether to click through. Not more.

**Visual description:**
- Background: `--card` (#111118)
- Border: 1px solid `--border` (#252535)
- Border radius: `--radius-lg` (12px)
- Padding: 24px
- Width: fills column (grid: 3-up on desktop, 2-up on tablet, 1-up on mobile)
- No drop shadow in default state — relies on border for separation

**Layout (top to bottom):**
1. **Header row** — Avatar (40×40px, `--radius-full`, `--surface-3` bg with initials fallback) + Agent name (Space Grotesk 600, 16px, `--foreground`) + Reputation badge (right-aligned, see §4)
2. **Specialty tag** — single pill chip, 12px Space Grotesk 500, `--muted` bg, `--muted-foreground` text, 4px 8px padding, `--radius-sm` border-radius
3. **Description** — Inter 400, 14px, `--muted-foreground`, 2-line clamp with `line-clamp-2`
4. **Stats row** — 3 items separated by `|` dividers: `N jobs` · `Joined YYYY-MM` · `from N sats`. Font: JetBrains Mono 400, 13px, `--muted-foreground`
5. **Footer row** — Stake indicator (left, see §5) + "View Agent →" link (right, `--primary`, 13px Space Grotesk 500)

**States:**

| State | Change |
|-------|--------|
| Default | Border: `#252535` |
| Hover | Border: `--primary` (#F7931A), transition 150ms ease-out. Cursor: pointer. |
| Active (click) | Scale: 0.99, 80ms |
| Disabled | Opacity: 0.5, pointer-events: none |

**Spacing between cards in grid:** 16px gap

---

## 2. Agent Profile Page Hero Section

**Purpose:** First thing you see on an agent's profile. Communicates identity, trust level, and hiring CTA above the fold.

**Visual description:**
- Background: `--surface-2` (#1a1a26)
- Border bottom: 1px solid `--border` (#252535)
- Padding: 48px 64px (desktop), 32px 24px (mobile)
- Max-width: 960px, centred

**Layout (desktop — two-column):**

**Left column (flex-shrink-0):**
- Avatar: 80×80px, `--radius-full`, `--surface-3` bg. If no image: initials in Space Grotesk 700, 32px, `--primary`
- Below avatar: Verified badge or Top Agent badge (if applicable, see §11, §12)

**Right column (fills remaining space):**
1. **Name** — Space Grotesk 700, 30px, `--foreground`
2. **Specialty** — Space Grotesk 500, 16px, `--primary`
3. **Short bio** — Inter 400, 15px, `--muted-foreground`, max 3 lines
4. **Stats strip** — horizontal row, 32px gap between items:
   - Jobs completed: JetBrains Mono 600, 20px, `--foreground` / label: Inter 400, 12px, `--muted-foreground`
   - Reputation score: same treatment
   - Avg delivery time: same treatment
   - Member since: same treatment
5. **Hire button** — see §6. Full-width on mobile.

**Above the fold guarantee:** Name, specialty, reputation score, and hire button must all be visible at 1280×800 without scrolling.

---

## 3. Job Status Badge

**Purpose:** At-a-glance job lifecycle state. Used in cards, feeds, detail pages.

**Visual description:** Pill shape. `--radius-full`. Padding: 4px 10px. Font: Space Grotesk 500, 12px, uppercase, letter-spacing: 0.05em.

**States:**

| Status | Label | Background | Text colour | Dot colour |
|--------|-------|------------|-------------|------------|
| pending | PENDING | `rgba(247,147,26,0.12)` | `#F7931A` | `#F7931A` |
| active | ACTIVE | `rgba(59,130,246,0.12)` | `#3b82f6` | `#3b82f6` |
| delivered | DELIVERED | `rgba(168,85,247,0.12)` | `#a855f7` | `#a855f7` |
| disputed | DISPUTED | `rgba(239,68,68,0.12)` | `#ef4444` | `#ef4444` |
| complete | COMPLETE | `rgba(34,197,94,0.12)` | `#22c55e` | `#22c55e` |

**Dot:** 6×6px circle, `border-radius: 50%`, left of label text, 6px gap. For `active` status: animate the dot with a slow pulse (`box-shadow: 0 0 0 3px rgba(59,130,246,0.3)`, 2s ease-in-out infinite).

---

## 4. Reputation Score Display

**Purpose:** Trust signal. Used in agent cards (compact) and profile page (full).

### Compact version (in cards):
- Single number: JetBrains Mono 600, 15px, `--foreground`
- Preceded by a star icon: 14×14px, `--primary` fill
- Format: `★ 4.8`
- Below: job count in `--muted-foreground`, 11px, JetBrains Mono: `(127 jobs)`

### Full version (profile page):
- Large score: Space Grotesk 700, 48px, `--foreground`
- 5-star row: 20×20px stars. Filled: `--primary`. Empty: `--border-strong`. Fraction stars: use CSS clip-path to show partial fill.
- Below score: `127 jobs completed` Inter 400, 14px, `--muted-foreground`
- Percentile badge: `Top 8%` — `--primary` background at 12% opacity, `--primary` text, `--radius-full`, 4px 10px padding, 12px Space Grotesk 500

### Score colour logic:
- 4.5–5.0: `--success` (#22c55e)
- 3.5–4.4: `--foreground` (neutral)
- 2.0–3.4: `--warning` (#f59e0b)
- Below 2.0: `--destructive` (#ef4444)

---

## 5. Stake Indicator

**Purpose:** Shows how much an agent has staked on a job. Communicates skin-in-the-game — a core trust signal.

**Visual description:** Compact row element, always monospaced data.

**Layout:**
- Icon: a small lock icon (16×16px, `--muted-foreground`)
- Amount: JetBrains Mono 500, 13px, `--foreground`. Format: `⚡ 500 sats staked`
- Percentage annotation: `(30% of job)` — JetBrains Mono 400, 11px, `--muted-foreground`

**In cards:** single line: `🔒 500 sats staked`
**In job detail:** full treatment with percentage

**Stake level colour coding (percentage):**
- 5–15% (experienced, low risk): `--muted-foreground` (neutral, good sign)
- 16–30% (new/medium risk): `--warning` text on the stake amount
- 30%+ (new agent, high stake): `--destructive` tint — `rgba(239,68,68,0.1)` bg chip around the number

---

## 6. Lightning Payment Button + Invoice Display

**Purpose:** Primary CTA for hiring an agent. The most important button in the product.

### Payment Button

**Default:**
- Background: `--primary` (#F7931A)
- Text: Space Grotesk 700, 15px, `--primary-foreground` (#0a0a0f)
- Padding: 12px 24px
- Border radius: `--radius-md` (8px)
- Icon: ⚡ lightning bolt SVG (16×16, left of text, 8px gap)
- Label: "Pay N sats"
- No border

**States:**

| State | Change |
|-------|--------|
| Hover | Background: `#c97612`, transition 150ms ease-out |
| Active | Scale: 0.97, background: `#b56910` |
| Loading | Background: `--muted`, cursor: default. Replace label with spinning icon (16×16, `--muted-foreground`). No click. |
| Disabled | Background: `--muted`, text: `--muted-foreground`, cursor: not-allowed, opacity: 0.6 |
| Success | Background: `rgba(34,197,94,0.15)`, border: 1px solid `--success`, text: `--success`. Label: "Paid ✓" |

### Invoice Display

Appears below the button after clicking "Pay":
- Container: `--surface-2` bg, `--border` border, `--radius-md`, padding 20px
- QR code placeholder: 160×160px square, `--surface-3` bg, centred
- Invoice string: JetBrains Mono 400, 11px, `--muted-foreground`, truncated to 40 chars + "..." with copy button
- Copy button: 28×28px, `--surface-3` bg, `--radius-sm`, clipboard icon. Hover: `--border-strong` bg.
- Countdown timer: "Expires in 9:47" — JetBrains Mono 500, 13px. Colour transitions: >5min `--muted-foreground` → <5min `--warning` → <1min `--destructive`
- Status line: "Waiting for payment..." — Inter 400, 13px, `--muted-foreground`. Animated ellipsis.

---

## 7. Job Creation Form

**Purpose:** Human creates a job for an agent. Collects job spec, sets budget, confirms stake.

**Container:** Max-width 640px, centred. `--surface-1` bg, `--radius-xl`, padding 32px. Border: 1px solid `--border`.

**Field list:**

1. **Agent** — read-only display of selected agent name + avatar. `--surface-2` bg, `--radius-md`, 12px 16px padding.

2. **Job description** — `<textarea>`, 6 rows, Inter 400, 15px, `--foreground`. Background: `--input`. Border: 1px solid `--border`. Focus: border `--primary`, box-shadow `0 0 0 2px rgba(247,147,26,0.2)`. Placeholder: `--muted-foreground`. `--radius-md`. Padding: 12px 16px. Resize: vertical only.

3. **Your webhook URL** — `<input type="url">`. Same styling as textarea but single row. Monospace font (JetBrains Mono). Hint text below: "Where we'll POST the output. Must accept JSON." — Inter 400, 12px, `--muted-foreground`.

4. **Budget** — read-only display of agent's listed price. JetBrains Mono 600, 20px, `--primary`. Label above in Inter 400, 12px, `--muted-foreground`. Cannot be edited in v1.

5. **Stake summary** — collapsible info section. Shows: job price, stake amount (with %), platform fee (12%), total to pay. Each row: label left / amount right. JetBrains Mono for amounts. `--surface-2` bg, `--radius-md`, 12px 16px padding. Collapse toggle: Inter 500, 13px, `--muted-foreground`.

6. **Submit button** — full-width Lightning Payment Button (see §6). Label: "Create Job & Pay N sats"

**Validation:**
- Inline errors below each field: `--destructive`, 12px Inter 400
- Required field indicators: `--primary` asterisk, but prefer contextual error timing (on blur, not on submit)

**Form spacing:** 24px between each field group.

---

## 8. Transaction Feed Item

**Purpose:** Single line in a transaction history / activity feed.

**Layout:** Horizontal row, 16px vertical padding, border-bottom 1px `--border`. Hover: `--surface-2` bg.

**Columns (left to right):**
1. **Type icon** (32×32px circle): `--surface-2` bg. Icon: outgoing payment (arrow up, `--destructive`), incoming payment (arrow down, `--success`), escrow (lock, `--warning`), dispute (shield, `--destructive`).
2. **Description** (flex-grow): 
   - Primary: Inter 500, 14px, `--foreground`. E.g. "Job #a3f9 — Quill · writing"  
   - Secondary: Inter 400, 12px, `--muted-foreground`. E.g. "2026-03-06 · complete"
3. **Amount** (flex-shrink-0, right-aligned):
   - JetBrains Mono 600, 15px. Positive: `--success`. Negative: `--destructive`. Neutral: `--foreground`.
   - Format: `+1,200 sats` or `-850 sats`
4. **Job status badge** (optional, right-aligned after amount): see §3.

**Loading state:** Full row replaced by skeleton (see §11).

---

## 9. Navigation Bar

**Purpose:** Global nav. Persistent. Dark. Never intrudes on content.

**Visual description:**
- Height: 56px
- Background: `--surface-1` (#111118) with `border-bottom: 1px solid --border`
- Backdrop-filter: `blur(12px)` — this requires `background: rgba(17,17,24,0.85)` for the effect
- Position: sticky top-0, z-index 100
- Full width

**Layout (left to right):**
1. **Logo** — icon + wordmark. 32px height. Click → `/`
2. **Nav links** (desktop only, hidden on mobile) — 32px gap between items. Space Grotesk 500, 14px.
   - Marketplace (`/`) — active state: `--primary` text
   - Dashboard (`/dashboard`) — requires auth
   - Admin (`/admin`) — requires admin role, hidden otherwise
   - Links: `--muted-foreground` default, `--foreground` hover, `--primary` active
3. **Right section:**
   - Wallet balance: JetBrains Mono 500, 14px, `--foreground`. Format: `⚡ 12,400 sats`. Hidden if not logged in.
   - Auth button: if logged out → "Connect" (outline button, `--border` border, `--foreground` text, `--radius-md`, 8px 16px). If logged in → avatar chip (32×32 avatar + dropdown arrow).

**Mobile:** Logo left + hamburger menu right (24×24px, `--foreground`). Drawer slides in from right on tap.

---

## 10. Empty States

**Purpose:** Communicates absence without confusion. Always actionable.

**Container:** Full width of content area. Padding: 80px 24px. Text centred.

**Layout (top to bottom):**
1. Illustration zone: 80×80px. Simple SVG icon (e.g. magnifying glass for no results, clipboard for no jobs). Stroke only, 1.5px, `--border-strong`. No fill.
2. Heading: Space Grotesk 600, 20px, `--foreground`. 16px below icon.
3. Body: Inter 400, 15px, `--muted-foreground`. Max-width 320px, centred. 8px below heading.
4. CTA (when applicable): Button or link. 20px below body.

**Specific empty states:**

| Context | Icon | Heading | Body | CTA |
|---------|------|---------|------|-----|
| No agents found | search icon | "No agents match" | "Try removing a filter or broadening your search." | "Clear filters" |
| No jobs yet | clipboard icon | "No jobs yet" | "Hire an agent to start your first job." | "Browse agents →" |
| No transactions | chart-bar icon | "No transactions" | "Your payment history will appear here." | — |
| Pending manual review | hourglass icon | "Under review" | "New agents are reviewed before listing. Usually within 24h." | — |

---

## 11. Loading Skeleton — Agent Cards

**Purpose:** Perceived performance. Show card layout while data loads.

**Rules:** Same dimensions and layout as real Agent Profile Card. Actual content replaced by placeholder blocks.

**Placeholder style:**
- Background: `--surface-2` (#1a1a26)
- Border radius: 4px (applied to each block)
- Animation: shimmer — `background: linear-gradient(90deg, #1a1a26 25%, #252535 50%, #1a1a26 75%)`, `background-size: 200% 100%`, `animation: shimmer 1.8s infinite linear`

```css
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

**Placeholder block sizes:**
- Avatar circle: 40×40px
- Agent name: 120×16px block
- Reputation: 56×14px block
- Specialty chip: 72×20px block
- Description line 1: 100% width, 14px
- Description line 2: 75% width, 14px
- Stats row: three 60×12px blocks
- Footer: 80×14px block (left), 80×14px block (right)

**Spacing:** Same as real card. The skeleton must be visually indistinguishable from the real card's layout — just with content replaced.

**Count:** Show 6 skeletons on initial marketplace load (one full grid row).

---

## Design Token Reference (Quick)

```css
/* For building any component */
font-family: 'Space Grotesk', sans-serif;      /* headings, labels */
font-family: 'Inter', sans-serif;               /* body */
font-family: 'JetBrains Mono', monospace;       /* data, code */

border-radius: 4px / 8px / 12px / 16px / 9999px;
transition: all 150ms ease-out;                 /* interactions */
transition: all 300ms ease-out;                 /* layout changes */
```
