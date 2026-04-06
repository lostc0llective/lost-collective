"""
Create SEO blog posts — Lost Collective
========================================
Publishes location-specific editorial blog posts targeting long-tail search.

Usage:
  op run --env-file=.env.tpl -- python3 shopify/scripts/create_blog_posts.py
  op run --env-file=.env.tpl -- python3 shopify/scripts/create_blog_posts.py --dry-run

Output:
  logs/create_blog_posts.log
"""

import sys, time, argparse, json
from pathlib import Path

LOG_FILE = Path("logs/create_blog_posts.log")
LOG_FILE.parent.mkdir(exist_ok=True)
_log_fh = open(LOG_FILE, "w")

def log(msg):
    print(msg)
    _log_fh.write(msg + "\n")
    _log_fh.flush()

sys.path.insert(0, str(Path(__file__).parent))
from shopify_gql import gql

BLOG_ID = "gid://shopify/Blog/70416924838"

ARTICLE_CREATE = """
mutation articleCreate($article: ArticleCreateInput!) {
  articleCreate(article: $article) {
    article { id handle title publishedAt }
    userErrors { field message }
  }
}
"""

# ── CTA block ─────────────────────────────────────────────────────────────────

def cta_block(collection_handle: str, collection_title: str) -> str:
    return f"""<div style="margin: 48px 0; padding: 32px; background: #f8f8f6; border-left: 3px solid #ebac20;">
<p style="margin: 0 0 8px; font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.08em; color: #666;">The series</p>
<p style="margin: 0 0 20px; line-height: 1.6;">{collection_title} is part of the Lost Collective collection. Fine art prints on Hahnemuhle Photo Rag 308gsm archival paper. Limited editions in M, L, and XL.</p>
<a href="/collections/{collection_handle}" style="display: inline-block; background: #1a1a1a; color: #fff; padding: 12px 24px; text-decoration: none; font-size: 0.85em; letter-spacing: 0.05em; text-transform: uppercase;">View the {collection_title} prints</a>
</div>"""


# ── Posts ─────────────────────────────────────────────────────────────────────

POSTS = [
    {
        "title": "Inside Wangi Power Station",
        "tags": ["wangi-power-station", "nsw", "industrial", "power-station", "lake-macquarie"],
        "seo_title": "Wangi Power Station - Photographs from Inside | Lost Collective",
        "seo_description": "Brett Patman photographed Wangi Power Station across multiple visits. The Lake Macquarie steam turbine plant ran from 1953 to 1986. Fine art prints available.",
        "collection_handle": "wangi-power-station",
        "collection_title": "Wangi Power Station",
        "body_paragraphs": [
            "I have been inside a lot of stopped buildings. Places that were running full tilt when the decision was made to close them, then locked up and left. Most of them have something in common: the evidence of the last shift. Tools left in a particular position. A logbook entry that does not have a following entry. The specific residue of work that stopped without ceremony.",
            "Wangi Power Station has all of that, and more of it than almost anywhere else I have been.",
            "The station was built on the southern shore of Lake Macquarie in 1948. The first generating units came online in 1953. More were added through the late fifties. At its peak the plant was running four steam turbine generators fed by coal barges crossing the lake, producing power that went into the NSW grid and came out as light and heat in homes from Newcastle to Sydney. It ran continuously, three shifts a day, for thirty-eight years before the last unit was decommissioned in 1986.",
            "What that means, in practice, is accumulation. Thirty-eight years of coal combustion worked into every surface. Thirty-eight years of maintenance records, equipment modifications, the particular patina that forms in spaces where heavy industrial work happens continuously for decades. The turbine hall at Wangi does not look like a museum. It looks like a place where the work stopped very recently, and where the evidence of thirty-eight years of work is still fully present.",
            "The A and B stations were built to different specifications. The men who worked there knew the difference by feel long before they could articulate it. The boiler house ran hot year-round. The administration block kept a different kind of record - the paperwork of a large operation, the logistics of getting coal barges across a freshwater lake in all weathers. The workshop held the tools. All of it is still there.",
            "I made the photographs in this series over several visits to the site. What I was trying to do was not document the building in an archival sense - that work had been done - but photograph the specific quality of what happens to a working building in the years after the work stops. The turbines are not rusting in any dramatic way. The structure is sound. The cranes are still on their rails. What is happening is slower and more particular: the light, the dust, the way the lake sits outside windows that were not designed to be looked through for their view.",
            "Wangi Power Station is heritage listed and on the state heritage register. There are plans for the site. In the meantime, it stands on the lake in more or less the condition it was in when the last turbine went quiet in 1986.",
        ],
    },
    {
        "title": "Kandos Cement Works: Sixty-Seven Years in the Valley",
        "tags": ["kandos-cement-works", "nsw", "industrial", "cement", "central-tablelands"],
        "seo_title": "Kandos Cement Works Photography | Inside the Mill | Lost Collective",
        "seo_description": "Kandos Cement Works operated 1920-1987. The plant built a town from scratch in the NSW Central Tablelands. Fine art prints by Brett Patman.",
        "collection_handle": "kandos-cement-works",
        "collection_title": "Kandos Cement Works",
        "body_paragraphs": [
            "There are towns in Australia that exist because of a single industry, and the relationship between the town and the industry is so complete that you cannot talk about one without the other. Kandos is one of them.",
            "In 1916, the location that would become Kandos did not have a name. The Cement and Lime Company selected the site for its limestone deposits - the raw material for cement manufacturing - and laid out a town grid. Workers were needed. Housing was built. A school, a hall, a railway siding. Within a few years there was a functioning plant and a community of people whose livelihoods were inseparable from the production of cement.",
            "Production started in 1920. By the 1940s, Kandos cement had gone into the construction of Sydney Harbour Bridge approaches, rural infrastructure across NSW, and the rapid postwar residential expansion that filled the suburbs. The plant ran through multiple ownership changes, recessions, and the transformation of the Australian construction industry. It closed in 1987, sixty-seven years after it opened.",
            "At its end, the works covered a large area of the valley. Rotary kilns. Ball mills - machines the size of small buildings arranged in long shed rows. A process laboratory. Storage silos. Conveyor systems. The limestone quarry above the town that fed the whole operation. Most of it was left standing when production stopped.",
            "The ball mill drives are the spaces that stay with me. The scale is difficult to communicate in a single photograph - you need the width of the shed, the height of the machinery, the way the light comes through windows that were sized for ventilation rather than illumination. The floor below them holds an accumulation of decades: spilled material, maintenance records, broken equipment, the residue of a process that ran continuously for sixty-seven years.",
            "I photographed the works in 2016. The buildings were intact, accessible, and largely unchanged from the day production stopped. The No. 2 Process Lab in particular was complete - the kind of space where every object tells you what the work was and what the people who did it needed close at hand.",
        ],
    },
    {
        "title": "Callan Park: A Century of Institutional Life in Rozelle",
        "tags": ["callan-park", "nsw", "psychiatric", "heritage", "rozelle", "iron-cove"],
        "seo_title": "Callan Park Rozelle - Photographs of the Former Asylum | Lost Collective",
        "seo_description": "Callan Park has housed the treatment of mental illness since 1878. Brett Patman photographed the Rozelle heritage estate across several visits. Fine art prints.",
        "collection_handle": "callan-park",
        "collection_title": "Callan Park",
        "body_paragraphs": [
            "The land at Callan Park has been used for the treatment of mental illness since 1878. That is not a brief history. In 1878, the suburb of Rozelle was farmland on the western edge of Sydney. The buildings that James Barnet designed that year - sandstone in the Italianate style, set in grounds that sloped down to Iron Cove - went up in a landscape that bore no resemblance to the dense inner suburb that surrounds the estate today.",
            "The idea behind the site was consistent with asylum design of the period: that space and greenery and productive work were part of the treatment. Patients came here from the city and from regional NSW. Some stayed for years. The campus grew around them - new wards added in different architectural periods, different buildings for different categories of patient, the whole ensemble accumulating over a century as the population grew and the theories of treatment changed.",
            "Deinstitutionalisation began in the 1980s. The wards closed progressively as the patient population was moved to community care settings. Buildings that had been in continuous use since the nineteenth century were locked and left. Some sections were repurposed - UTS now occupies part of the estate - but much of the fabric remained as it had been.",
            "What makes Callan Park different from industrial sites is the intimacy of the spaces. These were rooms designed for daily life - sleeping, eating, bathing, the slow passage of days in an institution. The scale is human. The evidence of occupation is different from a factory or a power station: institutional furniture, ward records, the specific quality of light in spaces designed to house people who were not free to leave.",
            "I photographed the site across several visits in 2015. There is a particular quality to October light in the grounds - the old sandstone, the established gardens, the way the Iron Cove foreshore sits below the heritage precinct - that I have not found anywhere else.",
        ],
    },
    {
        "title": "Bradmill Denim: The Yarraville Mill That Made Australian Levi's",
        "tags": ["bradmill-denim", "vic", "industrial", "textile", "yarraville", "levi's"],
        "seo_title": "Bradmill Denim Yarraville - Inside the Factory | Lost Collective",
        "seo_description": "Bradmill Industries made Levi's jeans in Yarraville from 1969 to 1996. Brett Patman photographed the mill after closure. Fine art prints on archival paper.",
        "collection_handle": "bradmill-denim",
        "collection_title": "Bradmill Denim",
        "body_paragraphs": [
            "For twenty-seven years, the Levi's jeans sold in Australia were made in Yarraville. Bradmill Industries held the manufacturing licence from 1969 and ran it until 1996, when import competition from Asian manufacturers made domestic denim production uneconomical. The plant that had woven and finished denim for the country's most recognisable clothing brand was closed.",
            "Yarraville in the early 1990s was already a declining industrial suburb - the kind of inner-Melbourne area where manufacturing had concentrated in the postwar boom and was now contracting as the economy restructured. The Bradmill closure was one of several. The mill building sat as industrial buildings often do: too substantial to knock down without a clear redevelopment plan, not immediately convertible to anything else.",
            "I photographed the mill in 2012. The looms had been removed by then - the heavy machinery was worth something - but the production floor retained the infrastructure of the process. The overhead systems. The loading docks. The dye works with its own infrastructure for the indigo and chemicals that gave the fabric its colour. The finishing areas. The spatial logic of a building designed around machinery that was no longer there was still entirely legible.",
            "Textile manufacturing at industrial scale has a specific atmosphere that I had not encountered before. The buildings are organised differently to metal or food processing. The dust is different. The acoustic quality is different - fabric absorbs sound in a way that concrete and steel do not. The specific history of the Bradmill licence - Australian workers making an American brand in a Melbourne suburb for nearly three decades - sits in the building whether you know it or not.",
            "Bradmill Denim is the earliest series in the Lost Collective collection. The 2012 photographs were made before I had a clear understanding of what the project would become, which in some ways makes them the most direct images I have. I was not thinking about a series. I was photographing a building that I could see was about to be gone.",
        ],
    },
    {
        "title": "Tin City: Built Without Permission on the Lake",
        "tags": ["tin-city", "nsw", "lake-macquarie", "community", "fibro"],
        "seo_title": "Tin City Lake Macquarie - Photographs of the Settlement | Lost Collective",
        "seo_description": "Tin City is a self-built community on the Lake Macquarie foreshore, established in the 1930s. Brett Patman photographed it in 2018. Fine art prints available.",
        "collection_handle": "tin-city",
        "collection_title": "Tin City",
        "body_paragraphs": [
            "Tin City is not a ruin. I want to be clear about that before I describe it, because the photographs could lead you to the wrong conclusion.",
            "It is a settlement - a collection of self-built fibro and corrugated iron structures on the western foreshore of Lake Macquarie that has been continuously occupied since the 1930s. The people who live there built it themselves, without council approval, without architects or developers, to their own specifications and on their own timeline. Some of the original structures have been there for ninety years. None of them were built to last ninety years. They have lasted anyway.",
            "The settlement grew during the Depression. People with few resources and no access to conventional housing built what they could with what they could afford. The lake foreshore was Crown land, technically unavailable for permanent occupation - which is also what made it available to people with nothing. They built, they stayed, they improved what they had built.",
            "Generations have come and gone. The original structures have been extended, modified, rebuilt in parts, let fall where maintenance was not possible or not worth it. The settlement has no consistent architectural language except the language of self-reliance and incremental improvement. What it has is the accumulated evidence of decades of occupancy by people who chose the lake over the suburb.",
            "I photographed Tin City in January 2018. I had known about it for years and kept not going, for the same reason I think a lot of people keep not going: it felt intrusive to photograph a place where people still lived. What changed my mind was a conversation with someone who had grown up there. The place had a history that deserved to be recorded. The people who lived there were not objects of pity or curiosity. They were people who had made a decision about how to live, and the decision had produced something remarkable.",
            "The collection is not a document of poverty. It is a document of a particular kind of resourcefulness, and of what a built environment looks like when every decision in it was made by a specific person for a specific reason, with no developer's brief and no architect's plan.",
        ],
    },
]


def build_body(paragraphs: list[str], cta: str) -> str:
    paras = "\n\n".join(f"<p>{p}</p>" for p in paragraphs)
    return paras + "\n\n" + cta


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    log("=" * 60)
    log("Create Blog Posts - Lost Collective")
    log(f"Mode: {'dry-run' if args.dry_run else 'live'}")
    log(f"Posts: {len(POSTS)}")
    log("=" * 60)

    # Get existing article handles
    q = """query { blog(id: "%s") { articles(first: 100) { edges { node { handle } } } } }""" % BLOG_ID
    r = gql(q)
    existing = {e["node"]["handle"] for e in r["data"]["blog"]["articles"]["edges"]}
    log(f"Existing articles: {len(existing)}")

    created = skipped = errors = 0

    for post in POSTS:
        log(f"\n--- {post['title']}")

        body = build_body(post["body_paragraphs"], cta_block(post["collection_handle"], post["collection_title"]))

        if args.dry_run:
            log(f"  [DRY] Would publish: {post['title']}")
            created += 1
            continue

        resp = gql(ARTICLE_CREATE, {"article": {
            "blogId": BLOG_ID,
            "title": post["title"],
            "body": body,
            "author": {"name": "Brett Patman"},
            "tags": post["tags"],
            "isPublished": True,
        }})

        result = resp["data"]["articleCreate"]
        if result["userErrors"]:
            log(f"  ✗ {result['userErrors']}")
            errors += 1
        else:
            a = result["article"]
            article_gid = a["id"]
            log(f"  ✓ /blogs/blog/{a['handle']} published")

            # Set SEO via metafields
            mf_resp = gql("""
            mutation metafieldsSet($metafields: [MetafieldsSetInput!]!) {
              metafieldsSet(metafields: $metafields) {
                metafields { key }
                userErrors { field message }
              }
            }
            """, {"metafields": [
                {"ownerId": article_gid, "namespace": "global", "key": "title_tag",
                 "type": "single_line_text_field", "value": post["seo_title"]},
                {"ownerId": article_gid, "namespace": "global", "key": "description_tag",
                 "type": "single_line_text_field", "value": post["seo_description"]},
            ]})
            mf_errs = mf_resp["data"]["metafieldsSet"]["userErrors"]
            if mf_errs:
                log(f"  ! SEO errors: {mf_errs}")
            else:
                log(f"  ✓ SEO set")

            created += 1

        time.sleep(0.5)

    log("\n" + "=" * 60)
    log(f"Created: {created}  |  Skipped: {skipped}  |  Errors: {errors}")
    log("=" * 60)


if __name__ == "__main__":
    main()
