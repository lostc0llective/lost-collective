"""
Update location landing pages — third person rewrite
=====================================================
Rewrites all location page body HTML to comply with the Shopify content brief:
no first person, place-focused, factual, specific.

Usage:
  op run --env-file=.env.tpl -- python3 shopify/scripts/update_location_pages.py
  op run --env-file=.env.tpl -- python3 shopify/scripts/update_location_pages.py --dry-run
"""

import sys, time, argparse
from pathlib import Path

LOG_FILE = Path("logs/update_location_pages.log")
LOG_FILE.parent.mkdir(exist_ok=True)
_log_fh = open(LOG_FILE, "w")

def log(msg):
    print(msg)
    _log_fh.write(msg + "\n")
    _log_fh.flush()

sys.path.insert(0, str(Path(__file__).parent))
from shopify_gql import gql

PAGE_UPDATE = """
mutation pageUpdate($id: ID!, $page: PageUpdateInput!) {
  pageUpdate(id: $id, page: $page) {
    page { id handle }
    userErrors { field message }
  }
}
"""


def build_page_html(image_url, location, year, title, body_paragraphs, collection_handle):
    paras = "\n\n".join(f"<p>{p}</p>" for p in body_paragraphs)
    return f"""<div class="location-hero" style="margin-bottom: 40px;">
  <img src="{image_url}" alt="{title}" style="width: 100%; height: 500px; object-fit: cover; display: block;">
</div>

<div class="location-editorial" style="max-width: 720px; margin: 0 auto; padding: 0 20px;">

<p style="font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.1em; color: #888; margin-bottom: 8px;">{location} - {year}</p>

<h1 style="font-size: 2.2em; font-weight: 600; margin-bottom: 24px; line-height: 1.2;">{title}</h1>

{paras}

<div style="margin-top: 48px; padding: 32px; background: #f8f8f6; border-left: 3px solid #ebac20;">
  <p style="margin: 0 0 16px; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.08em; color: #666;">The prints</p>
  <p style="margin: 0 0 24px; font-size: 1em; line-height: 1.6;">Fine art prints on Ilford Galerie Smooth Cotton Rag archival paper. Unframed, framed in sustainably sourced timber, and glass-mounted on Ilford Galerie Metallic Gloss. Limited editions in M, L, and XL. S and XS open edition.</p>
  <a href="/collections/{collection_handle}" style="display: inline-block; background: #1a1a1a; color: #fff; padding: 14px 28px; text-decoration: none; font-size: 0.9em; letter-spacing: 0.05em; text-transform: uppercase;">View the collection</a>
</div>

</div>"""


PAGES = [
    {
        "id": "gid://shopify/Page/698564346022",
        "handle": "wangi-power-station",
        "title": "Wangi Power Station",
        "location": "Wangi Wangi, New South Wales",
        "year": "1948-1986",
        "collection_handle": "wangi-power-station",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/wangi-wangi-power-statio",
        "body": [
            "Wangi Power Station operated on the southern shore of Lake Macquarie from 1953 to 1986, supplying electricity to the NSW grid for 33 years. Construction began in 1948. The first generating units came online in 1953, with additional units added through the late 1950s as demand across the state grew.",
            "At full capacity the station ran 4 steam turbine generators, fed by coal barges that crossed the lake from the northern shore. Workers operated the plant in rotating shifts around the clock. The boiler house, the turbine hall, the A and B stations, and the administrative block each served a distinct function in a facility that never stopped.",
            "Wangi closed in 1986 when newer generating capacity elsewhere in the state made it redundant. The turbines, overhead cranes, and the bulk of the plant infrastructure remained in place after decommissioning. The boiler house accumulated 33 years of combustion residue that no cleaning schedule addressed after the last shift ended.",
            "The station is heritage listed and on the NSW State Heritage Register. The turbine hall, boiler house, and surrounding infrastructure sit largely as they were left.",
        ],
    },
    {
        "id": "gid://shopify/Page/698564378790",
        "handle": "kandos-cement-works",
        "title": "Kandos Cement Works",
        "location": "Kandos, New South Wales",
        "year": "1920-1987",
        "collection_handle": "kandos-cement-works",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/kandos-cement-works_2016",
        "body": [
            "Kandos Cement Works operated from 1920 to 1987 in the Central Tablelands of NSW. The Kandos Cement and Lime Company established the site for its limestone deposits, and the town of Kandos was built alongside the plant to house the workforce. The 2 were inseparable from the start.",
            "At its peak the works ran rotary kilns, ball mill drives, a No. 2 process laboratory, and an extensive conveyor system connecting the limestone quarry above the town to the production floor below. Workers processed raw limestone into Portland cement that went into infrastructure across NSW, including components of the Sydney Harbour Bridge approaches and the postwar suburban expansion.",
            "The plant changed ownership several times over its 67 years and closed in 1987 when the economics of regional cement production shifted. The ball mill drives, the process lab, the kiln infrastructure, and the coal handling equipment remained largely intact after closure.",
            "The site is one of the more complete surviving examples of mid-20th-century cement manufacturing in Australia. The scale of the machinery, particularly the ball mill rows, is not readily communicated without standing in the shed.",
        ],
    },
    {
        "id": "gid://shopify/Page/698564411558",
        "handle": "callan-park",
        "title": "Callan Park",
        "location": "Rozelle, New South Wales",
        "year": "1878-present",
        "collection_handle": "callan-park",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/callan-park_2015_October",
        "body": [
            "Callan Park has operated as a facility for the treatment of mental illness since 1878. The original buildings were designed by colonial architect James Barnet in the Italianate style, constructed in sandstone on a site sloping down to Iron Cove on Sydney's inner west. The design followed the asylum model of the period: space, gardens, and structured work as components of treatment.",
            "The campus grew across successive building periods. Federation-era additions extended the original Barnet buildings. Mid-century blocks were added as the patient population peaked. At its largest, Callan Park housed over 2,000 patients and employed a proportionate permanent staff.",
            "Deinstitutionalisation from the 1980s saw wards close progressively as patients moved to community care settings. Buildings that had been in continuous use for a century were locked and left. UTS now occupies part of the estate. Much of the original fabric, including ward interiors, remains as it was.",
            "The scale of Callan Park is domestic rather than industrial. These were rooms where people slept, ate, and worked through years of institutional life. The architectural vocabulary is different from a factory or a power station, and what the spaces hold as evidence is different too.",
        ],
    },
    {
        "id": "gid://shopify/Page/698564444326",
        "handle": "morwell-power-station",
        "title": "Morwell Power Station",
        "location": "Morwell, Victoria",
        "year": "1956-2014",
        "collection_handle": "morwell-power-station",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/reference-image.jpg?v=16",
        "body": [
            "Morwell Power Station operated in the Latrobe Valley from 1956 to 2014, burning brown coal from the open-cut mines that define the region. Victoria's electricity supply for most of the 20th century came from the Latrobe Valley, and Morwell was one of the stations that carried that load.",
            "Brown coal, or lignite, has lower energy density and higher moisture content than black coal. The Latrobe Valley stations were designed specifically for it. The turbine hall at Morwell was built for the volume and character of this fuel, with equipment sized accordingly. Workers operated the plant across continuous shifts through privatisation of the state's electricity network in the 1990s and into the 2000s.",
            "The station changed ownership several times as the Victorian electricity market restructured. It finally closed in 2014, one of the later brown coal stations to go as the grid moved away from carbon-intensive generation. The turbine hall retained its full complement of equipment after closure.",
            "The Latrobe Valley is not a tourism destination in the conventional sense, and Morwell is not a building that many Victorians have stood inside. The scale and character of the turbine hall reflect a specific industrial moment that is now past.",
        ],
    },
    {
        "id": "gid://shopify/Page/698564477094",
        "handle": "eveleigh-paint-shop",
        "title": "Eveleigh Paint Shop",
        "location": "Eveleigh, New South Wales",
        "year": "1887-present",
        "collection_handle": "eveleigh-paint-shop",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/central-to-eveliegh_2016",
        "body": [
            "The Eveleigh Railway Workshops opened in 1887 to service the rolling stock of the NSW Government Railways. The complex covered 30 hectares on the southern edge of Sydney, with separate facilities for carriage building, blacksmithing, boiler work, and the paint shop where locomotives were finished before returning to service.",
            "The paint shop is one of the largest surviving Victorian-era industrial buildings in Australia. Iron trusses span 40 metres across tracks that could accommodate 12 locomotives simultaneously. The clerestory windows along the roofline were sized for the ventilation a working paint shop required, not for the quality of light that now characterises the interior.",
            "The workshops changed function over their century of operation as steam gave way to diesel and the railway maintenance workforce contracted and expanded with the economy. The paint shop had been out of heavy use for some years before the broader Eveleigh site began its transition to the Australian Technology Park and CarriageWorks arts venue.",
            "The building has been retained and is used for events. The truss structure, the overhead crane infrastructure, and the spatial logic of a building designed to hold large machines remain intact.",
        ],
    },
    {
        "id": "gid://shopify/Page/698564509862",
        "handle": "blayney-abattoir",
        "title": "Blayney Abattoir",
        "location": "Blayney, New South Wales",
        "year": "mid-20th century",
        "collection_handle": "blayney-abattoir",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/blayney-abattior_2016_Ja",
        "body": [
            "Blayney Abattoir served the Central Tablelands district of NSW through most of the 20th century. Municipal abattoirs were standard infrastructure in rural NSW: a local processing facility for livestock raised in the surrounding district, employing a small permanent workforce and supporting the farmers who brought their animals in.",
            "The spatial logic of an abattoir follows the work. Livestock moved through a defined sequence of spaces in one direction. Temperature was maintained throughout. Every surface was designed to be cleaned down at the end of each shift. The architecture makes no concession to anything beyond the process it houses.",
            "Blayney's abattoir closed as regional processing across NSW centralised into larger facilities. The building was left standing with much of its equipment and fitout in place. The tiling, the overhead rail systems, the holding areas, and the processing rooms remained.",
            "The photographs were made in 2016. The building had been closed long enough for the industrial residue to settle, but the layout and purpose of every space was still legible.",
        ],
    },
    {
        "id": "gid://shopify/Page/698564542630",
        "handle": "geelong-b-power-station",
        "title": "Geelong B Power Station",
        "location": "Geelong, Victoria",
        "year": "1954-2015",
        "collection_handle": "geelong-b-power-station",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/geelong-b-power-station_",
        "body": [
            "Geelong B Power Station was commissioned in 1954 on the Corio Bay foreshore, built to provide supplementary generating capacity closer to Melbourne and Geelong than the brown coal stations of the Latrobe Valley. The station was oil-fired, supplied directly from the Shell refinery at Corio via pipeline.",
            "Oil firing gave Geelong B a different character to the coal stations of the Latrobe Valley. The turbine hall was cleaner in some respects, the combustion residue different. Workers operated the plant through the nationalised and then privatised eras of Victorian electricity generation, across 6 decades of shifting ownership and market conditions.",
            "The station closed in 2015 as the economics of generation shifted. The Corio Bay foreshore site had always carried potential for redevelopment, and the closure opened that process. The turbine hall retained its full generating equipment between decommissioning and the subsequent site changes.",
            "The window between closure and demolition is rarely long for industrial sites of this type on waterfront land. The photographs record the turbine hall in the period immediately after operations stopped.",
        ],
    },
    {
        "id": "gid://shopify/Page/698564575398",
        "handle": "newington-armory",
        "title": "Newington Armory",
        "location": "Silverwater, New South Wales",
        "year": "1897-present",
        "collection_handle": "newington-armory",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/newington-armory_2015",
        "body": [
            "Newington Armory was established by the British Navy in 1897 on a bend in the Parramatta River at Silverwater. The site was selected for its distance from population, its river access for resupply by barge, and the natural containment provided by water on 3 sides. The corrugated iron storage magazines built that year were designed for a single purpose: to hold explosives safely.",
            "The armory supplied naval vessels through both world wars and operated as a military and then civilian storage facility through most of the 20th century. When the Department of Defence transferred the site to the NSW Government ahead of the 2000 Sydney Olympics, the athletes' village was built on the inland portions of the estate. The historic armory precinct at the waterfront was retained.",
            "The corrugated iron magazines are among the most complete examples of colonial industrial construction in Australia. The ventilation louvres on the storage buildings were designed to prevent sparks, which also determines the quality of light inside. The river access infrastructure, the heritage buildings, and the layout of the precinct remain largely intact.",
            "The armory is open to the public periodically through the National Parks and Wildlife Service.",
        ],
    },
    {
        "id": "gid://shopify/Page/698564608166",
        "handle": "ashio-copper-mine",
        "title": "Ashio Copper Mine",
        "location": "Ashio, Tochigi, Japan",
        "year": "1610-1973",
        "collection_handle": "ashio-copper-mine",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/ashio-copper-mine_2016_M",
        "body": [
            "Ashio Copper Mine operated in Tochigi Prefecture from 1610 to 1973, making it one of the longest continuously operating mines in Japanese history. The Furukawa family modernised the operation during the Meiji period, building it into one of the largest copper producers in Asia and supplying the raw material for Japan's industrial development.",
            "From the 1880s, smelter runoff from Ashio contaminated the Watarase River system. Downstream farmland in the Kanto plain became toxic. Fish populations collapsed. Rice paddies that had been worked for generations failed. The Ashio pollution incident became the subject of parliamentary inquiry, mass protest, and the forced relocation of the most affected villages. It is recognised as Japan's first industrial pollution disaster.",
            "Production continued regardless. The mine operated through the Meiji and Showa periods and through Japan's postwar economic recovery, closing in 1973 after 363 years of continuous operation. The site now operates as a heritage museum.",
            "The mine infrastructure, ore processing facilities, and company town buildings are partly preserved and partly in the process of return to the mountain. The photographs were made across both zones in 2016.",
        ],
    },
    {
        "id": "gid://shopify/Page/698564640934",
        "handle": "kinugawa-kan",
        "title": "Kinugawa Kan",
        "location": "Nikko, Tochigi, Japan",
        "year": "1970s-2000s",
        "collection_handle": "kinugawa-kan",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/kinugawa-kan_2016_May_3.",
        "body": [
            "Kinugawa Kan was a resort hotel in the Kinugawa Onsen district of Tochigi Prefecture, one of many large hotels built along the Kinugawa River during Japan's postwar economic boom to accommodate the domestic group travel market. Company retreats, package tours, and organised group bookings sustained the district through the Showa period.",
            "The resort economy of Kinugawa changed in the 1990s. The bubble economy collapsed, corporate travel budgets contracted, and younger Japanese shifted toward independent travel. Occupancy fell across the district. Hotels that had been profitable through the boom found themselves unable to service their debts. Kinugawa Kan was among those that closed and were left standing.",
            "The hotel's closure left the building intact. Guest rooms with their tatami and engawa corridors, the banquet halls, the lobby, and the dining areas were sealed as they stood. The engawa corridors that connected interior rooms to views of the river and mountain were a standard feature of traditional resort hotel design; at Kinugawa Kan, with the hotel empty, the afternoon light through those corridors had no function except to move across the floor.",
            "The photographs were made inside the hotel in 2016.",
        ],
    },
    {
        "id": "gid://shopify/Page/698564673702",
        "handle": "bathurst-gasworks",
        "title": "Bathurst Gasworks",
        "location": "Bathurst, New South Wales",
        "year": "1875-1970s",
        "collection_handle": "bathurst-gasworks",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/bathurst-gasworks_2016_J",
        "body": [
            "Bathurst Gasworks began producing coal gas in 1875, supplying the town's street lighting and domestic and industrial users. The plant operated a coal carbonisation process: raw coal was heated in sealed retort chambers to produce combustible gas, which was then purified and piped into the town's distribution mains. Spent coke was removed and sold as a secondary product.",
            "The retort house was the operational centre of the works. Retort workers charged and discharged the chambers on a continuous cycle, in conditions that were hot regardless of season. The work required precision and physical endurance. The brickwork of the retort house absorbed the heat and the byproducts of the process over nearly a century of operation.",
            "Natural gas replaced town gas progressively from the 1960s as the distribution network extended into regional centres. Bathurst Gasworks became redundant and closed. The site was retained as a heritage facility and is one of the more intact surviving gasworks complexes in NSW.",
            "The retort house, the coal storage infrastructure, and the purification equipment remain on site. The photographs were made there in 2016.",
        ],
    },
    {
        "id": "gid://shopify/Page/698564706470",
        "handle": "peters-ice-cream-factory",
        "title": "Peters' Ice Cream Factory",
        "location": "Minchinbury, New South Wales",
        "year": "mid-20th century-2010s",
        "collection_handle": "peters-ice-cream-factory",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/peters-ice-cream_2016_Fe",
        "body": [
            "Peters' Ice Cream, founded in Sydney in 1907, is one of Australia's oldest food brands. The Minchinbury facility in Western Sydney was built to service a national market, positioned for road and rail access to distribution networks across NSW and beyond. Nestlé acquired the Peters' brand in 1990.",
            "Ice cream manufacturing at industrial scale is a cold chain operation. The production floor ran at temperatures consistent with the product from mixing through to packaging. The equipment, including mixing tanks, extrusion lines, freezer tunnels, and hardening rooms, was arranged around the sequence of that process. Workers moved through a facility designed to keep the product at temperature at every stage.",
            "Production at Minchinbury wound down as Nestlé rationalised its Australian manufacturing operations. The factory closed and sat. The stainless steel and tile surfaces of the production floor, the cold rooms stripped of refrigeration equipment, and the loading infrastructure remained.",
            "The photographs were made in the factory in 2016.",
        ],
    },
    {
        "id": "gid://shopify/Page/698564739238",
        "handle": "mungo-scott-flour-mill",
        "title": "Mungo Scott Flour Mill",
        "location": "Summer Hill, New South Wales",
        "year": "1906-2000s",
        "collection_handle": "mungo-scott-flour-mill",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/mungo-scott-flour-mill_2",
        "body": [
            "Mungo Scott Flour Mill was built in 1906 on a railway siding in Summer Hill, 3 kilometres from the Sydney CBD. The site provided rail access for wheat arriving from country NSW and proximity to the bakeries and distributors that took the finished product. The mill ran on steam initially and was later converted to electric power.",
            "The milling equipment, including roller mills, sifters, purifiers, and grain elevators that moved wheat from the railway siding to storage bins to the production floor, was installed progressively over the mill's operating life. Newer equipment was added alongside older as technology changed. A century of flour dust worked into every surface and joint in the building.",
            "The mill ceased production in the early 2000s. Its heritage significance was recognised, and the building was retained while the future of the site was determined. The milling machinery, integral to the structure, remained largely in place. The wooden floors that had taken a century of trolleys and sacks held that record.",
            "The mill has since been converted to residential use, with the heritage fabric retained as part of the development.",
        ],
    },
    {
        "id": "gid://shopify/Page/698564772006",
        "handle": "lewisham-hospital",
        "title": "Lewisham Hospital",
        "location": "Lewisham, New South Wales",
        "year": "1890s-2010s",
        "collection_handle": "lewisham-hospital",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/Copy_2_1a9ed868-d9c5-42c",
        "body": [
            "Lewisham Hospital was established by the Sisters of the Little Company of Mary in the 1890s on a site in Sydney's inner west. It served the Catholic community of the district and expanded through the early 20th century as the surrounding suburbs developed. By mid-century it operated as a general hospital with full acute care, maternity, and surgical facilities.",
            "Catholic hospitals in Australia occupied a particular institutional role, funded and managed by religious orders but serving the broader community. The physical fabric of Lewisham reflected this, with the spatial language and decorative elements of a religious institution built into a working medical facility. Wards, operating theatres, and administrative spaces accumulated across different building periods over more than a century.",
            "The hospital closed as the broader reorganisation of Sydney's health network proceeded. The inner-west site, well-served by public transport and close to the city, carried value for redevelopment. Heritage provisions protected the original buildings while the site's future was determined.",
            "The building showed the full history of a long-operating hospital: successive modifications, equipment from different eras, the specific evidence of a place where medical work was done continuously across many decades.",
        ],
    },
    {
        "id": "gid://shopify/Page/698564804774",
        "handle": "waterfall-sanatorium",
        "title": "Waterfall Sanatorium",
        "location": "Waterfall, New South Wales",
        "year": "1909-1975",
        "collection_handle": "waterfall-sanatorium",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/reference-image_d0c6abcf",
        "body": [
            "Waterfall Sanatorium was built by the NSW Government in 1909 to treat tuberculosis, then the leading cause of death in the state. The site, in the bush south of Sydney at the edge of what became the Royal National Park, was selected for its climate and isolation. Medical consensus of the period held that fresh air, sunshine, and rest in a suitable environment could arrest the disease.",
            "The pavilion plan design placed separate weatherboard wards for men and women in the bush, with open verandahs on all sides for maximum ventilation and sun exposure. Patients came from Sydney and regional NSW and stayed for months or years. The isolation was both therapeutic and practical: a contagious disease managed in a contained location, with the bush as the boundary.",
            "Effective drug treatment for tuberculosis became available in the early 1950s. The long-stay patient population declined over the following 2 decades. Waterfall closed in 1975 after 66 years of operation. The weatherboard pavilions were left standing in the bush.",
            "The verandah spaces are what distinguish Waterfall from any other building in the series. Designed to face patients toward maximum bush air and light, they dissolve the boundary between interior and exterior in a way no contemporary building attempts.",
        ],
    },
    {
        "id": "gid://shopify/Page/698564837542",
        "handle": "bradmill-denim",
        "title": "Bradmill Denim",
        "location": "Yarraville, Victoria",
        "year": "1969-1996",
        "collection_handle": "bradmill-denim",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/bradmill-denim_2012_Marc",
        "body": [
            "Bradmill Industries held the Levi's manufacturing licence for Australia from 1969 to 1996, producing denim at its Yarraville mill in Melbourne's inner west for the full 27 years. The mill wove, dyed, and finished the fabric that went into the most widely sold jeans brand in the country. When import competition from Asian manufacturers made domestic production uneconomical, the mill closed.",
            "Textile manufacturing at this scale required specialised infrastructure. The loom shed housed wide industrial looms in long rows. The dye works ran the indigo and chemical processes that gave the fabric its colour. Finishing and quality control occupied separate areas. Workers moved fabric through a defined sequence from raw material to finished product.",
            "Yarraville in the 1990s was already a contracting industrial suburb, with manufacturing closing across the area as Melbourne's economy restructured. The Bradmill closure was one of several. The mill building, too substantial to demolish without a development plan, sat after the looms were removed.",
            "The photographs were made inside the mill in 2012, the earliest series in the Lost Collective collection. The production infrastructure remained largely intact.",
        ],
    },
    {
        "id": "gid://shopify/Page/698564870310",
        "handle": "tin-city",
        "title": "Tin City",
        "location": "Lake Macquarie, New South Wales",
        "year": "1930s-present",
        "collection_handle": "tin-city",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/tin-city_2018_January-24",
        "body": [
            "Tin City is a settlement on the western foreshore of Lake Macquarie, built from fibro and corrugated iron by its occupants without council approval from the 1930s onwards. The land is Crown land. The structures have no planning approval. They have been there for 90 years.",
            "The settlement grew during the Depression, when access to conventional housing was beyond what most people could manage. The lake foreshore was technically unavailable for permanent settlement, which also meant it was unpoliced as such. People built what they could afford with what they could find. They stayed. They improved what they had built. Their children stayed after them.",
            "Tin City has no consistent architectural vocabulary except the logic of self-build: each structure reflects the decisions of a specific person at a specific moment, extended and modified as circumstances changed. There is no developer's brief. There is no street grid. There are structures that have been continuously occupied for 9 decades on land where no structure should legally stand.",
            "The photographs were made in January 2018. The settlement is not derelict. Most of it is actively occupied. What distinguishes it is not decay but the specific character of a built environment assembled entirely outside institutional processes.",
        ],
    },
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    log("=" * 60)
    log("Update Location Pages — third person rewrite")
    log(f"Mode: {'dry-run' if args.dry_run else 'live'}")
    log(f"Pages: {len(PAGES)}")
    log("=" * 60)

    updated = errors = 0

    for p in PAGES:
        log(f"\n[{PAGES.index(p)+1}/{len(PAGES)}] {p['title']}")

        body = build_page_html(
            image_url=p["image_url"],
            location=p["location"],
            year=p["year"],
            title=p["title"],
            body_paragraphs=p["body"],
            collection_handle=p["collection_handle"],
        )

        if args.dry_run:
            log(f"  [DRY] Would update /pages/{p['handle']}")
            updated += 1
            continue

        resp = gql(PAGE_UPDATE, {"id": p["id"], "page": {"body": body}})
        result = resp["data"]["pageUpdate"]
        if result["userErrors"]:
            log(f"  ✗ {result['userErrors']}")
            errors += 1
        else:
            log(f"  ✓ /pages/{p['handle']} updated")
            updated += 1

        time.sleep(0.3)

    log("\n" + "=" * 60)
    log(f"Updated: {updated}  |  Errors: {errors}")
    log("=" * 60)


if __name__ == "__main__":
    main()
