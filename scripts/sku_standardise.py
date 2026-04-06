"""
SKU Standardisation — Lost Collective
======================================
Generates missing SKUs for all product variants using the standard format:
  LC-{handle}-{size}-{type-abbrev}[-{colour}]

Where:
  type:   Unframed → UF | Framed → FR | Glass → GL
  size:   XS / S / M / L / XL  (kept as-is)
  colour: Raw → R | White → W | Black → B | N/A → (omitted)

Examples:
  terminus-hotel-bar / XS / Unframed / N/A  → LC-terminus-hotel-bar-XS-UF
  terminus-hotel-bar / XS / Glass / N/A     → LC-terminus-hotel-bar-XS-GL
  terminus-hotel-bar / XS / Framed / Black  → LC-terminus-hotel-bar-XS-FR-B
  terminus-hotel-bar / M / Framed / Raw     → LC-terminus-hotel-bar-M-FR-R

Only sets SKUs that are currently blank/None — never overwrites existing SKUs.

Usage:
  op run --env-file=.env.tpl -- python3 shopify/scripts/sku_standardise.py
  op run --env-file=.env.tpl -- python3 shopify/scripts/sku_standardise.py --dry-run
  op run --env-file=.env.tpl -- python3 shopify/scripts/sku_standardise.py --limit 20

Output:
  logs/sku_standardise.log
"""

import sys, time, argparse
from pathlib import Path

LOG_FILE = Path("logs/sku_standardise.log")
LOG_FILE.parent.mkdir(exist_ok=True)
_log_fh = open(LOG_FILE, "w")

def log(msg: str):
    print(msg)
    _log_fh.write(msg + "\n")
    _log_fh.flush()

sys.path.insert(0, str(Path(__file__).parent))
from shopify_gql import gql, iter_products

# ── Option value mappings ──────────────────────────────────────────────────────

TYPE_ABBREV = {
    "unframed": "UF",
    "framed":   "FR",
    "glass":    "GL",
}

COLOUR_ABBREV = {
    "raw":   "R",
    "white": "W",
    "black": "B",
    "n/a":   None,
    "":      None,
}

# ── Variant query ──────────────────────────────────────────────────────────────

VARIANTS_QUERY = """
query getVariants($id: ID!) {
  product(id: $id) {
    id
    handle
    variants(first: 50) {
      edges {
        node {
          id
          sku
          selectedOptions { name value }
        }
      }
    }
  }
}
"""

VARIANTS_BULK_UPDATE = """
mutation productVariantsBulkUpdate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkUpdate(productId: $productId, variants: $variants) {
    productVariants { id sku }
    userErrors { field message }
  }
}
"""

# ── SKU generation ─────────────────────────────────────────────────────────────

def build_sku(handle: str, size: str, type_val: str, colour_val: str) -> str:
    type_abbrev   = TYPE_ABBREV.get(type_val.lower(), type_val.upper()[:2])
    colour_abbrev = COLOUR_ABBREV.get(colour_val.lower())
    parts = ["LC", handle, size, type_abbrev]
    if colour_abbrev:
        parts.append(colour_abbrev)
    return "-".join(parts)

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit",   type=int, help="Max products to process")
    args = parser.parse_args()
    dry_run = args.dry_run

    log("=" * 60)
    log("SKU Standardisation — Lost Collective")
    log(f"Mode: {'dry-run' if dry_run else 'live'}")
    log("=" * 60)

    products_processed = 0
    variants_set       = 0
    variants_skipped   = 0
    errors             = 0

    for product in iter_products(page_size=50):
        if args.limit and products_processed >= args.limit:
            break

        resp = gql(VARIANTS_QUERY, {"id": product["id"]})
        p    = resp["data"]["product"]
        handle = p["handle"]

        missing = []
        for ve in p["variants"]["edges"]:
            v = ve["node"]
            if v.get("sku"):
                variants_skipped += 1
                continue

            # Extract options
            opts = {o["name"].lower(): o["value"] for o in v["selectedOptions"]}
            size      = opts.get("size", "")
            type_val  = opts.get("type", "")
            colour    = opts.get("colour", opts.get("color", "N/A"))

            if not size or not type_val:
                log(f"  ✗ {handle}: missing size/type options — {opts}")
                errors += 1
                continue

            sku = build_sku(handle, size, type_val, colour)
            missing.append((v["id"], sku, f"{size}/{type_val}/{colour}"))

        if missing:
            log(f"\n{handle} — {len(missing)} missing SKUs")
            for vid, sku, opts_str in missing:
                log(f"  {opts_str:<30} → {sku}")

            if not dry_run:
                # Bulk update all missing SKUs for this product in one call
                # In API 2025-01, SKU lives under inventoryItem in ProductVariantsBulkInput
                variants_input = [{"id": vid, "inventoryItem": {"sku": sku}} for vid, sku, _ in missing]
                resp = gql(VARIANTS_BULK_UPDATE, {
                    "productId": p["id"],
                    "variants": variants_input
                })
                errs = resp.get("data", {}).get("productVariantsBulkUpdate", {}).get("userErrors", [])
                if errs:
                    log(f"  ✗ {errs}")
                    errors += len(missing)
                else:
                    variants_set += len(missing)
                    time.sleep(0.3)
            else:
                variants_set += len(missing)

        products_processed += 1

        if products_processed % 100 == 0:
            log(f"\n  {products_processed} products processed...")

    log("\n" + "=" * 60)
    log(f"Products processed:  {products_processed}")
    log(f"Variants SKU set:    {variants_set}")
    log(f"Variants had SKU:    {variants_skipped}")
    log(f"Errors:              {errors}")
    log("=" * 60)

if __name__ == "__main__":
    main()
