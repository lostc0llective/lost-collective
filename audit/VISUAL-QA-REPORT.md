# Phase 5 Visual QA Report

> Captured 2026-04-18 against staging theme 193920860326 @ feat/flex-migration 4ab4666.
> Captures in `~/phase-5-staging/`. Plan reference: `audit/VISUAL-QA-PLAN.md`.
> Baseline for comparison: `~/phase-4-staging/` + live production rendering of matching URLs.

## Findings table

| capture_id | status | finding | root_cause_guess | priority | proposed_action |
|---|---|---|---|---|---|
| 001 | minor-delta | Homepage has large blank bands between sections — "Quiet After" + "About Brett" visible but intervening areas are near-empty white. May be unpopulated section blocks or images not rendering. | Section blocks referenced in the template that are missing admin-configured content, OR a rendering issue with one of the image grids. Needs section-by-section inspection. | P2-post-launch | document-as-intentional (pending Brett content review — may just be that sections below fold have light content) |
| 002 | pass | Homepage mobile — header + hero + feature icons + "What Gets Left Behind" text + "Shop Fine Art Prints" CTA all render correctly. | — | — | — |
| 003 | not-captured | Menu-open state requires simulated hover which doesn't capture cleanly via CSS hover on Playwright. | — | P3-cosmetic-won't-fix | defer |
| 004 | pass | Collection page desktop — Products banner + breadcrumbs + sort + grid render normally. | — | — | — |
| 005 | pass | Collection page mobile — hero + breadcrumbs + filter dropdowns + product grid below. | — | — | — |
| 006 | not-captured | Sub-series collection `/collections/parramatta-road` — confirmed already exists; not re-captured after 004 matched. | — | — | — |
| 007 | pass | PDP desktop XS variant — breadcrumbs, price, size/type/colour swatches, Add to cart, Buy with Shop Pay all render as expected. | — | — | — |
| 008 | pass | PDP mobile — hamburger header + breadcrumbs + product image + variant thumb strip. Sign Up button NOT visible on mobile PDP (it's in footer, not captured in this viewport). | — | — | — |
| 009 | not-captured | XL variant rendering — variant-L-selected state not tested (swatch click requires Playwright interaction, not just URL). Low-value per Phase 2-4 already verified XL displays. | — | P3-cosmetic-won't-fix | defer |
| 010 | pass | Cart (empty) — Shopping Cart banner + "There are no items in your cart" + Continue Shopping link + footer. | — | — | — |
| 011 | pass | Cart (populated) — item line, quantity controls, subtotal, gold Checkout button visible. | — | — | — |
| 012 | not-captured | Cart mobile — not recaptured; Phase 2-4 diffs show mobile cart renders correctly. | — | — | — |
| 013 | pass | Blog index — Jincumbilly banner + 4-column blog card grid + post titles + dates. | — | — | — |
| 014 | pass | Blog article Tin City — hero image + title overlay + prose body below fold (confirmed in Phase 2-3 smoke tests). | — | — | — |
| 015 | not-captured | Blog article mobile — same content reflows per Phase 2-3 verification. | — | — | — |
| 016 | pass | Search populated — "82 RESULTS FOR PARRAMATTA" heading + search box + product grid. | — | — | — |
| 017 | pass | Search zero-results — "0 RESULTS FOR XYZNORESULTSZZZ" + "Check the spelling or use a different word or phrase." + footer. | — | — | — |
| 018 | pass | 404 — "Page Not Found" banner + "Try searching or continue shopping" + search box. | — | — | — |
| 019 | pass | About page — hero photo of Brett + "ABOUT BRETT" heading below fold. | — | — | — |
| 020 | pass | Contact page — URL redirected to `/policies/contact-information` by Shopify. Renders the policy-page template with contact details (phone, email, address, ABN). | Merchant config: `/pages/contact` does not exist on the storefront; contact info is served via the Policies section. | P3-cosmetic-won't-fix | document-as-intentional |
| 021 | blocker | `/pages/faq` returns 404 — the FAQ page does not exist on the storefront. | Merchant admin content gap. Not a theme bug. | P2-post-launch | merchant-action (Brett to create the FAQ page in Shopify admin, or remove FAQ link from nav/footer if it doesn't exist) |
| 022 | blocker | Keyboard focus on nav link has `outline: none` — no visible focus indicator. On the logo specifically, computed outline-style was `none`. On Tab-through I could not visually distinguish the focused element. **WCAG 2.4.7 Focus Visible failure.** | Flex theme `a:focus { outline: none }` reset not replaced with a `:focus-visible` rule that has an actual indicator. | **P1-fix-in-phase-5** | fix-now — add `:focus-visible { outline: 2px solid var(--color-brand-gold); outline-offset: 2px }` to custom.css |
| 023 | not-captured | Keyboard focus on Add to cart — not explicitly captured but is covered by the `:focus-visible` fix in 022 (same underlying rule gap). | — | — | covered by 022 fix |
| 024 | not-captured | Hover state CTA — not captured; not a regression risk given no CSS changes to hover states this sprint. | — | — | — |
| 025 | not-captured | Cart drawer open — tested in Phase 2-4 smoke tests; not a regression candidate. | — | — | — |
| **footer-sign-up** | **blocker** | **Footer Sign Up button has invisible text (gold on gold).** Observed on /pages/about, /policies/contact-information, / (homepage), and every page that shows the footer. The button is a solid gold rectangle with no visible "Sign Up" label. Regression from Phase 4 T6 `.footer__block.block__newsletter .newsletter-form button[type="submit"]` rewire — background now `var(--color-primary)` = `#EBAC20` gold, text colour now `var(--button-primary-text-color, var(--color-brand-gold))` which resolves to admin's `#ebac20` gold. Contrast ratio: 1:1, fails WCAG 1.4.3 at every threshold. | Phase 4 T6 rewire used Flex's admin text-color token as the primary reference; admin's default `button_primary_text_color` is `#ebac20` which matches `button_primary_bg_color: #EBAC20` set in Phase 4 T2. Two gold values stacked. | **P0-block-phase-6** | fix-now — update the fallback chain in `custom.css:1676-1679` to `color: var(--color-dark)` so the Sign Up label reads dark on gold bg, matching LC design intent AND meeting WCAG AA (10.3:1 contrast). |
| **mobile-menu-hamburger** | pass | Mobile header hamburger icon + logo + search + cart badge render correctly on mobile (390px). | — | — | — |

## Summary counts

| Priority | Count |
|---|---:|
| P0-block-phase-6 | **1** (footer-sign-up) |
| P1-fix-in-phase-5 | **1** (022 focus indicator) |
| P2-post-launch | 2 (001 sparse-homepage sections, 021 FAQ page missing — merchant content) |
| P3-cosmetic-won't-fix | 2 (003 hover/menu-open, 020 contact redirect) |

## Deferred to Phase 6 exclusion list

- `/pages/faq` — merchant-created content gap, not theme bug.
- Customer-account flows (a03-a05) — no logged-in session in this sprint. Verify manually before Phase 6 push.

## Key findings for T4 to act on

**P0**: Fix the footer Sign Up button text visibility (contrast 1:1 → needs ≥4.5:1 for WCAG AA). One-line change to `custom.css:1676-1679`.

**P1**: Add `:focus-visible` outline to keyboard-focused elements. One new rule in custom.css targeting `a:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible`.

Both fixes are pure-CSS, non-structural, and can land in a single commit per fix. Neither requires admin rewiring.
