"""
Local webhook receiver — Lost Collective
For development/testing only. Receives Shopify webhooks and logs them.

Run: python3 scripts/webhook_receiver.py
Listens on: http://localhost:8765/webhook

To expose publicly for testing (requires ngrok):
  ngrok http 8765
  → use the https URL as WEBHOOK_ENDPOINT in .env.tpl

Shopify signs every webhook with HMAC-SHA256.
Set SHOPIFY_WEBHOOK_SECRET in .env.tpl to verify signatures.
Get secret: Admin → Settings → Notifications → Webhooks → any webhook → signing secret
"""

import hashlib, hmac, base64, json, os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

PORT   = int(os.environ.get("WEBHOOK_PORT", 8765))
SECRET = os.environ.get("SHOPIFY_WEBHOOK_SECRET", "")


def verify_signature(body: bytes, header_sig: str) -> bool:
    if not SECRET:
        return True   # skip verification if no secret configured
    digest = hmac.new(SECRET.encode(), body, hashlib.sha256).digest()
    computed = base64.b64encode(digest).decode()
    return hmac.compare_digest(computed, header_sig)


class WebhookHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path != "/webhook":
            self.send_response(404)
            self.end_headers()
            return

        length  = int(self.headers.get("Content-Length", 0))
        body    = self.rfile.read(length)
        topic   = self.headers.get("X-Shopify-Topic", "unknown")
        shop    = self.headers.get("X-Shopify-Shop-Domain", "unknown")
        sig     = self.headers.get("X-Shopify-Hmac-Sha256", "")

        if not verify_signature(body, sig):
            print(f"  ✗ INVALID SIGNATURE — {topic}")
            self.send_response(401)
            self.end_headers()
            return

        self.send_response(200)
        self.end_headers()

        try:
            payload = json.loads(body)
        except Exception:
            payload = {"raw": body.decode(errors="replace")}

        ts = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{ts}] {topic} — {shop}")
        print(json.dumps(payload, indent=2, ensure_ascii=False)[:800])

        # Route to handler
        dispatch(topic, payload)

    def log_message(self, *args):
        pass   # suppress default access log


# ── Event handlers ─────────────────────────────────────────────────────────────

def dispatch(topic: str, payload: dict):
    handlers = {
        "orders/create":           on_order_create,
        "orders/paid":             on_order_paid,
        "orders/fulfilled":        on_order_fulfilled,
        "orders/cancelled":        on_order_cancelled,
        "checkouts/create":        on_checkout_create,
        "customers/create":        on_customer_create,
        "inventory_levels/update": on_inventory_update,
        "products/update":         on_product_update,
    }
    handler = handlers.get(topic)
    if handler:
        handler(payload)


def on_order_create(p: dict):
    order_id  = p.get("id")
    email     = p.get("email", "")
    total     = p.get("total_price", "0")
    currency  = p.get("currency", "AUD")
    items     = [li.get("title") for li in p.get("line_items", [])]
    print(f"  → NEW ORDER #{p.get('order_number')} | {email} | {currency} {total}")
    for item in items:
        print(f"     · {item}")


def on_order_paid(p: dict):
    print(f"  → PAID #{p.get('order_number')} | {p.get('currency')} {p.get('total_price')}")


def on_order_fulfilled(p: dict):
    print(f"  → FULFILLED #{p.get('order_number')} | {p.get('email')}")


def on_order_cancelled(p: dict):
    reason = p.get("cancel_reason", "unknown")
    print(f"  → CANCELLED #{p.get('order_number')} | reason: {reason}")


def on_checkout_create(p: dict):
    email = p.get("email", "(no email yet)")
    total = p.get("total_price", "0")
    print(f"  → CHECKOUT STARTED | {email} | {total}")


def on_customer_create(p: dict):
    print(f"  → NEW CUSTOMER | {p.get('email')} | {p.get('first_name')} {p.get('last_name')}")


def on_inventory_update(p: dict):
    item_id  = p.get("inventory_item_id")
    location = p.get("location_id")
    avail    = p.get("available")
    print(f"  → INVENTORY UPDATE | item:{item_id} location:{location} available:{avail}")
    if avail is not None and avail <= 2:
        print(f"  ⚠  LOW STOCK — only {avail} remaining")


def on_product_update(p: dict):
    print(f"  → PRODUCT UPDATE | {p.get('handle')} | {p.get('title')}")


# ── Entry ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    server = HTTPServer(("", PORT), WebhookHandler)
    print(f"Webhook receiver running on http://localhost:{PORT}/webhook")
    if not SECRET:
        print("  ⚠  SHOPIFY_WEBHOOK_SECRET not set — skipping signature verification")
    print("  Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
