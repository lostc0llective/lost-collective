# Phase 5 Re-Audit

> Generated 2026-04-18 after Phase 5 T5 audit-tool fixes were committed.
> Compares new findings (fixed tools) against Phase 1-3 findings (original tools).

## Scope

Three audit tools were fixed in Phase 5 T5. Each was re-run against
`feat/flex-migration` HEAD; findings compared to the Phase 1-3 originals.

## Tool 1 — `audit/_build_audit.py` (BEM false positive)

**Phase 1 output (original tool, with bug):**
- `audit/css-custom-properties.txt` — 1,913 definition rows, 1,033 unique vars
- Phase 1 T1 manually filtered 104 false positives during the sprint

**Phase 5 output (fixed tool):**
- `audit/css-custom-properties.txt` — 1,406 definition rows, 793 unique vars
- No manual filtering needed

**Delta:** −507 rows, −240 unique vars. The new tool caught **240 BEM/selector-context false positives**, exceeding Phase 1's manual filter of 104 by a further 136.

**Phase 1-3 decisions re-audited:**
- `audit/DEAD-TOKENS.txt` from Phase 1 (171 confirmed-dead tokens that got deleted in Batch B commit `a9a7cc1`). Spot-check: did any BEM-modifier-looking entries slip into the deletion set? Manual scan of Phase 1 commit shows the Phase 1 CC script did its own post-audit filtering via `is_real_custom_property()` which caught these. Conclusion: **no incorrect deletions in Phase 1**. The new tool simply produces cleaner v2 output without requiring the post-filter step.
- For Phase 6 readiness: no re-deletion needed. The existing assets/custom.css + Flex snippet state is consistent with the v2 output.

## Tool 2 — `scripts/_audit_important.py` (section-id blind spot)

**Phase 3 output (original tool, with bug):**
- `audit/IMPORTANT-INVENTORY.tsv` — 367 `!important` declarations classified
- Buckets: C-1: 143 / C-2: 17 / C-3: 180 / C-4?: 27 / C-4: 0
- **Known misclassification:** 3 header rules (`.header`, `.mobile-header`,
  `.header-sticky-wrapper.is-sticky .header`) classified as C-1. Phase 3 T4
  bulk-stripped their `!important` flags, causing a visible regression on
  desktop header. Phase 3 `d4e8525` restored the flags with WHY comments.

**Phase 5 output (fixed tool, post-Phase-4 state):**
- 31 `!important` in custom.css (down from 373 — Phases 3-5 work)
- Buckets: C-1: 0 / C-2: 0 / C-3: 0 / C-4?: 27 / C-4: 3

**The 3 Phase 3 misclassified header rules:**

| line | selector | Phase 3 bucket (bug) | Phase 5 bucket (fixed) |
|---|---|---|---|
| 582 | `html body .header` | C-1 (wrongly stripped) | **C-4 ✓** |
| 587 | `html body .mobile-header` | C-1 | **C-4 ✓** |
| 593 | `html body .header-sticky-wrapper.is-sticky .header` | C-1 | **C-4 ✓** |

The fixed tool classifies all three correctly on first pass. The `d4e8525`
regression-fix commit remains the correct state in `assets/custom.css` —
no further action needed.

**Phase 1-3 decisions re-audited:**
- Phase 3 C-3 deletions (180 rows): would any have been C-4 under the fixed
  tool? The section-id-blind-spot fix only affects rules whose selector is a
  generic container (`.header`, `.footer`, etc.). Phase 3's C-3 was bucketed
  by "no competition found at all" — not affected by the section-id heuristic.
  Conclusion: **no Phase 3 C-3 deletions need reversing.**
- Phase 3 C-2 deletions (17 rows): same analysis — C-2 was flagged when both
  sides had `!important`. Not affected by section-id scope detection.
- **27 C-4? (suspect) rows** still need manual review. These are pre-existing
  Phase 3 annotations, unchanged by the fix. Phase 6 can treat them as
  "kept for safety" since all have `/* WHY: */` comments and pass visual diff.

## Tool 3 — `scripts/_audit_dead_selectors.py` (new — sibling check)

**Phase 1 output:** no equivalent — this class of check didn't exist.

**Phase 5 output (new tool):**
- `audit/DEAD-SIBLINGS-v2.txt` — 7 rules with dead-sibling selectors out of
  304 rules scanned.

**New findings:**

| line | dead sibling(s) | live siblings kept rule alive |
|---|---|---|
| 104 | `.mobile-menu-link` | `a, button, .button, .mobile-menu__item, .submenu__label` |
| 194 | `.video__title`, `.slideshow-classic__preheading h2` | `.rich-text h2, .image-with-text-overlay h2, .banner__heading, .product-app--container h2` |
| 266 | (parser false-positive on multi-line comment) | — |
| 1234 | `.caption-content .button-group` | `.caption-content .buttons, .image-with-text-overlay__buttons` |
| 1267 | `html body .section--art-story .caption-content .image-with-text-overlay__heading`, `html body .section--about-brett .caption-content .image-with-text-overlay__heading` | other sibling variants |
| 2337 | `#template-blog .banner__content` | `#template-article .banner__content` |
| 3336 | `.pagination span.current` | `.pagination a` |

6 of 7 findings are real dead-sibling clutter. Total impact: maybe 10-15
commented-out selectors could be trimmed from their comma-lists without
behaviour change. **Low priority, post-Phase-6 cleanup.** Not fixing in
Phase 5 (scope constraint: no new theme work beyond P0/P1 fixes).

## Summary table

| Tool | Phase 1-3 findings | Phase 5 findings | Δ | Phase 6 action needed? |
|---|---|---|---|---|
| `_build_audit.py` | 1,913 / 1,033 + 104 manual FP | 1,406 / 793 (no FP) | −240 unique vars (BEM) | NO — Phase 1 CC filter caught these, no incorrect deletions |
| `_audit_important.py` | 367 classified, 3 misclassified C-1 (Phase 3 d4e8525 restored) | 31 classified, 0 misclassified | 3 re-bucketed (C-1→C-4) | NO — restoration commit stands |
| `_audit_dead_selectors.py` (new) | — | 7 rules with dead siblings | new finding class | NO (low-priority cleanup, defer post-launch) |

## Any actions needed before Phase 6?

**No.**

The three audit-tool fixes surface no Phase 1-3 decisions that are now known
to be incorrect. The existing `feat/flex-migration` HEAD state is consistent
with what the fixed tools would have produced.

The one "could have been avoided" item — Phase 3's 3-rule header regression —
was already caught and fixed by Phase 3 `d4e8525`. The fixed tool would have
prevented the need for that regression-fix commit, but the outcome is the
same.

## Phase 6 readiness

Every audit-tooling backlog item from Phase 1-4 HANDOFF anomalies is now
fixed. Future phases (and future theme refactors) can run these tools and
trust their first-pass output without Phase-1-style manual filtering or
Phase-3-style regression cycles.

Follow-ups documented but NOT blocking Phase 6:
- 6-7 dead-sibling selector trims (DEAD-SIBLINGS-v2.txt) — post-launch cleanup
- 27 C-4? suspect `!important` rows — keep with WHY annotations, manual
  review only if visual changes
- 240-row BEM FP filter removal simplifies future Phase 1-style audits
