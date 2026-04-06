"""
Claude API — Lost Collective copy generation
Model:   claude-sonnet-4-6
Key:     1Password → ANTHROPIC_API_KEY

Replaces Gemini for all product/collection copy. Uses vision to read the
actual photograph before writing — prevents title-only hallucinations.

Run standalone to test:
  op run --env-file=.env.tpl -- python3 scripts/claude_copy.py

Key operations:
  subject_description(...)          — single product subject_description metafield
  batch_subject_descriptions(...)   — bulk generation with validation + review flags
  collection_description(...)       — series/collection page description
"""

import os, sys, time, re

MODEL       = "claude-sonnet-4-6"   # subject_description + collection descriptions
MODEL_OPUS  = "claude-opus-4-6"    # product body_html — highest quality, full TOV reasoning

# ── Banned words / phrases ─────────────────────────────────────────────────────
# Any output containing these is rejected and retried.
# Mirrors docs/lost-collective-tov.md and Brett's explicit corrections.

BANNED = [
    "stunning", "breathtaking", "captivating", "mesmerising", "mesmerizing",
    "haunting beauty", "hauntingly beautiful", "hidden gem",
    "testament to", "stands as a testament", "bears witness",
    "passage of time", "frozen in time", "whispers of", "echoes of",
    "fleeting beauty", "fleeting moment", "bygone era", "bygone age",
    "once-thriving", "once thriving", "in its heyday",
    "timeless", "evocative", "poignant", "nostalgic",
    "raw beauty", "silent beauty", "quiet beauty",
    "speaks to", "reminds us", "invites you", "beckons",
    "unique", "remarkable", "incredible", "amazing", "wonderful",
    "photographic journey", "visual story", "story of time",
    "art lover", "art lovers", "wall art", "perfect for",
    "add to your collection", "shop now", "discover",
]

# Titles that are too ambiguous for vision-less generation.
# If image_url is also missing, these are flagged for manual review.
AMBIGUOUS_TITLE_PATTERNS = re.compile(
    r"^(yummy|door|window|wall|room|corner|light|shadow|detail|view|"
    r"interior|exterior|entrance|exit|stairs|steps|floor|ceiling|"
    r"rust|decay|broken|old|abandoned|forgotten|lost|found|untitled|\d+)$",
    re.IGNORECASE,
)


# ── Client ─────────────────────────────────────────────────────────────────────

def _client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY not set. Run via: op run --env-file=.env.tpl -- python3 ...")
    import anthropic
    return anthropic.Anthropic(api_key=api_key)


# ── TOV system prompt ──────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You write copy for Lost Collective, a fine art photography print store.
The photographs document forgotten, abandoned, and historically significant places:
industrial ruins, ghost towns, derelict architecture, decaying infrastructure across
Australia and Japan.

Tone of voice rules (non-negotiable):
- Content is always about the PLACE — never about the photographer or the viewer
- Historical facts are essential. Name the place, structure, date, or industrial function clearly.
- Sensory, visceral writing. Make the reader imagine being there — smell, texture, scale.
- Short sentences. Present tense for description. Past tense for history.
- Australian spelling: colour, centre, grey, realise, harbour, storey
- No em dashes. No exclamation marks. No calls to action.
- No first person (I, we, our) — this is product/storefront copy, not social media.

Absolutely banned words and phrases — using any of these means the copy is rejected:
stunning, breathtaking, captivating, mesmerising, haunting beauty, hidden gem,
testament to, bears witness, passage of time, frozen in time, whispers of, echoes of,
fleeting beauty, bygone era, once-thriving, in its heyday, timeless, evocative,
poignant, nostalgic, raw beauty, speaks to, reminds us, invites you, unique,
remarkable, incredible, amazing, photographic journey, visual story, wall art,
perfect for, add to your collection, shop now, discover.

Good calibration examples (from Brett's own writing):
- "Corrugated iron and timber frame a narrow passage between buildings at Tin City. Dust on the floor. No wind."
- "Inside White Bay Power Station, turbine hall C stands three storeys high. Steel gantries cross overhead. The floor is covered in debris from decades of water ingress."
- "The Newington Armory stored naval munitions from 1897 until decommissioning in 1999. Sandstone magazines line the river foreshore, their thick walls built to contain an accidental detonation."

These examples show: specific place names, physical details, historical facts, short sentences, no emotional editorialising."""


# ── Validation ─────────────────────────────────────────────────────────────────

def _validate(text: str) -> list[str]:
    """Return list of banned words/phrases found in text. Empty = clean."""
    lower = text.lower()
    return [b for b in BANNED if b in lower]


def _is_ambiguous_title(title: str) -> bool:
    """True if title is too generic to describe without seeing the image."""
    clean = title.strip().lower()
    return bool(AMBIGUOUS_TITLE_PATTERNS.match(clean))


# ── subject_description ────────────────────────────────────────────────────────

def subject_description(
    title: str,
    series: str = "",
    location: str = "",
    year: str = "",
    image_url: str = "",
    max_retries: int = 2,
) -> dict:
    """
    Generate a subject_description metafield for a single product.

    Returns:
      {
        "text":         str,   # the description (20–40 words)
        "needs_review": bool,  # True if title was ambiguous AND no image was available
        "violations":   list,  # banned words found (empty if clean after retries)
      }
    """
    client = _client()

    needs_review = _is_ambiguous_title(title) and not image_url

    details = []
    if series:
        details.append(f"Series: {series}")
    if location:
        details.append(f"Location: {location}")
    if year:
        details.append(f"Year photographed: {year}")

    detail_block = "\n".join(details)

    user_text = f"""Write the `subject_description` metafield for this fine art photograph.

Product title: {title}
{detail_block}

Requirements:
- 20–40 words
- Present tense, observational voice
- Name the specific place, structure, or object — do not be vague
- No title, heading, or label — just the description text
- Do not repeat the product title word for word
{"- NOTE: The title alone is ambiguous. Describe only what you can actually see in the image." if image_url else ""}

Write the subject_description:"""

    for attempt in range(max_retries + 1):
        # Build message content — include image on first attempt if available
        content = []
        if image_url and attempt == 0:
            content.append({
                "type": "image",
                "source": {"type": "url", "url": image_url},
            })
        content.append({"type": "text", "text": user_text})

        # On retry, append explicit retry instruction
        if attempt > 0:
            retry_note = (
                f"\n\nPrevious attempt contained banned words: {violations}. "
                "Rewrite without any of these words or phrases."
            )
            content[-1] = {"type": "text", "text": user_text + retry_note}

        resp = client.messages.create(
            model=MODEL,
            max_tokens=120,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": content}],
        )
        text = resp.content[0].text.strip()
        violations = _validate(text)

        if not violations:
            return {"text": text, "needs_review": needs_review, "violations": []}

        # Will retry unless this was the last attempt
        if attempt < max_retries:
            time.sleep(1)

    # Exhausted retries — return with violations flagged for manual review
    return {"text": text, "needs_review": True, "violations": violations}


# ── Batch generation ───────────────────────────────────────────────────────────

def batch_subject_descriptions(
    products: list[dict],
    delay: float = 1.5,
) -> list[dict]:
    """
    Generate subject_descriptions for a list of products.

    Each product dict should have:
      id, title, series (optional), location (optional),
      year (optional), image_url (optional)

    Returns list of dicts:
      { id, title, subject_description, needs_review, violations, error }

    needs_review=True items should be inspected before pushing to Shopify.
    """
    results = []
    review_count = 0

    for i, p in enumerate(products, 1):
        title = p.get("title", "")
        try:
            result = subject_description(
                title=title,
                series=p.get("series", ""),
                location=p.get("location", ""),
                year=p.get("year", ""),
                image_url=p.get("image_url", ""),
            )
            flagged = result["needs_review"]
            if flagged:
                review_count += 1

            results.append({
                "id":                  p["id"],
                "title":               title,
                "subject_description": result["text"],
                "needs_review":        flagged,
                "violations":          result["violations"],
                "error":               None,
            })

            if i % 25 == 0:
                print(f"  {i}/{len(products)} done  |  flagged for review: {review_count}", flush=True)

        except Exception as e:
            results.append({
                "id":                  p["id"],
                "title":               title,
                "subject_description": None,
                "needs_review":        True,
                "violations":          [],
                "error":               str(e),
            })

        time.sleep(delay)

    return results


# ── Collection description ─────────────────────────────────────────────────────

def collection_description(
    title: str,
    location: str = "",
    year: str = "",
    context: str = "",
    max_words: int = 80,
) -> str:
    """
    Generate a collection/series description for the storefront.
    Returns plain text (no HTML).
    """
    client = _client()

    details = []
    if location:
        details.append(f"Location: {location}")
    if year:
        details.append(f"Photographed: {year}")
    if context:
        details.append(f"Context: {context}")

    prompt = f"""Write a collection description for the Lost Collective online store.

Series: {title}
{chr(10).join(details)}

Requirements:
- {max_words} words maximum
- 2–3 sentences
- Factual and atmospheric — name the place, its history, what makes it significant
- Do not mention "Lost Collective" or "Brett Patman" by name
- No title or heading — body text only
- No calls to action"""

    for attempt in range(3):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=200,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text.strip()
        violations = _validate(text)
        if not violations:
            return text
        time.sleep(1)

    # Return best effort with a warning
    print(f"  WARNING: collection description for '{title}' still has violations after 3 attempts: {violations}")
    return text


# ── product_description ────────────────────────────────────────────────────────

def product_description(
    title: str,
    series: str = "",
    location: str = "",
    year: str = "",
    image_url: str = "",
    existing: str = "",
    max_retries: int = 2,
) -> dict:
    """
    Generate a full product body_html description using Claude Opus.

    Uses vision when image_url is available — Claude looks at the actual
    photograph before writing. Flags ambiguous/unresolvable titles for
    manual review rather than pushing hallucinated copy.

    Returns:
      {
        "text":         str,   # HTML-safe product description (2–3 paragraphs)
        "needs_review": bool,
        "violations":   list,
      }
    """
    client = _client()

    needs_review = _is_ambiguous_title(title) and not image_url

    details = []
    if series:
        details.append(f"Series: {series}")
    if location:
        details.append(f"Location: {location}")
    if year:
        details.append(f"Year photographed: {year}")
    detail_block = "\n".join(details)

    existing_block = ""
    if existing:
        existing_block = f"\n\nExisting description (for reference — rewrite, do not copy):\n{existing}"

    user_text = f"""Write the product page description for this fine art photograph print.

Product title: {title}
{detail_block}{existing_block}

Requirements:
- 2 paragraphs
- First paragraph: describe what is physically visible in the photograph — specific details, scale, materials, light, texture. Present tense.
- Second paragraph: historical or contextual facts about the place. What it was, when it operated, what happened there, why it matters. Past tense for history.
- 60–120 words total
- No title, heading, or label — body text only
- Do not mention "Lost Collective", "Brett Patman", or "this print"
- Australian spelling throughout
- No calls to action, no price references, no framing options
{"- The title alone is ambiguous — describe only what you can see in the image provided." if image_url else "- No image provided — use the title, series, and location to write factual, specific copy. If you cannot write with confidence, say NEEDS_REVIEW."}

Write the description:"""

    violations = []
    text = ""

    for attempt in range(max_retries + 1):
        content = []
        if image_url and attempt == 0:
            content.append({
                "type": "image",
                "source": {"type": "url", "url": image_url},
            })
        prompt = user_text
        if attempt > 0 and violations:
            prompt += (
                f"\n\nPrevious attempt contained banned words: {violations}. "
                "Rewrite completely, avoiding all of these."
            )
        content.append({"type": "text", "text": prompt})

        resp = client.messages.create(
            model=MODEL_OPUS,
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": content}],
        )
        text = resp.content[0].text.strip()

        if "NEEDS_REVIEW" in text:
            return {"text": text.replace("NEEDS_REVIEW", "").strip(),
                    "needs_review": True, "violations": []}

        violations = _validate(text)
        if not violations:
            return {"text": text, "needs_review": needs_review, "violations": []}

        if attempt < max_retries:
            time.sleep(1.5)

    return {"text": text, "needs_review": True, "violations": violations}


# ── CLI test ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    # Quick smoke test — uses title only (no image) to keep it fast
    test_products = [
        {"id": "test-1", "title": "White Bay #03", "series": "White Bay Power Station", "year": "2019"},
        {"id": "test-2", "title": "Turbine Hall", "series": "Wangi Power Station", "year": "2018"},
        {"id": "test-3", "title": "Yummy", "series": "Landscapes", "year": "2021"},
    ]

    print("Testing Claude copy generation...\n")
    results = batch_subject_descriptions(test_products, delay=1.0)
    for r in results:
        flag = " [NEEDS REVIEW]" if r["needs_review"] else ""
        violations = f" [VIOLATIONS: {r['violations']}]" if r["violations"] else ""
        print(f"{r['title']}{flag}{violations}")
        print(f"  {r['subject_description'] or r['error']}")
        print()
