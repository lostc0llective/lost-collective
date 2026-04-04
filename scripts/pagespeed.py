"""
PageSpeed Insights baseline — Lost Collective
Run: python3 scripts/pagespeed.py
Requires: PAGESPEED_API_KEY environment variable (or edit API_KEY below)
Get key: console.cloud.google.com → APIs → PageSpeed Insights API → Credentials
"""
import urllib.request, urllib.parse, json, os, sys

API_KEY = os.environ.get("PAGESPEED_API_KEY", "")

PAGES = {
    "Homepage":   "https://lost-collective.myshopify.com",
    "Collection": "https://lost-collective.myshopify.com/collections/white-bay-power-station",
    "Product":    "https://lost-collective.myshopify.com/products/white-bay-power-station-boiler-water-valves",
}

def psi(url, strategy):
    key_param = f"&key={API_KEY}" if API_KEY else ""
    api = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={urllib.parse.quote(url)}&strategy={strategy}{key_param}"
    with urllib.request.urlopen(api, timeout=90) as r:
        return json.loads(r.read())

print(f"{'Page':<12} {'Strategy':<10} {'Perf':>5}  {'LCP':<10} {'CLS':<8} {'TBT':<10} {'FCP'}")
print("-" * 70)

for name, url in PAGES.items():
    for strategy in ["mobile", "desktop"]:
        try:
            data   = psi(url, strategy)
            cats   = data["lighthouseResult"]["categories"]
            audits = data["lighthouseResult"]["audits"]
            perf   = round(cats["performance"]["score"] * 100)
            lcp    = audits.get("largest-contentful-paint",  {}).get("displayValue", "—")
            cls    = audits.get("cumulative-layout-shift",   {}).get("displayValue", "—")
            tbt    = audits.get("total-blocking-time",       {}).get("displayValue", "—")
            fcp    = audits.get("first-contentful-paint",    {}).get("displayValue", "—")
            print(f"{name:<12} {strategy:<10} {perf:>5}  {lcp:<10} {cls:<8} {tbt:<10} {fcp}")
        except Exception as e:
            print(f"{name:<12} {strategy:<10} ERROR: {e}")
