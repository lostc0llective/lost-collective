# Phase 4 Fix Plan — admin-CSS wiring restoration

Generated 2026-04-18 at feat/flex-migration @ 45d42aa. Reconciles CONFLICTS.md
A-series findings against current HEAD after Phases 0-3. Sprint's A1/A5/A6
framing is used here (not CONFLICTS.md's original numbering — sprint is
authoritative for Phase 4 scope).

| id | current_state | intended_state | pre_flight_admin_value | override_to_delete | wiring_action | verification |
|---|---|---|---|---|---|---|
| **A1** | Admin `button_primary_bg_color: #2a2a2a` is hidden by `custom.css:119` (`--color-primary: var(--color-brand-gold)` → resolves to `#EBAC20`). Every primary button renders gold regardless of admin. | Admin `button_primary_bg_color` drives primary button colour site-wide. LC override deleted. Admin value set to `#EBAC20` so visual at moment of deletion is unchanged. | `#EBAC20` set in admin **before** deleting the override (Task 2 two-commit sequence) | `assets/custom.css:119` | `delete-override` | Task 6 smoke test 3.0 — change admin value to `#0070F3` (Vercel blue), verify 5 button locations propagate, revert |
| **A5** | Admin `footer_background: #4d4d4d` exists; `custom.css:73` declares static `--color-footer-bg: #4d4d4d` that happens to match. Values aligned by coincidence, not by design — admin-change propagation is silent no-op. | `--color-footer-bg` interpolates from `settings.footer_background` via `snippets/lc.css-tokens.liquid`. Admin change propagates. | `#4d4d4d` already matches admin, no pre-flight change needed. | `assets/custom.css:73` (moves to snippet with Liquid interpolation) | `delete-then-rewire` | Task 4 verification — change admin `footer_background` to magenta, push + recompile, footer updates on staging; revert. |
| **A6** | Admin `header_background: #f5f5f5` exists; `custom.css:114` declares static `--color-header-bg: #4d4d4d` that **differs** from admin. The LC token drives the **mobile** header + announcement bar via three rules; the desktop header rule (Phase 3 commit `d4e8525`) uses `rgba(18,18,18,0.55) !important` and does NOT use this token. Calling this a straight admin-wire is wrong — the desktop and mobile headers have different design intents. | Split the concern: admin `header_background` continues to drive **desktop** (via the rebuilt Phase 3 rule). Add `mobile_header_background` as a new setting (MISSING-MOBILE-HEADER-BG below). The current `--color-header-bg` token becomes admin-driven from `mobile_header_background`. | `#4d4d4d` (sampled from current visual) for the new `mobile_header_background` admin setting | `assets/custom.css:114` (moves to snippet; rebinds to `settings.mobile_header_background`) | `add-schema-setting` + `add-liquid-snippet` + `delete-then-rewire` | Task 3 test — add admin setting, change to coral `#FF6B6B`, verify mobile header turns coral on staging, revert. |
| **MISSING-MOBILE-HEADER-BG** | Schema has no `mobile_header_background`. Mobile header colour is purely LC-hardcoded via `--color-header-bg`. Merchant has no control surface for it. | New schema setting in the "Header" group with `type: color`, `default: #4d4d4d`, descriptive label following ToV. Wired through the Liquid snippet to `--color-header-bg`. | `#4d4d4d` (current visual baseline) | n/a — wiring missing entirely | `add-schema-setting` + `add-liquid-snippet` | Task 3 admin-propagation test (same as A6) — confirms the new setting appears in theme editor AND changes the rendered mobile header. |

## Reconciliation notes against CONFLICTS.md

- CONFLICTS.md's original **A6** was about `link_hover_color` vs gold unification, NOT header background. The sprint re-purposed A6 to mean "desktop header background" because CONFLICTS.md's pre-refactor header-background finding landed under A5 in the original audit. Both concerns are valid — link hover + gold unification is deferred to Phase 5+ as it's part of the broader design-token consolidation in Task 5.
- CONFLICTS.md's original **B6** (`--color-mid` / `--color-body-text` collapse) and **B7** (`--color-primary` override) were resolved in Phase 1 (B6) and are being resolved now in Phase 4 A1 (B7 — this fix plan's A1 is the B7 from CONFLICTS).

## Order of operations

1. **T2** A1 two-commit sequence: pre-flight admin to `#EBAC20` → delete `custom.css:119` → verify buttons still gold, now admin-driven.
2. **T3** MISSING-MOBILE-HEADER-BG: add schema + data default + snippet wiring. Verify admin propagates mobile-header change.
3. **T4** A5 + A6: move `--color-footer-bg` and `--color-header-bg` declarations out of `:root` into `snippets/lc.css-tokens.liquid` with Liquid interpolation from `settings.footer_background` and `settings.mobile_header_background` respectively.
4. **T5** Walk remaining LC colour tokens in `:root`; migrate any that represent merchant-controllable concepts to the same snippet.
5. **T6** Smoke test 3.0 — the validation of the original complaint.

Every task verification is staging-only. Production (`193859780774`) is not touched until Phase 6.

## Out of scope for Phase 4

Per the sprint's "out of scope" list, none of these block Phase 4 but one may surface and needs flagging:

- Audit-tool bugs (`_audit_important.py` C-4 blind spot, `_build_audit.py` BEM false positive, dead-selector sibling check) — Phase 5 backlog.
- `vendors.js` instant.page dedup — Flex upstream, separate sprint.
- Shopify asset-recompile lag root cause — mitigated in T7 Part B via `scripts/_force_theme_recompile.py`.
