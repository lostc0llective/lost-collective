# Phase 7 — Fix + Uplift Catalogue

**Date:** 2026-04-19
**Source:** `PHASE7-VISUAL-AUDIT.md` (Sprint A audit output)
**Purpose:** Prioritised fix queue for Cowork to design Sprint B/C/D prompts from

## Priority legend

- **P0** — customer-visible conversion blocker / brand damage. Fix first.
- **P1** — broken or incomplete but not directly conversion-blocking.
- **P2** — uplift / polish / design-system foundation.

## Root-cause legend

- `FX` — Flex v5.5.1 upstream regression (Flex changed class contract / DOM structure)
- `P2T` — Phase 2 hex→var migration gap (missing var fallback or stale hex)
- `P3I` — Phase 3 !important scope-tightening over-deleted a load-bearing rule
- `P1D` — Phase 1 dead-code deletion over-deleted
- `P6P` — Phase 6 bulk-push partial-damage (file missing or stale on theme)
- `PRE` — pre-existing, independent of phases
- `ADM` — Shopify Admin-side, not theme-code
- `NEW` — active uplift, no existing rule to fix

---

## P0 — Fix first (conversion-critical or brand-critical)

**Status key:** ✅ shipped live 2026-04-19 Sprint A5 • ⬜ still open for Sprint B

| # | Status | Finding | Root-cause bucket | Files | Notes |
|---|---|---|---|---|---|
| P0-1 | ⬜ | PDP metafields not rendering (`custom.collection_series`, `print_technique`, `paper_type`, `certificate_included`, `location`, `year_photographed`, `subject_description`) | Code-side confirmed — all 12 definitions exist on admin via GraphQL `metafieldDefinitions(ownerType: PRODUCT)` | `sections/product__main.liquid`, `snippets/product.liquid`, new LC metafield-block snippet | **A3 resolved root-cause**: admin side clean, Liquid render chain doesn't include metafield block. Needs new snippet authored in Sprint B |
| P0-2 | ✅ | Trust bar no icons + no rotation | Phase-x edit or Flex upstream: block schema stores `block.settings.icon` but liquid read `block.settings.icon_library` — variable-name mismatch | `sections/footer__icon-bar.liquid` | Fixed icon var name + added CSS marquee rotation (doubled DOM pass, keyframes, 45s loop, hover-pause, prefers-reduced-motion respected) |
| P0-3 | ✅ | Testimonial block — images 100×100 | Flex default `max-width: 100px` avatar treatment at `theme.css.liquid:17700`; LC customer photos are horizontal compositions not avatars | `assets/custom.css` override | Unstuck from absolute, natural aspect, `object-fit: contain`, block restructured as flex column (image first, quote second, name third) |
| P0-4 | ✅ | Instagram feed not edge-to-edge | `.section` class on inner `<section>` inherited Flex's 1200px max-width — same bug previously hit on logo-list + slideshow | `sections/index__instagram.liquid` | Class removed; inner section now 1440px full-viewport width |
| P0-5 | ⬜ | Slideshow text scrim inverted (white bg / dark text, should be dark bg / light text for editorial dark-hero treatment) | Shopify Admin theme-editor block setting | `templates/index.json` slideshow block settings | **Merchant action** — flip background_color to #0d0d0d + text colors to #f8f6f2 in Theme Editor → Slideshow → each slide block |
| P0-6 | ✅ | PDP breadcrumb overlaps sticky nav | Header height offset not applied to `.breadcrumb` on product template | `assets/custom.css` | Added `padding-top: calc(var(--lc-header-height, 120px) + 12px)` scoped to `#template-product .breadcrumb` |
| P0-7 | ⬜ | PDP variant picker visually flat (dark boxes, no LC brand treatment) | Phase 3 !important scope-tightening likely dropped LC-custom swatch styling; Flex base now wins | `snippets/options-radios.liquid`, `assets/custom.css` | Deferred to Sprint B — requires refined CSS (gold selected state, paper unselected, serif labels, proper unavailable handling). Functional now, just unstyled |
| P0-8 | ✅ | `assets/custom.css.backup` in repo being shipped as theme asset | Housekeeping — leftover from Phase 2 | — | `git rm`d locally; remote cleanup on next bulk push (Sprint E) |

### Sprint A5 summary

- **Shipped 5/8 P0s** to live theme `193925775526` on 2026-04-19 with per-fix verification at 1440: P0-2, P0-3, P0-4, P0-6, P0-8
- **Remaining 3 P0s:** P0-1 PDP metafields (substantial — new render chain), P0-5 slideshow scrim (merchant admin action), P0-7 variant picker styling (CSS polish, functional already)
- **Shopify edge-cache lesson**: live HTML serves stale up to 30-60 min post-push; verification must use `?preview_theme_id=<id>&_fd=0&_ab=0` on `lost-collective.myshopify.com` to bypass CDN

## P1 — Broken but not conversion-blocking

| # | Finding | Root-cause bucket | Files |
|---|---|---|---|
| P1-1 | Collection page — only 2 filters vs rich-metafield catalogue; needs faceted filters | ADM + NEW | Shopify Admin (install Search & Discovery) + `sections/collection__main.liquid` filter block wiring |
| P1-2 | Cart page hero image cluttered; title low-contrast | PRE | `templates/cart.json` or `sections/cart__banner.liquid` |
| P1-3 | Cart page no trust bar (free-shipping progress, authenticity, secure checkout) | NEW | `templates/cart.ajax.liquid` + new trust-bar snippet |
| P1-4 | Blog hero pill title — low contrast, weird scale | PRE | `sections/blog__banner.liquid` or banner block CSS |
| P1-5 | Blog post cards — no excerpts, minimal hierarchy | NEW | `sections/blog.liquid` + blog-card snippet |
| P1-6 | PDP price "$50.00" plain — no "From" prefix / no range / no tabular numerics | NEW | `snippets/product__price.liquid` or equivalent |
| P1-7 | Collection hero treatment generic (dark pill over product image) | NEW | `sections/collection__main.liquid` banner block |
| P1-8 | 32 `console.log`/`console.warn`/`console.debug` in asset JS | PRE | `assets/*.js`, `assets/*.js.liquid` |
| P1-9 | `assets/z__jsTestimonials.js` may be orphaned (testimonial section rebuilt) | PRE | Verify usage then delete |
| P1-10 | Sticky mobile ATC missing on PDP | NEW | PDP section + IntersectionObserver JS |
| P1-11 | Free shipping progress bar missing in cart drawer | NEW | `templates/cart.ajax.liquid` |
| P1-12 | Secure-checkout lock icon on PDP (toggle exists but may not render) | NEW / ADM | `settings_data.json` (`show_lock_icon: true` confirmed) + snippet wiring |
| P1-13 | Missing trust signals on PDP (authenticity, numbered edition X of Y, shipping guarantee) | NEW | PDP side panel |
| P1-14 | Crossed-out colour swatches look like "sold out" — unavailable-combination UX needs rethink | NEW | `snippets/options-radios.liquid` + swatch-availability CSS |
| P1-15 | Inconsistent section wrapper pattern (`instagram-feed` constrained to 1200px while `index__slideshow-classic` is 100vw) | NEW | Define canonical `lc-section-full` + `lc-section-contained` utility classes in `assets/custom.css` and apply per section liquid |
| P1-16 | PDP "Size Guide" — unclear if this is a link, button, popover | PRE | PDP side panel; enhance interaction |

## P2 — Uplift / polish / design-system

| # | Finding | Root-cause bucket | Files |
|---|---|---|---|
| P2-1 | No design-token CSS hierarchy — establish `--lc-space-*`, `--lc-type-*`, `--lc-color-surface-*`, `--lc-radius-*`, `--lc-motion-*` | NEW | `assets/custom.css` — add `:root` token block at top |
| P2-2 | No font strategy — adopt serif display (e.g. GT Sectra, Canela) + body sans (e.g. Söhne, Basis Grotesque) with `font-display: swap` + preload | NEW | `snippets/head.fonts.liquid` (new), `layout/theme.liquid` (preload tags), `assets/custom.css` |
| P2-3 | No motion system — orchestrated page-load reveal (staggered section fade-in), hover micro-states, `prefers-reduced-motion` respected | NEW | `assets/custom.css` + small new `assets/lc-motion.js` if IntersectionObserver needed |
| P2-4 | Section vertical-rhythm inconsistent — apply `--lc-space-*` scale for section padding-top/bottom | NEW | Every `sections/index__*.liquid` — standardise padding vars |
| P2-5 | Blog titles render heavy-bold-uppercase-sans — switch to serif titlecase with decorative rule | NEW | `sections/blog.liquid` + CSS |
| P2-6 | Collection tile hover state — overlay price + quick-look chip on hover | NEW | `snippets/list.product-card-basic.liquid` + CSS |
| P2-7 | Subtle film-grain texture on dark hero sections + warm paper texture on product-page whitespace | NEW | `assets/custom.css` background layered gradients + SVG noise |
| P2-8 | Tabular numerics for prices + edition numbers | NEW | CSS `font-variant-numeric: tabular-nums` on price + metafield elements |
| P2-9 | Product card title case + rule decoration ("Yummy | Landscapes" → serif title on top, small-caps subtitle below) | NEW | Product card snippet + CSS |
| P2-10 | Breadcrumb typography treatment — small caps + chevron separator | NEW | `sections/product__breadcrumb.liquid` + CSS |
| P2-11 | Consent Mode v2 wiring + dataLayer `view_item` / `add_to_cart` / `purchase` | NEW | `layout/theme.liquid`, `assets/z__jsCart.js`, order-confirmation script |
| P2-12 | Shopify Admin merchant actions (Search & Discovery install, slideshow block admin edits) | ADM | Brett |
| P2-13 | Address 5 remaining `TODO:` comments in `snippets/head.styles.settings-color.liquid` | PRE | File-level refactor |
| P2-14 | Introduce Figma design system as source-of-truth (optional) | NEW | Figma file + `figma-create-design-system-rules` skill |

---

## Sprint structure recommendation

- **Sprint B** (next CC session) — execute ALL P0 items. Evidence-before-completion on each. Batch push to live. Close out only after screenshot diff proves every P0 fixed.
- **Sprint C** — execute P1 items, plus Pillar 2 Performance + Pillar 3 Conversion audits. Introduces cart trust bar, sticky mobile ATC, free-shipping progress. Meanwhile run the remaining template audits (customer/*, page.*, search, 404, password, gift-card).
- **Sprint D** — Pillar 1 Security + Pillar 4 SEO code-level audits. P2-1 through P2-10 — establish the design system tokens, fonts, motion, spacing rhythm. This is where "boutique-agency uplift" actually lands.
- **Sprint E** — Ops close-out: P2-11 analytics, `.shopifyignore` verification, dead-asset cleanup. Merge `feat/flex-migration` → `main`. Archive Phase 6 + 7 audit/. Retrospective.

## Out-of-scope reminders

- Shopify-hosted checkout is NOT editable on non-Plus plans beyond the deprecated `checkout.liquid`. If Brett's "checkout broken" report stems from a non-theme issue, it needs Shopify Plus ($2,300/mo) to customise.
- Redesigning logo / nav IA / footer IA is explicitly out of scope.
- Any merchant-action item (ADM bucket) surfaces in the merchant-action list for Brett to execute in Shopify Admin.
