#!/usr/bin/env python3
"""
Meta Ads retrospective — per-campaign spend, conversions, ROAS.

Answers the "spent a lot, sold nothing — where exactly?" question without
waiting on Adspirer's backend sync. Hits the Meta Graph API directly
using the already-loaded META_ACCESS_TOKEN env var (via direnv).

Usage:
    cd ~/Claude/code-projects/lost-collective
    python3 shopify/scripts/meta_campaign_insights.py
    # or with a custom window:
    META_LOOKBACK_DAYS=180 python3 shopify/scripts/meta_campaign_insights.py

Outputs (written to shopify/docs/):
    meta-insights-<YYYY-MM-DD>.csv   - all raw fields per campaign
    meta-insights-<YYYY-MM-DD>.md    - scannable summary with wasted-spend callout

No external deps. urllib only.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_VERSION = "v22.0"
TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
ACCOUNT_ID = os.environ.get("META_AD_ACCOUNT_ID", "")
LOOKBACK_DAYS = int(os.environ.get("META_LOOKBACK_DAYS", "90"))

# Wasted-spend thresholds (sales campaigns only)
WASTED_SPEND_MIN = 10.0  # below this, not worth flagging
ROAS_BREAKEVEN = 1.0


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def fetch_insights(account_id: str, token: str, lookback_days: int) -> list[dict]:
    """Pull campaign-level insights. Handles pagination."""
    if account_id.startswith("act_"):
        acct = account_id
    else:
        acct = f"act_{account_id}"

    date_preset_map = {7: "last_7d", 14: "last_14d", 30: "last_30d", 90: "last_90d"}
    params: dict[str, str] = {
        "level": "campaign",
        "fields": ",".join([
            "campaign_id",
            "campaign_name",
            "objective",
            "spend",
            "impressions",
            "clicks",
            "reach",
            "frequency",
            "cpm",
            "cpc",
            "ctr",
            "actions",
            "action_values",
            "purchase_roas",
            "date_start",
            "date_stop",
        ]),
        "limit": "500",
        "access_token": token,
    }
    if lookback_days in date_preset_map:
        params["date_preset"] = date_preset_map[lookback_days]
    else:
        # Custom window: compute from today
        from datetime import timedelta
        end = datetime.now(timezone.utc).date()
        start = end - timedelta(days=lookback_days)
        params["time_range"] = json.dumps({"since": start.isoformat(), "until": end.isoformat()})

    url = f"https://graph.facebook.com/{API_VERSION}/{acct}/insights?{urllib.parse.urlencode(params)}"
    rows: list[dict] = []
    while url:
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                payload = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            die(f"HTTP {e.code} from Meta: {err_body[:500]}")
        except Exception as e:
            die(f"Request failed: {e}")

        rows.extend(payload.get("data", []))
        paging = payload.get("paging", {})
        url = paging.get("next")

    return rows


def extract_purchase_count(actions: list | None) -> int:
    if not actions:
        return 0
    total = 0
    # Prefer "omni_purchase" (covers web + offline + app); fall back to "purchase"
    for a in actions:
        if a.get("action_type") == "omni_purchase":
            try:
                total += int(float(a.get("value", "0")))
            except (ValueError, TypeError):
                pass
    if total > 0:
        return total
    for a in actions:
        if a.get("action_type") == "purchase":
            try:
                total += int(float(a.get("value", "0")))
            except (ValueError, TypeError):
                pass
    return total


def extract_purchase_value(action_values: list | None) -> float:
    if not action_values:
        return 0.0
    for a in action_values:
        if a.get("action_type") == "omni_purchase":
            try:
                return float(a.get("value", "0"))
            except (ValueError, TypeError):
                return 0.0
    for a in action_values:
        if a.get("action_type") == "purchase":
            try:
                return float(a.get("value", "0"))
            except (ValueError, TypeError):
                return 0.0
    return 0.0


def classify(row: dict) -> str:
    """Simple verdict for SALES campaigns; 'n/a' for non-sales objectives."""
    obj = (row.get("objective") or "").upper()
    spend = float(row.get("spend", 0) or 0)
    purchases = row.get("_purchases", 0)
    roas_raw = row.get("purchase_roas")
    roas = 0.0
    if roas_raw:
        try:
            roas = float(roas_raw[0].get("value", 0)) if isinstance(roas_raw, list) else float(roas_raw)
        except (ValueError, TypeError, IndexError):
            roas = 0.0

    is_sales = "SALES" in obj or "CONVERSIONS" in obj

    if not is_sales:
        return "n/a (not a sales objective)"
    if spend < WASTED_SPEND_MIN and purchases == 0:
        return "negligible spend"
    if purchases == 0:
        return "WASTED (no purchases)"
    if roas < ROAS_BREAKEVEN:
        return f"loss (ROAS {roas:.2f})"
    if roas < 2.0:
        return f"breakeven (ROAS {roas:.2f})"
    return f"profitable (ROAS {roas:.2f})"


def main() -> None:
    if not TOKEN:
        die("META_ACCESS_TOKEN not set. Run from ~/Claude/code-projects/lost-collective (direnv).")
    if not ACCOUNT_ID:
        die("META_AD_ACCOUNT_ID not set.")

    print(f"Fetching {LOOKBACK_DAYS}-day insights for act_{ACCOUNT_ID.lstrip('act_')}...", file=sys.stderr)
    raw = fetch_insights(ACCOUNT_ID, TOKEN, LOOKBACK_DAYS)
    if not raw:
        print("No campaign data returned.", file=sys.stderr)
        return

    # Enrich rows with parsed purchase data
    enriched: list[dict] = []
    for row in raw:
        row["_purchases"] = extract_purchase_count(row.get("actions"))
        row["_purchase_value"] = extract_purchase_value(row.get("action_values"))
        row["_verdict"] = classify(row)
        enriched.append(row)

    # Sort by spend descending
    enriched.sort(key=lambda r: float(r.get("spend", 0) or 0), reverse=True)

    # Totals
    total_spend = sum(float(r.get("spend", 0) or 0) for r in enriched)
    total_purchases = sum(r.get("_purchases", 0) for r in enriched)
    total_purchase_value = sum(r.get("_purchase_value", 0) for r in enriched)
    total_impressions = sum(int(r.get("impressions", 0) or 0) for r in enriched)
    total_clicks = sum(int(r.get("clicks", 0) or 0) for r in enriched)
    acct_roas = (total_purchase_value / total_spend) if total_spend > 0 else 0.0

    # Output paths
    here = Path(__file__).resolve().parent
    docs_dir = here.parent / "docs"
    docs_dir.mkdir(exist_ok=True)
    date_tag = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    csv_path = docs_dir / f"meta-insights-{date_tag}.csv"
    md_path = docs_dir / f"meta-insights-{date_tag}.md"

    # CSV — raw fields per campaign
    csv_fields = [
        "campaign_name", "campaign_id", "objective",
        "spend", "impressions", "clicks", "reach", "frequency",
        "cpm", "cpc", "ctr",
        "purchases", "purchase_value", "roas", "verdict",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=csv_fields)
        w.writeheader()
        for r in enriched:
            roas_raw = r.get("purchase_roas")
            roas_val = ""
            if roas_raw:
                try:
                    roas_val = f"{float(roas_raw[0].get('value', 0)):.2f}" if isinstance(roas_raw, list) else f"{float(roas_raw):.2f}"
                except (ValueError, TypeError, IndexError):
                    pass
            w.writerow({
                "campaign_name": r.get("campaign_name", ""),
                "campaign_id": r.get("campaign_id", ""),
                "objective": r.get("objective", ""),
                "spend": f"{float(r.get('spend', 0) or 0):.2f}",
                "impressions": r.get("impressions", ""),
                "clicks": r.get("clicks", ""),
                "reach": r.get("reach", ""),
                "frequency": r.get("frequency", ""),
                "cpm": r.get("cpm", ""),
                "cpc": r.get("cpc", ""),
                "ctr": r.get("ctr", ""),
                "purchases": r.get("_purchases", 0),
                "purchase_value": f"{r.get('_purchase_value', 0):.2f}",
                "roas": roas_val,
                "verdict": r.get("_verdict", ""),
            })

    # Markdown summary
    wasted = [r for r in enriched if r.get("_verdict", "").startswith("WASTED")]
    losses = [r for r in enriched if r.get("_verdict", "").startswith("loss")]
    profitable = [r for r in enriched if r.get("_verdict", "").startswith("profitable")]
    wasted_spend_total = sum(float(r.get("spend", 0) or 0) for r in wasted)

    lines = []
    lines.append(f"# Meta Ads retrospective — last {LOOKBACK_DAYS} days")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"Account: act_{ACCOUNT_ID.lstrip('act_')}")
    lines.append("")
    lines.append("## Account totals")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Total spend | ${total_spend:,.2f} |")
    lines.append(f"| Total impressions | {total_impressions:,} |")
    lines.append(f"| Total clicks | {total_clicks:,} |")
    lines.append(f"| Total purchases | {total_purchases:,} |")
    lines.append(f"| Total purchase value | ${total_purchase_value:,.2f} |")
    lines.append(f"| Account ROAS | {acct_roas:.2f} |")
    lines.append("")

    if wasted:
        lines.append("## Wasted spend (sales campaigns with zero purchases)")
        lines.append("")
        lines.append(f"**${wasted_spend_total:,.2f} across {len(wasted)} campaigns — this is the \"spent a lot, sold nothing\" bucket.**")
        lines.append("")
        lines.append("| Campaign | Objective | Spend | Impressions | Clicks | CTR | CPC |")
        lines.append("|---|---|---|---|---|---|---|")
        for r in wasted:
            lines.append(
                f"| {r.get('campaign_name', '')[:60]} "
                f"| {r.get('objective', '')} "
                f"| ${float(r.get('spend', 0) or 0):,.2f} "
                f"| {r.get('impressions', '')} "
                f"| {r.get('clicks', '')} "
                f"| {r.get('ctr', '')} "
                f"| {r.get('cpc', '')} |"
            )
        lines.append("")

    if losses:
        lines.append("## Negative ROAS (sold but didn't break even)")
        lines.append("")
        lines.append("| Campaign | Spend | Purchases | Value | ROAS |")
        lines.append("|---|---|---|---|---|")
        for r in losses:
            val = r.get("_purchase_value", 0)
            spend = float(r.get("spend", 0) or 0)
            roas = (val / spend) if spend > 0 else 0
            lines.append(
                f"| {r.get('campaign_name', '')[:60]} "
                f"| ${spend:,.2f} "
                f"| {r.get('_purchases', 0)} "
                f"| ${val:,.2f} "
                f"| {roas:.2f} |"
            )
        lines.append("")

    if profitable:
        lines.append("## Profitable (ROAS ≥ 2.0)")
        lines.append("")
        lines.append("| Campaign | Spend | Purchases | Value | ROAS |")
        lines.append("|---|---|---|---|---|")
        for r in profitable:
            val = r.get("_purchase_value", 0)
            spend = float(r.get("spend", 0) or 0)
            roas = (val / spend) if spend > 0 else 0
            lines.append(
                f"| {r.get('campaign_name', '')[:60]} "
                f"| ${spend:,.2f} "
                f"| {r.get('_purchases', 0)} "
                f"| ${val:,.2f} "
                f"| {roas:.2f} |"
            )
        lines.append("")

    lines.append("## All campaigns (sorted by spend)")
    lines.append("")
    lines.append("| Campaign | Objective | Spend | Purchases | ROAS | Verdict |")
    lines.append("|---|---|---|---|---|---|")
    for r in enriched:
        roas_raw = r.get("purchase_roas")
        roas_val = "—"
        if roas_raw:
            try:
                roas_val = f"{float(roas_raw[0].get('value', 0)):.2f}" if isinstance(roas_raw, list) else f"{float(roas_raw):.2f}"
            except (ValueError, TypeError, IndexError):
                pass
        lines.append(
            f"| {r.get('campaign_name', '')[:60]} "
            f"| {r.get('objective', '')} "
            f"| ${float(r.get('spend', 0) or 0):,.2f} "
            f"| {r.get('_purchases', 0)} "
            f"| {roas_val} "
            f"| {r.get('_verdict', '')} |"
        )

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"✓ CSV:      {csv_path}", file=sys.stderr)
    print(f"✓ Markdown: {md_path}", file=sys.stderr)
    print("", file=sys.stderr)
    print(f"Account ROAS: {acct_roas:.2f}  |  Total spend: ${total_spend:,.2f}  |  Total purchases: {total_purchases}", file=sys.stderr)
    if wasted:
        print(f"Wasted spend: ${wasted_spend_total:,.2f} across {len(wasted)} campaigns", file=sys.stderr)


if __name__ == "__main__":
    main()
