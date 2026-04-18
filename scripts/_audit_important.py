#!/usr/bin/env python3
"""
Phase 3 inventory: classify every !important in assets/custom.css.

Writes audit/IMPORTANT-INVENTORY.tsv. Buckets:
    C-1  Selector specificity war (fighting a more-specific Flex rule)
    C-2  !important vs !important (both sides flagged)
    C-3  Defends nothing (no competing rule at any specificity)
    C-4  Genuine override (inline style=, third-party injection, runtime class)

Algorithm:
  1. Locate every `!important` occurrence in custom.css (after comment-stripping).
  2. For each occurrence, walk BACKWARD to extract the property/value declaration
     and the enclosing rule's selector (innermost non-@ selector).
  3. Pre-scan Flex files once to build { property: [(path, line, tokens, is_imp), ...] }.
  4. For each LC !important, intersect selector class/id tokens with competing rules.

Sibling to audit/_build_audit.py. Do not touch that file (BEM false-positive fix
is on Phase 5 backlog).
"""

import re
import sys
import time
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parent.parent
CUSTOM_CSS = ROOT / "assets" / "custom.css"
AUDIT = ROOT / "audit"
OUT = AUDIT / "IMPORTANT-INVENTORY.tsv"

COMP_GLOBS = [ROOT / "assets" / "theme.css.liquid", ROOT / "assets" / "base.typography.css"]
for p in (ROOT / "assets").glob("*.css"):
    if p.name != "custom.css" and p not in COMP_GLOBS:
        COMP_GLOBS.append(p)
for p in (ROOT / "snippets").glob("*.liquid"):
    COMP_GLOBS.append(p)
for p in (ROOT / "layout").glob("*.liquid"):
    COMP_GLOBS.append(p)

C4_SUSPECT_PROPS = {"display", "visibility", "position", "z-index", "pointer-events",
                    "opacity", "transform", "overflow"}


def strip_comments(css: str) -> str:
    out = list(css)
    i, n = 0, len(css)
    while i < n - 1:
        if css[i] == "/" and css[i + 1] == "*":
            j = css.find("*/", i + 2)
            if j < 0:
                j = n
            for k in range(i, min(j + 2, n)):
                if out[k] != "\n":
                    out[k] = " "
            i = j + 2
        else:
            i += 1
    return "".join(out)


def tokens(sel: str):
    toks = set(re.findall(r"\.[a-zA-Z0-9_-]+|#[a-zA-Z0-9_-]+", sel))
    return {t.lower() for t in toks if len(t) >= 3}


def line_of(css: str, offset: int) -> int:
    return css.count("\n", 0, offset) + 1


def extract_decl_around(css: str, imp_offset: int):
    """
    Given the offset of `!important` start, walk back to find property:value.
    Returns (property, value, decl_start) or None if parse fails.
    """
    # Walk back to find the previous ; or { that starts this declaration
    start = imp_offset - 1
    while start > 0 and css[start] not in ";{":
        start -= 1
    decl = css[start + 1:imp_offset].strip()
    m = re.match(r"^([a-zA-Z-]+)\s*:\s*(.+?)$", decl, flags=re.S)
    if not m:
        return None
    prop = m.group(1).strip().lower()
    value = m.group(2).strip()[:120]
    return prop, value, start + 1


def extract_selector_for(css: str, imp_offset: int) -> str:
    """
    Walk back from imp_offset to find the nearest unmatched `{`.
    The selector is the text between the `}` (or start-of-file) and that `{`.
    If the enclosing rule is @media / @supports, skip up one level.
    """
    depth = 0
    i = imp_offset - 1
    opens = []  # positions of unmatched `{`
    while i >= 0:
        c = css[i]
        if c == "}":
            depth += 1
        elif c == "{":
            if depth == 0:
                opens.append(i)
                # Keep walking to pick up outer context, so we can identify @media wrappers
            else:
                depth -= 1
        i -= 1

    if not opens:
        return "(root)"

    # Innermost open brace is the first in `opens` (we walked backward)
    for brace_pos in opens:
        # Selector is text between the previous delimiter (`}` or `{`) and this `{`
        prev_close = css.rfind("}", 0, brace_pos)
        prev_open = css.rfind("{", 0, brace_pos)
        cut = max(prev_close, prev_open)
        sel_text = css[cut + 1:brace_pos] if cut >= 0 else css[:brace_pos]
        sel_text = re.sub(r"\s+", " ", sel_text).strip()
        # If this is an @-rule wrapper, skip to the enclosing rule's selector
        if sel_text.startswith("@"):
            continue
        return sel_text[:400] or "(root)"
    return "(at-root)"


def build_competition_index():
    """Parse Flex files' decls into { property: [(path, line, tokens, is_imp, sel)] }."""
    idx = defaultdict(list)
    DECL_IMP_RE = re.compile(r"([a-zA-Z-]+)\s*:\s*[^;{}]+?(!\s*important)?\s*(?=[;}])")
    for f in COMP_GLOBS:
        if not f.exists():
            continue
        try:
            raw = f.read_text(errors="ignore")
        except Exception:
            continue
        # Strip liquid tags to reduce regex confusion
        clean = re.sub(r"\{%[^%]*%\}|\{\{[^}]*\}\}", " ", raw)
        stripped = strip_comments(clean)
        rel = str(f.relative_to(ROOT))
        # Walk body-by-body: find every `}` closing block, collect rules
        # For performance, iterate top-level blocks naively.
        # Split into rule-bodies by brace depth-1 parsing
        depth = 0
        body_start = None
        sel_start = 0
        n = len(stripped)
        for i, c in enumerate(stripped):
            if c == "{":
                if depth == 0:
                    sel_text = stripped[sel_start:i].strip()
                    sel_text = re.sub(r"\s+", " ", sel_text)[:200]
                    body_start = i + 1
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0 and body_start is not None:
                    body = stripped[body_start:i]
                    if "{" not in body and not sel_text.startswith("@"):
                        sel_toks = tokens(sel_text)
                        if sel_toks:
                            for m in DECL_IMP_RE.finditer(body):
                                prop = m.group(1).lower()
                                is_imp = m.group(2) is not None
                                abs_off = body_start + m.start()
                                ln = stripped.count("\n", 0, abs_off) + 1
                                idx[prop].append((rel, ln, sel_toks, is_imp))
                    body_start = None
                    sel_start = i + 1
        # Handle @media blocks by stripping them at top level and rescanning inner
        # (approximation — good enough for heuristic overlap)
    return idx


def main():
    if not CUSTOM_CSS.exists():
        print(f"FATAL: {CUSTOM_CSS} missing", file=sys.stderr)
        return 1

    t0 = time.time()
    print("Building competition index...", flush=True)
    idx = build_competition_index()
    print(f"  {len(idx)} props, {sum(len(v) for v in idx.values())} rule-decls "
          f"in {time.time()-t0:.1f}s", flush=True)

    raw = CUSTOM_CSS.read_text()
    stripped = strip_comments(raw)
    imp_offsets = [m.start() for m in re.finditer(r"!\s*important", stripped)]
    print(f"Found {len(imp_offsets)} !important occurrences in custom.css", flush=True)

    rows = []
    skipped = 0
    for off in imp_offsets:
        info = extract_decl_around(stripped, off)
        if info is None:
            skipped += 1
            continue
        prop, val, decl_start = info
        sel = extract_selector_for(stripped, off)
        lc_toks = tokens(sel)
        ln = line_of(raw, off)

        comp_imp = False
        comp_plain = False
        sample = ""
        for (cpath, cln, ctoks, is_imp) in idx.get(prop, []):
            if lc_toks & ctoks:
                if is_imp:
                    comp_imp = True
                    if not sample:
                        sample = f"{cpath}:{cln}"
                else:
                    comp_plain = True
                    if not sample:
                        sample = f"{cpath}:{cln}"
                if comp_imp and comp_plain:
                    break

        if comp_imp:
            bucket, fix = "C-2", "delete"
        elif comp_plain:
            bucket, fix = "C-1", "tighten:#section-id"
        elif prop in C4_SUSPECT_PROPS:
            bucket, fix = "C-4?", "manual-review"
        else:
            bucket, fix = "C-3", "delete"

        rows.append({
            "line": ln,
            "selector": sel.replace("\t", " "),
            "property": prop,
            "value": val.replace("\t", " "),
            "bucket": bucket,
            "competing_rule": sample,
            "proposed_fix": fix,
        })

    header = ["line", "selector", "property", "value", "bucket", "competing_rule", "proposed_fix"]
    with OUT.open("w") as f:
        f.write("# Phase 3 !important inventory — audit/IMPORTANT-INVENTORY.tsv\n")
        f.write("# Generated by scripts/_audit_important.py\n")
        f.write("# Buckets: C-1 specificity war, C-2 vs !important, C-3 defends nothing, C-4? suspect, C-4 confirmed\n")
        f.write("#\n")
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in header) + "\n")

    bc = Counter(r["bucket"] for r in rows)
    print("\nBucket distribution:")
    for b in ("C-1", "C-2", "C-3", "C-4?", "C-4"):
        print(f"  {b:<5} {bc.get(b, 0)}")
    print(f"\nTotal classified: {len(rows)}  (skipped: {skipped})")
    print(f"Wrote {OUT}")
    print(f"Time: {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
