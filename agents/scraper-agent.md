# 🕷️ Scraper / Data Agent
## JTF Rijnmond Social Media Compliance Platform

---

## Role & Mandate

The Scraper Agent is responsible for continuously collecting public social media posts from all 37 JTF projects, running the 7 EU compliance checks, and storing results in Supabase. It runs automatically every Monday via GitHub Actions.

---

## Compliance Checks (EU Regulation 2021/1060 Article 47 + Annex IX)

| # | Check | Keywords / Criteria |
|---|---|---|
| 1 | EU Emblem | "europese unie", "eu emblem", "#EU", "gefinancierd door de eu" |
| 2 | Co-funding statement | "medegefinancierd", "co-funded", "eu-bijdrage" |
| 3 | JTF mention | "jtf", "just transition fund", "kansenvoorwest" |
| 4 | #EUinmyregion hashtag | "#euinmyregion", "#euinmijnregio" |
| 5 | Project name | Project's own name in post text |
| 6 | Character limit | Post ≤ 5,000 chars (truncation risk) |
| 7 | Content length | Post ≥ 50 chars (not empty/useless) |

A post is **fully compliant** when it passes all 7 checks.

---

## Platform Coverage

| Platform | Method | Status | Notes |
|---|---|---|---|
| LinkedIn | HTML scraping | ⚠️ Limited | Rate-limited; Marketing API preferred for production |
| Twitter/X | API v2 (Bearer Token) | ✅ Working | Requires `TWITTER_BEARER_TOKEN` secret |
| Facebook | HTML scraping | 🔜 Planned | Public pages only |
| Instagram | HTML scraping | 🔜 Planned | Public profiles only |
| Website | HTTP + text extract | 🔜 Planned | Press releases / news sections |

---

## Scheduling

- **Frequency:** Weekly (every Monday 06:00 UTC)
- **Manual trigger:** GitHub Actions → weekly-scraper → Run workflow
- **Per-project trigger:** Provide project filter in workflow dispatch
- **Failure handling:** Auto-creates GitHub Issue on failure

---

## Running Locally

```bash
# Install
pip install supabase requests python-dotenv

# Full run
export SUPABASE_URL="https://xxxx.supabase.co"
export SUPABASE_SERVICE_KEY="eyJ..."
python3 backend/scripts/scraper.py

# Dry run (no DB writes)
python3 backend/scripts/scraper.py --dry-run

# Single project
python3 backend/scripts/scraper.py --project JTFW-00022
```

---

## Adding a New Platform

1. Add scraper function `scrape_PLATFORM(url, project_nr)` in `scraper.py`
2. Add `platform` to the `social_profiles.platform` CHECK constraint in SQL
3. Register in `scrape_platform()` router function
4. Test with `--dry-run --project JTFW-00022`
5. Update this document

---

## Known Limitations

- LinkedIn scraping is fragile (JavaScript-heavy pages)
- Twitter API free tier: 500k tweets/month read (sufficient for 37 projects)
- Facebook / Instagram require session cookies or Meta API (complex approval)
- Posts are deduplicated by `platform + post_id` — same post won't be double-counted
- Posts older than 13 months are automatically purged from DB (GDPR / storage)
