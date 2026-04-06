"""
Create location landing pages — Lost Collective
================================================
Builds /pages/{series-handle} editorial pages for all major series.
Format mirrors the White Bay Power Station pilot page.

Each page: hero image, location/year byline, editorial copy (~400 words),
collection CTA. SEO title and meta set via metafields mutation.

Usage:
  op run --env-file=.env.tpl -- python3 shopify/scripts/create_location_pages.py
  op run --env-file=.env.tpl -- python3 shopify/scripts/create_location_pages.py --dry-run

Output:
  logs/create_location_pages.log
"""

import sys, time, argparse
from pathlib import Path

LOG_FILE = Path("logs/create_location_pages.log")
LOG_FILE.parent.mkdir(exist_ok=True)
_log_fh = open(LOG_FILE, "w")

def log(msg):
    print(msg)
    _log_fh.write(msg + "\n")
    _log_fh.flush()

sys.path.insert(0, str(Path(__file__).parent))
from shopify_gql import gql

# ── Page template ─────────────────────────────────────────────────────────────

def build_page_html(image_url: str, location: str, year: str, title: str,
                    body_paragraphs: list[str], collection_handle: str) -> str:
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
  <p style="margin: 0 0 24px; font-size: 1em; line-height: 1.6;">Fine art prints on Hahnemuhle Photo Rag 308gsm archival paper. Unframed, framed, and glass-mounted options. Limited editions in M, L, and XL. S and XS open edition.</p>
  <a href="/collections/{collection_handle}" style="display: inline-block; background: #1a1a1a; color: #fff; padding: 14px 28px; text-decoration: none; font-size: 0.9em; letter-spacing: 0.05em; text-transform: uppercase;">View the collection</a>
</div>

</div>"""


# ── Series data ───────────────────────────────────────────────────────────────

SERIES = [
    {
        "handle": "wangi-power-station",
        "title": "Wangi Power Station",
        "location": "Wangi Wangi, New South Wales",
        "year": "1948-1986",
        "collection_handle": "wangi-power-station",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/wangi-wangi-power-statio",
        "seo_title": "Wangi Power Station Photography Prints | Lost Collective",
        "seo_description": "Fine art prints from Wangi Power Station, Lake Macquarie NSW. Decommissioned 1986. Limited edition archival prints of the turbine hall, boiler house and A/B stations.",
        "body": [
            "The turbines at Wangi ran for thirty-eight years before they went quiet. From 1948, when construction crews broke ground on the southern shore of Lake Macquarie, to 1986 when the last generating unit was shut down, Wangi Power Station put electricity into the NSW grid that lit homes from Newcastle to Sydney.",
            "The station was built in stages. The first units came online in 1953. More were added through the late fifties as demand grew. At its peak, Wangi was running four steam turbine generators fed by coal barges crossing the lake. The boiler house - the loud heart of the place - ran around the clock, three shifts, every day.",
            "The A and B stations were built to different specifications. Walk from one to the other and the ceilings change, the machinery layout changes, the light changes. The men who worked there knew the difference by feel. The rest of the building - the administration block, the workshops, the coal handling infrastructure along the waterfront - accumulated over decades without any particular plan.",
            "After decommissioning, the site sat largely intact. The turbines did not go anywhere. The overhead cranes stayed on their rails. What coal dust and oil residue had worked into every surface over thirty-eight years of continuous operation stayed there too. The building did not deteriorate so much as accumulate.",
            "These photographs were made inside Wangi before restoration work changed the interior. They are a record of a working building in the years after the work stopped.",
        ],
    },
    {
        "handle": "kandos-cement-works",
        "title": "Kandos Cement Works",
        "location": "Kandos, New South Wales",
        "year": "1920-1987",
        "collection_handle": "kandos-cement-works",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/kandos-cement-works_2016",
        "seo_title": "Kandos Cement Works Photography Prints | Lost Collective",
        "seo_description": "Fine art prints from Kandos Cement Works, NSW. Operating 1920-1987. Archival photography of kilns, ball mills, process labs and the industrial landscape of the Central Tablelands.",
        "body": [
            "The town of Kandos was built for the cement works. That is not a figure of speech - in 1916, Kandos Kandos did not exist. The Cement and Lime Company selected the site for its limestone deposits, laid out a town grid, and within a few years had a functioning plant and a community of workers living in the houses they had built nearby.",
            "Production started in 1920. By the 1940s, Kandos cement had gone into the construction of Sydney Harbour Bridge approaches, rural infrastructure across NSW, and the rapid postwar residential expansion that filled the suburbs. The plant ran through multiple ownership changes, recessions, and the transformation of the Australian construction industry.",
            "The works closed in 1987. At its end, the plant covered a large area of the valley - rotary kilns, ball mills, a process laboratory, storage silos, conveyor systems, and the limestone quarry above the town that fed the whole operation. Most of it was left standing.",
            "The scale of the interior spaces is difficult to communicate in a single photograph. The ball mill drives - machines the size of small buildings - sit in long shed rows. The cement mill floor holds an accumulation of decades: spilled material, maintenance records, broken equipment, the residue of a process that ran continuously for sixty-seven years.",
            "These photographs were made inside the works in 2016. The buildings were intact, accessible, and largely unchanged from the day production stopped.",
        ],
    },
    {
        "handle": "callan-park",
        "title": "Callan Park",
        "location": "Rozelle, New South Wales",
        "year": "1878-present",
        "collection_handle": "callan-park",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/callan-park_2015_October",
        "seo_title": "Callan Park Photography Prints | Lost Collective",
        "seo_description": "Fine art prints from Callan Park, Rozelle NSW. The former Broughton Hall Psychiatric Clinic, operating since 1878. Archival photography of the asylum buildings and grounds.",
        "body": [
            "The land at Callan Park has been used for the treatment of mental illness since 1878. The first buildings went up that year under the direction of colonial architect James Barnet - sandstone structures in the Italianate style, set in grounds that sloped down to Iron Cove. The idea, consistent with asylum design of the period, was that space and greenery and productive work were part of the treatment.",
            "The campus grew over the following century. New wards were added in different architectural periods - the original Barnet buildings, the federation-era additions, the mid-century blocks built when the patient population was at its peak. At its largest, Callan Park housed over two thousand patients and employed a small city worth of staff.",
            "Deinstitutionalisation began in the 1980s. Wards closed progressively as the population was moved to community care settings. Buildings that had been in continuous use for a century were locked up and left. Some were repurposed - the University of Technology Sydney now occupies part of the estate - but much of the fabric remained as it had been.",
            "What makes Callan Park different from other heritage sites is the intimacy of it. These were spaces designed for daily life - sleeping, eating, bathing, working - not for industry or commerce. The scale is human. The evidence of occupation is different: institutional furniture, ward records, the specific light of spaces that were never meant to be photographed.",
            "These photographs were made across several visits to the site in 2015.",
        ],
    },
    {
        "handle": "morwell-power-station",
        "title": "Morwell Power Station",
        "location": "Morwell, Victoria",
        "year": "1956-2014",
        "collection_handle": "morwell-power-station",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/reference-image.jpg?v=16",
        "seo_title": "Morwell Power Station Photography Prints | Lost Collective",
        "seo_description": "Fine art prints from Morwell Power Station, Latrobe Valley VIC. Brown coal-fired generator operating 1956-2014. Limited edition archival photography of the turbine hall and infrastructure.",
        "body": [
            "The Latrobe Valley sits on one of the largest deposits of brown coal in the world. For most of the twentieth century, that deposit powered Victoria. Morwell Power Station was part of that system - a brown coal-fired plant commissioned in 1956 that ran for nearly sixty years before the economics of electricity generation made it unviable.",
            "Brown coal - lignite - burns differently to black coal. Lower energy density, higher moisture content, a different quality of combustion. The Latrobe Valley plants were designed specifically for it, with equipment sized to the fuel. The turbine hall at Morwell reflected this: large-scale, built for continuous heavy operation, without the refinement of stations designed for higher-value fuel.",
            "Morwell operated through the privatisation of Victoria's electricity network in the 1990s and into the twenty-first century, changing ownership several times as the market restructured. The plant finally closed in 2014, one of the later brown coal stations to go as the network shifted away from carbon-intensive generation.",
            "The photographs in this series were made inside Morwell shortly after closure. The turbine hall retained its full complement of generating equipment. The scale of the space - the overhead cranes, the turbine casings, the switchgear rows - was unchanged from the working plant.",
        ],
    },
    {
        "handle": "eveleigh-paint-shop",
        "title": "Eveleigh Paint Shop",
        "location": "Eveleigh, New South Wales",
        "year": "1887-2000s",
        "collection_handle": "eveleigh-paint-shop",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/central-to-eveliegh_2016",
        "seo_title": "Eveleigh Railway Workshops Photography Prints | Lost Collective",
        "seo_description": "Fine art prints from the Eveleigh Railway Workshops paint shop, Sydney NSW. Built 1887. Archival photography of the historic locomotive maintenance facility.",
        "body": [
            "The Eveleigh Railway Workshops opened in 1887 to service the rolling stock of the NSW Government Railways. The complex covered thirty hectares in what was then the southern fringe of Sydney - carriage workshops, blacksmith shops, a boiler shop, and the paint shop where locomotives were finished before returning to service.",
            "The paint shop is one of the largest surviving Victorian-era industrial buildings in Australia. The roof structure - iron trusses spanning forty metres across tracks that could accommodate twelve locomotives simultaneously - was designed for a specific industrial purpose and built to last. It has.",
            "The workshops changed character several times over their century of operation. Steam gave way to diesel. The workforce contracted and expanded with the economy. Sections of the complex were periodically closed as functions were centralised or moved. The paint shop itself had been out of heavy use for years before the broader site transition began.",
            "The Eveleigh site has been redeveloped progressively since the 1990s - the Australian Technology Park, the CarriageWorks arts venue, residential towers along the southern boundary. The paint shop has been retained and is used for events. These photographs were made when the building was in a transitional state: the structure preserved, the industrial interior largely intact.",
            "What the photographs show is the quality of the light inside a building designed around the movement of large machines - the clerestory windows, the way the afternoon sun moves across the truss structure, the relationship between the building's scale and the human figures that occasionally appear in the frames.",
        ],
    },
    {
        "handle": "blayney-abattoir",
        "title": "Blayney Abattoir",
        "location": "Blayney, New South Wales",
        "year": "mid-1900s",
        "collection_handle": "blayney-abattoir",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/blayney-abattior_2016_Ja",
        "seo_title": "Blayney Abattoir Photography Prints | Lost Collective",
        "seo_description": "Fine art prints from Blayney Abattoir, NSW Central Tablelands. Archival photography of the abandoned rural processing facility, fine art prints on archival paper.",
        "body": [
            "Rural abattoirs were infrastructure. Every town of any size in rural NSW had one - a municipal facility that processed locally raised livestock, supported local farmers, and employed a small permanent workforce. Blayney's abattoir served the Central Tablelands district for decades.",
            "The work done in these buildings was not decorative. The spaces were designed for function: for moving animals through a defined process efficiently, for maintaining temperatures that preserved the product, for cleaning down at the end of each shift. The architecture follows the work. Nothing is superfluous.",
            "When Blayney's abattoir closed - as rural processing facilities across NSW did in the latter decades of the twentieth century, replaced by larger centralised operations - the building was left as it stood. The equipment stayed. The tiling, installed to be cleaned rather than admired, accumulated the history of the place.",
            "These photographs were made in 2016. The building had been out of operation long enough for the industrial patina to have fully set, but recent enough that the spatial logic of the facility was still legible. This is not a ruin - it is a stopped machine.",
        ],
    },
    {
        "handle": "geelong-b-power-station",
        "title": "Geelong B Power Station",
        "location": "Geelong, Victoria",
        "year": "1954-2015",
        "collection_handle": "geelong-b-power-station",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/geelong-b-power-station_",
        "seo_title": "Geelong B Power Station Photography Prints | Lost Collective",
        "seo_description": "Fine art prints from Geelong B Power Station, Victoria. Oil-fired generator commissioned 1954. Archival photography of the turbine hall and infrastructure.",
        "body": [
            "Geelong B Power Station was built on the Corio Bay foreshore at a time when Victoria's industrial growth was outpacing its power supply. The plant was commissioned in 1954, oil-fired, and designed to supplement the brown coal generators of the Latrobe Valley with peaking capacity closer to the load centres of Melbourne and Geelong.",
            "Oil firing suited the site - there was no coal infrastructure on the bay foreshore, but fuel oil could be piped directly from the nearby Shell refinery at Corio. The turbine hall was configured accordingly: different in character to the coal stations of the Latrobe Valley, cleaner in some respects, with the particular atmosphere of a plant that had been burning liquid fuel rather than solid.",
            "The station ran for over sixty years under various ownership arrangements before the economics of generation made continued operation unviable. It was decommissioned in 2015. The waterfront site it occupied was always valuable real estate; redevelopment has since proceeded.",
            "The photographs in this series were made inside Geelong B in the period between decommissioning and demolition - a window that in industrial heritage terms is rarely long. They record a turbine hall that had been in continuous service since 1954 and showed the accumulated evidence of that service in every surface.",
        ],
    },
    {
        "handle": "newington-armory",
        "title": "Newington Armory",
        "location": "Silverwater, New South Wales",
        "year": "1897-present",
        "collection_handle": "newington-armory",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/newington-armory_2015",
        "seo_title": "Newington Armory Photography Prints | Lost Collective",
        "seo_description": "Fine art prints from Newington Armory, Silverwater NSW. Colonial gunpowder magazine built 1897, site of 2000 Sydney Olympics. Archival photography of the heritage buildings.",
        "body": [
            "The British Navy chose this bend in the Parramatta River in 1897 for the same reason that gunpowder magazines have always been placed near water: it was far enough from population to be safe, accessible by barge for resupply, and bounded on three sides by the river. The corrugated iron storage buildings they constructed were designed to one specification - hold the explosives, survive the climate, and if something went wrong, fail in a direction that caused minimum damage.",
            "The armory supplied naval vessels throughout both world wars and operated as a military and then civilian storage facility through most of the twentieth century. When the Department of Defence transferred the site to the NSW Government in the 1990s, the buildings - remarkably intact for their age - came with it.",
            "The 2000 Sydney Olympics used the Newington site as the athletes' village. After the Games, the residential buildings were sold as housing. The historic armory precinct at the waterfront was retained as a heritage site and opened periodically to the public.",
            "The corrugated iron buildings that store the guns and powder are among the most complete examples of colonial industrial construction in the country. The light inside them - filtered through ventilation louvres designed to prevent sparks - is unlike any other industrial interior. These photographs were made inside the armory during one of the periodic access events.",
        ],
    },
    {
        "handle": "ashio-copper-mine",
        "title": "Ashio Copper Mine",
        "location": "Ashio, Tochigi, Japan",
        "year": "1610-1973",
        "collection_handle": "ashio-copper-mine",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/ashio-copper-mine_2016_M",
        "seo_title": "Ashio Copper Mine Photography Prints | Lost Collective",
        "seo_description": "Fine art prints from Ashio Copper Mine, Tochigi Japan. Operating 1610-1973, site of Japan's first industrial pollution disaster. Archival photography on fine art paper.",
        "body": [
            "Copper has been mined at Ashio since 1610. By the Meiji period, the Furukawa family had modernised the operation into one of the largest copper producers in Asia - a transformation that built the infrastructure for Japan's industrial development and simultaneously caused the country's first recorded industrial pollution disaster.",
            "From the 1880s, smelter waste from Ashio was contaminating the Watarase River system. Downstream rice paddies in the Kanto plain failed. Fish died. Farmers who had worked the same land for generations found their fields toxic and their livelihoods destroyed. The Ashio pollution incident became a defining event in Japanese environmental and labour history - the subject of parliamentary inquiry, mass protest, and eventually forced relocation of the most affected villages.",
            "Production continued regardless. The mine operated through the Meiji and Showa periods, through the Second World War, through Japan's postwar economic recovery, closing finally in 1973. At its closure, Ashio had been in operation for 363 years.",
            "The mine site now operates as a heritage museum. The industrial infrastructure - ore processing facilities, the company town buildings, the mine entrances in the valley walls - is partly preserved and partly in the process of return to the mountain. These photographs were made in the preserved and transitional zones of the site in 2016.",
        ],
    },
    {
        "handle": "kinugawa-kan",
        "title": "Kinugawa Kan",
        "location": "Nikko, Tochigi, Japan",
        "year": "1970s-2000s",
        "collection_handle": "kinugawa-kan",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/kinugawa-kan_2016_May_3.",
        "seo_title": "Kinugawa Kan Photography Prints | Lost Collective",
        "seo_description": "Fine art prints from Kinugawa Kan, an abandoned hotel in Nikko, Tochigi Japan. Archival photography of the collapsed spa resort interiors.",
        "body": [
            "The Kinugawa Onsen resort district in Tochigi Prefecture was built for the postwar Japanese middle class. Hot spring resorts along the Kinugawa River filled through the Showa economic boom - large hotels catering to group tours, company retreats, and the domestic travel that became possible as disposable income rose. Kinugawa Kan was one of them.",
            "The resort economy that sustained these hotels changed in the 1990s. The bubble burst. Corporate travel budgets contracted. The travel patterns of younger Japanese shifted away from the group resort model toward independent travel. Hotels that had been profitable through the boom found themselves suddenly unviable. Across the Kinugawa valley and through onsen districts across Japan, large resort hotels closed and were left standing.",
            "Kinugawa Kan's closure left the building intact. The furniture remained. The tatami, the engawa corridors connecting rooms that looked out over the river, the dining hall set for a meal that was never served - the building was frozen at the moment of closure. The specific aesthetics of Showa-era resort architecture - the combination of traditional Japanese spatial organisation with modernist construction methods and Western decorative elements - were preserved in full.",
            "These photographs were made inside the hotel in 2016. The building showed several years of abandonment but retained the spatial logic and material evidence of its operating period. The engawa light in particular - the quality of afternoon sun moving across corridor floors designed to connect interior space with a view of water and mountain - was unlike anything I had photographed before.",
        ],
    },
    {
        "handle": "bathurst-gasworks",
        "title": "Bathurst Gasworks",
        "location": "Bathurst, New South Wales",
        "year": "1875-1970s",
        "collection_handle": "bathurst-gasworks",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/bathurst-gasworks_2016_J",
        "seo_title": "Bathurst Gasworks Photography Prints | Lost Collective",
        "seo_description": "Fine art prints from the Bathurst Gasworks, NSW. Coal gas production facility operating from 1875. Archival photography of the retort house and historic industrial infrastructure.",
        "body": [
            "Town gas came to Bathurst in 1875. The gasworks built to produce it sat on the eastern edge of the town centre - a coal carbonisation plant that converted raw coal into combustible gas for street lighting, domestic cooking, and the industrial applications that gas enabled. The retort house where coal was heated in sealed chambers to produce gas was the operational heart of the facility.",
            "Coal gas production was dirty, precise work. The retorts had to be charged and discharged on a cycle - coal in, coke out, gas into the purification system and then into the distribution mains. The men who did this work did it through every shift, in every season, in conditions that were hot in summer and still hot in winter because the retorts never cooled.",
            "Natural gas replaced town gas progressively from the 1960s. The Bathurst gasworks, like hundreds of similar plants across regional Australia, became redundant as the distribution network reached regional centres. The plant closed and was retained as a heritage site - one of the few relatively intact gasworks complexes remaining in NSW.",
            "The retort house is the space that rewards time. The brickwork absorbs the history of the process - coal tar, combustion residue, the accumulated soot of a century of operation. The light inside is specific to the clerestory windows and the particular colour of that saturation. These photographs were made there in 2016.",
        ],
    },
    {
        "handle": "peters-ice-cream-factory",
        "title": "Peters' Ice Cream Factory",
        "location": "Minchinbury, New South Wales",
        "year": "1920s-2010s",
        "collection_handle": "peters-ice-cream-factory",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/peters-ice-cream_2016_Fe",
        "seo_title": "Peters Ice Cream Factory Photography Prints | Lost Collective",
        "seo_description": "Fine art prints from the Peters' Ice Cream Factory, Minchinbury NSW. Production facility for Australia's oldest ice cream brand. Archival photography of the industrial interior.",
        "body": [
            "Peters' ice cream is one of the oldest food brands in Australia. The company was founded in Sydney in 1907 by Fred Peters, an American who had been making ice cream in New Zealand. The Minchinbury factory was built to service a national market from a site in Western Sydney with good road and rail access.",
            "Ice cream manufacturing at industrial scale is a cold, precise business. The production floor ran at temperatures that preserved the product from mix to packaging. The equipment - mixing tanks, extrusion lines, freezer tunnels, hardening rooms - was designed for continuous production runs and cleaned down between batches. The architecture of the factory followed the cold chain.",
            "The Peters' brand changed ownership multiple times over its century of operation - Nestlé acquired it in 1990 - and production at Minchinbury eventually wound down as manufacturing was rationalised. The factory closed and sat.",
            "What a food processing facility looks like after it stops is different from other industrial buildings. The stainless steel and tile surfaces clean up differently than cast iron and brick. The specific smell of the product lingers. The cold rooms, stripped of their refrigeration equipment, become spaces with an unusual acoustic quality - insulated, dense, without reverberation. These photographs were made in the factory in 2016.",
        ],
    },
    {
        "handle": "mungo-scott-flour-mill",
        "title": "Mungo Scott Flour Mill",
        "location": "Summer Hill, New South Wales",
        "year": "1906-2000s",
        "collection_handle": "mungo-scott-flour-mill",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/mungo-scott-flour-mill_2",
        "seo_title": "Mungo Scott Flour Mill Photography Prints | Lost Collective",
        "seo_description": "Fine art prints from Mungo Scott Flour Mill, Summer Hill NSW. Steam-powered flour mill built 1906. Archival photography of the mill machinery and historic industrial interior.",
        "body": [
            "The Mungo Scott mill was built in 1906 on a railway siding in Summer Hill, three kilometres from the centre of Sydney. Flour milling requires grain in and flour out - the rail access that allowed wheat to arrive from country NSW and the proximity to Sydney's bakeries made the site logical. The building that went up on that site was built to produce, not to be photographed a century later.",
            "The mill ran on steam initially, later converted to electricity. The milling equipment - roller mills, sifters, purifiers, the grain elevators that moved wheat from rail siding to storage bin to production floor - was installed progressively and updated as technology changed. What accumulated over a century of operation was a layered machine: newer equipment bolted alongside older, floor plans modified to accommodate process changes, every surface bearing the evidence of flour dust and mechanical work.",
            "Mungo Scott ceased milling operations in the early 2000s. The building was retained - its heritage significance recognised - while the site's future was debated. The mill machinery, because it was integral to the structure, largely stayed in place.",
            "Inside a flour mill that has stopped is a particular thing. The dust settles slowly. The wooden floors hold the record of a century of trolleys and sacks. The light coming through flour-hazed windows is diffused in a way that has nothing to do with decoration. These photographs were made inside the mill when the machinery was intact but the production had stopped.",
        ],
    },
    {
        "handle": "lewisham-hospital",
        "title": "Lewisham Hospital",
        "location": "Lewisham, New South Wales",
        "year": "1890s-2010s",
        "collection_handle": "lewisham-hospital",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/Copy_2_1a9ed868-d9c5-42c",
        "seo_title": "Lewisham Hospital Photography Prints | Lost Collective",
        "seo_description": "Fine art prints from Lewisham Hospital, Sydney NSW. Catholic hospital operating from the 1890s. Archival photography of the heritage building interiors and wards.",
        "body": [
            "The Sisters of the Little Company of Mary established Lewisham Hospital in the 1890s on a site in the inner west of Sydney. The hospital served the Catholic community of the district and grew through the early twentieth century as the suburbs around it developed. By mid-century it was a general hospital of significant size, with operating theatres, maternity wards, and all the infrastructure of a working acute-care facility.",
            "Catholic hospitals in Australia occupied a particular institutional niche - simultaneously religious institutions and public services, funded and managed by religious orders but serving the wider community. The physical fabric of Lewisham reflected this: the architecture of a functional medical facility overlaid with the spatial and decorative language of a religious institution.",
            "Lewisham's closure came as the broader reconfiguration of Sydney's hospital network proceeded. The site, close to the inner city and well-served by transport, became valuable for redevelopment. The historic buildings were retained under heritage provisions while the future of the site was determined.",
            "The photographs in this series were made inside the hospital during the period after clinical operations ceased. What the building showed was a century of institutional occupation - the modifications that accumulate in any working hospital, the relationship between a building designed in one era and the equipment and practices of another.",
        ],
    },
    {
        "handle": "waterfall-sanatorium",
        "title": "Waterfall Sanatorium",
        "location": "Waterfall, New South Wales",
        "year": "1909-1975",
        "collection_handle": "waterfall-sanatorium",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/reference-image_d0c6abcf",
        "seo_title": "Waterfall Sanatorium Photography Prints | Lost Collective",
        "seo_description": "Fine art prints from Waterfall Sanatorium, NSW. Tuberculosis treatment facility 1909-1975. Archival photography of the heritage asylum buildings in the Royal National Park.",
        "body": [
            "The NSW Government built the Waterfall Sanatorium in 1909 to address a public health crisis. Tuberculosis was the leading cause of death in the colony and the state, and the medical consensus of the period held that fresh air, sunshine, and rest in an appropriate environment could arrest the disease. The Waterfall site, in the bush south of Sydney at the edge of what would become the Royal National Park, was chosen for its isolation and its climate.",
            "The pavilion-plan hospital - separate buildings for men and women, open verandahs, cross-ventilation designed into every ward - was state of the art in 1909. Patients came here from Sydney and regional NSW and stayed for months or years. The isolation was part of the treatment and part of the management: a contagious disease in a contained location.",
            "Effective drug treatment for tuberculosis became available in the early 1950s. The long-stay patient population declined. By 1975, when the sanatorium closed, it had been operating for sixty-six years and tuberculosis had been largely controlled as a public health threat. The buildings - weatherboard pavilions in the bush, a built expression of a particular moment in medical history - were left standing.",
            "The verandah spaces are what make Waterfall different from any other building I have photographed. Designed to expose patients to the maximum amount of bush air and light, they face into the bush in a way that blurs the boundary between inside and outside in a way no modern building does. These photographs were made on site in 2016.",
        ],
    },
    {
        "handle": "bradmill-denim",
        "title": "Bradmill Denim",
        "location": "Yarraville, Victoria",
        "year": "1969-1996",
        "collection_handle": "bradmill-denim",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/bradmill-denim_2012_Marc",
        "seo_title": "Bradmill Denim Factory Photography Prints | Lost Collective",
        "seo_description": "Fine art prints from Bradmill Denim, Yarraville VIC. Australian manufacturer of Levi's denim 1969-1996. Archival photography of the industrial textile mill.",
        "body": [
            "For twenty-seven years, the Levi's jeans sold in Australia were made at Yarraville. Bradmill Industries' Yarraville mill had the licence from 1969 and ran it until 1996, when import competition from Asian manufacturers made domestic denim production uneconomical. The plant that had woven and finished denim for the country's most recognisable clothing brand was closed and left.",
            "Textile manufacturing at this scale is a specific industrial environment. The looms - wide, loud machines that ran in long rows - occupied most of the production floor. The dye works were separate, with their own infrastructure for the indigo and chemicals that gave denim its colour. The finishing and quality control areas were quieter. The whole operation was organised around the movement of fabric through a defined sequence of processes.",
            "Yarraville in the 1990s was already a declining industrial suburb. The closure of Bradmill was one of several in the area as Melbourne's manufacturing base contracted. The mill building - large, brick, built for industrial purposes - sat as industrial buildings often do: too substantial to knock down casually, not immediately convertible to other uses.",
            "These photographs were made inside the mill in 2012. The looms had been removed but the production floor retained the infrastructure of the process - the overhead systems, the loading docks, the specific spatial logic of a building designed around machinery that was no longer there.",
        ],
    },
    {
        "handle": "tin-city",
        "title": "Tin City",
        "location": "Lake Macquarie, New South Wales",
        "year": "1930s-present",
        "collection_handle": "tin-city",
        "image_url": "https://cdn.shopify.com/s/files/1/1304/3623/collections/tin-city_2018_January-24",
        "seo_title": "Tin City Photography Prints | Lost Collective",
        "seo_description": "Fine art prints from Tin City, Lake Macquarie NSW. The self-built fibro and corrugated iron community on the lake foreshore. Archival photography of this unique Australian settlement.",
        "body": [
            "Tin City is not a ruin. It is a settlement - a collection of self-built fibro and corrugated iron structures on the western foreshore of Lake Macquarie that has been occupied continuously since the 1930s. The people who built it and live in it built it for themselves, without council approval, without the involvement of architects or developers, to their own specifications and on their own timeline.",
            "The settlement grew during the Depression, when people with few resources and no access to conventional housing built what they could with what they could afford. The lake foreshore was Crown land, technically unavailable for permanent occupation, which was also what made it available to people with nothing. They built, they stayed, they improved what they had built.",
            "Generations have come and gone. The original structures have been extended, modified, rebuilt in parts, let fall where maintenance was not possible. The settlement has no consistent architectural language except the language of self-reliance and incremental improvement. What it has is the accumulated evidence of decades of occupancy by people who chose the lake over the suburb.",
            "I photographed Tin City in January 2018. What drew me there was not decay - most of it is very much alive - but the particular quality of a built environment that has no institutional logic behind it. Every structure is a decision made by a specific person at a specific moment. The collection records that.",
        ],
    },
]

# ── Shopify page mutations ────────────────────────────────────────────────────

PAGE_CREATE = """
mutation pageCreate($page: PageCreateInput!) {
  pageCreate(page: $page) {
    page { id handle title }
    userErrors { field message }
  }
}
"""

METAFIELDS_UPDATE = """
mutation metafieldsSet($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields { key }
    userErrors { field message }
  }
}
"""


def get_existing_handles() -> set:
    q = "query { pages(first: 100) { edges { node { handle } } } }"
    r = gql(q)
    return {e["node"]["handle"] for e in r["data"]["pages"]["edges"]}


def create_page(series: dict, dry_run: bool) -> bool:
    handle = series["handle"]
    body = build_page_html(
        image_url=series["image_url"],
        location=series["location"],
        year=series["year"],
        title=series["title"],
        body_paragraphs=series["body"],
        collection_handle=series["collection_handle"],
    )

    if dry_run:
        log(f"  [DRY] Would create /pages/{handle}")
        return True

    resp = gql(PAGE_CREATE, {"page": {
        "title": series["title"],
        "handle": handle,
        "body": body,
        "isPublished": True,
    }})
    result = resp["data"]["pageCreate"]
    if result["userErrors"]:
        log(f"  ✗ {result['userErrors']}")
        return False

    page_gid = result["page"]["id"]
    log(f"  ✓ /pages/{handle} created ({page_gid})")

    # Set SEO metafields
    mf_resp = gql(METAFIELDS_UPDATE, {"metafields": [
        {"ownerId": page_gid, "namespace": "global", "key": "title_tag",
         "type": "single_line_text_field", "value": series["seo_title"]},
        {"ownerId": page_gid, "namespace": "global", "key": "description_tag",
         "type": "single_line_text_field", "value": series["seo_description"]},
    ]})
    mf_errs = mf_resp["data"]["metafieldsSet"]["userErrors"]
    if mf_errs:
        log(f"  ! SEO metafield errors: {mf_errs}")
    else:
        log(f"  ✓ SEO title + description set")

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    log("=" * 60)
    log("Create Location Pages - Lost Collective")
    log(f"Mode: {'dry-run' if args.dry_run else 'live'}")
    log(f"Series: {len(SERIES)}")
    log("=" * 60)

    existing = get_existing_handles()
    log(f"Existing pages: {len(existing)}")

    created = skipped = errors = 0

    for series in SERIES:
        handle = series["handle"]
        log(f"\n[{SERIES.index(series)+1}/{len(SERIES)}] {series['title']}")

        if handle in existing:
            log(f"  - already exists, skipping")
            skipped += 1
            continue

        ok = create_page(series, args.dry_run)
        if ok:
            created += 1
        else:
            errors += 1

        time.sleep(0.5)

    log("\n" + "=" * 60)
    log(f"Created: {created}  |  Skipped: {skipped}  |  Errors: {errors}")
    log("=" * 60)


if __name__ == "__main__":
    main()
