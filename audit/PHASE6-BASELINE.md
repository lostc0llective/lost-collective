# Phase 6 Baseline Metrics

> Captured 2026-04-18 immediately before Phase 6 production push.
> These are the reference points for Task 6 rollback triggers.

## Branch state

- Branch: `feat/flex-migration`
- HEAD: `0026884` (chore: sync audit snapshots + Phase 6 sprint doc)
- Previous commit: `2c7b389` (Phase 5 close)
- Pushed to origin: yes
- theme-check: 179 errors / 527 warnings (= Phase 0 baseline, no regression)

## Shopify theme IDs

| Role | ID | Name |
|---|---|---|
| Live (pre-Phase-6) | `193859780774` | Lost Collective Live - 2026-04-15 |
| Staging | `193920860326` | LC Flex Staging 2026-04-18 |
| Pre-Phase-6 backup | (pending T1) | LC BACKUP Pre-Phase-6 2026-04-18 |
| Production candidate | (pending T2) | LC Flex Production Candidate 2026-04-18 |

## Order volume (Shopify Admin GraphQL)

- Last 24h: 0 orders
- Last 7d: 0 orders (avg 0/day)

Low-volume, high-value store. Order-count is not a sensitive rollback signal — use GA4 + Sentry + PageSpeed instead.

## GA4 (property 325530752) — last 28d

- Total sessions: 1,202 (~43/day)
- Top channels: Direct (611), Organic Search (436), Referral (68)
- Bounce rate (Direct): 74.1%
- Bounce rate (Organic Search): 51.6%

Rollback trigger for GA4 sessions/day: >30% drop vs 28d baseline sustained over 2h.

## PageSpeed Insights (Google API)

PageSpeed API was flaky during baseline capture (mobile timeouts, PDP 500s). Re-capture post-publish:

- Homepage desktop: Perf 18, LCP 3.8s, CLS 0.534, TBT 1420ms, FCP 1.0s
- Collection mobile: Perf 45, LCP 11.5s, CLS 0.017, TBT 740ms, FCP 3.2s
- Homepage mobile: API timeout (recapture in T5)
- PDP both strategies: API 500s (recapture in T5)

Rollback trigger: Homepage Perf drops >10 points vs pre-Phase-6 re-run.

## Sentry

No Sentry instrumentation on the Shopify storefront itself (only the Next.js dashboard). Phase 6 cannot rely on Sentry for theme-side errors. Rollback signal will be manual browser console inspection during T5 + customer reports.

## Rollback procedure (one command, memorised)

```bash
shopify theme publish --theme 193859780774 \
  --store lost-collective.myshopify.com
```

Re-publishing the current live theme ID atomically reverts the live swap. CDN warm-up: ~60s.

## Deploy window

Approved autonomous execution 2026-04-18 per Brett's explicit approval:
1. Deploy window open
2. Manual Admin UI duplicate path approved
3. Auto-rollback authority granted
4. "Trust CC to know the best course of action"
