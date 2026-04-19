# Phase 7 Sprint B — Task B8 decision note

**Date:** 2026-04-19
**Author:** CC
**Status:** Descoped per Brett's mid-sprint direction.

## What B8 originally scoped

Decision 6 in HANDOFF.md L2239–L2253 described a PDP interaction surface uplift:

- 4px border-radius across every PDP button (variant swatches, ATC, notify-me, size-guide, accordion triggers).
- ATC hover: `border-color: #EBAC20`, `translateY(-1px)`, 200ms ease-out. Active: `transform: scale(0.99)`, 100ms.
- Page-load reveal on `.product-main-column`: opacity 0 → 1 over 400ms after the product image loads.
- Accordion uplift: replace Flex's heavy chevron and box border with hairline rules, 12px gold chevron, small-caps serif label, 200ms rotation, hover background tint.

## What changed mid-sprint

Brett intervened at the start of B6:

> "i do not want you introducing new fonts an styles inconsistent with the global theme settings, disregard the request to go nuts here, just get the layout looking clean and consistent with the rest of the theme. change the button styling so that it matches the rest of the site."

This direction supersedes Decision 6. The implication: **Decision 6 is not aligned with the global theme** because:

- Site CTAs use `--radius-pill` (35px), not 4px.
- Site does not use page-load opacity reveals.
- Site uses Lato/Montserrat, not serif-italic editorial labels.
- Existing accordion (`snippets/collapsible-row.liquid`) is already on brand (dark fill, white text, plus-icon trigger) and merchants control it via standard Flex blocks.

## What B8 actually delivers

Nothing net-new. The cleanup pass committed in B6 already addressed the parts of Decision 6 that align with Brett's direction:

- Variant swatches use `--radius-md` (10px), white surface, dark selected fill — consistent with the theme's form treatment.
- Sticky ATC button uses `--radius-pill` to match the site's primary button shape.
- Focus-visible rings already exist on swatches via B2 CSS section 44 (`outline: 2px solid var(--color-brand-gold)`).
- All Sprint B fonts are now `var(--font-body)` Lato — no Georgia, no italic editorial labels.

## Rationale for descoping

Brett's "consistent with the rest of the site" rule outranks Cowork's spec. The HANDOFF instruction "Six decisions are LOCKED — do not reopen" is overridden by direct user instruction (per `superpowers:using-superpowers`: "User's explicit instructions" sit above skills, plans, and prior context). B8 in its original form would re-introduce the inconsistencies Brett asked to remove.

## What's deferred

If Brett later wants the page-load reveal or accordion restyle, those land cleanly as a single later commit:

- Page-load reveal: add `.product-main-column { opacity: 0; transition: opacity 400ms ease-out } .product-main-column.is-loaded { opacity: 1 }` + `assets/z__lcPdpReveal.js`. Probably worth A/B testing before shipping.
- Accordion uplift: requires editing `snippets/collapsible-row.liquid` markup. Should be paired with a customer Apple/UX review.

Both can ship as Sprint D items if desired.
