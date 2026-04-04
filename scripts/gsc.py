"""
Google Search Console integration — Lost Collective
Property: https://lostcollective.com/

Credentials: 1Password → "Lost Collective — Google Search Console" (document)
No .env.tpl entry needed — reads directly from 1Password at runtime.

Run: python3 scripts/gsc.py
Requires: pip install google-auth requests   (one-time)

Key operations:
  performance()     — clicks/impressions/position by page or query
  index_coverage()  — indexed vs non-indexed URL breakdown
  inspect_url()     — detailed indexing status for a single URL
  sitemaps()        — list submitted sitemaps and their stats
"""

import json, subprocess, sys
from datetime import date, timedelta

# ── Auth ───────────────────────────────────────────────────────────────────────

PROPERTY = "https://lostcollective.com/"
SCOPES   = ["https://www.googleapis.com/auth/webmasters.readonly"]


def _credentials():
    """Load service account credentials from 1Password."""
    try:
        from google.oauth2 import service_account
    except ImportError:
        sys.exit("Missing dependency. Run: pip install google-auth requests")

    raw = subprocess.run(
        ["op", "document", "get", "Lost Collective — Google Search Console"],
        capture_output=True, text=True, check=True
    ).stdout

    info = json.loads(raw)
    return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)


def _get(url: str, params: dict = None) -> dict:
    """Authenticated GET against the Search Console API."""
    import requests
    from google.auth.transport.requests import Request as GoogleRequest

    creds = _credentials()
    creds.refresh(GoogleRequest())

    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {creds.token}"},
        params=params or {},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _post(url: str, body: dict) -> dict:
    """Authenticated POST against the Search Console API."""
    import requests
    from google.auth.transport.requests import Request as GoogleRequest

    creds = _credentials()
    creds.refresh(GoogleRequest())

    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {creds.token}",
            "Content-Type":  "application/json",
        },
        json=body,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# ── Performance ────────────────────────────────────────────────────────────────

def performance(
    days: int = 28,
    dimension: str = "page",       # "page" | "query" | "country" | "device"
    start_date: str = None,
    end_date: str = None,
    row_limit: int = 50,
    filter_page: str = None,       # restrict to URLs containing this string
    filter_query: str = None,      # restrict to queries containing this string
) -> list[dict]:
    """
    Return search performance rows sorted by clicks desc.

    dimension examples:
      "page"    → top landing pages
      "query"   → top search queries
      "country" → breakdown by country
      "device"  → desktop / mobile / tablet
    """
    end   = end_date   or str(date.today() - timedelta(days=3))  # GSC lags ~3 days
    start = start_date or str(date.today() - timedelta(days=days + 3))

    body = {
        "startDate":       start,
        "endDate":         end,
        "dimensions":      [dimension],
        "rowLimit":        row_limit,
        "dataState":       "final",
    }

    if filter_page or filter_query:
        body["dimensionFilterGroups"] = [{"filters": []}]
        if filter_page:
            body["dimensionFilterGroups"][0]["filters"].append({
                "dimension": "page", "operator": "contains", "expression": filter_page
            })
        if filter_query:
            body["dimensionFilterGroups"][0]["filters"].append({
                "dimension": "query", "operator": "contains", "expression": filter_query
            })

    url  = f"https://searchconsole.googleapis.com/webmasters/v3/sites/{_enc(PROPERTY)}/searchAnalytics/query"
    data = _post(url, body)
    return data.get("rows", [])


# ── Index coverage ─────────────────────────────────────────────────────────────

def index_coverage() -> dict:
    """
    Return URL counts by index status.
    Note: the URL Inspection API is per-URL; coverage totals come from the
    Search Console UI. This returns sitemaps as a proxy for indexed content.
    """
    return sitemaps()


def sitemaps() -> list[dict]:
    """List all submitted sitemaps and their stats."""
    url  = f"https://searchconsole.googleapis.com/webmasters/v3/sites/{_enc(PROPERTY)}/sitemaps"
    data = _get(url)
    return data.get("sitemap", [])


# ── URL inspection ─────────────────────────────────────────────────────────────

def inspect_url(page_url: str) -> dict:
    """
    Inspect a single URL — returns index status, coverage state,
    canonical URL, last crawl time, and any issues.
    """
    body = {
        "inspectionUrl": page_url,
        "siteUrl":       PROPERTY,
    }
    url  = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
    data = _post(url, body)
    return data.get("inspectionResult", data)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _enc(s: str) -> str:
    """URL-encode a string for use in API paths."""
    import urllib.parse
    return urllib.parse.quote(s, safe="")


def top_pages(days: int = 28, n: int = 20) -> None:
    """Print top N pages by clicks."""
    rows = performance(days=days, dimension="page", row_limit=n)
    print(f"\nTop {n} pages — last {days} days\n{'─'*70}")
    print(f"  {'Clicks':>7}  {'Impr':>7}  {'CTR':>6}  {'Pos':>5}  URL")
    for r in rows:
        url = r["keys"][0].replace(PROPERTY.rstrip("/"), "")
        print(f"  {r['clicks']:>7.0f}  {r['impressions']:>7.0f}  "
              f"{r['ctr']*100:>5.1f}%  {r['position']:>5.1f}  {url}")


def top_queries(days: int = 28, n: int = 20) -> None:
    """Print top N queries by clicks."""
    rows = performance(days=days, dimension="query", row_limit=n)
    print(f"\nTop {n} queries — last {days} days\n{'─'*70}")
    print(f"  {'Clicks':>7}  {'Impr':>7}  {'CTR':>6}  {'Pos':>5}  Query")
    for r in rows:
        print(f"  {r['clicks']:>7.0f}  {r['impressions']:>7.0f}  "
              f"{r['ctr']*100:>5.1f}%  {r['position']:>5.1f}  {r['keys'][0]}")


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Google Search Console — {PROPERTY}\n")

    print("Sitemaps:")
    for sm in sitemaps():
        path     = sm.get("path", "")
        warnings = sm.get("warnings", 0)
        errors   = sm.get("errors", 0)
        print(f"  {path}  warnings:{warnings}  errors:{errors}")

    top_pages(days=28, n=15)
    top_queries(days=28, n=15)
