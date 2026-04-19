# Phase 7 — Mobile 375 Audit (Sprint B Task B7)

**Date:** 2026-04-19
**Theme:** `193925775526` (LC Flex Production Candidate 2026-04-18)
**Viewport:** 375 × 812 (iPhone X-class)
**Verification URL:** `https://lost-collective.myshopify.com/?preview_theme_id=193925775526&_fd=0&_ab=0`
**Scope:** Verify B1–B6 changes render cleanly at 375 across the five highest-traffic templates. Document any regressions; fix in source.

## Summary

Five templates audited. No horizontal scroll, no clipped text, no Sprint-B regressions surfaced at 375. All Sprint B components (PDP metafields, variant picker, price treatment, lock icon, sticky ATC, cart trust bar, cart hero scrim) verified visible and functional at mobile.

| # | Template | Severity | Finding | Source | Action |
|---|---|---|---|---|---|
| 1 | Homepage | LOW | "Shop Best Sellers" / "Browse Collections" buttons are 40-41px tall (under 44px touch target) | `sections/index__*.liquid`, button styling | Pre-existing, not Sprint B regression. Defer to Sprint D as part of touch-target sweep. |
| 2 | Homepage | INFO | Trust icon bar `.icon-bar__track` and logo marquee compute 1959px / 4716px wide | Intentional CSS marquee tracks, parent has `overflow:hidden`. Not horizontal scroll. | None. |
| 3 | PDP | PASS | All LC components present: `.lc-metafields`, `.lc-sticky-atc`, `.lc-price-block`. Swatches at 48px height. | `snippets/lc-product-metafields.liquid`, `snippets/lc-sticky-atc.liquid`, etc. | None. |
| 4 | PDP | PASS | Sticky mobile ATC reveals on scroll past in-flow ATC; hidden on initial load. | `assets/z__lcStickyAtc.js` | None. |
| 5 | PDP | PASS | Variant picker editorial label renders `SIZE · XS` in Lato. Type toggle preserves layout (no jump). | `snippets/options-radios.liquid`, `assets/custom.css` section 44 | None. |
| 6 | Collection | PASS | "PRODUCTS" hero pill renders. Filter and sort dropdowns full-width and tappable. Two product cards per row. | `sections/collection__main.liquid` (Sprint A change held) | None. |
| 7 | Cart | PASS | LC trust bar stacks vertically (single column), three rows visible above PRODUCTS table. Progress bar 33% (cart $50 vs threshold $150). | `snippets/lc-cart-trust-bar.liquid`, `assets/custom.css` section 48 | None. |
| 8 | Cart | PASS | Cart hero `.banner__heading` "Shopping Cart" renders white (`rgb(255,255,255)`) over a dark scrim with text shadow. AA contrast. | `assets/custom.css` section 49 | None. |
| 9 | Blog | LOW | Blog hero pill title contrast remains low (pre-existing, P1-4 in Sprint A catalogue). | `sections/blog__banner.liquid` | Out of Sprint B scope (P1-4 deferred to Sprint C). |
| 10 | Blog | PASS | Blog post cards render serif title, date, read-time. No horizontal scroll. | `sections/blog.liquid` | None. |

## Per-template detail

### Homepage (`/`)

- Document scrollWidth = 375 (no horizontal scroll).
- Trust bar marquee + logo marquee are intentionally wide; parents clip via `overflow:hidden`.
- 40 sub-44px tap targets identified — all are inline nav/footer links (typical for the theme's link styling). Not Sprint B work.
- Screenshot: `audit/sprint-b-evidence/b7-home-375.png`

### Product Detail Page (PDP) (`/products/hotel-motel-101-3-sisters-motel-sign`)

- Document scrollWidth = 375.
- LC PDP metafields render in single-column stack with hairline rules.
- LC variant picker: 5 size swatches at 48px height, 3 type swatches, Colour fieldset preserves layout when hidden (no ATC jump).
- LC price block: `$50.00 – $2,500.00 AUD` with tabular numerics.
- LC ATC lock icon visible inside the Add-to-cart button.
- LC sticky ATC reveals correctly on scroll-past (verified independently in B5).
- Screenshot: `audit/sprint-b-evidence/b7-pdp-375.png`

### Collection (`/collections/all`)

- Document scrollWidth = 375.
- Hero "PRODUCTS" pill, breadcrumb, product type and sort dropdowns all rendering.
- Two product cards per row at this width.
- Pre-existing P1-1 (faceted filtering) remains a merchant action / Sprint C item.
- Screenshot: `audit/sprint-b-evidence/b7-collection-375.png`

### Cart (`/cart`)

- Document scrollWidth = 375.
- LC trust bar stacks vertically with all three rows: shipping progress, authenticity, encrypted-checkout.
- Progress bar fills proportionally based on `cart.total_price` vs `settings.free_shipping_threshold`.
- Cart hero title `Shopping Cart` renders white over a dark gradient scrim.
- Screenshot: `audit/sprint-b-evidence/b6-after-375.png` (captured in B6).

### Blog (`/blogs/blog`)

- Document scrollWidth = 375.
- Pre-existing pill title (P1-4) still present — not in Sprint B scope.
- Post cards render with title, date, read-time.
- Screenshot: `audit/sprint-b-evidence/b7-blog-375.png`

## Regressions surfaced from B1–B6 at 375

None. All Sprint B work renders cleanly at 375 with no horizontal overflow, no clipped text, and 48px+ tap targets on net-new interactive elements (variant swatches, sticky ATC button, trust bar progress).

## Deferred to later sprints

- Homepage CTA tap targets (40-41px tall) — Sprint D touch-target pass.
- Blog hero pill (P1-4) — Sprint C blog uplift.
- Collection page faceted filtering (P1-1) — merchant action + Sprint C.
