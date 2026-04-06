"""
Fix em dashes in product body_html — Lost Collective
=====================================================
Reads the catalog audit report, fetches body_html for flagged products,
replaces em dashes (— –) with a clean rewrite, and pushes back via API.

Strategy:
  " — " → " - "   (mid-sentence connector)
  "—"   → ":"      (introducing a clause)
  "–"   → "-"      (en dash, range or connector)

Then cleans up any double spaces or orphaned punctuation.

Usage:
  op run --env-file=.env.tpl -- python3 shopify/scripts/fix_em_dashes.py
  op run --env-file=.env.tpl -- python3 shopify/scripts/fix_em_dashes.py --dry-run

Output:
  logs/fix_em_dashes.log
"""

import re, sys, time, html as html_lib, argparse
import json
from pathlib import Path

REPORT_FILE = Path("logs/catalog_audit_report.json")
LOG_FILE    = Path("logs/fix_em_dashes.log")

LOG_FILE.parent.mkdir(exist_ok=True)
_log_fh = open(LOG_FILE, "w")

def log(msg):
    print(msg)
    _log_fh.write(msg + "\n")
    _log_fh.flush()

sys.path.insert(0, str(Path(__file__).parent))
from shopify_gql import gql

PRODUCT_BODY_QUERY = """
query getBody($id: ID!) {
  product(id: $id) { id bodyHtml }
}
"""

PRODUCT_UPDATE = """
mutation productUpdate($input: ProductInput!) {
  productUpdate(input: $input) {
    product { id }
    userErrors { field message }
  }
}
"""

# Note: ProductInput uses descriptionHtml, not bodyHtml

def fix_dashes(text: str) -> str:
    # em dash surrounded by spaces → hyphen with spaces
    text = re.sub(r'\s*\u2014\s*', ' - ', text)
    # en dash surrounded by spaces → hyphen
    text = re.sub(r'\s*\u2013\s*', '-', text)
    # HTML entities
    text = text.replace('&mdash;', ' - ').replace('&ndash;', '-')
    # Clean up double spaces
    text = re.sub(r'  +', ' ', text)
    return text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    dry_run = args.dry_run

    if not REPORT_FILE.exists():
        log(f"Report not found: {REPORT_FILE} — run catalog_audit.py --audit-only first.")
        sys.exit(1)

    with open(REPORT_FILE) as f:
        report = json.load(f)

    targets = [
        p for p in report.get("products", [])
        if any(i["code"] == "COPY_EM_DASH" for i in p.get("issues", []))
    ]
    if args.limit:
        targets = targets[:args.limit]

    log("=" * 60)
    log(f"Fix Em Dashes — Lost Collective")
    log(f"Mode: {'dry-run' if dry_run else 'live'}")
    log(f"Products to fix: {len(targets)}")
    log("=" * 60)

    fixed = errors = 0

    for i, entry in enumerate(targets, 1):
        gid   = entry["id"]
        title = entry["title"]
        log(f"\n[{i}/{len(targets)}] {title}")

        try:
            resp = gql(PRODUCT_BODY_QUERY, {"id": gid})
            body = resp["data"]["product"]["bodyHtml"] or ""
        except Exception as e:
            log(f"  ✗ fetch failed: {e}")
            errors += 1
            continue

        new_body = fix_dashes(body)

        if new_body == body:
            log("  — no dashes found in HTML, skipping")
            continue

        log(f"  fixed dashes")
        if dry_run:
            log("  [dry-run] would update")
            fixed += 1
            continue

        resp = gql(PRODUCT_UPDATE, {"input": {"id": gid, "descriptionHtml": new_body}})
        errs = resp.get("data", {}).get("productUpdate", {}).get("userErrors", [])
        if errs:
            log(f"  ✗ {errs}")
            errors += 1
        else:
            log("  ✓ updated")
            fixed += 1

        time.sleep(0.4)

    log("\n" + "=" * 60)
    log(f"Fixed: {fixed}  |  Errors: {errors}")
    log("=" * 60)

if __name__ == "__main__":
    main()
