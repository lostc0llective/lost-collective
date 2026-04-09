"""
Fix META_LOCATION_MISSING — Lost Collective
============================================
Sets custom.location metafield for all products where it is currently missing,
derived from their custom.collection_series value.

Covers 39 of 62 series. The remaining ~23 are either multi-location, category
collections, or need Brett to confirm the geographic location.

Usage:
  export SHOPIFY_ADMIN_TOKEN=$(op read "op://Private/6u6evrxttlqexvzu6et4bpcl3y/Admin Token")
  export SHOPIFY_ENV=production
  python3 scripts/fix_location_metafields.py

  # Dry run:
  python3 scripts/fix_location_metafields.py --dry-run
"""

import argparse, json, os, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault("SHOPIFY_ENV", "production")

from shopify_gql import gql, paginate, metafields_set

# ── Series → Geographic Location ──────────────────────────────────────────────
# Format: "City/Town, State/Prefecture, Country"
# Series not listed here are skipped (categories, multi-location, or uncertain)

SERIES_LOCATION_MAP = {
    # New South Wales, Australia
    "ANSTO HIFAR":                           "Lucas Heights, New South Wales, Australia",
    "Balmain Leagues Club":                  "Rozelle, New South Wales, Australia",
    "Bankstown RSL":                         "Bankstown, New South Wales, Australia",
    "Bathurst Gasworks":                     "Bathurst, New South Wales, Australia",
    "Blayney Abattoir":                      "Blayney, New South Wales, Australia",
    "BlueScope Port Kembla":                 "Port Kembla, New South Wales, Australia",
    "Bombala Station":                       "Bombala, New South Wales, Australia",
    "Braidwood Hotel":                       "Braidwood, New South Wales, Australia",
    "Callan Park":                           "Rozelle, New South Wales, Australia",
    "Eveleigh Paint Shop":                   "Eveleigh, New South Wales, Australia",
    "Halvorsens Boat Yard":                  "Putney, New South Wales, Australia",
    "Hornsby Quarry":                        "Hornsby, New South Wales, Australia",
    "Kandos Cement Works":                   "Kandos, New South Wales, Australia",
    "Kenmore Asylum":                        "Goulburn, New South Wales, Australia",
    "Leichhardt House":                      "Southern Tablelands, New South Wales, Australia",
    "Lewisham Hospital":                     "Lewisham, New South Wales, Australia",
    "Mittagong Maltings":                    "Mittagong, New South Wales, Australia",
    "MV Cape Don":                           "Balls Head, New South Wales, Australia",
    "Mungo Scott Flour Mill":                "Summer Hill, New South Wales, Australia",
    "Newington Armory":                      "Silverwater, New South Wales, Australia",
    "Newington Armory Gun Powder Magazine":  "Silverwater, New South Wales, Australia",
    "Parramatta Road":                       "Sydney, New South Wales, Australia",
    "Peters' Ice Cream Factory":             "Taree, New South Wales, Australia",
    "Port Botany":                           "Botany, New South Wales, Australia",
    "Portland Cement Works":                 "Portland, New South Wales, Australia",
    "Queen Victoria Sanitorium":             "Wentworth Falls, New South Wales, Australia",
    "Terminus Hotel":                        "Pyrmont, New South Wales, Australia",
    "Tin City":                              "Lake Macquarie, New South Wales, Australia",
    "Wangi Power Station":                   "Wangi Wangi, New South Wales, Australia",
    "Waratah Park":                          "Duffys Forest, New South Wales, Australia",
    "Waterfall Sanatorium":                  "Waterfall, New South Wales, Australia",
    "West Ryde Pumping Station":             "West Ryde, New South Wales, Australia",
    "White Bay Power Station":               "Rozelle, New South Wales, Australia",
    # Victoria, Australia
    "Box Hill Brickworks":                   "Box Hill, Victoria, Australia",
    "Bradmill Denim":                        "Yarraville, Victoria, Australia",
    "Geelong B Power Station":               "Corio, Victoria, Australia",
    "Morwell Power Station":                 "Morwell, Victoria, Australia",
    # Victoria, Australia (additional)
    "Abandoned Shoe Factory":               "Northcote, Victoria, Australia",
    "O-I Glass":                            "Thomastown, Victoria, Australia",
    # New South Wales, Australia (additional confirmed)
    "ATL Building":                         "Meadowbank, New South Wales, Australia",
    "Abandoned Bakery":                     "Leichhardt, New South Wales, Australia",
    "Female Ward 9 & 10":                   "Rozelle, New South Wales, Australia",
    "Macquarie Boys Technology High":       "Rydalmere, New South Wales, Australia",
    "Marina Picture Palace":               "Rosebery, New South Wales, Australia",
    "Mill Pond Farm":                       "Jembaicumbene, New South Wales, Australia",
    "Mountain View Homestead":             "Wisemans Creek, New South Wales, Australia",
    "Sundell Holden":                       "Chatswood, New South Wales, Australia",
    "The Asylum":                           "Kenmore, New South Wales, Australia",
    "The Post Office":                      "Big Hill, New South Wales, Australia",
    "The Woolshed":                         "Various, New South Wales, Australia",
    "Woolla":                               "Deua River Valley, New South Wales, Australia",
    # Multi-state, Australia
    "A Place To Call Home":                 "Various, Australia",
    "Hotel Motel 101":                      "Various, New South Wales, Australia",
    "The Dairy":                            "Various, Australia",
    # Japan
    "Ashio Copper Mine":                     "Ashio, Tochigi, Japan",
    "Family School Fureai":                  "Yubari, Hokkaido, Japan",
    "Kinugawa Kan":                          "Nikko, Tochigi, Japan",
    "Kuwashima Hospital":                    "Kaga, Ishikawa, Japan",
    "Nichitsu Mining Village":               "Chichibu, Saitama, Japan",
    "Seika Dormitory":                       "Kyoto, Kyoto, Japan",
    "Shimizusawa Thermal Power Plant":       "Yubari, Hokkaido, Japan",
    "Streetscapes of Yubari":               "Yubari, Hokkaido, Japan",
    "Western Village":                       "Nasu-Shiobara, Tochigi, Japan",
}

# These are category/mood collections or have ambiguous/multiple locations — skip
SKIP_SERIES = {
    "Commercial", "Industrial", "Japan",
    "Landscapes", "Medical", "New", "Rural", "Scenes",
    "Starting at $50",
}


def fetch_products_missing_location(dry_run: bool):
    """Yield (product_gid, series) for products missing custom.location."""
    q = """
    query($first: Int!, $cursor: String) {
      products(first: $first, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        edges { node {
          id
          metafields(first: 20, namespace: "custom") {
            edges { node { key value } }
          }
        }}
      }
    }
    """
    count = 0
    for page in paginate(q, {"first": 100}, ["products"]):
        for edge in page:
            node = edge["node"]
            mfs = {m["node"]["key"]: m["node"]["value"] for m in node["metafields"]["edges"]}
            location = mfs.get("location", "")
            series = mfs.get("collection_series", "")
            if not location and series and series in SERIES_LOCATION_MAP:
                count += 1
                yield node["id"], series
    if dry_run:
        print(f"  (dry run scan complete — {count} products would be updated)")


def run(dry_run: bool):
    print(f"{'[DRY RUN] ' if dry_run else ''}Setting custom.location for products missing it")
    print(f"Coverage: {len(SERIES_LOCATION_MAP)} series mapped, {len(SKIP_SERIES)} skipped")
    print("=" * 60)

    batch = []
    updated = 0
    skipped_series = set()

    for product_gid, series in fetch_products_missing_location(dry_run):
        location = SERIES_LOCATION_MAP[series]
        if dry_run:
            print(f"  [DRY] {series[:40]:<40} → {location}")
            updated += 1
            continue

        batch.append({
            "ownerId":   product_gid,
            "namespace": "custom",
            "key":       "location",
            "type":      "single_line_text_field",
            "value":     location,
        })

        if len(batch) >= 25:
            result = metafields_set(batch)
            n = result["success"]
            updated += n
            print(f"  ✓ batch pushed ({n}/{len(batch)})")
            batch.clear()
            time.sleep(0.5)

    if batch and not dry_run:
        result = metafields_set(batch)
        n = result["success"]
        updated += n
        print(f"  ✓ final batch pushed ({n}/{len(batch)})")

    print("\n" + "=" * 60)
    print(f"Done. {'Would update' if dry_run else 'Updated'}: {updated} products")

    # All remaining SKIP_SERIES are category/mood collections with no specific location


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    token = os.environ.get("SHOPIFY_ADMIN_TOKEN")
    if not token:
        sys.exit("SHOPIFY_ADMIN_TOKEN not set.")

    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
