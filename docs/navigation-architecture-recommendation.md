# Navigation Architecture Recommendation
**Lost Collective — 60-Series Fine Art Photography Catalogue**
**Prepared:** 2026-04-03

---

## Current State

The theme supports three navigation levels and a full mega-menu system (`sections/include-mega-menu.liquid`). The mega-menu supports columns containing: linked menu lists, images, featured products, and promotional banners. It is currently unused or minimally configured.

For a catalogue of 60 series across two countries and multiple subject categories, a flat main menu of 60 series would be unusable. Mega-menu architecture is the right solution.

**Do not configure the mega-menu until you have decided on a grouping strategy.** The three viable approaches are below.

---

## Option A — Geography First (Recommended)

```
Australia
  ├── Industrial
  ├── Medical
  ├── Rural & Agricultural
  ├── Commercial & Civic
  └── View all Australian series →

Japan
  ├── Industrial
  ├── Medical & Institutional
  ├── Commercial & Hotels
  └── View all Japanese series →

Browse All Series →
```

**Why this works:**
- The two-country split is the clearest differentiator for buyers (many customers are drawn to one country's aesthetic)
- Within each country, 5–8 categories are a manageable scan load
- "View all" links at the bottom of each panel provide an escape hatch
- The Japan collection is distinct enough to justify its own panel

**Mega-menu setup:**
- Two mega-menu panels: "Australia" and "Japan" (triggered by top-level nav items of the same name)
- Each panel: one `menu` column linking to series collections, one `featured_promo` or `image` column with an editorial image for that country

---

## Option B — Subject Category First

```
Industrial
  ├── Power Stations
  ├── Cement & Concrete Works
  ├── Abattoirs & Meatworks
  ├── Textile & Leather
  └── View all industrial →

Healthcare & Institutional
  ├── Hospitals & Asylums
  ├── Schools & Universities
  └── View all institutional →

Landscapes & Rural
  ├── Farmsteads & Homesteads
  ├── Silos & Grain Stores
  └── View all rural →

Browse All Series →
```

**Why this works:**
- Buyers browsing by subject type (power stations, hospitals) find their category immediately
- Works well if you plan to expand into more countries — geography becomes less central to the structure
- Natural alignment with existing product type taxonomy

---

## Option C — Era / Decay Status

```
Recently Documented
Recently Demolished
Heritage Listed
Unknown Status
```

**Why this does NOT work well:**
- Status changes over time — a series documented before demolition must be recategorised
- Buyers don't typically browse by demolition status
- This information belongs as a filter or badge, not a primary navigation dimension

---

## Recommended Navigation Structure (Option A)

### Top-level menu items

| Item | Type | Link |
|------|------|------|
| Australia | Mega-menu trigger | /collections/australia (or #) |
| Japan | Mega-menu trigger | /collections/japan (or #) |
| All Series | Direct link | /collections/all |
| About | Direct link | /pages/about |
| Cart | Icon (action bar) | — |

### Admin setup for mega-menu

1. Create menu in Admin: **Navigation → Add menu** — name: "Australia Series"
   - Add links to each Australian series collection
2. Create menu in Admin: "Japan Series"
   - Add links to each Japanese series collection
3. In Theme Editor, add a **Mega Menu** section to the header group
4. Set `Parent menu item` to "Australia" — this triggers the mega-panel when hovering that nav item
5. Add a `menu` block — link it to "Australia Series" menu
6. Add an `image` or `featured_promo` block — upload an editorial photograph representing Australia
7. Repeat for Japan

---

## Accessibility notes on the current mega-menu

The current mega-menu uses a CSS radio/checkbox pattern for no-JS support. `aria-expanded` is present but **statically set to "false"** and is not updated when a panel opens. This is a known limitation of the CSS-only toggle pattern. If keyboard accessibility for the mega-menu is a priority, the `z__jsMegaMenu.js` file would need to be updated to toggle `aria-expanded` dynamically on hover/focus. This is a medium-complexity JS change — raise it if needed.

---

## Current mega-menu file

`sections/include-mega-menu.liquid` — max 6 blocks per mega panel, supports: menu list, image, HTML, featured product, promotional banner, mixed (4 menus + images).
