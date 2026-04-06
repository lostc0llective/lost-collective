"""
Gemini API — Lost Collective
Model:   gemini-2.5-flash (Google AI, paid tier)
Key:     1Password → "Lost Collective — Gemini" (password field)

Run: op run --env-file=.env.tpl -- python3 scripts/gemini.py

Key operations:
  generate(prompt)                    — single generation
  collection_description(title, ...)  — SEO collection description
  subject_description(product, ...)   — product subject_description metafield
  batch_subject_descriptions(...)     — bulk metafield generation for many products
"""

import os, sys, time

MODEL = "gemini-2.5-flash"


# ── Client ─────────────────────────────────────────────────────────────────────

def _client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("GEMINI_API_KEY not set. Run via: op run --env-file=.env.tpl -- python3 ...")
    from google import genai
    return genai.Client(api_key=api_key)


def generate(prompt: str, temperature: float = 0.7) -> str:
    """Single generation. Returns plain text."""
    from google.genai import types
    client = _client()
    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=temperature),
    )
    return resp.text.strip()


# ── Store voice / style ────────────────────────────────────────────────────────

BRAND_VOICE = """
Lost Collective is a fine art photography store documenting forgotten, abandoned, and
historically significant places: industrial ruins, ghost towns, derelict architecture,
decaying infrastructure across Australia and Japan.

Tone of voice rules (from docs/lost-collective-tov.md):
- Website/Shopify content is always about the place, never about the photographer
- Historical facts are essential, not optional. Name dates, events, people, context.
- Sensory, visceral writing. Make the reader imagine being there.
- No em dashes, no hashtags, no generic emotional language
- No "stunning", "breathtaking", "haunting beauty", "hidden gem", "unique" or similar AI slop
- No exclamation marks, no calls to action, no "Shop now" language
- Australian spelling (colour, centre, grey, realise)
- Short sentences. Present tense for descriptions. Past tense for history.
"""


# ── Collection descriptions ────────────────────────────────────────────────────

def collection_description(
    title: str,
    location: str = "",
    year: str = "",
    context: str = "",
    max_words: int = 80,
) -> str:
    """
    Generate a collection (series) description for the storefront.

    title:    Collection name, e.g. "White Bay Power Station"
    location: e.g. "Rozelle, Sydney NSW"
    year:     Year photographed, e.g. "2019"
    context:  Any additional factual notes about the place
    """
    details = []
    if location:
        details.append(f"Location: {location}")
    if year:
        details.append(f"Photographed: {year}")
    if context:
        details.append(f"Context: {context}")
    detail_block = "\n".join(details)

    prompt = f"""{BRAND_VOICE}

Write a collection description for the Lost Collective online store.

Series: {title}
{detail_block}

Requirements:
- {max_words} words maximum
- 2–3 sentences
- Factual, atmospheric, no fluff
- Do not mention "Lost Collective" or "Brett Patman" by name
- Do not include a title or heading — body text only
"""
    return generate(prompt, temperature=0.6)


# ── Product subject_description metafield ──────────────────────────────────────

SUBJECT_DESC_SYSTEM = f"""{BRAND_VOICE}

You are writing the `subject_description` metafield for individual fine art photographs.
This appears on the product page as a short caption beneath the image — it describes
what is depicted in the photograph and its context or significance.

Requirements:
- 20–40 words
- Present tense, observational voice
- Specific — name the place, structure, or object clearly
- No title or heading — just the description text
- Do not repeat the product title verbatim
"""

def subject_description(
    title: str,
    series: str = "",
    location: str = "",
    year: str = "",
    notes: str = "",
) -> str:
    """
    Generate a subject_description metafield for a single product.

    title:    Product title, e.g. "White Bay #03"
    series:   Series/collection name
    location: Location if known
    year:     Year photographed
    notes:    Any additional context
    """
    details = []
    if series:
        details.append(f"Series: {series}")
    if location:
        details.append(f"Location: {location}")
    if year:
        details.append(f"Year: {year}")
    if notes:
        details.append(f"Notes: {notes}")

    prompt = f"""{SUBJECT_DESC_SYSTEM}

Product title: {title}
{chr(10).join(details)}

Write the subject_description:"""
    return generate(prompt, temperature=0.65)


# ── Batch generation ───────────────────────────────────────────────────────────

def batch_subject_descriptions(
    products: list[dict],
    delay: float = 1.0,
) -> list[dict]:
    """
    Generate subject_descriptions for a list of products.

    Each product dict should have:
      id       — Shopify GID (gid://shopify/Product/...)
      title    — product title
      series   — (optional) series name
      location — (optional) location
      year     — (optional) year

    Returns list of dicts: { id, title, subject_description }
    """
    results = []
    total = len(products)
    for i, p in enumerate(products, 1):
        print(f"  [{i}/{total}] {p['title'][:50]}", end="", flush=True)
        try:
            desc = subject_description(
                title=p["title"],
                series=p.get("series", ""),
                location=p.get("location", ""),
                year=p.get("year", ""),
                notes=p.get("notes", ""),
            )
            results.append({"id": p["id"], "title": p["title"], "subject_description": desc})
            print(f" → {len(desc.split())} words")
        except Exception as e:
            print(f" ERROR: {e}")
            results.append({"id": p["id"], "title": p["title"], "subject_description": None, "error": str(e)})
        if i < total:
            time.sleep(delay)
    return results


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "test"

    if cmd == "test":
        print("Testing Gemini 2.5 Flash...\n")
        result = generate("In one sentence, describe what fine art photography is.")
        print(f"  {result}\n")
        print("Generating sample collection description...\n")
        desc = collection_description(
            title="White Bay Power Station",
            location="Rozelle, Sydney NSW",
            year="2019",
            context="Disused coal-fired power station built in 1912, now awaiting redevelopment",
        )
        print(f"  {desc}\n")

    elif cmd == "collection":
        if len(sys.argv) < 3:
            print("Usage: python3 scripts/gemini.py collection <title> [location] [year]")
            sys.exit(1)
        title = sys.argv[2]
        location = sys.argv[3] if len(sys.argv) > 3 else ""
        year = sys.argv[4] if len(sys.argv) > 4 else ""
        print(collection_description(title=title, location=location, year=year))

    elif cmd == "product":
        if len(sys.argv) < 3:
            print("Usage: python3 scripts/gemini.py product <title> [series]")
            sys.exit(1)
        title = sys.argv[2]
        series = sys.argv[3] if len(sys.argv) > 3 else ""
        print(subject_description(title=title, series=series))

    else:
        print("Usage: python3 scripts/gemini.py [test|collection <title>|product <title>]")
