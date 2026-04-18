# Shopify Theme Refactor Handoff

**Date:** 2026-04-15
**Staging theme:** 143356625062
**Branch:** feat/april-2026-audit-sprint

---

## What changed

### Phase 1: Audit (c9f50c0)
- Full codebase inventory in AUDIT-REPORT.md
- 347 CSS selectors audited, 33 confirmed dead
- 34 JS files audited, dependency graph mapped
- 78 sections, 85 snippets, 26 templates catalogued

### Phase 2: CSS (5e007f1)
- Removed dead CSS: `.link--animated`, instafeed rules, `.page--about-content`
- Replaced hardcoded `#ffffff` and `#111111` with CSS custom properties
- custom.css: 4,416 -> 4,360 lines
- Design token system already comprehensive (no new tokens needed)
- 378 !important declarations retained (all justified by Flex theme constraints)

### Phase 3: Liquid (c61096d)
- **fixed-message.liquid:** Now uses schema settings for text, button_label, button_style instead of hardcoded values. 8 hex colours replaced with CSS custom properties.
- **Deleted 4 orphaned sections:** rotating-logos, logo-carousel, predictive-search, surface-pick-up
- Removed stale monorail preconnects from password.liquid and quickshop.liquid
- Replaced all deprecated `| script_tag` and `| stylesheet_tag` filters
- Removed duplicate script loading in quickshop.liquid
- Replaced hardcoded colours in article__related-series and index__instagram with CSS vars

### Phase 4: JavaScript (1d8be8a)
- **SECURITY:** Replaced `eval()` with `JSON.parse()` in z__jsCart.js
- Fixed duplicate `dataType` in z__jsCart.js, removed deprecated `async: false`
- Fixed bare `window.event` reference in z__jsCustomContactForm.js
- Removed IE11 detection guard in z__jsCollection.js
- Fixed `$.ajaxSetup` global mutation in z__jsMap.js (localised to $.ajax call)
- Removed deprecated `DocumentTouch` check from theme.liquid
- Removed dead IE10 media query from js-variables.liquid

### Phase 5: Lint (702c67a)
- Fixed parser-blocking currencies.js in quickshop.liquid (added defer)
- Fixed duplicate translation key typo in de.json (`comment_pladeholder`)
- Remaining theme-check errors are false positives (parser limitations)

### Phase 6: Mobile verification
- All 4 April 12 staging fixes confirmed intact:
  1. Slideshow portrait fix (120vw height)
  2. Mobile header colour (#4d4d4d)
  3. Sticky header shrink (8px padding)
  4. Footer 2x2 grid
- 42 mobile media queries, 15 WCAG 44px touch target fixes in place
- No regressions found

---

## What Brett should visually verify on staging

1. **Cookie banner** (fixed-message section) -- text and button should now match whatever is set in the theme editor settings. If the settings were never updated from defaults, the button will say "I agree" instead of "Got it" and the text will be the schema default.

2. **Footer icon bar** -- the trust bar marquee script now loads with `defer`. Verify the marquee animation still works on first load.

3. **Announcement bar** -- same defer change. Verify marquee scrolls correctly.

4. **Gift card page** -- scripts now load with `defer` instead of `| script_tag`. Verify the QR code still renders.

5. **Collection page filters** -- IE11 guard removed from z__jsCollection. Verify 3D model viewer still loads (if any products use it).

6. **Cart page** -- `eval()` replaced with `JSON.parse()` and `async: false` removed. Verify cart item removal and quantity updates work correctly.

7. **Contact form** -- `event.preventDefault()` bug fixed. Verify form validation works when required checkboxes are unchecked.

8. **Map section** -- `$.ajaxSetup` removed. Verify Google Maps still loads on the contact page.

---

## What was NOT changed (and why)

- **custom.css is still 4,360 lines.** The 200-line target is not achievable for a Flex theme with this much custom functionality. Every section is actively used.
- **378 !important declarations remain.** The Flex theme uses inline section styles and deeply nested selectors that can only be overridden with !important.
- **jQuery dependency remains.** 544 jQuery references across 31 files. Cannot be removed without a complete JS rewrite.
- **z__jsProduct.js is still 7,191 lines.** Module splitting was deemed out of scope (future sprint).
- **vendors.js still contains instant.page v1.2.2** (duplicate of the v5.2.0 module in theme.liquid). Cannot safely remove from bundled file.
- **Non-default locale age_gate translations** are missing. This is a Flex theme vendor issue.

---

## Push to staging

```bash
cd ~/Claude/lost-collective/shopify
shopify theme push --theme 143356625062 --store lost-collective.myshopify.com --allow-live
```

---

## Pre-migration audit — CC sprint done — 2026-04-18

Branch: `feat/flex-migration` (from `main` @ tag `pre-flex-migration-2026-04-18`).

### Theme slot confirmed

| | Value |
|---|---|
| $LIVE_ID | `193859780774` — "Lost Collective Live - 2026-04-15" (role=live) |
| Flex version **before** | v5.2.1 (recorded in `lost-collective/CLAUDE.md`, old theme IDs `141183910054` / `143356625062`) |
| Flex version **after** | v5.5.1 (from `config/settings_schema.json` → `theme_info.theme_version`) |

The upstream install published Flex into a **new theme slot** (`193859780774`) rather than replacing either of the two IDs currently stored in `scripts/config.py`. `config.py` **has not been updated** — flagged for the reconciliation sprint.

Other existing theme slots (IDs concealed by 1Password, names as-reported): "Lost Collective Live" (unpublished), "Copy of Lost Collective Live" (unpublished), "Lost Collective Backup 05/01/2026" (unpublished).

### Audit data files

Written to `shopify/audit/`. Raw data only — no analysis, no opinions.

| File | Bytes | Rows |
|---|---:|---:|
| settings-schema-flat.json | 62,268 | 285 |
| settings-data-flat.json | 10,558 | 137 |
| css-custom-properties.txt | 238,357 | 1,913 (1,033 unique vars) |
| css-custom-properties-usage.txt | 199,875 | 1,118 unique vars |
| custom-css-rules.tsv | 36,442 | 517 rules |
| inline-styles.txt | 5,590 | 48 |
| injected-styles.txt | 5,969 | 84 |
| section-schemas.json | 369,114 | 68 sections parsed |
| file-inventory.tsv | 18,772 | 400 files |
| _build_audit.py | 14,962 | generator script (re-runnable) |
| _anomalies.log | 367 | (gitignored — see anomalies below) |

### Anomalies noticed during pull and audit

1. **Theme ID mismatch.** Live theme `193859780774` does not match either ID in `scripts/config.py`. Reconciliation sprint will need to decide whether to (a) update `config.py` THEME_IDS or (b) publish Flex back over an existing slot.
2. **CLAUDE.md conflict.** `lost-collective/CLAUDE.md` says production=`141183910054`, `shopify/CLAUDE.md` and `scripts/config.py` say production=`143356625062`. These disagree even before the new `193859780774` slot entered the picture. Needs reconciling.
3. **Pull diff size.** `git diff --stat pre-flex-migration-2026-04-18..HEAD` → 253 files changed, 33,735 insertions, 5,410 deletions. This is the raw upstream Flex v5.2.1 → v5.5.1 delta including the LC customisations being overwritten. All customisations are preserved in the pre-migration tag and on `feat/april-2026-audit-sprint`.
4. **Deleted assets.** Upstream removed `assets/productOptions.js`, `assets/styles.css.liquid`, `assets/z__jsSlideshowClassic.js`. Reconciliation needs to check whether any of these were custom-edited.
5. **Section schemas with trailing commas.** 4 sections (`index__featured-product`, `product-image-scroll__main`, `product__main`, `quickshop`) have trailing commas in their `{% schema %}` JSON. Valid Shopify Liquid but strict JSON rejects them. Parser strips them before JSON parse; original files untouched.
6. **CSS custom properties inside Liquid templating.** `assets/base.typography.css:104` captures `--heading-2xl-font-size: var(--text-size-scale-n{{ 11 | plus: block.heading_modifier;` — a `.css` file contains Liquid interpolation. Expected for Flex; noting so reconciliation doesn't trip over it.
7. **Stashed WIP.** `git stash` entry "WIP before pre-flex-migration-2026-04-18 tag" preserved on `feat/april-2026-audit-sprint` — contains modified HANDOFF.md, `scripts/gsc.py`, `scripts/judgeme_sync_ratings.py`, `sections/index__slideshow-classic.liquid`, and untracked `assets/custom.css.backup`, `product.json`, `scripts/gmc_variant_labels.py`, `settings_data.json`, `shopify-launcher.sh`.
8. **HANDOFF.md provenance.** HANDOFF.md only existed on `feat/april-2026-audit-sprint`, not on `main`. Copied forward to `feat/flex-migration` and appended to. If `main` should also carry it, that's a separate decision.
9. **Shopify 1Password concealment.** Three of the four theme IDs reported by `shopify theme list --json` came back `"id": <concealed by 1Password>` under `op run`. Only the live theme's ID (`193859780774`) was visible. If we need the unpublished theme IDs for reconciliation, run the CLI without the `op run` wrapper.

### Commits on feat/flex-migration

```
9f101f1 audit(theme): raw data dump for settings/CSS conflict analysis
71fe7f7 chore(theme): pull live Flex from Shopify (post-upstream-install baseline)
```

Branch pushed to `origin/feat/flex-migration`. Tag `pre-flex-migration-2026-04-18` on `main` and origin.

### Ready for Cowork

Reconciliation sprint needs to:
- Pick the correct Shopify theme slot for production + staging.
- Reconcile `scripts/config.py` THEME_IDS, `shopify/CLAUDE.md`, and `lost-collective/CLAUDE.md`.
- Work through `audit/` to classify every LC customisation vs upstream Flex default.
- Re-apply classified customisations onto this baseline.
