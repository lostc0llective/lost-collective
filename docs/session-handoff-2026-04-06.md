# Session Handoff — 6 April 2026

Everything done this session. What's left to push, and what Brett needs to do.

---

## Pending push (Claude — needs 1Password re-auth)

These two files are edited locally but not yet live on the production theme (143356625062). The Shopify automatic discount is already live — only the on-page notice needs pushing.

| File | Change | Why blocked |
|------|--------|-------------|
| `shopify/snippets/product__form.liquid` | Collector discount notice: "Add 2 or more prints — 10% off applied at checkout" | 1Password session timed out |
| `shopify/assets/custom.css` | `.lc-collector-discount` styles (grey pill under edition scarcity bar) | Same |

**To push:** re-auth 1Password then run:
```bash
export OP_SESSION_my=$(op signin --raw) && op whoami
op run --env-file=.env.tpl -- python3 -c "
import sys; sys.path.insert(0, 'shopify/scripts')
from config import STORE, ADMIN_TOKEN
import requests

def push(key, path):
    content = open(path).read()
    r = requests.put(f'https://{STORE}/admin/api/2025-01/themes/143356625062/assets.json',
        headers={'X-Shopify-Access-Token': ADMIN_TOKEN},
        json={'asset': {'key': key, 'value': content}})
    print('pushed' if 'asset' in r.json() else 'ERROR', key)

push('snippets/product__form.liquid', 'shopify/snippets/product__form.liquid')
push('assets/custom.css', 'shopify/assets/custom.css')
"
```

---

## This session — what was completed

### Audit tracker: 34/44 items done (was 27/44 at start of session)

| Item | What was done |
|------|---------------|
| M2 | Judge.me confirmed live. Yotpo block removed from product template via API. |
| M3 | Klaviyo popup copy: "Before the next series goes live" / early access. |
| M6 | Faceted filtering added to collection template (`faceted_filtering` block). |
| M7 | Gift card product confirmed live (Brett created it). |
| M9 | `prints-from-50` smart collection created. |
| S1 | 18 location landing pages live. |
| S2 | 5 SEO blog posts published. Ongoing monthly. |
| S3 | Theme evaluation brief written (`docs/theme-evaluation-brief-2026.md`). |
| S4 | Trade page live at /pages/trade. |
| S5 | 4 aesthetic smart collections: Dark & Moody, After Dark, Graffiti & Urban Decay, Wide Open Spaces. |
| S6 | /pages/in-your-home created. |
| S7 | n/a — no YouTube videos. |
| S8 | Multi-currency already live. |
| D3 | Favicon already set. White Bay OG fallback added to social-meta-info.liquid. |
| D14 | Automatic 10% collector discount created (ID: 2327615864998). On-page notice added (push pending). |
| Lightroom | Both auth bugs fixed. Endpoint verified: `{"ok":true,"message":"Connected to Lost Collective dashboard"}`. |

---

## Brett actions outstanding (non-blocking for Claude)

### Shopify audit items requiring Brett's decision

| Item | Action needed |
|------|--------------|
| S3 | Read `docs/theme-evaluation-brief-2026.md`. Decide: stay Flex / migrate to Prestige / other. |
| D4 | Primary nav restructure — tell Claude what changes you want (menus are your call). |
| D8 | Japan mega menu duplication — decide how to clean it up. |
| D17 | App audit — open Shopify Admin > Apps > list what's installed. Claude can advise what to cut. |
| D19 | Japan cross-listing architecture — filter on existing collections? Separate editorial section? |

### Klaviyo (flip to Live — all manual/draft)

| Flow | Action |
|------|--------|
| Abandoned Checkout Reminder | Open flow in Klaviyo, check trigger, flip to Live |
| Welcome Series | Paste copy from `docs/klaviyo-flow-copy.md` → flip to Live |
| Winback | Same |
| Browse Abandonment | Same |
| Thank You / Post-Purchase | Same |
| Product Review / Cross-Sell | Same |
| Sunset Re-permission | Same |

### Instafeed (D22)

Open Instafeed app in Shopify admin. Connect the @lostc0llective Instagram account in app settings. Then report the app block UUID so Claude can inject it into `templates/index.json`.

### Other

| Item | Action |
|------|--------|
| Meta App ID + Secret | Get from developers.facebook.com → Settings → Basic → add to 1Password |
| GTM | Add `claude-code-lost-collective@lost-collective-492307.iam.gserviceaccount.com` as Editor in GTM-K898GWK UI |
| YNAB | Close Qantas Brett account + add Bankwest card + categorise ~200 uncategorised transactions |
| Mailchimp | Delete legacy account |

---

## Audit tracker score

| Tier | Total | Done | In Progress | Todo | Blocked |
|------|-------|------|-------------|------|---------|
| Quick Wins | 5 | 5 | 0 | 0 | 0 |
| Medium Term | 9 | 9 | 0 | 0 | 0 |
| Strategic | 8 | 6 | 1 | 0 | 0 |
| Detailed | 22 | 14 | 0 | 5 | 3 |
| **Total** | **44** | **34** | **1** | **5** | **3** |
