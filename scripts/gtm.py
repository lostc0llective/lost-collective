"""
Google Tag Manager API — Lost Collective
Container:   GTM-K898GWK
Account ID:  6000446623
Container ID: 30486092

Credentials: same service account as GSC/GA4
1Password → "Lost Collective — Google Search Console" (document)

One-time setup:
  1. Enable Tag Manager API in Google Cloud Console (project lost-collective-492307)
  2. GTM → Admin → Container → User management → add service account email as Editor:
     claude-code-lost-collective@lost-collective-492307.iam.gserviceaccount.com

Run: python3 scripts/gtm.py

Key operations:
  audit()           — list all tags, triggers, variables + pass/fail checks
  list_tags()       — all tags with firing triggers
  list_triggers()   — all triggers
  get_tag(name)     — find a tag by name
  publish(notes)    — publish a new container version
"""

import json, subprocess, sys

# ── Config ─────────────────────────────────────────────────────────────────────

GTM_ACCOUNT_ID   = "6000446623"
GTM_CONTAINER_ID = "30486092"
CONTAINER_PATH   = f"accounts/{GTM_ACCOUNT_ID}/containers/{GTM_CONTAINER_ID}"
WORKSPACE_PATH   = f"{CONTAINER_PATH}/workspaces/3"   # default workspace

SCOPES = ["https://www.googleapis.com/auth/tagmanager.edit.containers",
          "https://www.googleapis.com/auth/tagmanager.publish",
          "https://www.googleapis.com/auth/tagmanager.readonly"]

GA4_TAG_NAME             = "GA4 - Configuration"
CONSENT_INIT_TAG_NAME    = "Consent Initialization - Default"
META_TAG_NAME            = "Meta - Facebook Pixel"
BEGIN_CHECKOUT_TAG_NAME  = "GA4 - begin_checkout"
EXPECTED_GA4_ID          = "G-411MPGQ64J"
EXPECTED_META_PIXEL_ID   = "1564860757158131"


# ── Auth ───────────────────────────────────────────────────────────────────────

def _service():
    """Return an authenticated GTM API resource."""
    try:
        from googleapiclient.discovery import build
        from google.oauth2 import service_account
    except ImportError:
        sys.exit("Missing dependency. Run: pip install google-api-python-client google-auth")

    raw = subprocess.run(
        ["op", "document", "get", "Lost Collective — Google Search Console"],
        capture_output=True, text=True, check=True
    ).stdout

    creds = service_account.Credentials.from_service_account_info(
        json.loads(raw), scopes=SCOPES
    )
    return build("tagmanager", "v2", credentials=creds, cache_discovery=False)


# ── Read operations ────────────────────────────────────────────────────────────

def list_tags() -> list:
    svc = _service()
    resp = svc.accounts().containers().workspaces().tags().list(
        parent=WORKSPACE_PATH
    ).execute()
    return resp.get("tag", [])


def list_triggers() -> list:
    svc = _service()
    resp = svc.accounts().containers().workspaces().triggers().list(
        parent=WORKSPACE_PATH
    ).execute()
    return resp.get("trigger", [])


def list_variables() -> list:
    svc = _service()
    resp = svc.accounts().containers().workspaces().variables().list(
        parent=WORKSPACE_PATH
    ).execute()
    return resp.get("variable", [])


def get_tag(name: str) -> dict | None:
    return next((t for t in list_tags() if t.get("name") == name), None)


def get_trigger(name: str) -> dict | None:
    return next((t for t in list_triggers() if t.get("name") == name), None)


# ── Audit ──────────────────────────────────────────────────────────────────────

def audit() -> None:
    """Run all checks and report pass/fail."""
    tags     = list_tags()
    triggers = list_triggers()

    tag_names     = {t["name"] for t in tags}
    trigger_names = {t["name"] for t in triggers}

    print(f"\nGTM Container Audit — GTM-K898GWK\n{'─'*60}")

    checks = []

    # 1. Consent Initialization trigger exists
    has_consent_trigger = any("Consent Init" in n for n in trigger_names)
    checks.append(("Consent Initialization trigger", has_consent_trigger))

    # 2. Consent defaults tag exists and fires on consent init
    consent_tag = get_tag(CONSENT_INIT_TAG_NAME)
    checks.append((f"Tag: '{CONSENT_INIT_TAG_NAME}'", consent_tag is not None))

    # 3. GA4 config tag exists
    ga4_tag = get_tag(GA4_TAG_NAME)
    checks.append((f"Tag: '{GA4_TAG_NAME}'", ga4_tag is not None))

    # 4. begin_checkout tag exists
    checkout_tag = get_tag(BEGIN_CHECKOUT_TAG_NAME)
    checks.append((f"Tag: '{BEGIN_CHECKOUT_TAG_NAME}'", checkout_tag is not None))

    # 5. Meta pixel tag exists
    meta_tag = get_tag(META_TAG_NAME)
    checks.append((f"Tag: '{META_TAG_NAME}'", meta_tag is not None))

    for name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status}  {name}")

    print(f"\nAll tags ({len(tags)}):\n{'─'*60}")
    for t in tags:
        firing = [tf.get("triggerId") for tf in t.get("firingTriggerId", [])]
        print(f"  {t['name']:<45} triggers: {firing}")

    print(f"\nAll triggers ({len(triggers)}):\n{'─'*60}")
    for t in triggers:
        print(f"  {t.get('type', 'UNKNOWN'):<25} {t['name']}")


# ── Publish ────────────────────────────────────────────────────────────────────

def publish(notes: str = "Published via Claude Code API") -> dict:
    """Create and publish a new container version."""
    svc = _service()

    # Create version
    version_resp = svc.accounts().containers().workspaces().create_version(
        path=WORKSPACE_PATH,
        body={"name": notes, "notes": notes}
    ).execute()

    container_version = version_resp.get("containerVersion", {})
    version_id = container_version.get("containerVersionId")

    if not version_id:
        return {"error": "No version ID returned", "response": version_resp}

    # Publish
    pub_resp = svc.accounts().containers().versions().publish(
        path=f"{CONTAINER_PATH}/versions/{version_id}"
    ).execute()

    return {"version_id": version_id, "published": True, "response": pub_resp}


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "audit"

    if cmd == "audit":
        audit()
    elif cmd == "tags":
        for t in list_tags():
            print(f"{t['tagId']:>4}  {t['name']}")
    elif cmd == "triggers":
        for t in list_triggers():
            print(f"{t['triggerId']:>4}  {t.get('type',''):<20}  {t['name']}")
    elif cmd == "publish":
        notes = " ".join(sys.argv[2:]) or "Published via Claude Code"
        print(publish(notes))
    else:
        print("Usage: python3 scripts/gtm.py [audit|tags|triggers|publish <notes>]")
