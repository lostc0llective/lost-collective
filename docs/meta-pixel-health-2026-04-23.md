# Meta Pixel health check

Generated: 2026-04-23 20:53 UTC
Pixel ID: `1564860757158131`

## Pixel metadata

- **Name:** Lost Collective's Pixel
- **Created:** 2016-03-24T09:29:29+0000
- **Last fired:** 2026-04-22T23:59:59+0000
- **Automatic matching enabled:** True
- **Automatic matching fields:** em, fn, ln, ge, ph, ct, st, zp, db, country, external_id
- **First-party cookie:** first_party_cookie_enabled

✓ Pixel fired recently (0d ago).

## Event volume (last 30 days)

| Event | 30-day count |
|---|---|
| `PageView` | 27,799 |
| `ViewContent` | 16,713 |
| `Search` | 54 |
| `AddToCart` | 27 |
| `InitiateCheckout` | 15 |
| `Lead` | 3 |

## Funnel health

- ViewContent: **16,713**
- AddToCart: **27**
- InitiateCheckout: **15**
- Purchase: **0**

**⚠ Purchase event not firing despite ViewContent events being received.** This is the classic Advantage+ signal-broken pattern:
1. Meta sees traffic (ViewContent) so campaigns serve impressions
2. Meta never sees conversions (Purchase) so no learning happens
3. Campaigns keep spending without finding buyers

**Fix paths:**
- Verify the Purchase event fires on order confirmation page — test with Meta Pixel Helper
- Check Shopify's Meta integration is sending server-side events via Conversion API (CAPI)
- Confirm the Pixel ID in Shopify admin matches this Pixel (`1564860757158131` per memory)
