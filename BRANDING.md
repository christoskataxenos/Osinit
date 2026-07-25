# Osinit Brand & Style Guidelines

This document outlines the design principles, visual standards, and verbal guidelines for the **Osinit** project. Adhering to these guidelines ensures a consistent, secure, and professional user experience across the dashboard, Telegram bot, error states, and developer documentation.

---

## 1. Active Design Dials (High-Agency Baseline)

To maintain a premium, tactical, and high-performance dashboard layout, all frontend development is matched the following system parameters:

*   **DESIGN_VARIANCE: 8** (Asymmetric bento layouts, split-screen sections, and left-aligned display headers over centered grids).
*   **MOTION_INTENSITY: 6** (Weighty spring physics, infinite status loops, and layout transition cascades).
*   **VISUAL_DENSITY: 9** (Cockpit Mode: High-density layouts, narrow table paddings, and negative-space dividers over boxed elements).

---

## 2. Brand Philosophy

Osinit is a security-focused, offline-first open-source intelligence aggregator. The brand experience must project **reliability, stealth, analytical precision, and absolute data ownership**.

-   **Analytical (Never Sensational)**: We present intelligence data objectively. We let facts and numbers speak for themselves.
-   **Privacy-First**: The UI and copy should reassure the user that data is held locally and isn't being sent to third-party cloud trackers.
-   **Developer-Centric**: We prioritize clarity, clean layouts, and functional details over decorative clutter.

---

## 3. Visual & Styling Standards

The visual design is inspired by high-fidelity tactical operation dashboards. It uses a high-contrast dark theme with sharp, desaturated status indicators.

### Color Palette

| Usage | Tailwind Class | HEX Value | Purpose / Description |
| :--- | :--- | :--- | :--- |
| **Primary Background** | `bg-slate-950` | `#020617` | Main container and application background. (Never use pure `#000000`). |
| **Secondary Background** | `bg-slate-900` | `#0f172a` | Card containers, sidebar background, and structured inputs. |
| **Borders** | `border-slate-800` | `#1e293b` | Structural borders dividing panels and feed items. |
| **Primary Text** | `text-slate-100` | `#f1f5f9` | High-contrast readability for titles and main headers. |
| **Secondary Text** | `text-slate-400` | `#94a3b8` | Subheadings, descriptions, and metadata labels. |
| **Interactive / Accent** | `text-sky-400` / `bg-sky-950` | `#38bdf8` / `#0c4a6e` | Active tabs, selected feed items, and primary action buttons. |
| **Warning / Alert (Live)** | `text-red-400` / `bg-red-950` | `#f87171` / `#450a0a` | Indicates active conflict reports, critical errors, or destructive actions. |
| **Transit / Pending** | `text-amber-400` / `bg-amber-950` | `#fbbf24` / `#451a03` | Loading states, "Fetching data...", or API rate limits. |
| **Security / Tor Indicator** | `text-emerald-400` / `bg-emerald-950` | `#34d399` / `#064e3b` | Confirms encrypted darknet status, safe connections, or successful database saves. |

> [!WARNING]
> **The Lila Ban**: The standard "AI Purple/Blue" aesthetic is strictly forbidden. No purple glows, neon gradients, or oversaturated accents are allowed.

### Typography Guidelines
-   **Display & Headlines**: Use clean, modern, tracking-tight sans-serif fonts (e.g., `Geist`, `Satoshi`, or `Outfit`). Serif fonts are strictly BANNED.
-   **Body & Paragraphs**: Keep font sizing functional (`text-sm` or `text-base` in `text-slate-400`) and contain line lengths to `max-w-[65ch]` to improve readability.
-   **Data & System Text**: Use monospace fonts (e.g., `Geist Mono`, `JetBrains Mono`, or `Fira Code`) for UUIDs, coordinates, timestamps, and SOCKS5 proxy logs.

### Spacing & Dashboard Hardening
-   **High Information Density**: The UI must support tactical monitoring. Use tight vertical paddings (`py-1` or `py-2`) in tables and incident feeds rather than oversized UI elements.
-   **Anti-Card Overuse**: Banned generic card wrapping. Use logic-grouping via `border-t`, `divide-y`, or purely negative space. Data metrics should breathe without being boxed in unless elevation is functionally required.
-   **Asymmetric Grids**: Avoid the generic "3 equal cards" feature row. Use asymmetric grid layouts (`grid-cols-1 md:grid-cols-3` with custom span ratios like `md:col-span-2`) to guide the analyst's eye.
-   **Viewport Stability**: Never use `h-screen` for full-height UI grids. Always use `min-h-[100dvh]` to prevent catastrophic layout jumping on mobile browsers.

### Interactive UI States & Tactile Feedback
-   **Tactile Actions**: On `:active` interaction, apply physical feedback: scale elements down slightly (`active:scale-[0.98]`) or shift them vertically (`active:translate-y-[0.5px]`).
-   **Liquid Glass Refraction**: When glassmorphic dialogs or overlays are required, add a `1px` inner border (`border-white/10`) and a subtle inner shadow (`shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]`) to simulate glass refraction.
-   **Loading States**: Use skeleton pulse loaders matching the exact card/row shape instead of generic circular spinners.
-   **Perpetual Motion Loops**: Active connections (like SOCKS5 status dots) must feature a slow breathing infinite keyframe animation (`animate-pulse`) to keep the dashboard feeling live and operational.

---

## 4. Verbal Guidelines (Tone & Voice)

Osinit follows the **Plain Speech** framework as its default tone, reserving structured personality for specific system feedback.

### Key Principles
-   **Be Concise**: Strip out fluff. Use the minimum number of words to describe actions or statuses.
-   **Be Direct**: Tell users exactly what to do or what is happening.
-   **Use Active Voice**: Prefer active, direct verbs.
-   **Remain Objective**: Avoid emotionally charged words (e.g., `"devastating"`, `"shocking"`, `"catastrophic"`) in system-generated text.

### Plain Speech Examples

| Instead of | Write |
| :--- | :--- |
| "Please click here to refresh the current incident list" | "Refresh feed" |
| "You can now select to view darknet reports only" | "Filter: Darknet" |
| "A connection error has unfortunately occurred while saving" | "Save failed" |
| "Are you sure you want to delete this incident?" | "Delete incident?" |

### Writing for Security & Tor Statuses
Since Osinit works with SOCKS5 proxies and onion routing, status updates must be descriptive and reassuring:
-   **Good**: `Tor Proxy Status: Connected (IP: 185.220.101.5)`
-   **Bad**: `You are now browsing anonymously on Tor!` (too marketing-focused / hype-slop)

---

## 5. UI Copy Standards

### Date & Time Formatting
All timestamps must be strictly standardized to avoid confusion across global conflict zones.
-   Use 24-hour format and explicitly state the timezone (UTC preferred).
-   **Format**: `YYYY-MM-DD HH:MM UTC` (e.g., `2026-07-25 14:30 UTC`).

### Buttons & Navigation Labels
-   Start with an active verb.
-   Keep them to 2ΓÇ"3 words maximum.
-   No punctuation (periods or exclamation marks) on button labels.
-   *Examples*: `Filter Feed`, `Export CSV`, `View Source`, `Submit Report`.

### Error Messages
Don't just say something went wrong; state **what happened**, **why** (if known), and **how to fix it locally**.
-   **Good**: `Could not fetch incidents. Database server is unreachable. Check your Docker network and try again.`
-   **Bad**: `Error 500: Server disconnected.`

### Empty States
When a panel or search query returns no results:
1.  Explain what would normally be displayed.
2.  Provide a clear path to populate it.
-   **Good**: `No incidents recorded. Active darknet scrapers or user Telegram reports will populate the feed automatically. You can also import n8n workflow datasets to load initial events.`

---

## 6. Style Checklist

Before committing new frontend code or bot dialogues, verify:

- [ ] UI buttons use **Sentence case** (e.g., "Delete incident", not "DELETE INCIDENT" or "Delete Incident").
- [ ] No exclamations (`!`) are used in instructions or confirmation modals.
- [ ] SOCKS5 and Tor indicators use emerald color tokens when connected, and red/amber tokens when disconnected or pending.
- [ ] All error messages offer an actionable troubleshooting step.
- [ ] Layout spacing remains compact, supporting high data density (`py-1`/`py-2` lists).
- [ ] Dates and times are displayed in UTC following the `YYYY-MM-DD HH:MM UTC` format.
- [ ] Emojis are completely banned in code, markup, or main UI text (use Phosphor/Radix icons or raw SVG paths instead).
