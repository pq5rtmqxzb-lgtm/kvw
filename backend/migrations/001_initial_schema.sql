-- ============================================================
-- JTF Rijnmond Social Media Compliance Platform
-- Migration 001: Initial Schema
-- Run in: Supabase SQL Editor
-- ============================================================

-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- ============================================================
-- PROJECTS
-- ============================================================
create table if not exists public.projects (
  id          uuid primary key default uuid_generate_v4(),
  nr          text unique not null,          -- e.g. "JTFW-00003"
  naam        text not null,                 -- project name
  penvoerder  text,                          -- lead partner
  stad        text,                          -- city
  begunstigden text[],                       -- all partners
  eu_bijdrage numeric(15,2),                 -- EU contribution €
  kosten      numeric(15,2),                 -- total costs €
  startdatum  date,
  einddatum   date,
  prioriteit  text,
  spoor       text,                          -- JTF track
  beschrijving text,
  created_at  timestamptz default now(),
  updated_at  timestamptz default now()
);

comment on table public.projects is 'JTF Rijnmond financed projects from Excel register';

-- ============================================================
-- SOCIAL PROFILES
-- Each project can have multiple social media profiles
-- ============================================================
create table if not exists public.social_profiles (
  id          uuid primary key default uuid_generate_v4(),
  project_nr  text references public.projects(nr) on delete cascade,
  platform    text not null check (platform in ('website','linkedin','twitter','facebook','instagram','youtube','tiktok')),
  url         text not null,
  handle      text,                          -- @username or page name
  verified    boolean default false,         -- manually verified by JTF team
  active      boolean default true,
  created_at  timestamptz default now()
);

create index idx_social_profiles_project on public.social_profiles(project_nr);
create index idx_social_profiles_platform on public.social_profiles(platform);

-- ============================================================
-- SCRAPE RUNS
-- Every execution of the scraper is logged here
-- ============================================================
create table if not exists public.scrape_runs (
  id            uuid primary key default uuid_generate_v4(),
  started_at    timestamptz default now(),
  finished_at   timestamptz,
  status        text default 'running' check (status in ('running','success','partial','failed')),
  projects_scraped integer default 0,
  posts_found   integer default 0,
  posts_new     integer default 0,
  error_message text,
  triggered_by  text default 'github-actions'  -- or 'manual'
);

-- ============================================================
-- POSTS
-- Individual social media posts collected per project
-- ============================================================
create table if not exists public.posts (
  id              uuid primary key default uuid_generate_v4(),
  scrape_run_id   uuid references public.scrape_runs(id),
  project_nr      text references public.projects(nr) on delete cascade,
  platform        text not null,
  post_id         text,                         -- native platform post ID
  url             text,                          -- direct link to post
  content         text,                          -- full post text
  published_at    timestamptz,
  likes           integer,
  shares          integer,
  comments        integer,
  has_eu_emblem   boolean,                       -- image analysis (future)
  scraped_at      timestamptz default now(),
  unique(platform, post_id)                      -- deduplication
);

create index idx_posts_project on public.posts(project_nr);
create index idx_posts_platform on public.posts(platform);
create index idx_posts_published on public.posts(published_at desc);

-- ============================================================
-- COMPLIANCE RESULTS
-- 7 checks per post per EU Regulation 2021/1060 Article 47
-- ============================================================
create table if not exists public.compliance_results (
  id                    uuid primary key default uuid_generate_v4(),
  post_id               uuid references public.posts(id) on delete cascade,
  scrape_run_id         uuid references public.scrape_runs(id),
  -- The 7 compliance checks
  check_eu_emblem       boolean,    -- EU emblem visible/mentioned
  check_cofunding       boolean,    -- co-funding statement present
  check_jtf_mention     boolean,    -- JTF / Just Transition Fund named
  check_hashtag         boolean,    -- #EUinmyregion hashtag used
  check_project_name    boolean,    -- project name mentioned
  check_char_limit      boolean,    -- post not too long (truncated risk)
  check_content_length  boolean,    -- sufficient content (not empty)
  -- Aggregate
  checks_passed         integer generated always as (
    (check_eu_emblem::int + check_cofunding::int + check_jtf_mention::int +
     check_hashtag::int + check_project_name::int + check_char_limit::int +
     check_content_length::int)
  ) stored,
  compliance_score      numeric(5,2) generated always as (
    round(
      (check_eu_emblem::int + check_cofunding::int + check_jtf_mention::int +
       check_hashtag::int + check_project_name::int + check_char_limit::int +
       check_content_length::int) * 100.0 / 7.0, 2
    )
  ) stored,
  notes                 text,
  checked_at            timestamptz default now()
);

create index idx_compliance_post on public.compliance_results(post_id);
create index idx_compliance_score on public.compliance_results(compliance_score);

-- ============================================================
-- AUDIT LOG
-- Who did what and when (GDPR + EU accountability)
-- ============================================================
create table if not exists public.audit_log (
  id          bigserial primary key,
  user_id     uuid,                    -- Supabase auth user id
  user_email  text,
  action      text not null,           -- 'view_post', 'export_report', etc.
  entity_type text,                    -- 'post', 'project', 'report'
  entity_id   text,
  ip_address  text,
  created_at  timestamptz default now()
);

-- ============================================================
-- VIEWS: handy aggregations
-- ============================================================

-- Project compliance summary
create or replace view public.v_project_compliance as
select
  p.nr,
  p.naam,
  p.penvoerder,
  p.eu_bijdrage,
  count(distinct po.id)                               as total_posts,
  count(distinct po.id) filter (where cr.checks_passed = 7) as fully_compliant,
  round(avg(cr.compliance_score), 1)                  as avg_score,
  max(po.published_at)                                as last_post_at
from public.projects p
left join public.posts po on po.project_nr = p.nr
left join public.compliance_results cr on cr.post_id = po.id
group by p.nr, p.naam, p.penvoerder, p.eu_bijdrage;

-- Platform breakdown
create or replace view public.v_platform_stats as
select
  platform,
  count(*)                                            as total_posts,
  round(avg(cr.compliance_score), 1)                  as avg_compliance,
  count(*) filter (where cr.checks_passed >= 5)       as mostly_compliant
from public.posts po
join public.compliance_results cr on cr.post_id = po.id
group by platform;

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================
alter table public.projects enable row level security;
alter table public.posts enable row level security;
alter table public.compliance_results enable row level security;
alter table public.audit_log enable row level security;

-- Public read access for projects (dashboard is semi-public)
create policy "Public can read projects"
  on public.projects for select
  using (true);

-- Authenticated users can read posts
create policy "Auth users read posts"
  on public.posts for select
  using (auth.role() = 'authenticated');

-- Service role can insert (scraper uses service key)
create policy "Service role inserts posts"
  on public.posts for insert
  with check (auth.role() = 'service_role');

create policy "Auth users read compliance"
  on public.compliance_results for select
  using (auth.role() = 'authenticated');

create policy "Service role inserts compliance"
  on public.compliance_results for insert
  with check (auth.role() = 'service_role');

-- ============================================================
-- AUTO-UPDATE updated_at
-- ============================================================
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger trg_projects_updated_at
  before update on public.projects
  for each row execute function public.set_updated_at();

-- ============================================================
-- DATA RETENTION: auto-purge posts older than 13 months
-- (run via pg_cron in Supabase or a scheduled edge function)
-- ============================================================
-- select cron.schedule('purge-old-posts', '0 3 1 * *',
--   $$delete from public.posts where published_at < now() - interval '13 months'$$);
