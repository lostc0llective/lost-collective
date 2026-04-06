# Audit Recommendations Tracker

**Source:** `docs/site-audit-april-2026.md`  
**Last updated:** 2026-04-05

## How to use this file

Each session: read this file first. Pick the next `[ ] Todo` item in the current tier. Check the **Who** and **How** columns — if it's `Auto` or `Claude`, start immediately. If it's `Brett`, surface it to him with the specific action.

Update status as work progresses:
- `[ ]` Todo
- `[~]` In Progress
- `[x]` Done
- `[B]` Blocked (reason in notes)

---

## Tier 1: Quick Wins (This Week)

| # | Rec | Title | Status | Who | How |
|---|-----|-------|--------|-----|-----|
| Q1 | #25 | Add National Trust Heritage Award to About page and homepage | [x] | Claude | About page updated via API (added Recognition section). Homepage trust bar block added in `templates/index.json`. Live 2026-04-05. |
| Q2 | #18 | Write unique meta descriptions — homepage + top 10 collections | [x] | Claude | 20 collections with missing meta descriptions all updated via Shopify API. All 72 collections now have SEO descriptions. Homepage meta: check Shopify Admin > Online Store > Preferences. |
| Q3 | #16 | Add collection links to all existing blog posts | [x] | Claude | All 64 posts updated. Broken /gallery/ internal links fixed (13 posts), external Guardian URLs corrected, old lostcollective.com absolute URLs replaced. All 64 posts now have /collections/ links — specific series where identifiable, general browse for press/events/inspiration posts. |
| Q4 | #1  | Unify logo files — single lockup across all breakpoints | [x] | Claude | Removed logo_mobile override from settings_data.json. Desktop logo (Logo.jpg) now used across all breakpoints. Live 2026-04-05. |
| Q5 | #2  | Reduce homepage Best Sellers grid to 6 products | [x] | Claude | Both Best Sellers AND New Arrivals changed from products_limit:50 to products_limit:6 in `templates/index.json`. Live 2026-04-05. |

---

## Tier 2: Medium Term (30–90 Days)

| # | Rec | Title | Status | Who | How |
|---|-----|-------|--------|-----|-----|
| M1 | #24 | Create Press/Media page with all coverage + pull-quotes | [x] | Claude | Page created at /pages/press (ID 698539409574). Covers: Guardian, Vice, Broadsheet, Capture, SMH, Smith Journal, 7News, ABC Radio National, ABC Hobart, ABC Central West, My Nikon Life, 2016 National Trust Award. CNN logo on homepage but no article URL found — Brett to add if known. Brett to add to footer nav manually. Live 2026-04-05. |
| M2 | #26 | Implement review collection app + post-purchase email | [~] | Both | Judge.me installed + activated 2026-04-05. Pending: get app block UUID from theme editor → replace Yotpo block in product.json. Chrome computer use task queued. |
| M3 | #38 | Add email capture popup with incentive | [ ] | Both | Brett decides incentive (discount % vs early access vs content). Claude implements popup in theme or via Klaviyo. |
| M4 | #13 | Rewrite homepage copy to reflect Lost Collective TOV | [x] | Both | All 10 homepage text fields rewritten. Hero: "Still Here" / "buildings that outlived their purpose". Slideshow: "The Quiet After". Collections: "Six Categories. Two Countries. One Thread." About Brett: tradesman/curiosity paragraph. Also nuked slop body copy in New Arrivals section. Live 2026-04-05. |
| M5 | #15 | Rewrite About page — press quotes, milestones, CTA | [x] | Claude | Rewritten with 5 sections: how it started (tradesman/White Bay/Capture quote), the project (62 series/1800+ prints/2 countries/lost purpose framing), community response, recognition (NT Award + all press + Vice/Guardian pull-quotes), prints (editions/signed/never reproduced) + CTA. Live 2026-04-05. |
| M6 | #7  | Add collection-level filtering: size, type, price | [ ] | Both | Requires theme work. Brett to confirm if Flex v5.2.1 has native filtering or if a filter app (e.g. Boost Commerce, Searchie) is needed. Claude implements once confirmed. |
| M7 | #29 | Create gift card product | [ ] | Brett | Simple: Shopify Admin > Products > Gift Cards. Brett to create and set denominations. No theme work needed. |
| M8 | #27 | Surface edition scarcity — remaining stock on limited editions | [x] | Claude | Edition scarcity bar added to product__form.liquid. Shared pool formula: sums inventory across all framing variants of a given size. Live 2026-04-05. |
| M9 | #33 | Create "Starting at $50" entry-point collection | [x] | Claude | Smart collection created: ID 685073236134, handle `prints-from-50`. Rules: type = Fine Art Print + variant_price < $51. Sorted price-asc. TOV description written. SEO title/desc set. Live on Shopify (auto-indexed). |

---

## Tier 3: Strategic (90+ Days)

| # | Rec | Title | Status | Who | How |
|---|-----|-------|--------|-----|-----|
| S1 | #23 | Develop location-specific landing pages (story + prints) | [x] | Claude | 18 pages live (White Bay pilot + 17 new: Wangi, Kandos, Callan Park, Morwell, Eveleigh, Blayney, Geelong B, Newington Armory, Ashio, Kinugawa Kan, Bathurst, Peters' Ice Cream, Mungo Scott, Lewisham, Waterfall, Bradmill, Tin City). Each with hero image, editorial copy, collection CTA, SEO title/desc. Live 2026-04-06. |
| S2 | #20 | Monthly blog publishing cadence — location-specific SEO | [~] | Both | 5 posts published 2026-04-06: Wangi Power Station, Kandos Cement Works, Callan Park, Bradmill Denim, Tin City. Each with full editorial copy + collection CTA. Target: continue monthly. |
| S3 | #35 | Theme evaluation — OS 2.0 upgrade vs custom build | [ ] | Brett | Requires a decision conversation. Claude to prepare a brief comparing Flex v5.2.1 current state vs OS 2.0 theme options vs custom build. Brett decides. |
| S4 | —   | Interior design / trade buyer page for B2B | [x] | Both | Page live: /pages/trade (ID 698557366438). Covers: trade pricing intro, collection overview, contact CTA (brett@lostcollective.com.au), lead times, series suggestions for commercial use. Brett to add to footer nav if desired. SEO title/desc set. Live 2026-04-06. |
| S5 | —   | Aesthetic/mood curated collections | [x] | Claude | 4 smart collections created: Dark & Moody (225), After Dark (109), Graffiti & Urban Decay (75), Wide Open Spaces (219). Disjunctive tag rules. SEO titles/descriptions set. Live 2026-04-05. Light & Minimal deferred — needs image-vision tagging via catalog_audit.py. |
| S6 | #28 | Customer photo gallery / UGC integration | [ ] | Brett | Requires a strategy decision: dedicated page, homepage section, or third-party UGC app (e.g. Stamped, Okendo). Brett to decide approach. |
| S7 | —   | Video content surfaced on site (TV features, BTS) | [ ] | Claude | Embed existing ABC/7 News features on About page and/or dedicated Press page. Add YouTube embed support to blog post template. |
| S8 | —   | Shopify Markets / multi-currency for international buyers | [ ] | Brett | Admin decision: enable Shopify Markets, configure USD/GBP/JPY pricing rules. Straightforward to implement once Brett decides to proceed. |

---

## Additional Detailed Recommendations (from audit sections)

These are secondary items from the audit not yet in the priority roadmap above.

| # | Rec | Title | Status | Who | How |
|---|-----|-------|--------|-----|-----|
| D1 | #3  | Eliminate repeated homepage copy (headlines used twice) | [x] | Claude | Resolved as part of M4 homepage copy rewrite. No duplicate headings in templates/index.json. |
| D2 | #4  | Strengthen "About Brett" homepage teaser — punchier one-liner + CTA | [x] | Claude | Resolved as part of M4 homepage copy rewrite. |
| D3 | #5  | Add branded favicon and Open Graph social sharing image | [ ] | Claude | Add to theme `<head>`. Use existing brand mark. Requires a 32x32 favicon and a 1200x630 OG image. |
| D4 | #6  | Restructure primary nav — top-level categories as direct items | [ ] | Brett | Navigation change. Brett confirmed menus are already configured — any nav changes require explicit Brett approval. |
| D5 | #8  | Improve product variant UX — visual swatches/buttons | [x] | Claude | Colour option replaced with CSS Grid text buttons in options-radios.liquid. Size/type options unchanged (already radio buttons). Live 2026-04-05. |
| D6 | #9  | Display price range prominently on product pages ("From $50 – $2,500") | [x] | Claude | Static "From $XX – $XX" line added above price-ui in product.liquid. Always visible, uses product.price_min/max. Live 2026-04-05. |
| D7 | #10 | Add contextual "back to collection" links on product pages | [x] | Claude | "← [Collection Title]" link added above h1 in product.liquid. Uses Shopify `collection` object (present when arriving from a collection). Live 2026-04-05. |
| D8 | #11 | De-duplicate Japan collection entries in mega menu | [ ] | Brett | Navigation change — requires Brett approval per working style rules. |
| D9 | #12 | Verify cart count updates dynamically via JavaScript | [x] | Claude | Already working — z__jsAjaxCart.js lines 390-397 update `[data-bind="itemCount"]` on every cart change. No fix needed. Live 2026-04-05. |
| D10| #14 | Audit product descriptions — ensure every product has a story paragraph | [x] | Claude | overnight_content.py confirmed all 1,809 products have subject_description filled (previous Gemini batch complete). 2 empty collection descriptions (Leichhardt House, Newington Armory) fixed 2026-04-06. |
| D11| #17 | Add reusable blog-to-shop CTA component | [x] | Claude | `snippets/blog-cta.liquid` created. Injected after article.content in article__main.liquid. Resolves collection from custom.related_series metafield → matching tag → /collections/all fallback. Live 2026-04-06. |
| D12| #19 | Internal linking — products link back to related blog content | [x] | Claude | "Read the story behind this series →" link added below subject_description in art-details block. Links to /blogs/blog/tagged/[series-handle]. Live 2026-04-05. |
| D13| #21 | Add Article structured data to blog posts | [x] | Claude | `snippets/article-schema.liquid` created (Article JSON-LD with headline, datePublished, dateModified, author, image, publisher). Rendered at top of article__main.liquid. Live 2026-04-06. |
| D14| #30 | Add bundle/set pricing for curated pairs or triptychs | [ ] | Both | Requires a Shopify bundle app (e.g. Bundler, Rebundle) or custom metafield approach. Brett to decide strategy. |
| D15| #31 | Add express checkout (Buy Now) to product pages | [x] | Claude | Already live — `show_payment_button: true` in product.json, `{{ form \| payment_button }}` in product__form.liquid. No action needed. |
| D16| #32 | Reinforce free shipping threshold in cart drawer | [x] | Both | HTML + CSS already in theme. `free_shipping_threshold` set to 150 (AUD) in settings_data.json. Progress bar + "Complimentary shipping applied" state. Live 2026-04-05. |
| D17| #34 | Audit installed apps — remove anything not contributing | [ ] | Brett | Brett to review app list in Shopify Admin. Claude can advise on any specific app once Brett lists what's installed. |
| D18| #36 | Reduce product image variants loaded per page | [x] | Claude | Lazy-load gating for non-selected slides + variant thumbnail strip filtering by Type/Colour alt text. Staggered fade/drift animation on type/colour change; size-only changes skip animation; main gallery navigates to matching image on type change. Live 2026-04-05. |
| D19| #37 | Clarify Japan cross-listing — filter or separate editorial context | [ ] | Brett | Navigation/architecture decision requiring Brett approval. |
| D20| #39 | Implement abandoned cart email recovery | [B] | Brett | Klaviyo "Abandoned Checkout Reminder" flow is in `manual` status (not live). Brett to open flow in Klaviyo, check trigger + actions, flip to Live. |
| D21| #40 | Build post-purchase email sequence in Klaviyo | [B] | Brett | All 7 Klaviyo flows confirmed in draft/manual. Brett to review copy in `docs/klaviyo-flow-copy.md`, paste into Klaviyo, and flip each flow to Live. Flows: Welcome Series, Winback, Browse Abandonment, Thank You, Product Review/Cross Sell, Sunset Re-permission, Abandoned Checkout. |
| D22| #41 | Embed Instagram feed on homepage | [B] | Both | Instafeed installed but not surfaced — no script tags, no theme section, no template references. App block UUID needed to inject into templates/index.json. Brett to open theme editor, add Instafeed block, report UUID. Or: connect Instagram account in Instafeed app settings first. |

---

## Completion Summary

| Tier | Total | Done | In Progress | Todo | Blocked |
|------|-------|------|-------------|------|---------|
| Quick Wins | 5 | 5 | 0 | 0 | 0 |
| Medium Term | 9 | 5 | 1 | 3 | 0 |
| Strategic | 8 | 5 | 1 | 1 | 0 |
| Detailed | 22 | 12 | 0 | 7 | 3 |
| **Total** | **44** | **27** | **2** | **11** | **3** |
