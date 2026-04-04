"""
Google Analytics 4 Data API — Lost Collective
Property: 325530752 (lostcollective.com)

Credentials: 1Password → "Lost Collective — Google Search Console" (document)
Same service account as GSC — no separate credential needed.

One-time setup:
  1. pip install google-analytics-data google-auth
  2. GA4 Admin → Property access management → Add user:
     claude-code-lost-collective@lost-collective-492307.iam.gserviceaccount.com
     Role: Viewer

Run: python3 scripts/ga4.py

Key operations:
  sessions()            — sessions/users by channel for last N days
  conversions()         — purchase events, revenue, transaction count
  revenue_by_product()  — revenue + quantity sold per product
  channel_attribution() — channel breakdown (organic, email, direct, etc.)
  top_pages()           — pageviews by landing page
  device_breakdown()    — desktop / mobile / tablet split
"""

import json, subprocess, sys
from datetime import date, timedelta

# ── Config ─────────────────────────────────────────────────────────────────────

PROPERTY_ID = "325530752"
PROPERTY    = f"properties/{PROPERTY_ID}"

# ── Auth ───────────────────────────────────────────────────────────────────────

def _client():
    """Return an authenticated GA4 BetaAnalyticsDataClient."""
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.oauth2 import service_account
    except ImportError:
        sys.exit("Missing dependency. Run: pip install google-analytics-data google-auth")

    raw = subprocess.run(
        ["op", "document", "get", "Lost Collective — Google Search Console"],
        capture_output=True, text=True, check=True
    ).stdout

    info  = json.loads(raw)
    creds = service_account.Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
    return BetaAnalyticsDataClient(credentials=creds)


def _run_report(dimensions: list, metrics: list, days: int = 28,
                order_by_metric: str = None, limit: int = 50) -> list[dict]:
    """Run a GA4 report and return rows as list of dicts."""
    from google.analytics.data_v1beta.types import (
        RunReportRequest, DateRange, Dimension, Metric, OrderBy
    )

    end   = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)

    request = RunReportRequest(
        property=PROPERTY,
        date_ranges=[DateRange(start_date=str(start), end_date=str(end))],
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        limit=limit,
    )

    if order_by_metric:
        request.order_bys = [
            OrderBy(metric=OrderBy.MetricOrderBy(metric_name=order_by_metric), desc=True)
        ]

    response = _client().run_report(request)

    rows = []
    for row in response.rows:
        record = {}
        for i, dim in enumerate(dimensions):
            record[dim] = row.dimension_values[i].value
        for i, met in enumerate(metrics):
            val = row.metric_values[i].value
            try:
                record[met] = float(val) if "." in val else int(val)
            except (ValueError, TypeError):
                record[met] = val
        rows.append(record)

    return rows


# ── Core functions ─────────────────────────────────────────────────────────────

def sessions(days: int = 28) -> list[dict]:
    """Sessions and users by default channel group."""
    return _run_report(
        dimensions=["sessionDefaultChannelGroup"],
        metrics=["sessions", "totalUsers", "bounceRate", "averageSessionDuration"],
        days=days,
        order_by_metric="sessions",
    )


def conversions(days: int = 28) -> list[dict]:
    """Purchase events — transactions, revenue, conversion rate."""
    return _run_report(
        dimensions=["date"],
        metrics=["transactions", "purchaseRevenue", "sessionConversionRate"],
        days=days,
        order_by_metric="purchaseRevenue",
        limit=days,
    )


def revenue_by_product(days: int = 28, n: int = 25) -> list[dict]:
    """Revenue and units sold per product."""
    return _run_report(
        dimensions=["itemName"],
        metrics=["itemRevenue", "itemsPurchased", "itemsViewed", "itemsAddedToCart"],
        days=days,
        order_by_metric="itemRevenue",
        limit=n,
    )


def channel_attribution(days: int = 28) -> list[dict]:
    """Revenue and transactions broken down by acquisition channel."""
    return _run_report(
        dimensions=["sessionDefaultChannelGroup"],
        metrics=["transactions", "purchaseRevenue", "sessions"],
        days=days,
        order_by_metric="purchaseRevenue",
    )


def top_pages(days: int = 28, n: int = 20) -> list[dict]:
    """Top landing pages by sessions."""
    return _run_report(
        dimensions=["landingPage"],
        metrics=["sessions", "totalUsers", "bounceRate"],
        days=days,
        order_by_metric="sessions",
        limit=n,
    )


def device_breakdown(days: int = 28) -> list[dict]:
    """Sessions split by device category."""
    return _run_report(
        dimensions=["deviceCategory"],
        metrics=["sessions", "totalUsers", "transactions", "purchaseRevenue"],
        days=days,
        order_by_metric="sessions",
    )


# ── CLI ────────────────────────────────────────────────────────────────────────

def _fmt_currency(v) -> str:
    try:
        return f"${float(v):,.2f}"
    except (ValueError, TypeError):
        return str(v)


def _fmt_pct(v) -> str:
    try:
        return f"{float(v)*100:.1f}%"
    except (ValueError, TypeError):
        return str(v)


if __name__ == "__main__":
    print(f"Google Analytics 4 — Lost Collective (property {PROPERTY_ID})\n")

    # Sessions by channel
    rows = sessions(days=28)
    print(f"Sessions by channel — last 28 days\n{'─'*65}")
    print(f"  {'Channel':<30}  {'Sessions':>8}  {'Users':>7}  {'Bounce':>7}")
    for r in rows:
        print(f"  {r['sessionDefaultChannelGroup']:<30}  "
              f"{r['sessions']:>8,}  {r['totalUsers']:>7,}  "
              f"{_fmt_pct(r['bounceRate']):>7}")

    # Revenue by channel
    print(f"\nRevenue by channel — last 28 days\n{'─'*65}")
    rows = channel_attribution(days=28)
    print(f"  {'Channel':<30}  {'Revenue':>10}  {'Orders':>7}")
    for r in rows:
        print(f"  {r['sessionDefaultChannelGroup']:<30}  "
              f"{_fmt_currency(r['purchaseRevenue']):>10}  {r['transactions']:>7,}")

    # Top products
    print(f"\nTop 15 products by revenue — last 28 days\n{'─'*65}")
    rows = revenue_by_product(days=28, n=15)
    print(f"  {'Product':<40}  {'Revenue':>10}  {'Units':>6}")
    for r in rows:
        name = r["itemName"][:40]
        print(f"  {name:<40}  "
              f"{_fmt_currency(r['itemRevenue']):>10}  {r['itemsPurchased']:>6,}")

    # Device split
    print(f"\nDevice breakdown — last 28 days\n{'─'*65}")
    rows = device_breakdown(days=28)
    print(f"  {'Device':<15}  {'Sessions':>8}  {'Revenue':>10}  {'Orders':>7}")
    for r in rows:
        print(f"  {r['deviceCategory']:<15}  {r['sessions']:>8,}  "
              f"{_fmt_currency(r['purchaseRevenue']):>10}  {r['transactions']:>7,}")
