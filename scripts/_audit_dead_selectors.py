#!/usr/bin/env python3
"""
Phase 5 T5 bug 3: dead-selector sibling-check audit.

Phase 1 flagged that the prior dead-selector detection only looked at rules
as a whole — if a rule like `.a, .b, .c { ... }` had `.a` rendered but `.c`
not rendered, the rule was kept entirely because at least one selector
matched. `.c` survived as dead clutter within a live rule.

This script fixes that blind spot:
  1. Parse assets/custom.css rule-by-rule.
  2. Split each rule's selector list by commas into individual selectors.
  3. For each individual selector, fetch a sample of rendered HTML from
     staging (homepage + PDP + collection + blog) and check if any element
     matches the selector.
  4. Flag selector-list entries that:
     - render nowhere (dead sibling), AND
     - coexist in a rule with at least one sibling that DOES render (live rule)

Output: audit/DEAD-SIBLINGS-v2.txt — one row per dead sibling with file:line,
the full selector list, and which sibling is dead.

Regression expectation: Phase 1 never ran this check. The v2 output is the
first time we're looking at selector-list granularity. Low-priority cleanup;
these are not broken rules, just dead clutter inside live rule bodies.
"""

from __future__ import annotations
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config

ROOT = Path(__file__).resolve().parent.parent
CUSTOM_CSS = ROOT / "assets" / "custom.css"
OUT = ROOT / "audit" / "DEAD-SIBLINGS-v2.txt"

SAMPLE_PAGES = [
    "/",
    "/collections/all",
    "/products/parramatta-road-yeah",
    "/blogs/blog/tin-city-built-without-permission-on-the-lake",
    "/cart",
]


def fetch_corpus() -> str:
    """Fetch HTML from staging pages and concatenate."""
    base = f"https://{config.STORE}/?preview_theme_id={config.THEME_IDS['staging']}&_fd=0"
    # Actually hit the preview subdomain via a fresh theme preview generation.
    # For simplicity, use the direct URLs; the content of class attributes
    # is what we need (rendered HTML snapshot).
    corpus = []
    for path in SAMPLE_PAGES:
        url = f"https://{config.STORE}{path}?preview_theme_id={config.THEME_IDS['staging']}&_fd=0"
        try:
            with urllib.request.urlopen(url, timeout=20) as resp:
                corpus.append(resp.read().decode("utf-8", errors="ignore"))
        except Exception as e:
            print(f"  WARN: {url}: {e}", file=sys.stderr)
    return "\n".join(corpus)


def extract_class_id_names(html: str) -> set[str]:
    """From HTML corpus, extract all class-name and id-name tokens actually rendered."""
    classes = set()
    for m in re.finditer(r'class=["\']([^"\']+)["\']', html):
        for tok in m.group(1).split():
            classes.add("." + tok)
    for m in re.finditer(r'id=["\']([^"\']+)["\']', html):
        classes.add("#" + m.group(1))
    return classes


def parse_custom_css_rules(css: str):
    """
    Yield (line, selector_list) for each rule in assets/custom.css.
    selector_list is the raw comma-separated string before `{`.
    """
    # Strip comments to simplify
    clean = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    # Find top-level rules
    depth = 0
    sel_start = 0
    n = len(clean)
    for i, c in enumerate(clean):
        if c == "{":
            if depth == 0:
                sel = clean[sel_start:i].strip()
                sel = re.sub(r"\s+", " ", sel)
                line_no = clean.count("\n", 0, sel_start) + 1
                if sel and not sel.startswith("@"):
                    yield line_no, sel
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                sel_start = i + 1


def main() -> int:
    html = fetch_corpus()
    print(f"Fetched {len(html):,} bytes of HTML across {len(SAMPLE_PAGES)} pages")
    live_tokens = extract_class_id_names(html)
    print(f"Found {len(live_tokens)} unique class/id tokens in rendered HTML")

    css = CUSTOM_CSS.read_text()
    dead_siblings = []
    total_rules = 0
    for line_no, sel_list in parse_custom_css_rules(css):
        total_rules += 1
        parts = [p.strip() for p in sel_list.split(",") if p.strip()]
        if len(parts) < 2:
            # Only multi-selector rules can have dead siblings
            continue
        live_parts, dead_parts = [], []
        for p in parts:
            # Extract class/id tokens from this selector
            toks = re.findall(r"\.[a-zA-Z0-9_-]+|#[a-zA-Z0-9_-]+", p)
            if not toks:
                live_parts.append(p)  # element-only or pseudo; assume live
                continue
            # A selector is "live" if every required class/id token is in the corpus
            all_live = all(t in live_tokens for t in toks)
            if all_live:
                live_parts.append(p)
            else:
                dead_parts.append(p)
        # Flag if rule has at least one live + at least one dead sibling
        if live_parts and dead_parts:
            dead_siblings.append((line_no, sel_list[:140], dead_parts))

    print(f"Scanned {total_rules} rules; {len(dead_siblings)} have dead siblings")
    with OUT.open("w") as f:
        f.write("# Phase 5 T5 bug 3 output — DEAD-SIBLINGS-v2.txt\n")
        f.write("# Generated by scripts/_audit_dead_selectors.py\n")
        f.write("#\n")
        f.write("# Rules in assets/custom.css with at least one comma-separated sibling\n")
        f.write("# selector that never renders on the sample pages.\n")
        f.write(f"# Sample corpus: {SAMPLE_PAGES}\n")
        f.write("# Column: line<TAB>rule_selector_list<TAB>dead_siblings\n#\n")
        for ln, sel, dead in dead_siblings:
            f.write(f"{ln}\t{sel}\t{'|'.join(dead)}\n")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
