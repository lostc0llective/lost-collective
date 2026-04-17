"""
Lost Collective — shared script utilities.

Import in scripts instead of re-implementing:
  from lc_lib import log, progress, rate_limit, confirm_destructive

Already available from existing modules:
  config.py      — STORE, ENV, ADMIN_TOKEN, require_production_confirmation()
  shopify_gql.py — gql(), iter_products(), iter_collections()
"""

import sys
import time
from datetime import datetime


# ── Logging ────────────────────────────────────────────────────────────────────

def log(msg: str, *, level: str = "info") -> None:
    """
    Timestamped log line to stderr.
    level: "info" | "warn" | "error" | "ok"
    """
    prefix = {
        "info":  "  ",
        "warn":  "  ! ",
        "error": "  X ",
        "ok":    "  ✓ ",
    }.get(level, "  ")
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {prefix}{msg}", file=sys.stderr)


def log_ok(msg: str) -> None:
    log(msg, level="ok")


def log_warn(msg: str) -> None:
    log(msg, level="warn")


def log_error(msg: str) -> None:
    log(msg, level="error")


# ── Progress ───────────────────────────────────────────────────────────────────

def progress(current: int, total: int, label: str = "") -> None:
    """
    Print an inline progress counter. Overwrites the same line.
    Call with current == total to finalize (adds newline).
    """
    pct = int(100 * current / total) if total else 0
    bar = ("#" * (pct // 5)).ljust(20)
    suffix = f" {label}" if label else ""
    end = "\n" if current >= total else "\r"
    print(f"  [{bar}] {pct:3d}%  {current}/{total}{suffix}", end=end, file=sys.stderr, flush=True)


# ── Rate limiting ──────────────────────────────────────────────────────────────

def rate_limit(delay: float = 0.5) -> None:
    """Sleep for `delay` seconds. Use between Shopify REST API calls."""
    time.sleep(delay)


def rate_limit_batch(items: list, fn, *, delay: float = 0.5, label: str = "items") -> list:
    """
    Apply fn(item) to each item in items with rate limiting and progress output.
    Returns list of fn(item) results.
    """
    results = []
    total = len(items)
    for i, item in enumerate(items, 1):
        results.append(fn(item))
        progress(i, total, label)
        if i < total:
            time.sleep(delay)
    return results


# ── Safety ─────────────────────────────────────────────────────────────────────

def confirm_destructive(operation: str, *, skip_in_ci: bool = False) -> None:
    """
    Prompt for confirmation before a destructive operation.
    Exits if the user does not type 'yes'.
    Pass skip_in_ci=True to bypass when SHOPIFY_ENV=staging (non-interactive).
    """
    import os
    if skip_in_ci and os.environ.get("SHOPIFY_ENV", "staging") == "staging":
        return
    print(f"\n  About to: {operation}", file=sys.stderr)
    answer = input("  Type 'yes' to continue: ").strip().lower()
    if answer != "yes":
        print("  Aborted.", file=sys.stderr)
        sys.exit(0)


# ── Summary table ──────────────────────────────────────────────────────────────

def print_summary(rows: list[tuple], headers: tuple = ("Item", "Result")) -> None:
    """
    Print a simple two-column summary table.
    rows: list of (label, value) tuples
    """
    if not rows:
        return
    col1 = max(len(h) for h, _ in [headers, *rows])
    print(file=sys.stderr)
    print(f"  {headers[0]:<{col1}}  {headers[1]}", file=sys.stderr)
    print(f"  {'-' * col1}  {'-' * 30}", file=sys.stderr)
    for label, value in rows:
        print(f"  {label:<{col1}}  {value}", file=sys.stderr)
    print(file=sys.stderr)
