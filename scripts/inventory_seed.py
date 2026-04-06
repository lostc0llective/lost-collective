"""
Inventory seeding — Lost Collective
====================================
Sets correct inventory levels across all 1,809 products based on:
  - Actual units sold per variant (from order history)
  - Edition sizes: M=100, L=50, XL=25
  - XS/S are open editions — inventory tracking turned OFF

Rules applied:
  XS / S variants      → inventoryItem.tracked = false  (open edition, never sell out)
  M / L / XL variants  → tracked = true, qty = edition_size - units_sold  (min 0)
  Unframed + Glass     → seeded same as Framed for that size (shared pool)

Usage:
  op run --env-file=.env.tpl -- python3 scripts/inventory_seed.py [--dry-run]

  --dry-run   Print changes without writing to Shopify
  --check     Just report current state, no changes

Output:
  logs/inventory_seed.log
  logs/inventory_seed_results.json
"""

import json, os, sys, time, argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
import shopify_gql as shop

# ── Config ─────────────────────────────────────────────────────────────────────

EDITION_SIZES = {"M": 100, "L": 50, "XL": 25}
OPEN_SIZES    = {"XS", "S"}
LOCATION_GID  = "gid://shopify/Location/31336397"

LOG_DIR  = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE    = LOG_DIR / "inventory_seed.log"
JSON_FILE   = LOG_DIR / "inventory_seed_results.json"


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# ── Fetch orders → qty sold per variant ────────────────────────────────────────

def fetch_units_sold() -> dict:
    """
    Returns { variant_gid: qty_sold } from all non-cancelled orders.
    Counts fulfilled + unfulfilled (anything not cancelled = edition slot used).
    """
    log("Fetching order history to count units sold per variant...")
    sold = {}
    q = """
    query Orders($first: Int!, $cursor: String) {
      orders(first: $first, after: $cursor, query: "status:any -financial_status:voided") {
        pageInfo { hasNextPage endCursor }
        edges {
          node {
            cancelledAt
            lineItems(first: 50) {
              edges {
                node {
                  variant { id }
                  quantity
                }
              }
            }
          }
        }
      }
    }
    """
    order_count = 0
    for page in shop.paginate(q, {"first": 50}, ["orders"]):
        for edge in page:
            order = edge["node"]
            if order.get("cancelledAt"):
                continue  # cancelled orders don't consume edition slots
            order_count += 1
            for li_edge in order["lineItems"]["edges"]:
                li = li_edge["node"]
                if li["variant"] and li["variant"]["id"]:
                    vid = li["variant"]["id"]
                    sold[vid] = sold.get(vid, 0) + li["quantity"]

    log(f"  Scanned {order_count} orders. {len(sold)} variants have sales.")
    return sold


# ── Fetch all variants with inventory items ─────────────────────────────────────

def fetch_all_variants() -> list[dict]:
    """
    Returns list of variant dicts with size, type, inventory item ID, current qty.
    """
    log("Fetching all product variants...")
    q = """
    query Products($first: Int!, $cursor: String) {
      products(first: $first, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        edges {
          node {
            id title
            variants(first: 50) {
              edges {
                node {
                  id title
                  selectedOptions { name value }
                  inventoryQuantity
                  inventoryItem { id tracked }
                }
              }
            }
          }
        }
      }
    }
    """
    variants = []
    product_count = 0
    for page in shop.paginate(q, {"first": 50}, ["products"]):
        for p_edge in page:
            product = p_edge["node"]
            product_count += 1
            for v_edge in product["variants"]["edges"]:
                v = v_edge["node"]
                opts = {o["name"]: o["value"] for o in v["selectedOptions"]}
                size = opts.get("Size", "")
                type_ = opts.get("Type", "")
                variants.append({
                    "product_title":   product["title"],
                    "variant_id":      v["id"],
                    "variant_title":   v["title"],
                    "size":            size,
                    "type":            type_,
                    "inventory_item":  v["inventoryItem"]["id"],
                    "tracked":         v["inventoryItem"]["tracked"],
                    "current_qty":     v["inventoryQuantity"],
                })
    log(f"  Fetched {len(variants)} variants across {product_count} products.")
    return variants


# ── Mutations ──────────────────────────────────────────────────────────────────

def set_tracking(inventory_item_id: str, tracked: bool) -> bool:
    """Enable or disable inventory tracking for an item."""
    q = """
    mutation InventoryItemUpdate($id: ID!, $input: InventoryItemInput!) {
      inventoryItemUpdate(id: $id, input: $input) {
        inventoryItem { id tracked }
        userErrors { field message }
      }
    }
    """
    r = shop.gql(q, {"id": inventory_item_id, "input": {"tracked": tracked}})
    result = r["data"]["inventoryItemUpdate"]
    if result["userErrors"]:
        log(f"    ERROR setting tracking on {inventory_item_id}: {result['userErrors']}")
        return False
    return True


def set_quantities_batch(items: list[dict], location_id: str) -> list[str]:
    """
    Set absolute inventory quantities for multiple items in one mutation.
    items: [{ inventory_item, target_qty }, ...]
    Returns list of inventory_item IDs that errored.
    """
    q = """
    mutation InventorySetQuantities($input: InventorySetQuantitiesInput!) {
      inventorySetQuantities(input: $input) {
        inventoryAdjustmentGroup { id }
        userErrors { field message }
      }
    }
    """
    payload = {
        "input": {
            "name": "available",
            "reason": "correction",
            "ignoreCompareQuantity": True,
            "quantities": [
                {
                    "inventoryItemId": item["inventory_item"],
                    "locationId":      location_id,
                    "quantity":        item["target_qty"],
                }
                for item in items
            ],
        }
    }
    r = shop.gql(q, payload)
    result = r["data"]["inventorySetQuantities"]
    if result["userErrors"]:
        log(f"    ERROR in batch set: {result['userErrors']}")
        return [item["inventory_item"] for item in items]
    return []


# ── Main ───────────────────────────────────────────────────────────────────────

def run(dry_run: bool = False, check_only: bool = False):
    log("=" * 60)
    mode = "DRY RUN" if dry_run else ("CHECK ONLY" if check_only else "LIVE")
    log(f"Inventory seed — {mode} — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60)

    sold = fetch_units_sold()
    variants = fetch_all_variants()

    stats = {
        "untrack_open":    {"planned": 0, "done": 0, "skip": 0},
        "seed_limited":    {"planned": 0, "done": 0, "skip": 0},
        "already_correct": 0,
    }

    changes = []
    already_correct = []

    for v in variants:
        size  = v["size"]
        iid   = v["inventory_item"]
        vid   = v["variant_id"]
        cur   = v["current_qty"]
        tracked = v["tracked"]

        if size in OPEN_SIZES:
            # Open edition — should be untracked
            if tracked:
                stats["untrack_open"]["planned"] += 1
                changes.append({**v, "action": "untrack", "target_qty": None})
            else:
                stats["already_correct"] += 1
                already_correct.append({**v, "action": "already_correct"})

        elif size in EDITION_SIZES:
            edition = EDITION_SIZES[size]
            units_sold = sold.get(vid, 0)
            target_qty = max(0, edition - units_sold)

            if not tracked or cur != target_qty:
                stats["seed_limited"]["planned"] += 1
                changes.append({**v, "action": "seed", "target_qty": target_qty, "units_sold": units_sold})
            else:
                stats["already_correct"] += 1
                already_correct.append({**v, "action": "already_correct"})

    log(f"\nChanges needed:")
    log(f"  Open editions to untrack (XS/S): {stats['untrack_open']['planned']}")
    log(f"  Limited editions to seed (M/L/XL): {stats['seed_limited']['planned']}")
    log(f"  Already correct: {stats['already_correct']}")

    if check_only:
        _save_results(changes, already_correct, stats)
        log("\nCheck complete. No changes made.")
        return

    # Show a sample of what will change
    log("\nSample changes (first 10):")
    for c in changes[:10]:
        if c["action"] == "untrack":
            log(f"  UNTRACK  {c['product_title'][:35]} | {c['variant_title']}")
        else:
            log(f"  SEED     {c['product_title'][:35]} | {c['variant_title']} → {c['target_qty']} (sold: {c['units_sold']})")

    if dry_run:
        _save_results(changes, already_correct, stats)
        log("\nDry run complete. No changes made.")
        return

    log(f"\nApplying {len(changes)} changes...")
    errors = []

    # ── Step 1: Untrack all XS/S variants (must be done individually) ──────────
    untrack_list = [c for c in changes if c["action"] == "untrack"]
    seed_list    = [c for c in changes if c["action"] == "seed"]

    log(f"  Step 1: Untracking {len(untrack_list)} open edition variants...")
    for i, c in enumerate(untrack_list, 1):
        ok = set_tracking(c["inventory_item"], False)
        if ok:
            stats["untrack_open"]["done"] += 1
        else:
            errors.append(c)
        if i % 200 == 0:
            log(f"    {i}/{len(untrack_list)} untracked...")
        time.sleep(0.35)

    # ── Step 2: Enable tracking on any M/L/XL that need it ────────────────────
    needs_tracking = [c for c in seed_list if not c["tracked"]]
    if needs_tracking:
        log(f"  Step 2: Enabling tracking on {len(needs_tracking)} M/L/XL variants...")
        for i, c in enumerate(needs_tracking, 1):
            set_tracking(c["inventory_item"], True)
            if i % 200 == 0:
                log(f"    {i}/{len(needs_tracking)} enabled...")
            time.sleep(0.35)

    # ── Step 3: Batch-set quantities for M/L/XL (100 per call) ────────────────
    BATCH = 100
    log(f"  Step 3: Setting quantities for {len(seed_list)} limited edition variants (batches of {BATCH})...")
    for batch_start in range(0, len(seed_list), BATCH):
        batch = seed_list[batch_start:batch_start + BATCH]
        failed_ids = set_quantities_batch(batch, LOCATION_GID)
        ok_count = len(batch) - len(failed_ids)
        stats["seed_limited"]["done"] += ok_count
        for c in batch:
            if c["inventory_item"] in failed_ids:
                errors.append(c)
        if batch_start % 1000 == 0 and batch_start > 0:
            log(f"    {batch_start}/{len(seed_list)} quantities set...")
        time.sleep(0.5)

    log(f"\nDone.")
    log(f"  Untracked: {stats['untrack_open']['done']} / {stats['untrack_open']['planned']}")
    log(f"  Seeded:    {stats['seed_limited']['done']} / {stats['seed_limited']['planned']}")
    if errors:
        log(f"  Errors:    {len(errors)} — see {JSON_FILE}")

    _save_results(changes, already_correct, stats, errors)


def _save_results(changes, already_correct, stats, errors=None):
    data = {
        "run_at":          datetime.now().isoformat(),
        "stats":           stats,
        "changes":         changes,
        "already_correct": already_correct,
        "errors":          errors or [],
    }
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=2)
    log(f"Results saved to {JSON_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",    action="store_true", help="Show changes without applying them")
    parser.add_argument("--check",      action="store_true", help="Report current state only")
    args = parser.parse_args()

    run(dry_run=args.dry_run, check_only=args.check)
