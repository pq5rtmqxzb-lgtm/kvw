# 🗂️ Project Manager Agent
## JTF Rijnmond Social Media Compliance Platform

---

## Role & Mandate

The PM Agent is responsible for **overall project delivery**. It translates EU audit deadlines and JTF reporting cycles into actionable development tickets, monitors progress across all other agents, and ensures nothing falls through the cracks.

---

## Current Sprint: Foundation (Week 1–2)

### Backlog — Priority Order

#### 🔴 CRITICAL (blocks other work)
- [ ] **INFRA-001** — Create Supabase project and configure environment
- [ ] **INFRA-002** — Run database migrations (001_initial_schema.sql)
- [ ] **INFRA-003** — Deploy Cloudflare Worker API proxy
- [ ] **INFRA-004** — Configure GitHub Secrets (SUPABASE_URL, keys)

#### 🟠 HIGH (Week 1)
- [ ] **BE-001** — Migrate 37 projects from JSON → Supabase `projects` table
- [ ] **BE-002** — Migrate PROJECT_URLS → Supabase `social_profiles` table
- [ ] **BE-003** — Seed compliance_results from existing scraped_results.json
- [ ] **SCRAPER-001** — Port compliance_check.py to use Supabase storage

#### 🟡 MEDIUM (Week 2)
- [ ] **FE-001** — Replace hardcoded PROJECTS JSON with Supabase API call
- [ ] **FE-002** — Replace hardcoded SCRAPED_RESULTS with API call
- [ ] **AUTH-001** — Add login page and Supabase Auth integration
- [ ] **SCRAPER-002** — Configure GitHub Actions weekly cron

#### 🟢 LOW (Week 3–4)
- [ ] **FE-003** — Add export-to-PDF compliance report
- [ ] **FE-004** — Email digest for JTF team (weekly summary)
- [ ] **BE-004** — Audit log table + RLS policies
- [ ] **BE-005** — Data retention policy (auto-purge >12 months)

---

## GitHub Issues Templates

The following templates should be created in `.github/ISSUE_TEMPLATE/`:

### Bug Report Template
```yaml
name: Bug Report
about: Something is broken
labels: bug
body:
  - type: input
    label: Tab/Feature affected
  - type: textarea
    label: Steps to reproduce
  - type: textarea
    label: Expected vs actual behavior
  - type: dropdown
    label: Severity
    options: [Critical, High, Medium, Low]
```

### Feature Request Template
```yaml
name: Feature Request
labels: enhancement
body:
  - type: input
    label: User story ("As a [role] I want...")
  - type: textarea
    label: Acceptance criteria
  - type: input
    label: Agent owner (PM/Backend/Scraper/Frontend)
```

---

## Weekly Status Report Template

```markdown
## JTF Compliance Tool — Week [N] Status

### ✅ Completed this week
- ...

### 🔄 In progress
- ...

### 🚫 Blocked
- ...

### 📊 Metrics
- Projects monitored: 37
- Posts scraped (last 7 days): N
- Compliance rate: N%
- Last scrape run: [date]

### 🗓️ Next week
- ...
```

---

## EU Audit Deadlines (Critical Dates)

| Date | Event | Action Required |
|---|---|---|
| Quarterly | JTF progress report | Export compliance summary PDF |
| Annually | EU audit possible | Full post history + evidence export |
| Per project | Project closure | Final compliance certificate |

---

## Escalation Rules

1. If any agent is blocked > 2 days → PM Agent raises GitHub Issue with `blocked` label
2. If compliance rate drops below 70% → immediate alert to JTF team
3. If scraper fails 2 consecutive runs → create CRITICAL ticket
4. If Supabase/Cloudflare outage → fallback to static JSON export (emergency mode)
