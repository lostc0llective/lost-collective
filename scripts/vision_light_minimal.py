"""
Light & Minimal Vision Classifier — Lost Collective
====================================================
Runs every product image through Claude vision to identify products with
high-key lighting, minimal compositions, soft tones, and clean lines.

Qualifying products are tagged 'light-and-minimal' and a Shopify smart
collection is created/updated to pull them automatically.

Checkpointing: results saved to /tmp/light_minimal_results.json after each
batch so the script can resume if interrupted.

Usage:
  op run --env-file=.env.tpl -- python3 shopify/scripts/vision_light_minimal.py
  op run --env-file=.env.tpl -- python3 shopify/scripts/vision_light_minimal.py --dry-run
  op run --env-file=.env.tpl -- python3 shopify/scripts/vision_light_minimal.py --resume
"""

import argparse, json, os, sys, time
from pathlib import Path
import urllib.request

sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault("SHOPIFY_ENV", "production")

from shopify_gql import gql, iter_products, metafields_set

CHECKPOINT_FILE = "/tmp/light_minimal_results.json"
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

VISION_PROMPT = """Look at this fine art photography print and score it on the "Light & Minimal" aesthetic.

Score each dimension 1-5:
- LIGHTING: 1=very dark/moody, 5=bright/high-key/airy
- COMPOSITION: 1=very busy/complex, 5=minimal/sparse/clean
- TONES: 1=high contrast/saturated, 5=soft/muted/neutral
- BACKGROUND: 1=dark/textured/complex, 5=white/pale/neutral/open space
- LINES: 1=chaotic/organic, 5=clean architectural/geometric

Reply with ONLY a JSON object, no other text:
{"lighting": N, "composition": N, "tones": N, "background": N, "lines": N, "verdict": "yes" or "no", "reason": "one sentence"}

"yes" verdict = average score >= 3.5 AND lighting >= 3 AND composition >= 3"""


def score_image(image_url: str) -> dict:
    """Send image to Claude vision and return scores."""
    if not ANTHROPIC_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    payload = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 256,
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": image_url,
                    }
                },
                {
                    "type": "text",
                    "text": VISION_PROMPT,
                }
            ]
        }]
    }

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)

    if data.get("error"):
        raise RuntimeError(data["error"]["message"])

    raw = data["content"][0]["text"].strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def load_checkpoint() -> dict:
    if Path(CHECKPOINT_FILE).exists():
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {}


def save_checkpoint(results: dict):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(results, f)


def fetch_all_products():
    """Fetch all products with their featured image URL."""
    query = """
    query($cursor: String) {
      products(first: 100, after: $cursor) {
        edges { node {
          id handle title tags
          featuredImage { url }
        }}
        pageInfo { hasNextPage endCursor }
      }
    }
    """
    products = []
    cursor = None
    while True:
        result = gql(query, {"cursor": cursor})
        for edge in result["data"]["products"]["edges"]:
            node = edge["node"]
            img = node.get("featuredImage") or {}
            products.append({
                "id": node["id"],
                "handle": node["handle"],
                "title": node["title"],
                "tags": node["tags"],
                "image_url": img.get("url"),
            })
        page = result["data"]["products"]["pageInfo"]
        if not page["hasNextPage"]:
            break
        cursor = page["endCursor"]
    return products


def tag_products(product_ids: list[str], tag: str, dry_run: bool):
    """Add tag to qualifying products via productUpdate."""
    TAG_MUTATION = """
    mutation ProductUpdate($input: ProductInput!) {
      productUpdate(input: $input) {
        product { id tags }
        userErrors { field message }
      }
    }
    """
    updated = 0
    for gid in product_ids:
        if dry_run:
            print(f"  [DRY RUN] would tag {gid}")
            continue
        result = gql(TAG_MUTATION, {"input": {"id": gid, "tags": [tag]}})
        errors = result["data"]["productUpdate"]["userErrors"]
        if errors:
            print(f"  Tag error {gid}: {errors}")
        else:
            updated += 1
        time.sleep(0.3)  # rate limit
    return updated


def create_or_update_collection(tag: str, dry_run: bool):
    """Create a smart collection filtered on the light-and-minimal tag."""
    # Check if collection already exists
    check = gql("""
    query { collections(first: 250) { edges { node { id handle title } } } }
    """)
    existing = next(
        (e["node"] for e in check["data"]["collections"]["edges"]
         if e["node"]["handle"] == "light-and-minimal"),
        None
    )

    if existing:
        print(f"Collection already exists: /collections/{existing['handle']} ({existing['id']})")
        return existing["id"]

    if dry_run:
        print("[DRY RUN] would create /collections/light-and-minimal")
        return None

    CREATE_COLLECTION = """
    mutation CollectionCreate($input: CollectionInput!) {
      collectionCreate(input: $input) {
        collection { id handle }
        userErrors { field message }
      }
    }
    """
    SET_META = """
    mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
      metafieldsSet(metafields: $metafields) {
        metafields { id }
        userErrors { field message }
      }
    }
    """

    result = gql(CREATE_COLLECTION, {"input": {
        "title": "Light & Minimal",
        "handle": "light-and-minimal",
        "descriptionHtml": "<p>Photographs defined by open space, high-key light, and clean architectural lines. Pale walls, white ceilings, daylight through large windows. Works that sit quietly on a wall without demanding attention.</p>",
        "ruleSet": {
            "appliedDisjunctively": False,
            "rules": [{"column": "TAG", "relation": "EQUALS", "condition": "light-and-minimal"}]
        },
        "sortOrder": "BEST_SELLING",
    }})
    errors = result["data"]["collectionCreate"]["userErrors"]
    if errors:
        print(f"Collection create error: {errors}")
        return None

    col_id = result["data"]["collectionCreate"]["collection"]["id"]
    gql(SET_META, {"metafields": [
        {"ownerId": col_id, "namespace": "global", "key": "title_tag",
         "value": "Light & Minimal Wall Art Prints | Lost Collective", "type": "single_line_text_field"},
        {"ownerId": col_id, "namespace": "global", "key": "description_tag",
         "value": "Fine art photography prints with high-key lighting, minimal compositions, and soft tones. Works that bring stillness to a wall.", "type": "single_line_text_field"},
    ]})
    print(f"Created: /collections/light-and-minimal ({col_id})")
    return col_id


def run(dry_run: bool, resume: bool):
    print(f"{'[DRY RUN] ' if dry_run else ''}Light & Minimal Vision Classifier")
    print("=" * 60)

    if not ANTHROPIC_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    # Load checkpoint
    results = load_checkpoint() if resume else {}
    if resume and results:
        print(f"Resuming from checkpoint: {len(results)} products already scored")

    # Fetch all products
    print("Fetching products...", end=" ", flush=True)
    products = fetch_all_products()
    print(f"{len(products)} products")

    # Filter: skip products already scored, skip those already tagged, skip those without images
    to_score = [
        p for p in products
        if p["image_url"]
        and p["id"] not in results
        and "light-and-minimal" not in p["tags"]
    ]
    already_tagged = sum(1 for p in products if "light-and-minimal" in p["tags"])
    no_image = sum(1 for p in products if not p["image_url"])

    print(f"  Already tagged: {already_tagged}")
    print(f"  No image: {no_image}")
    print(f"  To score: {len(to_score)}")
    print()

    # Score each product
    qualified = []
    errors = 0
    batch_size = 10

    for i, product in enumerate(to_score):
        try:
            scores = score_image(product["image_url"])
            verdict = scores.get("verdict", "no") == "yes"
            avg = sum([scores.get("lighting", 1), scores.get("composition", 1),
                       scores.get("tones", 1), scores.get("background", 1),
                       scores.get("lines", 1)]) / 5

            results[product["id"]] = {
                "title": product["title"],
                "handle": product["handle"],
                "scores": scores,
                "avg": round(avg, 2),
                "qualified": verdict,
            }

            if verdict:
                qualified.append(product["id"])
                marker = "✓"
            else:
                marker = "·"

            print(f"[{i+1:4d}/{len(to_score)}] {marker} {product['title'][:55]:<55} avg={avg:.1f}")

        except Exception as e:
            print(f"[{i+1:4d}/{len(to_score)}] ERROR {product['title'][:40]}: {e}")
            errors += 1
            # Don't checkpoint on error for this product — retry next time
            time.sleep(2)
            continue

        # Save checkpoint every 50 products
        if (i + 1) % 50 == 0:
            save_checkpoint(results)
            print(f"  --- checkpoint saved ({len(qualified)} qualified so far) ---")

        # Rate limit: ~20 req/min to stay well within limits
        time.sleep(3)

    # Final checkpoint
    save_checkpoint(results)

    # Add any from checkpoint that were previously qualified
    all_qualified = [pid for pid, r in results.items() if r.get("qualified")]

    print()
    print("=" * 60)
    print(f"Scored: {len(results)} products")
    print(f"Qualified (Light & Minimal): {len(all_qualified)}")
    print(f"Errors: {errors}")

    if not all_qualified:
        print("No qualifying products found — check scoring thresholds")
        return

    # Tag qualifying products
    print(f"\nTagging {len(all_qualified)} products with 'light-and-minimal'...")
    tagged = tag_products(all_qualified, "light-and-minimal", dry_run)
    if not dry_run:
        print(f"Tagged: {tagged} products")

    # Create/verify collection
    print("\nCreating smart collection...")
    create_or_update_collection("light-and-minimal", dry_run)

    # Summary of top scorers
    print("\nTop 10 scoring products:")
    top = sorted(results.items(), key=lambda x: x[1].get("avg", 0), reverse=True)[:10]
    for pid, r in top:
        print(f"  {r['avg']:.1f} — {r['title']}")

    print("\nDone.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    args = parser.parse_args()
    run(args.dry_run, args.resume)
