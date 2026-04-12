"""
Judge.me → Shopify reviews metafield sync
==========================================
Reads aggregate ratings from Judge.me and writes them to Shopify product
metafields (reviews.rating + reviews.rating_count) so that the theme's
product-schema.liquid can include aggregateRating in Product structured data.

This enables Google rich results (star ratings in search) for all products
that have reviews.

Run: op run --env-file=.env.tpl -- python3 shopify/scripts/judgeme_sync_ratings.py

Optional flags:
  --dry-run    Show what would be written without actually writing
  --limit N    Only process first N products (for testing)
"""

import os, sys, time, requests, argparse
from collections import defaultdict

SHOP     = "lost-collective.myshopify.com"
JM_TOKEN = "CGm0VeT_HhyftrYNFn9e6KO74AA"
JM_BASE  = "https://judge.me/api/v1"
SP_BASE  = f"https://{SHOP}/admin/api/2024-01"

SHOPIFY_DELAY = 0.6   # ~1.6 req/s, within Shopify's 2/s REST limit
JUDGEME_DELAY = 0.3


def shopify_headers():
    return {"X-Shopify-Access-Token": os.environ["SHOPIFY_ADMIN_TOKEN"]}


# ── Step 1: Ensure metafield definitions exist ─────────────────────────────────

def ensure_metafield_definitions():
    """Create reviews.rating and reviews.rating_count definitions if missing."""
    resp = requests.get(
        f"{SP_BASE}/metafield_definitions.json",
        params={"owner_type": "PRODUCT", "namespace": "reviews"},
        headers=shopify_headers(),
    )
    existing = {d["key"] for d in resp.json().get("metafield_definitions", [])}

    needed = [
        {
            "name":        "Rating",
            "namespace":   "reviews",
            "key":         "rating",
            "type":        "rating",
            "owner_type":  "PRODUCT",
        },
        {
            "name":        "Rating Count",
            "namespace":   "reviews",
            "key":         "rating_count",
            "type":        "number_integer",
            "owner_type":  "PRODUCT",
        },
    ]

    for defn in needed:
        if defn["key"] in existing:
            print(f"  Definition reviews.{defn['key']} already exists — skipping")
            continue
        r = requests.post(
            f"{SP_BASE}/metafield_definitions.json",
            headers={**shopify_headers(), "Content-Type": "application/json"},
            json={"metafield_definition": defn},
        )
        if r.status_code in (200, 201):
            print(f"  Created definition: reviews.{defn['key']}")
        else:
            print(f"  ERROR creating reviews.{defn['key']}: {r.status_code} {r.text[:200]}")
        time.sleep(SHOPIFY_DELAY)


# ── Step 2: Fetch all Judge.me reviews and aggregate per product ───────────────

def fetch_judgeme_ratings() -> dict:
    """
    Return {product_handle: {"rating": float, "count": int}} for all products
    with at least one published review.
    """
    ratings  = defaultdict(list)
    page     = 1
    per_page = 100

    print("Fetching all Judge.me reviews...", flush=True)
    while True:
        resp = requests.get(
            f"{JM_BASE}/reviews",
            params={
                "api_token":   JM_TOKEN,
                "shop_domain": SHOP,
                "per_page":    per_page,
                "page":        page,
                "published":   True,
            },
        )
        reviews = resp.json().get("reviews", [])
        if not reviews:
            break

        for r in reviews:
            handle = r.get("product_handle")
            rating = r.get("rating")
            if handle and rating and handle != "judgeme-shop-reviews":
                ratings[handle].append(int(rating))

        print(f"  Page {page}: {len(reviews)} reviews ({sum(len(v) for v in ratings.values())} product reviews so far)", flush=True)

        if len(reviews) < per_page:
            break
        page += 1
        time.sleep(JUDGEME_DELAY)

    # Aggregate
    aggregated = {}
    for handle, scores in ratings.items():
        aggregated[handle] = {
            "rating": round(sum(scores) / len(scores), 1),
            "count":  len(scores),
        }

    print(f"\nAggregated ratings for {len(aggregated)} products.\n")
    return aggregated


# ── Step 3: Get Shopify product IDs for each handle ───────────────────────────

def get_product_ids(handles: list) -> dict:
    """Return {handle: product_id} for the given handles."""
    result   = {}
    per_page = 250

    # Fetch all products in batches and match by handle
    print("Fetching Shopify product IDs...", flush=True)
    since_id = None
    while True:
        params = {"limit": per_page, "fields": "id,handle"}
        if since_id:
            params["since_id"] = since_id

        resp = requests.get(
            f"{SP_BASE}/products.json",
            params=params,
            headers=shopify_headers(),
        )
        products = resp.json().get("products", [])
        if not products:
            break

        for p in products:
            if p["handle"] in handles:
                result[p["handle"]] = p["id"]

        since_id = products[-1]["id"]
        if len(products) < per_page:
            break
        time.sleep(SHOPIFY_DELAY)

    print(f"Found {len(result)}/{len(handles)} product IDs in Shopify.\n")
    return result


# ── Step 4: Write metafields ───────────────────────────────────────────────────

def write_metafields(product_id: int, rating: float, count: int, dry_run: bool) -> bool:
    """Write reviews.rating and reviews.rating_count metafields to a product."""
    metafields = [
        {
            "namespace": "reviews",
            "key":       "rating",
            "type":      "rating",
            "value":     f'{{"value":"{rating:.1f}","scale_min":"1.0","scale_max":"5.0"}}',
        },
        {
            "namespace": "reviews",
            "key":       "rating_count",
            "type":      "number_integer",
            "value":     str(count),
        },
    ]

    if dry_run:
        return True

    for mf in metafields:
        resp = requests.post(
            f"{SP_BASE}/products/{product_id}/metafields.json",
            headers={**shopify_headers(), "Content-Type": "application/json"},
            json={"metafield": mf},
        )
        if resp.status_code not in (200, 201):
            # Might already exist — try PUT via metafield list
            existing = requests.get(
                f"{SP_BASE}/products/{product_id}/metafields.json",
                params={"namespace": "reviews", "key": mf["key"]},
                headers=shopify_headers(),
            ).json().get("metafields", [])

            if existing:
                mf_id = existing[0]["id"]
                resp = requests.put(
                    f"{SP_BASE}/metafields/{mf_id}.json",
                    headers={**shopify_headers(), "Content-Type": "application/json"},
                    json={"metafield": {"id": mf_id, "value": mf["value"]}},
                )
                if resp.status_code not in (200, 201):
                    print(f"    ERROR updating {mf['key']}: {resp.status_code} {resp.text[:100]}")
                    return False
            else:
                print(f"    ERROR creating {mf['key']}: {resp.status_code} {resp.text[:100]}")
                return False

        time.sleep(SHOPIFY_DELAY)

    return True


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Show plan without writing")
    parser.add_argument("--limit",   type=int, default=None, help="Process only first N products")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN — no changes will be written\n")

    # 1. Ensure metafield definitions
    print("Step 1: Checking metafield definitions...")
    if not args.dry_run:
        ensure_metafield_definitions()
    else:
        print("  (skipped in dry-run)")

    # 2. Fetch Judge.me ratings
    print("\nStep 2: Fetching Judge.me ratings...")
    ratings = fetch_judgeme_ratings()

    if args.limit:
        handles = list(ratings.keys())[:args.limit]
        ratings = {h: ratings[h] for h in handles}
        print(f"Limiting to first {args.limit} products.\n")

    # 3. Get Shopify product IDs
    print("Step 3: Fetching Shopify product IDs...")
    product_ids = get_product_ids(list(ratings.keys()))

    # 4. Write metafields
    print("Step 4: Writing metafields to Shopify...\n")
    success = 0
    skipped = 0
    errors  = 0

    for handle, data in ratings.items():
        pid = product_ids.get(handle)
        if not pid:
            print(f"  SKIP  {handle} — not found in Shopify")
            skipped += 1
            continue

        rating = data["rating"]
        count  = data["count"]
        label  = "DRY-RUN" if args.dry_run else "WRITE"
        print(f"  [{label}] {handle}  →  {rating:.1f} ★ ({count} reviews)", flush=True)

        if write_metafields(pid, rating, count, args.dry_run):
            success += 1
        else:
            errors += 1

    print(f"\n{'─'*60}")
    print(f"Done.  Written: {success}  Skipped: {skipped}  Errors: {errors}")
    if not args.dry_run:
        print("\nNext: Push product-schema.liquid to production and validate with")
        print("Google's Rich Results Test: https://search.google.com/test/rich-results")


if __name__ == "__main__":
    main()
