# Phase 7 — Visual Render Audit

**Date:** 2026-04-19 (Sprint A)
**Auditor:** CC via `shopify-theme-audit` skill (Pillar 0 visual + Pillar 5A dev-workflow) and `frontend-design` aesthetic direction
**Theme under audit:** `193925775526` "LC Flex Production Candidate 2026-04-18" (live)
**Viewport captured:** 1440 × 900 desktop baseline; mobile (375) pass queued for Sprint B

**Scope note:** Sprint A captures the highest-traffic templates Brett flagged. `customers/*`, `page.*`, `search`, `404`, `password`, `gift_card` deferred to Sprint B.

---

## Homepage — Findings

| Severity | Element | Symptom | Evidence | Root-cause hypothesis |
|---|---|---|---|---|
| **CRITICAL** | Trust icon bar | No SVG icons rendering; no horizontal rotation/marquee | `[id*=trust_icon_bar]` → 4 `<p>` items, zero inner `<svg>` / `[class*=icon]`; `animationName: none` on container + inner | Phase 1 dead-code deletion likely removed the icon-rendering block; OR Flex v5.5.1 upstream changed `sections/footer__icon-bar.liquid` contract away from the LC-custom icons |
| **CRITICAL** | Testimonial block | Images rendering 100×100 px despite 2400×2398 source | `.testimonial__image` computed `max-width: 100px; width: 100px` | CSS `max-width: 100px` override active; not picked up by Phase 3 !important scope-tightening survey |
| **HIGH** | Slideshow text overlay | White 77%-opacity background + dark text — inverted vs intended dark/light editorial treatment | Inline `style="background-color: rgba(255, 255, 255, 0.77)"` on `.slideshow-slide__content`; heading `rgb(42,42,42)`, body `rgb(111,111,111)` | Section block setting `background_color: #FFFFFF` + `background_opacity: 77` persisted in `templates/index.json` → inline-style. Schema default is white; admin never flipped to dark |
| **HIGH** | Instagram feed | Constrained to 1200 px max-width (centered, not edge-to-edge) | Outer `#shopify-section-*` = 1440 px × 0 x; inner `<section class="instagram-feed section">` = 1200 px × 120 x with `max-width: 1200px` | `.section` class inherited Flex's container max-width, same pattern as the earlier logo-list / slideshow regressions. Fix = remove `.section` from inner wrapper, add explicit 100vw breakout |
| **MEDIUM** | Slideshow image radius | Rounded corners applied (16 px) but vs other "big photo sections" the inset + radius treatment is inconsistent | Slideshow slide padding `0 12px`, radius 16 px; `image_with_text_overlay` sections have `firstImgRadius: 0px` — edge-to-edge with no radius | Inconsistent styling across "hero image" section types. Needs design-system decision: either all hero sections get the inset+rounded treatment, or the slideshow returns to edge-to-edge |
| **LOW** | Section vertical rhythm | Rich-text sections 270–329 px tall; gaps between sections feel uneven | Section heights captured: video 810, trust 83, rich-text 300, overlay 760, featured 535, logo 60, rich-text 270, collection-list 499, overlay 760, rich-text 329, featured 535, testimonial 525, slideshow 721, ig 580 | No spacing-rhythm system; each section has its own padding defaults. Uplift: introduce section-spacing scale (e.g. 48/64/96 px) and apply consistently |

## Product template (PDP) — Findings

Tested URL: `/products/hotel-motel-101-3-sisters-motel-sign`

| Severity | Element | Symptom | Evidence | Root-cause hypothesis |
|---|---|---|---|---|
| **CRITICAL** | PDP metafields | `custom.collection_series`, `print_technique`, `paper_type`, `certificate_included`, `custom.location`, `custom.year_photographed`, `custom.subject_description` do NOT render anywhere on PDP. Only one `.accordion` (Editions & Collectibility) found | `metafield_text_probes: {hasCollectionSeries:false, hasPrintTechnique:false, hasPaperType:true (matches plain word), hasCertificate:false, hasYear:false, hasSubjectDesc:false}` | Either (a) the snippet rendering metafield blocks was deleted in Phase 1 dead-code sweep or never migrated from pre-Flex, OR (b) Flex v5.5.1 upstream replaced the PDP structure so the LC-custom metafield blocks aren't wired in. Requires file-level investigation in Sprint A3 via `shopify-custom-data` skill |
| **HIGH** | Variant picker style | Buttons render but look flat/generic — dark boxes, no paper-white card surface, no gold accent, no refined spacing | 3 fieldsets (Size×5, Type×3, Colour×4) rendering at 40–95 px wide × 42 px tall. `.swatch-element` computed `backgroundColor: rgb(26,26,26)`, `border: 1px solid rgb(0,0,0)` | Phase 3 !important scope-tightening likely dropped LC-custom swatch styling; base Flex styling now wins. Variant buttons exist — the VISUAL is what's gone, not the DOM |
| **HIGH** | Crossed-out colour swatches | When Type=Unframed is selected, Colour options Raw/White/Black render with strikethrough (correct availability logic) but visually read as "sold out" | `.crossed-out` span inside swatch labels for unavailable combinations | Default Flex styling on unavailable swatches. Needs design decision: hide unavailable vs show disabled vs keep strikethrough but restyle |
| **HIGH** | Breadcrumb overlaps nav | Breadcrumb "Home > All > 3 Sisters Motel Sign..." sits in the same vertical band as the main nav items, visually colliding | Screenshot `audit-pdp-variant.png` | Nav is sticky + transparent; breadcrumb z-index or top-margin isn't offsetting for the sticky nav height |
| **MEDIUM** | Price display | "$50.00" rendered as single line — no "From" prefix; no range ($50–$2500); no tabular numerics | Inspection of `.price` area | Product has 25 variants spanning $50–$2500. Single price misrepresents catalogue depth |
| **MEDIUM** | Missing trust signals | No secure-checkout badge, no authenticity/numbered-edition callout, no shipping guarantee | None in viewport captured | Conversion layer missing. Per Pillar 3 remediation list: `show_lock_icon`, `notify_me_form`, edition-scarcity (`X of Y remaining`) |

## Collection template — Findings

Tested URL: `/collections/all`

| Severity | Element | Symptom | Evidence | Root-cause hypothesis |
|---|---|---|---|---|
| **HIGH** | Faceted filtering | Only two dropdowns: "All Products" (type switcher) + "Alphabetically: A-Z" (sort). No filters by collection series, size, price range, in-stock, type, colour | Screenshot `audit-collection-1440.png` | Shopify Search & Discovery app not configured / theme's faceted filter block not present. Merchant action. Per Pillar 4 — big SEO + UX miss with a 1,809-product catalogue |
| **MEDIUM** | Hero banner treatment | Background image (jail cell / blue overalls?) with dark pill "PRODUCTS" title — generic vs editorial. Doesn't signal "fine art prints catalogue" | Same screenshot | Collection hero schema accepts banner image + text overlay. Current content / composition is the issue, not code. Can be uplifted: full-bleed image, large serif title, short 1-line collection tagline |
| **MEDIUM** | Product card treatment | Tiles render in 4-up grid, white-frame variant image visible (variant fix from earlier sprint holding), but no price / title visible on first-scroll, no hover affordance | Screenshot | Card info is below-fold of tile. Uplift: overlay price on hover, serif-styled title, subtle scale/overlay on hover |
| **LOW** | "Page 1 of 76" | Honest but implies catalogue is deep — could be reframed as e.g. "1,809 prints across 62 series" | Screenshot | Copy + template output. Small uplift |

## Cart template — Findings

Tested URL: `/cart`

| Severity | Element | Symptom | Evidence | Root-cause hypothesis |
|---|---|---|---|---|
| **HIGH** | Hero treatment | Cluttered photo collage with "Shopping Cart" title rendering at low contrast — dark title on mixed light/dark busy background, nearly illegible | `audit-cart-1440.png` | Banner section image choice + title-on-image without scrim. Dark scrim / title treatment fix = small CSS edit |
| **HIGH** | No trust bar in cart | No free-shipping progress, no authenticity/numbered-edition re-assurance, no secure-checkout mark | Screenshot | Per Pillar 3 remediation: add cart drawer trust bar + free-shipping threshold progress |
| **MEDIUM** | Variant display in line item | "Size: XS / Type: Unframed / Colour: N/A" renders plain text — readable but unpolished. Could use dot-separated, smaller caps, muted colour | Screenshot | Cart line-item template. Typography polish |
| **LOW** | Quantity stepper | `–  [1]  +` stepper rendering but buttons look like default Flex grey boxes | Screenshot | Default Flex styling; uplift with LC-brand styling |

## Blog template — Findings

Tested URL: `/blogs/blog`

| Severity | Element | Symptom | Evidence | Root-cause hypothesis |
|---|---|---|---|---|
| **HIGH** | Hero pill title | "Blog" rendered in a pale pill floating against a busy photo — low contrast, weird scale | `audit-blog-1440.png` | Banner block default styling. Pill → clean serif title in dark scrim, or just remove pill and use large serif hero |
| **MEDIUM** | Post cards — no excerpts | Only title + date + "2 min read", no preview copy to entice click-through | Screenshot | Flex default blog card. Article excerpt available via `article.excerpt`, not rendered. Boutique uplift: render excerpt + "Continue reading" link |
| **MEDIUM** | Titles all-caps heavy | Editorial intent is right, but rendered bold uppercase sans is heavy — a serif title cased normally would read more "photography-book", less "news website" | Screenshot | Blog-title CSS. Matches editorial direction but wrong font family |
| **LOW** | "Read more" CTA style | Appears as a yellow gold button cut off in screenshot — visually heavy below three lines of uppercase title | Screenshot | Small styling decision — could be a subtle underline link instead of a pill button |

## Pillar 5A — Dev Workflow (code-level)

| Severity | Location | Finding | Action |
|---|---|---|---|
| **MEDIUM** | `.shopifyignore` | Does NOT exclude `audit/`, `backups/`, `scripts/`, `docs/`, `HANDOFF.md`, `CLAUDE.md` at HEAD — these are in `.shopifyignore` on `feat/flex-migration` branch (commit `5bc691f`), need to verify current repo state vs expected | Confirm branch `feat/flex-migration` is correctly ignoring these; if not, re-apply |
| **MEDIUM** | `assets/*.js` and `assets/*.js.liquid` | **32 `console.log` / `console.warn` / `console.debug` statements** in asset JS | Remove debug logs; keep `console.error` in error paths |
| **LOW** | `debugger` statements | Zero found | PASS |
| **HIGH** | `assets/custom.css.backup` | Legacy backup file in `assets/` — will be pushed to theme as a valid asset on every bulk push, wastes bandwidth + storage quota | Delete `assets/custom.css.backup` |
| **MEDIUM** | `assets/z__jsTestimonials.js` | `z__` prefix implies legacy/archived Flex-bundled vendor file; testimonials section was rebuilt earlier but this JS is still being loaded | Audit whether still referenced by live section; delete if orphaned |
| **LOW** | `snippets/head.styles.settings-color.liquid` | 5 `TODO:` comments (Phase 4 cleanup deferred) | Resolve in Sprint E ops close-out |
| **LOW** | Render graph | Sampled 20 `render '<name>'` calls — all pointed at existing snippets (spot-checked). Full orphan sweep deferred | Defer to Sprint B |
| **LOW** | Hardcoded pixel IDs / API keys | None found in liquid or `config/settings_data.json` on spot-check — Phase 4 Meta env-var migration already completed | PASS |

## Merchant actions (not fixable in code, Brett to do in Shopify Admin)

| Priority | Where | Action | Why |
|---|---|---|---|
| HIGH | Shopify Admin → Apps → Search & Discovery | Install + configure faceted filters on collection page (filter by price range, size option, type option, colour option, availability) | 1,809-product catalogue without facets is a major UX + SEO loss. Enables "from $50" filtering, size-specific browsing, white-frame browsing, etc. |
| HIGH | Shopify Admin → Online Store → Preferences → Theme Editor → Slideshow section | Flip slideshow slide background from white (currently `#FFFFFF` @ 77%) to dark (e.g. `#0d0d0d` @ 55%) with white text | Currently inverted vs editorial direction — white scrim + dark text on dark hero imagery gives low contrast + clashes with other dark hero sections |
| MEDIUM | Shopify Admin → Products → 3 Sisters Motel Sign → Media | Ensure each variant whose image should differ has a media item tagged to that variant (white-frame variants now pull correctly; verify the same behaviour for framed-raw, framed-black, glass) | Carousel + cart line item + cross-sell all benefit |
| MEDIUM | Shopify Admin → Online Store → Themes → Customize → Collection → Hero banner | Replace "jail cell" hero image with a curated wide-shot + 1-line tagline ("1,809 prints across 62 series") | Current composition doesn't signal fine-art catalogue |
| LOW | Shopify Admin → Online Store → Themes → Customize → Blog → Hero | Remove pale pill title treatment, use large serif title + dark image scrim | Editorial polish |

## Systemic / cross-cutting findings

1. **No design-system token layer under current CSS.** Phase 2 migrated hex→var but vars point at per-section settings, not a coherent design-token hierarchy. Uplift Sprint D should introduce: `--lc-space-*` (4, 8, 16, 24, 32, 48, 64, 96 px scale); `--lc-type-display-*` / `--lc-type-body-*` (font family + size + letter-spacing composites); `--lc-color-surface-*` (dark, paper, ink, gold); `--lc-radius-*` (none, sm, md, lg); `--lc-motion-*` (timing, easing).
2. **No font loading strategy.** `Lato-Bold.woff2` + `Lato-BoldItalic.woff2` present in `assets/` but loading strategy (preload, `font-display: swap`, subset) not verified. Boutique uplift should establish: display serif (e.g. GT Sectra, Canela, or similar) + body sans (Söhne or Basis Grotesque) with proper preload + subset.
3. **No motion system.** Phase 5 adds `:focus-visible` rings (WCAG), but no orchestrated page-load reveal, no hover-state language, no `prefers-reduced-motion` respect verified outside the logo-list marquee.
4. **Inconsistent section "wrapper" pattern.** `instagram-feed` constrained by `.section` class to 1200px while `index__slideshow-classic` uses `#shopify-section-*` full-width + per-section inset. Earlier logo-list had same issue. Uplift: define "full-bleed hero" vs "contained content" wrapper classes explicitly in custom.css as the two canonical section shapes.
5. **Phase 6 push damage may be broader than `templates/index.json`.** Visual bugs across templates that "shouldn't be broken" are consistent with partial-push damage. Recommend running full integrity diff of live theme vs repo on `feat/flex-migration` as part of Sprint B.

## Deferred to Sprint B

- Mobile 375 pass across every template
- Customer templates (login, register, account, order, addresses, activate, reset)
- Page templates (default, banner, contact, details, faq, gallery, sidebar)
- Search template
- 404 / password / gift-card templates
- Full render-graph orphan sweep
- Pillar 1 Security (injected-code / credential / robots / schema)
- Pillar 4 SEO (canonical, meta-description fallback, pagination type, breadcrumb aria, Twitter card conditional)
- Pillar 2 Performance (CWV baseline via PageSpeed)
- Pillar 3 Conversion (sticky mobile ATC, free-shipping progress, cart drawer)
