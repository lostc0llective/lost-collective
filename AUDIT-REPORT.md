# Lost Collective Theme Audit Report

**Date:** 2026-04-15
**Theme:** Flex v5.2.1 by Out of the Sandbox
**Staging theme:** 143356625062
**Scope:** Full codebase inventory, CSS dependency map, dead code list, JS audit, Liquid template hierarchy

---

## 1. Codebase Inventory

### File counts

| Category | Count | Total lines |
|----------|-------|-------------|
| CSS files | 2 | 4,427 |
| JS files | 34 | ~12,811 |
| Sections | 78 | - |
| Snippets | 85 | - |
| Templates | 26 | - |
| Layouts | 3 | 425 (theme.liquid) |
| Locales | 8 | - |
| Config files | 2 | settings_data.json, settings_schema.json |

### CSS files

| File | Lines | Purpose |
|------|-------|---------|
| custom.css | 4,416 | All custom styling, 42 documented sections |
| fancybox.css | 11 | Lightbox library (minimal) |

### JS files (by size, descending)

| File | Lines | Category | Loaded by |
|------|-------|----------|-----------|
| z__jsProduct.js | 7,191 | Feature | product__main, quickshop, featured-product |
| utilities.js | 1,682 | Core | theme.liquid (global) |
| currencyConversion.js | 757 | Integration | theme.liquid (conditional) |
| vendors.js | 457 | Vendor bundle | theme.liquid (global) |
| z__jsAjaxCart.js | 417 | Feature | ajax-cart snippet |
| z__jsHeader.js | 297 | Feature | header sections |
| z__jsCollection.js | 259 | Feature | collection__main |
| z__jsVideo.js | 173 | Feature | index__video |
| z__jsCart.js | 131 | Feature | cart__main |
| z__jsMegaMenu.js | 130 | Feature | mega-menu |
| All others (24 files) | <100 each | Feature | Respective sections |

All 34 JS files are loaded somewhere. No orphaned JS files.

---

## 2. CSS Dependency Map

### Design tokens (custom.css :root)

Already well-structured with CSS custom properties:

**Colours:** --color-brand-yellow (#ebac20), --color-dark (#1a1a1a), --color-mid (#6f6f6f), --color-light (#f5f5f5), --color-sale (#d32f2f), --color-white (#ffffff), --color-body-text (#6f6f6f), --color-footer-bg (#4d4d4d), --color-header-bg (#4d4d4d), --color-primary (alias for brand-yellow), social colours (twitter, facebook, pinterest, email)

**Fonts:** --font-body (Lato), --font-heading (Montserrat)

**Spacing:** --space-xs (4px) through --space-3xl (80px)

**Border radius:** --radius-xs (3px) through --radius-pill (35px)

**Shadows:** --shadow-sm through --shadow-xl

**Transitions:** --transition-fast (0.2s) through --transition-base (0.3s)

### Shopify admin colour settings (settings_schema.json)

These are set in the theme editor and output as Liquid variables, not CSS custom properties:

| Setting ID | Label | Default |
|------------|-------|---------|
| shop_bg_color | Background | #ffffff |
| border_color | Borders | #D3D3D3 |
| regular_color | Body text | #000000 |
| link_color | Links | #007ACE |
| link_hover_color | Links hover | #51B2F5 |
| heading_color | Headings | #000000 |
| header_background | Header BG | #3F3F3F |
| header_link_color | Header links | #FFFFFF |
| footer_background | Footer BG | #808080 |
| footer_link_color | Footer links | #FFFFFF |
| footer_text_color | Footer text | #FFFFFF |
| sale_color | Sale price | #C70000 |
| review_star | Review star | #000000 |
| + 15 more | Stickers, qty buttons, dropdowns, etc. | Various |

### Typography settings (settings_schema.json)

| Setting ID | Type | Default |
|------------|------|---------|
| regular__font | font_picker | open_sans_n4 |
| regular_font_size | range 12-20px | 15px |
| logo__font | font_picker | open_sans_n4 |
| nav__font | font_picker | open_sans_n4 |
| nav_font_size | range 12-20px | 14px |
| nav_letter_spacing | range 0-5px | 1px |
| button__font | font_picker | open_sans_n4 |
| heading__font | font_picker | open_sans_n4 |
| + dropdown sizes, capitalization settings | Various | Various |

### CSS specificity analysis

**250+ !important declarations** in custom.css.

High-volume areas:
- Navigation chevrons (lines 395-470): 36 declarations. Required to override Flex theme's flex-icon font styling.
- Mobile header/sticky bar (lines 669-774): 57 declarations. Required to override inline section styles.
- Dark overlay cards (lines 1526-1590): 16 declarations.
- Footer responsive grid (lines 1782-1987): 65+ declarations.

Assessment: Most are legitimate overrides of the Flex theme's high-specificity selectors. The theme uses inline styles on section wrappers and deeply nested selectors that can only be overridden with !important. However, many can be refactored using :where() for resets and @layer for cascade management.

### Inline styles in Liquid

Zero `style=` attributes found in any Liquid template. All styling is in external CSS. Clean.

---

## 3. Dead CSS

### Confirmed dead selectors (33 total, ~120 lines removable)

**Largest dead block -- lc-marquee component (lines 4170-4251, ~80 lines):**
- `.lc-marquee`, `.lc-marquee__track`, `.lc-marquee__item`, `.lc-marquee__card`, `.lc-marquee__text`, `.lc-marquee__author`, `.lc-marquee__role`, `@keyframes marquee-scroll`, `@keyframes marquee-scroll-mobile`
- Testimonial marquee CSS with no corresponding Liquid section.

**Individual dead selectors:**
- `.page--about-content` (lines 4290-4306) -- page class never applied
- `.link--animated` (lines 1205-1221) -- animated underline never used
- `.instafeed-container`, `.instafeed-image`, `.instafeed-link` (lines 1647-1657) -- third-party app uninstalled
- `.block__link-list` -- footer uses different class names
- `.footer__bottom` -- naming mismatch with actual footer Liquid
- `.rich-text__title` -- theme uses `.rich-text__heading.title`
- `.mega-menu__heading` -- theme uses `.menu__heading`
- `.product-grid-item` -- theme uses `.product-thumbnail`
- `#shopify-section-index_slideshow_classic_mewq3w` (line 4413) -- hardcoded section ID, fragile and likely stale

**Verify before removing (7 selectors):**
- `.product-block--price`, `.product-block--description`, `.product-block--share` -- may be generated by Shopify block rendering at runtime
- `.product-gallery--media-amount-1` -- may be generated by product gallery JS
- `.image-item`, `.kandos-gallery` -- may exist in article rich text HTML
- `.index-json` -- may be a body class for JSON templates

---

## 4. JavaScript Audit

### Dependency graph

```
jQuery 3.6.0 (CDN, defer)
  +-- vendors.js (Flickity, fancyBox, Waypoints, jQuery Sticky, jQuery Zoom, Plyr, js-cookie, instant.page v1.2.2)
  +-- utilities.js (PXUTheme.* namespace: animation, asyncView, breadcrumbs, infiniteScroll, mobileMenu, predictiveSearch, video)
  +-- app.js.liquid (SectionManager, rimg, age gate, shipping calc)
  +-- All z__js* modules register on window.PXUTheme.{moduleName}
```

### Security issues

| Severity | File | Line | Issue |
|----------|------|------|-------|
| **HIGH** | z__jsCart.js | 49 | `eval('(' + XMLHttpRequest.responseText + ')')` -- XSS vector. Must replace with `JSON.parse()` |

### Bugs

| File | Line | Issue |
|------|------|-------|
| z__jsCart.js | 57-58 | Duplicate `dataType` key (`"json"` then `"html"`). Second wins. Also uses deprecated `async: false` (blocks main thread) |
| z__jsCustomContactForm.js | 44 | References bare `event` instead of parameter `e`. Relies on deprecated `window.event` |
| z__jsCollection.js | 92 | Bare `url('?sort_by')` may call wrong function if `#sort-by` element is absent |
| z__jsMap.js | 19 | `$.ajaxSetup({ cache: true })` mutates global jQuery AJAX state |

### Obsolete code

| File | Line | Issue |
|------|------|-------|
| z__jsCollection.js | 10-13 | IE11 detection (`navigator.userAgent.match(/Trident/)`) -- IE11 EOL June 2022 |
| z__jsProduct.js | 239-242 | `document.createEvent`/`initEvent` polyfill for IE10 |
| js-variables.liquid | ~110 | `window.PXUTheme.media_queries.ie10` -- dead code |
| theme.liquid | ~184 | `DocumentTouch` check -- removed from all browsers |

### Duplicate library load

| Library | Location 1 | Location 2 |
|---------|-----------|-----------|
| instant.page | vendors.js (v1.2.2) | theme.liquid line ~424 (v5.2.0 module) |

The v5.2.0 module is correct. Remove v1.2.2 from vendors.js.

### jQuery dependency

544 occurrences across all modules. **Hard dependency** -- cannot be removed without complete rewrite of ~12,000 lines. Only 3 files are jQuery-free: announcement-bar-marquee.js, trust-bar-marquee.js, swatch-layout.js.

### Console statements

12 total, all `console.error` or `console.warn` in error paths. No `console.log` debug statements. Acceptable.

### Global pollution (minor)

`window.arrowShape`, `window.isScreenSizeLarge`, `window.videoPlayers`, `window.videoControls`, `window.moneyFormats` -- could be namespaced under PXUTheme but low risk.

---

## 5. Liquid Template Audit

### Orphaned sections (no template references, no schema presets)

| Section | Issue |
|---------|-------|
| rotating-logos.liquid | No schema. Duplicate of logo-carousel.liquid. 18 hardcoded CDN image URLs. |
| logo-carousel.liquid | No schema. Duplicate of rotating-logos.liquid. 18 hardcoded CDN image URLs. |
| predictive-search.liquid | No schema, not referenced anywhere. |
| surface-pick-up.liquid | No schema, not referenced. Store pickup never wired in. |

### Orphaned snippets (potentially)

| Snippet | Notes |
|---------|-------|
| icon_outline_a-l.liquid | May be loaded dynamically by icon.liquid -- verify before removing |
| icon_outline_m-z.liquid | Same |
| icon_solid_a-l.liquid | Same |
| icon_solid_m-z.liquid | Same |

### Deprecated Liquid filters

| File | Filter | Count |
|------|--------|-------|
| quickshop.liquid | `| script_tag` | 2 |
| announcement-bar.liquid | `| script_tag` | 1 |
| footer__icon-bar.liquid | `| script_tag` | 1 |
| gift_card.liquid | `| script_tag`, `| stylesheet_tag` | 4 |

### Anti-patterns found

**Hardcoded values that should use settings:**
- fixed-message.liquid: Ignores its own `text` and `button_label` schema settings, uses hardcoded cookie consent text and "Got it" button
- fixed-message.liquid: Brand colours #ebac20 and #1a1a1a hardcoded 8 times (should use CSS vars)
- rotating-logos.liquid and logo-carousel.liquid: 18 logo URLs hardcoded (should use image_picker blocks)
- article__related-series.liquid: Hardcoded colours #e8e8e8, #666
- index__instagram.liquid: Hardcoded colour #f0eeea
- logo-carousel.liquid: Hardcoded colour #f9f9f9

**Layout logic that should be extracted:**
- theme.liquid lines 22-33: Template-specific meta robots logic
- theme.liquid lines 195-213: Consent Mode v2 JS (should be a snippet)
- theme.liquid lines 405-421: Policy page H1 fix (should be a snippet)
- theme.liquid line 29: Hardcoded page handle `shipping-blurb-for-product-page`

**Stale references:**
- quickshop.liquid: Preconnects to monorail-edge.shopifysvc.com (removed from theme.liquid already)
- password.liquid: Same stale monorail preconnect

**Inline `<style>` blocks in sections:**
- index__instagram.liquid
- index__testimonial.liquid
- logo-carousel.liquid (full CSS baked inline)
- product-image-scroll__main.liquid

**Duplicated code across layouts:**
- Icon-star SVG symbol -- in theme.liquid, password.liquid, quickshop.liquid
- CSS variables (:root) -- in theme.liquid and quickshop.liquid
- Price-UI globals -- in theme.liquid and quickshop.liquid
- Consent Mode v2 JS -- in theme.liquid and password.liquid
- DNS prefetch/preconnect -- in all 3 layouts
- jQuery + vendor JS loading -- in all 3 layouts

### Section schema issues

| Section | Issue |
|---------|-------|
| fixed-message.liquid | `button_label` and `button_style` settings defined but overridden by hardcoded values |
| header-centered__top-bar.liquid | `show_currency_selector` and `show_locale_selector` settings unused |

---

## 6. Asset Loading Strategy

**Current order (theme.liquid):**

1. Font preloads (woff2): nav, heading, regular, logo
2. CSS: fancybox.css (conditional), styles.css (Flex base), custom.css
3. JS (all defer): jQuery 3.6.0, vendors.js, utilities.js, app.js, swatch-layout.js, currencyConversion.js (conditional)
4. DNS prefetch/preconnect: cdn.shopify.com, fonts.shopify.com, ajax.googleapis.com

Assessment: Solid. Fonts preloaded for FOUT prevention. JS deferred. Conditional preloads for fancybox reduce payload on non-product pages.

---

## 7. Priority Remediation List (for Phases 2-5)

### Critical (Phase 2-3)

1. **Security:** Replace `eval()` in z__jsCart.js:49 with `JSON.parse()`
2. **Dead CSS:** Remove lc-marquee block (~80 lines) and 25 other confirmed dead selectors
3. **Duplicate logo sections:** Consolidate rotating-logos + logo-carousel into one section with schema
4. **fixed-message.liquid:** Wire up existing schema settings instead of hardcoding text/colours

### High priority

5. Remove instant.page v1.2.2 duplicate from vendors.js
6. Fix z__jsCart.js duplicate dataType bug and remove sync XHR
7. Fix z__jsCustomContactForm.js bare `event` reference
8. Replace deprecated `| script_tag` and `| stylesheet_tag` filters
9. Remove stale monorail preconnects from password.liquid and quickshop.liquid
10. Extract consent-mode JS and policy-page H1 fix into snippets

### Medium priority

11. Remove IE11/IE10 detection code (3 instances)
12. Replace `document.createEvent`/`initEvent` with `new CustomEvent()`
13. Remove `DocumentTouch` check from theme.liquid
14. Move hardcoded colours in sections to CSS custom properties
15. Move inline `<style>` blocks to section-scoped CSS or custom.css

### Low priority (future consideration)

16. Namespace global JS variables under PXUTheme
17. Fix `$.ajaxSetup({ cache: true })` global mutation in z__jsMap.js
18. Consider deduplicating layout boilerplate (SVG symbols, CSS vars, vendor loading) into snippets
19. z__jsProduct.js is 7,191 lines -- candidate for module splitting in a future sprint

---

## 8. What Is NOT Broken

- Design token system is already in place and well-documented
- Zero inline styles in Liquid templates
- Asset loading strategy is optimised
- No console.log debug statements
- All JS files are loaded and used
- Section/snippet architecture follows Flex theme conventions
- Previous audit tiers (1-3) have been implemented
- Mobile fixes from April 12 are in custom.css sections 37-42
