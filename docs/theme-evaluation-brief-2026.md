# Theme Evaluation Brief — Lost Collective
**Prepared:** 2026-04-06  
**Decision owner:** Brett Patman  
**Options:** Flex v5.2.1 (status quo) · OS 2.0 upgrade · Custom build

---

## Current state: Flex v5.2.1

**Out of the Sandbox** — purchased theme, heavily customised.

### What's working
- All customisations from the April 2026 audit are live and stable: edition scarcity bar, faceted filtering, price range display, collection breadcrumbs, variant swatches, image lazy loading, blog CTA snippet, article schema
- Judge.me, Instafeed, Klaviyo, Stape GTM all integrated via app blocks
- Multi-currency works correctly via Shopify Payments
- Performance: Flex loads fast for a feature-heavy theme. Lazy loading improvements done this week help
- No known critical bugs

### What's limiting
- **Flex is not an Online Store 2.0 theme.** App blocks are limited — some sections can't host app blocks, which is why Instafeed required a `<head>` block workaround
- Flex v5.x is no longer actively developed by Out of the Sandbox. Last meaningful update was 2024. No OS 2.0 migration path announced
- Section-specific customisation requires editing `.liquid` files directly — can't use the visual theme editor for custom sections
- No native metafield display in theme editor (requires liquid code)
- The "Copy of Lost Collective Live" theme name is a leftover from an old duplicate — cosmetically messy but functionally fine

### Risk of staying
- **Low-medium.** Flex works. Customisations are stable. No Shopify deprecation of Flex themes imminent. But as Shopify's OS 2.0 ecosystem matures, third-party apps increasingly assume OS 2.0 compatibility. Some future app integrations may be blocked or require workarounds.

---

## Option A: Stay on Flex v5.2.1

**Effort:** None  
**Cost:** $0  
**Risk:** Low-medium (see above)  

**Verdict:** Viable for 12–24 months. All audit work is complete. The only genuine limitation is app block flexibility, which has been worked around on a case-by-case basis. If no new apps requiring OS 2.0 blocks are needed, this is the lowest-risk path.

---

## Option B: Migrate to an OS 2.0 Theme

### What OS 2.0 gives you
- Full drag-and-drop in theme editor for all sections and app blocks
- Native metafield display in theme editor (no liquid coding for simple changes)
- Better app ecosystem compatibility going forward
- Active development and security updates from theme vendors

### Recommended OS 2.0 themes for fine art / photography stores

| Theme | Cost | Notes |
|-------|------|-------|
| **Prestige** (Maestrooo) | $380 AUD one-off | Best-in-class for premium photography/art stores. Clean, typography-forward, large image support. Strong metafield support. Most similar aesthetic to current Lost Collective look. |
| **Impulse** (Archetype) | Free | Widely used, solid OS 2.0, but more general retail. Less refined for art/print positioning. |
| **Cascade** (Shopify) | Free | Minimalist, editorial. Photography-friendly. Shopify-native so very stable, but limited customisation ceiling. |
| **Symmetry** (Eight Themes) | $380 AUD one-off | Fashion/lifestyle. Works for art but not optimised for it. |

### Migration effort
Migrating from Flex to any OS 2.0 theme is a **full rebuild**. Not an upgrade — a rewrite.

Items that would need to be rebuilt:
- Edition scarcity bar (`product__form.liquid`)
- Price range display (`product.liquid`)
- Variant swatch CSS grid layout (`options-radios.liquid`)
- Image lazy loading and variant-change animations
- Blog CTA snippet injection (`article__main.liquid`)
- Article schema snippet (`article__main.liquid`)
- Back-to-collection link (`product.liquid`)
- All `templates/*.json` section and block ordering

**Estimated rebuild time:** 20–40 hours of Claude-assisted work, plus testing. All custom code is documented and recoverable — migration is doable, not trivial.

**Cost:** Theme purchase ($380 for Prestige) + rebuild time

**Risk:** Medium. Migration introduces regression risk. Thorough staging testing required before going live.

---

## Option C: Custom Build

**Not recommended at this stage.**

A custom Shopify theme built from OS 2.0 primitives gives maximum control but:
- Requires ongoing developer maintenance
- No vendor support
- Theme Kit / GitHub Actions CI/CD is already complex enough
- The store's needs are well-served by a good commercial theme

Only warranted if Lost Collective outgrows what any commercial theme can offer (e.g., custom checkout flows, highly specialised product configurators).

---

## Recommendation

**Short term (now–12 months):** Stay on Flex v5.2.1. All audit items are complete. The theme is stable, customisations are solid, and migration risk outweighs the benefit right now.

**Medium term (12–18 months):** Evaluate migrating to **Prestige** when either:
1. A new app integration is blocked by Flex's non-OS 2.0 architecture, OR
2. Shopify announces meaningful deprecation pressure on non-OS 2.0 themes, OR
3. A redesign / brand refresh is planned anyway

When migration happens, rebuild on staging first. All current customisations are documented and can be ported.

---

## Decision required from Brett

| Question | Options |
|----------|---------|
| Stay on Flex for now? | Yes / No |
| If migrating: which theme? | Prestige ($380) / Cascade (free) / Other |
| Timeline for migration (if yes)? | Now / Later this year / When triggered by a specific need |
