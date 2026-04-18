"""
Environment configuration — Lost Collective
Shared by all scripts. Import this instead of reading env vars directly.

Environments:
  staging    → theme #193920860326 "LC Flex Staging 2026-04-18" (unpublished)
  production → theme #193859780774 "Lost Collective Live - 2026-04-15" (live, Flex v5.5.1)
  backup     → theme #191393464486 "Lost Collective Backup 05/01/2026" (unpublished)
  dev        → theme created dynamically by `shopify theme dev`

Default is staging. To target production, set SHOPIFY_ENV=production in your
shell or override in .env.tpl before running op run.
"""

import os, sys

# ── Store ──────────────────────────────────────────────────────────────────────

STORE         = "lost-collective.myshopify.com"
ADMIN_TOKEN   = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
API_VERSION   = "2025-01"

# ── Environment ────────────────────────────────────────────────────────────────

ENV = os.environ.get("SHOPIFY_ENV", "staging").lower()

THEME_IDS = {
    "production": os.environ.get("SHOPIFY_THEME_ID_PRODUCTION", "193859780774"),
    "staging":    os.environ.get("SHOPIFY_THEME_ID_STAGING",    "193920860326"),
    "backup":     os.environ.get("SHOPIFY_THEME_ID_BACKUP",     "191393464486"),
}

THEME_NAMES = {
    "production": "Lost Collective Live - 2026-04-15 (LIVE, Flex v5.5.1)",
    "staging":    "LC Flex Staging 2026-04-18 (unpublished)",
    "backup":     "Lost Collective Backup 05/01/2026 (unpublished)",
}

def theme_id() -> str:
    """Return the theme ID for the current environment."""
    if ENV == "dev":
        raise ValueError("Dev theme is created by `shopify theme dev` — no static ID")
    return THEME_IDS[ENV]


# ── Production guard ───────────────────────────────────────────────────────────

def require_production_confirmation(operation: str):
    """
    Call before any write operation that targets production.
    Aborts with a clear message if SHOPIFY_ENV is not explicitly set to production.
    """
    if ENV != "production":
        print(
            f"\n  BLOCKED: '{operation}' targets production but SHOPIFY_ENV={ENV!r}.\n"
            f"  To proceed, set SHOPIFY_ENV=production in .env.tpl and re-run.\n"
            f"  Current theme would be: {THEME_NAMES.get(ENV, ENV)} ({THEME_IDS.get(ENV, '?')})\n",
            file=sys.stderr,
        )
        sys.exit(1)


def production_banner():
    """Print a visible warning when running against production."""
    if ENV == "production":
        print("=" * 60, file=sys.stderr)
        print("  WARNING: SHOPIFY_ENV=production — targeting LIVE theme", file=sys.stderr)
        print("=" * 60, file=sys.stderr)


# ── Theme push helpers ─────────────────────────────────────────────────────────

def push_command(allow_live: bool = False) -> str:
    """
    Return the shopify CLI push command for the current environment.
    Raises if trying to push to production without allow_live=True.
    """
    if ENV == "production" and not allow_live:
        raise RuntimeError(
            "Set allow_live=True to push to production, or switch to staging."
        )
    tid = theme_id()
    return (
        f"shopify theme push --theme {tid} "
        f"--store {STORE} --allow-live"
    )


# ── Summary ────────────────────────────────────────────────────────────────────

def print_env():
    print(f"  Environment : {ENV.upper()}")
    print(f"  Store       : {STORE}")
    print(f"  Theme       : {THEME_NAMES.get(ENV, '(dev)')}  [{THEME_IDS.get(ENV, 'dynamic')}]")
    print(f"  API version : {API_VERSION}")
    print(f"  Auth        : {'✓ token set' if ADMIN_TOKEN else '✗ SHOPIFY_ADMIN_TOKEN not set'}")


if __name__ == "__main__":
    print_env()
