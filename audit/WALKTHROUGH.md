# How your theme's settings actually work

> A teaching piece for Brett, written 2026-04-18.
> Read this before or alongside `CONFLICTS.md` and `REFACTOR-PLAN.md`.
> No jargon you don't need. Real examples from your actual theme.

## The short version

Your theme has two systems fighting over who controls visual style. One of them is Flex's proper design system, driven by admin settings. The other is a set of CSS custom properties declared in `assets/custom.css` that re-define the same things using hardcoded values. When they agree (they mostly do, today), the site looks fine. When you touch admin, only half the theme hears you. That's why "I change it in admin and nothing happens" is a recurring pattern.

This walkthrough explains how the proper system works, what your custom layer is doing, and the five different ways the two systems collide.

---

## Part 1 — How Flex's design system is supposed to work

Shopify themes have a settings pipeline. Flex follows it properly. The pipeline has five stages, and each stage has a single job.

### Stage 1 — The schema (`config/settings_schema.json`)

This file defines *what settings exist*. It's the blueprint. A setting in the schema looks like:

```json
{
  "type": "color",
  "id": "button_primary_bg_color",
  "label": "Primary button background",
  "default": "#2a2a2a"
}
```

Four things: a type (color, text, range, select…), an id (the name Liquid uses to read it), a human label (what the theme editor shows), and a default. The schema is the contract. If a setting is in the schema, merchants can change it in the theme editor.

Your schema has 285 settings across groups like Colors, Typography, Layout, Buttons, Cart, etc. You can see the flat list in `audit/settings-schema-flat.json`.

### Stage 2 — The data (`config/settings_data.json`)

This is what the merchant (you) has actually *chosen* for each setting. Every time you save in the theme editor, Shopify writes your values here. It looks like:

```json
"button_primary_bg_color": "#2a2a2a",
"regular_color": "#6f6f6f",
"heading_color": "#2a2a2a",
...
```

The flat version of your current data is in `audit/settings-data-flat.json`.

### Stage 3 — Liquid reads the data

When Shopify renders a page, Liquid templates can access any setting via `{{ settings.setting_id }}`. For example, `layout/theme.liquid` contains this block (around line 180-280):

```liquid
<style>
  :root {
    --color-primary: {{ settings.button_primary_bg_color }};
    --element-text-color--body: {{ settings.regular_color }};
    --element-text-color--heading: {{ settings.heading_color }};
    --element-button-radius: {{ settings.button_primary_border_radius }}px;
    --element-text-font-family--heading: {{ settings.heading__font.family }}, ...;
    --element-text-font-size--heading-lg: {{ settings.heading_size }}px;
    ...
  }
</style>
```

This is the bridge. The Liquid template writes your admin values into CSS custom properties. The output on the rendered page looks like:

```css
:root {
  --color-primary: #2a2a2a;
  --element-text-color--body: #6f6f6f;
  --element-text-color--heading: #2a2a2a;
  --element-button-radius: 35px;
  --element-text-font-family--heading: Montserrat, ...;
  --element-text-font-size--heading-lg: 27px;
}
```

Those custom properties are now available to every stylesheet loaded on the page.

### Stage 4 — Flex's stylesheets consume the properties

Flex's CSS doesn't use hardcoded hex values. It references the custom properties defined in Stage 3:

```css
.button--primary {
  background-color: var(--color-primary);
  color: var(--color-primary-contrast);
  border-radius: var(--element-button-radius);
}

h1, h2, h3, h4, h5, h6 {
  color: var(--element-text-color--heading);
  font-family: var(--element-text-font-family--heading);
}
```

Because the stylesheet reads the custom properties, any change to the admin setting flows through Stages 1-4 and takes effect immediately. That's the design.

### Stage 5 — Section-level overrides (local scope)

Some sections need to override a global setting for just that one section — a dark-themed hero that needs white text even though the global body text is black. Flex does this by writing a `{% style %}` block inside the section file that scopes the override:

```liquid
{% style %}
  #shopify-section-{{ section.id }} {
    --element-text-color--body: #ffffff;
  }
{% endstyle %}
```

Now inside that one section, body text is white. Outside it, the global admin setting still wins. This is the right way to do localised overrides.

### The whole pipeline in one picture

```
Admin theme editor
    |
    v
config/settings_schema.json   (what settings exist)
    |
    v
config/settings_data.json     (what values merchant chose)
    |
    v
layout/theme.liquid           ({% style %} block reads settings,
    |                            writes CSS custom properties)
    v
CSS custom properties at :root
    |
    v
Flex stylesheets              (rules reference var(--name))
    |
    v
Rendered page
```

That's Flex working correctly.

---

## Part 2 — What `assets/custom.css` does instead

`assets/custom.css` is 4,360 lines of stylesheet added to Flex over time. It opens with a table of contents (42 sections) and then a `:root` block (lines 56-120) that **declares its own custom properties with hardcoded hex values**:

```css
:root {
  --color-brand-yellow: #ebac20;
  --color-dark:         #1a1a1a;
  --color-mid:          #6f6f6f;
  --color-light:        #f5f5f5;
  --color-white:        #ffffff;
  --color-body-text:    #6f6f6f;
  --color-footer-bg:    #4d4d4d;
  ...
}
```

And most importantly, at line 119:

```css
--color-primary: var(--color-brand-yellow);
```

This is where it goes wrong. `--color-primary` was already set in Stage 4 of the proper pipeline, driven by the admin setting `button_primary_bg_color`. By re-declaring it at `:root` in `custom.css`, the custom stylesheet wins (same specificity, later in the cascade), and `--color-primary` is now `#ebac20` everywhere — regardless of what you choose in admin.

Rules throughout `custom.css` then reference these local tokens:

```css
.custom-something {
  color: var(--color-mid);        /* = #6f6f6f, hardcoded */
  background: var(--color-light); /* = #f5f5f5, hardcoded */
}
```

Because these local tokens re-read hardcoded values, not admin settings, the two systems drift any time you touch the theme editor. That drift is the source of the conflicts in `CONFLICTS.md`.

---

## Part 3 — When admin should win

**Rule of thumb:** admin wins whenever the concept is something merchants should be able to change without editing code. That includes:

- All top-level colours (body text, heading, links, primary button, footer bg)
- All typography (font families, sizes, letter spacing, line heights)
- All spacing/sizing tokens that have a sensible merchant-controlled default (button border radius, image corner radius)
- Any "show/hide" toggle (announcement bar, locale selector, newsletter popup)
- Any merchant-written string (search placeholder, footer link labels, button labels)

If the concept belongs in that list, the stylesheet should reference the Flex-provided CSS var, not re-declare it. If you need a fallback, use CSS var fallback syntax:

```css
color: var(--element-text-color--body, #6f6f6f);
```

That reads "use the Flex var; if it's not defined for some reason, fall back to #6f6f6f".

---

## Part 4 — When CSS should win

**Rule of thumb:** CSS wins when the concept is something merchants should *not* be able to break, or when it's context-specific enough that exposing it in admin would clutter the editor without improving merchant control. That includes:

- Social brand colours (Twitter blue, Facebook blue) — these are the real colours owned by those brands, no merchant should override them.
- Very specific UI states (a particular modal's shadow, one section's micro-animation timing).
- Spacing/transitions tied to a designed component's internal rhythm.
- Anything that takes more than one value to work right (e.g. a gradient, a multi-stop keyframe).

These should live in a *local* `:root` block or inside a scoped selector — but they should never re-declare a name that the Flex pipeline already owns. That's what causes the cascade war.

If you must have a CSS-only custom property, give it a clear name (`--lc-newsletter-popup-shadow`), prefix it with something LC-specific (`--lc-*`), and put it somewhere other than `:root` if possible (scope it to the section or component that uses it).

---

## Part 5 — The five conflict types, with real examples from your theme

### Type A — Dead admin settings

The setting exists in admin, you set a value, nothing happens — because custom.css overrides it.

**Example from your theme:** `button_primary_bg_color` is set to `#2a2a2a` (dark grey) in admin. But `custom.css:119` re-declares `--color-primary: var(--color-brand-yellow)` which is `#ebac20` (gold). Every primary button is gold regardless of what you set admin to.

**Fix:** delete the custom.css override line, change admin to `#ebac20` if you want gold buttons. The setting becomes live again.

### Type B — Duplicate definitions

The same token is defined in two places, usually with the same value today. Nothing breaks — until one changes and the other doesn't.

**Example:** `--color-sale: #d32f2f` is defined in both `custom.css:71` AND in Flex's own legacy-settings snippet. Neither is used anywhere (the token is dead, see DEAD-CODE.md), but if someone adds a reference and then later updates one definition, the other silently drifts.

**Fix:** delete one. If the value is provided by Flex, Flex's version wins.

### Type C — `!important` inflation

378 `!important` declarations in custom.css. Most defend against Flex sections that inject their own `{% style %}` blocks with `#section-id`-scoped rules (which beat class selectors on specificity). The `!important` flag tells the cascade "no matter what specificity, I win".

**Example:** `custom.css:150` has `font-family: Montserrat, 'Montserrat Fallback', sans-serif !important;` on `.navbar-link, .header__link, h1, h2, h3, h4`. Admin already sets this via `heading__font`. The `!important` is defending against nothing specific — it's an artefact of someone debugging a one-off issue and leaving the flag in.

**Fix:** rewrite the rule to include the section selector (`#section-header .header__link`) for higher specificity, drop `!important`. Or just drop `!important` and see what breaks — usually nothing.

### Type D — Hardcoded values that should reference vars

Hex values typed directly into custom.css rules instead of referencing a token.

**Example:** 9 rules in custom.css contain the literal `#4d4d4d`. Ten admin settings also hold `#4d4d4d`. If you change the admin value, those 9 rules don't update. They're coupled by coincidence, not by design.

**Fix:** replace every `#4d4d4d` in custom.css with `var(--element-text-color--body, #4d4d4d)` (or whichever Flex var is semantically right). The hex becomes a fallback; admin drives the value.

### Type E — Device-split overrides

Mobile behaves differently from desktop, and the override is hardcoded instead of admin-driven.

**Example:** `header_background` is set to `#f5f5f5` (near-white) in admin for desktop. But mobile media queries in custom.css force the header to `#4d4d4d` (dark grey). The admin setting is lying — it says "header is light" but mobile shows dark.

**Fix:** either expose a `mobile_header_background` admin setting and wire it through Liquid (`{{ settings.mobile_header_background }}` -> `--color-header-bg-mobile`), or hardcode the mobile value inline and delete the misleading `--color-header-bg` token. Currently you have the worst of both.

---

## Part 6 — Five rules to follow from here on

1. **If it's a colour, font, or size that a boutique agency would put in the theme editor, put it in the theme editor.** Any new token you introduce should have a matching admin setting unless there's a specific reason not to.
2. **Never redefine a Flex token at `:root` in custom.css.** If you need to change how a Flex token looks, change the admin setting that feeds it. If you need to override it locally, scope the override to a selector (`.my-section { --color-primary: ...; }`).
3. **Prefix your own tokens with `--lc-*`.** Makes it obvious at a glance whether a var is yours or Flex's. Grep becomes instant.
4. **`!important` is a debt instrument, not a tool.** Every `!important` you write is a promise to revisit it later. Comment *why* it's there next to it. Remove it the moment the original reason evaporates.
5. **When admin and CSS disagree, admin wins by default.** The exception is a brand-colour constant (Twitter blue) or a component-internal style (modal transition timing) where merchant control isn't the point.

---

## Part 7 — What "boutique agency quality" means for this theme

A boutique Shopify agency wouldn't ship a theme with 378 `!important` declarations, two parallel colour systems, or admin settings that silently do nothing. They also wouldn't ship a theme with zero custom CSS — your store has real custom functionality (category grid, collection series layout, newsletter popup with Lost Collective voice) that deserves polished code. The goal isn't to delete everything custom; it's to make the custom stuff look like someone who respects both the merchant and the next developer wrote it.

Concretely, after `REFACTOR-PLAN.md` phases 1-4:

- `custom.css` drops from 4,360 lines to ~3,800-4,000 lines (dead code gone)
- `!important` count drops from 378 to ~80-120 (only the genuinely needed ones, each commented)
- Admin settings drive rendered appearance end-to-end (you change `link_hover_color`, links hover that colour)
- The `:root` block in custom.css contains only LC-specific tokens (spacing, shadows, transitions, social brand colours) — maybe 20 lines total
- Every hardcoded hex is either referenced via a var or commented with why it's local (`/* LC newsletter popup shadow — not admin-configurable by design */`)

That's the shape of "boutique agency" for a Flex theme with LC customisation.

---

## Where to next

Read `CONFLICTS.md` for the specific A1-A6 / B1-B7 / C / D / E issues found in your theme. Read `REFACTOR-PLAN.md` for the phased plan to fix them. `DEAD-CODE.md` is the shopping list for what to delete in Phase 1.

When CC executes each phase, it will work from those three documents plus the CC prompt Cowork writes at the bottom of `HANDOFF.md`.
