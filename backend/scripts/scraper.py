#!/usr/bin/env python3
"""
JTF Rijnmond — Social Media Compliance Scraper
===============================================
Scrapes public social media posts for all JTF projects,
runs EU Regulation 2021/1060 compliance checks,
and stores results in Supabase.

Triggered by: GitHub Actions (weekly cron)
Runtime: ~5-15 minutes per full run

Environment variables required:
    SUPABASE_URL
    SUPABASE_SERVICE_KEY

Optional (enables richer scraping):
    TWITTER_BEARER_TOKEN    (Twitter API v2)

Usage:
    python3 scraper.py [--project JTFW-00003] [--dry-run]
"""

import os
import re
import json
import time
import logging
import argparse
import hashlib
from datetime import datetime, timezone
from typing import Optional
import requests
from supabase import create_client

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("jtf-scraper")

# ── Supabase client ───────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
sb = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── EU Compliance checks ──────────────────────────────────────────────────────
EU_EMBLEM_KEYWORDS = ["europese unie", "european union", "eu-embleem", "eu emblem", "#eu", "gefinancierd door de eu"]
COFUNDING_KEYWORDS = ["medegefinancierd", "mede gefinancierd", "co-funded", "co-financing", "eu-bijdrage", "european regional development"]
JTF_KEYWORDS       = ["jtf", "just transition fund", "rechtvaardige transitie", "just transition", "kansenvoorwest", "kansen voor west"]
HASHTAG_KEYWORDS   = ["#euinmyregion", "#euinmijnregio"]
MAX_CONTENT_LENGTH = 5000  # chars — posts longer than this risk truncation on platforms

def compliance_check(post_content: str, project_name: str) -> dict:
    """Run 7 EU Regulation 2021/1060 compliance checks on a post."""
    text = (post_content or "").lower()

    def has_any(keywords):
        return any(kw in text for kw in keywords)

    return {
        "check_eu_emblem":      has_any(EU_EMBLEM_KEYWORDS),
        "check_cofunding":      has_any(COFUNDING_KEYWORDS),
        "check_jtf_mention":    has_any(JTF_KEYWORDS),
        "check_hashtag":        has_any(HASHTAG_KEYWORDS),
        "check_project_name":   project_name.lower()[:20] in text if project_name else False,
        "check_char_limit":     len(post_content or "") <= MAX_CONTENT_LENGTH,
        "check_content_length": len((post_content or "").strip()) >= 50,
    }

# ── Scrapers per platform ─────────────────────────────────────────────────────
def scrape_linkedin(profile_url: str, project_nr: str) -> list[dict]:
    """
    LinkedIn public scraping via HTML.
    Note: LinkedIn aggressively rate-limits; this gets recent posts only.
    For production, consider the LinkedIn Marketing API (requires app approval).
    """
    posts = []
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; JTFComplianceBot/1.0; +https://jtf-rijnmond.kansenvoorwest.nl)",
        "Accept-Language": "nl-NL,nl;q=0.9",
    }
    # Normalise to /posts/ URL
    company_slug = re.search(r"/company/([^/]+)", profile_url)
    if not company_slug:
        return posts
    posts_url = f"https://www.linkedin.com/company/{company_slug.group(1)}/posts/"

    try:
        resp = requests.get(posts_url, headers=headers, timeout=15)
        if resp.status_code != 200:
            log.warning(f"LinkedIn {project_nr}: HTTP {resp.status_code}")
            return posts

        # Extract post text via regex (fragile but works for simple cases)
        matches = re.findall(
            r'"commentary"\s*:\s*\{"text"\s*:\s*"([^"]{30,})"', resp.text
        )
        for i, text in enumerate(matches[:10]):
            posts.append({
                "project_nr": project_nr,
                "platform":   "linkedin",
                "post_id":    hashlib.md5(text.encode()).hexdigest(),
                "url":        posts_url,
                "content":    text.encode().decode("unicode_escape"),
                "published_at": None,  # not easily parseable from HTML
            })
    except Exception as e:
        log.error(f"LinkedIn scrape error {project_nr}: {e}")

    return posts


def scrape_twitter(handle_or_url: str, project_nr: str) -> list[dict]:
    """Scrape Twitter/X via Bearer Token (Twitter API v2)."""
    bearer = os.environ.get("TWITTER_BEARER_TOKEN")
    if not bearer:
        log.warning("TWITTER_BEARER_TOKEN not set, skipping Twitter scrape")
        return []

    # Extract handle
    m = re.search(r"twitter\.com/([^/?\s]+)", handle_or_url) or re.search(r"x\.com/([^/?\s]+)", handle_or_url)
    handle = m.group(1) if m else handle_or_url.lstrip("@")

    posts = []
    try:
        # Look up user ID
        resp = requests.get(
            f"https://api.twitter.com/2/users/by/username/{handle}",
            headers={"Authorization": f"Bearer {bearer}"},
            timeout=10,
        )
        if resp.status_code != 200:
            log.warning(f"Twitter user lookup {handle}: {resp.status_code}")
            return posts

        user_id = resp.json()["data"]["id"]

        # Fetch recent tweets
        resp = requests.get(
            f"https://api.twitter.com/2/users/{user_id}/tweets",
            params={
                "max_results": 20,
                "tweet.fields": "created_at,public_metrics,text",
                "exclude": "retweets,replies",
            },
            headers={"Authorization": f"Bearer {bearer}"},
            timeout=10,
        )
        if resp.status_code != 200:
            log.warning(f"Twitter timeline {handle}: {resp.status_code}")
            return posts

        for tweet in resp.json().get("data", []):
            posts.append({
                "project_nr": project_nr,
                "platform":   "twitter",
                "post_id":    tweet["id"],
                "url":        f"https://twitter.com/{handle}/status/{tweet['id']}",
                "content":    tweet["text"],
                "published_at": tweet.get("created_at"),
                "likes":      tweet.get("public_metrics", {}).get("like_count"),
                "shares":     tweet.get("public_metrics", {}).get("retweet_count"),
                "comments":   tweet.get("public_metrics", {}).get("reply_count"),
            })

    except Exception as e:
        log.error(f"Twitter scrape error {project_nr} @{handle}: {e}")

    return posts


def scrape_platform(platform: str, url: str, project_nr: str) -> list[dict]:
    """Route to the correct scraper based on platform."""
    if platform == "linkedin":
        return scrape_linkedin(url, project_nr)
    elif platform in ("twitter", "x"):
        return scrape_twitter(url, project_nr)
    else:
        log.info(f"Platform '{platform}' not yet implemented for {project_nr}")
        return []


# ── Main scraping loop ────────────────────────────────────────────────────────
def run_scrape(filter_project: Optional[str] = None, dry_run: bool = False):
    log.info("=" * 60)
    log.info("JTF Compliance Scraper starting")
    log.info(f"dry_run={dry_run}, filter={filter_project or 'all'}")

    # Create scrape run record
    run_id = None
    if not dry_run:
        run = sb.table("scrape_runs").insert({
            "status": "running",
            "triggered_by": os.environ.get("GITHUB_ACTOR", "manual"),
        }).execute()
        run_id = run.data[0]["id"]
        log.info(f"Scrape run ID: {run_id}")

    # Load projects + social profiles from DB
    projects_resp = sb.table("projects").select("nr, naam").execute()
    profiles_resp = sb.table("social_profiles").select("*").execute()

    projects = {p["nr"]: p for p in projects_resp.data}
    profiles = profiles_resp.data

    if filter_project:
        profiles = [p for p in profiles if p["project_nr"] == filter_project]

    log.info(f"Scraping {len(set(p['project_nr'] for p in profiles))} projects, {len(profiles)} profiles")

    all_posts = []
    for profile in profiles:
        project_nr = profile["project_nr"]
        platform   = profile["platform"]
        url        = profile["url"]

        if platform == "website":
            continue  # websites scraped separately in future

        project_name = projects.get(project_nr, {}).get("naam", "")
        log.info(f"  Scraping {project_nr} [{platform}] {url}")

        posts = scrape_platform(platform, url, project_nr)
        log.info(f"    → {len(posts)} posts found")

        for post in posts:
            checks = compliance_check(post["content"] or "", project_name)
            post["_compliance"] = checks
        all_posts.extend(posts)

        time.sleep(2)  # Rate limiting

    log.info(f"Total posts scraped: {len(all_posts)}")

    if dry_run:
        log.info("DRY RUN — not saving to database")
        for p in all_posts[:5]:
            log.info(f"  Sample: {p['project_nr']} [{p['platform']}] score={sum(p['_compliance'].values())}/7")
        return

    # Save posts + compliance results
    new_posts = 0
    for post in all_posts:
        checks = post.pop("_compliance", {})
        try:
            # Upsert post (deduplicate by platform + post_id)
            post["scrape_run_id"] = run_id
            result = sb.table("posts").upsert(
                post, on_conflict="platform,post_id"
            ).execute()

            if result.data:
                post_id = result.data[0]["id"]
                # Save compliance result
                sb.table("compliance_results").upsert({
                    "post_id": post_id,
                    "scrape_run_id": run_id,
                    **checks,
                }, on_conflict="post_id").execute()
                new_posts += 1
        except Exception as e:
            log.error(f"DB insert error: {e}")

    # Update scrape run
    sb.table("scrape_runs").update({
        "status": "success",
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "projects_scraped": len(set(p["project_nr"] for p in all_posts)),
        "posts_found": len(all_posts),
        "posts_new": new_posts,
    }).eq("id", run_id).execute()

    log.info(f"Done! {new_posts} posts saved to DB.")


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JTF Social Media Compliance Scraper")
    parser.add_argument("--project", help="Only scrape one project nr (e.g. JTFW-00003)")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to database")
    args = parser.parse_args()

    run_scrape(filter_project=args.project, dry_run=args.dry_run)
