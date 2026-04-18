#!/usr/bin/env python3
"""
Force Shopify to recompile assets/theme.css on the staging theme.

Phase 3 anomaly #2: a `shopify theme push --only config/settings_data.json`
does NOT reliably trigger regeneration of the compiled theme.css asset.
Workaround: append a single trailing whitespace to assets/theme.css.liquid,
push, poll the served theme.css URL for a content-hash change, then revert.

Usage:
    op run --env-file=.env.tpl -- python3 shopify/scripts/_force_theme_recompile.py

Exits 0 on recompile confirmed, 1 on timeout or error.

Reads staging theme ID from scripts/config.py. Uses shopify CLI for pushes,
urllib for polling (no extra deps).
"""

from __future__ import annotations

import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # scripts/config.py

ROOT = Path(__file__).resolve().parent.parent
THEME_CSS_LIQUID = ROOT / "assets" / "theme.css.liquid"
TRIGGER_LINE = ".__lc_force_recompile_{ts} {{ display: none; }}"
POLL_INTERVAL_SEC = 2
POLL_TIMEOUT_SEC = 60


def _get_preview_subdomain() -> str | None:
    """
    Generate a tokenised *.shopifypreview.com URL via `shopify theme preview`.
    Standard `?preview_theme_id=` URLs route through Shopify's CDN which
    aggressively caches HTML; the preview subdomain bypasses that.
    """
    # Write a tiny empty-overrides file on the fly
    empty = Path("/tmp/lc-force-recompile-overrides.json")
    empty.write_text("{}")
    try:
        out = subprocess.run(
            ["shopify", "theme", "preview",
             "--theme", config.THEME_IDS["staging"],
             "--store", config.STORE,
             "--overrides", str(empty),
             "--json", "--no-color"],
            check=True, cwd=str(ROOT), capture_output=True, timeout=60,
        )
        import json as _json
        # Shopify CLI emits the JSON response to stderr, not stdout
        combined = (out.stdout + out.stderr).decode(errors="ignore").strip()
        for line in combined.split("\n"):
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                d = _json.loads(line)
                return d.get("url")
        return None
    except Exception as e:
        print(f"  could not generate preview URL: {e}", file=sys.stderr)
        return None


def current_theme_css_version(base_url: str | None = None) -> str | None:
    """Fetch the staging preview URL and extract the theme.css ?v= hash."""
    try:
        url = base_url or f"https://{config.STORE}/?preview_theme_id={config.THEME_IDS['staging']}&_fd=0"
        req = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
        m = re.search(r"theme\.css\?v=(\d+)", body)
        return m.group(1) if m else None
    except Exception as e:
        print(f"  poll: {e}", file=sys.stderr)
        return None


def push_theme_css_liquid() -> bool:
    """Shopify theme push --only assets/theme.css.liquid."""
    cmd = [
        "shopify", "theme", "push",
        "--theme", config.THEME_IDS["staging"],
        "--store", config.STORE,
        "--allow-live",
        "--only", "assets/theme.css.liquid",
    ]
    try:
        subprocess.run(cmd, check=True, cwd=str(ROOT), capture_output=True, timeout=120)
        return True
    except subprocess.CalledProcessError as e:
        print(f"push failed: {e.stderr.decode(errors='ignore')[:400]}", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("push timed out after 120s", file=sys.stderr)
        return False


def touch_trigger() -> str:
    """
    Append a dummy CSS rule with a timestamped selector to theme.css.liquid.

    Using a rule rather than a comment because Shopify's compile step
    minifies CSS comments out, producing byte-identical compiled theme.css
    and therefore no version-hash bump. A real rule with a unique class
    name guarantees the compiled output differs.
    """
    ts = int(time.time())
    line = TRIGGER_LINE.format(ts=ts)
    with THEME_CSS_LIQUID.open("a") as f:
        f.write("\n" + line + "\n")
    return line


def git_checkout_theme_css_liquid() -> bool:
    """Revert the working-tree change on theme.css.liquid."""
    try:
        subprocess.run(
            ["git", "checkout", "assets/theme.css.liquid"],
            check=True, cwd=str(ROOT), capture_output=True, timeout=15,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"git checkout failed: {e.stderr.decode(errors='ignore')}", file=sys.stderr)
        return False


def main() -> int:
    staging_id = config.THEME_IDS["staging"]
    print(f"force-recompile: staging theme {staging_id}")

    preview_url = _get_preview_subdomain()
    if preview_url:
        print(f"  preview URL: {preview_url}")
    else:
        print("  preview URL unavailable — falling back to ?preview_theme_id= (may be CDN-cached)")

    starting_version = current_theme_css_version(preview_url)
    if starting_version is None:
        print("ERROR: could not fetch starting theme.css version", file=sys.stderr)
        return 1
    print(f"  starting theme.css v={starting_version[:16]}...")

    # Touch + push
    trigger = touch_trigger()
    print(f"  touched assets/theme.css.liquid with: {trigger}")
    t0 = time.time()
    if not push_theme_css_liquid():
        git_checkout_theme_css_liquid()
        return 1
    push_duration = time.time() - t0
    print(f"  pushed in {push_duration:.1f}s")

    # Poll
    deadline = time.time() + POLL_TIMEOUT_SEC
    new_version = None
    while time.time() < deadline:
        v = current_theme_css_version(preview_url)
        if v and v != starting_version:
            new_version = v
            break
        time.sleep(POLL_INTERVAL_SEC)

    # Revert trigger touch regardless of outcome
    reverted = git_checkout_theme_css_liquid()

    if new_version:
        elapsed = time.time() - t0
        print(f"  new theme.css v={new_version[:16]}... (recompile confirmed in {elapsed:.1f}s)")
        if reverted:
            print("  reverted theme.css.liquid working-tree change")
        return 0
    else:
        print(f"  recompile NOT detected within {POLL_TIMEOUT_SEC}s — try manual UI save", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
