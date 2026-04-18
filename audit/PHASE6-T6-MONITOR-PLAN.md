# Phase 6 T6 — 24-hour monitor plan

> Monitoring window opens 2026-04-18 ~20:15 AEST. Close at 2026-04-19 ~20:15 AEST.

## What's monitored

| Signal | Baseline | Rollback trigger | Check via |
|---|---|---|---|
| GA4 sessions/day | ~43/day (28d avg) | >30% drop sustained 2h | `scripts/ga4.py` |
| Shopify orders | 0/24h, 0/7d (low-volume store) | >50% drop from 7d trailing avg | Shopify admin |
| Customer reports | none | any | Brett |
| Sentry errors | N/A (no instrumentation) | N/A | — |
| PageSpeed homepage Perf | 18 desktop (API flaky) | >10pt drop | `scripts/pagespeed.py` |
| Customer-facing visual regressions | none | any P0 reported | Brett's eyes |

## Claude Code is NOT running a daemon

Session-persistent monitoring isn't viable within Claude Code. Instead:

1. **Brett is the primary watcher** — use the site as normal over the next 24h. Any page that looks wrong, any customer email about a broken flow, any Klaviyo bounce — message CC immediately.

2. **Periodic checks** on Brett's schedule. Run from `~/Claude/lost-collective/`:
   ```bash
   op run --env-file=.env.tpl -- python3 shopify/scripts/ga4.py
   ```

3. **Rollback is one command, already verified**:
   ```bash
   shopify theme publish --theme 193859780774 \
     --store lost-collective.myshopify.com
   ```
   The old live theme is sitting unpublished as an instant revert target. No data loss, no delay.

## Homepage page cache

Continue to watch whether homepage HTML clears from Shopify's edge cache. If still stale after ~30 minutes post-publish:
- Open the Shopify admin → Customize theme → save any trivial change → exit. That forces a cache invalidation.
- Or push `templates/index.json` with a trivial whitespace change.

This is a cosmetic-metadata issue only (the `window.Shopify.theme.id` JS variable is the only visible symptom; rendering is correct).

## Auto-rollback thresholds (for CC if Brett triggers)

If Brett says any of these, CC will rollback without further confirmation:

- "Rollback" or "revert" — explicit command
- "Checkout is broken" / "cart is broken" / "PDP is broken" — critical flow failures
- "Prices are wrong" — pricing regression (very unlikely from refactor)

CC will NOT auto-rollback for:
- Cosmetic complaints (font size, spacing, colour nuance — raise a defer-to-post-Phase-6 item instead)
- The homepage `Shopify.theme.id` cache issue (cosmetic metadata, not visible to users)
- Logo-list marquee regression (pre-existing from Flex v5.5.1, documented as post-Phase-6 backlog)

## Known deferred items (not rollback triggers)

| Item | Why not rolling back | Post-Phase-6 fix |
|---|---|---|
| Logo-list marquee | Pre-existed the refactor (Flex v5.5.1 upgrade broke it) | Rebuild as CSS marquee (~30min, same pattern as testimonials) |
| 27 C-4? suspect !important rows | Defensive keeps with WHY comments | Manual review only if visual changes prompt it |
| 6-7 dead-sibling selector trims | Dead clutter inside live rules | Low-priority cleanup |
