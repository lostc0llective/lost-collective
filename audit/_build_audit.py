#!/usr/bin/env python3
"""
Pre-migration audit generator.

Writes raw data files (no analysis, no opinions) to audit/ so a later
session can do the reconciliation analysis. Designed to be safe to re-run.
"""

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "audit"
AUDIT.mkdir(exist_ok=True)

ANOMALIES: list[str] = []


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def _iter_files(dirs: list[str], exts: tuple[str, ...]) -> list[Path]:
    out: list[Path] = []
    for d in dirs:
        base = ROOT / d
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix in exts:
                out.append(p)
    return sorted(out)


# ── 4a: settings-schema-flat.json ──────────────────────────────────────────────
def task_4a() -> None:
    src = ROOT / "config" / "settings_schema.json"
    data = json.loads(src.read_text())
    flat = []
    for group in data:
        group_name = group.get("name", "")
        for s in group.get("settings", []) or []:
            # Skip section headers / paragraphs without id
            row = {
                "group": group_name,
                "label": s.get("label", ""),
                "id": s.get("id", ""),
                "type": s.get("type", ""),
                "default": s.get("default", None),
                "info": s.get("info", ""),
                "options": s.get("options", None) if s.get("type") in ("select", "radio") else None,
            }
            flat.append(row)
    (AUDIT / "settings-schema-flat.json").write_text(json.dumps(flat, indent=2))
    print(f"4a: {len(flat)} rows -> settings-schema-flat.json")


# ── 4b: settings-data-flat.json ────────────────────────────────────────────────
def task_4b() -> None:
    src = ROOT / "config" / "settings_data.json"
    raw = src.read_text()
    # strip /* */ comments at top of file so json.loads works
    cleaned = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)
    data = json.loads(cleaned)
    current = data.get("current", {}) or {}
    if isinstance(current, str):
        ANOMALIES.append(f"4b: settings_data.json 'current' is a string preset name, not an object ({current!r})")
        flat = []
    else:
        flat = [{"id": k, "current_value": v} for k, v in current.items()]
    (AUDIT / "settings-data-flat.json").write_text(json.dumps(flat, indent=2))
    print(f"4b: {len(flat)} rows -> settings-data-flat.json")


# ── 4c + 4d: CSS custom properties ────────────────────────────────────────────
CSS_SEARCH_DIRS = ["assets", "snippets", "sections", "layout"]
CSS_SEARCH_EXTS = (".css", ".liquid")
DEFINE_RE = re.compile(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;}\n]+)")
USE_RE = re.compile(r"var\(\s*(--[a-zA-Z0-9_-]+)")
SELECTOR_RE = re.compile(r"([^{}]+)\{")


def _guess_selector(text: str, offset: int) -> str:
    """Walk backward from offset to find nearest unmatched `{` and return its selector."""
    depth = 0
    i = offset
    while i > 0:
        ch = text[i]
        if ch == "}":
            depth += 1
        elif ch == "{":
            if depth == 0:
                # capture selector before this brace
                j = i - 1
                while j >= 0 and text[j] in " \t\n\r":
                    j -= 1
                start = j
                while start >= 0 and text[start] not in "{}":
                    start -= 1
                sel = text[start + 1:j + 1].strip()
                # collapse whitespace
                return re.sub(r"\s+", " ", sel)[:200]
            depth -= 1
        i -= 1
    return "(file-scope)"


def task_4cd() -> None:
    files = _iter_files(CSS_SEARCH_DIRS, CSS_SEARCH_EXTS)
    # file.suffix of .css.liquid appears as .liquid; that's fine.
    # We explicitly include *.css and *.liquid.
    defs_out: list[str] = []
    defs_index: dict[str, list[tuple[str, int, str]]] = {}  # var -> [(file, line, selector)]
    for f in files:
        try:
            text = f.read_text()
        except Exception as e:
            ANOMALIES.append(f"4c: cannot read {rel(f)}: {e}")
            continue
        for m in DEFINE_RE.finditer(text):
            name = m.group(1)
            value = m.group(2).strip()
            # line number
            line = text.count("\n", 0, m.start()) + 1
            selector = _guess_selector(text, m.start())
            defs_out.append(f"{rel(f)}:{line} | {selector} | {name}: {value};")
            defs_index.setdefault(name, []).append((rel(f), line, selector))

    (AUDIT / "css-custom-properties.txt").write_text("\n".join(defs_out) + "\n")
    print(f"4c: {len(defs_out)} definitions across {len(defs_index)} unique vars -> css-custom-properties.txt")

    # 4d: for each var, find usages across the WHOLE theme (use same search dirs)
    uses_index: dict[str, list[tuple[str, int]]] = {}
    for f in files:
        try:
            text = f.read_text()
        except Exception:
            continue
        for m in USE_RE.finditer(text):
            name = m.group(1)
            line = text.count("\n", 0, m.start()) + 1
            uses_index.setdefault(name, []).append((rel(f), line))

    out_lines = []
    all_vars = sorted(set(defs_index.keys()) | set(uses_index.keys()))
    for v in all_vars:
        defined = defs_index.get(v, [])
        used = uses_index.get(v, [])
        def_str = ", ".join(f"{p}:{ln}" for p, ln, _ in defined) if defined else "(undefined)"
        use_str = ", ".join(f"{p}:{ln}" for p, ln in used) if used else "(unused)"
        out_lines.append(f"{v} | defined_in: [{def_str}] | used_in: [{use_str}]")
    (AUDIT / "css-custom-properties-usage.txt").write_text("\n".join(out_lines) + "\n")
    print(f"4d: {len(out_lines)} unique vars -> css-custom-properties-usage.txt")


# ── 4e: custom-css-rules.tsv ───────────────────────────────────────────────────
def task_4e() -> None:
    src = ROOT / "assets" / "custom.css"
    if not src.exists():
        ANOMALIES.append("4e: assets/custom.css does not exist")
        (AUDIT / "custom-css-rules.tsv").write_text("line_start\tselector\tproperty_count\timportant_count\tmedia_query\n")
        return
    text = src.read_text()
    # Strip comments
    text_no_comments = re.sub(r"/\*.*?\*/", lambda m: " " * len(m.group(0)), text, flags=re.S)

    rows = ["line_start\tselector\tproperty_count\timportant_count\tmedia_query"]
    i = 0
    n = len(text_no_comments)
    media_stack: list[tuple[str, int]] = []  # (media_query, brace_depth_at_entry)
    depth = 0
    parse_fail_count = 0

    # We'll scan linearly, using a small state machine:
    # when we hit `{`, we have the accumulated selector
    # if selector starts with "@media" etc, push media_stack
    # otherwise it's a normal rule: count properties and !important inside
    buf = ""
    buf_start = 0
    while i < n:
        ch = text_no_comments[i]
        if ch == "{":
            sel = buf.strip()
            sel_line = text.count("\n", 0, buf_start) + 1
            if sel.startswith("@media") or sel.startswith("@supports"):
                media_stack.append((sel, depth))
                depth += 1
                buf = ""
                buf_start = i + 1
                i += 1
                continue
            # find matching close brace for the rule body
            j = i + 1
            inner_depth = 1
            while j < n and inner_depth > 0:
                if text_no_comments[j] == "{":
                    inner_depth += 1
                elif text_no_comments[j] == "}":
                    inner_depth -= 1
                j += 1
            body = text_no_comments[i + 1:j - 1]
            # count properties = number of ";" at top level of body
            # (body may contain nested blocks in rare cases; approximate)
            prop_count = body.count(";")
            imp_count = len(re.findall(r"!\s*important", body, re.I))
            media_q = media_stack[-1][0] if media_stack else ""
            # TSV escape
            sel_clean = re.sub(r"\s+", " ", sel).replace("\t", " ")[:400]
            media_clean = re.sub(r"\s+", " ", media_q).replace("\t", " ")[:200]
            if sel_clean == "":
                parse_fail_count += 1
                sel_clean = "(parse_fail)"
            rows.append(f"{sel_line}\t{sel_clean}\t{prop_count}\t{imp_count}\t{media_clean}")
            i = j
            buf = ""
            buf_start = j
            continue
        elif ch == "}":
            depth -= 1
            if media_stack and media_stack[-1][1] == depth:
                media_stack.pop()
            buf = ""
            buf_start = i + 1
            i += 1
            continue
        else:
            if not buf and not ch.isspace():
                buf_start = i
            buf += ch
            i += 1

    if parse_fail_count:
        ANOMALIES.append(f"4e: {parse_fail_count} rules in custom.css had empty selector after parse (flagged as parse_fail)")

    (AUDIT / "custom-css-rules.tsv").write_text("\n".join(rows) + "\n")
    print(f"4e: {len(rows) - 1} rules -> custom-css-rules.tsv")


# ── 4f: inline-styles.txt ──────────────────────────────────────────────────────
INLINE_STYLE_RE = re.compile(r"<(\w+)([^>]*?)\sstyle=\"([^\"]+)\"", re.I)


def task_4f() -> None:
    dirs = ["sections", "snippets", "templates", "layout"]
    files = _iter_files(dirs, (".liquid",))
    out = []
    for f in files:
        try:
            text = f.read_text()
        except Exception as e:
            ANOMALIES.append(f"4f: cannot read {rel(f)}: {e}")
            continue
        for m in INLINE_STYLE_RE.finditer(text):
            element = m.group(1)
            style_value = m.group(3).replace("\n", " ").strip()
            line = text.count("\n", 0, m.start()) + 1
            out.append(f"{rel(f)}:{line} | {element} | {style_value}")
    (AUDIT / "inline-styles.txt").write_text("\n".join(out) + "\n")
    print(f"4f: {len(out)} inline styles -> inline-styles.txt")


# ── 4g: injected-styles.txt ────────────────────────────────────────────────────
STYLE_BLOCK_RE = re.compile(r"\{%\s*style\s*%\}(.*?)\{%\s*endstyle\s*%\}", re.S | re.I)


def task_4g() -> None:
    dirs = ["sections", "snippets", "templates", "layout"]
    files = _iter_files(dirs, (".liquid",))
    out = []
    for f in files:
        try:
            text = f.read_text()
        except Exception as e:
            ANOMALIES.append(f"4g: cannot read {rel(f)}: {e}")
            continue
        for m in STYLE_BLOCK_RE.finditer(text):
            block = m.group(1)
            start_line = text.count("\n", 0, m.start()) + 1
            end_line = text.count("\n", 0, m.end()) + 1
            sel_count = len(re.findall(r"[^{}]+\{", block))
            uses_liquid = "yes" if "{{" in block or "{%" in block else "no"
            context = f.stem if f.parent.name in ("sections", "snippets") else rel(f)
            out.append(f"{rel(f)}:{start_line}-{end_line} | {context} | {sel_count} | {uses_liquid}")
    (AUDIT / "injected-styles.txt").write_text("\n".join(out) + "\n")
    print(f"4g: {len(out)} injected style blocks -> injected-styles.txt")


# ── 4h: section-schemas.json ──────────────────────────────────────────────────
SCHEMA_BLOCK_RE = re.compile(r"\{%\s*schema\s*%\}(.*?)\{%\s*endschema\s*%\}", re.S | re.I)


def task_4h() -> None:
    sections = ROOT / "sections"
    if not sections.exists():
        ANOMALIES.append("4h: sections/ does not exist")
        (AUDIT / "section-schemas.json").write_text("{}")
        return
    merged: dict = {}
    parsed = 0
    failed = 0
    for f in sorted(sections.glob("*.liquid")):
        text = f.read_text()
        m = SCHEMA_BLOCK_RE.search(text)
        if not m:
            continue
        raw = m.group(1).strip()
        # Shopify permits trailing commas in section schema JSON; strict JSON doesn't.
        relaxed = re.sub(r",(\s*[}\]])", r"\1", raw)
        try:
            merged[f.name] = json.loads(relaxed)
            if relaxed != raw:
                ANOMALIES.append(f"4h: {rel(f)} had trailing comma(s) — stripped before JSON parse")
            parsed += 1
        except json.JSONDecodeError as e:
            ANOMALIES.append(f"4h: JSON parse failed for {rel(f)}: {e}")
            merged[f.name] = {"_parse_error": str(e), "_raw_head": raw[:200]}
            failed += 1
    (AUDIT / "section-schemas.json").write_text(json.dumps(merged, indent=2))
    print(f"4h: {parsed} parsed, {failed} failed -> section-schemas.json")


# ── 4i: file-inventory.tsv ─────────────────────────────────────────────────────
def task_4i() -> None:
    dirs = ["assets", "sections", "snippets", "templates", "layout", "config", "locales"]
    rows = ["path\tsize_bytes\tlast_modified"]
    count = 0
    for d in dirs:
        base = ROOT / d
        if not base.exists():
            ANOMALIES.append(f"4i: {d}/ does not exist")
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file():
                st = p.stat()
                rows.append(f"{rel(p)}\t{st.st_size}\t{int(st.st_mtime)}")
                count += 1
    (AUDIT / "file-inventory.tsv").write_text("\n".join(rows) + "\n")
    print(f"4i: {count} files -> file-inventory.tsv")


# ── main ───────────────────────────────────────────────────────────────────────
def main() -> int:
    task_4a()
    task_4b()
    task_4cd()
    task_4e()
    task_4f()
    task_4g()
    task_4h()
    task_4i()

    if ANOMALIES:
        print("\n=== anomalies ===", file=sys.stderr)
        for a in ANOMALIES:
            print(a, file=sys.stderr)
        (AUDIT / "_anomalies.log").write_text("\n".join(ANOMALIES) + "\n")
    else:
        (AUDIT / "_anomalies.log").write_text("(none)\n")

    # Report byte sizes
    print("\n=== audit/ contents ===")
    for p in sorted(AUDIT.iterdir()):
        if p.is_file():
            print(f"  {p.stat().st_size:>10}  {p.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
