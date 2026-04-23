#!/usr/bin/env python3
"""
Meta Ads placement breakdown — which placement wasted the money?

For each of the top N sales campaigns by spend, break out spend/clicks/
purchases by placement (Feed / Stories / Reels / Marketplace / Audience
Network / Messenger). This is the "is Audience Network eating your
budget" check.

Usage:
    cd ~/Claude/code-projects/lost-collective
    python3 shopify/scripts/meta_placement_breakdown.py
    # defaults: top 5 by spend, 540-day lookback

Env:
    META_ACCESS_TOKEN, META_AD_ACCOUNT_ID (direnv)
    META_TOP_N (default 5)
    META_LOOKBACK_DAYS (default 540)
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

API_VERSION = "v22.0"
TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
ACCOUNT_ID = os.environ.get("META_AD_ACCOUNT_ID", "")
TOP_N = int(os.environ.get("META_TOP_N", "5"))
LOOKBACK_DAYS = int(os.environ.get("META_LOOKBACK_DAYS", "540"))


def die(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def call(url):
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        die(f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:500]}")


def time_range_params():
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=LOOKBACK_DAYS)
    return json.dumps({"since": start.isoformat(), "until": end.isoformat()})


def get_top_campaigns():
    """Return top N campaigns by spend (sales-objective only)."""
    acct = ACCOUNT_ID if ACCOUNT_ID.startswith("act_") else f"act_{ACCOUNT_ID}"
    params = {
        "level": "campaign",
        "fields": "campaign_id,campaign_name,objective,spend",
        "time_range": time_range_params(),
        "limit": "500",
        "access_token": TOKEN,
    }
    url = f"https://graph.facebook.com/{API_VERSION}/{acct}/insights?{urllib.parse.urlencode(params)}"
    data = call(url).get("data", [])
    sales = [r for r in data if "SALES" in (r.get("objective", "").upper()) or "CONVERSIONS" in (r.get("objective", "").upper())]
    sales.sort(key=lambda r: float(r.get("spend", 0) or 0), reverse=True)
    return sales[:TOP_N]


def get_placement_breakdown(campaign_id):
    acct = ACCOUNT_ID if ACCOUNT_ID.startswith("act_") else f"act_{ACCOUNT_ID}"
    params = {
        "level": "campaign",
        "fields": "spend,impressions,clicks,ctr,cpc,actions",
        "filtering": json.dumps([{"field": "campaign.id", "operator": "EQUAL", "value": campaign_id}]),
        "breakdowns": "publisher_platform,platform_position",
        "time_range": time_range_params(),
        "limit": "500",
        "access_token": TOKEN,
    }
    url = f"https://graph.facebook.com/{API_VERSION}/{acct}/insights?{urllib.parse.urlencode(params)}"
    return call(url).get("data", [])


def count_purchases(actions):
    if not actions:
        return 0
    for a in actions:
        if a.get("action_type") == "omni_purchase":
            try:
                return int(float(a.get("value", "0")))
            except (ValueError, TypeError):
                pass
    for a in actions:
        if a.get("action_type") == "purchase":
            try:
                return int(float(a.get("value", "0")))
            except (ValueError, TypeError):
                pass
    return 0


def main():
    if not TOKEN or not ACCOUNT_ID:
        die("META_ACCESS_TOKEN and META_AD_ACCOUNT_ID required (direnv).")

    print(f"Pulling top {TOP_N} sales campaigns by spend ({LOOKBACK_DAYS}-day)...", file=sys.stderr)
    top = get_top_campaigns()
    if not top:
        die("No sales campaigns found in that window.")

    here = Path(__file__).resolve().parent
    docs = here.parent / "docs"
    docs.mkdir(exist_ok=True)
    date_tag = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = docs / f"meta-placement-breakdown-{date_tag}.md"

    lines = [
        f"# Meta Ads placement breakdown — top {TOP_N} sales campaigns",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · lookback {LOOKBACK_DAYS}d",
        "",
        "**What this tells you:** whether cheap clicks came from low-quality placements",
        "(Audience Network, in-feed Reels) vs high-intent placements (Feed, Stories).",
        "If >50% of spend on a campaign went to Audience Network, that's the problem.",
        "",
    ]

    for campaign in top:
        name = campaign.get("campaign_name", "?")
        cid = campaign.get("campaign_id", "?")
        total_spend = float(campaign.get("spend", 0) or 0)
        print(f"  {name} (${total_spend:,.2f})...", file=sys.stderr)
        breakdown = get_placement_breakdown(cid)

        lines.append(f"## {name}")
        lines.append("")
        lines.append(f"Campaign ID: `{cid}` · Total spend: **${total_spend:,.2f}**")
        lines.append("")

        if not breakdown:
            lines.append("_No breakdown data available._")
            lines.append("")
            continue

        # Aggregate by placement
        rows = []
        for r in breakdown:
            placement = f"{r.get('publisher_platform', '?')} / {r.get('platform_position', '?')}"
            spend = float(r.get("spend", 0) or 0)
            pct = (spend / total_spend * 100) if total_spend > 0 else 0
            rows.append({
                "placement": placement,
                "spend": spend,
                "pct": pct,
                "impressions": int(r.get("impressions", 0) or 0),
                "clicks": int(r.get("clicks", 0) or 0),
                "ctr": r.get("ctr", ""),
                "cpc": r.get("cpc", ""),
                "purchases": count_purchases(r.get("actions")),
            })
        rows.sort(key=lambda r: r["spend"], reverse=True)

        lines.append("| Placement | Spend | % of total | Impr | Clicks | CTR | CPC | Purchases |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for r in rows:
            lines.append(
                f"| {r['placement']} "
                f"| ${r['spend']:,.2f} "
                f"| {r['pct']:.1f}% "
                f"| {r['impressions']:,} "
                f"| {r['clicks']:,} "
                f"| {r['ctr']} "
                f"| {r['cpc']} "
                f"| {r['purchases']} |"
            )
        lines.append("")

        # Callout for audience network dominance
        an_spend = sum(r["spend"] for r in rows if "audience_network" in r["placement"].lower())
        if an_spend / total_spend > 0.3 if total_spend > 0 else False:
            lines.append(
                f"**⚠ {an_spend/total_spend*100:.0f}% of this campaign's spend went to Audience Network.** "
                "Audience Network is a classic low-quality placement for e-commerce — cheap clicks, "
                "poor intent. Exclude it in future campaigns via `excluded_publisher_platforms`."
            )
            lines.append("")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✓ Wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
