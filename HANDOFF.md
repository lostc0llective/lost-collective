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
