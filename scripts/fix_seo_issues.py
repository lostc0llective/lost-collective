"""
Fix SEO issues flagged in catalog audit — Lost Collective
=========================================================
Reads logs/catalog_audit_report.json and fixes:
  - SEO_TITLE_MISSING  — set from product title (truncated to 60 chars)
  - SEO_TITLE_LONG     — truncate to 60 chars at word boundary
  - SEO_DESC_MISSING   — generate from body_html snippet
  - SEO_DESC_SHORT     — expand using body_html snippet
  - SEO_DESC_LONG      — truncate to 160 chars at sentence boundary
  - SEO_SLOP           — strip banned words from SEO description

Does NOT use Claude API — all fixes are deterministic.
Run after catalog_audit.py --audit-only to populate the report.

Usage:
  op run --env-file=.env.tpl -- python3 shopify/scripts/fix_seo_issues.py
  op run --env-file=.env.tpl -- python3 shopify/scripts/fix_seo_issues.py --dry-run
  op run --env-file=.env.tpl -- python3 shopify/scripts/fix_seo_issues.py --limit 10

Output:
  logs/fix_seo_issues.log
"""

import json, re, sys, time, html, argparse
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────────

REPORT_FILE   = Path("logs/catalog_audit_report.json")
LOG_FILE      = Path("logs/fix_seo_issues.log")
SEO_TITLE_MAX = 60
SEO_DESC_MIN  = 50
SEO_DESC_MAX  = 160

# Banned words/phrases to strip from SEO fields
SEO_BANNED = [
    "wall art", "fine art print", "fine-art print",
    "stunning", "breathtaking", "captivating", "mesmerising", "mesmerizing",
    "haunting beauty", "hauntingly beautiful",
    "testament to", "stands as a testament", "bears witness",
    "passage of time", "frozen in time", "whispers of", "echoes of",
    "timeless", "evocative", "poignant", "nostalgic",
    "unique", "remarkable", "incredible", "amazing", "wonderful",
    "photographic journey", "visual story",
    "transform your walls", "transform your space", "transform your home",
    "perfect for any room", "perfect addition",
    "elevate your", "enhance your",
]

# ── Logging ────────────────────────────────────────────────────────────────────

LOG_FILE.parent.mkdir(exist_ok=True)
_log_fh = open(LOG_FILE, "w")

def log(msg: str):
    print(msg)
    _log_fh.write(msg + "\n")
    _log_fh.flush()

# ── Imports ────────────────────────────────────────────────────────────────────

sys.path.insert(0, str(Path(__file__).parent))
from shopify_gql import gql, iter_products

# ── Helpers ────────────────────────────────────────────────────────────────────

def strip_html(text: str) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def truncate_words(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    truncated = text[:max_len]
    last_space = truncated.rfind(" ")
    if last_space > max_len - 15:
        truncated = truncated[:last_space]
    return truncated.rstrip(",.;: —–-")

def truncate_sentences(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    # Try to end at sentence boundary
    truncated = text[:max_len]
    for sep in (". ", "! ", "? "):
        idx = truncated.rfind(sep)
        if idx > max_len - 40:
            return truncated[:idx + 1]
    return truncate_words(truncated, max_len)

def strip_seo_banned(text: str) -> str:
    for phrase in sorted(SEO_BANNED, key=len, reverse=True):
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        text = pattern.sub("", text)
    text = re.sub(r"\s{2,}", " ", text).strip().lstrip(".,;: —–-").strip()
    return text

def make_seo_desc(product_title: str, body_html: str, max_len: int = SEO_DESC_MAX) -> str:
    plain = strip_html(body_html)
    if not plain:
        return ""
    # Take first clean sentences up to max_len
    desc = truncate_sentences(plain, max_len)
    desc = strip_seo_banned(desc)
    if len(desc) < SEO_DESC_MIN:
        desc = truncate_sentences(plain, max_len)
    return desc[:max_len]

# ── Shopify SEO update ─────────────────────────────────────────────────────────

PRODUCT_UPDATE = """
mutation productUpdate($input: ProductInput!) {
  productUpdate(input: $input) {
    product {
      id
      seo { title description }
    }
    userErrors { field message }
  }
}
"""

PRODUCT_SEO_QUERY = """
query getProductSeo($id: ID!) {
  product(id: $id) {
    id
    title
    bodyHtml
    seo { title description }
  }
}
"""

def get_product_seo(product_gid: str) -> dict:
    resp = gql(PRODUCT_SEO_QUERY, {"id": product_gid})
    return resp["data"]["product"]

def update_seo(product_gid: str, seo_title: str, seo_desc: str, dry_run: bool = False) -> bool:
    if dry_run:
        return True
    resp = gql(PRODUCT_UPDATE, {
        "input": {
            "id": product_gid,
            "seo": {"title": seo_title, "description": seo_desc}
        }
    })
    errors = resp.get("data", {}).get("productUpdate", {}).get("userErrors", [])
    if errors:
        log(f"    ✗ userErrors: {errors}")
        return False
    return True

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    dry_run = args.dry_run

    if not REPORT_FILE.exists():
        log(f"Report not found: {REPORT_FILE}")
        log("Run catalog_audit.py --audit-only first.")
        sys.exit(1)

    with open(REPORT_FILE) as f:
        report = json.load(f)

    products = report.get("products", [])

    # Filter to products with SEO issues
    seo_codes = {"SEO_TITLE_MISSING", "SEO_TITLE_LONG", "SEO_DESC_MISSING",
                 "SEO_DESC_SHORT", "SEO_DESC_LONG", "SEO_SLOP"}
    targets = [
        p for p in products
        if any(i["code"] in seo_codes for i in p.get("issues", []))
    ]

    if args.limit:
        targets = targets[:args.limit]

    log("=" * 60)
    log(f"Fix SEO Issues — Lost Collective")
    log(f"Mode: {'dry-run' if dry_run else 'live'}")
    log(f"Products to fix: {len(targets)}")
    log("=" * 60)

    fixed = 0
    errors = 0

    for i, entry in enumerate(targets, 1):
        gid = entry["id"]
        title = entry["title"]
        issue_codes = [iss["code"] for iss in entry.get("issues", [])]

        log(f"\n[{i}/{len(targets)}] {title}")

        # Fetch current SEO data
        try:
            product = get_product_seo(gid)
        except Exception as e:
            log(f"  ✗ fetch failed: {e}")
            errors += 1
            continue

        current_seo_title = (product.get("seo") or {}).get("title") or ""
        current_seo_desc  = (product.get("seo") or {}).get("description") or ""
        product_title     = product.get("title") or title
        body_html         = product.get("bodyHtml") or ""

        # Compute new SEO title
        new_seo_title = current_seo_title or product_title
        # Strip slop from title
        new_seo_title = strip_seo_banned(new_seo_title)
        # If stripping gutted it, fall back to product title
        if len(new_seo_title) < 10:
            new_seo_title = product_title
        if len(new_seo_title) > SEO_TITLE_MAX:
            new_seo_title = truncate_words(new_seo_title, SEO_TITLE_MAX)
        new_seo_title = new_seo_title.strip()

        # Compute new SEO description
        new_seo_desc = current_seo_desc

        if not new_seo_desc or "SEO_DESC_MISSING" in issue_codes:
            new_seo_desc = make_seo_desc(product_title, body_html)
        elif "SEO_SLOP" in issue_codes:
            new_seo_desc = strip_seo_banned(new_seo_desc)
            if len(new_seo_desc) < SEO_DESC_MIN:
                new_seo_desc = make_seo_desc(product_title, body_html)
        elif "SEO_DESC_LONG" in issue_codes:
            new_seo_desc = truncate_sentences(new_seo_desc, SEO_DESC_MAX)
        elif "SEO_DESC_SHORT" in issue_codes:
            new_seo_desc = make_seo_desc(product_title, body_html)

        new_seo_desc = new_seo_desc[:SEO_DESC_MAX].strip()

        log(f"  title: {new_seo_title[:70]}")
        log(f"  desc:  {new_seo_desc[:80]}...")

        ok = update_seo(gid, new_seo_title, new_seo_desc, dry_run)
        if ok:
            fixed += 1
            log(f"  {'[dry-run] ' if dry_run else ''}✓ updated")
        else:
            errors += 1

        time.sleep(0.4)

    log("\n" + "=" * 60)
    log(f"Fixed: {fixed}  |  Errors: {errors}")
    log("=" * 60)

if __name__ == "__main__":
    main()
