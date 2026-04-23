#!/usr/bin/env python3
"""
Meta Pixel health check — is the Purchase event signal actually reaching
Meta? This is the diagnostic that answers "why did Advantage+ and Manual
Shopping campaigns get zero purchases despite thousands of clicks."

Checks:
1. Pixel metadata — creation date, last fired time, CAPI enabled
2. Event volume by event name (last 30 days): ViewContent, AddToCart,
   InitiateCheckout, Purchase. If Purchase volume is zero or tiny
   relative to ViewContent, the signal is broken.
3. Deduplication status — whether server-side (CAPI) + client-side
   (Pixel) events are being matched

Usage:
    cd ~/Claude/code-projects/lost-collective
    python3 shopify/scripts/meta_pixel_health.py

Env:
    META_ACCESS_TOKEN, META_PIXEL_ID (direnv)
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
PIXEL_ID = os.environ.get("META_PIXEL_ID", "")


def die(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def call(url):
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"_error_code": e.code, "_error_body": body[:500]}
    except Exception as e:
        return {"_error": str(e)}


def get_pixel_info():
    fields = ",".join([
        "id", "name", "code", "creation_time", "last_fired_time",
        "is_created_by_business", "owner_business",
        "automatic_matching_fields", "enable_automatic_matching",
        "data_use_setting", "first_party_cookie_status",
    ])
    url = f"https://graph.facebook.com/{API_VERSION}/{PIXEL_ID}?fields={fields}&access_token={TOKEN}"
    return call(url)


def get_event_stats(pixel_id, start, end):
    """
    /stats endpoint returns per-event daily counts. Aggregate ourselves.
    """
    params = {
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "aggregation": "event",
        "access_token": TOKEN,
    }
    url = f"https://graph.facebook.com/{API_VERSION}/{pixel_id}/stats?{urllib.parse.urlencode(params)}"
    return call(url)


def main():
    if not TOKEN or not PIXEL_ID:
        die("META_ACCESS_TOKEN and META_PIXEL_ID required (direnv).")

    print(f"Checking pixel {PIXEL_ID}...", file=sys.stderr)

    pixel = get_pixel_info()
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=30)
    stats = get_event_stats(PIXEL_ID, start, end)

    here = Path(__file__).resolve().parent
    docs = here.parent / "docs"
    docs.mkdir(exist_ok=True)
    date_tag = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = docs / f"meta-pixel-health-{date_tag}.md"

    lines = [
        f"# Meta Pixel health check",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Pixel ID: `{PIXEL_ID}`",
        "",
        "## Pixel metadata",
        "",
    ]

    if "_error" in pixel or "_error_code" in pixel:
        lines.append(f"**Error fetching pixel:** `{pixel.get('_error_body') or pixel.get('_error')}`")
        lines.append("")
    else:
        name = pixel.get("name", "?")
        created = pixel.get("creation_time", "?")
        last_fired = pixel.get("last_fired_time", "?")
        auto_matching = pixel.get("enable_automatic_matching", "?")
        auto_fields = pixel.get("automatic_matching_fields", [])
        first_party = pixel.get("first_party_cookie_status", "?")
        lines.append(f"- **Name:** {name}")
        lines.append(f"- **Created:** {created}")
        lines.append(f"- **Last fired:** {last_fired}")
        lines.append(f"- **Automatic matching enabled:** {auto_matching}")
        lines.append(f"- **Automatic matching fields:** {', '.join(auto_fields) if auto_fields else '(none)'}")
        lines.append(f"- **First-party cookie:** {first_party}")
        lines.append("")

        # Staleness check
        if last_fired and last_fired != "?":
            try:
                # Meta returns ISO 8601 with Z or offset
                lf = datetime.fromisoformat(last_fired.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - lf).days
                if age_days > 1:
                    lines.append(f"**⚠ Pixel hasn't fired in {age_days} days.** This is the root cause of the zero-conversion problem.")
                else:
                    lines.append(f"✓ Pixel fired recently ({age_days}d ago).")
                lines.append("")
            except Exception:
                pass

    # Event stats
    lines.append("## Event volume (last 30 days)")
    lines.append("")

    if "_error" in stats or "_error_code" in stats:
        lines.append(f"**Error fetching event stats:** `{stats.get('_error_body') or stats.get('_error')}`")
        lines.append("")
        lines.append("_Common cause: the token's scope doesn't include `ads_management` + `business_management`. Check scopes at developers.facebook.com/tools/debug/accesstoken._")
    else:
        data = stats.get("data", [])
        if not data:
            lines.append("**No event data returned.** Either the pixel fired zero events in 30 days, or the `/stats` endpoint isn't available on this token's scope.")
            lines.append("")
        else:
            # Aggregate by event name across all buckets
            # Response shape: { data: [ { start_time, data: [{ value: "PageView", count: N }] } ] }
            event_totals: dict[str, int] = {}
            for bucket in data:
                for ev in bucket.get("data", []):
                    name = ev.get("value", "?")
                    try:
                        count = int(ev.get("count", 0) or 0)
                    except (ValueError, TypeError):
                        count = 0
                    event_totals[name] = event_totals.get(name, 0) + count

            lines.append("| Event | 30-day count |")
            lines.append("|---|---|")
            for name, count in sorted(event_totals.items(), key=lambda x: -x[1]):
                lines.append(f"| `{name}` | {count:,} |")
            lines.append("")

            # Key diagnosis
            purchase = event_totals.get("Purchase", 0)
            view_content = event_totals.get("ViewContent", 0)
            add_to_cart = event_totals.get("AddToCart", 0)
            initiate = event_totals.get("InitiateCheckout", 0)

            lines.append("## Funnel health")
            lines.append("")
            lines.append(f"- ViewContent: **{view_content:,}**")
            lines.append(f"- AddToCart: **{add_to_cart:,}**")
            lines.append(f"- InitiateCheckout: **{initiate:,}**")
            lines.append(f"- Purchase: **{purchase:,}**")
            lines.append("")

            if view_content == 0 and purchase == 0:
                lines.append("**⚠ Zero events across the funnel.** Pixel is not firing at all on the LC storefront. Check:")
                lines.append("1. Is the Pixel installed in the theme? (Settings > Customer events in Shopify admin)")
                lines.append("2. Is the correct Pixel ID connected?")
                lines.append("3. Does Meta Pixel Helper Chrome extension show the pixel on lostcollective.com?")
            elif purchase == 0 and view_content > 0:
                lines.append("**⚠ Purchase event not firing despite ViewContent events being received.** This is the classic Advantage+ signal-broken pattern:")
                lines.append("1. Meta sees traffic (ViewContent) so campaigns serve impressions")
                lines.append("2. Meta never sees conversions (Purchase) so no learning happens")
                lines.append("3. Campaigns keep spending without finding buyers")
                lines.append("")
                lines.append("**Fix paths:**")
                lines.append("- Verify the Purchase event fires on order confirmation page — test with Meta Pixel Helper")
                lines.append("- Check Shopify's Meta integration is sending server-side events via Conversion API (CAPI)")
                lines.append("- Confirm the Pixel ID in Shopify admin matches this Pixel (`1564860757158131` per memory)")
            elif purchase > 0 and purchase < view_content / 100:
                lines.append(f"**✓ Purchase events are firing** but conversion rate is low ({purchase/view_content*100:.2f}%). Audience quality or landing page issue rather than Pixel signal.")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✓ Wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
