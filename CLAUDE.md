# Lost Collective — Claude Code Project

## Read this first, every session

Memory files live at `~/.claude/projects/-Users-brettpatman-lost-collective/memory/`.
The index (`MEMORY.md`) loads automatically. Read the relevant files before acting — they hold credentials, account IDs, decisions already made, and working style rules. Do not ask Brett for information that is already in memory.

Master context: `~/lost-collective/CLAUDE.md`

---

## Who Brett is

Store owner of Lost Collective — a fine art photography print store on Shopify. Not a contractor or developer. Technically proficient and decisive. Works fast, wants direct responses. Full profile: `memory/user_profile.md`.

---

## Tone of Voice

All content (collection descriptions, product copy, blog posts, social captions, ad copy) MUST follow:

**`docs/lost-collective-tov.md`** — read it before generating any content.

Key rules:
- Website/Shopify content is about the *place*, never about Brett (except About page)
- First person (I) only for social media and blog posts
- Historical facts are essential, not optional
- Sensory, visceral writing — make people imagine being there
- No em dashes. No hashtags on Facebook. No AI slop words (stunning, captivating, testament to, etc.)

---

## Working style rules

- Lead with action, not preamble. Never restate what Brett said.
- Tables over paragraphs for structured info.
- Get direction approval before executing design changes.
- Never suggest nav/footer changes — menus are already configured (`memory/feedback_navigation.md`).
- Never execute a full design overhaul without explicit approval.
- Full scope set upfront for all integrations — never minimum viable.
- `SHOPIFY_ENV=staging` by default. Require explicit instruction to target production.

---

## Credentials and secrets

All credentials are in **1Password (Private vault)**. Scripts inject them via:
```bash
# Run from ~/lost-collective/ root (where .env.tpl lives)
op run --env-file=.env.tpl -- python3 shopify/scripts/[script].py
```

If 1Password prompts authentication:
```bash
export OP_SESSION_my=$(op signin --raw) && op whoami
```

Never ask Brett for API keys or tokens — check 1Password or `.env.tpl` first. Full integration details: `memory/project_integrations.md`.

---

## Available scripts

All scripts run from `~/lost-collective/` root:

| Script | What it does | Run command |
|--------|-------------|-------------|
| `shopify/scripts/shopify_gql.py` | Shopify Admin GraphQL layer — products, metafields, collections, SEO | `op run --env-file=.env.tpl -- python3 shopify/scripts/shopify_gql.py` |
| `shopify/scripts/config.py` | Environment config (staging/production) — source of truth for theme IDs | (imported by other scripts) |
| `shopify/scripts/klaviyo.py` | Klaviyo — lists, profiles, events, campaigns, flows | `op run --env-file=.env.tpl -- python3 shopify/scripts/klaviyo.py` |
| `shopify/scripts/gsc.py` | Google Search Console — performance, top pages, queries, inspect URL | `op run --env-file=.env.tpl -- python3 shopify/scripts/gsc.py` |
| `shopify/scripts/meta.py` | Meta Graph API — pixel health, campaigns, catalog, audiences | `op run --env-file=.env.tpl -- python3 shopify/scripts/meta.py` |
| `shopify/scripts/meta_audiences.py` | Meta custom audience refresh — buyer email upload (value-based) | `op run --env-file=.env.tpl -- python3 shopify/scripts/meta_audiences.py` |
| `shopify/scripts/gemini.py` | Gemini 2.5 Flash — content generation at scale | `op run --env-file=.env.tpl -- python3 shopify/scripts/gemini.py` |
| `shopify/scripts/yotpo.py` | Yotpo — reviews, ratings, audit | `op run --env-file=.env.tpl -- python3 shopify/scripts/yotpo.py` |
| `shopify/scripts/webhooks.py` | Shopify webhook management (list/register/delete) | `op run --env-file=.env.tpl -- python3 shopify/scripts/webhooks.py` |
| `shopify/scripts/webhook_receiver.py` | Local webhook test receiver (localhost:8765) | `python3 shopify/scripts/webhook_receiver.py` |
| `shopify/scripts/ynab.py` | YNAB — account balances, budget, transactions, cleanup | `op run --env-file=.env.tpl -- python3 shopify/scripts/ynab.py [audit\|accounts\|budget\|cleanup]` |
| `shopify/scripts/ynab_import.py` | Import ING CSV exports into YNAB with dedup | `op run --env-file=.env.tpl -- python3 shopify/scripts/ynab_import.py [bills\|spending\|saving]` |
| `shopify/scripts/pagespeed.py` | PageSpeed Insights (needs PAGESPEED_API_KEY in .env.tpl) | `op run --env-file=.env.tpl -- python3 shopify/scripts/pagespeed.py` |
| `shopify/scripts/ga4.py` | GA4 Data API — sessions, purchases, conversions | `op run --env-file=.env.tpl -- python3 shopify/scripts/ga4.py` |
| `shopify/scripts/gtm.py` | GTM audit/publish (needs service account as Editor in GTM UI first) | `op run --env-file=.env.tpl -- python3 shopify/scripts/gtm.py` |
| `shopify/scripts/overnight_content.py` | Batch Gemini content generation — collection descriptions + subject_description metafields | `op run --env-file=.env.tpl -- python3 shopify/scripts/overnight_content.py` |

---

## Shopify theme

- **Live theme ID:** `141183910054` ("Lost Collective Live", Flex v5.2.1 by Out of the Sandbox)
- **Staging theme ID:** `143356625062` ("Copy of Lost Collective Live")
- Push to staging: `shopify theme push --theme 143356625062 --store lost-collective.myshopify.com --allow-live`
- Push to live: `shopify theme push --theme 141183910054 --store lost-collective.myshopify.com --allow-live`
- Custom CSS: `assets/custom.css` (sections 24–30 are custom additions)
- Custom JS: `assets/swatch-layout.js`

---

## Infrastructure

- **Cloudflare Worker:** `lost-collective-webhooks.fragrant-union-3149.workers.dev` — 17 Shopify webhook topics, HMAC verified, fans out to Klaviyo
- **Stape Server GTM:** sole analytics layer (GTM-K898GWK). No direct GA4 in theme.
- **GitHub:** `github.com/lostc0llective/lost-collective` — main→production CI/CD via GitHub Actions

---

## Key store facts

- 1,809 products, 62 series, all with matching Shopify collections
- All products have: `custom.collection_series`, `print_technique`, `paper_type`, `certificate_included`, `custom.location`, `custom.year_photographed`, `custom.subject_description`
- SKU format: `LC-{handle}-{size}-{type-abbrev}[-{colour}]`
- Edition sizes: M=100, L=50, XL=25. S and XS are open editions.
- Currency: AUD. Multi-currency enabled. High average order value.

---

## Pending actions (check `memory/project_outstanding_merchant_actions.md` for full list)

**Claude to do:**
- `ynab.py cleanup` — delete legacy reconciled/uncleared transactions (Bills/Spending/Saving balances are wrong). Run when YNAB rate limit is clear (200 req/hour rolling window).

**Brett to do:**
- Mailchimp account deletion (overdue)
- Meta App ID + Secret from developers.facebook.com/apps/ → Settings → Basic → add to 1Password + `.env.tpl`
- YNAB: close Qantas Brett account + add Bankwest card (use Chrome prompt)
- YNAB: categorise ~200 uncategorised transactions
- Klaviyo: paste copy from `docs/klaviyo-flow-copy.md` → activate subscription → flip 7 flows live
- GTM: add `claude-code-lost-collective@lost-collective-492307.iam.gserviceaccount.com` as Editor in GTM-K898GWK UI
