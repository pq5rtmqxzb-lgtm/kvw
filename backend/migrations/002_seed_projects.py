#!/usr/bin/env python3
"""
Migration 002: Seed projects + social profiles from existing JSON data.
Run once after migration 001.

Usage:
    pip install supabase python-dotenv
    SUPABASE_URL=... SUPABASE_SERVICE_KEY=... python3 002_seed_projects.py
"""

import os, json, sys
from datetime import datetime
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Load source data ──────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(__file__)
ROOT = os.path.join(SCRIPT_DIR, "..", "..")

with open(os.path.join(ROOT, "projects_data.json")) as f:
    projects_raw = json.load(f)

# PROJECT_URLS extracted from the HTML (copy-paste or re-parse)
PROJECT_URLS = {
    "JTFW-00003": {"website": "https://hydrotwin.com", "linkedin": "https://www.linkedin.com/company/hydrotwin"},
    "JTFW-00004": {"website": "https://www.battolysersystems.com", "linkedin": "https://www.linkedin.com/company/battolysersystems"},
    "JTFW-00006": {"website": "https://sds-separation.com", "linkedin": "https://www.linkedin.com/company/sds-separation"},
    "JTFW-00007": {"website": "https://vertoro.com", "linkedin": "https://www.linkedin.com/company/vertoro"},
    "JTFW-00009": {"website": "https://berylcircular.com"},
    "JTFW-00013": {"website": "https://www.gradyent.ai", "linkedin": "https://www.linkedin.com/company/gradyent"},
    "JTFW-00016": {"website": "https://www.plantone-rotterdam.nl", "linkedin": "https://www.linkedin.com/company/plant-one-rotterdam-bv", "twitter": "https://twitter.com/plantonerdam", "facebook": "https://www.facebook.com/Plant1Rotterdam/"},
    "JTFW-00018": {"website": "https://hdm.nl"},
    "JTFW-00020": {"website": "https://www.decomcockpit.com"},
    "JTFW-00021": {"website": "https://concr3de.com", "linkedin": "https://www.linkedin.com/company/concr3de", "facebook": "https://www.facebook.com/concr3de/"},
    "JTFW-00022": {"website": "https://www.rotterdam.nl", "linkedin": "https://www.linkedin.com/company/gemeente-rotterdam", "twitter": "https://twitter.com/rotterdam", "facebook": "https://www.facebook.com/gem.Rotterdam/", "instagram": "https://www.instagram.com/gemeenterotterdam/"},
    "JTFW-00023": {"website": "https://xyclegroup.com", "linkedin": "https://www.linkedin.com/company/xycle"},
    "JTFW-00024": {"website": "https://zepp.solutions/en/", "linkedin": "https://www.linkedin.com/company/zepp.solutions"},
    "JTFW-00025": {"website": "https://maxwellandspark.com", "linkedin": "https://www.linkedin.com/company/maxwell-and-spark", "instagram": "https://www.instagram.com/maxwellandspark/"},
    "JTFW-00027": {"website": "https://www.stroomopwaarts.nl", "linkedin": "https://www.linkedin.com/company/stroomopwaarts", "twitter": "https://twitter.com/stroom_opwaarts"},
    "JTFW-00028": {"website": "https://www.decomcockpit.com"},
    "JTFW-00029": {"website": "https://futureproofshipping.com", "linkedin": "https://www.linkedin.com/company/future-proof-shipping/"},
    "JTFW-00031": {"website": "https://www.portofrotterdam.com", "linkedin": "https://www.linkedin.com/company/port-of-rotterdam"},
    "JTFW-00034": {"website": "https://obbotec-spex.com"},
    "JTFW-00035": {"website": "https://site.no-waste-in-time.nl/project/xirqulate/"},
    "JTFW-00038": {"website": "https://portliner.nl", "twitter": "https://twitter.com/port_liner"},
    "JTFW-00042": {"website": "https://www.plantone-rotterdam.nl", "linkedin": "https://www.linkedin.com/company/plant-one-rotterdam-bv", "twitter": "https://twitter.com/plantonerdam", "facebook": "https://www.facebook.com/Plant1Rotterdam/"},
    "JTFW-00045": {"website": "https://www.netics.nl", "linkedin": "https://www.linkedin.com/company/netics-bv"},
    "JTFW-00047": {"website": "https://zemquest.com"},
    "JTFW-00051": {"website": "https://www.vapro.nl", "linkedin": "https://www.linkedin.com/company/vapro", "instagram": "https://www.instagram.com/vapro.nl/"},
    "JTFW-00056": {"website": "https://www.plantone-rotterdam.nl", "linkedin": "https://www.linkedin.com/company/plant-one-rotterdam-bv", "twitter": "https://twitter.com/plantonerdam", "facebook": "https://www.facebook.com/Plant1Rotterdam/"},
    "JTFW-00060": {"website": "https://www.vakwijs.nl", "linkedin": "https://www.linkedin.com/school/vakwijs-b-v-/", "twitter": "https://twitter.com/vakwijs", "facebook": "https://www.facebook.com/Vakwijs/"},
    "JTFW-00064": {"website": "https://www.inholland.nl", "facebook": "https://www.facebook.com/Inholland/", "instagram": "https://www.instagram.com/hogeschoolinholland/"},
    "JTFW-00076": {"website": "https://twd.nl", "linkedin": "https://www.linkedin.com/company/temporary-works-design"},
    "JTFW-00091": {"website": "https://www.battolysersystems.com", "linkedin": "https://www.linkedin.com/company/battolysersystems"},
    "JTFW-00092": {"website": "https://www.krs.solar", "linkedin": "https://www.linkedin.com/company/krsolar"},
    "JTFW-00094": {"website": "https://www.deltalinqs.nl", "linkedin": "https://www.linkedin.com/company/deltalinqs", "twitter": "https://twitter.com/deltalinqs", "instagram": "https://www.instagram.com/deltalinqs/"},
    "JTFW-00098": {"website": "https://www.deberoepentuin.nl", "linkedin": "https://www.linkedin.com/company/de-beroepentuin"},
    "JTFW-00108": {"website": "https://switch2offshore.com", "linkedin": "https://www.linkedin.com/company/switch2-offshore/"},
    "JTFW-00113": {"website": "https://duiker.com", "linkedin": "https://www.linkedin.com/company/duiker"},
}

def parse_date(s):
    if not s:
        return None
    for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"]:
        try:
            return datetime.strptime(str(s), fmt).date().isoformat()
        except Exception:
            pass
    return None

# ── Seed projects ─────────────────────────────────────────────────────────────
print(f"Seeding {len(projects_raw)} projects...")
project_rows = []
for p in projects_raw:
    project_rows.append({
        "nr":           p.get("nr"),
        "naam":         p.get("naam"),
        "penvoerder":   p.get("penvoerder"),
        "stad":         p.get("stad"),
        "begunstigden": p.get("begunstigden", []) if isinstance(p.get("begunstigden"), list) else [],
        "eu_bijdrage":  float(p["eu_bijdrage"]) if p.get("eu_bijdrage") else None,
        "kosten":       float(p["kosten"]) if p.get("kosten") else None,
        "startdatum":   parse_date(p.get("startdatum")),
        "einddatum":    parse_date(p.get("einddatum")),
        "prioriteit":   p.get("prioriteit"),
        "spoor":        p.get("spoor"),
        "beschrijving": p.get("beschrijving"),
    })

result = sb.table("projects").upsert(project_rows, on_conflict="nr").execute()
print(f"  ✅ Projects seeded: {len(result.data)}")

# ── Seed social profiles ──────────────────────────────────────────────────────
print(f"Seeding social profiles for {len(PROJECT_URLS)} projects...")
profile_rows = []
for nr, urls in PROJECT_URLS.items():
    for platform, url in urls.items():
        profile_rows.append({
            "project_nr": nr,
            "platform":   platform,
            "url":        url,
        })

result = sb.table("social_profiles").upsert(
    profile_rows, on_conflict="project_nr,platform"
).execute()
print(f"  ✅ Social profiles seeded: {len(result.data)}")

print("\nDone! Database is ready.")
