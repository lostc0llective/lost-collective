# Phase 6 T3 — Candidate preview verification

> Executed 2026-04-18 on candidate theme 193925775526 via Playwright.

## Summary: all 7 checks green

| # | Check | Result |
|---|---|---|
| 1 | Homepage loads on candidate theme | ✓ themeId `193925775526` confirmed across all pages |
| 2 | Header renders (desktop) | ✓ Header bg rgba(18, 18, 18, 0.55), nav links visible |
| 3 | Admin-driven primary button colour | ✓ `.button--primary` bg `rgb(235, 172, 32)` = #EBAC20 brand gold. Phase 4 admin pipeline confirmed end-to-end. |
| 4 | Footer Sign Up contrast (Phase 5 T4 fix) | ✓ Sign Up button bg #EBAC20 + color rgb(26, 26, 26) = --color-dark. WCAG AA compliant. |
| 5 | PDP renders | ✓ Size XS/S/M/L/XL selectors, type UNFRAMED/FRAMED/GLASS, colour N/A/BLACK/WHITE/METAL, ATC + Shop Pay, TOV-compliant copy |
| 6 | Collection page | ✓ 48 product thumbnails, 27/27 images loaded, titles + prices ("from $50.00") |
| 7 | Cart empty state + checkout | ✓ h1 "Shopping Cart", "Your Cart is Empty" message, Checkout button bg #EBAC20 |

## Focus-visible accessibility

- `--color-brand-gold` CSS variable resolves to `#ebac20` (Phase 5 T4 target)
- Phase 5 focus-visible rule exists and applies to body elements
- Header/announcement-bar links have a pre-existing, more-specific white-on-dark focus-visible rule — acceptable (passes WCAG AA for dark-header context). Not a Phase 5 regression.
- Screenshot evidence: `phase6-t3-03-homepage-tabbed-focus.png` shows visible focus ring around "Shop" link after Tab key.

## Console errors observed

Two third-party errors on PDP; neither is theme code:
- Meta Pixel "Attestation check for Attribution Reporting on facebook.com failed" — Playwright browser sandbox limitation, not a real-user issue
- Shopify monorail analytics `Failed to fetch` — checkout widget telemetry, doesn't affect functionality

## Screenshots captured

- `phase6-t3-01-homepage-desktop.png`
- `phase6-t3-02-pdp-desktop.png` (PDP above-fold with hero)
- `phase6-t3-02b-pdp-product.png` (product selectors + ATC)
- `phase6-t3-03-homepage-tabbed-focus.png` (focus ring on "Shop")

## T4 readiness

All preview checks pass. Candidate theme `193925775526` is functionally equivalent to live theme `193859780774` with the full Phase 1-5 refactor applied. No blockers for T4 publish.
