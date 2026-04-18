# Phase 5 Accessibility Report — WCAG 2.1 AA

> Generated 2026-04-18 against staging 193920860326 @ feat/flex-migration 4ab4666.
> Scoped to customer paths: homepage, PDP, cart, search results, blog article.
> Methodology: manual WCAG 2.1 AA audit via browser computed-style inspection +
> CSS-rule enumeration. `design:accessibility-review` skill not installed; used
> equivalent checks against WCAG criteria.
>
> Any finding that reproduces on vanilla Flex (i.e. exists before LC customisation)
> is marked `upstream-flex` and routed to Phase 6 exclusion list — LC is not forking
> Flex to fix Flex's base-theme issues.

## Findings by WCAG criterion

### WCAG 1.4.3 Contrast (Minimum) — Level AA

| id | element | fg | bg | ratio | threshold | status | priority | action |
|---|---|---|---|---|---|---|---|---|
| C-01 | `.footer__block.block__newsletter .newsletter-form button[type="submit"]` (Sign Up) | `#ebac20` | `#EBAC20` | **1.00** | 4.5 (button text) | **FAIL** | **P0-block-phase-6** | fix-now — set `color: var(--color-dark)` |
| C-02 | `.button.button--primary` (primary CTAs site-wide) | `#ebac20` | `#EBAC20` | **1.00** | 4.5 | **FAIL** | **P0-block-phase-6** | fix-now — same fix as C-01; this is the root of both (admin `button_primary_text_color: #ebac20` matches `button_primary_bg_color: #EBAC20`) |
| C-03 | `h1` product title on white surface | `#2a2a2a` | `#ffffff` | 14.35 | 4.5 | PASS | — | — |
| C-04 | body paragraph on article bg (Lato 17px) | `#6f6f6f` or darker | white/grey | 9.68 | 4.5 | PASS | — | — |
| C-05 | footer link | `#f5f5f5` | `#4d4d4d` | 7.75 | 4.5 | PASS | — | — |
| C-06 | `.button--secondary` text | `#2a2a2a` | `#EBAC20` | 7.15 | 4.5 | PASS | — | — |
| C-07 | announcement bar gold on near-black | `#EBAC20` | `#0d0d0d` | 10.2 (per Phase 3 comment) | 4.5 | PASS | — | — |
| C-08 | header nav white links over translucent hero | `#fff` | `rgba(18,18,18,0.55)` composited over video | varies | 4.5 | **AMBIGUOUS** | P2-post-launch | document-as-intentional — LC design relies on the dark-translucent overlay; worst-case video frames can drop contrast below 4.5. Phase 6 exclusion list. |

**Headline contrast finding: C-01 and C-02 are one bug. Both originate from Phase 4 T6 rewiring `.button--primary` descendants to read `var(--button-primary-text-color)`. Admin's default for that token is `#ebac20` gold, identical to the gold background. Same fix resolves both entries.**

### WCAG 2.4.7 Focus Visible — Level AA

| id | element | observation | priority | action |
|---|---|---|---|---|
| F-01 | Multiple | 9 CSS rules set `outline: none` on `:focus` state across Flex theme.css + LC custom.css. Only 2 `:focus-visible` rules replace them. The net effect: most keyboard-focusable elements have no visible focus indicator when tabbed to. | **P1-fix-in-phase-5** | fix-now — add `:focus-visible` rule to `custom.css` covering `a, button, input, select, textarea` with `outline: 2px solid var(--color-brand-gold); outline-offset: 2px`. Do NOT replace `:focus { outline: none }` (mouse clicks shouldn't show rings); use `:focus-visible` specifically. |
| F-02 | Logo (primary-logo img) | First tab lands on logo; computed outline is `rgb(255,255,255) none 1.5px` — outline-style `none` = no visible ring. | **P1-fix-in-phase-5** | covered by F-01 fix |

### WCAG 2.5.5 Target Size — Level AAA (aspirational)

| id | element | size | priority | action |
|---|---|---|---|---|
| T-01 | `.mega-menu__linklist-link` (10+ entries sampled) | 159–190 × **34** px — below 44 × 44 | P2-post-launch | document-as-intentional — Flex's mega menu base density; increasing height reflows the mega panel; Brett's visual-density preference retains compact rows. AAA target not AA. |

WCAG 2.1 AA does NOT require 44×44 (that's AAA via 2.5.5). On AA, target size (2.5.5 is AAA) is only a guideline via adequate spacing (2.5.8 at AA — but 2.5.8 is AA in WCAG 2.2, not 2.1). Under the sprint's stated AA target, T-01 is **not a blocker**.

### WCAG 1.1.1 Non-text Content (alt text) — Level A

| id | observation | priority | action |
|---|---|---|---|
| A-01 | 66 images total on PDP, 0 with missing `alt` attribute, 36 with empty `alt=""`. | P3-cosmetic-won't-fix | — (decorative images with `alt=""` is valid — used for repeated thumbnails, icons, etc. Flex's pattern.) |

### WCAG 3.3.2 Labels or Instructions — Level A

| id | element | observation | priority | action |
|---|---|---|---|---|
| L-01 | Newsletter email input (`name="contact[email]"`) | has placeholder `"Email*"` but no `<label>` or `aria-label`. Placeholder is not a substitute for label. | **P1-fix-in-phase-5** | fix-now — add `aria-label="Email address"` via the snippet that renders the newsletter form (OR wrap in a visually-hidden `<label>`). |
| L-02 | Search input (`name="q"`, appears 2×) | placeholder only; no label. | **P1-fix-in-phase-5** | fix-now — add `aria-label="Search"` to both. |
| L-03 | Size variant `<select>` | `name="id"` with no id or label. | upstream-flex | document-as-intentional — Flex's rendering of variant select. Not fixing in LC custom.css; propose to Brett as merchant action to request Flex upstream fix. |

### WCAG 1.3.1 Info and Relationships (heading hierarchy) — Level A

| id | observation | priority | action |
|---|---|---|---|
| H-01 | PDP page heading order: `h1` → `h5` (Size Guide) → `h2` (More from) → `h4` (More works) → `h2` (Search). Not strictly sequential — `h5` directly under `h1`, `h4` before a later `h2`. | P2-post-launch | document-as-intentional — Flex's base heading pattern for these sections. LC could not unilaterally demote `h4` to `h3` etc. without breaking visual scale. Propose as a post-launch cleanup. |

### WCAG 2.2.2 Pause, Stop, Hide — Level A

| id | observation | priority | action |
|---|---|---|---|
| M-01 | Homepage hero auto-plays a video (Vimeo iframe). Video has pause controls (visible per Phase 0-3 captures showing the Vimeo player chrome). | — | PASS — controls available via the embedded Vimeo player. |
| M-02 | Announcement bar marquee — if any — is CSS animated. `prefers-reduced-motion` handling not audited in this sprint. | P2-post-launch | follow-up — add `@media (prefers-reduced-motion: reduce) { .marquee { animation: none }}` rule to `custom.css`. |

## Summary counts

| Priority | Count |
|---|---:|
| P0-block-phase-6 | **2** (C-01, C-02 — both resolved by the same fix) |
| P1-fix-in-phase-5 | **4** (F-01, F-02 focus; L-01, L-02 form labels) |
| P2-post-launch | 4 (C-08 header-over-video contrast; T-01 mega menu target; H-01 heading order; M-02 reduced-motion) |
| P3-cosmetic-won't-fix | 1 (A-01 empty alt) |
| upstream-flex (Phase 6 exclusion) | 1 (L-03 variant select label) |

## T4 action list

| Fix | Covers | Approach |
|---|---|---|
| Update `.button.button--primary` and `.footer__block...newsletter...button` to use `color: var(--color-dark)` | C-01, C-02 | One edit in `custom.css:1164` + `:1677` (already two separate rules — small edit in each). After: gold bg + dark text = 7.15:1 contrast ✓ |
| Add `:focus-visible` outline rule in `custom.css` | F-01, F-02 | New rule near the accessibility section at `custom.css` section 42 (2026-04-09 audit). Outline: `2px solid var(--color-brand-gold); outline-offset: 2px` |
| Add `aria-label` to newsletter + search inputs | L-01, L-02 | Requires editing snippet(s) that render the newsletter form + search popup. Modify without touching layout/visuals. |

## Deferred (post-launch follow-ups, post-Phase-6)

- C-08 header contrast over video — needs design decision: either darken the header bg further OR add a text-shadow to nav links. Brett's call.
- T-01 mega menu target height — needs design decision: increase by ~5px per row to meet AAA, or defer.
- H-01 heading hierarchy — Flex upstream issue; propose cleanup in a post-launch theme-refactor or submit to Flex.
- M-02 `prefers-reduced-motion` — small follow-up, no user impact on default motion preference.
- L-03 variant select label — upstream Flex.

## Phase 6 exclusion list

- L-03 variant `<select>` missing label — upstream-flex. Won't be fixed in LC fork.
- Customer-account pages — no logged-in session to test in this sprint. Brett or Cowork to do pre-push manual spot-check.
