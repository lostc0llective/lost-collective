"""
Meta Custom Audiences — Lost Collective
Refreshes the "Shopify Customers" custom audience with current buyer emails.

Steps:
  1. Pull all paid orders from Shopify → unique customer emails
  2. Normalise + SHA-256 hash each email (Meta requirement)
  3. Replace audience users via Meta Graph API

Run: op run --env-file=.env.tpl -- python3 scripts/meta_audiences.py

Commands:
  python3 scripts/meta_audiences.py list          — list all custom audiences
  python3 scripts/meta_audiences.py refresh       — dry run (prints email count, no upload)
  python3 scripts/meta_audiences.py refresh --go  — live upload to Meta
  python3 scripts/meta_audiences.py lookalikes    — list lookalike audiences
"""

import hashlib, json, os, sys, time, urllib.request, urllib.parse
from typing import Generator

# ── Config ─────────────────────────────────────────────────────────────────────

AD_ACCOUNT  = "act_2044897662414265"
GRAPH_API   = "https://graph.facebook.com/v19.0"
AUDIENCE_NAME = "Shopify Customers 2025.csv"  # target audience to replace


# ── Meta HTTP helpers ───────────────────────────────────────────────────────────

def _token() -> str:
    token = os.environ.get("META_ACCESS_TOKEN")
    if not token:
        sys.exit("META_ACCESS_TOKEN not set. Run via: op run --env-file=.env.tpl -- python3 ...")
    return token


def _get(path: str, params: dict = None) -> dict:
    p = {"access_token": _token(), **(params or {})}
    url = f"{GRAPH_API}/{path.lstrip('/')}?{urllib.parse.urlencode(p)}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())


def _post(path: str, payload: dict) -> dict:
    # Custom audiences endpoint requires form-encoded body with payload as JSON string
    body = {**payload, "access_token": _token()}
    # Serialize nested dicts/lists as JSON strings (Meta API requirement for payload field)
    form_parts = {}
    for k, v in body.items():
        form_parts[k] = json.dumps(v) if isinstance(v, (dict, list)) else str(v)
    data = urllib.parse.urlencode(form_parts).encode()
    req = urllib.request.Request(
        f"{GRAPH_API}/{path.lstrip('/')}",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {body}") from e


def _delete_post(path: str, payload: dict) -> dict:
    """POST to remove users from an audience."""
    data = json.dumps({**payload, "access_token": _token()}).encode()
    req = urllib.request.Request(
        f"{GRAPH_API}/{path.lstrip('/')}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="DELETE"
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


# ── Audience management ─────────────────────────────────────────────────────────

def list_audiences() -> list:
    """All custom audiences in the ad account."""
    data = _get(f"{AD_ACCOUNT}/customaudiences", {
        "fields": "id,name,approximate_count_lower_bound,approximate_count_upper_bound,subtype,description"
    })
    return data.get("data", [])


def find_audience(name: str) -> dict | None:
    """Find a custom audience — exact match first, then partial (non-lookalike)."""
    audiences = list_audiences()
    for a in audiences:
        if a.get("name", "").lower() == name.lower():
            return a
    for a in audiences:
        if name.lower() in a.get("name", "").lower() and a.get("subtype") != "LOOKALIKE":
            return a
    return None


def list_lookalikes() -> list:
    """Lookalike audiences derived from custom audiences."""
    data = _get(f"{AD_ACCOUNT}/customaudiences", {
        "fields": "id,name,approximate_count_lower_bound,approximate_count_upper_bound,subtype"
    })
    return [a for a in data.get("data", []) if a.get("subtype") == "LOOKALIKE"]


# ── Email hashing ───────────────────────────────────────────────────────────────

def hash_email(email: str) -> str:
    """Normalise and SHA-256 hash an email per Meta's spec."""
    normalised = email.strip().lower()
    return hashlib.sha256(normalised.encode()).hexdigest()


# ── Shopify customer pull ───────────────────────────────────────────────────────

def pull_buyers_with_value() -> list[tuple[str, float]]:
    """
    Pull unique customer emails + lifetime spend from all paid orders.
    Returns list of (email, total_spend_aud) sorted by spend desc.
    Used for value-based custom audiences — spend drives lookalike quality.
    """
    sys.path.insert(0, os.path.dirname(__file__))
    from shopify_gql import iter_orders

    spend: dict[str, float] = {}   # email → cumulative spend
    count = 0
    print("Pulling paid orders from Shopify...")
    for order in iter_orders("financial_status:paid"):
        customer = order.get("customer")
        if customer and customer.get("email"):
            email = customer["email"].strip().lower()
            amount = float(
                order.get("totalPriceSet", {})
                     .get("shopMoney", {})
                     .get("amount", 0)
            )
            spend[email] = spend.get(email, 0.0) + amount
        count += 1
        if count % 100 == 0:
            print(f"  {count} orders scanned, {len(spend)} unique emails so far...")

    print(f"  Done — {count} paid orders, {len(spend)} unique customer emails")
    return sorted(spend.items(), key=lambda x: x[1], reverse=True)


# ── Meta upload ─────────────────────────────────────────────────────────────────

BATCH_SIZE = 10_000   # Meta max per request


def replace_audience(audience_id: str, buyers: list[tuple[str, float]]) -> dict:
    """
    Replace all users in a value-based custom audience.
    buyers: list of (email, spend_value) tuples.
    Uses EMAIL_SHA256 + LOOKALIKE_VALUE schema (required for value-based audiences).
    """
    rows = [[hash_email(email), f"{value:.2f}"] for email, value in buyers]
    batches = [rows[i:i+BATCH_SIZE] for i in range(0, len(rows), BATCH_SIZE)]
    print(f"  Uploading {len(rows):,} hashed email+value rows in {len(batches)} batch(es)...")

    results = []
    for i, batch in enumerate(batches, 1):
        payload = {
            "payload": {
                "schema": ["EMAIL_SHA256", "LOOKALIKE_VALUE"],
                "data": batch,
            }
        }
        resp = _post(f"{audience_id}/users", payload)
        results.append(resp)
        print(f"  Batch {i}/{len(batches)}: {resp}")
        if len(batches) > 1:
            time.sleep(1)

    return {"batches": len(batches), "results": results}


def create_audience(name: str, description: str = "") -> dict:
    """Create a new CUSTOM FILE (email) audience in the ad account."""
    resp = _post(f"{AD_ACCOUNT}/customaudiences", {
        "name": name,
        "description": description or f"Created via Claude Code — {name}",
        "subtype": "CUSTOM",
        "customer_file_source": "USER_PROVIDED_ONLY",
    })
    return resp


# ── CLI ─────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    go  = "--go" in sys.argv

    if cmd == "list":
        audiences = list_audiences()
        print(f"\nCustom audiences — {AD_ACCOUNT}\n{'─'*70}")
        for a in audiences:
            lo = a.get("approximate_count_lower_bound", "?")
            hi = a.get("approximate_count_upper_bound", "?")
            size = f"{lo:,}–{hi:,}" if isinstance(lo, int) else f"{lo}–{hi}"
            print(f"  {a['id']:<20} {a.get('name',''):<40} ~{size}")

    elif cmd == "lookalikes":
        lals = list_lookalikes()
        print(f"\nLookalike audiences — {AD_ACCOUNT}\n{'─'*70}")
        for a in lals:
            lo = a.get("approximate_count_lower_bound", -1)
            print(f"  {a['id']:<20} {a.get('name',''):<50} ~{lo:,}")

    elif cmd == "refresh":
        # 1. Pull buyers with spend values
        buyers = pull_buyers_with_value()
        print(f"\n  {len(buyers):,} buyers ready (email + lifetime spend as lookalike value)")
        top5 = buyers[:5]
        for email, val in top5:
            print(f"    {email[:4]}***  ${val:,.2f}")

        # 2. Find target audience
        audience = find_audience(AUDIENCE_NAME)
        if not audience:
            print(f"\nNo audience matching '{AUDIENCE_NAME}' found.")
            print("Run with 'list' to see available audiences.")
            sys.exit(1)

        print(f"\n  Target audience: {audience['name']} (ID: {audience['id']})")
        lo = audience.get("approximate_count_lower_bound", "?")
        hi = audience.get("approximate_count_upper_bound", "?")
        print(f"  Current size:   ~{lo}–{hi}")

        if not go:
            print(f"\n  DRY RUN — pass --go to upload {len(buyers):,} buyers to Meta")
            sys.exit(0)

        # 3. Upload
        print(f"\n  Uploading to Meta...")
        result = replace_audience(audience["id"], buyers)
        print(f"\n  Upload complete: {result}")

    else:
        print("Usage: python3 scripts/meta_audiences.py [list|lookalikes|refresh [--go]]")
