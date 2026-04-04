/**
 * Lost Collective — Shopify Webhook Worker
 * Deployed at: https://lost-collective-webhooks.fragrant-union-3149.workers.dev
 *
 * Receives all Shopify webhook events, verifies HMAC signatures,
 * routes to handlers, and fans out to downstream services (Klaviyo etc.)
 *
 * Secrets (set via wrangler secret put):
 *   SHOPIFY_WEBHOOK_SECRET  — Shopify Admin → Settings → Notifications → Webhooks → signing secret
 *   KLAVIYO_PRIVATE_KEY     — Full-access private key
 */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Health check
    if (url.pathname === "/" || url.pathname === "/health") {
      return new Response("Lost Collective webhook worker — ok", { status: 200 });
    }

    // Only handle /webhook
    if (url.pathname !== "/webhook" || request.method !== "POST") {
      return new Response("Not found", { status: 404 });
    }

    const body  = await request.arrayBuffer();
    const topic = request.headers.get("X-Shopify-Topic") || "";
    const shop  = request.headers.get("X-Shopify-Shop-Domain") || "";
    const sig   = request.headers.get("X-Shopify-Hmac-Sha256") || "";

    // ── Verify HMAC signature ──────────────────────────────────────────────────
    if (env.SHOPIFY_WEBHOOK_SECRET) {
      const valid = await verifySignature(body, sig, env.SHOPIFY_WEBHOOK_SECRET);
      if (!valid) {
        console.error(`Invalid signature for ${topic}`);
        return new Response("Unauthorized", { status: 401 });
      }
    }

    // ── Parse payload ──────────────────────────────────────────────────────────
    let payload;
    try {
      payload = JSON.parse(new TextDecoder().decode(body));
    } catch {
      return new Response("Bad request", { status: 400 });
    }

    console.log(`[${topic}] ${shop}`);

    // ── Route ──────────────────────────────────────────────────────────────────
    try {
      await route(topic, payload, env);
    } catch (err) {
      console.error(`Handler error for ${topic}:`, err);
      // Still return 200 — Shopify will retry on non-2xx indefinitely
    }

    return new Response("ok", { status: 200 });
  }
};


// ── Router ─────────────────────────────────────────────────────────────────────

async function route(topic, payload, env) {
  switch (topic) {

    // Orders
    case "orders/create":
      await onOrderCreate(payload, env);
      break;
    case "orders/paid":
      await onOrderPaid(payload, env);
      break;
    case "orders/fulfilled":
      await onOrderFulfilled(payload, env);
      break;
    case "orders/cancelled":
      await onOrderCancelled(payload, env);
      break;
    case "orders/updated":
      await onOrderUpdated(payload, env);
      break;
    case "refunds/create":
      await onRefund(payload, env);
      break;

    // Checkouts
    case "checkouts/create":
    case "checkouts/update":
      await onCheckout(topic, payload, env);
      break;

    // Customers
    case "customers/create":
      await onCustomerCreate(payload, env);
      break;
    case "customers/update":
      await onCustomerUpdate(payload, env);
      break;

    // Inventory
    case "inventory_levels/update":
      await onInventoryUpdate(payload, env);
      break;

    // Products
    case "products/create":
    case "products/update":
    case "products/delete":
      await onProductChange(topic, payload, env);
      break;

    // Collections
    case "collections/create":
    case "collections/update":
    case "collections/delete":
      await onCollectionChange(topic, payload, env);
      break;

    default:
      console.log(`Unhandled topic: ${topic}`);
  }
}


// ── Handlers ───────────────────────────────────────────────────────────────────

async function onOrderCreate(p, env) {
  const items = (p.line_items || []).map(li => li.title).join(", ");
  console.log(`NEW ORDER #${p.order_number} | ${p.email} | ${p.currency} ${p.total_price} | ${items}`);

  // Track Placed Order event in Klaviyo
  if (p.email) {
    await klaviyoEvent("Placed Order", p.email, {
      order_id:    p.id,
      order_num:   p.order_number,
      total:       parseFloat(p.total_price),
      currency:    p.currency,
      items:       (p.line_items || []).map(li => ({
        title:    li.title,
        sku:      li.sku,
        price:    li.price,
        quantity: li.quantity,
      })),
    }, env);
  }
}

async function onOrderPaid(p, env) {
  console.log(`PAID #${p.order_number} | ${p.currency} ${p.total_price}`);

  if (p.email) {
    await klaviyoEvent("Paid Order", p.email, {
      order_id:  p.id,
      order_num: p.order_number,
      total:     parseFloat(p.total_price),
      currency:  p.currency,
    }, env);
  }
}

async function onOrderFulfilled(p, env) {
  console.log(`FULFILLED #${p.order_number} | ${p.email}`);

  if (p.email) {
    await klaviyoEvent("Fulfilled Order", p.email, {
      order_id:        p.id,
      order_num:       p.order_number,
      tracking_number: p.fulfillments?.[0]?.tracking_number,
      tracking_url:    p.fulfillments?.[0]?.tracking_url,
    }, env);
  }
}

async function onOrderCancelled(p, env) {
  console.log(`CANCELLED #${p.order_number} | reason: ${p.cancel_reason}`);
}

async function onOrderUpdated(p, env) {
  // Low-noise — only log, no downstream action by default
  console.log(`ORDER UPDATED #${p.order_number} | status: ${p.financial_status}`);
}

async function onRefund(p, env) {
  console.log(`REFUND | order: ${p.order_id} | amount: ${p.transactions?.[0]?.amount}`);
}

async function onCheckout(topic, p, env) {
  const email = p.email;
  if (!email) return; // anonymous checkout — no email yet, skip

  if (topic === "checkouts/create") {
    console.log(`CHECKOUT STARTED | ${email} | ${p.total_price}`);
    await klaviyoEvent("Started Checkout", email, {
      checkout_token: p.token,
      total:          parseFloat(p.total_price || 0),
      currency:       p.currency,
      items:          (p.line_items || []).map(li => ({
        title:    li.title,
        sku:      li.sku,
        price:    li.price,
        quantity: li.quantity,
      })),
    }, env);
  }
}

async function onCustomerCreate(p, env) {
  console.log(`NEW CUSTOMER | ${p.email} | ${p.first_name} ${p.last_name}`);

  // Upsert profile in Klaviyo
  await klaviyoUpsertProfile({
    email:      p.email,
    first_name: p.first_name,
    last_name:  p.last_name,
    phone:      p.phone,
    location: {
      city:    p.default_address?.city,
      country: p.default_address?.country_code,
    },
    properties: {
      shopify_id:       p.id,
      accepts_marketing: p.accepts_marketing,
    },
  }, env);
}

async function onCustomerUpdate(p, env) {
  console.log(`CUSTOMER UPDATE | ${p.email}`);

  await klaviyoUpsertProfile({
    email:      p.email,
    first_name: p.first_name,
    last_name:  p.last_name,
    properties: {
      shopify_id:        p.id,
      accepts_marketing: p.accepts_marketing,
      orders_count:      p.orders_count,
      total_spent:       parseFloat(p.total_spent || 0),
    },
  }, env);
}

async function onInventoryUpdate(p, env) {
  const avail = p.available;
  console.log(`INVENTORY | item:${p.inventory_item_id} available:${avail}`);

  // Low stock alert — log prominently (extend to Slack/email as needed)
  if (avail !== null && avail <= 3) {
    console.warn(`⚠ LOW STOCK — inventory_item_id:${p.inventory_item_id} only ${avail} remaining`);
  }
}

async function onProductChange(topic, p, env) {
  const action = topic.split("/")[1];
  console.log(`PRODUCT ${action.toUpperCase()} | ${p.handle} | ${p.title}`);
}

async function onCollectionChange(topic, p, env) {
  const action = topic.split("/")[1];
  console.log(`COLLECTION ${action.toUpperCase()} | ${p.handle} | ${p.title}`);
}


// ── Klaviyo helpers ────────────────────────────────────────────────────────────

async function klaviyoEvent(name, email, properties, env) {
  if (!env.KLAVIYO_PRIVATE_KEY) return;

  const body = {
    data: {
      type: "event",
      attributes: {
        metric:     { data: { type: "metric", attributes: { name } } },
        profile:    { data: { type: "profile", attributes: { email } } },
        properties: properties || {},
      }
    }
  };

  const resp = await fetch("https://a.klaviyo.com/api/events/", {
    method:  "POST",
    headers: {
      "Authorization":  `Klaviyo-API-Key ${env.KLAVIYO_PRIVATE_KEY}`,
      "revision":       "2024-10-15",
      "Content-Type":   "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const err = await resp.text();
    console.error(`Klaviyo event error (${name}):`, err);
  }
}

async function klaviyoUpsertProfile(attrs, env) {
  if (!env.KLAVIYO_PRIVATE_KEY) return;

  const body = {
    data: { type: "profile", attributes: attrs }
  };

  const resp = await fetch("https://a.klaviyo.com/api/profile-import/", {
    method:  "POST",
    headers: {
      "Authorization": `Klaviyo-API-Key ${env.KLAVIYO_PRIVATE_KEY}`,
      "revision":      "2024-10-15",
      "Content-Type":  "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const err = await resp.text();
    console.error("Klaviyo profile upsert error:", err);
  }
}


// ── HMAC verification ──────────────────────────────────────────────────────────

async function verifySignature(body, headerSig, secret) {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig     = await crypto.subtle.sign("HMAC", key, body);
  const computed = btoa(String.fromCharCode(...new Uint8Array(sig)));
  return computed === headerSig;
}
