# Series Collection Architecture
**Lost Collective — Admin Brief**
**Prepared:** 2026-04-03

---

## Purpose

This document defines the recommended Shopify collection structure for Lost Collective's 60-series photographic catalogue. Each series should have its own Shopify collection. This enables:

1. **Clean collection URLs:** `/collections/white-bay-power-station` instead of `/collections/all?sort_by=...`
2. **"More from this series" section on product pages** — the `product__series.liquid` section (now in the theme) queries `collections[series_handle]` to find sibling products. The collection handle **must match** the `custom.collection_series` metafield value exactly after `handleize`.
3. **Series landing pages** with description text, collection-level SEO, and CollectionPage structured data (now outputting from `structured-data.liquid`)
4. **Mega-menu navigation** — series collections are the menu links
5. **Internal link equity** — product pages now link "Series" labels to series collection pages

---

## The handleize rule

The theme derives the collection handle from the metafield value using Shopify's `handleize` filter:

```
"White Bay Power Station" → handleize → "white-bay-power-station"
"Kandos Cement Works" → handleize → "kandos-cement-works"
```

**When creating each collection in Shopify Admin:**
- Set the collection handle to match the handleized version of what is stored in `custom.collection_series`
- Or: set `custom.collection_series` on products to match the title you give the collection

---

## Collection setup checklist (per series)

In Shopify Admin → Products → Collections → Create collection:

1. **Title** — The full series name (e.g. "White Bay Power Station")
2. **Handle** — Must match the handleized series name (auto-generated from title, verify it)
3. **Description** — 2–4 sentences covering: what the location is, why it is significant, when it was photographed, current status. Template below.
4. **Collection image** — Upload a representative photograph from the series
5. **Sort order** — Set to "Manually" — then arrange products in editorial order
6. **Conditions** — Use manual collection (not automatic), add products individually or by tag

---

## Description template

```
[Location name] [was/is] [brief description of what it is — factory, hospital, power station, etc.]
located in [suburb/region], [state/country]. [One sentence of historical context — when built, 
what it was used for, who built it.] [One sentence about current status — demolished in [year], 
heritage listed, privately owned, abandoned since [year].] Photographed by [photographer name]
in [year].
```

**Example:**
> White Bay Power Station was a coal-fired power station located in Rozelle, New South Wales, 
> constructed in 1902 to supply electricity to Sydney's early tram network. Decommissioned in 1983 
> after 80 years of operation, it stands as one of Australia's finest examples of Edwardian industrial 
> architecture and is heritage listed under the NSW State Heritage Register. Photographed in 2018.

---

## Series list and recommended handles

Below is the naming convention. Adjust the series names in `custom.collection_series` metafields on products, or adjust collection handles, so that they match. The theme derives the link automatically — no code change required once handles align.

| Series Name (metafield value) | Recommended Collection Handle | Country |
|-------------------------------|------------------------------|---------|
| White Bay Power Station | white-bay-power-station | Australia |
| Kandos Cement Works | kandos-cement-works | Australia |
| Wangi Power Station | wangi-power-station | Australia |
| Tin City | tin-city | Australia |
| *(add remaining ~56 series)* | *(handleize the name)* | — |

**How to get the current list:**
In Shopify Admin → Products → export to CSV → look at the `custom.collection_series` column to see every unique value currently stored. These become your collection titles (and handles).

---

## Priority order for creation

Create series collections in this order of impact:

1. **Highest-product-count series first** — more products = more "More from series" widgets firing = more internal links immediately
2. **Series already featured on the homepage** — these are the most visited
3. **Series with the richest historical context** — best return on description writing effort
4. **Remaining series** — once the pattern is established, bulk creation is fast

---

## After creating collections

1. Add products to each collection manually (or bulk via CSV if needed)
2. Verify each collection URL: `https://lost-collective.myshopify.com/collections/[handle]`
3. Add series collections to the navigation menus as per `navigation-architecture-recommendation.md`
4. Write collection descriptions for at least the top 10 series before launching navigation changes
5. The "More from series" section (`product__series.liquid`) will activate automatically on product pages once the collection exists and has more than 1 product — no further theme changes needed

---

## Verifying the metafield → handle match

Visit any product page in the store. In the art details block, if the "Series" label now shows as a hyperlink, the match is working. If it shows as plain text, the collection handle does not match the handleized metafield value. Check both the metafield value and the collection handle in Admin.
