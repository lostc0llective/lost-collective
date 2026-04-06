"""
Yotpo → Judge.me review migration — Lost Collective
====================================================
Migrates all 40 Yotpo reviews (product + site-level) into Judge.me.

Requirements:
  JUDGEME_API_TOKEN  — Private API token from Judge.me Dashboard → Settings → API
  SHOPIFY_ADMIN_TOKEN — Shopify Admin API token (for product handle lookup)
  logs/yotpo_reviews.json      — Yotpo export (already saved)
  logs/yotpo_product_map.json  — Product ID → handle map (already saved)

Usage:
  export JUDGEME_API_TOKEN=<token from judge.me>
  export SHOPIFY_ADMIN_TOKEN=$(op read "op://Private/6u6evrxttlqexvzu6et4bpcl3y/Admin Token")
  python3 scripts/judgeme_migrate.py

  # Dry run (no writes):
  python3 scripts/judgeme_migrate.py --dry-run
"""

import argparse, html, json, os, sys, time
from datetime import datetime
from pathlib import Path

SHOP_DOMAIN = "lost-collective.myshopify.com"
JUDGEME_BASE = "https://judge.me/api/v1"
LOG_DIR = Path("logs")

# These 11 store reviews have no specific product match.
# The other 29 (20 direct product SKUs + 9 matched store reviews) are handled via CSV import.
STORE_ONLY_IDS = {
    678036289,  # Emily T. — "The essence of wabisabi"
    678036291,  # Lindy G. — "Divine"
    678036293,  # Julianne M. — "So different!"
    678036294,  # Harry H. — "Contrast of colors"
    678037029,  # David S. — "Great photos, great framing"
    678037030,  # Bryan D. — "Sensational"
    678037040,  # Tanya E. — "Beautiful!"
    678037042,  # Tanya E. — "Love it!"
    678037044,  # Tanya E. — "Awesome photo"
    678037046,  # miguel c. — "Awesome purchase"
    786017013,  # Lesley J. — "Great products, great service."
}


def load_data():
    reviews_path = LOG_DIR / "yotpo_reviews.json"
    map_path = LOG_DIR / "yotpo_product_map.json"
    if not reviews_path.exists():
        sys.exit("logs/yotpo_reviews.json not found. Run: python3 scripts/judgeme_migrate.py --fetch-yotpo first")
    if not map_path.exists():
        sys.exit("logs/yotpo_product_map.json not found. Run the product map fetch first.")
    with open(reviews_path) as f:
        reviews = json.load(f)
    with open(map_path) as f:
        product_map = json.load(f)
    return reviews, product_map


def clean_text(s: str) -> str:
    """Decode HTML entities, strip whitespace."""
    if not s:
        return ""
    return html.unescape(s).strip()


def post_review(api_token: str, payload: dict, dry_run: bool) -> dict:
    import requests
    if dry_run:
        return {"dry_run": True, "payload_keys": list(payload.keys())}
    r = requests.post(
        f"{JUDGEME_BASE}/reviews",
        params={"api_token": api_token, "shop_domain": SHOP_DOMAIN},
        json=payload,
        timeout=15,
    )
    return r.json()


def migrate(api_token: str, dry_run: bool):
    reviews, product_map = load_data()

    results = {"success": [], "skipped": [], "failed": []}

    print(f"{'[DRY RUN] ' if dry_run else ''}Posting {len(STORE_ONLY_IDS)} unmatched store reviews → Judge.me")
    print("(29 product-linked reviews handled separately via CSV import)")
    print("=" * 60)

    print(f"Posting {len(STORE_ONLY_IDS)} unmatched store reviews (the other 29 come from CSV import)")
    print()

    for rv in reviews:
        yotpo_id = rv["id"]

        # Only post the 11 unmatched store reviews — the rest are in the CSV import
        if yotpo_id not in STORE_ONLY_IDS:
            continue

        name = clean_text(rv.get("name", "Anonymous"))
        email = rv.get("email", "").strip()
        rating = int(rv.get("score", 5))
        title = clean_text(rv.get("title", ""))
        body = clean_text(rv.get("content", ""))
        created_at = rv.get("created_at", datetime.utcnow().isoformat())[:10]

        # Skip deleted or archived
        if rv.get("deleted") or rv.get("archived"):
            print(f"  SKIP [{yotpo_id}] {name} — deleted/archived")
            results["skipped"].append(yotpo_id)
            continue

        # Build payload — store review, no product association
        payload = {
            "shop_domain": SHOP_DOMAIN,
            "platform": "shopify",
            "id": yotpo_id,
            "email": email,
            "name": name,
            "reviewer_name": name,
            "rating": rating,
            "body": body,
            "title": title,
            "created_at": created_at,
            "verified": True,
            "published": True,
        }

        label = "[store review]"

        print(f"  {'[DRY] ' if dry_run else ''}POST {label} — {name} ({rating}★) {title[:40]}")

        try:
            result = post_review(api_token, payload, dry_run)
            background_msg = "processed in background" in str(result.get("message", ""))
            if dry_run or "review" in result or result.get("dry_run") or background_msg:
                results["success"].append(yotpo_id)
                if not dry_run:
                    if background_msg:
                        print(f"    ✓ queued (background processing)")
                    else:
                        jdgm_id = result.get("review", {}).get("id", "?")
                        print(f"    ✓ Judge.me ID: {jdgm_id}")
            else:
                error = result.get("error") or result.get("message") or str(result)[:100]
                print(f"    ✗ FAILED: {error}")
                results["failed"].append({"yotpo_id": yotpo_id, "error": error})
        except Exception as e:
            print(f"    ✗ EXCEPTION: {e}")
            results["failed"].append({"yotpo_id": yotpo_id, "error": str(e)})

        if not dry_run:
            time.sleep(0.3)  # Rate limit respect

    # Summary
    print("\n" + "=" * 60)
    print(f"Done.")
    print(f"  Success:  {len(results['success'])}")
    print(f"  Skipped:  {len(results['skipped'])}")
    print(f"  Failed:   {len(results['failed'])}")
    if results["failed"]:
        print("\nFailed reviews:")
        for f in results["failed"]:
            print(f"  Yotpo ID {f['yotpo_id']}: {f['error']}")

    # Save results
    output_path = LOG_DIR / ("judgeme_migrate_dryrun.json" if dry_run else "judgeme_migrate_results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print what would be sent, no API calls")
    args = parser.parse_args()

    api_token = os.environ.get("JUDGEME_API_TOKEN")
    if not api_token and not args.dry_run:
        sys.exit(
            "JUDGEME_API_TOKEN not set.\n"
            "Get it from: Judge.me Dashboard → Settings → API → Private token\n"
            "Then: export JUDGEME_API_TOKEN=<token> && python3 scripts/judgeme_migrate.py"
        )
    if not api_token:
        api_token = "DRY_RUN_TOKEN"

    migrate(api_token, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
