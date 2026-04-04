"""
Shopify Webhook management — Lost Collective
Run via: op run --env-file=.env.tpl -- python3 scripts/webhooks.py

Subcommands:
  list                  — show all registered webhooks
  register              — register all ACTIVE_TOPICS (idempotent)
  delete <id>           — delete a single webhook by GID
  delete-all            — delete all registered webhooks
  test <topic>          — send a test payload to the local receiver

Endpoint config:
  Set WEBHOOK_ENDPOINT in .env.tpl to your live handler URL.
  For local testing run: python3 scripts/webhook_receiver.py
  then set WEBHOOK_ENDPOINT=http://localhost:8765/webhook
"""

import json, os, sys
sys.path.insert(0, 'scripts')
from shopify_gql import gql

ENDPOINT = os.environ.get("WEBHOOK_ENDPOINT", "")

# ── Topics to register ─────────────────────────────────────────────────────────
# Format: (topic_enum, description)
ACTIVE_TOPICS = [
    # Orders
    ("ORDERS_CREATE",          "New order placed"),
    ("ORDERS_PAID",            "Payment confirmed"),
    ("ORDERS_FULFILLED",       "Order fulfilled"),
    ("ORDERS_CANCELLED",       "Order cancelled"),
    ("ORDERS_UPDATED",         "Order updated"),
    ("REFUNDS_CREATE",         "Refund issued"),

    # Checkouts (abandoned cart signal)
    ("CHECKOUTS_CREATE",       "Checkout started"),
    ("CHECKOUTS_UPDATE",       "Checkout updated"),

    # Customers
    ("CUSTOMERS_CREATE",       "New customer created"),
    ("CUSTOMERS_UPDATE",       "Customer profile updated"),

    # Products & inventory
    ("PRODUCTS_CREATE",        "New product created"),
    ("PRODUCTS_UPDATE",        "Product updated"),
    ("PRODUCTS_DELETE",        "Product deleted"),
    ("INVENTORY_LEVELS_UPDATE","Inventory level changed"),

    # Collections
    ("COLLECTIONS_CREATE",     "New collection created"),
    ("COLLECTIONS_UPDATE",     "Collection updated"),
    ("COLLECTIONS_DELETE",     "Collection deleted"),
]


# ── GraphQL helpers ────────────────────────────────────────────────────────────

def list_webhooks() -> list[dict]:
    q = """
    {
      webhookSubscriptions(first: 50) {
        edges { node {
          id topic createdAt
          endpoint { __typename ... on WebhookHttpEndpoint { callbackUrl } }
        }}
      }
    }
    """
    return [e["node"] for e in gql(q)["data"]["webhookSubscriptions"]["edges"]]


def register_webhook(topic: str, endpoint: str) -> dict:
    m = """
    mutation Register($topic: WebhookSubscriptionTopic!, $webhook: WebhookSubscriptionInput!) {
      webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhook) {
        webhookSubscription { id topic }
        userErrors { field message }
      }
    }
    """
    resp = gql(m, {
        "topic": topic,
        "webhook": {
            "callbackUrl": endpoint,
            "format": "JSON",
        }
    })
    result = resp["data"]["webhookSubscriptionCreate"]
    if result["userErrors"]:
        raise RuntimeError(f"{topic}: {result['userErrors']}")
    return result["webhookSubscription"]


def delete_webhook(gid: str) -> bool:
    m = """
    mutation Delete($id: ID!) {
      webhookSubscriptionDelete(id: $id) {
        deletedWebhookSubscriptionId
        userErrors { field message }
      }
    }
    """
    result = gql(m, {"id": gid})["data"]["webhookSubscriptionDelete"]
    if result["userErrors"]:
        raise RuntimeError(result["userErrors"])
    return result["deletedWebhookSubscriptionId"] is not None


# ── CLI ────────────────────────────────────────────────────────────────────────

def cmd_list():
    subs = list_webhooks()
    if not subs:
        print("No webhooks registered.")
        return
    print(f"\n{'Topic':<45} {'Endpoint':<50} ID")
    print("─" * 110)
    for s in subs:
        url = s["endpoint"].get("callbackUrl", "(non-http)")
        print(f"  {s['topic']:<43} {url:<50} {s['id']}")
    print(f"\n{len(subs)} webhook(s) registered.")


def cmd_register():
    if not ENDPOINT:
        sys.exit(
            "WEBHOOK_ENDPOINT not set.\n"
            "Add to .env.tpl: WEBHOOK_ENDPOINT=https://your-handler.com/webhook\n"
            "For local testing: WEBHOOK_ENDPOINT=http://localhost:8765/webhook"
        )

    existing = {s["topic"] for s in list_webhooks()}
    registered, skipped = [], []

    for topic, desc in ACTIVE_TOPICS:
        if topic in existing:
            skipped.append(topic)
        else:
            try:
                register_webhook(topic, ENDPOINT)
                registered.append(topic)
                print(f"  ✓ {topic}")
            except Exception as e:
                print(f"  ✗ {topic}: {e}")

    print(f"\nRegistered: {len(registered)}  Already existed: {len(skipped)}")


def cmd_delete(gid: str):
    delete_webhook(gid)
    print(f"  Deleted: {gid}")


def cmd_delete_all():
    subs = list_webhooks()
    if not subs:
        print("Nothing to delete.")
        return
    confirm = input(f"Delete all {len(subs)} webhooks? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return
    for s in subs:
        delete_webhook(s["id"])
        print(f"  Deleted: {s['topic']}")


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd  = args[0] if args else "list"

    if cmd == "list":
        cmd_list()
    elif cmd == "register":
        cmd_register()
    elif cmd == "delete" and len(args) == 2:
        cmd_delete(args[1])
    elif cmd == "delete-all":
        cmd_delete_all()
    else:
        print(__doc__)
