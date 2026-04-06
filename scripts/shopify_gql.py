"""
Shopify Admin GraphQL integration layer — Lost Collective
Store: lost-collective.myshopify.com  |  API: 2025-01

Run via: op run --env-file=.env.tpl -- python3 scripts/shopify_gql.py
Token:   1Password → Lost Collective — Shopify → Admin Token
         Update token: Admin → Settings → Apps → Develop apps → API credentials → Reveal token

Scoped to operations this store actually uses:
  products, collections, variants, metafields, orders (read), inventory
"""

import json, os, sys, time, urllib.request, urllib.error
from typing import Generator
from config import STORE, API_VERSION, ADMIN_TOKEN, ENV, production_banner

# ── Config ─────────────────────────────────────────────────────────────────────

VERSION  = API_VERSION
TOKEN    = ADMIN_TOKEN
ENDPOINT = f"https://{STORE}/admin/api/{VERSION}/graphql.json"

HEADERS = {
    "Content-Type":           "application/json",
    "X-Shopify-Access-Token": TOKEN,
}

# Shopify GraphQL cost throttle — restore rate is 50/s on Basic, higher on Advanced
MAX_COST_PER_REQUEST = 900   # leave headroom below 1000 limit
THROTTLE_WAIT        = 2.0   # seconds to wait on throttle before retry


# ── Base client ────────────────────────────────────────────────────────────────

def gql(query: str, variables: dict = None, retries: int = 5) -> dict:
    """Execute a GraphQL query. Returns the full response dict."""
    if not TOKEN or TOKEN.strip() == "":
        sys.exit(
            "SHOPIFY_ADMIN_TOKEN not set.\n"
            "Run via: op run --env-file=.env.tpl -- python3 scripts/shopify_gql.py\n"
            "Or update the token in 1Password: Lost Collective — Shopify → Admin Token"
        )

    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(ENDPOINT, data=payload, headers=HEADERS, method="POST")

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read())

            # Surface GraphQL-level errors
            if "errors" in data:
                for err in data["errors"]:
                    if err.get("extensions", {}).get("code") == "THROTTLED":
                        wait = THROTTLE_WAIT * (attempt + 1)
                        print(f"  throttled — waiting {wait}s", file=sys.stderr)
                        time.sleep(wait)
                        break
                else:
                    raise RuntimeError(f"GraphQL errors: {data['errors']}")
            else:
                return data

        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                wait = 2 ** attempt
                print(f"  HTTP {e.code} — retry {attempt+1}/{retries} in {wait}s", file=sys.stderr)
                time.sleep(wait)
            else:
                raise

    raise RuntimeError(f"Failed after {retries} attempts")


def paginate(query: str, variables: dict, path: list[str]) -> Generator[list, None, None]:
    """
    Auto-paginate a GraphQL query using cursor-based pagination.

    path: list of keys to walk from data → the connection node
          e.g. ["products"] for data["products"]
               ["collection", "products"] for data["collection"]["products"]

    Yields each page's `edges` list. Query must include:
        pageInfo { hasNextPage endCursor }
    and accept $cursor: String as a variable.
    """
    variables = {**variables, "cursor": None}
    while True:
        resp = gql(query, variables)
        node = resp["data"]
        for key in path:
            node = node[key]
        yield node["edges"]
        if not node["pageInfo"]["hasNextPage"]:
            break
        variables["cursor"] = node["pageInfo"]["endCursor"]


# ── Products ───────────────────────────────────────────────────────────────────

def get_product(gid: str) -> dict:
    """Fetch a single product by GID (gid://shopify/Product/123)."""
    q = """
    query GetProduct($id: ID!) {
      product(id: $id) {
        id title handle status
        variants(first: 100) {
          edges { node { id sku title price inventoryQuantity } }
        }
        metafields(first: 50) {
          edges { node { namespace key value type } }
        }
      }
    }
    """
    return gql(q, {"id": gid})["data"]["product"]


def iter_products(query_str: str = "", page_size: int = 50) -> Generator[dict, None, None]:
    """
    Iterate all products matching an optional query string.
    Yields individual product nodes.

    query_str examples:
      ""                              → all products
      "status:active"                 → active only
      "collection_id:12345"           → in a collection
      "tag:limited-edition"           → by tag
    """
    q = """
    query Products($first: Int!, $cursor: String, $query: String) {
      products(first: $first, after: $cursor, query: $query) {
        pageInfo { hasNextPage endCursor }
        edges {
          node {
            id title handle status vendor
            featuredImage { url }
            variants(first: 100) {
              edges { node { id sku title price compareAtPrice inventoryQuantity } }
            }
            metafields(first: 20, namespace: "custom") {
              edges { node { namespace key value type } }
            }
          }
        }
      }
    }
    """
    for page in paginate(q, {"first": page_size, "query": query_str}, ["products"]):
        for edge in page:
            yield edge["node"]


# ── Collections ────────────────────────────────────────────────────────────────

def get_collection(gid: str) -> dict:
    """Fetch a single collection by GID."""
    q = """
    query GetCollection($id: ID!) {
      collection(id: $id) {
        id title handle descriptionHtml
        metafields(first: 20) {
          edges { node { namespace key value type } }
        }
      }
    }
    """
    return gql(q, {"id": gid})["data"]["collection"]


def iter_collections(page_size: int = 50) -> Generator[dict, None, None]:
    """Iterate all collections. Yields individual collection nodes."""
    q = """
    query Collections($first: Int!, $cursor: String) {
      collections(first: $first, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        edges {
          node {
            id title handle
            metafields(first: 20, namespace: "custom") {
              edges { node { namespace key value type } }
            }
          }
        }
      }
    }
    """
    for page in paginate(q, {"first": page_size}, ["collections"]):
        for edge in page:
            yield edge["node"]


# ── Variants ───────────────────────────────────────────────────────────────────

def get_variants(product_gid: str) -> list[dict]:
    """Return all variants for a product."""
    q = """
    query ProductVariants($id: ID!) {
      product(id: $id) {
        variants(first: 100) {
          edges { node { id sku title price compareAtPrice inventoryQuantity
                         selectedOptions { name value } } }
        }
      }
    }
    """
    edges = gql(q, {"id": product_gid})["data"]["product"]["variants"]["edges"]
    return [e["node"] for e in edges]


def update_variant(product_gid: str, variant_gid: str, input_fields: dict) -> dict:
    """
    Update a single variant. input_fields may include: price, compareAtPrice, sku, etc.
    Uses productVariantsBulkUpdate (productVariantUpdate removed in API 2025-01).
    Returns the updated variant node.
    """
    q = """
    mutation UpdateVariant($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
      productVariantsBulkUpdate(productId: $productId, variants: $variants) {
        productVariants { id sku price compareAtPrice }
        userErrors { field message }
      }
    }
    """
    # Note: sku must be nested under inventoryItem in ProductVariantsBulkInput
    resp = gql(q, {"productId": product_gid, "variants": [{"id": variant_gid, **input_fields}]})
    result = resp["data"]["productVariantsBulkUpdate"]
    if result["userErrors"]:
        raise RuntimeError(f"Variant update errors: {result['userErrors']}")
    return result["productVariants"][0]


# ── Metafields ─────────────────────────────────────────────────────────────────

def metafields_set(entries: list[dict]) -> dict:
    """
    Bulk-set metafields. Each entry: { ownerId, namespace, key, type, value }
    Processes in batches of 25 (Shopify limit per call).
    Returns dict of { success: int, errors: list }
    """
    q = """
    mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
      metafieldsSet(metafields: $metafields) {
        metafields { id namespace key }
        userErrors  { field message elementIndex }
      }
    }
    """
    BATCH = 25
    success, errors = 0, []

    for i in range(0, len(entries), BATCH):
        batch = entries[i : i + BATCH]
        resp  = gql(q, {"metafields": batch})
        result = resp["data"]["metafieldsSet"]
        success += len(result.get("metafields") or [])
        errors  += result.get("userErrors") or []

    return {"success": success, "errors": errors}


def delete_metafield(metafield_gid: str) -> bool:
    """Delete a single metafield by GID."""
    q = """
    mutation DeleteMetafield($input: MetafieldDeleteInput!) {
      metafieldDelete(input: $input) {
        deletedId
        userErrors { field message }
      }
    }
    """
    resp = gql(q, {"input": {"id": metafield_gid}})
    result = resp["data"]["metafieldDelete"]
    if result["userErrors"]:
        raise RuntimeError(f"Metafield delete errors: {result['userErrors']}")
    return result["deletedId"] is not None


# ── Orders (read-only) ─────────────────────────────────────────────────────────

def iter_orders(query_str: str = "", page_size: int = 50) -> Generator[dict, None, None]:
    """
    Iterate orders. Read-only.

    query_str examples:
      "financial_status:paid"
      "created_at:>2026-01-01"
      "fulfillment_status:unfulfilled"
    """
    q = """
    query Orders($first: Int!, $cursor: String, $query: String) {
      orders(first: $first, after: $cursor, query: $query) {
        pageInfo { hasNextPage endCursor }
        edges {
          node {
            id name createdAt displayFinancialStatus displayFulfillmentStatus
            totalPriceSet { shopMoney { amount currencyCode } }
            customer { id email firstName lastName }
            lineItems(first: 20) {
              edges { node { title quantity sku variantTitle } }
            }
          }
        }
      }
    }
    """
    for page in paginate(q, {"first": page_size, "query": query_str}, ["orders"]):
        for edge in page:
            yield edge["node"]


# ── Inventory ──────────────────────────────────────────────────────────────────

def get_locations() -> list[dict]:
    """Return all active locations."""
    q = """
    query {
      locations(first: 10) {
        edges { node { id name isActive } }
      }
    }
    """
    return [e["node"] for e in gql(q)["data"]["locations"]["edges"]]


def adjust_inventory(inventory_item_gid: str, location_gid: str, delta: int) -> dict:
    """Adjust inventory quantity by delta (positive = add, negative = remove)."""
    q = """
    mutation AdjustInventory($input: InventoryAdjustQuantityInput!) {
      inventoryAdjustQuantity(input: $input) {
        inventoryLevel { available }
        userErrors { field message }
      }
    }
    """
    resp = gql(q, {"input": {
        "inventoryItemId": inventory_item_gid,
        "locationId":      location_gid,
        "availableDelta":  delta,
    }})
    result = resp["data"]["inventoryAdjustQuantity"]
    if result["userErrors"]:
        raise RuntimeError(f"Inventory errors: {result['userErrors']}")
    return result["inventoryLevel"]


# ── Shop info ──────────────────────────────────────────────────────────────────

def get_shop() -> dict:
    """Return basic shop info — good for verifying auth."""
    q = """
    query {
      shop {
        name myshopifyDomain plan { displayName }
        primaryDomain { url }
        currencyCode
      }
    }
    """
    return gql(q)["data"]["shop"]


# ── CLI diagnostics ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    production_banner()
    print("Verifying connection...\n")
    shop = get_shop()
    print(f"  Store:    {shop['name']} ({shop['myshopifyDomain']})")
    print(f"  Plan:     {shop['plan']['displayName']}")
    print(f"  Domain:   {shop['primaryDomain']['url']}")
    print(f"  Currency: {shop['currencyCode']}")

    print("\nCounting products...")
    count = sum(1 for _ in iter_products())
    print(f"  {count} products")

    print("\nCounting collections...")
    count = sum(1 for _ in iter_collections())
    print(f"  {count} collections")

    locs = get_locations()
    print(f"\nLocations ({len(locs)}):")
    for loc in locs:
        print(f"  {loc['id']}  {loc['name']}  active:{loc['isActive']}")
