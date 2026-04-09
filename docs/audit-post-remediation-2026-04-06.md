# Post-Remediation Audit Report
**Date:** 6 April 2026  
**Auditor:** Claude (overnight session)  
**Scope:** Shopify theme + Next.js dashboard — full codebase review against Apple-level quality standard  
**Status:** All fixes applied locally. One push command required to go live.

---

## Executive Summary

The remediation project was 43 of 44 items complete at audit start, with 2 files blocked from production by a 1Password timeout from the previous session. The audit identified 8 additional issues beyond those in the prior `AUDIT_REPORT.md`, ranging from a critical JavaScript error on every product page to a React Rules of Hooks violation in the dashboard. All 8 have been fixed in local files. A single command pushes everything to production.

The site is in genuinely strong shape. The 43 completed audit items are all correctly implemented — the blog CTA, article schema, edition scarcity, collector discount, price range, back-to-collection link, and all other remediation work verified clean in code. The issues found overnight were largely residual from older code that predates the remediation, not regressions from it.

---

## Your One Command

Run this first thing. It handles the 2 session-handoff items plus all 5 new fixes in a single pass:

```bash
cd ~/lost-collective
SHOPIFY_ENV=production op run --env-file=.env.tpl -- python3 shopify/scripts/push_audit_fixes.py
```

Then deploy the dashboard:

```bash
cd ~/lost-collective/dashboard && npx vercel --prod --yes
```

Then verify: open any product page on lostcollective.com, open browser console (F12), confirm zero JavaScript errors.

---

## Issues Found and Fixed

### 1. CRITICAL — options-radios.liquid: Legacy JS block throwing TypeErrors on every product page

**What it was:** A 209-line block of JavaScript at the bottom of `options-radios.liquid` was left over from an old size chart popup system that was replaced months ago. The code contained 5 size-switching functions (`showM()`, `showS()` etc.), event listener attachments, and a hidden `div` containing 15 CDN-hosted size diagram images. The `SelectedNAColor()` function at the bottom called `document.getElementById('color').style.display = "flex"` — but no element with `id="color"` exists in the current template, so this threw a `TypeError: Cannot set properties of null` on every product page load. Additionally, because the snippet is rendered once per option (Size, Type, Colour), these event listeners were being attached 3 times each per page.

**Why it mattered:** TypeErrors in inline scripts stop execution at the point of failure. While modern Shopify theme JS uses separate deferred scripts that are isolated, the inline script failure was visible in the console on every product page — a red flag for anyone debugging, and a signal that code quality is lower than it is.

**What was fixed:** The entire legacy block was removed. The modern MutationObserver approach in `product__form.liquid` already handles all of this functionality correctly. The 15 dead CDN images are also gone, removing 15 unnecessary HTTP requests from every product page.

---

### 2. HIGH — custom.css: Liquid comment tags in a plain CSS file

**What it was:** Section 5 of `custom.css` contained `{%- comment -%} ... {%- endcomment -%}` Liquid template tags. The file is named `custom.css`, not `custom.css.liquid`, so Shopify's CDN serves it as a plain text file without any Liquid processing. The Liquid tags were sent verbatim to the browser as raw text content inside the CSS stream.

**Why it mattered:** Browsers are forgiving and skip unknown tokens when parsing CSS, so there was no visible breakage — but it means the CSS that every visitor downloads contains literal `{%- comment -%}` text. It's technically invalid CSS, and it's a code quality issue that would confuse anyone doing a CSS audit.

**What was fixed:** The Liquid comment tags were replaced with a standard CSS comment block. The content of the comment was preserved — only the syntax changed.

---

### 3. HIGH — custom.css: Fragile CSS alpha hack that would break on any color variable change

**What it was:** The `.lc-edition-scarcity` rule had `background: var(--color-brand-yellow)14`. After CSS variable substitution this resolved to `background: #d4a40014`, which is a valid 8-digit hex RGBA color (8% opacity yellow) in modern browsers. It actually worked — but only because `--color-brand-yellow` resolves to a 6-digit hex value `#d4a400`. If that variable were ever changed to `rgb(212, 164, 0)` or `hsl(46, 100%, 42%)` notation, the substitution would produce invalid CSS and the background would silently disappear.

**What was fixed:** Replaced with `background: rgba(212, 164, 0, 0.08)` — explicit, readable, and immune to variable notation changes. A comment explains the intent.

---

### 4. HIGH — useLocalStorage.js: React Rules of Hooks violation

**What it was:** `useLocalStorage` called `useContext(DashboardContext)` inside a `try/catch` block, with the intention of gracefully handling cases where the hook is used outside the provider tree. This violates the React Rules of Hooks, which require hooks to be called unconditionally at the top level of a function — never inside conditionals, loops, or try/catch blocks.

**Why this matters in practice:** React's reconciliation algorithm relies on hooks being called in the same order on every render. Wrapping `useContext` in a try/catch is unstable because the hook call might or might not execute depending on whether an exception is thrown. In practice, `useContext(DashboardContext)` never throws — when called outside a provider, it simply returns the context's default value (which is `null`). The try/catch was both unnecessary and dangerous.

**What was fixed:** The try/catch was removed. `useContext` is now called unconditionally at the top level, and the null check is handled with optional chaining: `context?.addToast ?? null`. This is correct React, and it still handles the outside-provider case gracefully.

---

### 5. MEDIUM — product__images.liquid: Lazy load handler suppressing images across the entire page

**What it was:** The `lazybeforeunveil` event handler — which prevents off-screen gallery images from loading before they're selected — was attached to `document` rather than to the gallery container. This means it intercepted ALL lazy-load events on the page, including images outside the product gallery (related products slider, recommendations section, blog post thumbnails that might appear in the footer).

**What was fixed:** The handler is now attached to `galleryMain = document.querySelector('.product-gallery__main')` and wrapped in an existence check. It only intercepts events from within the product gallery, leaving all other lazy-loaded images on the page unaffected.

---

### 6. MEDIUM — social-meta-info.liquid: Homepage OG image URL improvement and documentation

**What it was:** The homepage Open Graph fallback image was a hardcoded CDN URL including a `?v=` cache-busting parameter. The URL itself is stable (it's a product image path, which doesn't change when products are updated), but the `?v=` parameter was unnecessary in this context and added confusion about whether the URL was stable.

**What was fixed:** The `?v=` parameter was stripped from the URL. The remaining URL (`https://cdn.shopify.com/s/files/1/1304/3623/products/white-bay-power-station-control-room-reference-image.jpg`) is the canonical, permanent path to the file. A detailed comment was added explaining the rationale for using this image, why it's stable, and a clear TODO for the proper long-term solution — adding a `social_image` image picker to `config/settings_schema.json` so the image can be managed from the theme customiser.

---

### 7. LOW — custom.css: Table of contents missing sections 31-33

**What it was:** The structured comment block at the top of `custom.css` listed sections 1–30, but the file contained three additional sections (31: Product Page Back Link/Price Range/Story Link; 32: Product Gallery Variant Thumbnail Strip; 33: Blog Shop CTA Block) added during the remediation without updating the TOC.

**What was fixed:** All three sections added to the table of contents.

---

### 8. LOW — Dashboard.js: Hardcoded external CDN URL for sidebar logo

**What it was:** The sidebar logo used a hardcoded Shopify CDN URL with a specific version parameter. If this image file is ever updated or replaced in Shopify, the URL would change and the dashboard logo would break silently.

**What was fixed:** The URL was extracted to a named constant `SIDEBAR_LOGO_URL` with a clear TODO comment explaining how to properly fix it (copy the logo to `dashboard/public/logo.jpg` and change the reference to `/logo.jpg`). An `onError` handler was added to hide the broken image element rather than showing a broken icon if the URL ever becomes invalid.

---

## Audit Verification: Previously Remediated Items

All 43 completed items from the audit tracker were verified against actual code. Highlights:

**Confirmed correctly implemented in code:** Blog CTA snippet (`snippets/blog-cta.liquid`) is rendering in `article__main.liquid` with the correct collection resolution logic. Article schema (`snippets/article-schema.liquid`) outputs well-formed JSON-LD. Edition scarcity bar uses MutationObserver correctly in `product__form.liquid`. Price range, back-to-collection link, and story link are all present in product pages. Logo is unified (no `logo_mobile` override in `settings_data.json`). Favicon is set. Klaviyo popup is configured with the correct "Before the next series goes live" copy. Free shipping threshold is set to $150.

**One discrepancy noted:** `product.json` still shows a Yotpo app block in the local file, but the audit tracker records it was removed "via API" on 2026-04-06. The local file is out of sync with the live theme. This is not a functional issue (removed app blocks render nothing), but the local file should be brought in sync by running `shopify theme pull --theme 143356625062 --store lost-collective.myshopify.com` after the push today. This will overwrite `product.json` with whatever is actually live.

---

## Outstanding Items (Brett Action Required)

These were flagged in the session handoff and remain unchanged:

The Klaviyo flows are confirmed live via API but the copy in `docs/klaviyo-flow-copy.md` still needs to be pasted into each flow and activated in the Klaviyo UI. The session handoff lists all 7 flows that need this manual step.

GTM still needs `claude-code-lost-collective@lost-collective-492307.iam.gserviceaccount.com` added as Editor in GTM-K898GWK via the GTM UI (can't be done programmatically without pre-existing access).

The YNAB cleanup script (`ynab.py cleanup`) is ready to run once the rate limit window clears.

---

## Next Session Recommendations

In order of commercial impact: the `social_image` settings schema addition (5 minute change, fixes the OG image story permanently). Then a `shopify theme pull` to sync local files with production. After that, the monthly blog cadence (S2 is marked in-progress) — a new location post would be the highest-SEO-leverage action available right now.

---

*Audit conducted overnight 5–6 April 2026. All fixes applied to local files. Push command above deploys to production.*
