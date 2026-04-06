"""
YNAB CSV Import — ING Accounts
Parses ING transaction export and imports missing transactions into YNAB.
Deduplicates against existing YNAB transactions (date + amount match).

Usage:
  op run --env-file=.env.tpl -- python3 scripts/ynab_import.py <account> [--dry-run]

  account     bills | spending | saving
  --dry-run   Show what would be imported without pushing to YNAB

Examples:
  python3 scripts/ynab_import.py bills
  python3 scripts/ynab_import.py spending --dry-run
"""

import csv, os, re, sys
from datetime import datetime

import requests

# ── Config ─────────────────────────────────────────────────────────────────────

BASE    = "https://api.ynab.com/v1"
TOKEN   = os.environ["YNAB_TOKEN"]
BUDGET  = os.environ["YNAB_BUDGET_ID"]
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

ACCOUNT_CONFIG = {
    "bills": {
        "id":  "ac9c72fc-0c7b-47e0-9092-f67821b1f2bd",
        "csv": os.path.expanduser("~/Downloads/Transactions (1).csv"),
    },
    "spending": {
        "id":  "e59be376-73a0-4115-85d0-162b6c5f0044",
        "csv": os.path.expanduser("~/Downloads/Transactions (2).csv"),
    },
    "saving": {
        "id":  "6cbd6bc5-4752-4a53-b73b-8f1290cf32b7",
        "csv": os.path.expanduser("~/Downloads/Transactions (3).csv"),
    },
}

account_name = next((a for a in sys.argv[1:] if a in ACCOUNT_CONFIG), "bills")
ACCOUNT_ID   = ACCOUNT_CONFIG[account_name]["id"]
CSV_PATH     = ACCOUNT_CONFIG[account_name]["csv"]
DRY_RUN      = "--dry-run" in sys.argv

# ── Payee → Category mapping ───────────────────────────────────────────────────
# Format: "payee keyword": (category_id, category_name)
# Matched case-insensitively against cleaned description.
# None = leave uncategorised (YNAB will flag it for review)

CATEGORY_MAP = {
    # ── Transport / EV ────────────────────────────────────────────────────────
    "transport for nsw":        ("07da8f54-bc29-4717-8349-4219484e1dd8", "Kia EV5 Tolls"),
    # ── Rent & utilities ──────────────────────────────────────────────────────
    "bay realty":               ("270cba6f-3670-49a5-8ecf-c4363f50c6fd", "Rent"),
    "lj hooker":                ("270cba6f-3670-49a5-8ecf-c4363f50c6fd", "Rent"),
    "hbfhealth":                ("0434bf29-67ea-4d22-bf2a-6ab2ab170d27", "Health Insurance"),
    "everyday insurance":       ("0434bf29-67ea-4d22-bf2a-6ab2ab170d27", "Health Insurance"),
    "aussie broadband":         ("e5d8b212-d397-4078-8956-ef06d3ba6bb2", "Internet"),
    "globird":                  ("439eae55-69eb-4757-bfff-6cb238397fa6", "Gas/Electricity"),
    "wooliesmobile":            ("ba8fa88a-9fe5-40e4-98aa-eff10c79cfec", "Brett Mobile"),
    # ── Groceries ─────────────────────────────────────────────────────────────
    "coles":                    ("abce3384-b966-496f-ab6c-3424c36bb64e", "Groceries"),
    "woolworths":               ("abce3384-b966-496f-ab6c-3424c36bb64e", "Groceries"),
    "aldi":                     ("abce3384-b966-496f-ab6c-3424c36bb64e", "Groceries"),
    "harris farm":              ("abce3384-b966-496f-ab6c-3424c36bb64e", "Groceries"),
    "iga ":                     ("abce3384-b966-496f-ab6c-3424c36bb64e", "Groceries"),
    "metro master meats":       ("abce3384-b966-496f-ab6c-3424c36bb64e", "Groceries"),
    "metro earlwood":           ("abce3384-b966-496f-ab6c-3424c36bb64e", "Groceries"),
    "australian meat empori":   ("abce3384-b966-496f-ab6c-3424c36bb64e", "Groceries"),
    "earlwood growers":         ("abce3384-b966-496f-ab6c-3424c36bb64e", "Groceries"),
    "orange supermarket":       ("abce3384-b966-496f-ab6c-3424c36bb64e", "Groceries"),
    "ek nominees":              ("abce3384-b966-496f-ab6c-3424c36bb64e", "Groceries"),
    "c1mart":                   ("abce3384-b966-496f-ab6c-3424c36bb64e", "Groceries"),
    "saliba brothers":          ("abce3384-b966-496f-ab6c-3424c36bb64e", "Groceries"),
    "petras vegys":             ("abce3384-b966-496f-ab6c-3424c36bb64e", "Groceries"),
    "the grocery store":        ("abce3384-b966-496f-ab6c-3424c36bb64e", "Groceries"),
    "ww metro":                 ("abce3384-b966-496f-ab6c-3424c36bb64e", "Groceries"),
    # ── Takeout / Dining Out ──────────────────────────────────────────────────
    "frenchies":                ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "welcome dose":             ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "mentmore":                 ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "mcdonald":                 ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "kfc ":                     ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "ol mates":                 ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "cre8 cafe":                ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "healthe and delices":      ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "ansto nsw":                ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "bakers delight":           ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "el jannah":                ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "guzman y gomez":           ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "gelato messina":           ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "gelatomes":                ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "bettys burgers":           ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "sushi":                    ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "chicken george":           ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "frango marrick":           ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "clems chicken":            ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "chebbos":                  ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "roll'd":                   ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "black star pastry":        ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "hoiak":                    ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "marrickville spirit":      ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "smp*cafein":               ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "opera bar":                ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "and here cafe":            ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "algorithm cafe":           ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "newmarket hotel":          ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "general gordon hotel":     ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "coogee bay hotel":         ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "barrel and batch":         ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "bourke street bakery":     ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "five guys":                ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "sweet beiruit":            ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "earlwood lebanese":        ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "orient hotel":             ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "flappy's fried":           ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "yeeros shop":              ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "sweet chilli indian":      ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "yo-chi":                   ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "super noodles":            ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "get sashimi":              ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "manpuku":                  ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "orchid kitchen":           ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "deli republic":            ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "eat istanbul":             ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "andiamo dai":              ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "pappa flock":              ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "keens sandwich":           ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "hero sushi":               ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "u know thai":              ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "lumiere":                  ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "cactus vision":            ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "ho's bakery":              ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "liberty hall":             ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "substation east":          ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "ariomi":                   ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "jamie s cafe":             ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "xk espresso":              ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "oasis espresso":           ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "sugarbaby espresso":       ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "schoolbus coffee":         ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "hidden grounds":           ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "chargrill marrick":        ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "provender":                ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "sharetea":                 ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "sushi maru":               ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "pattison's burwood":       ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "cortado cafe":             ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "lune croissanterie":       ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "ze rosebery":              ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "zeus rosebery":            ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "dani & fio":               ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "gyradiko":                 ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "the lark earlwood":        ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "earl rosebery":            ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "el loco":                  ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "miranda express":          ("dafbd511-0d07-414e-8b3a-a268f30a83c2", "Takeout/Dining Out"),
    "hoyts":                    ("1e9f838d-ef06-433c-ac4c-a24ed9a95c67", "Movie Hire"),
    # ── Booze ─────────────────────────────────────────────────────────────────
    "bws liquor":               ("6a3a4bcb-eccb-42a8-a178-917d4c421610", "Booze"),
    "dan murphy":               ("6a3a4bcb-eccb-42a8-a178-917d4c421610", "Booze"),
    "davids cellars":           ("6a3a4bcb-eccb-42a8-a178-917d4c421610", "Booze"),
    "see saw wine":             ("6a3a4bcb-eccb-42a8-a178-917d4c421610", "Booze"),
    # ── Transport ─────────────────────────────────────────────────────────────
    "transport for ns":         ("e4a17129-b641-4cc1-995b-d44b309babb8", "Forester Tolls"),
    "linkt sydney":             ("e4a17129-b641-4cc1-995b-d44b309babb8", "Forester Tolls"),
    "linkt avis":               ("e4a17129-b641-4cc1-995b-d44b309babb8", "Forester Tolls"),
    "transportfornsw":          ("ea9d9841-5826-48c0-aff4-0cd130cc4e39", "Opal"),
    "tfnsw opal":               ("ea9d9841-5826-48c0-aff4-0cd130cc4e39", "Opal"),
    "opal machine":             ("ea9d9841-5826-48c0-aff4-0cd130cc4e39", "Opal"),
    "transport nsw":            ("ea9d9841-5826-48c0-aff4-0cd130cc4e39", "Opal"),
    "uber":                     ("7bc86cc2-332b-47b8-801c-9c5b33b1b4ec", "Uber"),
    "taxipay":                  ("a24b08eb-c173-4227-ad2a-dcc94720baf7", "Taxi"),
    "parknpay":                 ("d66749ab-2e2b-422f-bd58-e655121ed08c", "Parking"),
    "cityofsydney parking":     ("d66749ab-2e2b-422f-bd58-e655121ed08c", "Parking"),
    "wilson parking":           ("d66749ab-2e2b-422f-bd58-e655121ed08c", "Parking"),
    "sydney olympic park p":    ("d66749ab-2e2b-422f-bd58-e655121ed08c", "Parking"),
    "np-budget":                ("18c7c817-0356-4e33-96b9-946b9d52ea94", "Forester Servicing"),
    "ampol":                    ("f89cca2a-250b-4460-94a6-0ef87a042e50", "Fuel"),
    "bp ":                      ("f89cca2a-250b-4460-94a6-0ef87a042e50", "Fuel"),
    "payless fuel":             ("f89cca2a-250b-4460-94a6-0ef87a042e50", "Fuel"),
    "eg group":                 ("f89cca2a-250b-4460-94a6-0ef87a042e50", "Fuel"),
    "seven-eleven":             ("f89cca2a-250b-4460-94a6-0ef87a042e50", "Fuel"),
    "7-eleven":                 ("f89cca2a-250b-4460-94a6-0ef87a042e50", "Fuel"),
    "7 eleven":                 ("f89cca2a-250b-4460-94a6-0ef87a042e50", "Fuel"),
    "randwick city council":    ("d66749ab-2e2b-422f-bd58-e655121ed08c", "Parking"),
    # ── Personal care ─────────────────────────────────────────────────────────
    "fitness passport":         ("778f371c-1587-4f0b-80fa-6b1efbff5e28", "Gym"),
    "nomad bouldering":         ("778f371c-1587-4f0b-80fa-6b1efbff5e28", "Gym"),
    "gunyama park":             ("778f371c-1587-4f0b-80fa-6b1efbff5e28", "Gym"),
    "chemist warehouse":        ("c3dbb174-a504-45d7-8392-37035c7cd3f8", "Prescriptions"),
    "pharmacy 4 less":          ("c3dbb174-a504-45d7-8392-37035c7cd3f8", "Prescriptions"),
    "terrywhite":               ("c3dbb174-a504-45d7-8392-37035c7cd3f8", "Prescriptions"),
    "mcare benefits":           ("407a064d-08fc-46f6-91af-8bb658e40e23", "Medicare Benifits"),
    "zone34 physio":            ("1aa78e9b-1a50-4125-b9a8-017d3ba7ab9c", "Physiotherapist"),
    "the foot hub":             ("1aa78e9b-1a50-4125-b9a8-017d3ba7ab9c", "Physiotherapist"),
    "sp angelo personal":       ("7aadc041-5879-4ac3-b8f5-a81aca682068", "Massage"),
    "noddys on king":           ("8302073b-b351-4618-9002-dcde90724957", "Hairdresser"),
    "luxe beauty bar":          ("8302073b-b351-4618-9002-dcde90724957", "Hairdresser"),
    "oz hair beauty":           ("8302073b-b351-4618-9002-dcde90724957", "Hairdresser"),
    "aesop":                    ("e11552d1-09e2-4820-a743-7c82ba018977", "Cosmetics"),
    "margi by azure":           ("e11552d1-09e2-4820-a743-7c82ba018977", "Cosmetics"),
    "lovisa":                   ("686ba26c-b40a-46bd-98d2-1d18094de42d", "Clothes"),
    "cotton on":                ("686ba26c-b40a-46bd-98d2-1d18094de42d", "Clothes"),
    "the iconic":               ("686ba26c-b40a-46bd-98d2-1d18094de42d", "Clothes"),
    "david jones":              ("686ba26c-b40a-46bd-98d2-1d18094de42d", "Clothes"),
    "pandora":                  ("686ba26c-b40a-46bd-98d2-1d18094de42d", "Clothes"),
    "opsm":                     ("eda85aad-9d9d-456d-baf9-137edf50edfb", "Prescription Glasses"),
    "rebel ":                   ("20bd57f4-da87-44ad-8add-98c433c50877", "Fitness Equipment"),
    "decathlon":                ("20bd57f4-da87-44ad-8add-98c433c50877", "Fitness Equipment"),
    "tune cycles":              ("20bd57f4-da87-44ad-8add-98c433c50877", "Fitness Equipment"),
    # ── Household ─────────────────────────────────────────────────────────────
    "bunnings":                 ("472d5a29-bf67-419c-b9bb-d3d9c79d3d9a", "Homewares"),
    "kmart":                    ("472d5a29-bf67-419c-b9bb-d3d9c79d3d9a", "Homewares"),
    "ikea":                     ("807751de-28cc-40e2-8ac8-cb5977c314db", "Furniture"),
    "bed bath n table":         ("472d5a29-bf67-419c-b9bb-d3d9c79d3d9a", "Homewares"),
    "spotlight":                ("472d5a29-bf67-419c-b9bb-d3d9c79d3d9a", "Homewares"),
    "garden life":              ("a4526170-2d91-4d1c-83b0-e4f710abf51d", "Lawn Mowing"),
    "cleaners warehouse":       ("472d5a29-bf67-419c-b9bb-d3d9c79d3d9a", "Homewares"),
    # ── Digital subscriptions ─────────────────────────────────────────────────
    "amazon web services":      ("118932cb-7ecb-46f5-bac5-a27aa3ea7251", "AWS"),
    "anthropic":                ("d04db585-bfbf-487a-9f69-d81348c47486", "ChatGPT+"),
    "claude.ai":                ("d04db585-bfbf-487a-9f69-d81348c47486", "ChatGPT+"),
    "paypal *apple.com":        ("0758889f-ae1e-4fc4-9830-e2cc31479d04", "AppleCare+"),
    "paypal *netflix":          ("2683559f-7cd6-41a0-a8a5-9ce0b294a76b", "Netflix"),
    "paypal *playstation":      ("4bfcf97c-3608-4b71-9ec7-224efdd3c2cb", "Games"),
    "paypal *patreonaust":      ("be2dcf77-5617-41df-a926-cbef0915aa0d", "Letting Loose"),
    "paypal *googleaustr":      ("118932cb-7ecb-46f5-bac5-a27aa3ea7251", "AWS"),
    "prime vide":               ("dadb71ef-2e1f-4f12-a7a9-a2edd36e0b4d", "Amazon Prime"),
    "udemy":                    ("57fe2b72-09ed-4037-b83b-d54e4596297c", "Learning"),
    # ── Entertainment ─────────────────────────────────────────────────────────
    "qudos bank arena":         ("2d7b1f7d-23c4-4e1d-830c-7ef38f6f87c7", "Game Spectator Fees"),
    "opera lirica":             ("8a972dc8-2be7-468f-9aa5-cc21d20a9ba0", "Holidays"),
    # ── Basketball ────────────────────────────────────────────────────────────
    "basketball connect":       ("2d7b1f7d-23c4-4e1d-830c-7ef38f6f87c7", "Game Spectator Fees"),
    "basketballconnec":         ("2d7b1f7d-23c4-4e1d-830c-7ef38f6f87c7", "Game Spectator Fees"),
    "bulls basketball":         ("b7070e2c-ab7c-4402-8402-368c69a46aeb", "Off Season and Workshops"),
    "penrith valley":           ("66b10918-b24d-4d67-89ef-8ead43c67879", "Heidi Local Comp"),
    "shoalhaven indoor":        ("83075772-119c-4773-98f4-db5b43693867", "Jasper Local Comp"),
    "pcyc nsw":                 ("2d7b1f7d-23c4-4e1d-830c-7ef38f6f87c7", "Game Spectator Fees"),
    # ── School / kids ─────────────────────────────────────────────────────────
    "flexischools":             ("fd38034a-52b8-4280-b4d8-80c60f533388", "Vacation Care"),
    "schoolsonline":            ("1e738a16-833e-49d1-a093-c75cd9339965", "School Fees"),
    "school photographer":      ("bc9b62e8-489f-4911-acb4-99c871a807c4", "School Photos"),
    "ls toys and tales":        ("00f217d9-1a84-49f9-b0ec-f70ccc5c6be3", "Goodies for Kids"),
    "zing pop culture":         ("00f217d9-1a84-49f9-b0ec-f70ccc5c6be3", "Goodies for Kids"),
    "ice zoo sydney":           ("00f217d9-1a84-49f9-b0ec-f70ccc5c6be3", "Goodies for Kids"),
    "camp australia":           ("fd38034a-52b8-4280-b4d8-80c60f533388", "Vacation Care"),
    "bounce holdings":          ("9c812dfb-689c-4048-8953-afef2363336e", "School Special Events"),
    # ── Medical ───────────────────────────────────────────────────────────────
    "hfm broadway":             ("30f747e3-823f-4222-8459-196cf7a8aea9", "Doctor"),
    "hfm boronia":              ("30f747e3-823f-4222-8459-196cf7a8aea9", "Doctor"),
    "your doctors":             ("30f747e3-823f-4222-8459-196cf7a8aea9", "Doctor"),
    # ── Lost Collective ───────────────────────────────────────────────────────
    "amazon marketplace":       ("e4551d6e-87ef-4b22-8368-88911997d5a7", "Equipment"),
    "amazon reta":              ("e4551d6e-87ef-4b22-8368-88911997d5a7", "Equipment"),
    "amazon mktpl":             ("e4551d6e-87ef-4b22-8368-88911997d5a7", "Equipment"),
    "officeworks":              ("170d8ae8-11e0-40bf-8556-da2dbfef6610", "Office Supplies"),
    "my post business":         ("40a6a0bd-67d5-4cca-a2ab-0efd1752e0b6", "Postage"),
    "3d bro":                   ("53350aa3-6717-4c77-8088-ffd364d613dc", "3D Printing"),
    "bambulab":                 ("53350aa3-6717-4c77-8088-ffd364d613dc", "3D Printing"),
    "sp robot specialist":      ("e4551d6e-87ef-4b22-8368-88911997d5a7", "Equipment"),
    "walkens film":             ("7a03afca-a35b-4149-b3fb-3292dc806a8e", "Film Development"),
    # ── Misc / Special occasions ──────────────────────────────────────────────
    "make-a-wish":              ("0efcfa7e-b4ba-45ae-bea6-6d9fbcae5c41", "Donation"),
    "raffletix":                ("a0d8b608-8d63-4df9-b11c-742489680a4f", "Misc"),
    "rafflelink":               ("a0d8b608-8d63-4df9-b11c-742489680a4f", "Misc"),
    "atm rebate":               ("467a0538-5ecf-4247-b0cf-514944a13755", "ATM Rebate"),
    "utility bill cashback":    ("467a0538-5ecf-4247-b0cf-514944a13755", "ATM Rebate"),
    "spaceship":                ("cc11fd21-8182-48b1-8948-c36554e51e49", "Investment"),
    "sydney party":             ("195791cc-ff39-4922-b099-30d29f3d0546", "Gift Giving"),
    "stanley gifts":            ("195791cc-ff39-4922-b099-30d29f3d0546", "Gift Giving"),
    "airbnb":                   ("8a972dc8-2be7-468f-9aa5-cc21d20a9ba0", "Holidays"),
    # ── Japan Trip ────────────────────────────────────────────────────────────
    "takayama":                 ("98f6162f-3516-4f1c-afde-67fca2df17e7", "Japan Trip / Food"),
    "tokyo disney":             ("8a972dc8-2be7-468f-9aa5-cc21d20a9ba0", "Japan Trip / Holidays"),
    "megadonquijote":           ("98f6162f-3516-4f1c-afde-67fca2df17e7", "Japan Trip / Food"),
    "familymart":               ("98f6162f-3516-4f1c-afde-67fca2df17e7", "Japan Trip / Food"),
    "lawson":                   ("98f6162f-3516-4f1c-afde-67fca2df17e7", "Japan Trip / Food"),
    "yodobashi":                ("e4551d6e-87ef-4b22-8368-88911997d5a7", "Japan Trip / Equipment"),
    "bic camera":               ("e4551d6e-87ef-4b22-8368-88911997d5a7", "Japan Trip / Equipment"),
    "klook":                    ("8a972dc8-2be7-468f-9aa5-cc21d20a9ba0", "Japan Trip / Holidays"),
    "headout":                  ("8a972dc8-2be7-468f-9aa5-cc21d20a9ba0", "Japan Trip / Holidays"),
    "mobile suica":             ("c429f9b4-1e55-4c7e-b047-38700d83f2ce", "Japan Trip / Tolls"),
    "japanpost bank":           ("0dc3bb8d-46e6-4018-ad85-852a45edb053", "Japan Trip / Flights"),
    "hakata-ku":                ("0dc3bb8d-46e6-4018-ad85-852a45edb053", "Japan Trip / Flights"),
    "familymart nagasaki":      ("0dc3bb8d-46e6-4018-ad85-852a45edb053", "Japan Trip / Flights"),
    "familymart uenonaka":      ("0dc3bb8d-46e6-4018-ad85-852a45edb053", "Japan Trip / Flights"),
    "haneda airport":           ("0dc3bb8d-46e6-4018-ad85-852a45edb053", "Japan Trip / Flights"),
    "rakutenpay":               ("98f6162f-3516-4f1c-afde-67fca2df17e7", "Japan Trip / Food"),
    "tullys coffee":            ("98f6162f-3516-4f1c-afde-67fca2df17e7", "Japan Trip / Food"),
    "segafredo":                ("98f6162f-3516-4f1c-afde-67fca2df17e7", "Japan Trip / Food"),
    "ueno zoo":                 ("8a972dc8-2be7-468f-9aa5-cc21d20a9ba0", "Japan Trip / Holidays"),
    "shibuya loft":             ("472d5a29-bf67-419c-b9bb-d3d9c79d3d9a", "Japan Trip / Shopping"),
    "ichikakuya":               ("98f6162f-3516-4f1c-afde-67fca2df17e7", "Japan Trip / Food"),
    "shimokitazawa":            ("98f6162f-3516-4f1c-afde-67fca2df17e7", "Japan Trip / Food"),
    "ichiryu":                  ("98f6162f-3516-4f1c-afde-67fca2df17e7", "Japan Trip / Food"),
    "sutameshi":                ("98f6162f-3516-4f1c-afde-67fca2df17e7", "Japan Trip / Food"),
    "andhere tokyo":            ("98f6162f-3516-4f1c-afde-67fca2df17e7", "Japan Trip / Food"),
    "chuukocamerabox":          ("e4551d6e-87ef-4b22-8368-88911997d5a7", "Japan Trip / Equipment"),
    "ezo fukuoka":              ("98f6162f-3516-4f1c-afde-67fca2df17e7", "Japan Trip / Food"),
    "kumasandog":               ("98f6162f-3516-4f1c-afde-67fca2df17e7", "Japan Trip / Food"),
    "kitamura":                 ("e4551d6e-87ef-4b22-8368-88911997d5a7", "Japan Trip / Equipment"),
}

# Descriptions that indicate internal account transfers.
# We do NOT use YNAB transfer payee_ids here — importing all three ING accounts means
# both sides of every transfer are in the CSVs. Using payee_ids would cause YNAB to
# auto-create phantom partner transactions. Instead we import as regular payee names
# and let YNAB show accurate account balances without the phantom problem.
TRANSFER_KEYWORDS = [
    "internal transfer",
    "to orange everyday",
    "rent - internal transfer",
    "qantas credit cards",
    "bonus interest credit",
    "interest credit",
    "bonus interest",
]


# ── Helpers ─────────────────────────────────────────────────────────────────────

def clean_payee(desc: str) -> str:
    """Strip receipt numbers, dates, card numbers from ING descriptions."""
    desc = re.sub(r" - Receipt \w+.*", "", desc)
    desc = re.sub(r" - Visa Purchase.*", "", desc)
    desc = re.sub(r" - Direct Debit.*", "", desc)
    desc = re.sub(r" - BPAY.*", "", desc)
    desc = re.sub(r" - Osko Payment.*", "", desc)
    desc = re.sub(r"In \w+ Date.*", "", desc)
    desc = re.sub(r"\\ withdrawal.*", "", desc)
    desc = re.sub(r"^\d+ - ", "", desc)
    desc = re.sub(r"^\d+ \w+ - ", "", desc)
    return desc.strip()


def parse_date(d: str) -> str:
    """Convert DD/MM/YYYY to YYYY-MM-DD."""
    return datetime.strptime(d, "%d/%m/%Y").strftime("%Y-%m-%d")


def parse_amount(row: dict) -> int:
    """Return amount in YNAB milliunits. Positive = inflow, negative = outflow."""
    if row["Credit"]:
        return round(float(row["Credit"]) * 1000)
    if row["Debit"]:
        return round(float(row["Debit"]) * 1000)  # already negative in ING export
    return 0


def categorise(desc: str) -> tuple[str | None, str | None, str | None]:
    """
    Returns (transfer_payee_id | None, category_id | None, clean_payee_name).
    Transfer keywords return (None, None, payee_name) — imported as plain inflows/outflows.
    """
    lower = desc.lower()

    # Internal transfers — import as plain transactions (no YNAB transfer link)
    for keyword in TRANSFER_KEYWORDS:
        if keyword in lower:
            return None, None, clean_payee(desc)

    # Check expense categories
    payee = clean_payee(desc)
    for keyword, (cat_id, _) in CATEGORY_MAP.items():
        if keyword in lower:
            return None, cat_id, payee

    return None, None, payee  # uncategorised — YNAB will flag for review


# ── Fetch existing YNAB transactions ───────────────────────────────────────────

def fetch_existing() -> set[tuple[str, int]]:
    """Return set of (date, amount_milliunits) for deduplication."""
    r = requests.get(
        f"{BASE}/budgets/{BUDGET}/accounts/{ACCOUNT_ID}/transactions",
        headers=HEADERS,
        params={"since_date": "2025-07-01"},
    )
    r.raise_for_status()
    existing = set()
    for t in r.json()["data"]["transactions"]:
        if not t["deleted"]:
            existing.add((t["date"], t["amount"]))
    return existing


# ── Parse CSV ──────────────────────────────────────────────────────────────────

FY_START = datetime(2025, 7, 1)

def parse_csv() -> list[dict]:
    with open(CSV_PATH, newline="") as f:
        rows = list(csv.DictReader(f))
    # Filter to current financial year only
    return [r for r in rows if datetime.strptime(r["Date"], "%d/%m/%Y") >= FY_START]


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print(f"{'DRY RUN — ' if DRY_RUN else ''}Importing ING {account_name.title()} transactions to YNAB")
    print(f"CSV: {CSV_PATH}")
    print()

    print("Fetching existing YNAB transactions...")
    existing = fetch_existing()
    print(f"  {len(existing)} existing transactions found (will skip duplicates)")
    print()

    rows = parse_csv()
    print(f"Parsing {len(rows)} CSV rows...")

    to_import = []
    skipped   = 0
    uncategorised = []

    for row in rows:
        date   = parse_date(row["Date"])
        amount = parse_amount(row)

        if amount == 0:
            continue

        # Skip if already in YNAB
        if (date, amount) in existing:
            skipped += 1
            continue

        transfer_payee_id, category_id, payee_name = categorise(row["Description"])

        txn = {
            "account_id": ACCOUNT_ID,
            "date":        date,
            "amount":      amount,
            "payee_name":  payee_name,
            "cleared":     "cleared",
            "approved":    True,
            "memo":        row["Description"][:200],
        }
        if transfer_payee_id:
            txn["payee_id"] = transfer_payee_id
            del txn["payee_name"]
        if category_id:
            txn["category_id"] = category_id

        if not transfer_payee_id and not category_id:
            uncategorised.append(f"  {date}  {amount/1000:>10.2f}  {payee_name}")

        to_import.append(txn)

    print(f"  {skipped} duplicates skipped")
    print(f"  {len(to_import)} new transactions to import")
    if uncategorised:
        print(f"  {len(uncategorised)} will be uncategorised (needs manual review in YNAB):")
        for u in uncategorised:
            print(u)
    print()

    if not to_import:
        print("Nothing to import.")
        return

    if DRY_RUN:
        print("DRY RUN — showing first 20 transactions that would be imported:")
        for t in to_import[:20]:
            cat = t.get("category_id", t.get("payee_id", "UNCATEGORISED"))[:8]
            print(f"  {t['date']}  {t['amount']/1000:>10.2f}  {t.get('payee_name', '[transfer]')[:40]}")
        return

    # Push in batches of 50
    BATCH = 50
    total_imported = 0
    errors = []

    for i in range(0, len(to_import), BATCH):
        batch = to_import[i : i + BATCH]
        r = requests.post(
            f"{BASE}/budgets/{BUDGET}/transactions",
            headers={**HEADERS, "Content-Type": "application/json"},
            json={"transactions": batch},
        )
        if r.status_code in (200, 201):
            result = r.json()["data"]
            imported = len(result.get("transactions") or []) + len(result.get("transaction_ids") or [])
            total_imported += imported
            dupes = len(result.get("duplicate_import_ids") or [])
            print(f"  Batch {i//BATCH + 1}: {imported} imported, {dupes} duplicates caught by YNAB")
        else:
            errors.append(f"Batch {i//BATCH + 1} error {r.status_code}: {r.text[:200]}")
            print(f"  Batch {i//BATCH + 1}: ERROR {r.status_code}")

    print()
    print(f"Done. {total_imported} transactions imported.")
    if errors:
        print("Errors:")
        for e in errors:
            print(f"  {e}")
    print()
    print("Review uncategorised transactions in YNAB: Budget > All Accounts > filter by Uncategorised")


if __name__ == "__main__":
    main()
