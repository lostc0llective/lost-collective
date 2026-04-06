"""
Overnight content generation — Lost Collective
Runs unattended. Safe to leave running.

Tasks (in order):
  1. Fix 2 empty collection descriptions (Leichhardt House, Newington Armory)
  2. Generate subject_description metafields for all products missing one

Usage:
  op run --env-file=.env.tpl -- python3 scripts/overnight_content.py

Progress is logged to logs/overnight_content.log
Results are saved to logs/overnight_content_results.json
"""

import json, os, sys, time
from datetime import datetime
from pathlib import Path

# ── Setup ───────────────────────────────────────────────────────────────────────

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE  = LOG_DIR / "overnight_content.log"
JSON_FILE = LOG_DIR / "overnight_content_results.json"

def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# ── Imports ─────────────────────────────────────────────────────────────────────

sys.path.insert(0, os.path.dirname(__file__))
import shopify_gql as shop
import claude_copy as copy_gen

# ── Helpers ─────────────────────────────────────────────────────────────────────

def parse_title(title: str) -> tuple[str, str]:
    """
    Split "Subject Title | Series Name" into (subject, series).
    Returns (title, "") if no pipe present.
    """
    if " | " in title:
        parts = title.split(" | ", 1)
        return parts[0].strip(), parts[1].strip()
    return title.strip(), ""


def collection_update_description(collection_gid: str, description_html: str) -> dict:
    """Update a collection's descriptionHtml."""
    q = """
    mutation CollectionUpdate($input: CollectionInput!) {
      collectionUpdate(input: $input) {
        collection { id title descriptionHtml }
        userErrors  { field message }
      }
    }
    """
    resp = shop.gql(q, {"input": {"id": collection_gid, "descriptionHtml": description_html}})
    return resp["data"]["collectionUpdate"]


def get_products_missing_metafield(metafield_key: str = "subject_description") -> list[dict]:
    """
    Fetch all products that are missing the given custom metafield.
    Returns list of { id, title, series }.
    """
    log("Fetching all products from Shopify...")
    all_products = []
    count = 0
    for product in shop.iter_products():
        count += 1
        if count % 100 == 0:
            log(f"  ...fetched {count} products so far")
        # Check if metafield exists, and grab year + location if available
        metas = product.get("metafields", {}).get("edges", [])
        has_key = False
        year = ""
        location = ""
        for m in metas:
            node = m["node"]
            if node["key"] == metafield_key:
                has_key = True
            if node["key"] == "year_photographed":
                year = node["value"]
            if node["key"] == "location":
                location = node["value"]
        if not has_key:
            subject, series = parse_title(product["title"])
            image_url = (product.get("featuredImage") or {}).get("url", "")
            all_products.append({
                "id":          product["id"],
                "title":       subject,
                "series":      series,
                "year":        year,
                "location":    location,
                "image_url":   image_url,
                "_full_title": product["title"],
            })
    log(f"Total products: {count}  |  Missing {metafield_key}: {len(all_products)}")
    return all_products


# ── Task 1: Fix empty collection descriptions ───────────────────────────────────

EMPTY_COLLECTIONS = [
    {
        "title": "Leichhardt House",
        "location": "Leichhardt, Sydney NSW",
        "context": (
            "A residential or institutional building in Leichhardt, an inner-western "
            "Sydney suburb with a strong working-class and Italian immigrant heritage."
        ),
    },
    {
        "title": "Newington Armory",
        "location": "Newington, Sydney NSW",
        "context": (
            "The Newington Armory is a heritage-listed former Royal Australian Navy "
            "armaments depot at Newington on the Parramatta River. Operated from 1897, "
            "it stored naval munitions and was decommissioned in 1999. The site became "
            "part of Sydney Olympic Park. Original sandstone and brick magazines and "
            "stores survive in various states of preservation."
        ),
    },
]


def run_collection_descriptions():
    log("=" * 60)
    log("TASK 1: Fix empty collection descriptions")
    log("=" * 60)

    # Fetch all collections to find GIDs
    collection_map = {}
    for coll in shop.iter_collections():
        collection_map[coll["title"]] = coll["id"]

    results = []
    for c in EMPTY_COLLECTIONS:
        title = c["title"]
        gid = collection_map.get(title)
        if not gid:
            log(f"  SKIP — could not find collection: {title}")
            continue

        log(f"  Generating description for: {title}")
        try:
            description = copy_gen.collection_description(
                title=title,
                location=c.get("location", ""),
                context=c.get("context", ""),
                max_words=80,
            )
            # Wrap in store HTML format
            description_html = (
                f'<section class="gallery-intro">\n'
                f"<p>{description}</p>\n"
                f"</section>"
            )
            log(f"  Generated ({len(description.split())} words): {description[:80]}...")
            result = collection_update_description(gid, description_html)
            if result.get("userErrors"):
                log(f"  ERROR pushing {title}: {result['userErrors']}")
                results.append({"title": title, "status": "error", "errors": result["userErrors"]})
            else:
                log(f"  OK — pushed to Shopify: {title}")
                results.append({"title": title, "status": "ok", "description": description})
        except Exception as e:
            log(f"  EXCEPTION {title}: {e}")
            results.append({"title": title, "status": "exception", "error": str(e)})

        time.sleep(2)  # brief pause between Gemini calls

    return results


# ── Task 2: Product subject_description metafields ─────────────────────────────

def run_product_subject_descriptions():
    log("=" * 60)
    log("TASK 2: Generate subject_description metafields for all products")
    log("=" * 60)

    products = get_products_missing_metafield("subject_description")

    if not products:
        log("All products already have subject_description. Nothing to do.")
        return []

    log(f"Generating descriptions for {len(products)} products via Gemini...")
    log("Estimated time: ~{:.0f} minutes".format(len(products) * 1.2 / 60))

    # Generate in chunks of 200 so we can save progress periodically
    CHUNK = 200
    all_results = []
    errors = []

    for chunk_start in range(0, len(products), CHUNK):
        chunk = products[chunk_start : chunk_start + CHUNK]
        chunk_end = min(chunk_start + CHUNK, len(products))
        log(f"\nGenerating chunk {chunk_start + 1}–{chunk_end} of {len(products)}...")

        chunk_results = copy_gen.batch_subject_descriptions(chunk, delay=1.5)

        # Separate clean, needs-review, and errors
        successes    = [r for r in chunk_results if r.get("subject_description") and not r.get("needs_review")]
        needs_review = [r for r in chunk_results if r.get("subject_description") and r.get("needs_review")]
        chunk_errors = [r for r in chunk_results if not r.get("subject_description")]

        if needs_review:
            log(f"  {len(needs_review)} flagged for review (ambiguous title or TOV violations) — NOT pushed to Shopify")
            log(f"  Review these in logs/overnight_content_results.json before pushing manually")

        if chunk_errors:
            log(f"  {len(chunk_errors)} errors in this chunk — will retry later")
            errors.extend(chunk_errors)

        all_results.extend(chunk_results)

        # Save progress before pushing (so descriptions aren't lost on push error)
        _save_results(all_results, errors)

        # Push successes to Shopify
        if successes:
            log(f"  Pushing {len(successes)} metafields to Shopify...")
            entries = [
                {
                    "ownerId":   r["id"],
                    "namespace": "custom",
                    "key":       "subject_description",
                    "type":      "multi_line_text_field",
                    "value":     r["subject_description"],
                }
                for r in successes
            ]
            try:
                push_result = shop.metafields_set(entries)
                log(f"  Shopify: {push_result['success']} saved, {len(push_result['errors'])} errors")
                if push_result["errors"]:
                    log(f"  Shopify errors: {push_result['errors'][:3]}")
            except Exception as push_err:
                log(f"  Shopify push ERROR: {push_err}")
                log(f"  Descriptions saved to JSON — can retry push separately")
        log(f"  Progress saved. Total processed: {len(all_results)}/{len(products)}")

    # Retry errors once
    if errors:
        log(f"\nRetrying {len(errors)} failed products...")
        time.sleep(10)
        retry_results = gemini.batch_subject_descriptions(errors, delay=2.0)
        retry_successes = [r for r in retry_results if r.get("subject_description")]
        if retry_successes:
            entries = [
                {
                    "ownerId":   r["id"],
                    "namespace": "custom",
                    "key":       "subject_description",
                    "type":      "multi_line_text_field",
                    "value":     r["subject_description"],
                }
                for r in retry_successes
            ]
            push_result = shop.metafields_set(entries)
            log(f"  Retry: {push_result['success']} saved")
        # Update results
        for r in retry_results:
            all_results.append(r)
        _save_results(all_results, [r for r in retry_results if not r.get("subject_description")])

    total_ok  = sum(1 for r in all_results if r.get("subject_description"))
    total_err = sum(1 for r in all_results if not r.get("subject_description"))
    log(f"\nDone. Generated: {total_ok}  |  Failed: {total_err}")
    return all_results


def _save_results(results: list, errors: list):
    clean        = [r for r in results if r.get("subject_description") and not r.get("needs_review")]
    needs_review = [r for r in results if r.get("subject_description") and r.get("needs_review")]
    data = {
        "run_at":       datetime.now().isoformat(),
        "total":        len(results),
        "pushed":       len(clean),
        "needs_review": len(needs_review),
        "errors":       len(errors),
        "results":      clean,
        "review_queue": needs_review,
        "error_details": errors,
    }
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Main ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    start = datetime.now()
    log(f"Overnight content generation started at {start.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Logging to {LOG_FILE}")
    log("")

    summary = {"started": start.isoformat(), "tasks": {}}

    # Task 1
    try:
        coll_results = run_collection_descriptions()
        summary["tasks"]["collection_descriptions"] = {
            "total":   len(coll_results),
            "ok":      sum(1 for r in coll_results if r.get("status") == "ok"),
            "errors":  sum(1 for r in coll_results if r.get("status") != "ok"),
        }
    except Exception as e:
        log(f"FATAL ERROR in Task 1: {e}")
        summary["tasks"]["collection_descriptions"] = {"error": str(e)}

    log("")

    # Task 2
    try:
        prod_results = run_product_subject_descriptions()
        summary["tasks"]["subject_descriptions"] = {
            "total":   len(prod_results),
            "ok":      sum(1 for r in prod_results if r.get("subject_description")),
            "errors":  sum(1 for r in prod_results if not r.get("subject_description")),
        }
    except Exception as e:
        log(f"FATAL ERROR in Task 2: {e}")
        summary["tasks"]["subject_descriptions"] = {"error": str(e)}

    finish = datetime.now()
    duration = (finish - start).total_seconds() / 60
    log("")
    log(f"Finished at {finish.strftime('%H:%M:%S')}  |  Duration: {duration:.1f} min")
    log(f"Summary: {json.dumps(summary['tasks'], indent=2)}")
    log(f"Full results: {JSON_FILE}")
