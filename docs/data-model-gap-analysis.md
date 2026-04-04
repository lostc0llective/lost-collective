# Data Model Gap Analysis
**Lost Collective — Pillar 5 Deliverable**
**Prepared:** 2026-04-04

---

## Current Data Model Summary

### Product metafields (defined and implemented)
| Key | Type | Status |
|-----|------|--------|
| `custom.collection_series` | single_line_text | Populated on all 1,809 products |
| `custom.location` | single_line_text | Defined, pending population |
| `custom.year_photographed` | integer (Admin) / single_line_text (metafields.json) | Defined, pending population |
| `custom.print_technique` | single_line_text | Defined, pending population |
| `custom.paper_type` | single_line_text | Defined, pending population |
| `custom.certificate_included` | boolean | Defined, pending population |
| `custom.edition_number` | number_integer | Added this audit — pending Admin definition + population |
| `custom.subject_description` | multi_line_text | Added this audit — pending Admin definition + population |

### Collection metafields (newly defined)
| Key | Type | Status |
|-----|------|--------|
| `custom.series_description` | rich_text | Added this audit — pending Admin definition + population |
| `custom.location_name` | single_line_text | Added this audit — pending Admin definition + population |
| `custom.year_photographed` | single_line_text | Added this audit — pending Admin definition + population |
| `custom.historical_period` | single_line_text | Added this audit — pending Admin definition + population |
| `custom.current_status` | single_line_text | Added this audit — pending Admin definition + population |

### Standard fields in use
| Field | Used for | Assessment |
|-------|----------|------------|
| `product.title` | Display, structured data, breadcrumb | Correct — "Photograph Title \| Series Name" format |
| `product.description` | Product page, meta description, schema | Correct |
| `product.vendor` | Product page (optional block) | Single-vendor store — `link_to_vendor` creates /collections/vendors?q= link. Low value but harmless. |
| `product.type` | Product page (optional block) | "Fine Art Print" across all products — `link_to_type` creates /collections/types?q= link. Low value but harmless. |
| `product.tags` | Size chart lookup (`meta-size-chart-` prefix), tag display (optional block) | Tags serve dual purpose — structured tags (meta- prefix, hidden from display) and display tags. Reasonable. |
| `variant.option1` | Size (XS/S/M/L/XL) | Correct |
| `variant.option2` | Type (Unframed/Framed/Glass) | Correct |
| `variant.option3` | Colour (Raw/White/Black/N/A) | N/A correctly hidden from display |
| `variant.sku` | Display on product page | Populated via CSV import (LC-{handle}-{size}-{type}[-{colour}] format) |

---

## IMMEDIATE GAPS

### 1. Seven of nine product metafields have no data populated

`custom.collection_series` is populated on all 1,809 products. The remaining seven (`location`, `year_photographed`, `print_technique`, `paper_type`, `certificate_included`, `edition_number`, `subject_description`) are defined and display code is in place, but no values exist yet.

**Recommended population order:**
1. `location` and `year_photographed` — highest SEO and filter value. These power Search & Discovery filters and structured data.
2. `print_technique` and `paper_type` — purchase-decision data. "Giclée on Canson Rag 310 GSM" distinguishes this store from budget print services.
3. `certificate_included` — boolean, fast to bulk-set if it applies consistently per series.
4. `subject_description` — editorial, high effort, high reward. Prioritise the top 10 series by product count.
5. `edition_number` — only relevant for pre-numbered prints. Not typically set for made-to-order.

**Approach:** Shopify CSV import. Export products, add column `Custom: Location (product.metafields.custom.location)`, populate in spreadsheet by series (all products in a series share the same location), re-import.

### 2. `product.vendor` creates a low-value link

The vendor block on product pages renders `{{ product.vendor | link_to_vendor }}` — clicking "Lost Collective" goes to `/collections/vendors?q=Lost+Collective`, a Shopify auto-generated vendor collection page. This page is probably unformatted and not useful.

**Fix options:**
- Disable the vendor block in the Theme Editor (Admin → Themes → Customize → Product page → remove Vendor block) — no code change needed
- Or change the vendor link to go to the About page or homepage instead. Code change: replace `link_to_vendor` with a plain `<a href="{{ routes.root_url }}">{{ product.vendor }}</a>` in `snippets/product.liquid` line 107.

### 3. Tags used for size chart lookup are structurally mixed with display tags

Tags prefixed `meta-size-chart-` trigger the size guide popup. These are hidden from customer display via `unless tag contains 'meta-'` (product.liquid line 364). This pattern is correct and already implemented, but it conflates configuration data with content tags.

No immediate action required — the pattern works. If you introduce more `meta-` prefix tags for other logic (e.g., `meta-no-framing`), this convention extends cleanly.

---

## MEDIUM-TERM GAPS (address when series collections are created)

### 1. Collection metafields — 62 series pages have no editorial content

All 62 series collections exist and have products assigned, but none have:
- Collection description (the existing description field in Admin)
- Custom metafields: `series_description`, `location_name`, `year_photographed`, `historical_period`, `current_status`

The collection page currently shows the product grid with no series context. For a fine art photography store where the backstory of the location is part of the value proposition, this is a missed opportunity.

**Priority order for content entry:**
1. Top 10 series by product count — White Bay Power Station (124), Hotel Motel 101 (103), Morwell Power Station (79), The Asylum (74), Callan Park (66), A Place to Call Home (64), Streetscapes of Yubari (54), Waterfall Sanatorium (54), Wangi Power Station (51), Landscapes (51).
2. Any series with active ad spend or significant organic traffic.

### 2. Variant-level data missing physical dimensions

Each size variant (XS through XL) has a fixed set of physical dimensions that are documented in the product description accordion but not structured:
- XS: 300 × 200mm
- S: 420 × 300mm
- M: 600 × 400mm
- L: 841 × 594mm
- XL: 1189 × 841mm

Currently these are in a hardcoded HTML accordion block in `templates/product.json` (the `index_html_a7B9Fd` section). If you ever want to surface dimensions next to the size selector, or include them in structured data, you would need either:
- A variant metafield `custom.dimensions` (e.g. "600 × 400mm") — populated during import
- Or a Liquid map derived from variant option1 (same approach as edition size)

The Liquid map approach is simpler for a fixed size set. No action required until you need dimensions in structured data or on the product card.

### 3. Frame depth and glass specification not structured

"6mm toughened, low-iron, bevelled-edge glass" and framing timber depth are described in the accordion but not in any metafield. Relevant for buyers comparing premium print presentation options.

Structural candidates:
- `variant.metafields.custom.frame_depth` — per-variant (only framed variants have a frame depth)
- `variant.metafields.custom.glass_spec` — per-variant (only glass variants)

Deferred until there is customer demand for this level of specification detail.

---

## LONG-TERM GAPS (address when traffic and conversion justify)

### 1. Customer metafields for collector segmentation

A buyer of print #42 of 100 in a Limited Edition is a different customer from someone buying an Open Edition XS. Distinguishing collectors from gift buyers from interior designers would enable:
- Targeted post-purchase email sequences (certificate delivery, future release notifications for collectors)
- Curated product recommendations
- Loyalty treatment for repeat collectors

**Implementation:** Shopify customer metafields (Admin → Settings → Custom data → Customers). Fields:
- `custom.buyer_type` — dropdown: Collector / Interior Designer / Gift Buyer / Unknown
- `custom.preferred_series` — list of series names or collection references

Populated via: post-purchase survey, or inferred from purchase history (buying Limited Editions M/L/XL correlates with collector behaviour).

### 2. Order metafields for custom fulfilment data

Currently no mechanism to capture:
- Dedication text (for gift orders)
- Installation instructions requested (yes/no)
- Specific wall orientation or room noted

These would live on the order as custom data and surface in the fulfilment workflow. Shopify Order metafields are writable via API but not natively via storefront cart properties without custom development.

**Low priority** until fulfilment volume justifies the tooling investment.

### 3. Series metaobject migration (Option C from Pillar 4)

When series collections have rich editorial content and traffic data confirms that buyers research series context before purchasing, migrating from the current flat `custom.collection_series` string to a Series metaobject (Option C) consolidates all series data into a single structured object.

**Not recommended before:**
- At least 20 series collections have descriptions and custom metafields populated
- Search & Discovery filters are live and generating measurable filter engagement
- You are building a dedicated series landing page beyond a standard collection page

---

## Tags Audit

Tags identified from theme code inspection (not a full product export — full audit requires exporting and grouping):

**Structural tags (hidden from customer display):**
- `meta-size-chart-{handle}` — triggers size guide popup for specific size chart pages

**Display tags (shown to customers when tag block is enabled):**
- Unknown — no product export was run as part of this audit

**Recommendation:** Run a product export and extract the Tags column. Group tag values by apparent purpose:

| Tag pattern | Likely purpose | Recommendation |
|-------------|---------------|----------------|
| Location names (e.g. "NSW", "Japan") | Geographic filtering | Replace with `custom.location` metafield once populated |
| Subject matter (e.g. "industrial", "nature") | Theme filtering | Keep as tags — complement to series navigation, not a duplicate |
| Print-related (e.g. "giclée", "limited-edition") | Type filtering | Replace with `custom.print_technique` and variant-based edition logic |
| Series names | Series filtering | Retire once `custom.collection_series` is the authoritative source and S&D filters are live |

Until Search & Discovery filters are live with metafield-based filtering, existing tags provide a useful fallback filter mechanism. Do not delete tags until metafield-based filtering is verified working.
