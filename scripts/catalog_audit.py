"""
Comprehensive product catalog audit — Lost Collective
======================================================
Audits all 1,809 products across five dimensions, auto-fixes safe structural
issues, and regenerates copy for products with AI slop or missing descriptions.

Audit dimensions:
  1. Copy quality     — AI slop, empty, too short, first person, em dashes
  2. SEO              — missing/short meta title + description
  3. Metafields       — all 7 required custom.* fields
  4. Structural       — product_type, images, image alt text
  5. SKU format       — LC-{handle}-{size}-{type} pattern

Auto-fixes (safe, no approval needed):
  - product_type ≠ "Fine Art Print"  → corrected via API
  - Image alt text blank             → set to product title
  - SEO title blank                  → set from product title
  - SEO description blank            → set from existing body_html snippet

Queues for copy regeneration (via claude_copy.py):
  - body_html empty or < 80 chars stripped
  - body_html contains AI slop words
  - subject_description empty or < 60 chars

Usage:
  ANTHROPIC_API_KEY=... SHOPIFY_ADMIN_TOKEN=... python3 scripts/catalog_audit.py
  # or via op:
  ANTHROPIC_API_KEY=$(op read "op://Private/yxpyrgwqqu3jn6rn6qcntgekji/credential") \\
  SHOPIFY_ADMIN_TOKEN=$(op read "op://Private/6u6evrxttlqexvzu6et4bpcl3y/Admin Token") \\
  python3 scripts/catalog_audit.py

Flags:
  --audit-only    Run checks, write report, no fixes or regen
  --fix-only      Auto-fix structural issues only, no regen
  --regen-only    Regenerate copy for already-flagged products (reads report)
  --limit N       Process only first N products (for testing)

Output:
  logs/catalog_audit.log            — progress log
  logs/catalog_audit_report.json    — full issue report
  logs/catalog_audit_summary.txt    — human-readable summary
"""

import json, os, re, sys, time, html
from datetime import datetime
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────────

LOG_DIR      = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE     = LOG_DIR / "catalog_audit.log"
REPORT_FILE  = LOG_DIR / "catalog_audit_report.json"
SUMMARY_FILE = LOG_DIR / "catalog_audit_summary.txt"

PAGE_SIZE     = 25   # products per GQL page — keep cost low
REGEN_DELAY   = 2.5  # seconds between Claude API calls
FIX_DELAY     = 0.5  # seconds between Shopify fix calls

REQUIRED_COPY_LENGTH   = 80   # chars stripped — below this triggers regen
REQUIRED_SUBJECT_LEN   = 60   # chars for subject_description
SEO_TITLE_MAX          = 60
SEO_DESC_MIN           = 50
SEO_DESC_MAX           = 160
CORRECT_PRODUCT_TYPE   = "Fine Art Print"
SKU_PATTERN            = re.compile(r"^LC-[\w-]+-(?:XS|S|M|L|XL)-(?:UF|FR|GL)(?:-[A-Z]+)?$", re.IGNORECASE)

# AI slop — mirrors claude_copy.BANNED
BANNED = [
    "stunning", "breathtaking", "captivating", "mesmerising", "mesmerizing",
    "haunting beauty", "hauntingly beautiful", "hidden gem",
    "testament to", "stands as a testament", "bears witness",
    "passage of time", "frozen in time", "whispers of", "echoes of",
    "fleeting beauty", "fleeting moment", "bygone era", "bygone age",
    "once-thriving", "once thriving", "in its heyday",
    "timeless", "evocative", "poignant", "nostalgic",
    "raw beauty", "silent beauty", "quiet beauty",
    "speaks to", "reminds us", "invites you", "beckons",
    "unique", "remarkable", "incredible", "amazing", "wonderful",
    "photographic journey", "visual story", "story of time",
    "art lover", "art lovers", "wall art", "perfect for",
    "add to your collection", "shop now", "discover",
]

# First-person signals that don't belong in storefront product copy
FIRST_PERSON = re.compile(r"\b(I |I'|I'm|I've|I'll|I'd|my |mine\b|we |we're|we've|our |ours\b)\b", re.IGNORECASE)
EM_DASH      = re.compile(r"[—–]")

# ── Logging ────────────────────────────────────────────────────────────────────

def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# ── Shopify GQL ────────────────────────────────────────────────────────────────

sys.path.insert(0, os.path.dirname(__file__))
import shopify_gql as shop

AUDIT_QUERY = """
query AuditProducts($first: Int!, $cursor: String) {
  products(first: $first, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    edges {
      node {
        id
        title
        handle
        status
        productType
        descriptionHtml
        tags
        vendor
        featuredImage { url altText }
        images(first: 5) {
          edges { node { id altText src } }
        }
        seo { title description }
        variants(first: 30) {
          edges {
            node {
              id
              sku
              title
              price
              inventoryItem { tracked }
            }
          }
        }
        metafields(first: 30) {
          edges {
            node { namespace key value type }
          }
        }
      }
    }
  }
}
"""


def iter_all_products(limit: int = 0):
    """Yield all products from the audit query."""
    variables = {"first": PAGE_SIZE, "cursor": None}
    total = 0
    while True:
        resp = shop.gql(AUDIT_QUERY, variables)
        conn = resp["data"]["products"]
        for edge in conn["edges"]:
            yield edge["node"]
            total += 1
            if limit and total >= limit:
                return
        if not conn["pageInfo"]["hasNextPage"] or (limit and total >= limit):
            break
        variables["cursor"] = conn["pageInfo"]["endCursor"]


def get_metafield(metafields: list, namespace: str, key: str) -> str:
    """Extract a metafield value from the edges list."""
    for mf in metafields:
        if mf["namespace"] == namespace and mf["key"] == key:
            return mf["value"] or ""
    return ""


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return " ".join(text.split()).strip()


# ── Check functions ────────────────────────────────────────────────────────────

def check_copy(product: dict, mf: dict) -> list[dict]:
    """Check body_html for quality issues."""
    issues = []
    raw  = product.get("descriptionHtml") or ""
    text = strip_html(raw)

    if not text:
        issues.append({"code": "COPY_EMPTY", "severity": "critical",
                        "detail": "body_html is empty", "regen": True})
        return issues

    if len(text) < REQUIRED_COPY_LENGTH:
        issues.append({"code": "COPY_TOO_SHORT", "severity": "high",
                        "detail": f"{len(text)} chars (min {REQUIRED_COPY_LENGTH})", "regen": True})

    slop = [b for b in BANNED if b in text.lower()]
    if slop:
        issues.append({"code": "COPY_AI_SLOP", "severity": "high",
                        "detail": f"banned words: {slop}", "regen": True})

    if FIRST_PERSON.search(text):
        issues.append({"code": "COPY_FIRST_PERSON", "severity": "medium",
                        "detail": "first-person language in storefront copy", "regen": True})

    if EM_DASH.search(raw):
        issues.append({"code": "COPY_EM_DASH", "severity": "low",
                        "detail": "em dash or en dash found", "regen": False})

    return issues


def check_subject_description(mf: dict) -> list[dict]:
    """Check subject_description metafield."""
    issues = []
    val  = mf.get("subject_description", "")
    text = strip_html(val)

    if not text:
        issues.append({"code": "META_SUBJECT_EMPTY", "severity": "high",
                        "detail": "subject_description metafield missing", "regen": True})
    elif len(text) < REQUIRED_SUBJECT_LEN:
        issues.append({"code": "META_SUBJECT_SHORT", "severity": "medium",
                        "detail": f"{len(text)} chars (min {REQUIRED_SUBJECT_LEN})", "regen": True})
    else:
        slop = [b for b in BANNED if b in text.lower()]
        if slop:
            issues.append({"code": "META_SUBJECT_SLOP", "severity": "high",
                            "detail": f"banned words: {slop}", "regen": True})

    return issues


def check_seo(product: dict) -> list[dict]:
    """Check SEO title and description."""
    issues = []
    seo   = product.get("seo") or {}
    title = (seo.get("title") or "").strip()
    desc  = (seo.get("description") or "").strip()

    if not title:
        issues.append({"code": "SEO_TITLE_MISSING", "severity": "high",
                        "detail": "SEO title not set", "fix": "seo_title"})
    elif len(title) > SEO_TITLE_MAX:
        issues.append({"code": "SEO_TITLE_LONG", "severity": "low",
                        "detail": f"{len(title)} chars (max {SEO_TITLE_MAX})", "fix": None})

    if not desc:
        issues.append({"code": "SEO_DESC_MISSING", "severity": "high",
                        "detail": "SEO description not set", "fix": "seo_desc"})
    elif len(desc) > SEO_DESC_MAX:
        issues.append({"code": "SEO_DESC_LONG", "severity": "low",
                        "detail": f"{len(desc)} chars (max {SEO_DESC_MAX})", "fix": None})
    elif len(desc) < SEO_DESC_MIN:
        issues.append({"code": "SEO_DESC_SHORT", "severity": "medium",
                        "detail": f"{len(desc)} chars (min {SEO_DESC_MIN})", "fix": None})

    slop_in_seo = [b for b in BANNED if b in (title + " " + desc).lower()]
    if slop_in_seo:
        issues.append({"code": "SEO_SLOP", "severity": "medium",
                        "detail": f"banned words in SEO fields: {slop_in_seo}", "fix": None})

    return issues


def check_metafields(mf: dict) -> list[dict]:
    """Check all required custom metafields are present."""
    issues = []
    required = [
        ("collection_series", "high"),
        ("location",          "high"),
        ("year_photographed", "medium"),
        ("print_technique",   "medium"),
        ("paper_type",        "medium"),
        ("certificate_included", "low"),
    ]
    for key, severity in required:
        if not mf.get(key, "").strip():
            issues.append({"code": f"META_{key.upper()}_MISSING", "severity": severity,
                            "detail": f"custom.{key} not set", "fix": None})
    return issues


def check_structural(product: dict) -> list[dict]:
    """Check product_type, images, image alt text."""
    issues = []

    if product.get("productType") != CORRECT_PRODUCT_TYPE:
        issues.append({"code": "STRUCT_PRODUCT_TYPE", "severity": "medium",
                        "detail": f"productType is '{product.get('productType')}' not '{CORRECT_PRODUCT_TYPE}'",
                        "fix": "product_type"})

    images = [e["node"] for e in (product.get("images") or {}).get("edges", [])]
    if not images:
        issues.append({"code": "STRUCT_NO_IMAGES", "severity": "critical",
                        "detail": "product has no images", "fix": None})
    else:
        missing_alt = [img for img in images if not (img.get("altText") or "").strip()]
        if missing_alt:
            issues.append({"code": "STRUCT_IMAGE_ALT_MISSING", "severity": "low",
                            "detail": f"{len(missing_alt)} image(s) missing alt text",
                            "fix": "image_alt"})

    return issues


def check_skus(product: dict) -> list[dict]:
    """Check SKU format on all variants."""
    issues = []
    variants = [e["node"] for e in (product.get("variants") or {}).get("edges", [])]
    bad_skus = []
    for v in variants:
        sku = (v.get("sku") or "").strip()
        if not sku:
            bad_skus.append(f"'{v.get('title')}' — no SKU")
        elif not SKU_PATTERN.match(sku):
            bad_skus.append(f"'{sku}'")
    if bad_skus:
        issues.append({"code": "SKU_FORMAT", "severity": "medium",
                        "detail": f"non-standard SKUs: {bad_skus[:5]}", "fix": None})
    return issues


# ── Auto-fix functions ─────────────────────────────────────────────────────────

def fix_product_type(product_gid: str):
    """Set productType to 'Fine Art Print'."""
    shop.gql("""
        mutation($input: ProductUpdateInput!) {
          productUpdate(product: $input) {
            product { id productType }
            userErrors { field message }
          }
        }
    """, {"input": {"id": product_gid, "productType": CORRECT_PRODUCT_TYPE}})


def fix_image_alt(image_id: str, product_title: str):
    """Set alt text on an image to product title."""
    shop.gql("""
        mutation($id: ID!, $alt: String!) {
          fileUpdate(files: [{ id: $id, alt: $alt }]) {
            files { ... on MediaImage { id alt } }
            userErrors { field message }
          }
        }
    """, {"id": image_id, "alt": product_title})


def fix_seo(product_gid: str, title: str, description: str):
    """Set SEO title and description on a product."""
    shop.gql("""
        mutation($input: ProductUpdateInput!) {
          productUpdate(product: $input) {
            product { id seo { title description } }
            userErrors { field message }
          }
        }
    """, {"input": {"id": product_gid, "seo": {"title": title, "description": description}}})


# ── Copy regeneration ──────────────────────────────────────────────────────────

import claude_copy as copy_gen

def regenerate_product(product: dict, mf: dict, needs_body: bool, needs_subject: bool):
    """
    Regenerate body_html (via Claude Opus) and/or subject_description (Sonnet)
    for a product. Pushes directly to Shopify if output is clean.
    Flags needs_review items in the log but does not push them.
    """
    title     = product["title"]
    series    = mf.get("collection_series", "")
    location  = mf.get("location", "")
    year      = mf.get("year_photographed", "")
    image_url = (product.get("featuredImage") or {}).get("url", "")

    if needs_subject:
        log(f"    [Sonnet] subject_description: {title}")
        try:
            result = copy_gen.subject_description(
                title=title, series=series, location=location,
                year=year, image_url=image_url,
            )
            if not result.get("needs_review"):
                shop.metafields_set([{
                    "ownerId":   product["id"],
                    "namespace": "custom",
                    "key":       "subject_description",
                    "value":     result["text"],
                    "type":      "multi_line_text_field",
                }])
                log(f"      ✓ pushed")
            else:
                log(f"      ⚠ needs_review — not pushed (violations: {result['violations']})")
        except Exception as e:
            log(f"      ✗ error: {e}")
        time.sleep(REGEN_DELAY)

    if needs_body:
        log(f"    [Opus] body_html: {title}")
        existing = product.get("descriptionHtml") or ""
        try:
            result = copy_gen.product_description(
                title=title, series=series, location=location,
                year=year, image_url=image_url, existing=existing,
            )
            if not result.get("needs_review"):
                shop.gql("""
                    mutation UpdateBody($input: ProductUpdateInput!) {
                      productUpdate(product: $input) {
                        product { id }
                        userErrors { field message }
                      }
                    }
                """, {"input": {"id": product["id"],
                                "descriptionHtml": f"<p>{result['text']}</p>"}})
                log(f"      ✓ pushed")
            else:
                log(f"      ⚠ needs_review — not pushed (violations: {result['violations']})")
        except Exception as e:
            log(f"      ✗ error: {e}")
        time.sleep(REGEN_DELAY)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-only",  action="store_true", help="Report only, no fixes")
    parser.add_argument("--fix-only",    action="store_true", help="Fix structural issues only")
    parser.add_argument("--regen-only",  action="store_true", help="Regen copy only (reads existing report)")
    parser.add_argument("--limit",       type=int, default=0, help="Process only first N products")
    args = parser.parse_args()

    audit_only = args.audit_only
    fix_only   = args.fix_only
    regen_only = args.regen_only
    limit      = args.limit

    log("=" * 60)
    log("Lost Collective — Catalog Audit")
    log(f"Mode: {'audit-only' if audit_only else 'fix-only' if fix_only else 'regen-only' if regen_only else 'full'}")
    if limit:
        log(f"Limit: {limit} products")
    log("=" * 60)

    # ── If regen-only, read existing report ──────────────────────────────────
    if regen_only:
        if not REPORT_FILE.exists():
            sys.exit("No report file found. Run a full audit first.")
        with open(REPORT_FILE) as f:
            report = json.load(f)
        products_to_regen = [p for p in report["products"] if p.get("needs_regen")]
        log(f"Regen-only mode: {len(products_to_regen)} products flagged")
        for entry in products_to_regen:
            product_node = shop.gql("""
                query($id: ID!) {
                  product(id: $id) {
                    id title handle featuredImage { url altText }
                    metafields(first: 20) { edges { node { namespace key value } } }
                  }
                }
            """, {"id": entry["id"]})["data"]["product"]
            mf_list = [e["node"] for e in (product_node.get("metafields") or {}).get("edges", [])]
            mf = {m["key"]: m["value"] for m in mf_list if m["namespace"] == "custom"}
            regenerate_product(product_node, mf,
                               needs_body=entry.get("regen_body", False),
                               needs_subject=entry.get("regen_subject", False))
        log("Regen complete.")
        return

    # ── Full audit pass ──────────────────────────────────────────────────────
    report = {
        "run_at": datetime.now().isoformat(),
        "products": [],
        "totals": {
            "scanned": 0, "clean": 0, "issues": 0,
            "auto_fixed": 0, "regen_queued": 0,
            "by_code": {},
        },
    }

    counters = report["totals"]

    for product in iter_all_products(limit=limit):
        counters["scanned"] += 1
        pid   = product["id"]
        title = product["title"]
        n     = counters["scanned"]

        if n % 50 == 0:
            log(f"  {n} products scanned...")

        # Parse metafields
        mf_list = [e["node"] for e in (product.get("metafields") or {}).get("edges", [])]
        mf = {m["key"]: m["value"] for m in mf_list if m["namespace"] == "custom"}

        # Run all checks
        all_issues = (
            check_copy(product, mf) +
            check_subject_description(mf) +
            check_seo(product) +
            check_metafields(mf) +
            check_structural(product) +
            check_skus(product)
        )

        if not all_issues:
            counters["clean"] += 1
            continue

        counters["issues"] += 1
        for issue in all_issues:
            code = issue["code"]
            counters["by_code"][code] = counters["by_code"].get(code, 0) + 1

        needs_regen   = any(i.get("regen") for i in all_issues)
        needs_body    = any(i["code"].startswith("COPY_") and i.get("regen") for i in all_issues)
        needs_subject = any(i["code"].startswith("META_SUBJECT") and i.get("regen") for i in all_issues)

        entry = {
            "id":             pid,
            "title":          title,
            "handle":         product["handle"],
            "issues":         all_issues,
            "needs_regen":    needs_regen,
            "regen_body":     needs_body,
            "regen_subject":  needs_subject,
            "auto_fixed":     [],
        }

        if not audit_only:
            images = [e["node"] for e in (product.get("images") or {}).get("edges", [])]

            # Fix: product_type
            if any(i["code"] == "STRUCT_PRODUCT_TYPE" for i in all_issues):
                try:
                    fix_product_type(pid)
                    entry["auto_fixed"].append("product_type")
                    counters["auto_fixed"] += 1
                    log(f"  ✓ fixed product_type: {title}")
                    time.sleep(FIX_DELAY)
                except Exception as e:
                    log(f"  ✗ product_type fix failed: {e}")

            # Fix: image alt text
            if any(i["code"] == "STRUCT_IMAGE_ALT_MISSING" for i in all_issues):
                for img in images:
                    if not (img.get("altText") or "").strip():
                        try:
                            fix_image_alt(img["id"], title)
                            time.sleep(FIX_DELAY)
                        except Exception as e:
                            log(f"  ✗ image alt fix failed: {e}")
                entry["auto_fixed"].append("image_alt")
                counters["auto_fixed"] += 1

            # Fix: SEO fields (derive from existing content if blank)
            seo_issues = [i for i in all_issues if i["code"] in ("SEO_TITLE_MISSING", "SEO_DESC_MISSING")]
            if seo_issues and not fix_only:
                seo   = product.get("seo") or {}
                s_title = (seo.get("title") or "").strip()
                s_desc  = (seo.get("description") or "").strip()
                body_text = strip_html(product.get("descriptionHtml") or "")

                if not s_title:
                    series = mf.get("collection_series", "")
                    s_title = f"{title} | Lost Collective" if not series else f"{title} | {series} | Lost Collective"
                    s_title = s_title[:SEO_TITLE_MAX]

                if not s_desc and body_text:
                    s_desc = body_text[:SEO_DESC_MAX]

                if s_title or s_desc:
                    try:
                        fix_seo(pid, s_title, s_desc)
                        entry["auto_fixed"].append("seo")
                        counters["auto_fixed"] += 1
                        time.sleep(FIX_DELAY)
                    except Exception as e:
                        log(f"  ✗ SEO fix failed: {e}")

        if needs_regen and not audit_only and not fix_only:
            counters["regen_queued"] += 1
            try:
                regenerate_product(product, mf,
                                   needs_body=needs_body,
                                   needs_subject=needs_subject)
                entry["auto_fixed"].append("copy_regen")
            except Exception as e:
                log(f"  ✗ regen failed for {title}: {e}")

        report["products"].append(entry)

    # ── Write report ──────────────────────────────────────────────────────────
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)

    # ── Write summary ─────────────────────────────────────────────────────────
    lines = [
        "Lost Collective — Catalog Audit Summary",
        f"Run at: {report['run_at']}",
        "",
        f"Products scanned:    {counters['scanned']}",
        f"Clean (no issues):   {counters['clean']}",
        f"With issues:         {counters['issues']}",
        f"Auto-fixed:          {counters['auto_fixed']}",
        f"Copy regenerated:    {counters['regen_queued']}",
        "",
        "Issues by type:",
    ]
    for code, count in sorted(counters["by_code"].items(), key=lambda x: -x[1]):
        lines.append(f"  {code:<35} {count}")

    lines += [
        "",
        "Critical issues (products with no images or empty copy):",
    ]
    for p in report["products"]:
        critical = [i for i in p["issues"] if i["severity"] == "critical"]
        if critical:
            lines.append(f"  {p['handle']} — {', '.join(i['code'] for i in critical)}")

    summary = "\n".join(lines)
    with open(SUMMARY_FILE, "w") as f:
        f.write(summary)

    log("")
    log("=" * 60)
    log(summary)
    log("=" * 60)
    log(f"Full report: {REPORT_FILE}")
    log(f"Summary:     {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
