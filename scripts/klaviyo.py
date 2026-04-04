"""
Klaviyo API utility — Lost Collective
Run via: op run --env-file=.env.tpl -- python3 scripts/klaviyo.py

Credentials stored in 1Password: "Lost Collective — Klaviyo"
Private key scope: Full Access (all read/write scopes)
"""
import urllib.request, urllib.parse, json, os, sys

API_KEY = os.environ.get("KLAVIYO_PRIVATE_KEY", "")
BASE    = "https://a.klaviyo.com/api"
HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": "2024-10-15",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def _req(method, path, body=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"HTTP {e.code}: {err}")
        raise


def get(path):        return _req("GET",    path)
def post(path, body): return _req("POST",   path, body)
def patch(path, body):return _req("PATCH",  path, body)


# ── Lists ──────────────────────────────────────────────────────────────────────

def list_lists():
    """Return all Klaviyo lists."""
    data = get("/lists/?fields[list]=name,created,updated")
    return data.get("data", [])


def get_list_profiles(list_id, max_pages=10):
    """Return all profiles in a list (auto-paginated)."""
    profiles, path = [], f"/lists/{list_id}/profiles/?fields[profile]=email,first_name,last_name"
    for _ in range(max_pages):
        r = get(path)
        profiles.extend(r.get("data", []))
        path = r.get("links", {}).get("next", "")
        if not path:
            break
    return profiles


# ── Profiles ───────────────────────────────────────────────────────────────────

def get_profile_by_email(email):
    """Look up a single profile by email."""
    encoded = urllib.parse.quote(f'equals(email,"{email}")')
    r = get(f"/profiles/?filter={encoded}")
    data = r.get("data", [])
    return data[0] if data else None


def create_or_update_profile(email, props: dict):
    """Upsert a profile. props can include first_name, last_name, or any custom property."""
    body = {
        "data": {
            "type": "profile",
            "attributes": {"email": email, **props}
        }
    }
    return post("/profile-import/", body)


# ── Events ─────────────────────────────────────────────────────────────────────

def track_event(event_name, email, properties: dict = None):
    """Track a custom event against a profile."""
    body = {
        "data": {
            "type": "event",
            "attributes": {
                "metric": {"data": {"type": "metric", "attributes": {"name": event_name}}},
                "profile": {"data": {"type": "profile", "attributes": {"email": email}}},
                "properties": properties or {},
            }
        }
    }
    return post("/events/", body)


# ── Metrics ────────────────────────────────────────────────────────────────────

def list_metrics():
    """Return all metrics (events) tracked in the account."""
    return get("/metrics/").get("data", [])


# ── Campaigns ──────────────────────────────────────────────────────────────────

def list_campaigns(channel="email"):
    """Return all campaigns for a given channel (email / sms)."""
    return get(f"/campaigns/?filter=equals(messages.channel,'{channel}')").get("data", [])


# ── Segments ───────────────────────────────────────────────────────────────────

def list_segments():
    """Return all segments."""
    return get("/segments/?fields[segment]=name,created,updated").get("data", [])


# ── Templates ──────────────────────────────────────────────────────────────────

def list_templates():
    """Return all email templates."""
    return get("/templates/?fields[template]=name,created,updated").get("data", [])


# ── Quick diagnostics ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not API_KEY:
        sys.exit("KLAVIYO_PRIVATE_KEY not set — run via: op run --env-file=.env.tpl -- python3 scripts/klaviyo.py")

    print("=== Lists ===")
    for l in list_lists():
        print(f"  {l['id']}  {l['attributes']['name']}")

    print("\n=== Metrics (top 10) ===")
    for m in list_metrics()[:10]:
        print(f"  {m['id']}  {m['attributes']['name']}")

    print("\n=== Segments ===")
    for s in list_segments():
        print(f"  {s['id']}  {s['attributes']['name']}")
