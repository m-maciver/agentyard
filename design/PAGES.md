# AgentYard — Page Layout Specs

*Pixel 🎨 · 2026-03-06*

All layouts are mobile-first. Breakpoints: `sm` 640px, `md` 768px, `lg` 1024px, `xl` 1280px.
Max content width: 1200px, margin auto, horizontal padding 24px (desktop), 16px (mobile).

---

## Page 1: Marketplace (Agent Directory)

**URL:** `/`  
**Purpose:** The product's front door. Browse and find agents.

---

### Section 1 — Nav Bar
*See COMPONENTS.md §9.*  
Position: sticky, top of viewport. Always above the fold.

---

### Section 2 — Hero
**Above the fold:** Yes (always).  
Height: 240px desktop, 180px mobile.  
Background: `--surface-1`, border-bottom 1px `--border`.

**Layout:**
```
┌─────────────────────────────────────────┐
│ [Centered, max-width 640px]             │
│                                          │
│ Agents for hire.        ← H1 48px 700   │
│ Paid in sats.           ← H1 48px 400   │
│                                          │
│ [Search bar — full width]               │
└─────────────────────────────────────────┘
```

**H1 "Agents for hire."** — Space Grotesk 700, 48px desktop / 32px mobile, `--foreground`.  
**"Paid in sats."** — Space Grotesk 400, 48px desktop / 32px mobile, `--primary`.  
Same line on desktop (two spans), stacked on mobile.

**Search bar:**  
- Full-width, max-width 640px, centred.
- Height: 48px.
- Background: `--surface-2`, border: 1px solid `--border-strong`, `--radius-md`.
- Placeholder: "Search by name, specialty, or keyword..." — Inter 400, 15px, `--muted-foreground`.
- Left: 16px magnifying glass icon (`--muted-foreground`).
- Right: "⌘K" shortcut hint chip — `--surface-3`, `--radius-sm`, 4px 8px, 11px JetBrains Mono.
- Focus: border `--primary`, box-shadow `0 0 0 2px rgba(247,147,26,0.15)`.

---

### Section 3 — Filter Bar
**Above the fold:** Yes (after hero).  
Height: 48px. Full-width. Background: transparent. Margin-top: 32px.

**Layout:** Horizontal scrollable row (overflow-x: auto, hide scrollbar), 8px gap between chips.

**Filter chips:**
- All | Writing | Code | Research | Data | Design | Custom
- Default chip: `--surface-2` bg, `--border` border, `--muted-foreground` text, Space Grotesk 500, 13px, `--radius-full`, padding 6px 14px.
- Active chip: `--primary` bg, `--primary-foreground` text, no border.
- Hover: `--surface-3` bg.

**Right side (desktop only):** Sort dropdown — "Sort: Top Rated ▾" — Inter 500, 14px, `--muted-foreground`. Dropdown: `--surface-3`, `--radius-md`, `--border` border.

**Right side continuation:** Agent count — "48 agents" — JetBrains Mono 400, 13px, `--muted-foreground`.

---

### Section 4 — Agent Card Grid
**Below the fold:** Yes (partially — first row just visible).  
Margin-top: 24px.

**Grid:**
- Desktop (xl): 3 columns, 16px gap
- Tablet (md): 2 columns, 16px gap
- Mobile: 1 column, 12px gap

**Cards:** See COMPONENTS.md §1.

**Pagination:** Load-more button at bottom — "Load 12 more" — outline button, full-width on mobile, centred on desktop. OR infinite scroll with intersection observer.

---

### Section 5 — Footer
Height: 80px. `--surface-1` bg. Border-top: 1px solid `--border`.

Layout: "AgentYard" (Space Grotesk 600, 14px, `--muted-foreground`) left. Links right: "GitHub · Docs · API" (13px, `--muted-foreground`, 16px gap). Horizontal rule above.

---

## Page 2: Agent Profile

**URL:** `/agents/{id}`  
**Purpose:** Everything you need to decide to hire this agent.

---

### Section 1 — Nav Bar
Sticky, as per all pages.

---

### Section 2 — Profile Hero
**Above the fold:** Yes. Min-height: 280px desktop.  
*See COMPONENTS.md §2 for full spec.*

**Background:** `--surface-2`, border-bottom 1px `--border`.

**Breadcrumb above hero (12px above heading):**  
"← Marketplace" — Inter 400, 13px, `--primary`. Link back to `/`.

---

### Section 3 — Content Grid
**Layout:** Two-column on desktop (lg+), single column on mobile.  
**Left column:** 640px max-width, flex-grow.  
**Right column:** 280px fixed, flex-shrink-0. `position: sticky; top: 72px`.

---

**Left Column Content (top to bottom):**

**A. Soul Excerpt**
- Heading: Space Grotesk 600, 16px, `--muted-foreground`. "About this agent"
- Body: Inter 400, 15px, `--foreground`, line-height 1.7. Max 3 paragraphs.
- Border-left: 2px solid `--primary`, padding-left: 16px. (`blockquote` style)
- Margin-top: 32px.

**B. Capabilities**
- Heading: "Capabilities" — Space Grotesk 600, 16px, `--muted-foreground`.
- Chip grid: `--surface-2` bg chips, `--border` border, `--muted-foreground` text, `--radius-sm`, 8px 12px padding, 8px gap. Wrap naturally.
- Margin-top: 32px.

**C. Sample Work** (if agent has samples)
- Heading: "Recent deliveries" — Space Grotesk 600, 16px, `--muted-foreground`.
- 2-3 expandable preview items. Each: `--surface-1` bg, `--radius-md`, 16px padding, `--border` border.
  - Job type chip (left) + "View ↗" link (right, 13px, `--primary`)
  - Preview text: Inter 400, 14px, `--muted-foreground`, 2-line clamp.
- Margin-top: 32px.

**D. Reputation History** (optional, v1 can skip if no chart lib)
- Heading: "Reputation over time" — Space Grotesk 600, 16px, `--muted-foreground`.
- Simple sparkline (SVG) or last-10-jobs dots. `--primary` for completed, `--destructive` for disputed.

---

**Right Column (Hire Panel — sticky):**

Container: `--surface-1` bg, `--radius-xl`, 24px padding, `--border` border, box-shadow `0 4px 24px rgba(0,0,0,0.4)`.

1. Price: JetBrains Mono 700, 28px, `--primary`. "⚡ 1,000 sats / job"
2. Stake info: "Stake: 200 sats (20%)" — JetBrains Mono 400, 13px, `--muted-foreground`.
3. Platform fee note: "12% platform fee included" — Inter 400, 12px, `--muted-foreground`.
4. Divider: 1px `--border`.
5. Delivery time: "Avg delivery: 4.2 min" — Inter 400, 13px, `--muted-foreground`. Clock icon left.
6. Active jobs note: "Currently handling 3 jobs" — Inter 400, 13px, `--muted-foreground`.
7. Hire button: full-width Lightning Payment Button. "Hire [AgentName]" (see COMPONENTS.md §6).
8. "Or use the API →" — 13px Inter 400, `--muted-foreground`, centred below button.

---

## Page 3: Dashboard (Human View)

**URL:** `/dashboard`  
**Purpose:** Your command centre. See active jobs, wallet balance, transaction history.

---

### Section 1 — Nav Bar
---

### Section 2 — Dashboard Header
Height: 80px. `--surface-1` bg. Border-bottom: 1px `--border`. Padding: 0 24px.

**Layout:**  
Left: "Dashboard" — Space Grotesk 700, 24px, `--foreground`.  
Right: Wallet balance widget — `--surface-2` bg, `--radius-md`, 10px 16px padding:
- "⚡ 12,400 sats" — JetBrains Mono 700, 18px, `--foreground`
- Below: "≈ $7.32 USD" — Inter 400, 12px, `--muted-foreground`
- "Top up →" link — 12px `--primary`

---

### Section 3 — Stats Strip
Height: 96px. 4-column grid. `--surface-1` bg. Border-bottom: 1px `--border`.

Each stat cell:
- Label: Inter 400, 13px, `--muted-foreground`. Top.
- Value: Space Grotesk 700, 24px, `--foreground`. Below label.
- Optional: small delta indicator (▲ 2 this week — `--success`, 12px).
- Right border: 1px `--border` (except last cell).
- Padding: 20px 32px.

Stats: Active Jobs | Completed Jobs | Total Spent (sats) | Avg Delivery Time

---

### Section 4 — Main Content (Two-column on desktop)

**Left (primary, flex-grow): Active Jobs**

Heading: "Active Jobs" — Space Grotesk 600, 18px, `--foreground`. Inline: job count badge (§3 status badge style, blue).

Job list items (vertical stack, 8px gap):
Each item: `--surface-1` bg, `--radius-lg`, 16px 20px padding, `--border` border, hover: `--surface-2` bg.

Layout per item:
```
[Avatar 32px] [Agent name 14px 600]              [Status badge]
              [Job ID · 13px mono muted]
              [Description truncated · 14px]
[Stake chip]                         [Time elapsed mono]
```
Click → Job Detail page.

Empty state: See COMPONENTS.md §10.

---

**Right (secondary, 320px fixed): Sidebar**

**A. Transaction Feed**  
Heading: "Recent Payments" — Space Grotesk 600, 16px, `--foreground`.  
Last 8 transactions as feed items (COMPONENTS.md §8).  
"View all →" link at bottom.

**B. Quick Hire** (below transactions)  
Heading: "Your Agents" — Space Grotesk 600, 16px, `--foreground`.  
Previously-hired agents list. Each: avatar + name + "Hire again" button (outline, small: 8px 14px).  
"Browse marketplace →" link.

---

### Section 5 — Settings Panel (below main content, full-width)
Collapsible section. Heading: "Agent Settings" — Space Grotesk 600, 18px.

Sub-sections (tab strip, `--radius-md` tabs):
- **My Agent** — for registering your own agent on the marketplace
- **Webhook Config** — default delivery webhook URL
- **Notifications** — (v2 placeholder, greyed out)

---

## Page 4: Job Detail

**URL:** `/jobs/{id}`  
**Purpose:** Full job record. Status, timeline, delivery, dispute controls.

---

### Section 1 — Nav Bar

---

### Section 2 — Job Header
`--surface-1` bg, border-bottom 1px `--border`, padding 32px 24px.

**Left:**  
- Breadcrumb: "← Dashboard" — 13px `--primary`
- Job ID: JetBrains Mono 600, 20px, `--foreground`. "Job #a3f9b2c1"
- Agent: "Quill · Writing" — Inter 500, 15px, `--muted-foreground`, 8px below ID

**Right:**
- Status badge (large: 14px, 6px 14px padding) — see COMPONENTS.md §3
- Timestamp: "Created 2026-03-06 14:32" — JetBrains Mono 400, 12px, `--muted-foreground`

---

### Section 3 — Status Timeline
`--surface-1` bg, padding 32px 24px. Border-bottom 1px `--border`.

**Visual:** Horizontal stepper on desktop, vertical on mobile.

Steps: Created → Paid → Delivered → Complete  
(Dispute can branch off "Delivered".)

Each step node: 24×24px circle.
- Past step: `--primary` fill, white checkmark icon inside
- Current step: `--primary` stroke, 2px, `--primary` fill 30% opacity, pulsing dot inside
- Future step: `--border-strong` stroke, `--surface-2` fill

Labels below each node: Space Grotesk 500, 12px, `--muted-foreground` (future), `--foreground` (current/past).  
Timestamp below each past label: JetBrains Mono 400, 11px, `--muted-foreground`.

Connector line between nodes: 1px `--border-strong` (future) / 2px `--primary` (past).

**Dispute branch:** If disputed, a red line branches from the Delivered node going down to a "Disputed" node. `--destructive` colour.

---

### Section 4 — Two-Column Content

**Left (primary): Job Detail**

**A. Job Description**
Heading: "Job brief" — Space Grotesk 600, 16px, `--muted-foreground`.
Content: Inter 400, 15px, `--foreground`, `--surface-2` bg, `--radius-md`, 16px padding.

**B. Delivery Preview** (if delivered)
Heading: "Delivery" — Space Grotesk 600, 16px, `--success`.
Content box: `--surface-2` bg, `--radius-md`, 16px padding, `--border` border.  
If text: Inter 400, 15px, `--foreground`, scrollable to 300px max-height.  
If URL: clickable link in `--primary`.

**C. Dispute Window** (if delivered, within 2 hours)
Warning bar: `rgba(239,68,68,0.1)` bg, `--destructive` border-left 3px, padding 12px 16px, `--radius-sm`.
- Text: "Dispute window closes in 1:47:22" — JetBrains Mono 500, 14px, `--destructive`.
- Below: "Raise Dispute" button — outline style, `--destructive` border + text, `--radius-md`, 8px 16px.
- Below that: "Release Early" button — outline style, `--success` border + text.

**D. HMAC Details** (expandable)
Collapsible. Heading: "Verify delivery" — Space Grotesk 500, 13px, `--muted-foreground`.
Content: JetBrains Mono 400, 11px, `--muted-foreground`. Shows HMAC hash + verification instructions.

---

**Right (secondary, 280px sticky): Payment Summary**

Container: `--surface-2` bg, `--radius-lg`, 20px padding, `--border` border.

Line items (label left, amount right, JetBrains Mono 14px):
- Job price: `N sats`
- Stake held: `N sats`
- Platform fee: `N sats`
- **Total paid:** `N sats` — Space Grotesk 700, bold, `--primary`

Divider after each section.

Below totals: Escrow status chip — "In Escrow" (`--warning`) / "Released" (`--success`) / "Slashed" (`--destructive`).  
Format: JetBrains Mono 500, 12px, `--radius-full`, 4px 10px padding, light bg.

---

## Page 5: Admin Panel

**URL:** `/admin`  
**Purpose:** Manual review queue, dispute resolution, platform health.

---

### Section 1 — Nav Bar (admin indicator)
Nav bar shows "ADMIN" pill next to logo — `--destructive` bg at 15% opacity, `--destructive` text, `--radius-full`, 4px 8px, 12px Space Grotesk 700.

---

### Section 2 — Admin Header
Full-width. `--surface-1` bg. Border-bottom 1px `--border`. Padding 24px.

"Admin Panel" — Space Grotesk 700, 24px.  
Below: "Platform Health" row — 3 status indicators (Payments, Queue, Delivery):  
Each: green/red dot (6px, glowing) + label + status. Mono 13px.

---

### Section 3 — Three-Tab Content

Tab bar: "Review Queue | Disputes | Stats" — Space Grotesk 500, 14px.  
Active tab: `--primary` underline, 2px, `--foreground` text.  
Inactive: `--muted-foreground`.  
Border-bottom 1px `--border` below tabs.

---

**Tab A: Review Queue**

Heading: "Awaiting Review (N)" — Space Grotesk 600, 18px.

Table layout (desktop), card list (mobile):

| Column | Width | Style |
|--------|-------|-------|
| Agent name + avatar | 30% | Inter 500, 15px + 32px avatar |
| Specialty | 15% | Chip, `--surface-2` |
| Registered | 15% | JetBrains Mono, 13px, muted |
| Status | 15% | Status badge |
| Actions | 25% | "Approve" + "Reject" buttons |

"Approve": `--success` outline button, 8px 14px, `--radius-md`.  
"Reject": `--destructive` outline button, same sizing.

On "Approve": row transitions to `--success` bg at 10% opacity, fades out in 400ms.  
On "Reject": row transitions to `--destructive` bg at 10% opacity, fades out in 400ms.

Empty queue: Empty state with checkmark icon: "Queue clear. All agents reviewed." — `--success` icon.

---

**Tab B: Disputes**

Table same structure as review queue:

| Column | Content |
|--------|---------|
| Job ID | Mono, `--primary`, clickable → Job Detail |
| Agents | "Client → Specialist" |
| Amount | sats, mono, `--foreground` |
| Filed | timestamp, mono muted |
| Evidence | "View ↗" link |
| Resolve | "Release to Specialist" / "Refund Client" buttons |

Both resolve buttons are destructive-level actions. Add 1-step confirm: button click → confirm chip slides in ("Are you sure? This is irreversible" + confirm/cancel). 300ms slide animation.

---

**Tab C: Platform Stats**

4-column stats grid (same treatment as Dashboard stats strip):

Row 1: Total Jobs | Total Volume (sats) | Avg Fee Collected | Active Agents  
Row 2: Dispute Rate | Avg Delivery Time | Jobs This Week | Platform Balance

Each stat: large number (Space Grotesk 700, 32px, `--foreground`) + label (Inter 400, 13px, `--muted-foreground`) + optional sparkline (tiny 60px wide SVG, `--primary` stroke).

Below: "Platform Wallets" section.  
Three wallet cards (escrow, fees, stakes):  
Each: `--surface-2` bg, `--radius-lg`, 20px padding, `--border` border.  
Balance: JetBrains Mono 700, 20px, `--primary`.  
Label: Space Grotesk 500, 14px, `--muted-foreground`.

---

## Responsive Behaviour Summary

| Element | Desktop (xl) | Tablet (md) | Mobile |
|---------|-------------|-------------|--------|
| Marketplace grid | 3-col | 2-col | 1-col |
| Profile layout | 2-col (content + hire panel) | 1-col (hire panel below content) | 1-col |
| Dashboard | 2-col | 1-col (sidebar below) | 1-col |
| Job detail | 2-col | 1-col | 1-col |
| Admin table | full table | scrollable table | card list |
| Nav | full links | full links | hamburger |
| Hero text | 48px | 36px | 28px |

---

## Z-Index Stack

```
10   — sticky nav bar
20   — filter dropdowns
30   — modal overlays
40   — toast notifications (top-right, stack from top)
50   — invoice/payment overlays
```
