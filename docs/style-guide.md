# Lost Collective — Design System & Style Rules

> Single source of truth for visual consistency across the Shopify theme.
> All values are defined as CSS custom properties in `assets/custom.css` Section 1.
> Reference this document before adding any new UI element to the theme.

---

## Colour Palette

| Token | Hex | Use |
|-------|-----|-----|
| `--color-brand-yellow` | `#ebac20` | Gold accent — links, hover states, active labels, button text, focus rings |
| `--color-dark` | `#1a1a1a` | Near-black — custom element backgrounds (description boxes, cookie banner, sticky ATC, cart drawer). NOT used for body text — that's the admin-set colour. |
| `--color-mid` | `#6f6f6f` | Mid-grey — secondary text, muted labels, button hover backgrounds |
| `--color-light` | `#f5f5f5` | Off-white — dropdown backgrounds, filter surfaces, light card fills |
| `--color-white` | `#ffffff` | Pure white — text on dark backgrounds |
| `--color-sale` | `#d32f2f` | Red — sale pricing only, never decorative |
| `--color-footer-bg` | `#4d4d4d` | Charcoal — footer background |

**Rules:**
- Never hardcode hex values that have a matching token above.
- Body text colour, nav link colour, dropdown background, and header colours are set in Shopify admin > Themes > Customise > Colors — do NOT override these in custom.css unless explicitly correcting a bug. The admin values are documented in the `:root` comments.
- Gold (`--color-brand-yellow`) is the only accent colour. Do not introduce secondary accents.

---

## Border Radius

| Token | Value | Use |
|-------|-------|-----|
| `--radius-sm` | `5px` | Form inputs, small UI chips, dropdown elements |
| `--radius-md` | `10px` | Small cards, tags, thumbnails |
| `--radius-lg` | `20px` | **Standard text boxes and content cards** — rich text blocks, description containers, art story panels, about section, homepage collection cards. This is the site's primary card radius. |
| `--radius-xl` | `40px` | Hero feature elements, large image overlays |
| `--radius-pill` | `35px` | All buttons (primary, secondary, toggle) |

**Rules:**
- All content text boxes (description boxes, rich text panels, info cards) use `--radius-lg`.
- All buttons use `--radius-pill` — no exceptions.
- Form inputs and dropdowns use `--radius-sm`.
- Do not mix radius values within the same component group.

---

## Shadows

| Token | Value | Use |
|-------|-------|-----|
| `--shadow-sm` | `0 2px 5px rgba(0,0,0,0.2)` | Subtle lift — small cards, chips |
| `--shadow-md` | `0 4px 8px rgba(0,0,0,0.2)` | Standard card depth |
| `--shadow-lg` | `0 4px 20px rgba(0,0,0,0.4)` | Prominent panels, overlays |
| `--shadow-xl` | `0 6px 15px rgba(0,0,0,0.2)` | Product image cards |

---

## Typography

Fonts are set in Shopify admin and injected via `styles.css.liquid`. Do not change font families in `custom.css` without updating admin settings.

| Context | Font | Weight |
|---------|------|--------|
| Headings (h1–h4), nav | Montserrat | 600–700 |
| Body text, descriptions | Lato | 400 |
| Labels, uppercase tags | Montserrat | 700 + `letter-spacing: 0.1em` |

**Rules:**
- Uppercase labels always use `letter-spacing: 0.1em` minimum.
- Never use `font-size` smaller than `0.625rem` (10px).
- Line height for body copy: `1.7–1.8`. For headings: `1.1–1.3`.

---

## Buttons

All buttons use `--radius-pill`. There are two standard button types:

| Type | Class | Background | Text | Border |
|------|-------|------------|------|--------|
| Primary | `.button--primary` or `.button--primary-action` | `--color-dark` | `--color-brand-yellow` | none |
| Secondary | `.button--secondary` | transparent | dark | 1px solid |

**Rules:**
- The `.button--primary` class is globally overridden in custom.css to enforce dark+gold styling regardless of admin button colour setting.
- Every interactive toggle (e.g. "Read More", filter apply) must use pill radius and dark+gold colour scheme.
- Hover state: background shifts to `--color-mid`. Text colour does not change.
- Never create a button with a coloured background other than `--color-dark`, `--color-mid`, or `--color-brand-yellow`.

---

## Text Boxes / Content Cards

These rules apply to any dark-background content container (description boxes, rich text panels, info cards):

- **Background:** `--color-dark` (`#1a1a1a`)
- **Text:** `--color-light` (`#f5f5f5`) or `--color-white`
- **Border radius:** `--radius-lg` (20px) — always
- **Shadow:** `--shadow-md` unless nested inside another card (then none)
- **No coloured borders** — do not add accent-colour left borders or outlines to content boxes

---

## Dropdowns / Form Inputs

| Property | Value |
|----------|-------|
| Background | `#efefef` (slightly darker than `--color-light`) |
| Border | `1px solid rgba(0,0,0,0.15)` |
| Border radius | `--radius-sm` (5px) |
| Text | `--color-dark` |

---

## Spacing

No spacing tokens are defined yet — spacing is handled per-component. General rules:

- Section top/bottom padding: 16–60px depending on context (collection pages use 16px top to minimise gap after the banner)
- Card internal padding: `28px 32px` (desktop), `20px` (mobile)
- Gap between stacked cards/sections: `24px`

---

## What NOT to do

- Don't add coloured left-border accents to content boxes (breaks the established card style)
- Don't introduce new accent colours — gold is the only accent
- Don't use `border-radius` values that aren't in the token set above
- Don't hardcode colours that exist as CSS custom properties
- Don't set `font-family` without checking admin settings first
- Don't use `!important` except where overriding Flex theme specificity conflicts (always add a comment explaining why)
