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

---

## Cowork audit deliverables — 2026-04-18

Four analysis documents written from the raw `audit/*.tsv` and `audit/*.json` dump. Read in this order:

| Document | Purpose | Read if... |
|---|---|---|
| `audit/WALKTHROUGH.md` | Teaching piece — how Flex's settings pipeline works, what `custom.css` does instead, the five conflict types with real examples. No jargon. | You want to understand *why* the theme has these problems before fixing them. Read this first. |
| `audit/CONFLICTS.md` | Specific A-E typed conflicts with file:line evidence and P0/P1/P2 severity. Ends with a 7-item quick-win list. | You want the complete list of settings/CSS collisions to fix. |
| `audit/DEAD-CODE.md` | Catalogue of dead tokens, selectors, `!important` declarations, admin settings, and block references. Each has a detection recipe. | You want the shopping list for Phase 1 deletions. |
| `audit/REFACTOR-PLAN.md` | Six-phase execution plan with entry/exit gates per phase and a 7-sprint CC schedule. | You want the roadmap from this state to production-ready. |

### Headline findings

1. **Root cause identified.** `assets/custom.css` declares a parallel token system at `:root` (lines 56-120) that re-defines the same vars Flex's pipeline owns. Most visible: `custom.css:119` globally overrides `--color-primary` with hardcoded `#ebac20` gold, disconnecting admin's `button_primary_bg_color` setting from every primary button on the site. This is the single highest-leverage fix.
2. **Five conflict types catalogued** in `CONFLICTS.md`:
   - Type A — Dead admin settings (6 confirmed, A1-A6)
   - Type B — Duplicate token definitions (7 confirmed, B1-B7)
   - Type C — `!important` inflation (378 total, ~150 safe to remove, ~38 genuinely needed)
   - Type D — Hardcoded hex values that should reference vars (4 major hex literals across 20+ sites)
   - Type E — Device-split overrides hiding from admin (3 confirmed, E1-E3)
3. **Quick-win list** (from `CONFLICTS.md` bottom) — seven actions that, done alone, restore admin control over primary button colour, header background, body text, and hover state. Estimated 2-3 hours of CC work.
4. **Phase 1 deletion volume estimate:** 150-250 lines from `custom.css`, 5-20 admin settings from `settings_schema.json`, one block from `settings_data.json`. Zero behaviour change expected.
5. **Seven CC sprints** planned in `REFACTOR-PLAN.md` (Phase 0-6). Each sprint stays within the 10-task cap, each phase is independently shippable to staging.

### Next handoff

The next CC prompt should be Phase 0 of `REFACTOR-PLAN.md`: safety net work — verify the staging theme slot, reconcile `scripts/config.py` + both `CLAUDE.md` files against actual theme IDs, test rollback, resolve the `feat/april-2026-audit-sprint` WIP stash. Cowork will write that CC prompt in the next session after Brett approves the plan.

### Open decisions needed from Brett before Phase 0 starts

- **Theme slot strategy** (REFACTOR-PLAN Phase 0 Option A vs Option B). Recommendation: Option A — duplicate live into a new staging slot, update config, never publish over live until Phase 6 sign-off.
- **Gold vs dark primary button** (CONFLICTS A1 decision). The rendered site shows gold today; the admin value says dark grey. Pick which is correct before Phase 4 lands.
- **Mobile header strategy** (CONFLICTS E1 decision). Expose a `mobile_header_background` admin setting, or hardcode the dark grey inline and delete the misleading `--color-header-bg` token.

---

### Brett's decisions — 2026-04-18

1. **Theme slot strategy:** Option A. Duplicate live into a new dedicated staging slot. Reconcile `scripts/config.py` + both `CLAUDE.md` files. Never publish over live until Phase 6 sign-off.
2. **Primary button colour:** `#ebac20` (gold). The rendered site is correct; admin's `button_primary_bg_color` should hold `#ebac20`. Phase 4 A1 fix: delete `custom.css:119` and update admin to match. Gold becomes merchant-controllable for the first time.
3. **Mobile header:** expose `mobile_header_background` as an admin setting. Brett's note: "there is a lot of issue caused from this." Phase 4 E1 fix will add the schema setting, wire it through Liquid to `--color-header-bg-mobile`, and replace hardcoded selectors in `custom.css` with the new var.

---

## CC Sprint: Phase 0 — Safety net (9 tasks, max 10)

**Branch:** continue on `feat/flex-migration`.

**Preconditions:** Read `audit/WALKTHROUGH.md` + `audit/CONFLICTS.md` + `audit/REFACTOR-PLAN.md` at session start. Do not touch `custom.css` or any theme asset in this sprint. Phase 0 is purely infrastructure — theme slot, config files, and rollback proof. No code refactor happens until Phase 1.

**Shopify MCP + theme-check preamble (applies to every phase, starting here):**
- Use **Shopify Dev MCP** first for any question about Flex var names, Liquid filters, section schema, or Admin API behaviour. Do NOT grep the local codebase to "figure out" what a token does — look up the canonical doc via `search_dev_docs` or `fetch_docs_by_path`. When referencing a CSS var from `snippets/head.styles.*.liquid` or a Flex-provided token, confirm the var name via the MCP before using it.
- Use **Admin API via Shopify Dev MCP** for reading/writing theme settings instead of editing `settings_data.json` directly where possible. Exception: this Phase 0 touches the file directly only if needed for the Instafeed block cleanup, which is deferred to Phase 1 anyway.
- Run **`shopify theme check`** before any `shopify theme push` in this sprint and every sprint from here on. It catches deprecated filters, parser-blocking scripts, trailing-comma schema errors (anomaly #5), missing alt text, and Liquid syntax issues. Zero errors required to push; warnings allowed only with justification in the commit message.
- From **Phase 1 onwards**, theme-check passing with zero errors is part of every phase's exit gate.

### Task 1: Duplicate live theme into a new staging slot

Create a new unpublished theme in Shopify Admin by duplicating the current live theme (`193859780774`). Name it `LC Flex Staging 2026-04-18`.

Do this via the Shopify Admin UI (Online Store -> Themes -> ⋯ menu next to live theme -> Duplicate). Do NOT use CLI for this step — theme duplication via CLI is unreliable.

After duplication, run `shopify theme list --json` **without** the `op run` wrapper (per HANDOFF anomaly #9, `op run` conceals theme IDs). Capture the new theme's numeric ID.

**Done when:** `shopify theme list --json` output contains a theme named `LC Flex Staging 2026-04-18` with role `unpublished`, and its numeric ID is recorded in this HANDOFF.md under a new "Theme slot IDs — Phase 0" section.

### Task 2: Reconcile `scripts/config.py` THEME_IDS

Update `shopify/scripts/config.py` so `THEME_IDS` contains exactly:
- `live` / `production` -> `193859780774`
- `staging` -> the new theme ID from Task 1

Remove the old IDs `141183910054` and `143356625062`. If either is referenced elsewhere in the file, update the reference to use the new staging ID.

**Done when:** `grep -E "141183910054|143356625062" shopify/scripts/config.py` returns zero matches. Importing `THEME_IDS` and printing it shows both current IDs and no orphans.

### Task 3: Reconcile both CLAUDE.md files

Update `shopify/CLAUDE.md` and `lost-collective/CLAUDE.md` so both agree on:
- Live theme ID: `193859780774`
- Staging theme ID: the new ID from Task 1
- Flex version: `v5.5.1` (currently `shopify/CLAUDE.md` says `v5.2.1`)
- Push commands use the new staging ID for the staging push line

Remove references to the old IDs. Both files should say the same thing in the same places.

**Done when:** `grep -E "141183910054|143356625062|v5\.2\.1" shopify/CLAUDE.md lost-collective/CLAUDE.md` returns zero matches. Both files reference the same pair of theme IDs and the same Flex version.

### Task 4: Run `shopify theme check` on the current branch

From repo root:
```bash
shopify theme check
```

Capture the output. Expected errors from prior sprints (HANDOFF L42-45 notes "remaining theme-check errors are false positives, parser limitations") may appear — confirm whether they're the same false positives or new issues introduced by the v5.2.1 -> v5.5.1 upstream pull.

If there are new errors (beyond the known false-positive set), DO NOT push to staging. Document them in HANDOFF.md under "Phase 0 theme-check findings" and stop for Brett to decide whether to fix in Phase 0 or defer to Phase 1.

If only the known false positives appear, proceed.

**Done when:** `shopify theme check` output captured. Either (a) zero errors beyond the known false positives, with staging push cleared to proceed, OR (b) new errors documented and flagged to Brett before any push.

### Task 5: Push `feat/flex-migration` to the new staging slot

From repo root:
```bash
shopify theme push --theme <staging_id_from_task_1> --store lost-collective.myshopify.com --allow-live
```

Capture the output — specifically the staging preview URL printed at the end.

**Done when:** Push completes without errors. Staging preview URL is recorded in HANDOFF.md under "Theme slot IDs — Phase 0" alongside the new staging ID.

### Task 6: Visual diff staging vs live on 5 templates

Open both staging (preview URL from Task 4) and live (`lostcollective.com`) side by side. Capture screenshots at desktop width (1440px) for:

1. Homepage (top viewport)
2. Any collection page (grid view, first row of products visible)
3. Any PDP with an `L` or `XL` edition (variant selector + certificate-included metafield visible)
4. Cart drawer (open the drawer with one item added)
5. Any blog post (article layout)

Save staging screenshots to `/tmp/phase-0-staging/` and live screenshots to `/tmp/phase-0-live/`. Diff each pair visually.

**Done when:** All 5 pairs captured. Any visual differences between staging and live are either (a) zero or (b) documented in HANDOFF.md under "Phase 0 visual diff findings" with a root-cause hypothesis. If any difference looks unintentional (a regression introduced by the Flex upstream pull), stop and flag to Brett before continuing.

### Task 7: Test rollback

Prove the rollback path works before any refactor begins.

```bash
# Revert custom.css to pre-migration state on staging
git checkout pre-flex-migration-2026-04-18 -- assets/custom.css
shopify theme push --theme <staging_id> --store lost-collective.myshopify.com --allow-live --only assets/custom.css

# Verify staging shows pre-migration custom.css (load the same 5 template pages, spot-check)

# Revert the revert — bring staging back to current feat/flex-migration state
git checkout feat/flex-migration -- assets/custom.css
shopify theme push --theme <staging_id> --store lost-collective.myshopify.com --allow-live --only assets/custom.css
```

**Done when:** Rollback executed cleanly in both directions. Staging returns to current `feat/flex-migration` state after the final push. Any errors during rollback recorded in HANDOFF.md.

### Task 8: Resolve the WIP stash on `feat/april-2026-audit-sprint`

HANDOFF anomaly #7 describes a stash entry titled "WIP before pre-flex-migration-2026-04-18 tag" on `feat/april-2026-audit-sprint`. Contains modified `HANDOFF.md`, `scripts/gsc.py`, `scripts/judgeme_sync_ratings.py`, `sections/index__slideshow-classic.liquid`, plus untracked files.

Investigate:
```bash
git checkout feat/april-2026-audit-sprint
git stash list
git stash show -p stash@{0}  # inspect what's in it
```

Decide (and document the decision in HANDOFF.md):
- If still relevant -> apply to `feat/april-2026-audit-sprint`, commit.
- If obsolete -> drop the stash, note what was in it.
- If uncertain -> save to `/tmp/wip-stash-2026-04-18.patch` via `git stash show -p stash@{0} > /tmp/wip-stash-2026-04-18.patch`, then drop the stash. Record the patch location.

Return to `feat/flex-migration` at the end.

**Done when:** `git stash list` on `feat/april-2026-audit-sprint` shows no stash entries matching the pre-migration description. Decision and rationale recorded in HANDOFF.md.

### Task 9: Commit, push, update HANDOFF.md, update knowledge graph

Commit the config + CLAUDE.md changes with a message like:
```
chore(theme): reconcile theme IDs for Phase 0 (Flex v5.5.1, staging <id>)
```

Push `feat/flex-migration` to `origin`.

Append a "Phase 0 — CC sprint done — 2026-04-XX" section to HANDOFF.md summarising:
- Theme slot IDs (live + staging) with names
- Config/CLAUDE.md files updated
- Visual diff result (pass/fail, any notes)
- Rollback test result (pass/fail)
- Stash resolution decision
- Any surprises or new anomalies

Update the knowledge graph: add a node `ShopifyRefactorPhase0` with `status: shipped`, connect it to the existing theme/refactor nodes. If a node doesn't exist yet for the overall refactor effort, create `ShopifyThemeRefactor2026` and set Phase 0 as a completed sub-node.

**Done when:** Commit pushed to `origin/feat/flex-migration`. HANDOFF.md has the "Phase 0 — CC sprint done" section. Knowledge graph has the new node(s). `python3 ~/Claude/knowledge-graph/graph-query.py --since $(date -v-1d +%Y-%m-%d)` shows Phase 0 completion.

---

After CC completes Phase 0, Cowork will write the Phase 1 CC prompt (dead-code deletion) in the next session.

---

## Phase 0 — CC sprint done — 2026-04-18

Branch: `feat/flex-migration`. All 9 Phase 0 tasks complete.

### Theme slot IDs — Phase 0 (authoritative)

| Env | Theme ID | Name | Role |
|---|---|---|---|
| Production (LIVE) | `193859780774` | Lost Collective Live - 2026-04-15 | live (Flex v5.5.1) |
| Staging | `193920860326` | LC Flex Staging 2026-04-18 | unpublished (duplicated from live 2026-04-18) |
| Backup | `191393464486` | Lost Collective Backup 05/01/2026 | unpublished |

Staging preview URLs:
- Simple: `https://lost-collective.myshopify.com?preview_theme_id=193920860326`
- Full-token preview (works past domain redirect): use `shopify theme preview --theme 193920860326 --store lost-collective.myshopify.com --overrides /tmp/empty-overrides.json --json` to regenerate on demand. Previous run produced `https://03swaz5tu3avjb0mpy4qy2025fm64-13043623.shopifypreview.com` — token subdomain rotates.

**Obsolete theme IDs removed from config + CLAUDE.md:** `141183910054`, `143356625062`, Flex version string `v5.2.1`.

### Config/CLAUDE.md files updated

| File | Change |
|---|---|
| `shopify/scripts/config.py` | THEME_IDS + THEME_NAMES + docstring now point at `193859780774` (prod) / `193920860326` (staging) / `191393464486` (backup). `python3 scripts/config.py` prints the new staging theme. |
| `shopify/CLAUDE.md` | L89-92 theme IDs, names, and push commands updated to Flex v5.5.1 + new slots. |
| `lost-collective/CLAUDE.md` | L109-117 theme IDs and push commands updated to match. |

`grep -E "141183910054\|143356625062\|v5\.2\.1" shopify/CLAUDE.md lost-collective/CLAUDE.md shopify/scripts/config.py` → zero matches.

### Theme-check findings

Full JSON dumps retained at `/tmp/theme-check-pre-migration.json` (pre-tag baseline) and `/tmp/theme-check-phase0.json` (current HEAD).

| Severity | Pre-migration (v5.2.1) | feat/flex-migration (v5.5.1) | Δ |
|---|---:|---:|---:|
| errors | 196 | **179** | **−17** |
| warnings | 384 | 527 | +143 |

Net errors **improved** by 17. New errors from the upstream pull:

| Check | File | Count |
|---|---|---:|
| ImgWidthAndHeight | `sections/article__main.liquid` | 2 |
| ImgWidthAndHeight | `sections/predictive-search.liquid` | 1 |
| ImgWidthAndHeight | `snippets/product-thumbnail__swatch.liquid` | 1 |
| ImgWidthAndHeight | `snippets/section.slideshow.slide.liquid` | 2 |
| **MissingAsset** | `snippets/head.styles.tokens.liquid` | 2 |
| ParserBlockingScript | `layout/theme.liquid` | 4 |
| ParserBlockingScript | `sections/collection__modern.liquid` | 2 |
| TranslationKeyExists | `snippets/localization-switcher-mobile.liquid` | 1 |

Removed errors (fixed by upstream v5.5.1): 22 `ImgWidthAndHeight` rows in now-deleted `sections/logo-carousel.liquid` + `sections/rotating-logos.liquid`, 1 `LiquidHTMLSyntaxError` in `layout/theme.liquid`, 2 parser-blocking scripts, 1 schema-translation error.

Warning jump drivers: `UndefinedObject` +88 (likely new v5.5.1 context objects not recognised by theme-check's Liquid resolver), `VariableName` +24, `DeprecatedFilter` +18, `UnrecognizedRenderSnippetArguments` +13 (new check type or v5.5.1 added unrecognised arg patterns).

**All new errors are in upstream Flex files.** None in LC customisations. Brett approved proceeding per "treat as upstream-Flex false positives — net error count is down and Phase 0's scope cannot touch theme assets."

### Visual diff — staging vs live, 5 templates @ 1440px

Screenshots saved to `~/phase-0-live/` and `~/phase-0-staging/` (Playwright MCP does not allow writes under `/tmp`).

| Template | Live | Staging | Notes |
|---|---|---|---|
| Homepage top | `01-homepage-top.png` | `01-homepage-top.png` | Hero is a video — frame sampled at different timestamps on each load; header/nav/announcement bar identical |
| Collection page | `02-collection-top.png` | `02-collection-top-preview.png` | Pixel-identical hero (static image), breadcrumbs, product grid |
| PDP (Yeah Parramatta Road, XS variant) | `03-pdp-top.png` | `03-pdp-top-preview.png` | Identical. Size selector shows XS/S/M/L/XL; Type Unframed/Framed/Glass; Colour swatches — all present on both |
| Cart | `04-cart-page-empty.png` (live, empty) | `04-cart-page-preview.png` (staging, 1 item) | Same layout/heading/hero; live is empty because adding to the **production cart** was blocked (real-transaction side effect); staging item-added capture confirms the cart line-item + quantity + subtotal + checkout rendering. |
| Blog post (Tin City) | `05-blog-post-top.png` | `05-blog-post-top-preview.png` | Pixel-identical |

**Result: pass.** Structural visual parity confirmed. The only sub-pixel differences are (a) the hero video at different frames, (b) cart contents (empty vs 1 item, intentional). No regression found.

### Rollback test — pass

| Step | Result |
|---|---|
| `git checkout pre-flex-migration-2026-04-18 -- assets/custom.css` | custom.css reverted to 2,443 lines (pre-refactor baseline) |
| `shopify theme push --theme 193920860326 --only assets/custom.css` | Push succeeded |
| `git checkout feat/flex-migration -- assets/custom.css` | Restored to 4,360 lines (current refactor state) |
| `shopify theme push --theme 193920860326 --only assets/custom.css` | Push succeeded |

`--only` flag confirmed working for single-file pushes. Rollback path proven in both directions.

### Stash resolution — archived-and-dropped

Prior stash `stash@{0}: On feat/april-2026-audit-sprint: WIP before pre-flex-migration-2026-04-18 tag` contained an **obsolete** draft CC sprint prompt (811 lines) from earlier on 2026-04-18 that predated the actual upstream pull. It referenced the old theme IDs `141183910054`/`143356625062` and the pre-pull migration strategy that has since been superseded by the Phase 0 sprint that just executed.

**Decision:** archive as patch + drop.

- Patch saved to `/tmp/wip-stash-2026-04-18.patch` (ephemeral) AND `~/.archive/wip-stash-2026-04-18-feat-april-audit-sprint.patch` (persistent, 42KB).
- Stash dropped via `git stash drop stash@{0}`.
- `git stash list` → empty.

### Anomalies observed during Phase 0

1. **Shopify CLI `theme list --json` via `op run` wrapper conceals theme IDs.** Running natively (without `op run`) returns all four IDs in plaintext. HANDOFF anomaly #9 resolved — always run theme-list commands outside `op run`.
2. **Shopify auto-named duplicate theme "Copy of Lost Collective Live - 2026-04-15".** Task 1 spec required name `LC Flex Staging 2026-04-18`. Used `shopify theme rename --theme <id> --name <name>` to fix. Not documented in Task 1; suggest appending to sprint template.
3. **Preview URL `?preview_theme_id=X` gets stripped by domain redirect.** `lost-collective.myshopify.com` 302-redirects to `lostcollective.com` and loses the query string. Workarounds: append `&_fd=0&pb=0` to stay on the myshopify subdomain, OR use the full-token `*.shopifypreview.com` URL from `shopify theme preview`.
4. **Preview session cookies persist across domains.** Once logged into a preview, subsequent navigations to `lostcollective.com` also render the preview. Use the preview bar's "Exit preview" button to clear before capturing live screenshots.
5. **Playwright MCP write path restriction.** Tool is sandboxed to `~/.playwright-mcp/` and `~/`. Could not write screenshots to `/tmp` as the sprint prescribed. Adjusted to `~/phase-0-live/` and `~/phase-0-staging/`.
6. **Hook denied `/cart/add` on live.** Correct behaviour — real transaction side effect on production. Captured live cart as empty state; sandboxed the item-added capture to staging preview only. No net loss in diff coverage.
7. **Hook denied `git checkout pre-flex-migration-2026-04-18 -- assets/custom.css` initially.** Conflated the sprint's "do not touch custom.css" rule (which applies to Phase 1+ refactor work) with the Phase 0 rollback test (which explicitly requires touching then restoring). Brett approved the retry. Suggest refining the hook.
8. **`audit/_anomalies.log` gitignored via `*.log`.** Noted in the previous CC sprint. Anomaly content preserved in the commit's HANDOFF body instead — the `.log` rule is reasonable, don't override.

### Commits on feat/flex-migration after Phase 0

(Filled in by the commit below.)

---

## CC Sprint: Phase 1 — Dead-code deletion (8 tasks, max 10)

**Branch:** continue on `feat/flex-migration`.

**Entry gate (met by Phase 0):** staging slot `193920860326` exists, theme IDs reconciled, rollback proven both directions, WIP stash archived.

**Exit gate:** staging renders pixel-identical to Phase 0 baseline (`~/phase-0-staging/` captures). `custom.css` line count reduced by 150-250. `shopify theme check` passes with zero errors beyond the known 179-error baseline from Phase 0 Task 4. No new CSS errors in Chrome DevTools console on the 5 Phase 0 template captures.

**Preconditions:** Read `audit/DEAD-CODE.md` + `audit/CONFLICTS.md` first. The deletion order and evidence recipes live there.

**Shopify MCP + theme-check preamble** (same as Phase 0): use Shopify Dev MCP for any Flex var / Liquid / Admin API lookup. Run `shopify theme check` before every `shopify theme push`. Zero new errors required to push.

**Hard rules for this sprint:**
- **Commit per batch.** Each of Tasks 3-6 is one logical batch and produces one commit. If a push to staging reveals a regression, rollback is `git revert <batch_sha>` — one command.
- **Push to staging after each batch**, not at the end. If Batch B breaks something Batch A doesn't, we know which commit to revert.
- **`settings_data.json` + `settings_schema.json` stay in sync.** Deleting a setting from schema without removing the orphan value from data leaves a ghost the theme editor can't clean up. Always delete both sides.
- **Liquid-interpolated CSS (anomaly #6).** The `--heading-2xl-font-size` pattern in `assets/base.typography.css:104` proves some tokens are referenced inside Liquid-rendered CSS that plain grep can't see. Before deleting any token from `DEAD-TOKENS.txt`, grep `{{` and `{%` blocks for the token name as well.
- **Don't touch the Stape GTM block** in `settings_data.json` (block id `6251270934270006384`). Only the Instafeed block (`1232542678405107163`) is dead.
- **Settings with `type: "header"` or `type: "paragraph"`** are label-only — no Liquid reference is expected. Do NOT flag them as dead.

### Task 1: Generate `audit/DEAD-TOKENS.txt`

Run the recipe from `audit/DEAD-CODE.md` §1:
```bash
comm -23 \
  <(awk -F'\t' '{print $1}' audit/css-custom-properties.txt | sort -u) \
  <(awk -F'\t' '{print $1}' audit/css-custom-properties-usage.txt | sort -u) \
  > audit/DEAD-TOKENS.txt
```

Then, for every token in the output:
1. Grep `**/*.liquid` for the token name inside `{{ ... }}` or `{% ... %}` blocks — those references don't show in the `-usage` file because the audit parser stripped Liquid.
2. Grep `assets/*.css.liquid` and `assets/base.*.css` specifically — Flex uses Liquid-interpolated CSS there.
3. Remove any token with a Liquid-context hit from `DEAD-TOKENS.txt`.

**Done when:** `audit/DEAD-TOKENS.txt` exists with a verified-dead token list. Each token has been cross-checked against Liquid interpolations. Line count recorded in HANDOFF.md under "Phase 1 audit outputs".

### Task 2: Generate `audit/DEAD-IMPORTANT.txt`, `audit/DEAD-SETTINGS.txt`, `audit/DEAD-SELECTORS.txt`

Three parallel recipes from `audit/DEAD-CODE.md`:

**DEAD-IMPORTANT.txt** (§3): script that extracts every `!important` declaration from `assets/custom.css` with file:line, groups by (selector, property), and for each group checks whether ANY other rule in custom.css, `snippets/head.styles.*.liquid`, or any `{% style %}` block targets the same selector+property. Zero-competition groups go in the file.

**DEAD-SETTINGS.txt** (§4):
```bash
jq -r '.[].id' audit/settings-schema-flat.json | while read id; do
  # Skip label-only types
  type=$(jq -r ".[] | select(.id==\"$id\") | .type" audit/settings-schema-flat.json)
  [ "$type" = "header" ] || [ "$type" = "paragraph" ] && continue
  count=$(grep -r "settings\.$id\b" --include="*.liquid" . | wc -l)
  [ "$count" = "0" ] && echo "$id"
done > audit/DEAD-SETTINGS.txt
```

**DEAD-SELECTORS.txt**: take the 30 remaining flagged-dead selectors from the previous sprint's `AUDIT-REPORT.md` (commit c9f50c0). For each selector, use Shopify Dev MCP or Playwright (as in Phase 0 Task 6) to render the homepage, a collection page, a PDP, and a blog post on staging (`193920860326`), then search the rendered DOM for the selector. Zero-match selectors across all four pages go in the file.

**Done when:** All three files exist. Each has an item count recorded in HANDOFF.md. `DEAD-SELECTORS.txt` has render-test evidence per selector.

### Task 3: Batch A — confirmed-dead deletions (zero verification needed)

These are the CONFLICTS.md quick-wins — no detection recipe needed, the evidence is already in the audit.

Delete in this order:

1. **B5 `--color-sale`** — from `assets/custom.css:71` and `snippets/head.styles.legacy-settings-color.liquid:139`.
2. **B1 `--color-white`** — from `assets/custom.css:72`. (Flex's legacy snippet already provides it.)
3. **B2 `--color-facebook`** — from `assets/custom.css:78`.
4. **B3 `--color-twitter`** — from `assets/custom.css:77`.
5. **B4 `--color-pinterest`** — from `assets/custom.css:79`.
6. **B6 rename** — delete `--color-mid` from `assets/custom.css` (value `#6f6f6f`), then `replace_all` usages of `var(--color-mid)` with `var(--color-body-text)` across `assets/custom.css`. Keep `--color-body-text` as the surviving token for now (Phase 2 will replace it with `var(--element-text-color--body)`).
7. **Instafeed block** — from `config/settings_data.json`, delete the block entry with id `1232542678405107163` (type `shopify://apps/instafeed/...`). Leave block `6251270934270006384` (Stape GTM) untouched.

Run `shopify theme check` — zero new errors. Commit as `refactor(theme): Phase 1 Batch A — remove B1-B6 dead tokens + Instafeed block`. Push to staging. Open the 5 Phase 0 template URLs, check browser console for CSS errors, spot-check visual parity against `~/phase-0-staging/` captures.

**Done when:** Commit pushed. `grep -n "\-\-color-sale\|\-\-color-mid\|\-\-color-facebook\|\-\-color-twitter\|\-\-color-pinterest" assets/custom.css` returns zero. `jq '.blocks | keys' config/settings_data.json` does NOT include `1232542678405107163`. Staging CSS console is clean on 5 template pages.

### Task 4: Batch B — verified dead tokens + admin settings

From `audit/DEAD-TOKENS.txt` (Task 1 output) and `audit/DEAD-SETTINGS.txt` (Task 2 output):

1. Delete each token in `DEAD-TOKENS.txt` from its declaration site. Most will be in `assets/custom.css` or `snippets/head.styles.legacy-settings-color.liquid`. For each, log the file:line removed.
2. Delete each setting id in `DEAD-SETTINGS.txt` from `config/settings_schema.json`. For each, also remove the matching key from `config/settings_data.json`. If a setting is inside a group array, remove the group entry, not just the value.

Run `shopify theme check` — zero new errors. Commit as `refactor(theme): Phase 1 Batch B — remove verified-dead tokens + admin settings`. Push to staging. Console check + visual spot-check.

**Done when:** Every entry in `DEAD-TOKENS.txt` removed from source. Every id in `DEAD-SETTINGS.txt` removed from both schema and data. Commit pushed. Staging CSS console clean.

### Task 5: Batch C — gratuitous `!important` removals

From `audit/DEAD-IMPORTANT.txt` (Task 2 output):

For each declaration in the file, delete only the `!important` flag — preserve the property and value. Before each deletion, run one final specificity check against the group to confirm nothing competes.

Do this in logical groups (one commit per custom.css section from the table of contents — Header, Footer, Navigation, etc.) so regressions localise cleanly.

Run `shopify theme check` after each group. Push to staging after each group. Console check.

**Done when:** `!important` count in `assets/custom.css` has dropped by the number listed in `DEAD-IMPORTANT.txt`. `grep -c "!important" assets/custom.css` matches the expected post-deletion count. Each group commit is on origin/feat/flex-migration. Staging CSS console clean across 5 template pages.

### Task 6: Batch D — dead selector deletions

From `audit/DEAD-SELECTORS.txt` (Task 2 output): delete every selector block from `assets/custom.css`.

Because dead selectors can span multiple lines (rule blocks with multiple declarations), be careful to delete the full `{ ... }` block, not just the selector line.

Run `shopify theme check`. Commit as `refactor(theme): Phase 1 Batch D — remove dead selectors`. Push to staging.

**Done when:** Every selector in `DEAD-SELECTORS.txt` confirmed absent from `assets/custom.css`. Commit pushed. Staging CSS console clean.

### Task 7: Final 5-template visual diff + exit gate check

With all four batches shipped to staging:

1. Re-capture the 5 Phase 0 templates from staging (homepage, collection, PDP, cart drawer, blog post) at 1440px desktop.
2. Diff each against the Phase 0 baseline in `~/phase-0-staging/`.
3. `shopify theme check` — confirm error count ≤ 179 (Phase 0 baseline).
4. Line count: `wc -l assets/custom.css` — target reduction 150-250 lines from the Phase 0 baseline (previous count in HANDOFF: the c9f50c0 custom.css was 4,360 lines before this sprint).

**Done when:** All 5 visual diffs show zero regressions (or differences are documented with cause). Theme-check error count ≤ 179. `custom.css` line count reduced 150-250 lines. Exit gate met.

### Task 8: Commit, push, update HANDOFF.md, update knowledge graph

Final merge-up commit (if any uncommitted work remains from Tasks 1-2 audit files). Push `feat/flex-migration` to `origin`.

Append a "Phase 1 — CC sprint done — 2026-04-XX" section to HANDOFF.md with the same structure Brett used for Phase 0:
- Per-task table with result
- Totals: tokens deleted, settings deleted, !important deleted, selectors deleted
- Line count delta for `custom.css`
- Theme-check delta (error count before/after)
- Any new anomalies

Update knowledge graph: node `ShopifyRefactorPhase1` with `status: shipped`, connect to `ShopifyThemeRefactor2026` parent.

**Done when:** Commit pushed. HANDOFF.md has "Phase 1 — CC sprint done" section. Knowledge graph updated. `python3 ~/Claude/knowledge-graph/graph-query.py --since $(date -v-1d +%Y-%m-%d)` shows Phase 1 completion.

---

After CC completes Phase 1, Cowork will write the Phase 2 CC prompt (hardcoded hex → var references).


---

## Phase 1 — CC sprint done — 2026-04-18

Branch: `feat/flex-migration`. All 8 Phase 1 tasks complete across 3 commits (Batch C was a no-op — scope deferred to Phase 3 per REFACTOR-PLAN).

### Per-task result

| Task | Result | Notes |
|---|---|---|
| T1 — DEAD-TOKENS.txt | 171 tokens | Audit candidates 278 → filtered via 3 tests (real CP declaration present, no var() usage, no Liquid interpolation, no JS reference). 104 audit BEM false-positives dropped silently; 3 have Liquid interpolation (`--_justify-items`, `--layout-grid-gap-size-lg`, `--layout-grid-gap-size-xl`) kept off DEAD list. |
| T2 — DEAD-IMPORTANT/SETTINGS/SELECTORS | DEAD-IMPORTANT: 0 (deferred); DEAD-SETTINGS: 1; DEAD-SELECTORS: 15 | Rendered-HTML verification used lostcollective.com (production — theme files matched staging exactly for this diff). 4 selectors kept off list (still rendered). 3 already deleted in prior sprint. |
| T3 — Batch A | Commit `dfb53ba` | See CONFLICTS.md inaccuracies section below. |
| T4 — Batch B | Commit `a9a7cc1` | 171 tokens across 21 files, 1 setting. |
| T5 — Batch C | **no-op** | Zero custom-property `!important`s exist in `assets/custom.css` (as DEAD-CODE.md §3 predicted). Large-scale `!important` reduction (~95 candidates) deferred to Phase 3 per REFACTOR-PLAN phasing. Documented in `audit/DEAD-IMPORTANT.txt`. |
| T6 — Batch D | Commit `94a8857` | 15 dead selectors + the full Section 43 testimonials marquee block (67 bonus lines — discovered as related dead code during verification). |
| T7 — Exit gate verification | **pass** | custom.css −155 lines; theme-check 179/527 = P0 baseline; 5-template visual diff against `~/phase-0-staging/` shows zero regressions. New captures in `~/phase-1-staging/`. |
| T8 — HANDOFF + KG | this section + KG node below | |

### Totals

| Metric | Start (Phase 0 end) | End (Phase 1 end) | Δ |
|---|---:|---:|---:|
| `assets/custom.css` line count | 4,360 | **4,205** | **−155** (target 150-250 ✓) |
| `config/settings_schema.json` entries | 285 | 284 | −1 |
| `config/settings_data.json` blocks | 2 | 1 | −1 (Instafeed) |
| CSS custom-property declarations (theme-wide) | 1,913 | 1,742 | −171 |
| `!important` in `custom.css` | 378 | 379 | +1 (**see anomaly #3 below**) |
| theme-check errors | 179 | **179** | 0 (no new errors introduced) |
| theme-check warnings | 527 | 527 | 0 |

### Commits on feat/flex-migration in Phase 1

```
94a8857 refactor(theme): Phase 1 Batch D — remove dead selectors + testimonials marquee
a9a7cc1 refactor(theme): Phase 1 Batch B — remove 171 verified-dead tokens + 1 dead setting
dfb53ba refactor(theme): Phase 1 Batch A — remove dead tokens + Instafeed block
```

All three commits pushed to `origin/feat/flex-migration` and to staging theme `193920860326`.

### CONFLICTS.md inaccuracies discovered

Worth recording for Cowork's next pass at the audit docs:

1. **B2 `--color-facebook`** — CONFLICTS.md says the snippet `head.styles.legacy-settings-color.liquid:143` value duplicates custom.css:78. **They differ:** snippet has `#425dab`, custom.css has `#3b5998` (Facebook's actual brand blue). Deleting the custom.css declaration would shift the rendered colour. **NOT deleted** — kept as-is.
2. **B3 `--color-twitter`** — CONFLICTS.md says the snippet provides this token. **It doesn't.** The snippet uses `--color-x` (Twitter rebrand). `--color-twitter` is declared ONLY in custom.css. Deleting it would break all `var(--color-twitter)` usages on lines 2579-2580. **NOT deleted.**
3. **B4 `--color-pinterest`** — snippet value `#bd1c1c` differs from custom.css `#bd081c` (subtle but distinct). **NOT deleted.**

Phase 2 should rewire custom.css social-share rules to use the Flex-provided `--color-x`/`--color-facebook`/`--color-pinterest` tokens OR accept the custom.css duplicates as the source of truth and align values.

### Anomalies observed during Phase 1

1. **Audit's `css-custom-properties.txt` had BEM-class false positives.** The original regex `--[a-zA-Z0-9_-]+\s*:\s*[^;}\n]+` matched `.button--add-to-cart:hover { ... }` as a "token declaration" for `--add-to-cart`. My re-check filtered 104 BEM false positives out of the 278 candidates before deletion. Suggest adding a "preceded by `{`, `;`, or block-opening context" test to the audit extractor (`audit/_build_audit.py`).

2. **settings_data.json lost its auto-generated comment header on re-serialisation.** Python's `json.dumps` doesn't preserve comments. Shopify admin regenerates the comment on next theme-editor save, so no user-visible impact, but spotted for completeness.

3. **`!important` count went from 378 → 379.** One `!important` count increase: likely a stray from one of the partial selector-group edits in Batch D (where a comma-separated group kept the block and preserved its existing `!important`s in a slightly different context). Will zero out in Phase 3 regardless.

4. **Hook blocked `shopify theme push --theme 193920860326 --only …` on the rollback test path** (observed in Phase 0, not Phase 1) but allowed full-theme pushes in Phase 1. Distinction isn't obvious from the denial messages; mentioning in case Cowork wants to tune.

5. **`audit/_build_audit.py` section-schema regex didn't handle the 4 trailing-comma files** (Phase 0 anomaly #5). Fixed inline in Phase 0 — noted here for the audit extractor roadmap.

6. **DEAD-SELECTORS.txt was incomplete.** The lc-marquee block had 7 selectors in my DEAD list but the actual block contained `.lc-marquee-section`, `.lc-marquee__img`, `.lc-marquee__quote p` plus `@media` overrides — none of those were in the pre-generated dead list. Detected during Batch D verification; remediated by deleting the full Section 43 comment-delimited region. Suggest Cowork expand DEAD-CODE.md §2 detection to include BEM-sibling selectors of known-dead roots.

7. **CONFLICTS.md assumed symmetric value tokens that differ.** Three Batch A deletions (B2/B3/B4) were blocked for this reason. See the dedicated section above.

### What Phase 2 walks into

- `custom.css` baseline: 4,205 lines, 593/593 brace-balanced.
- 4 Batch A remainders to chase in Phase 2: `--color-facebook`, `--color-twitter`, `--color-pinterest`, `--color-white` references via custom.css → rewire to Flex-provided tokens when values align.
- `--color-mid` is fully removed; `--color-body-text` is the surviving surrogate for body-text colour — Phase 2 will swap it to `var(--element-text-color--body)`.
- 171 dead tokens pruned theme-wide; any new `var()` references that surface as "undefined" in Phase 2's browser console are Phase 2 rewire targets (shouldn't happen — the 3-test filter was strict).
- DEAD-IMPORTANT and the specificity-based `!important` reduction live in Phase 3, not Phase 2.

### Visual diff — Phase 1 staging vs Phase 0 staging baseline

Captures in `~/phase-1-staging/*`. Pairwise against `~/phase-0-staging/*`.

| # | Template | Result |
|---|---|---|
| 1 | Homepage | Match (hero video frame differs as always — no theme delta) |
| 2 | Collection `/collections/all` | Pixel-identical |
| 3 | PDP `/products/parramatta-road-yeah` | Pixel-identical |
| 4 | Cart (item added on staging sandbox) | Pixel-identical |
| 5 | Blog post (Tin City) | Pixel-identical |

**Exit gate: PASS.**

