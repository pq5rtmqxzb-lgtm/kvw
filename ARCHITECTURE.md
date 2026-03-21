# JTF Rijnmond — Social Media Compliance Platform
## Architecture & Agent Design Document

> **Status:** v1.0 — Initial design
> **Owner:** JTF Rijnmond / Kansen voor West
> **Stack decision date:** 2026-03-21

---

## 1. Current State vs Target State

| Dimension | Current (v0) | Target (v1) |
|---|---|---|
| Architecture | Single HTML file, data embedded | API-driven SPA + serverless backend |
| Data storage | Hard-coded JSON in HTML | PostgreSQL via Supabase |
| Scraping | Manual, one-off Python script | Scheduled GitHub Actions (weekly) |
| Auth | None | Supabase Auth (email/password) |
| Hosting | GitHub Pages | GitHub Pages (FE) + Cloudflare Workers (API proxy) |
| Deployment | Manual git push | CI/CD via GitHub Actions |
| Compliance checks | Client-side JS | Server-side Python + stored results |
| Auditability | None | Full run history in database |

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AGENTS                                    │
│  PM Agent │ Backend Agent │ Scraper Agent │ Frontend Agent       │
└─────────────────────────────────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   GitHub Issues        GitHub Actions      Supabase (DB + Auth)
   (tickets/plan)       (CI/CD + cron)      (PostgreSQL + REST)
                               │                   │
                    ┌──────────┘                   │
                    ▼                              ▼
              Scraper Worker              Cloudflare Workers
              (Python + APIs)            (API proxy / edge logic)
                    │                              │
                    └──────────────┬───────────────┘
                                   ▼
                           GitHub Pages
                        (HTML/JS Frontend)
```

### Data Flow

1. **Weekly scrape** → GitHub Actions triggers `scraper.py`
2. **Scraper** → fetches social media posts via public APIs / HTML scraping
3. **Compliance engine** → runs 7 EU-regulation checks per post
4. **Results** → stored in Supabase `posts` + `compliance_results` tables
5. **Frontend** → fetches results from Supabase REST API (via Cloudflare Worker proxy)
6. **User** → views dashboard, analyses posts, exports reports

---

## 3. Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| Frontend | Vanilla JS → progressive Vue 3 (CDN) | No build step, GitHub Pages compatible |
| API Proxy | Cloudflare Workers (free tier) | Edge performance, hides Supabase keys |
| Database | Supabase PostgreSQL | Managed Postgres, free tier, built-in REST + Auth |
| Auth | Supabase Auth | Email/password, RLS policies per user role |
| Scraping | Python + GitHub Actions | Free on public repos, cron scheduling |
| CI/CD | GitHub Actions | Native GitHub integration |
| Hosting | GitHub Pages | Free, already configured |

---

## 4. Database Schema

See `backend/migrations/001_initial_schema.sql`

**Key tables:**
- `projects` — 37 JTF projects with metadata and URLs
- `social_profiles` — per-project social media handles/URLs
- `scrape_runs` — history of every scraping session
- `posts` — individual social media posts collected
- `compliance_results` — per-post compliance check results (7 checks)
- `audit_log` — who viewed/changed what

---

## 5. Agent Responsibilities

### 🗂️ Project Manager Agent (`agents/pm-agent.md`)
- Owns GitHub Issues and Milestones
- Tracks progress against EU audit deadlines
- Generates weekly status report
- Escalates blocked items

### 🔧 Backend / API Agent (`agents/backend-agent.md`)
- Owns Supabase schema and migrations
- Implements Cloudflare Worker API proxy
- Defines RLS security policies
- Manages API versioning

### 🕷️ Scraper / Data Agent (`agents/scraper-agent.md`)
- Owns `backend/scripts/scraper.py`
- Schedules GitHub Actions cron workflow
- Implements compliance engine (7 checks)
- Handles rate limiting, retries, deduplication

### 🎨 Frontend Agent (`agents/frontend-agent.md`)
- Owns all HTML/CSS/JS in `frontend/`
- Migrates hardcoded JSON → API calls
- Implements auth flow (login/logout)
- Adds export-to-PDF and report generation

---

## 6. Milestones

| Milestone | Description | Target |
|---|---|---|
| M1 – Database | Supabase schema live, data migrated | Week 1 |
| M2 – API Proxy | Cloudflare Worker deployed | Week 1 |
| M3 – Scraper | Automated weekly scraping running | Week 2 |
| M4 – Auth | Login/logout for JTF team | Week 2 |
| M5 – Frontend v2 | API-driven frontend deployed | Week 3 |
| M6 – Reports | PDF export + email digest | Week 4 |
| M7 – Audit trail | Full run history + logging | Week 4 |

---

## 7. Security & Compliance

- Supabase Row Level Security (RLS) — each user sees only their data
- Cloudflare Worker hides Supabase anon key from frontend
- All secrets in GitHub Secrets / Cloudflare environment variables
- GDPR: only public social media posts are stored; no PII beyond public handles
- Data retention: posts older than 12 months auto-purged (Postgres cron)

---

## 8. Environment Variables

```env
# Supabase
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...   # server-side only, never in frontend

# Cloudflare
CF_ACCOUNT_ID=...
CF_API_TOKEN=...

# GitHub Actions scraper
TWITTER_BEARER_TOKEN=...      # optional if using v2 API
LINKEDIN_SESSION=...          # session cookie (limited, unofficial)
```
