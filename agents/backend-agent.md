# 🔧 Backend / API Agent
## JTF Rijnmond Social Media Compliance Platform

---

## Role & Mandate

The Backend Agent owns all server-side infrastructure: the Supabase database, the Cloudflare Worker API proxy, security policies, and data migrations. It ensures the frontend always has fast, secure, and reliable access to compliance data.

---

## Setup Checklist (one-time)

### Step 1 — Create Supabase project
1. Go to https://supabase.com → New Project
2. Name: `jtf-rijnmond-compliance`
3. Region: `West EU (Frankfurt)` ← GDPR-friendly
4. Note your: Project URL, anon key, service key

### Step 2 — Run migrations
```sql
-- In Supabase SQL Editor:
-- Copy and run: backend/migrations/001_initial_schema.sql
```

### Step 3 — Seed initial data
```bash
export SUPABASE_URL="https://xxxx.supabase.co"
export SUPABASE_SERVICE_KEY="eyJ..."
python3 backend/migrations/002_seed_projects.py
```

### Step 4 — Deploy Cloudflare Worker
```bash
npm install -g wrangler
cd backend/workers
wrangler secret put SUPABASE_ANON_KEY   # paste your anon key
wrangler deploy
```

### Step 5 — Set GitHub Secrets
In repo Settings → Secrets → Actions:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`
- `TWITTER_BEARER_TOKEN` (optional)

---

## Database Tables Overview

| Table | Purpose | Rows (est.) |
|---|---|---|
| `projects` | 37 JTF projects | 37 |
| `social_profiles` | Per-project social URLs | ~100 |
| `scrape_runs` | Scraper run history | ~50/year |
| `posts` | Collected social posts | ~1,000/year |
| `compliance_results` | 7-check results per post | ~1,000/year |
| `audit_log` | User action log | ~10k/year |

## Views

| View | Purpose |
|---|---|
| `v_project_compliance` | Per-project compliance score + post count |
| `v_platform_stats` | Per-platform breakdown |

---

## API Endpoints (via Cloudflare Worker)

Base URL: `https://jtf-api.YOUR.workers.dev/api`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/rest/v1/projects` | Public | All 37 projects |
| GET | `/rest/v1/social_profiles?project_nr=eq.JTFW-...` | Public | Project socials |
| GET | `/rest/v1/v_project_compliance` | Public | Compliance scores |
| GET | `/rest/v1/v_platform_stats` | Public | Platform breakdown |
| GET | `/rest/v1/posts?project_nr=eq.JTFW-...` | Auth | Posts per project |
| GET | `/rest/v1/compliance_results` | Auth | Raw check results |
| GET | `/rest/v1/scrape_runs` | Auth | Scraper run history |

---

## Security Notes

- Cloudflare Worker hides service key from frontend
- Row Level Security (RLS) on all sensitive tables
- Public views expose only aggregated compliance data
- Individual posts require authentication (JTF team login)
- GDPR: no PII stored beyond publicly available social handles
