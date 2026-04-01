# obiraoke — UI Specification

> **Authoritative style guide for ALL obiraoke UI work.**
> CC must read this file before touching any React component.
> This spec is law. If it conflicts with existing code, the code is wrong.


---

## Spec and UI Rules

The header is near-black — #262626 (which matches vf-bg-dark exactly from the UI spec). 
No gradient at all. 
White text, Ubuntu Orange CoF logo top left. Clean, flat, dark bar.

Topbar: background: #262626 — flat, no gradient
Suru gradient: Never
Everything else already correct per the UI spec

No border-radius on structural elements.

font-light on all headings.

Never use Suru gradient

Ubuntu variable font from assets.ubuntu.com only. 

Nothing below overalls these absolute rules.

## 1. Source of Truth

The canonical.com website is the visual reference. The live CSS was extracted
from `canonical.com/microcloud` and is the authoritative source for all color
values, typography, and spacing. Do not invent colors. Do not use Material UI.
Do not use Bootstrap. Do not use any component library except what is explicitly
listed below.

### Approved Libraries

| Library | Purpose | Scope |
|---------|---------|-------|
| Tailwind CSS v3 | Utility classes only | Both apps |
| lucide-react | Icons only | Both apps |
| Recharts | Charts only | Dashboard only |
| react-markdown + react-syntax-highlighter | Markdown rendering | Docs only |
| react-router-dom v6 | Routing | Both apps |

### Prohibited

- Material UI / MUI
- Bootstrap / React Bootstrap
- Chakra UI
- Ant Design
- Any component library not listed above
- `border-radius` on ANY structural element (cards, panels, inputs, buttons,
  nav items, tables). **EXCEPTION:** pill badges may use `rounded-full`
- Inventing Ubuntu/Canonical logos — use ONLY the SVGs at
  `web/dashboard/src/assets/ubuntu-logo.svg`
- Google Fonts — use Ubuntu variable font from `assets.ubuntu.com`
- Any shade of purple/violet that is not exactly `#772953`
- Any orange that is not exactly `#e95420`

---

## 2. Color System

These values are copied EXACTLY from `web/dashboard/tailwind.config.js`.
Do not approximate. Do not round hex values.

### Vanilla Framework Tokens

Use CSS var names in Tailwind as-is (e.g. `bg-vf-bg-alt`).

| Token | Value | Usage |
|-------|-------|-------|
| `vf-accent` | `#0f95a1` | Teal — links, chart lines, info |
| `vf-accent-paper` | `#70bbc2` | Lighter teal — hover states |
| `vf-link` | `#06c` | Body links |
| `vf-link-dark` | `#69c` | Links on dark backgrounds |
| `vf-bg` | `#ffffff` | Primary background |
| `vf-bg-alt` | `#f7f7f7` | Content area background |
| `vf-bg-paper` | `#f3f3f3` | Card backgrounds |
| `vf-bg-dark` | `#262626` | Sidebar background |
| `vf-bg-dark-alt` | `#202020` | Sidebar hover/active |
| `vf-text` | `#000000` | Primary text |
| `vf-text-muted` | `rgba(0,0,0,0.6)` | Secondary text |
| `vf-border` | `rgba(0,0,0,0.2)` | Light border |
| `vf-border-dark` | `rgba(255,255,255,0.2)` | Dark border |

### Status Colors

Use ONLY these values — do not use Tailwind's default green/red/yellow.

| Status | Hex | Usage |
|--------|-----|-------|
| Active / Success | `#0e8420` | Green |
| Warning / Expiring | `#f99b11` | Amber |
| Error / Critical | `#c7162b` | Red |
| Inactive / Unknown | `#757575` | Gray |
| Info | `#0f95a1` | Teal (same as `vf-accent`) |

---

## 3. Typography

### Font Stack

```
Primary:   "Ubuntu variable", "Ubuntu", -apple-system, "Segoe UI", Roboto, sans-serif
Monospace: "Ubuntu Mono variable", "Ubuntu Mono", Consolas, Monaco, Courier, monospace
```

### Font Sources

Use ONLY these URLs — never Google Fonts.

| Variant | URL |
|---------|-----|
| Regular/Italic variable | `https://assets.ubuntu.com/v1/f1ea362b-Ubuntu[wdth,wght]-latin-v0.896a.woff2` |
| Italic variable | `https://assets.ubuntu.com/v1/90b59210-Ubuntu-Italic[wdth,wght]-latin-v0.896a.woff2` |
| Mono variable | `https://assets.ubuntu.com/v1/d5fc1819-UbuntuMono[wght]-latin-v0.869.woff2` |

Weight range: 100–800 (variable font, no separate bold files needed).

### Type Scale

| Element | Tailwind Classes | Size / Weight |
|---------|------------------|---------------|
| Page title (h1) | `text-2xl font-light` | 24px, weight 300 |
| Section title (h2) | `text-xl font-light` | 20px, weight 300 |
| Card title | `text-sm font-medium` | 14px, weight 500 |
| Body | `text-sm` | 14px, weight 400 |
| Caption / label | `text-xs` | 12px, weight 400 |
| Uppercase label | `text-xs uppercase tracking-widest font-medium` | 12px, weight 500 |

### Heading Weight Rule

ALL headings use `font-light` (300) unless they are card titles or labels.
Canonical.com uses very light heading weights — never use `font-bold` on
h1/h2/h3.

---

## 4. Layout Chrome

The chrome (sidebar + topbar) is IDENTICAL between dashboard and docs. Copy
components exactly — do not rewrite from scratch.

### Sidebar

| Property | Value |
|----------|-------|
| Width | `w-52` (208px) fixed |
| Background | `bg-[#262626]` |
| Left accent | `4px solid #e95420` — applied as `style={{ borderLeft: '4px solid #e95420' }}` |



**Nav section headers:**
```
text-[10px] uppercase tracking-widest text-gray-500
px-4 pt-4 pb-1
```

**Nav items (inactive):**
```
flex items-center gap-2 px-4 py-2 text-sm text-gray-400
hover:text-white cursor-pointer
```
NO background change on hover — only text color.

**Nav items (active):**
```
style={{ borderLeft: '2px solid #e95420' }}
bg-[#313131] text-white
```
Active items have BOTH the 4px outer sidebar accent bar AND a 2px inner border
on the item itself.

**Nav icons:**
lucide-react, size 16, `className="shrink-0"`

**Version footer:**
```
mt-auto px-4 pb-4
text-[10px] text-gray-600
"obiraoke v0.1.0"  ← always lowercase
```

### Topbar

| Property | Value |
|----------|-------|
| Height | `h-12` (48px) |
| Background | Suru gradient (inline style) |
| Layout | `flex items-center px-6 gap-4` |

Background (always inline style):
```
style={{ background: 'linear-gradient(-89deg, #e95420 0%, #772953 42%, #2c001e 94%)' }}
```

**Left side — page title:**
```
text-white text-lg font-light
```
- Dashboard: `"Canonical obiraoke"` + hostname badge
- Docs: `"Docs - Canonical obiraoke"`

**Hostname badge (dashboard only):**
```
bg-white/20 text-white text-xs px-2 py-0.5
```
NO border-radius.

**Right side:**
- Docs: search input
- Dashboard: user menu placeholder

### Content Area

| Property | Value |
|----------|-------|
| Background | `bg-[#f7f7f7]` |
| Padding | `p-6` |
| Max width | None (full width) for dashboard |
| Max width | `max-w-4xl mx-auto` for docs prose |

---

## 5. Components

### Cards

| Property | Value |
|----------|-------|
| Background | `bg-white` |
| Border | `style={{ border: '1px solid rgba(0,0,0,0.2)' }}` |
| Border radius | NONE (`rounded-none`) |
| Shadow | `shadow-sm` |
| Padding | `p-4` |

### Stat Cards

Same as cards, plus:

| Element | Value |
|---------|-------|
| Icon circle | `w-10 h-10 flex items-center justify-center bg-{accent}-100` |
| Value | `text-2xl font-light` — `font-light` NOT `font-bold` |
| Label | `text-xs uppercase tracking-wide text-gray-500` |
| Subtitle | `text-xs text-gray-400` |

### Status Badges

```
inline-flex items-center px-2 py-0.5 text-xs
```
Border radius: NONE (`rounded-none`).

| State | Classes |
|-------|---------|
| Active | `bg-green-100 text-[#0e8420]` |
| Inactive | `bg-gray-100 text-[#757575]` |
| Error | `bg-red-100 text-[#c7162b]` |
| Warning | `bg-yellow-100 text-[#f99b11]` |

### Tables

| Element | Value |
|---------|-------|
| Width | `w-full border-collapse` |
| Header | `bg-[#f7f7f7] text-xs uppercase tracking-wide text-gray-500 border-b-2` with `style={{ borderBottomColor: 'rgba(0,0,0,0.2)' }}` |
| Row hover | `hover:bg-[#f7f7f7]` |
| Row border | `style={{ borderBottom: '1px solid rgba(0,0,0,0.1)' }}` |
| Cell padding | `px-4 py-3` |

### Buttons

**Primary (action):**
```
style={{ backgroundColor: '#e95420', color: 'white' }}
px-4 py-2 text-sm font-medium
```
NO border-radius. Hover: `style={{ backgroundColor: '#c44210' }}`.

**Secondary (outline):**
```
style={{ border: '1px solid #e95420', color: '#e95420' }}
px-3 py-1.5 text-sm
```
NO border-radius. Hover: `bg-orange-50`.

**Neutral:**
```
style={{ border: '1px solid rgba(0,0,0,0.2)' }}
text-gray-600 px-3 py-1.5 text-sm
```
NO border-radius.

### Inputs

```
style={{ border: '1px solid rgba(0,0,0,0.2)' }}
px-3 py-1.5 text-sm bg-white
```
NO border-radius. Focus: `style={{ outline: '2px solid #0f95a1', outlineOffset: 0 }}`.
Placeholder: `text-gray-400`.

### Alert Banners

Full width, no border-radius, `p-3`. Left border 4px:

| Type | Style |
|------|-------|
| Info | `style={{ borderLeft: '4px solid #0f95a1' }}` `bg-teal-50` |
| Warning | `style={{ borderLeft: '4px solid #f99b11' }}` `bg-yellow-50` |
| Error | `style={{ borderLeft: '4px solid #c7162b' }}` `bg-red-50` |

### Code Blocks (docs)

```
bg-[#262626] text-white p-4
font-family: "Ubuntu Mono variable"
```
NO border-radius. Copy button: `absolute top-2 right-2, text-gray-400 hover:text-white`.

---

## 6. Suru Gradient

NEVER USE

---

## 7. Icons

Use ONLY lucide-react. No other icon library.

Standard sizes: 16 (inline/nav), 20 (cards), 24 (hero stats).

Color: inherit from parent text color. Never use emoji as icons in the UI.


---

## 8. Implementation Rules for CC

These rules are ABSOLUTE. CC must follow them on every PR:

1. **Never use border-radius on structural elements.** Only pill badges
   (`rounded-full`) are permitted.

2. **Never invent a Ubuntu/Canonical logo.** Always import from the existing
   SVG asset file.

3. **Never use Google Fonts.** Ubuntu variable font only.

4. **Never use hex values not listed in Section 2.** If a color is needed,
   use the closest listed value.

5. **Never use a component library** (MUI, Bootstrap, etc). Tailwind utility
   classes only.

6. **Always use inline styles for the Suru gradient** — Tailwind's JIT may
   not generate it correctly.

7. **Always use inline styles for border colors that use `rgba()` values** —
   Tailwind cannot generate arbitrary rgba values without config.

8. **`font-light` (300) for all headings.** Never `font-bold` on h1/h2/h3.

9. **"Canonical obiraoke"** in visible UI branding. **"obiraoke"** (lowercase)
   everywhere else — commands, service names, version strings, config keys.

10. **Before writing any new component,** check if an equivalent already exists
    in `web/dashboard/src/components/`. If it does, copy it — do not rewrite
    from scratch.
