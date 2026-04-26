# Historical fact repository

## What this directory is

Single source of truth for verified historical facts about every location
Lost Collective photographs. One file per location. Every claim carries a
source reference and an authority tier. No claim ships in public copy
unless it is in the relevant file with a source.

This is both a research database (for generating copy) and a quality gate
(so nothing unverified leaks into the store, blog, social, or ads).

## Why this exists

- Lost Collective's credibility with the audience rests on specific,
  accurate historical detail. "Built in 1917" is fine. "Built in 1917,
  came online in May 1917 after WWI delayed the opening" is what makes
  the audience lean in.
- Claude does not remember corrections across sessions. If a fact is not
  written down in a file Claude reads, it gets forgotten. This
  repository is the memory.
- The real gold is not on the first page of Google. It is in
  Conservation Management Plans, Trove, NSW State Archives, heritage
  society publications, Dictionary of Sydney, Engineering Heritage
  Australia, council Section 170 registers, National Archives of
  Australia. Over time we chip away at those layers.

## How to use this directory

**Before writing any copy** about a location (collection description,
product description, blog post, social caption, email, ad copy, alt
text), read that location's file first. Use only facts present in the
file. If a fact you want is not there, add it (with source and tier)
before shipping. If you cannot verify it, park it in the "Claims to
verify" section and do not ship.

**When a fact is corrected** by Brett or anyone else, update the
location file with the new claim and source, and add a maintenance log
entry. That is the mechanism for the correction to persist.

## File naming convention

One file per location, filename matches the Shopify collection handle:

```
docs/locations/white-bay-power-station.md
docs/locations/callan-park.md
docs/locations/terminus-hotel.md
docs/locations/kinugawa-kan.md
```

Underscore-separated collections become hyphen-separated filenames.

## Research rounds

Each file moves through layers of depth. Do not try to skip rounds.

**Round 1: surface.**
Wikipedia, Engineering Heritage Australia, mainstream news coverage, the
location's own website if it has one. 15 minutes. Covers core dates,
rough outline, obvious facts.

**Round 2: institutional history.**
Dictionary of Sydney, NSW State Heritage Register listing (full
statement of significance), local council heritage studies, historical
society websites with public content, Engineering Heritage Australia
nomination dossiers. 30 to 45 minutes. Adds texture, rationale, named
people, construction drama.

**Round 3: primary documents.**
Conservation Management Plans (PDFs, often 200 to 500 pages),
digitised Trove newspaper articles (targeted permalinks), consultant
reports (Godden Mackay Logan, GML Heritage, Tropman & Tropman, etc.),
NSW State Archives finding aids, Australian Dictionary of Biography
entries for named people, parliamentary Hansard, academic papers.
1 to 2 hours. Produces specific named people, verbatim quotes, lost or
forgotten detail.

**Round 4: request-only.**
National Archives of Australia RecordSearch items not yet digitised,
State Library NSW reading room holdings, private heritage society
archives, council records not online. Claude cannot fetch these. They
are captured in the file as reference numbers so Brett can order copies
from the relevant institution.

## Source tiering

Every claim needs a source reference, and every source sits in a tier.
The tier tells you how much weight to place on the claim.

**Tier 1: Primary and institutional.**
- Conservation Management Plans (on NSW Planning Portal and similar).
- NSW State Heritage Register listings (hms.heritage.nsw.gov.au).
- National Archives of Australia RecordSearch (digitised items).
- NSW State Archives & Records (records.nsw.gov.au).
- Parliamentary Hansard.
- Contemporary newspaper reports via Trove (to 1954 for SMH and most
  Australian papers).
- Government gazettes and official reports.
- Consultant heritage reports commissioned by authorities (Godden Mackay
  Logan, GML Heritage, Tropman & Tropman, Design 5 Architects, etc.).

**Tier 2: Recognised histories and professional records.**
- Dictionary of Sydney (State Library NSW, academic editors).
- Engineering Heritage Australia entries.
- Australian Dictionary of Biography.
- Museum archives (Powerhouse, Australian War Memorial, etc.).
- Local historical society publications (where authored and cited).
- University research outputs.

**Tier 3: Encyclopaedic, useful when corroborated.**
- Wikipedia. Use only if at least one Tier 1 or 2 source corroborates
  the claim. Wikipedia is an index into its citations, not a source on
  its own.
- Kiddle, Wikiwand, and similar Wikipedia mirrors: do not cite
  separately, use the original Wikipedia entry.

**Tier 4: Context only.**
- Commercial location agency pages (CATO Location Services).
- Photography blogs, abandoned-spaces enthusiast sites.
- Instagram captions.
- Corporate site PR pages that do not cite primary sources.

Use Tier 4 only to flag a line of inquiry. Never cite Tier 4 as
authority.

## File structure

See `_template.md` for the blank structure. See
`white-bay-power-station.md` for the first completed example.

Each file contains:

1. **Purpose and rule block** at the top.
2. **At-a-glance table** with core facts, each source-tagged.
3. **Chronology** of dated claims.
4. **Architecture and site** notes, with wording-to-use callouts.
5. **Machinery / interior / features** specific to the location type.
6. **Heritage status.**
7. **Role in wider context** (network, industry, community).
8. **Narrative themes and angles** for copy.
9. **Things worth noting in photographs.**
10. **Claims to verify.**
11. **Sources** grouped by tier.
12. **Maintenance log.**

## Coverage status

All 62 Lost Collective locations. See the current Shopify collections
list for the canonical inventory. Status legend:

- **R1** = Round 1 complete (surface)
- **R2** = Round 2 complete (institutional)
- **R3** = Round 3 complete (primary documents)
- **R4** = Round 4 noted (offline references captured)
- **-** = not started

### Commercial

| Location | Status | Last updated | Notes |
|---|---|---|---|
| Hotel Motel 101 | **R2** | 2026-04-26 | Press chronology reordered (Suitcase 1 May → Vice 20 May → Broadsheet 28 May → BROAD 26 July 2018). Real count 102 photographed / ~120 visited (title is conceit). Three highway runs out of Sydney. 26 named motels with locations harvested. **Brett Whiteley / Thirroul Beach Motel room 4 confirmed.** ResortBrokers industry context (Bellair 1955 as first AU motor inn, McCarron, 1975-85 peak). NAA 2022 exhibition + Oakleigh Motel VHR listing as Tier 1 typology anchors. Smith Journal + Daily Mail features unverified. |
| Kinugawa Kan | **R2** | 2026-04-21 | Japanese-language sources integrated (ja.Wikipedia きぬ川館本店, 鬼怒川温泉; zeiri4.com; tochipro.net). Correct Japanese name きぬ川館本店 (Kinukawa-kan Honten). Owner Hoshi Takashi, Yugen-gaisha Kinukawa-kan Honten. 9 storeys, 70 rooms, Kappa-buro bath. First post-bubble failure at Kinugawa Onsen (June 1999, 30億円). Nikko City/Utsunomiya Uni anti-trespass sealing March 2022. R3 leads: MLIT 2005 report, Teikoku Databank, Japanese press archives. |
| Terminus Hotel | **R2** | 2026-04-21 | Pyrmont History Group and Dictionary of Sydney integrated. Four pubs on one corner since 1841 (Pyrmont Hotel, Land's End, Coopers Arms from 1845, Terminus from c.1900). 1917 Tooth & Co. rebuild (not remodel). Wakils held 1983 to 2016. Tram terminus corroborated. R3: Fitzgerald 2018 book, Tooth & Co. archive at ANU, SHR listing record. |
| Bankstown RSL | **R2** | 2026-04-26 | NSW JRPP DA-1207/2015 + War Memorials Register integrated. Heritage listing confirmed NOT applied (Bankstown LEP 2015). Sub-Branch founded 17 Sept 1928 by 26 returned WWI servicemen. New club: Altis Architecture, Rolfe Latimer. WWI Honor Roll + 1997 Denis Phillips memorial both registered. 1955 architect, exact opening date, and 1928 founding venue flagged R3/offline. |

### Industrial

| Location | Status | Last updated | Notes |
|---|---|---|---|
| White Bay Power Station | **R2** | 2026-04-21 | First file. Dictionary of Sydney integrated. CMP, Trove permalinks, architect pending. |
| Eveleigh Paint Shop | **R2** | 2026-04-21 | NSW SHR 01141 (gazetted 2 April 1999, Gazette 27 p. 1546) and machinery item 5001063 integrated. Paint Shop internal code N4 "Exceptional Significance"; 1912 extension N16 "Moderate". Architect attribution refined: John Whitton (Engineer-in-Chief NSWR 1856-1899) conceived, Cowdery (Engineer-in-Chief for Existing Lines 1880-1890, NOT Chief Engineer) executed. Cowdery biography from 1913 SMH obituary added (Britannia Bridge 1847, Picton/Mittagong first NSW tunnels). Closure corrected: Suburban Car Workshops (1912 Paint Shop extension) closed 1989, full precinct 1990. Pre-redev custody RailCorp / Office of Rail Heritage. Smithsonian world-heritage claim unverified beyond Wikipedia. R3: Otto Cserhalmi 2002 Draft CMP (priority), Godden 1986, NSW Public Works 1995, Weir Phillips 2008/2014, USyd Library site recording collection. |
| Wangi Power Station | **R2** | 2026-04-21 | NSW SHR 01014 and Hunter Living Histories mined. Architect Colin Smith of C.H. Smith & Johnson (NOT Cobden Parkes). Two stations under one roof: A (1957-58, stoker, 150 MW) and B (1958-60, pulverised coal, 180 MW, Australian first). W.H. Myers 1941 proposal; Railways-to-Elcom transfer 1 January 1953; Italian migrant labour; 1964 blackout recovery via stoker-fired boilers. Owner I.J. McDonald Pty Ltd from 1998 (winding up May 2018). R3: Fetscher 2018, three CMPs, UoN 8,000+ drawings. |
| ANSTO HIFAR | **R2** | 2026-04-26 | EHA National Engineering Landmark confirmed (awarded 7 Dec 2001). NOT on NSW SHR or Commonwealth Heritage List (explicit Oct 2005 ministerial non-listing). Primary docs read: W.H. Roberts 1958 AAEC paper + 2006 EHA nomination dossier. Times sharpened: critical 11:15pm 26 Jan 1958, shut 10:25am 30 Jan 2007 (49 yrs 4 days). Foundation team named (Stevens, Baxter, Watson-Munro, Dalton, Roberts, Page, Raggatt). Stephenson & Turner architects + Hutcherson Bros builders. Six DIDO-class confirmed; HIFAR 2nd built, last to close. £A937,500 contract 1955. 70 ha Lucas Heights site (Long Bay rejected). Decommissioning timeline 2007→2008→2024→2026→~2030 mapped. R1's "21m" reactor height flagged: Roberts gives 11.1m for reactor block; 21m likely containment dome. |
| Ashio Copper Mine | **R1** | 2026-04-21 | Baseline pass. Japan's first major industrial pollution disaster. Shozo Tanaka 1891 Diet speech. |
| Morwell Power Station | - | | |
| Kandos Cement Works | **R2** | 2026-04-26 | Harbour Bridge cement supply confirmed Tier 1 via Ennis 1932 *Bond of Empire* p.48. **Opera House claim NOT verifiable; pull from copy.** Heritage status confirmed: not listed (no SHR, no EHA marker, council demolition DA Dec 2013). Ownership chain mapped 1913→2011→2025. 2011 closure: 11 July announcement, 98 redundancies. Town origin: original "Candos" (director-surname acronym), Krupp Bremen plant interned in Portuguese West Africa at WWI, replacement plant from USA/UK. Foundation team named (Angus, Oakden, Richards, Langevad, Jeffreys, Dawson). Kilns 5 and 6 confirmed; 1-4 flagged R3. Cementa Festival + 2025 Cenagen methanol proposal added. |
| Shimizusawa Thermal Power Plant | **R1** | 2026-04-21 | Baseline pass. Methane-burning auxiliary plant. 1981 Hokutan Yubari explosion context. |

### Medical

| Location | Status | Last updated | Notes |
|---|---|---|---|
| Callan Park | **R1** | 2026-04-21 | Baseline pass. Kirkbride Plan, therapeutic not custodial. Third-pass rewrite earlier. |
| Waterfall Sanatorium | **R1** | 2026-04-21 | Baseline pass. 788 patients by 1919, 2000 graves. |
| Kuwashima Hospital | **R1 (skeleton)** | 2026-04-21 | Genuinely obscure in English sources. R2 needs Japanese-language research. |
| The Asylum | - | | |

### Landscapes

| Location | Status | Last updated | Notes |
|---|---|---|---|
| Streetscapes of Yubari | - | | |
| Tin City | **R2** | 2026-04-26 | **Location confirmed Tier 1: Stockton Bight, Port Stephens — NOT Lake Macquarie.** Store copy correction required. 8 Tier 1 sources added (NPWS, WCL Board, WCL Plan of Management 2015, OEH, Worimi LALC). Land tenure mapped end-to-end (1990s claims → 2007 grant + lease-back → 2015 Plan of Management licence system). Shack count: 11 today, peak 36-38 in 1930s Depression. Shipwreck origin: cumulative wreck cluster (Cawarra 1866 onwards), not single ship. Worimi co-management Board of 13 named. 12,000-year midden claim retracted; replaced with cited "over 1,200 years" / "many thousands of years." "Last legal squatter settlement" softened to attributed framing. "1920 100-year lease" flagged as folklore. Named shack-holders Garland and Stuart added (Newcastle Herald). |
| Parramatta Road | - | | |
| Scenes | - | | |

### Rural

| Location | Status | Last updated | Notes |
|---|---|---|---|
| The Woolshed | - | | |
| A Place To Call Home | - | | |
| Woolla | - | | |

### Japan (grouped — several overlap with Industrial/Medical/Landscapes)

| Location | Status | Last updated | Notes |
|---|---|---|---|
| Family School Fureai | - | | |

## Recommended priority

1. **Hero locations, Round 2 first.** White Bay (done), Callan Park,
   Kinugawa Kan, Terminus Hotel. These are the four live on Shopify and
   get the most traffic.
2. **Second-tier hero locations, Round 2.** Wangi, Hotel Motel 101,
   Eveleigh, ANSTO, Kuwashima.
3. **Everything else, Round 2.**
4. **Round 3 on hero locations** when demanded by a campaign, blog
   post, or press pitch.
5. **Round 3 on everything else** on demand.

## Conventions for Claude

- Do not ship any historical claim in public copy that is not in the
  relevant location file.
- Do not invent. If a fact cannot be found, say so.
- If a source is Tier 4, flag the claim as "tier 4 only" in the file
  rather than elevating it.
- Archive conflicting claims in "Claims to verify" rather than picking
  a side. State the conflict and the sources.
- Log every session's changes in the maintenance log at the bottom of
  each file.
- Australian English throughout the files.

## When adding a new location

1. Copy `_template.md` to `[collection-handle].md`.
2. Fill in the at-a-glance table from Round 1 searches.
3. Build chronology and sections from the same Round 1 pass.
4. Flag Round 2 and 3 as not yet done.
5. Update the coverage table in this README.

## When updating an existing location

1. Read the current file before editing.
2. Add new claims with source references, not by overwriting existing
   ones.
3. Resolve "Claims to verify" items when you confirm them against a
   Tier 1 or 2 source.
4. Add a maintenance log entry.
5. Update the coverage table in this README if the round has advanced.
