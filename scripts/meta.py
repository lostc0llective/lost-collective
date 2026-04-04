"""
Meta Graph API — Lost Collective
Business ID:  1691557587748276
Live Pixel:   1564860757158131
Ad Account:   act_2044897662414265

Credentials: 1Password → "Lost Collective — Meta" (item)
Run: op run --env-file=.env.tpl -- python3 scripts/meta.py

Key operations:
  pixel_health()      — event counts by type for last N days
  pixel_stats()       — detailed pixel firing stats
  delete_pixel(id)    — permanently delete a pixel
  list_pixels()       — all pixels in the business account
  ad_account_info()   — ad account health + spend summary
"""

import json, os, sys, time
from datetime import datetime, timedelta

# ── Config ─────────────────────────────────────────────────────────────────────

BUSINESS_ID  = "1691557587748276"
PIXEL_ID     = "1564860757158131"
AD_ACCOUNT   = "act_2044897662414265"
GRAPH_API    = "https://graph.facebook.com/v19.0"

DEAD_PIXELS  = [
    {"id": "612487612232461",  "name": "Default Pixel",                    "days_dead": 1686},
    {"id": "865983057246902",  "name": "Ads Pixel for Shopify Facebook",   "days_dead": 66},
]

# ── Auth ───────────────────────────────────────────────────────────────────────

def _token() -> str:
    token = os.environ.get("META_ACCESS_TOKEN")
    if not token:
        sys.exit("META_ACCESS_TOKEN not set. Add to .env.tpl and run via op run.")
    return token


def _get(path: str, params: dict = None) -> dict:
    import urllib.request, urllib.parse
    p = {"access_token": _token(), **(params or {})}
    url = f"{GRAPH_API}/{path.lstrip('/')}?{urllib.parse.urlencode(p)}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())


def _delete(path: str) -> dict:
    import urllib.request
    req = urllib.request.Request(
        f"{GRAPH_API}/{path.lstrip('/')}?access_token={_token()}",
        method="DELETE"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


# ── Pixel functions ────────────────────────────────────────────────────────────

def pixel_health(pixel_id: str = PIXEL_ID, days: int = 7) -> dict:
    """Event counts by type for the last N days, aggregated across all hours."""
    end_time   = int(time.time())
    start_time = end_time - (days * 86400)
    raw = _get(f"{pixel_id}/stats", {
        "start_time": start_time,
        "end_time":   end_time,
        "aggregation": "event",
    })
    # Flatten hourly buckets into totals by event name
    totals = {}
    for bucket in raw.get("data", []):
        for item in bucket.get("data", []):
            event = item.get("value", "unknown")
            totals[event] = totals.get(event, 0) + item.get("count", 0)
    return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))


def pixel_stats(pixel_id: str = PIXEL_ID) -> dict:
    """Pixel metadata — name, last fired, availability."""
    return _get(pixel_id, {
        "fields": "id,name,last_fired_time,is_unavailable,owner_business"
    })


def list_pixels() -> list:
    """All pixels under the business account."""
    data = _get(f"{BUSINESS_ID}/owned_pixels", {
        "fields": "id,name,last_fired_time,is_unavailable"
    })
    return data.get("data", [])


def delete_pixel(pixel_id: str, dry_run: bool = True) -> dict:
    """
    Permanently delete a pixel. Use dry_run=False to actually delete.
    Always confirm the pixel ID before setting dry_run=False.
    """
    if dry_run:
        print(f"[DRY RUN] Would delete pixel {pixel_id}. Pass dry_run=False to confirm.")
        return {"dry_run": True, "pixel_id": pixel_id}
    return _delete(pixel_id)


def delete_dead_pixels(dry_run: bool = True) -> None:
    """Delete the two confirmed dead pixels."""
    for p in DEAD_PIXELS:
        print(f"\nPixel: {p['name']} (ID: {p['id']}) — dead {p['days_dead']} days")
        result = delete_pixel(p["id"], dry_run=dry_run)
        print(f"  Result: {result}")


# ── Ad account ─────────────────────────────────────────────────────────────────

def ad_account_info() -> dict:
    """Ad account health, currency, spend cap."""
    return _get(AD_ACCOUNT, {
        "fields": "id,name,account_status,currency,spend_cap,balance,amount_spent"
    })


def campaign_performance(since: str = "2024-01-01", until: str = None) -> list:
    """Campaign-level spend, impressions, clicks, CTR, ROAS."""
    import json
    from datetime import date
    until = until or str(date.today())
    data = _get(f"{AD_ACCOUNT}/insights", {
        "fields": "campaign_name,spend,impressions,clicks,ctr,purchase_roas,actions",
        "time_range": json.dumps({"since": since, "until": until}),
        "level": "campaign",
        "limit": 50,
    })
    return data.get("data", [])


def catalog_status(catalog_id: str = "555359988464958") -> dict:
    """Product catalog health — product count and feed status."""
    info = _get(catalog_id, {"fields": "id,name,product_count,vertical"})
    feeds = _get(f"{catalog_id}/product_feeds", {"fields": "id,name,product_count"})
    return {"catalog": info, "feeds": feeds.get("data", [])}


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "health"

    if cmd == "health":
        print(f"\nPixel health — last 7 days (pixel {PIXEL_ID})\n{'─'*50}")
        info = pixel_stats()
        print(f"  Name:       {info.get('name')}")
        print(f"  Last fired: {info.get('last_fired_time')}")
        print(f"  Available:  {'Yes' if not info.get('is_unavailable') else 'NO — unavailable'}\n")
        totals = pixel_health(days=7)
        for event, count in totals.items():
            print(f"  {event:<25} {count:>8,} events")

    elif cmd == "pixels":
        print(f"\nAll pixels — business {BUSINESS_ID}\n{'─'*60}")
        for p in list_pixels():
            fired = p.get("last_fired_time", "never")
            unavail = "⚠️ unavailable" if p.get("is_unavailable") else "✅"
            print(f"  {unavail}  {p['id']}  {p.get('name', 'Unnamed'):<35}  last: {fired}")

    elif cmd == "delete-dead":
        dry = "--confirm" not in sys.argv
        if dry:
            print("DRY RUN — pass --confirm to actually delete")
        delete_dead_pixels(dry_run=dry)

    elif cmd == "account":
        info = ad_account_info()
        print(f"\nAd account: {info.get('name')}")
        print(f"  Status:   {info.get('account_status')}")
        print(f"  Currency: {info.get('currency')}")
        print(f"  Spent:    {info.get('amount_spent')}")

    elif cmd == "campaigns":
        rows = campaign_performance()
        total_spend = sum(float(r.get("spend", 0)) for r in rows)
        print(f"\nCampaign performance — all time\n{'─'*80}")
        print(f"  {'Campaign':<50}  {'Spend':>8}  {'CTR':>7}  {'ROAS':>6}")
        for r in sorted(rows, key=lambda x: float(x.get("spend", 0)), reverse=True):
            roas = r.get("purchase_roas", [{}])
            roas_val = roas[0].get("value", "—") if roas else "—"
            ctr = f"{float(r.get('ctr', 0)):.1f}%"
            name = r["campaign_name"][:50]
            print(f"  {name:<50}  ${float(r.get('spend', 0)):>7.2f}  {ctr:>7}  {roas_val:>6}")
        print(f"\n  Total spend: ${total_spend:,.2f}")

    elif cmd == "catalog":
        status = catalog_status()
        c = status["catalog"]
        print(f"\nProduct catalog: {c.get('name')}")
        print(f"  Products: {c.get('product_count'):,}")
        print(f"  Vertical: {c.get('vertical')}")
        feeds = status["feeds"]
        print(f"  Feeds: {len(feeds)} ({'native Shopify sync' if not feeds else ', '.join(f['name'] for f in feeds)})")

    else:
        print("Usage: python3 scripts/meta.py [health|pixels|delete-dead|account|campaigns|catalog]")
