"""
Yotpo Reviews API — Lost Collective
App Key:    DMhRLW22rOTwZUUJ9Qk10NvNhssBqTmT5xeoXVRw
Account ID: 347682

Credentials: 1Password → "Lost Collective — Yotpo"
Run: op run --env-file=.env.tpl -- python3 scripts/yotpo.py

Key operations:
  reviews()         — all store reviews, sorted by date
  ratings()         — per-product average ratings and review counts
  stats()           — account summary (total reviews, average rating)
  pending()         — reviews awaiting moderation
"""

import json, os, sys, urllib.request, urllib.parse
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────────

API_BASE    = "https://api.yotpo.com"
ACCOUNT_ID  = os.environ.get("YOTPO_ACCOUNT_ID", "347682")


# ── Auth ───────────────────────────────────────────────────────────────────────

_utoken_cache = None

def _app_key() -> str:
    key = os.environ.get("YOTPO_APP_KEY")
    if not key:
        sys.exit("YOTPO_APP_KEY not set. Run via: op run --env-file=.env.tpl -- python3 ...")
    return key

def _secret() -> str:
    secret = os.environ.get("YOTPO_SECRET_KEY")
    if not secret:
        sys.exit("YOTPO_SECRET_KEY not set. Run via: op run --env-file=.env.tpl -- python3 ...")
    return secret

def _utoken() -> str:
    """Generate and cache a uToken via OAuth."""
    global _utoken_cache
    if _utoken_cache:
        return _utoken_cache
    payload = json.dumps({
        "client_id": _app_key(),
        "client_secret": _secret(),
        "grant_type": "client_credentials",
    }).encode()
    req = urllib.request.Request(
        f"{API_BASE}/oauth/token",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    _utoken_cache = data["access_token"]
    return _utoken_cache


# ── HTTP helpers ───────────────────────────────────────────────────────────────

def _get(path: str, params: dict = None) -> dict:
    p = {"utoken": _utoken(), "app_key": _app_key(), **(params or {})}
    url = f"{API_BASE}/{path.lstrip('/')}?{urllib.parse.urlencode(p)}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())


# ── Review functions ───────────────────────────────────────────────────────────

def stats() -> dict:
    """Account-level review summary."""
    data = _get(f"v1/apps/{_app_key()}/reviews", {"count": 1, "page": 1})
    return data.get("response", {}).get("bottomline", data.get("response", {}))


def reviews(count: int = 100, page: int = 1, rating: int = None) -> list:
    """
    Fetch store reviews. Returns list of review dicts.
    rating: filter by star rating (1–5)
    """
    params = {"count": count, "page": page}
    if rating:
        params["score"] = rating
    data = _get(f"v1/apps/{_app_key()}/reviews", params)
    return data.get("response", {}).get("reviews", [])


def all_reviews() -> list:
    """Paginate through all reviews."""
    all_r, page = [], 1
    while True:
        batch = reviews(count=100, page=page)
        if not batch:
            break
        all_r.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return all_r


def ratings(product_ids: list[str] = None) -> list:
    """
    Per-product ratings from Yotpo bottomline.
    product_ids: list of Shopify product IDs (as strings). If None, uses store-level data.
    """
    if not product_ids:
        data = _get(f"products/{_app_key()}/yotpo_widget.json", {
            "widget_type": "bottomline"
        })
        return data.get("response", {}).get("bottomline", [])

    results = []
    for pid in product_ids:
        try:
            data = _get(f"products/{_app_key()}/{pid}/bottomline")
            bl = data.get("response", {}).get("bottomline", {})
            results.append({"product_id": pid, **bl})
        except Exception as e:
            results.append({"product_id": pid, "error": str(e)})
    return results


def pending() -> list:
    """Reviews awaiting moderation."""
    data = _get(f"v1/apps/{_app_key()}/reviews", {
        "count": 100,
        "status": "pending"
    })
    return data.get("response", {}).get("reviews", [])


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "audit"

    if cmd == "audit":
        print(f"\nYotpo Account Audit — #{ACCOUNT_ID}\n{'─'*60}")

        # Auth test
        token = _utoken()
        print(f"  Auth:       OK (uToken: {token[:12]}...)")

        # All reviews
        all_r = all_reviews()
        if all_r:
            scores = [r.get("score", 0) for r in all_r]
            avg = sum(scores) / len(scores)
            dist = {i: scores.count(i) for i in range(1, 6)}
            print(f"  Reviews:    {len(all_r)} total, {avg:.2f} avg rating")
            print(f"  Rating dist: " + "  ".join(f"{k}★:{v}" for k, v in sorted(dist.items(), reverse=True)))

            # Latest 5
            print(f"\nLatest reviews:\n{'─'*60}")
            for r in sorted(all_r, key=lambda x: x.get("created_at", ""), reverse=True)[:5]:
                date = r.get("created_at", "")[:10]
                score = "★" * r.get("score", 0)
                name = r.get("user", {}).get("display_name", "Anonymous")
                title = r.get("title", "")[:50]
                product = r.get("product_title", "")[:40]
                print(f"  {date}  {score:<5}  {name:<20}  {product:<40}  {title}")
        else:
            print("  Reviews:    none found")

        # Pending
        pend = pending()
        if pend:
            print(f"\n  ⚠️  {len(pend)} review(s) pending moderation")

    elif cmd == "reviews":
        for r in all_reviews():
            date = r.get("created_at", "")[:10]
            score = r.get("score", 0)
            name = r.get("user", {}).get("display_name", "Anonymous")
            body = (r.get("content") or "")[:80].replace("\n", " ")
            product = r.get("product_title", "")[:35]
            print(f"{date}  {'★'*score:<5}  {name:<20}  {product:<35}  {body}")

    elif cmd == "pending":
        pend = pending()
        print(f"\nPending reviews ({len(pend)}):\n{'─'*60}")
        for r in pend:
            print(f"  {r.get('created_at','')[:10]}  {'★'*r.get('score',0)}  {r.get('user',{}).get('display_name','')}  {r.get('title','')}")

    else:
        print("Usage: python3 scripts/yotpo.py [audit|reviews|pending]")
