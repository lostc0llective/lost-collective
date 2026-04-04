# Series Data Architecture — Recommendation
**Lost Collective — Pillar 4 Deliverable**
**Prepared:** 2026-04-04

---

## RECOMMENDATION: Option A — Keep `collection_series` as `single_line_text`

Augment with collection-level metafields (Pillar 3) rather than migrating the product metafield type.

**Reasoning follows.**

---

## Current State

`product.metafields.custom.collection_series` is a `single_line_text_field` storing the series name (e.g. "White Bay Power Station"). It is accessed in four places in the theme:

| File | Usage | Pattern |
|------|-------|---------|
| `snippets/product.liquid` | Display + link | Reads `.value`, handleizes, looks up `collections[handle]`, links to series collection |
| `snippets/product-schema.liquid` | Structured data | Reads `.value` as a PropertyValue string |
| `sections/product__series.liquid` | Sibling product display | Reads `.value`, derives collection handle, iterates `series_collection.products` |
| `sections/search__main.liquid` | Search result annotation | Reads `.value` for display text only |

In all four locations the metafield is used as **display text + a handle derivation key**, never as a direct object reference. The Liquid pattern is:

```liquid
assign series_name = product.metafields.custom.collection_series.value
assign series_handle = series_name | handleize
assign series_collection = collections[series_handle]
```

This works reliably: the 62 series all have confirmed matching collections (audited 2026-04-04, 0 missing).

---

## Option Analysis

### Option A — Keep as `single_line_text` + add collection metafields

**What it is:** Current state. The metafield stores the series name string. The theme derives the collection handle via `| handleize` and looks up the collection object via `collections[handle]`.

**Pros:**
- 1,809 products already populated — zero migration cost
- All four template access points work correctly today
- Adding editorial richness to series is done via collection metafields (implemented in Pillar 3 of this audit), not by changing the product metafield type
- Handle derivation is stable: all 62 series names handleize to unique, collision-free handles (verified in series audit)

**Cons:**
- The `collections[handle]` global lookup is a Liquid object access that loads the collection object at render time. It works, but it is a handle-based lookup rather than a direct reference. Not a performance concern — Shopify resolves these efficiently.
- If a series is renamed, the metafield value must be re-imported to match. But given that all 62 names are canonical and the collections exist, renaming risk is low.

**When this stops being the right choice:** If you need to display the series collection's image, description, or custom metafields (location, historical period etc.) directly on the product page — without the merchant manually maintaining consistency between product metafields and collection data. At that point Option B becomes worthwhile.

---

### Option B — Change to `collection_reference`

**What it is:** Products store a direct Shopify collection reference (GID) instead of a text string. `product.metafields.custom.collection_series.value` returns the full collection object.

**Template change — before (current):**
```liquid
assign series_name = product.metafields.custom.collection_series.value
assign series_handle = series_name | handleize
assign series_collection = collections[series_handle]
{% if series_collection != blank %}
  <a href="{{ series_collection.url }}">{{ series_name }}</a>
{% endif %}
```

**Template change — after (Option B):**
```liquid
assign series_collection = product.metafields.custom.collection_series.value
{% if series_collection != blank %}
  <a href="{{ series_collection.url }}">{{ series_collection.title }}</a>
{% endif %}
```

**What becomes possible that is not currently possible:**
- `series_collection.image` — display the series hero image on the product page without an extra lookup
- `series_collection.description` — output the series editorial description in product context
- `series_collection.metafields.custom.location_name` — show series location directly from product context, eliminating the need for the duplicate `custom.location` product metafield for collection-level data
- Direct reference integrity — if a series collection is deleted, the metafield reference goes blank; no orphaned text strings

**Migration cost:**
1. Admin → Settings → Custom data → Products → `collection_series` → change type from `single_line_text_field` to `collection_reference`. **This clears all 1,809 existing values.**
2. Re-import via CSV: each product row needs the collection GID in the metafield column (format: `gid://shopify/Collection/123456789`). Requires a script to map series name → collection GID for all 1,809 products.
3. Update four Liquid template files to use `.value.title`, `.value.url`, `.value.handle` instead of `.value` + handleize.

**Verdict:** High migration cost, moderate long-term benefit. Not worth doing until the series collections have rich editorial content (descriptions, images, custom metafields populated). Revisit when at least 20 series collections have content in the Pillar 3 metafields.

---

### Option C — Series Metaobject

**What it is:** A `series` metaobject type is created. Each series is an entry. Products reference their Series metaobject. The metaobject stores all series data: title, description, location, historical period, image, collection reference.

**Relationship diagram:**
```
Product
  └── custom.collection_series (metaobject_reference)
        └── Series metaobject
              ├── title (single_line_text)
              ├── description (rich_text)
              ├── location (single_line_text)
              ├── year_photographed (single_line_text)
              ├── historical_period (single_line_text)
              ├── current_status (single_line_text)
              ├── hero_image (file_reference)
              └── collection (collection_reference → Shopify Collection)
```

**Complete metaobject field definition:**

| Field | Key | Type | Required | Purpose |
|-------|-----|------|----------|---------|
| Series name | `title` | single_line_text | Yes | Display name |
| Description | `description` | rich_text | No | Editorial narrative |
| Location | `location` | single_line_text | No | Geographic location |
| Year photographed | `year_photographed` | single_line_text | No | Year or range |
| Historical period | `historical_period` | single_line_text | No | Operational dates |
| Current status | `current_status` | single_line_text | No | Current state |
| Hero image | `hero_image` | file_reference | No | Series feature image |
| Shopify collection | `shopify_collection` | collection_reference | No | Links to browseable collection |

**Template access (Liquid):**
```liquid
assign series = product.metafields.custom.collection_series.value
{% if series != blank %}
  <a href="{{ series.shopify_collection.value.url }}">{{ series.title.value }}</a>
  {{ series.description.value }}
  {{ series.location.value }}
{% endif %}
```

**Benefits over Option B:**
- Single source of truth for all series data — no duplication between product metafields and collection metafields
- Series data is independent of Shopify's collection system — exists even if no collection is created
- Supports future use cases: series landing pages rendered from metaobject entries, API-driven series indexes
- Location and editorial data stored once per series, not per-product

**Honest complexity assessment:**
- Metaobject creation, 62 series entries, product re-import (1,809 records with GID references): 1–2 days of work
- Template changes: 4 files, straightforward substitution
- Admin burden: every new product must reference the correct Series metaobject entry

**Recommended trigger point:** Pursue Option C when:
1. Series collections have enough editorial content that showing it on product pages would meaningfully improve conversion
2. You have traffic data showing buyers research series before purchasing
3. You are building a series landing page experience beyond a standard Shopify collection page

---

## Which metafields are unaffected by any option change

These product metafields have no dependency on the `collection_series` architecture decision:

- `custom.location`
- `custom.year_photographed`
- `custom.print_technique`
- `custom.paper_type`
- `custom.certificate_included`
- `custom.edition_number`
- `custom.subject_description`
- `reviews.rating`
- `reviews.rating_count`

Only `custom.collection_series` itself changes in Options B and C.

---

## Current action

Option A confirmed. Collection metafields have been added to `.shopify/metafields.json` (collection array) and conditional display slots added to `sections/collection__main.liquid`. These render nothing until the merchant creates the definitions in Admin → Settings → Custom data → Collections and enters values.

**To activate:** Admin → Settings → Custom data → Collections → Add definition, using the keys and types from the collection array in `.shopify/metafields.json`.
