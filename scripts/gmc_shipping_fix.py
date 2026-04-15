"""
GMC shipping rate mismatch investigation — Lost Collective
===========================================================
Investigates the 6,269 products showing "Missing or incorrect delivery costs"
in Google Merchant Center after the market restructure (236 -> 31 countries).

Checks:
  1. Which shipping zones exist in Shopify and which countries they cover
  2. Whether all 31 target market countries have shipping rates
  3. Whether shipping rate currencies match market presentment currencies

Usage:
  op run --env-file=.env.tpl -- python3 scripts/gmc_shipping_fix.py [--check] [--dry-run]

  --check     Investigation only (default) — report findings, no changes
  --dry-run   Show what changes would be made without applying them
  --fix       Apply shipping zone fixes (NOT IMPLEMENTED — requires manual Shopify Admin action)

SHOPIFY_ENV=staging by default. Investigation is read-only.
"""

import json, os, sys, argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
import shopify_gql as shop
from config import STORE, API_VERSION, ADMIN_TOKEN, ENV, print_env

# -- Target markets (31 countries after restructure) ---------------------------

# AU primary + NZ + US + UK + 27 EU countries
TARGET_COUNTRIES = {
    # Primary
    "AU": "Australia",
    # Oceania
    "NZ": "New Zealand",
    # North America
    "US": "United States",
    # UK
    "GB": "United Kingdom",
    # EU 27
    "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "HR": "Croatia",
    "CY": "Cyprus", "CZ": "Czechia", "DK": "Denmark", "EE": "Estonia",
    "FI": "Finland", "FR": "France", "DE": "Germany", "GR": "Greece",
    "HU": "Hungary", "IE": "Ireland", "IT": "Italy", "LV": "Latvia",
    "LT": "Lithuania", "LU": "Luxembourg", "MT": "Malta", "NL": "Netherlands",
    "PL": "Poland", "PT": "Portugal", "RO": "Romania", "SK": "Slovakia",
    "SI": "Slovenia", "ES": "Spain", "SE": "Sweden",
}

# Expected presentment currencies per market (GMC expects shipping currency to match)
MARKET_CURRENCIES = {
    "AU": "AUD", "NZ": "NZD", "US": "USD", "GB": "GBP",
    # EU countries use EUR
    **{cc: "EUR" for cc in [
        "AT", "BE", "CY", "EE", "FI", "FR", "DE", "GR", "IE", "IT",
        "LV", "LT", "LU", "MT", "NL", "PT", "SK", "SI", "ES",
    ]},
    # Non-euro EU
    "BG": "BGN", "HR": "EUR",  # Croatia adopted EUR 2023
    "CZ": "CZK", "DK": "DKK", "HU": "HUF", "PL": "PLN",
    "RO": "RON", "SE": "SEK",
}

LOG_DIR  = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "gmc_shipping_investigation.log"


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# -- Fetch shipping zones (REST API) ------------------------------------------

def fetch_shipping_zones() -> list[dict]:
    """Fetch all shipping zones via Shopify REST Admin API."""
    import urllib.request, urllib.error

    url = f"https://{STORE}/admin/api/{API_VERSION}/shipping_zones.json"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": ADMIN_TOKEN,
    }
    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
        return data.get("shipping_zones", [])
    except urllib.error.HTTPError as e:
        log(f"ERROR: HTTP {e.code} fetching shipping zones: {e.read().decode()[:500]}")
        return []


# -- Fetch markets via GraphQL -------------------------------------------------

def fetch_markets() -> list[dict]:
    """Fetch all Shopify markets with their regions and currencies."""
    query = """
    query Markets($first: Int!, $cursor: String) {
      markets(first: $first, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        edges {
          node {
            id name handle primary enabled
            currencySettings { baseCurrency { currencyCode } }
            regions(first: 250) {
              edges {
                node {
                  ... on MarketRegionCountry {
                    code name
                    currency { currencyCode }
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    markets = []
    for page in shop.paginate(query, {"first": 10}, ["markets"]):
        for edge in page:
            m = edge["node"]
            regions = [r["node"] for r in m.get("regions", {}).get("edges", [])]
            markets.append({
                "id": m["id"],
                "name": m["name"],
                "handle": m["handle"],
                "primary": m["primary"],
                "enabled": m["enabled"],
                "baseCurrency": m.get("currencySettings", {}).get("baseCurrency", {}).get("currencyCode"),
                "regions": regions,
            })
    return markets


# -- Analysis ------------------------------------------------------------------

def analyse(zones: list[dict], markets: list[dict]) -> dict:
    """Cross-reference shipping zones with target markets."""
    findings = {
        "countries_with_shipping": {},
        "countries_without_shipping": [],
        "currency_mismatches": [],
        "zone_summary": [],
        "market_summary": [],
    }

    # Build a map of country code -> shipping zone info
    country_shipping = {}
    for zone in zones:
        zone_name = zone.get("name", "Unnamed")
        countries = zone.get("countries", [])
        provinces = []

        zone_info = {
            "name": zone_name,
            "id": zone.get("id"),
            "country_count": len(countries),
            "countries": [],
            "price_based_rates": [],
            "weight_based_rates": [],
        }

        for country in countries:
            cc = country.get("code", "")
            zone_info["countries"].append(cc)

            rates = []
            for rate in zone.get("price_based_shipping_rates", []):
                rates.append({
                    "name": rate.get("name"),
                    "price": rate.get("price"),
                    "min_order": rate.get("min_order_subtotal"),
                    "max_order": rate.get("max_order_subtotal"),
                })
            for rate in zone.get("weight_based_shipping_rates", []):
                rates.append({
                    "name": rate.get("name"),
                    "price": rate.get("price"),
                    "min_weight": rate.get("weight_low"),
                    "max_weight": rate.get("weight_high"),
                })

            country_shipping[cc] = {
                "zone": zone_name,
                "zone_id": zone.get("id"),
                "rates": rates,
                "country_name": country.get("name", cc),
                "tax": country.get("tax", 0),
            }

        zone_info["price_based_rates"] = zone.get("price_based_shipping_rates", [])
        zone_info["weight_based_rates"] = zone.get("weight_based_shipping_rates", [])
        findings["zone_summary"].append(zone_info)

    findings["countries_with_shipping"] = country_shipping

    # Check which target countries are missing shipping rates
    for cc, name in sorted(TARGET_COUNTRIES.items()):
        if cc not in country_shipping:
            findings["countries_without_shipping"].append({
                "code": cc,
                "name": name,
                "expected_currency": MARKET_CURRENCIES.get(cc, "?"),
            })

    # Build market summary from GraphQL data
    for market in markets:
        if not market["enabled"]:
            continue
        region_codes = [r.get("code", "") for r in market["regions"]]
        findings["market_summary"].append({
            "name": market["name"],
            "handle": market["handle"],
            "primary": market["primary"],
            "baseCurrency": market["baseCurrency"],
            "region_count": len(region_codes),
            "regions": sorted(region_codes),
        })

    # Check currency mismatches (shipping rate currency vs market currency)
    # Shopify shipping rates are in the store's base currency (AUD).
    # GMC expects shipping costs in the same currency as the product price for each market.
    # Shopify's Markets feature handles currency conversion for product prices,
    # but shipping rates may not auto-convert depending on configuration.
    for cc, name in sorted(TARGET_COUNTRIES.items()):
        expected = MARKET_CURRENCIES.get(cc, "AUD")
        if expected != "AUD" and cc in country_shipping:
            # Shipping rate is likely in AUD (store base currency)
            # GMC needs it in the market's presentment currency
            findings["currency_mismatches"].append({
                "code": cc,
                "name": name,
                "shipping_currency": "AUD (store base)",
                "expected_currency": expected,
                "note": "Shopify Markets may auto-convert, but GMC feed may receive AUD rate",
            })

    return findings


def print_report(findings: dict):
    """Print a structured investigation report."""
    print("\n" + "=" * 70)
    print("  GMC SHIPPING RATE INVESTIGATION")
    print("=" * 70)

    # Zone summary
    print(f"\n  SHIPPING ZONES ({len(findings['zone_summary'])})")
    print("  " + "-" * 66)
    for zone in findings["zone_summary"]:
        rate_count = len(zone["price_based_rates"]) + len(zone["weight_based_rates"])
        print(f"  {zone['name']:30s}  {zone['country_count']:3d} countries  {rate_count} rates")
        for rate in zone["price_based_rates"]:
            price = rate.get("price", "?")
            name = rate.get("name", "Unnamed rate")
            min_o = rate.get("min_order_subtotal", "")
            max_o = rate.get("max_order_subtotal", "")
            bracket = ""
            if min_o or max_o:
                bracket = f"  (${min_o or '0'} - ${max_o or '∞'})"
            print(f"    ${price:>8s}  {name}{bracket}")
        for rate in zone["weight_based_rates"]:
            price = rate.get("price", "?")
            name = rate.get("name", "Unnamed rate")
            print(f"    ${price:>8s}  {name} (weight-based)")

    # Market summary
    print(f"\n  SHOPIFY MARKETS (enabled)")
    print("  " + "-" * 66)
    for market in findings["market_summary"]:
        tag = " (PRIMARY)" if market["primary"] else ""
        print(f"  {market['name']:30s}  {market['region_count']:3d} regions  {market['baseCurrency']}{tag}")

    # Missing shipping coverage
    missing = findings["countries_without_shipping"]
    if missing:
        print(f"\n  MISSING SHIPPING RATES ({len(missing)} target countries)")
        print("  " + "-" * 66)
        for c in missing:
            print(f"  {c['code']}  {c['name']:30s}  needs {c['expected_currency']} rate")
    else:
        print("\n  All 31 target countries have shipping rates.")

    # Currency mismatches
    mismatches = findings["currency_mismatches"]
    if mismatches:
        print(f"\n  POTENTIAL CURRENCY MISMATCHES ({len(mismatches)} countries)")
        print("  " + "-" * 66)
        for c in mismatches:
            print(f"  {c['code']}  {c['name']:30s}  shipping={c['shipping_currency']}  GMC expects={c['expected_currency']}")
        print("\n  NOTE: Shopify Markets auto-converts prices and shipping for international")
        print("  markets. If the Google channel feed correctly includes converted rates,")
        print("  these are not real mismatches. Check the GMC feed XML to confirm.")

    # Countries with rates
    covered = findings["countries_with_shipping"]
    target_covered = {cc: v for cc, v in covered.items() if cc in TARGET_COUNTRIES}
    non_target = {cc: v for cc, v in covered.items() if cc not in TARGET_COUNTRIES}

    print(f"\n  TARGET COUNTRIES WITH SHIPPING ({len(target_covered)}/{len(TARGET_COUNTRIES)})")
    print("  " + "-" * 66)
    for cc in sorted(target_covered):
        info = target_covered[cc]
        rate_count = len(info["rates"])
        print(f"  {cc}  {info['country_name']:30s}  zone={info['zone']:20s}  {rate_count} rates")

    if non_target:
        print(f"\n  NON-TARGET COUNTRIES WITH SHIPPING ({len(non_target)})")
        print("  " + "-" * 66)
        for cc in sorted(non_target):
            info = non_target[cc]
            print(f"  {cc}  {info['country_name']:30s}  zone={info['zone']}")

    print("\n" + "=" * 70)


def write_findings_json(findings: dict):
    """Write findings to a JSON file for reference."""
    out = LOG_DIR / "gmc_shipping_investigation.json"
    with open(out, "w") as f:
        json.dump(findings, f, indent=2, default=str)
    log(f"Findings written to {out}")


# -- Main ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="GMC shipping rate investigation")
    parser.add_argument("--check", action="store_true", default=True, help="Investigation only (default)")
    parser.add_argument("--dry-run", action="store_true", help="Show what changes would be made")
    parser.add_argument("--fix", action="store_true", help="Apply fixes (NOT IMPLEMENTED)")
    args = parser.parse_args()

    print("\n  GMC Shipping Rate Investigation")
    print("  " + "-" * 40)
    print_env()
    print()

    if args.fix:
        log("ERROR: --fix is not implemented. Shipping zone changes must be made in Shopify Admin.")
        log("This script is for investigation only. See HANDOFF.md for recommended actions.")
        sys.exit(1)

    # Step 1: Fetch shipping zones (REST API)
    log("Fetching shipping zones via REST API...")
    zones = fetch_shipping_zones()
    log(f"  Found {len(zones)} shipping zones")

    # Step 2: Fetch markets (GraphQL)
    log("Fetching Shopify markets via GraphQL...")
    markets = fetch_markets()
    enabled = [m for m in markets if m["enabled"]]
    log(f"  Found {len(markets)} markets ({len(enabled)} enabled)")

    # Step 3: Analyse
    log("Cross-referencing shipping zones with target markets...")
    findings = analyse(zones, markets)

    # Step 4: Report
    print_report(findings)
    write_findings_json(findings)

    # Summary
    missing = len(findings["countries_without_shipping"])
    mismatches = len(findings["currency_mismatches"])

    print(f"\n  Summary:")
    print(f"    Shipping zones:       {len(zones)}")
    print(f"    Target countries:     {len(TARGET_COUNTRIES)}")
    print(f"    With shipping rates:  {len(TARGET_COUNTRIES) - missing}")
    print(f"    Missing rates:        {missing}")
    print(f"    Currency mismatches:  {mismatches} (potential — check GMC feed)")

    if missing:
        print(f"\n  RECOMMENDATION: Add shipping rates for {missing} missing countries.")
        print("  This must be done in Shopify Admin > Settings > Shipping and delivery.")
        print("  See HANDOFF.md for detailed instructions.")

    print()


if __name__ == "__main__":
    main()
