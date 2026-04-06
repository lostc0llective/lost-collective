# Lost Collective Website Audit

## Comprehensive Ecommerce Review — April 2026

**Prepared for:** Brett Patman, Lost Collective  
**Site:** lostcollective.com (Shopify)  
**Scope:** Full-spectrum audit — design, UX, content, SEO, CRO, architecture, integrations

---

## Executive Summary

Lost Collective is a photography fine art print store with world-class source material, significant press credibility (CNN, Guardian, Vice, ABC, 7 News, National Trust), and a clear creative vision. The photography is exceptional and the brand story is compelling. However, the website is currently underperforming its potential as a commercial platform. The site functions more as a portfolio with a shop attached than a purpose-built ecommerce experience designed to convert visitors into buyers.

The core problem is not the quality of the work or the brand — it is that the site does not systematically guide visitors through the journey from discovery to purchase. There is a disconnect between the storytelling (blog), the social proof (press), the product catalogue, and the checkout experience. Each element exists, but they do not work together as an integrated conversion system.

**Overall assessment:** Strong foundations. The photography, brand story, press coverage, and product quality are all genuine competitive advantages. The site needs strategic restructuring, not a ground-up rebuild. The biggest gains will come from CRO improvements, content-to-commerce linking, social proof deployment, and SEO fundamentals — not from a new theme or visual redesign.

---

## 1. Brand & Visual Design

### What is working

- The visual identity is clean, dark, and photographic — appropriate for a fine art photography brand.
- Product photography is excellent. The framed/unframed/glass mockup system is well-executed.
- The hero section uses a video background (Brett exploring an abandoned building), which is atmospheric and on-brand.
- The media logo bar (CNN, Guardian, Vice, ABC, SMH, etc.) is present on the homepage.
- The collection category images (Commercial, Industrial, Medical, Landscapes, Rural, Japan) are well-chosen and visually distinct.

### What needs attention

- Two different logos appear across the site. The header uses `Logo_2000x.jpg` and the mobile/sticky header uses `lost-collective-logo_2000x.jpg`. These need to be unified.
- The homepage is too long. It displays a Best Sellers section with 48 products in a scrolling grid, then a New Arrivals section with another 28+ products. A fine art print shop should feel selective, not exhaustive. Recommendation: Show 4–6 hero products per section maximum, with a clear "View All" link.
- Repeated messaging. "Art That Tells a Story" appears twice on the homepage. "Preserving History Through Art" appears twice.
- The "About Brett" section on the homepage is too small and generic.
- No favicon or social sharing image is evident from the markup.

### Recommendations

1. Unify logo files to a single, consistent lockup across all breakpoints.
2. Reduce homepage product grids to 4–6 curated picks per section.
3. Rewrite homepage section copy to eliminate repetition and strengthen each section's distinct purpose.
4. Strengthen the "About Brett" homepage teaser — use a compelling one-liner and a stronger CTA.
5. Add a branded favicon and Open Graph social sharing image.

---

## 2. UX & Navigation

### Site Architecture

**Primary nav:** All Collections | New | Best Sellers | About | Blog

**Mega menu dropdowns:** Commercial (4 locations), Industrial (8 locations), Medical (4 locations), Landscapes (4 sub-collections), Rural (3 sub-collections), Japan (6 locations)

### What is working

- The mega menu organisation by category and then by specific location/series is logical.
- Breadcrumbs are present on product pages.
- The search function includes the contextual prompt: "Search by location, building, or theme."

### What needs attention

- Navigation hierarchy is confusing. "All Collections" as a primary nav item leads to a mega menu with 30+ sub-collections.
- "New" and "Best Sellers" are structurally identical — both lead to flat product grids with no contextual difference.
- No filtering or sorting on collection pages. Given 100+ products per collection, visitors cannot filter by price, size, type, or sort by date/popularity.
- Product page variant selection is complex. 25 variants (5 sizes × 3 frame types + glass + unframed) via three sequential dropdowns.
- The cart icon always shows "0" even when items are in the cart — possible JS rendering issue.
- No "back to collection" or contextual navigation on product pages.
- Japan collection appears twice in the mega menu (top-level and as sub-items duplicating entries from other categories).

### Recommendations

6. Restructure primary nav to show top-level categories (Commercial, Industrial, Medical, Landscapes, Rural, Japan) directly, with sub-collections in a cleaner dropdown.
7. Add collection-level filtering: by size, type (unframed/framed/glass), and price range.
8. Improve product page variant UX — consider visual selector (thumbnail swatches for frame type, button group for size) instead of three sequential dropdowns.
9. Display the price range prominently on product pages ("From $50 – $2,500") with clear size/type correlation.
10. Add contextual "back to collection" links that remember the visitor's browsing path.
11. De-duplicate Japan collection entries in the mega menu.
12. Verify cart count updates dynamically via JavaScript.

---

## 3. Content & Copywriting

### Assessment

The copy is competent but generic. Phrases like "spark conversation," "transform your walls," "bring a unique touch to your home or office," and "evoke emotion" are category-level language, not brand-specific language. The Lost Collective TOV describes the brand voice as: specific and grounded, unpretentious, people-first, history woven naturally, confident on subject, visceral sensory writing, unexpected angles, dry humour. Almost none of these traits come through in the current website copy.

The blog is a genuine asset — the Kinugawa Kan post is a 12-minute deep-dive with historical postcards, archival research, and personal narrative. But blog posts do not link to corresponding print collections. The Kinugawa Kan post does not include a single link to the Kinugawa Kan print collection. This is the single biggest missed conversion opportunity on the entire site.

### Recommendations

13. Rewrite homepage copy to reflect the established TOV — specific, grounded, unpretentious.
14. Ensure every product has a descriptive story paragraph, not just a title and specs.
15. Rewrite the About page with more personal specificity, press quotes, project milestones, and a clear CTA.
16. Add contextual product/collection links to every blog post.
17. Add a blog-to-shop CTA component ("Explore prints from this series") reusable across posts.

---

## 4. SEO Technical Audit

### What is working

- Shopify handles baseline technical SEO (sitemap, canonical tags, SSL, mobile responsiveness).
- Product pages have structured data (Shopify defaults).
- Blog is on the same domain (lostcollective.com/blogs/blog).
- Image alt text is present on many images and is descriptive.
- Clean URL structure.

### What needs attention

- Meta descriptions are identical across multiple pages: "Shop museum-quality wall art photography prints of abandoned places. Own a hauntingly beautiful piece of history. Explore the collection today." Every page needs a unique meta description.
- Heading structure: "Art That Tells a Story" appears twice as H2 on the homepage.
- Internal linking creates content silos — blog and products are disconnected from an SEO perspective.
- Homepage loads images at 2000px width. 48 best-seller thumbnails + 28 new arrivals + 6 category images + 18 media logos + hero images is significant image weight.
- Blog post frequency: 7 posts visible, most recent March 2025, with a gap from September 2022 to February 2025.
- No Article structured data on blog posts beyond Shopify defaults.

### Keyword Opportunities

- "[Location name] abandoned" (e.g., "White Bay Power Station abandoned", "Kinugawa Kan abandoned")
- "Abandoned places photography prints"
- "Urban exploration wall art"
- "Fine art prints abandoned buildings Australia"
- "Haikyo photography prints Japan"
- "Industrial photography wall art"
- "Abandoned hospital photography"

### Recommendations

18. Write unique meta descriptions for every page — homepage, each collection, each product, each blog post.
19. Build internal links between blog posts and their corresponding product collections.
20. Publish blog content on a regular cadence (monthly minimum) targeting location-specific long-tail keywords.
21. Add Article structured data to blog posts.
22. Audit and reduce homepage image load — fewer products displayed = faster page + stronger curation signal.
23. Consider adding location-specific landing pages that combine story (blog-style content) with prints (product grid) on a single page.

---

## 5. Conversion Rate Optimisation (CRO)

### Trust & Social Proof

- Press logos are present but underutilised — no links to articles, no pull-quotes.
- Product reviews are nearly absent. "Yummy" product page shows "5.0 / 5.0 — 1 Review." One review is worse than no reviews — it signals low sales volume.
- No customer testimonials anywhere on the site. No photos of prints installed in homes.
- The National Trust Heritage Award is not mentioned anywhere on the website.
- No consolidated press/media page.

### Pricing & Value Communication

- Products start at $50 (XS unframed) and go to $2,500 (XL framed).
- "Once sold out, they are never reproduced" is hidden inside a collapsible accordion — should be above the fold.
- No indication of edition sizes or remaining stock.
- The $50 entry point is not prominently featured.

### Checkout & Purchase Flow

- No "Buy Now" or express checkout option visible — only "Add to Cart."
- Free shipping threshold ($150) communicated via top-of-page banner — good, but could be reinforced more actively in the cart.
- Payment options are comprehensive: Apple Pay, Google Pay, Shop Pay, credit cards.
- No gift card option visible.
- No bundling or set discounts.

### Recommendations

24. Create a Press/Media page consolidating all coverage with links and pull-quotes. Link from footer and About page.
25. Add the National Trust Heritage Award to the About page and homepage.
26. Implement a review collection system (Judge.me, Loox, or Shopify native reviews) with automated post-purchase emails.
27. Surface edition scarcity — display remaining edition count on limited edition products.
28. Add customer photos/testimonials — a "Share your print" campaign on Instagram with a branded hashtag.
29. Create a gift card product.
30. Add bundle/set pricing for curated pairs or triptychs.
31. Add express checkout (Buy Now) to product pages.
32. Reinforce free shipping threshold in the cart drawer.
33. Create a dedicated "Starting at $50" entry-point collection for gift shoppers and first-time buyers.

---

## 6. Shopify Architecture & Technical

### Assessment

- Two distinct logo images are loaded for desktop vs mobile headers, adding unnecessary HTTP requests and brand inconsistency.
- The variant selector uses a traditional dropdown approach — modern Shopify themes have moved to visual swatches.
- Product image count is very high: "Yummy" loads 25 product images (5 variants × 5 views each).
- Products cross-listed between Japan and other categories creates navigation confusion — the same collection is accessible from two paths with no differentiation.

### Recommendations

34. Audit installed apps — remove any not actively contributing to conversion or operations.
35. Consider a theme upgrade or custom rebuild if the current theme is significantly customised legacy code. A modern OS 2.0 theme with native visual swatches, predictive search, and better section flexibility would improve both UX and maintainability.
36. Reduce product image variants loaded per page — consider loading additional views on variant selection rather than all at once.
37. Clarify the Japan cross-listing — either make Japan a filter rather than a separate collection, or give the Japan collection page its own editorial context.

---

## 7. Email & Marketing Integrations

### What is present

- Newsletter signup in the footer: "Stay in the Loop." No incentive offered.
- No visible popup or slide-in email capture.

### What is missing

- No post-purchase email flow visible.
- No email capture incentive.
- No SMS marketing presence.
- Instagram feed not embedded on the site despite 14,000 followers.

### Recommendations

38. Add an email capture popup with a compelling incentive (first access to new releases, behind-the-scenes content, or a modest discount).
39. Implement abandoned cart email recovery if not already active.
40. Build a post-purchase email sequence: order confirmation with story context, delivery follow-up, review request, cross-sell related prints.
41. Consider embedding an Instagram feed or curated grid on the homepage.

---

## 8. Competitive Positioning

### Genuine competitive advantages

1. The story is real and unique — specific location, specific history, specific moment of access.
2. Press coverage at a scale most art photographers never achieve: CNN, Guardian, Vice, ABC, 7 News, National Trust Heritage Award, Capture Magazine, Nikon, SMH.
3. Community connection — former workers and residents reaching out with their own stories and photos.
4. Museum-grade production quality: Canson Infinity Rag Photographique 310 GSM, Epson UltraChrome HD, 100+ year fade resistance.
5. Australia + Japan dual geographic focus.

### What competitors do better

- Customer photos in context — prints on real walls in real homes (not just mockups).
- Artist video — a short documentary or interview creating emotional connection.
- Limited edition urgency — countdown or stock level displays.
- Interior design positioning — explicitly targeting architects, interior designers, and hospitality buyers.
- Curated selections — aesthetic/mood-based curation rather than purely geographic.

---

## 9. Priority Roadmap

### Quick Wins (This Week)

1. Add National Trust Heritage Award to About page and homepage. **[Rec #25]**
2. Write unique meta descriptions for the homepage and top 10 collection pages. **[Rec #18]**
3. Add collection links to all existing blog posts. **[Rec #16]**
4. Unify logo files. **[Rec #1]**
5. Reduce homepage Best Sellers grid to 6 products. **[Rec #2]**

### Medium Term (30–90 Days)

1. Create a consolidated Press/Media page. **[Rec #24]**
2. Implement a review collection app with post-purchase email automation. **[Rec #26]**
3. Add email capture popup with incentive. **[Rec #38]**
4. Rewrite homepage copy to reflect the Lost Collective TOV. **[Rec #13]**
5. Rewrite the About page with press quotes, milestones, and CTA. **[Rec #15]**
6. Add collection-level filtering (size, type, price). **[Rec #7]**
7. Create a gift card product. **[Rec #29]**
8. Add edition count/remaining stock display to limited edition products. **[Rec #27]**
9. Build a "Starting at $50" gift/entry-point collection. **[Rec #33]**

### Strategic (90+ Days)

1. Develop location-specific landing pages combining story + prints. **[Rec #23]**
2. Monthly blog publishing cadence targeting location-specific long-tail SEO. **[Rec #20]**
3. Theme evaluation — assess whether a modern OS 2.0 theme or custom build would improve variant UX, page speed, and section flexibility. **[Rec #35]**
4. Interior design / trade buyer page for B2B opportunities.
5. Curated collections based on aesthetic/mood rather than geography.
6. Customer photo gallery / UGC integration. **[Rec #28]**
7. Video content surfaced on site (existing TV features, behind-the-scenes footage).
8. Consider Shopify Markets or multi-currency setup for international buyers.

---

## 10. Final Assessment

Lost Collective has something most ecommerce brands would kill for: a genuine story, world-class press coverage, a distinctive product, and a loyal community. The website's challenge is not awareness or quality — it is conversion architecture. The site needs to stop acting like a portfolio and start acting like a store that happens to have an incredible story behind it.

Every recommendation in this audit is designed to make the existing assets work harder, not to create new ones from scratch.

---

*Audit conducted April 2026. Based on live site review of lostcollective.com homepage, About page, product pages, blog, collection structure, and publicly available source code/markup.*
