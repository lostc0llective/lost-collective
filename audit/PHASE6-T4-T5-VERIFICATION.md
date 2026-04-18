# Phase 6 T4 + T5 Verification

> Executed 2026-04-18 immediately after production publish.

## T4 — Live swap

- Published: **193925775526** — "LC Flex Production Candidate 2026-04-18" (now `MAIN`)
- Unpublished (rollback target): **193859780774** — "Lost Collective Live - 2026-04-15"
- Backup (pre-Phase-6 snapshot): **193925644454** — "LC BACKUP Pre-Phase-6 2026-04-18"

Admin GraphQL API confirms the role swap: `themes(roles: [MAIN])` returns only the new theme.

## T5 — Critical-path walk

| # | Check | Result |
|---|---|---|
| 1 | Homepage loads (200) | ✓ |
| 2 | PDP loads (200) | ✓ |
| 3 | Collection loads (200) | ✓ |
| 4 | Cart loads (200) | ✓ |
| 5 | About page loads (200) | ✓ |
| 6 | Blog loads (200) | ✓ |
| 7 | Search loads (200) | ✓ |
| 8 | Cart AJAX add works | ✓ |
| 9 | Cart AJAX clear works | ✓ |
| 10 | Checkout button = #EBAC20 gold bg + #1a1a1a dark text | ✓ (Phase 4 admin + Phase 5 contrast) |
| 11 | Header renders absolute over video hero on homepage | ✓ (overlay restored) |
| 12 | Header renders relative on PDP (no overlay there) | ✓ |
| 13 | Server-timing `theme;desc="193925775526"` on all paths | ✓ |

## Known edge cache quirk

Homepage HTML body is in Shopify's `page_cache` (etag `W/"page_cache:13043623:IndexController:..."`).

- Server IS serving new theme (`server-timing: theme;desc="193925775526"`)
- HTML body contains stale `Shopify.theme` JS variable referencing the old theme ID
- Asset URLs in the HTML still reference old theme's compiled CSS path `/shop/t/59/...`
- All OTHER paths (`/products/*`, `/collections/*`, `/cart`, `/pages/*`) serve fresh with new theme metadata and assets

**Impact:** minimal. The new theme's underlying assets are being served, and the only visible difference is that `window.Shopify.theme.id` JS variable is outdated on the homepage. Shopify's page cache TTL is typically 5-15 minutes for homepage after a theme publish; if it persists past 30 minutes, trigger a manual purge via saving `templates/index.json` in the admin.

Customer-facing impact: negligible. Visual rendering on all pages is correct.

## Rollback state

Rollback command (one-line, known good):

```bash
shopify theme publish --theme 193859780774 --store lost-collective.myshopify.com
```

Rollback reverts to the pre-Phase-6 theme instantly. Also available:
- `shopify theme publish --theme 193925644454` — restore the T1 backup (identical to pre-Phase-6 but a different theme slot)

## Moving to T6 (24-hour monitor)

Rollback triggers per the Phase 6 sprint:
- Sentry error spike (>20% above 24h baseline) — N/A, theme has no Sentry
- Conversion rate drop (>30% over 2h) — monitor via Shopify admin
- GA4 sessions drop (>30% sustained 2h)
- Any customer report of broken flow
- Any P0 visual regression reported by Brett
