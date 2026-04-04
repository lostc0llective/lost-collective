/**
 * Series Volume Discount Function
 *
 * Applies a percentage discount when a customer buys 2 or more prints
 * from the same photographic series. Series is determined by the product
 * metafield: custom.collection_series (references a collection).
 *
 * Tiers:
 *   2 prints from same series → 10% off those items
 *   3+ prints from same series → 15% off those items
 *
 * The discount is applied per-line-item, only to lines in the qualifying group.
 */

// ---------------------------------------------------------------------------
// Input/Output types are injected by the Shopify Functions runtime.
// The function receives a RunInput object and must return a FunctionRunResult.
// ---------------------------------------------------------------------------

const TIERS = [
  { minQty: 3, percentage: 15.0, label: "Series Bundle (3+): 15% off" },
  { minQty: 2, percentage: 10.0, label: "Series Bundle (2+): 10% off" },
];

const NO_DISCOUNT = { discounts: [], discountApplicationStrategy: "FIRST" };

/**
 * Main entry point — called by the Shopify Functions runtime.
 * @param {Object} input - RunInput from Shopify
 * @returns {Object} FunctionRunResult
 */
export function run(input) {
  const lines = input.cart.lines;

  if (!lines || lines.length === 0) {
    return NO_DISCOUNT;
  }

  // Group cart lines by series GID.
  // The metafield value is the GID of the referenced collection
  // e.g. "gid://shopify/Collection/123456789"
  const seriesGroups = {};

  for (const line of lines) {
    const seriesValue = line.merchandise?.product?.seriesMetafield?.value;

    // Skip lines with no series (standalone prints, framing, etc.)
    if (!seriesValue) continue;

    if (!seriesGroups[seriesValue]) {
      seriesGroups[seriesValue] = [];
    }
    seriesGroups[seriesValue].push(line);
  }

  const discounts = [];

  for (const [seriesGid, seriesLines] of Object.entries(seriesGroups)) {
    // Total quantity across all lines in this series
    const totalQty = seriesLines.reduce((sum, line) => sum + line.quantity, 0);

    // Find the best applicable tier
    const tier = TIERS.find((t) => totalQty >= t.minQty);
    if (!tier) continue;

    discounts.push({
      message: tier.label,
      targets: seriesLines.map((line) => ({
        cartLine: { id: line.id },
      })),
      value: {
        percentage: {
          value: tier.percentage.toString(),
        },
      },
    });
  }

  if (discounts.length === 0) {
    return NO_DISCOUNT;
  }

  return {
    discounts,
    discountApplicationStrategy: "ALL",
  };
}
