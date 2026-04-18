# Lost Collective — Design Tokens

> Authoritative reference for every CSS custom property in the theme.
> Post-Phase-4 landscape (2026-04-18). Generated via the `design:design-system` skill.

This document is the canonical source of truth for where LC-rendered colour,
typography, spacing, and motion values come from. Any time you're asked "where
does colour X come from?" the answer is in one of the five sections below.

---

## 1. Admin-driven tokens

Tokens whose values come from `settings_data.json` via either Flex's own
`snippets/head.styles.*.liquid` or LC's `snippets/lc.css-tokens.liquid`.
Merchant changes propagate when Shopify recompiles `assets/theme.css`.

| CSS var | `settings.*` source | Flex/LC pipeline | Default | Consumed in |
|---|---|---|---|---|
| `--color-primary` | `button_primary_bg_color` | Flex `theme.css.liquid` compile-time interpolation | `#EBAC20` | `.button.button--primary`, `.footer__block.block__newsletter .newsletter-form button[type=submit]` |
| `--button-primary-text-color` | `button_primary_text_color` | Flex `snippets/head.styles.flex-legacy-settings-color.liquid:24` | `#ebac20` | Same as `--color-primary` |
| `--button-primary-bg-color-highlight` | `button_primary_bg_color--highlight` | Flex `theme.css.liquid` compile-time | `#ebac20` | `.button--primary:hover` pipelines |
| `--button-primary-text-color-highlight` | `button_primary_text_color--highlight` | Flex `snippets/head.styles.flex-legacy-settings-color.liquid:25` | `#2a2a2a` | `.button--primary:hover` pipelines |
| `--element-text-color--body` | `regular_color` | Flex `layout/theme.liquid:215` inline style | `#6f6f6f` | `--color-body-text` chain, any rule using `var(--color-body-text, #6f6f6f)` |
| `--element-text-color--heading` | `heading_color` | Flex `layout/theme.liquid:216` inline style | `#2a2a2a` | all `h1`–`h6` rules in Flex `theme.css` |
| `--color-header-bg` | `mobile_header_background` | LC `snippets/lc.css-tokens.liquid:16` | `#4d4d4d` | 3 mobile-header + announcement-bar rules in `custom.css` |
| `--color-footer-bg` | `footer_background` | LC `snippets/lc.css-tokens.liquid:19` | `#4d4d4d` | `.footer__content`, trust bar, footer-block rules (5 sites in `custom.css`) |
| `--color-body-text` | `regular_color` (via `--element-text-color--body`) | LC `assets/custom.css:72` `var()` chain | `#6f6f6f` | 20 rule bodies in `custom.css` (text colour, border colour on slate-toned UI) |

**Pipeline pattern.** Flex settings interpolate at compile time into `theme.css.liquid`
(resulting in a literal hex in the compiled `theme.css` asset). LC settings interpolate
at runtime inline via `snippets/lc.css-tokens.liquid` (re-evaluated on every page render,
so no recompile needed for LC-token changes).

**Recompile behaviour.** Shopify's `assets/theme.css` is compiled from `theme.css.liquid`
on save via the admin theme editor OR when `theme.css.liquid` itself is pushed. Settings
changes via `shopify theme push --only config/settings_data.json` **do NOT always trigger
recompile** — use `scripts/_force_theme_recompile.py` to verify the compiled asset reflects
the settings change (see section 2 below for the helper).

---

## 2. LC-owned tokens

Tokens declared by LC with values that merchants should NOT control.
Each has a justification inline in `assets/custom.css` `:root`.

| CSS var | Value | Location | Consumed in | Why LC-owned |
|---|---|---|---|---|
| `--color-brand-gold` | `#ebac20` | `assets/custom.css:68` | 49 sites — CTA hover, accent, logo box, edition chip, chevron hover, link hover | LC brand identity. Merchant cannot override. |
| `--color-dark` | `#1a1a1a` | `assets/custom.css:70` | Cookie banner, search popup, mobile sticky ATC, cart drawer, art description boxes, accordion headers | LC design ink. Distinct from admin heading_color — this is LC's dark surface, not a heading colour. |
| `--lc-surface-light` | `#f5f5f5` | `assets/custom.css:77` | `var(--color-light)` alias consumer chain (8 rule bodies) | Neutral light fill used across custom components. Coincidentally matches admin `dropdown_background` default but used in non-admin-controlled surfaces. |
| `--lc-surface-slate` | `#4d4d4d` | `assets/custom.css:78` | Available for future slate-toned LC components | Neutral dark fill. Available as a token so Phase 3+ custom components don't hardcode `#4d4d4d` literals. |
| `--color-light` | `var(--lc-surface-light)` | `assets/custom.css:79` | 8 rule bodies (compatibility alias for pre-Phase-1 selectors) | Back-compat: custom.css rule bodies written before Phase 1 reference `var(--color-light)`. This alias chains to the renamed `--lc-surface-light`. |
| `--lc-color-hover` | `var(--color-brand-gold)` | `assets/custom.css:82` | Available for future hover-state consistency | Unifies hover accent across LC components; always LC brand gold, not admin `link_hover_color` (merchant shouldn't break hover consistency). |
| `--color-twitter` | `#1da1f2` | `assets/custom.css:85` | Social share button rules | External brand colour. Twitter's trademark blue. |
| `--color-facebook` | `#3b5998` | `assets/custom.css:86` | Social share button rules | External brand colour. Meta's Facebook blue. |
| `--color-pinterest` | `#bd081c` | `assets/custom.css:87` | Social share button rules | External brand colour. Pinterest red. |
| `--color-email` | `#333333` | `assets/custom.css:88` | Email/mailto button rules | Generic email icon convention. |
| `--font-body` | `'Lato', sans-serif` | `assets/custom.css:91` | Fallback for body text font | LC body font. Admin `regular__font` drives the actual loaded font via Flex; this is a fallback. |
| `--font-heading` | `'Montserrat', sans-serif` | `assets/custom.css:92` | Fallback for heading font | LC heading font. Admin `heading__font` drives the actual loaded font via Flex; this is a fallback. |

---

## 3. Structural tokens

Non-colour tokens — spacing, radii, shadows, transitions. Never admin-controlled
because they represent internal layout rhythm, not merchant-configurable style.

| CSS var | Value | Location | Intent |
|---|---|---|---|
| `--radius-xs` | `3px` | `assets/custom.css:95` | Smallest border radius. Used on input borders, badges. |
| `--radius-sm` | `5px` | `assets/custom.css:96` | Small radius. Used on secondary buttons, chips. |
| `--radius-md` | `10px` | `assets/custom.css:97` | Medium radius. Default card corners. |
| `--radius-lg` | `20px` | `assets/custom.css:98` | Large radius. Marquee image corners, highlight boxes. |
| `--radius-xl` | `40px` | `assets/custom.css:99` | Extra-large radius. Hero-card corner treatments. |
| `--radius-pill` | `35px` | `assets/custom.css:100` | Pill shape. All primary/secondary buttons. Equals `button_primary_border_radius` admin default but structural by intent. |
| `--shadow-sm` | `0 2px 5px rgba(0, 0, 0, 0.2)` | `assets/custom.css:103` | Subtle lift. Card hover, dropdown panel. |
| `--shadow-md` | `0 4px 8px rgba(0, 0, 0, 0.2)` | `assets/custom.css:104` | Medium lift. Cart drawer, search popup. |
| `--shadow-lg` | `0 4px 20px rgba(0, 0, 0, 0.4)` | `assets/custom.css:105` | Heavy lift. Modal, overlay. |
| `--shadow-xl` | `0 6px 15px rgba(0, 0, 0, 0.2)` | `assets/custom.css:106` | Widest lift. Hero card over video. |
| `--transition-fast` | `0.2s ease-in-out` | `assets/custom.css:109` | Button state, dropdown open/close. |
| `--transition-slide` | `0.25s ease-in-out` | `assets/custom.css:110` | Drawer + mobile-menu slide. |
| `--transition-base` | `0.3s ease` | `assets/custom.css:111` | Default transition for unspecified properties. |

---

## 4. Deprecated tokens

Tokens that existed in prior LC code but were removed during the 2026 theme refactor.
Listed here so future contractors don't reintroduce them by accident.

| Former CSS var | Phase removed | Reason | Replacement |
|---|---|---|---|
| `--color-brand-yellow` | Phase 2 (commit `11a7970`) | Ambiguous naming — renamed for clarity | `--color-brand-gold` (same value, clearer intent) |
| `--color-mid` | Phase 1 (commit `dfb53ba`) | Duplicate of `--color-body-text` with different name | `--color-body-text` (now chains through admin `regular_color`) |
| `--color-sale` | Phase 1 (commit `dfb53ba`) | Unused — no `var(--color-sale)` consumer anywhere | None needed; if sale styling returns, use a semantic `--sale-accent` |
| `--color-white` | Phase 1 (commit `dfb53ba`) | Redundant with Flex's `snippets/head.styles.legacy-settings-color.liquid:109` which already declares it at `:root` | Reference Flex's version (no LC re-declaration) |
| `--color-facebook/twitter/pinterest` | NOT removed, see section 2 | Phase 1 audit flagged them but Phase 1 analysis showed snippet values differ — left as LC-owned | — |
| `--color-primary: var(--color-brand-gold)` override | Phase 4 (commit `61886bf`, formerly `custom.css:119`) | Hard-override that hid admin `button_primary_bg_color` from every primary button | Admin pipeline (Flex `theme.css.liquid` compile interpolation) now drives `--color-primary` |
| `.button.button--primary { background: var(--color-dark) }` | Phase 4 (commit `61886bf`, formerly `custom.css:1164`) | Secondary hard-override for the `.button--primary` selector specifically | Now reads `var(--color-primary)` + `var(--button-primary-text-color)` |
| `.newsletter-form button[type=submit] { background: var(--color-dark) }` | Phase 4 (commit `3470d03`, formerly `custom.css:1678`) | Another primary-button hard-override in the footer | Rewired to `var(--color-primary)` so admin propagates |
| `--color-footer-bg: #4d4d4d` in `:root` | Phase 4 (commit `19c7482`) | Static hex meant admin `footer_background` was silently ignored | Emitted by `snippets/lc.css-tokens.liquid` from `settings.footer_background` |
| `--color-header-bg: #4d4d4d` in `:root` | Phase 4 (commit `19c7482`) | Static hex with no admin concept (mobile header had no schema setting) | New schema setting `mobile_header_background` + `snippets/lc.css-tokens.liquid` emission |
| 171 additional tokens | Phase 1 (commit `a9a7cc1`) | Declared in Flex snippets but never consumed by any rule or Liquid interpolation | Deleted; see `audit/DEAD-TOKENS.txt` |

---

## 5. Cascade rules (when does what win?)

When two rules target the same property on the same element, who wins?

**Default: admin wins.**
Any token listed in section 1 takes its value from `settings.*`. Flex's pipeline
resolves the settings to CSS at compile time (Flex snippets) or at runtime (LC
`snippets/lc.css-tokens.liquid`). Custom stylesheets should read admin values
via `var(--token)` rather than hardcode literals.

**LC wins for brand identity.**
Tokens in section 2 — LC-owned — should never be overridden by admin. These
represent LC's brand (`--color-brand-gold`), design ink (`--color-dark`), and
product-specific surfaces (`--lc-surface-*`). If a merchant asks to change
these, the answer is "edit `custom.css`", not "change the theme editor."

**`!important` is allowed only in five categories** (Phase 3 C-4 keeper categories,
28 total real-code `!important` flags in `custom.css`, each carrying a
`/* WHY: */` annotation immediately above):

1. **defends against inline `style="..."` injected by Shopify section editor**
   — e.g. section-editor-rendered wrappers carrying layout inline styles.
2. **overrides third-party stylesheet** — Stape Server GTM, Klaviyo embed,
   Yotpo widget, Plyr video player, Flickity carousel, or any external app
   that ships CSS and runs after theme CSS loads.
3. **runtime class toggles on drawer/mobile nav/sticky/fixed elements** — rules
   that defend visual state against JS class flips (e.g. `z__jsMegaMenu.js`).
4. **Flex `{% style %}` block scoped to `#shopify-section-{id}`** — Flex emits
   section-scoped inline styles with `#id` specificity that beats class selectors.
   LC rules must either prefix with `#shopify-section-...` too or use `!important`
   with a WHY annotation pointing at the Flex section.
5. **desktop header dark-translucent design intent** (specific Phase 3 restored
   rule `html body .header { background-color: rgba(18,18,18,0.55) !important }`)
   — Flex's section-scoped header rule reads admin `header_background: #f5f5f5`
   which is LIGHT; LC design wants a dark translucent header over the hero video.
   Override kept with WHY annotation. Mobile header has its own admin setting
   now (`mobile_header_background`, Phase 4 MISSING-MOBILE-HEADER-BG).

Anything NOT in one of those five categories that carries `!important` is a bug —
either the rule was misclassified during Phase 3 and should be demoted (rewrite
with higher specificity), or the category list needs extending. Flag to Cowork
via HANDOFF and re-bucket.

---

## Operational notes

- **Canonical audit data:** `audit/IMPORTANT-INVENTORY.tsv` (Phase 3 output).
- **Dead-code corpus:** `audit/DEAD-TOKENS.txt`, `audit/DEAD-SELECTORS.txt`,
  `audit/DEAD-SETTINGS.txt`, `audit/DEAD-IMPORTANT.txt` (Phase 1 output; re-run
  `audit/_build_audit.py` before any future phase).
- **Fix plans:** `audit/PHASE4-FIX-PLAN.md` (current), `audit/REFACTOR-PLAN.md`
  (long-arc six-phase plan).
- **Tone of voice:** `docs/lost-collective-tov.md` — applies to admin setting
  labels/info as well as customer-facing copy.
- **Force-recompile helper:** `scripts/_force_theme_recompile.py` — use after
  admin-value changes to ensure `assets/theme.css` reflects the new values.
  Run: `op run --env-file=.env.tpl -- python3 shopify/scripts/_force_theme_recompile.py`.
