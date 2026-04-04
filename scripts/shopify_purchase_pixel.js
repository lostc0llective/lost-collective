/**
 * Lost Collective — Shopify Web Pixel: GA4 Purchase Event
 *
 * Installed at: Shopify Admin → Settings → Customer events → Add custom pixel
 * Paste this entire file as the pixel code.
 *
 * How it works:
 *   - Runs in a sandboxed iframe on checkout.shopify.com (not on lostcollective.com)
 *   - Shopify fires checkout_completed after a successful order
 *   - This pixel forwards the purchase data to GA4 via Measurement Protocol v2
 *   - Bypasses GTM intentionally — web pixels cannot push to the storefront dataLayer
 *
 * GA4 property:  325530752
 * Measurement ID: G-411MPGQ64J
 * Stream ID:      3874452404
 */

const GA4_MEASUREMENT_ID = "G-411MPGQ64J";
const GA4_API_SECRET      = "jYOyhXD1TG-qygCdgzApkA";
const GA4_ENDPOINT        = `https://www.google-analytics.com/mp/collect?measurement_id=${GA4_MEASUREMENT_ID}&api_secret=${GA4_API_SECRET}`;

// ---------------------------------------------------------------------------
// Purchase event
// ---------------------------------------------------------------------------

analytics.subscribe("checkout_completed", (event) => {
  const checkout = event.data.checkout;
  if (!checkout) return;

  const order       = checkout.order;
  const totalPrice  = parseFloat(checkout.totalPrice?.amount  ?? 0);
  const totalTax    = parseFloat(checkout.totalTax?.amount    ?? 0);
  const shippingAmt = parseFloat(checkout.shippingLine?.price?.amount ?? 0);

  // Map line items to GA4 item format
  const items = (checkout.lineItems ?? []).map((line, index) => {
    const variant = line.variant ?? {};
    const product = variant.product ?? {};
    return {
      item_id:    variant.sku || variant.id || product.id || `item_${index}`,
      item_name:  line.title ?? product.title ?? "Unknown",
      price:      parseFloat(variant.price?.amount ?? 0),
      quantity:   line.quantity ?? 1,
    };
  });

  // Derive a stable client_id from the browser cookie if available,
  // otherwise fall back to a generated value so the event still lands.
  const clientId = (
    document.cookie.match(/_ga=GA\d+\.\d+\.(\d+\.\d+)/)?.[1] ??
    `${Date.now()}.${Math.floor(Math.random() * 1e9)}`
  );

  const payload = {
    client_id: clientId,
    events: [
      {
        name: "purchase",
        params: {
          transaction_id: order?.id ?? checkout.token,
          value:          totalPrice,
          tax:            totalTax,
          shipping:       shippingAmt,
          currency:       checkout.totalPrice?.currencyCode ?? "AUD",
          items,
        },
      },
    ],
  };

  fetch(GA4_ENDPOINT, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify(payload),
    keepalive: true,
  }).catch(() => {
    // Silently fail — pixel sandbox has no console access
  });
});

// ---------------------------------------------------------------------------
// begin_checkout deduplication guard
// (begin_checkout already fires from storefront GTM — this pixel does NOT
//  re-fire it to avoid double-counting. Only purchase needs this pixel.)
// ---------------------------------------------------------------------------
