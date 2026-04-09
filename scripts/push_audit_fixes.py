#!/usr/bin/env python3
"""
push_audit_fixes.py — Pushes all post-audit code changes to production.

Run from ~/lost-collective/ root:
  SHOPIFY_ENV=production op run --env-file=.env.tpl -- python3 shopify/scripts/push_audit_fixes.py

Changes pushed:
  1. snippets/options-radios.liquid   — Legacy JS block removed (CRITICAL: was throwing TypeErrors
                                        on every product page, 209 lines + 15 dead CDN images gone)
  2. assets/custom.css                — Liquid comment tags removed from plain CSS file,
                                        var(--color-brand-yellow)14 alpha hack fixed,
                                        TOC updated with sections 31-33,
                                        .lc-collector-discount styles (from session handoff),
                                        z-index fix: header raised to z-200 so mega menu column
                                        headings render above the announcement bar section (z-90)
  3. snippets/product__images.liquid  — lazybeforeunveil handler scoped to gallery container
  4. snippets/social-meta-info.liquid — OG fallback URL cleaned up and documented
  5. snippets/product__form.liquid    — Collector discount notice (from session handoff)
"""

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from config import STORE, ADMIN_TOKEN, require_production_confirmation, production_banner

require_production_confirmation('push_audit_fixes')
production_banner()

try:
    import requests
except ImportError:
    print("requests not installed. Run: pip install requests --break-system-packages", file=sys.stderr)
    sys.exit(1)

THEME_ID = "143356625062"
BASE_URL = f"https://{STORE}/admin/api/2025-01/themes/{THEME_ID}/assets.json"
HEADERS = {"X-Shopify-Access-Token": ADMIN_TOKEN, "Content-Type": "application/json"}

ROOT = os.path.join(SCRIPT_DIR, "..", "..")

FILES = [
    ("snippets/options-radios.liquid",   "shopify/snippets/options-radios.liquid"),
    ("assets/custom.css",                "shopify/assets/custom.css"),
    ("snippets/product__images.liquid",  "shopify/snippets/product__images.liquid"),
    ("snippets/social-meta-info.liquid", "shopify/snippets/social-meta-info.liquid"),
    ("snippets/product__form.liquid",    "shopify/snippets/product__form.liquid"),
]

passed, failed = 0, []

for shopify_key, local_path in FILES:
    full_path = os.path.normpath(os.path.join(ROOT, local_path))
    if not os.path.exists(full_path):
        print(f"  SKIP (not found locally): {local_path}")
        continue
    with open(full_path, encoding="utf-8") as f:
        content = f.read()
    r = requests.put(BASE_URL, headers=HEADERS, json={"asset": {"key": shopify_key, "value": content}}, timeout=30)
    response_data = r.json()
    if "asset" in response_data:
        print(f"  pushed: {shopify_key}")
        passed += 1
    else:
        print(f"  ERROR: {shopify_key}: {response_data.get('errors', r.text[:200])}", file=sys.stderr)
        failed.append(shopify_key)

print(f"\n{passed}/{passed + len(failed)} files pushed.")
if failed:
    print(f"Failed: {', '.join(failed)}", file=sys.stderr)
    sys.exit(1)
print("\nDone. Then deploy dashboard: cd ~/lost-collective/dashboard && npx vercel --prod --yes")
