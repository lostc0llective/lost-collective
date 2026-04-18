# Phase 5 Visual QA Plan

> Generated 2026-04-18. Targets feat/flex-migration @ 4ab4666 on staging 193920860326.
> Minimum 20 captures covering every template + key interactive states.
> Customer-account captures deferred (no logged-in session available in this sprint —
> flagged in T3 as upstream-flex scope for Phase 6 exclusion list).

| capture_id | template_file | url_path | device | state | blocker_states |
|---|---|---|---|---|---|
| 001 | `templates/index.json` | `/` | desktop | default | — |
| 002 | `templates/index.json` | `/` | mobile | default | — |
| 003 | `templates/index.json` | `/` | desktop | menu-open (Shop dropdown) | — |
| 004 | `templates/collection.json` | `/collections/all` | desktop | default | default, filters-active |
| 005 | `templates/collection.json` | `/collections/all` | mobile | default | — |
| 006 | `templates/collection.modern.json` | `/collections/parramatta-road` | desktop | default | collection exists |
| 007 | `templates/product.json` | `/products/parramatta-road-yeah?variant=39841454751910` | desktop | default (XS variant) | default, sold-out |
| 008 | `templates/product.json` | `/products/parramatta-road-yeah?variant=39841454751910` | mobile | default | — |
| 009 | `templates/product.json` | `/products/parramatta-road-yeah?variant=39841454751910` | desktop | variant-XL-selected | test L+XL edition tier rendering |
| 010 | `templates/cart.json` | `/cart` | desktop | empty | empty, 1-item |
| 011 | `templates/cart.json` | `/cart` | desktop | 1-item | requires sandbox /cart/add |
| 012 | `templates/cart.json` | `/cart` | mobile | 1-item | — |
| 013 | `templates/blog.json` | `/blogs/blog` | desktop | default | — |
| 014 | `templates/article.json` | `/blogs/blog/tin-city-built-without-permission-on-the-lake` | desktop | default | default (canonical from prior phases) |
| 015 | `templates/article.json` | `/blogs/blog/tin-city-built-without-permission-on-the-lake` | mobile | default | — |
| 016 | `templates/search.json` | `/search?q=parramatta` | desktop | populated | populated, zero-results |
| 017 | `templates/search.json` | `/search?q=xyznoresults` | desktop | zero-results | — |
| 018 | `templates/404.json` | `/does-not-exist` | desktop | default | — |
| 019 | `templates/page.json` | `/pages/about` | desktop | default | — |
| 020 | `templates/page.contact.json` | `/pages/contact` | desktop | default | — |
| 021 | `templates/page.faq.json` | `/pages/faq` | desktop | default | — |
| 022 | `templates/index.json` | `/` | desktop | keyboard-focus-nav | Tab through top-nav CTAs — focus ring visibility |
| 023 | `templates/product.json` | `/products/parramatta-road-yeah` | desktop | keyboard-focus-add-to-cart | Tab to Add to cart button |
| 024 | `templates/product.json` | `/products/parramatta-road-yeah` | desktop | hover-cta | hover over primary CTA |
| 025 | `templates/index.json` | `/` | desktop | cart-drawer-open | trigger cart drawer with item added |

## Customer-account captures — DEFERRED

These require a logged-in customer session which is not available in this sprint. Flagged for Phase 6 exclusion list or post-launch follow-up:

| capture_id | template_file | url_path | why deferred |
|---|---|---|---|
| a01 | `templates/customers/login.json` | `/account/login` | Accessible unauth — can still capture. |
| a02 | `templates/customers/register.json` | `/account/register` | Accessible unauth — can still capture. |
| a03 | `templates/customers/account.json` | `/account` | Requires logged-in session. |
| a04 | `templates/customers/addresses.json` | `/account/addresses` | Requires logged-in session. |
| a05 | `templates/customers/order.json` | `/account/orders/{id}` | Requires real order. |

Will capture `a01` + `a02` in T2 (they render unauth). `a03`–`a05` go to the deferred list.

## Interactive-state captures

Covered by `022` (focus nav), `023` (focus CTA), `024` (hover CTA), `025` (cart drawer).
Form-error states (`empty required field submission` on newsletter + contact) will be probed
opportunistically during T2 if they render without real network submission.

## Out of scope

- Checkout pages (Shopify-hosted, theme has no direct control)
- Password page (admin-only)
- Gift-card page (rare template, captured only if a gift-card URL is trivially findable)
- `templates/collection.subcollections.json` (no collection on the store uses it per `shopify_gql`)
- `templates/product.quickshop.json` + `templates/product.scrolling.json` — rare variants, admin choice
