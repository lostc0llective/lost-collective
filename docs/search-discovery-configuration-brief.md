# Search & Discovery Configuration Brief
**Lost Collective — Shopify Admin Instructions**
**Prepared:** 2026-04-03

---

## What this achieves

Shopify's Search & Discovery app enables two things this store needs:

1. **Metafield-based filters on collection pages** — buyers can filter by location, series, print technique, or paper type without navigating away
2. **Better search relevance** — product metafields become searchable, so searching "Iceland" or "Giclée" returns relevant results

Both are configured entirely in Shopify Admin. No theme code changes are required for the filter UI — the theme's `collection__main.liquid` already has a `faceted_filtering` block type ready to use.

---

## Prerequisites

- Search & Discovery app must be installed (Shopify App Store — free)
- Custom metafields (`custom.collection_series`, `custom.location`, etc.) must be defined in Admin → Settings → Custom data → Products (see `.shopify/metafields.json` for the full list, or the architecture audit notes)
- Metafield values must be populated on products (check in Admin → Products → any product → scroll to Metafields section)

---

## Step 1 — Install Search & Discovery

Shopify Admin → Apps → Search the App Store → Search & Discovery → Install

If already installed, proceed to Step 2.

---

## Step 2 — Enable metafield filters

Shopify Admin → Apps → Search & Discovery → Filters → Add filter

Add the following filters in this order:

| Filter label | Metafield | Display type | Notes |
|-------------|-----------|--------------|-------|
| Series | `custom.collection_series` | List (single select) | Most important — enables browsing by series |
| Location | `custom.location` | List (single select) | Useful for buyers interested in specific places |
| Year | `custom.year_photographed` | List (single select) | Niche but useful for collectors |
| Print process | `custom.print_technique` | List (single select) | Important for buyers who care about print quality |
| Substrate | `custom.paper_type` | List (single select) | Secondary print detail |
| Price | Price | Price range | Standard e-commerce filter |
| Availability | Availability | Checkbox | Show in-stock only |

**Filter display type:** Use "List" for all metafield filters (not "Swatch" — no visual differentiation needed for text values).

**Filter visibility:** Apply filters to all collections, or selectively to the main browse collections (Australia, Japan, All Series). Avoid enabling filters on the Best Sellers collection where filtering by series would be confusing.

---

## Step 3 — Configure search

Shopify Admin → Apps → Search & Discovery → Search → Searchable fields

Enable these as searchable:
- Product title (default, always on)
- Product description (default)
- `custom.collection_series` — so "White Bay" returns all products from that series
- `custom.location` — so "Homebush" or "Iceland" returns relevant results
- `custom.year_photographed` — niche but enables "2019" searches
- Product tags (default)
- Product type (default)

**Search synonyms to add (Shopify Admin → Search & Discovery → Synonyms):**

| Term | Synonyms |
|------|---------|
| giclée | giclee, giclée print, archival print |
| fine art | fine-art, art print, limited edition |
| abandoned | derelict, urbex, urban exploration |
| power station | powerhouse, power plant |

---

## Step 4 — Add the filter block to collection pages in Theme Editor

1. Shopify Admin → Online Store → Themes → Customize
2. Navigate to a Collection page
3. In the left sidebar, find the Collection section
4. Add a block → select "Filtering" (or "Faceted filtering")
5. Save

This activates the Search & Discovery filter UI on collection pages. The theme's existing tag-based filters will be automatically hidden when the faceted filtering block is present (this is built into `collection__main.liquid` line 137).

---

## Step 5 — Test

1. Visit `/collections/all` — verify filter panel appears on the left/top
2. Select "Series: White Bay Power Station" — verify only those products appear
3. Select "Location: New South Wales" — verify relevant products appear
4. Run a search for "Kandos" — verify products from the Kandos series appear
5. Run a search for "Giclée" — verify the synonym maps to giclée results

---

## Note on tag-filtered URLs

The theme currently uses tag-based URLs like `/collections/best-sellers/landscape` for simple tag filtering. These are:
- **Noindexed** (already implemented in `layout/theme.liquid` — tag-filtered pages get `noindex, follow`)
- Still functional for existing tag links
- Will be **supplemented** by Search & Discovery filters (not replaced — both work in parallel)

Once Search & Discovery filters are live, you may choose to remove the legacy tag filter select dropdown from collection pages via the Theme Editor. This is optional.
