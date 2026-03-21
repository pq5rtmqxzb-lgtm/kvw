/**
 * JTF Compliance — API Client
 * ============================
 * Wraps all calls to the Cloudflare Worker / Supabase backend.
 * Drop this <script> into the HTML before your app code.
 *
 * Usage:
 *   const projects = await API.getProjects();
 *   const stats    = await API.getProjectCompliance();
 *   const posts    = await API.getPostsForProject("JTFW-00003");
 */

const API = (() => {
  // ── Configuration ────────────────────────────────────────────────────────
  // Replace with your actual Cloudflare Worker URL after deployment.
  // During development, set window.API_BASE to override.
  const BASE = window.API_BASE || "https://jtf-api.YOUR-SUBDOMAIN.workers.dev/api";

  // Supabase anon key — safe to expose (protected by RLS + Worker CORS)
  const ANON_KEY = window.SUPABASE_ANON_KEY || "";

  let _authToken = null;  // set after login

  // ── Core fetch ───────────────────────────────────────────────────────────
  async function _fetch(path, opts = {}) {
    const headers = {
      "Content-Type": "application/json",
      "apikey": ANON_KEY,
      ...(opts.headers || {}),
    };
    if (_authToken) {
      headers["Authorization"] = `Bearer ${_authToken}`;
    }

    const resp = await fetch(`${BASE}${path}`, {
      ...opts,
      headers,
    });

    if (!resp.ok) {
      const err = await resp.text();
      throw new Error(`API error ${resp.status}: ${err}`);
    }
    return resp.json();
  }

  // ── Auth ─────────────────────────────────────────────────────────────────
  async function login(email, password) {
    const resp = await fetch(`${BASE}/auth/v1/token?grant_type=password`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "apikey": ANON_KEY },
      body: JSON.stringify({ email, password }),
    });
    if (!resp.ok) throw new Error("Login failed");
    const data = await resp.json();
    _authToken = data.access_token;
    sessionStorage.setItem("jtf_token", _authToken);
    return data;
  }

  function logout() {
    _authToken = null;
    sessionStorage.removeItem("jtf_token");
  }

  function restoreSession() {
    _authToken = sessionStorage.getItem("jtf_token") || null;
    return !!_authToken;
  }

  function isLoggedIn() {
    return !!_authToken;
  }

  // ── Projects ─────────────────────────────────────────────────────────────
  async function getProjects() {
    return _fetch("/rest/v1/projects?select=*&order=naam.asc");
  }

  async function getProject(nr) {
    const data = await _fetch(`/rest/v1/projects?nr=eq.${encodeURIComponent(nr)}&select=*,social_profiles(*)`);
    return data[0] || null;
  }

  // ── Social Profiles ──────────────────────────────────────────────────────
  async function getSocialProfiles(projectNr) {
    return _fetch(`/rest/v1/social_profiles?project_nr=eq.${encodeURIComponent(projectNr)}&order=platform.asc`);
  }

  // ── Compliance Views ─────────────────────────────────────────────────────
  async function getProjectCompliance() {
    return _fetch("/rest/v1/v_project_compliance?select=*&order=avg_score.asc");
  }

  async function getPlatformStats() {
    return _fetch("/rest/v1/v_platform_stats?select=*");
  }

  // ── Posts & Results ──────────────────────────────────────────────────────
  async function getPostsForProject(projectNr, limit = 50) {
    return _fetch(
      `/rest/v1/posts?project_nr=eq.${encodeURIComponent(projectNr)}&select=*,compliance_results(*)&order=published_at.desc&limit=${limit}`
    );
  }

  async function getAllPosts(limit = 200) {
    return _fetch(
      `/rest/v1/posts?select=*,compliance_results(*)&order=published_at.desc&limit=${limit}`
    );
  }

  // ── Scrape Runs ──────────────────────────────────────────────────────────
  async function getScrapeRuns(limit = 10) {
    return _fetch(`/rest/v1/scrape_runs?select=*&order=started_at.desc&limit=${limit}`);
  }

  // ── Compliance Analyser (client-side, for manual post analysis) ──────────
  function analysePostLocally(content, projectName) {
    const text = (content || "").toLowerCase();
    const EU_EMBLEM  = ["europese unie", "european union", "eu-embleem", "eu emblem", "#eu", "gefinancierd door de eu"];
    const COFUNDING  = ["medegefinancierd", "co-funded", "co-financing", "eu-bijdrage", "european regional development"];
    const JTF        = ["jtf", "just transition fund", "rechtvaardige transitie", "kansenvoorwest", "kansen voor west"];
    const HASHTAG    = ["#euinmyregion", "#euinmijnregio"];

    const has = (kws) => kws.some(k => text.includes(k));
    const checks = {
      eu_emblem:      has(EU_EMBLEM),
      cofunding:      has(COFUNDING),
      jtf_mention:    has(JTF),
      hashtag:        has(HASHTAG),
      project_name:   projectName ? text.includes(projectName.toLowerCase().slice(0, 15)) : false,
      char_limit:     (content || "").length <= 5000,
      content_length: (content || "").trim().length >= 50,
    };
    const passed = Object.values(checks).filter(Boolean).length;
    return { checks, passed, total: 7, score: Math.round(passed / 7 * 100) };
  }

  // ── Public API ───────────────────────────────────────────────────────────
  return {
    login, logout, restoreSession, isLoggedIn,
    getProjects, getProject,
    getSocialProfiles,
    getProjectCompliance, getPlatformStats,
    getPostsForProject, getAllPosts,
    getScrapeRuns,
    analysePostLocally,
  };
})();

// Auto-restore session on load
API.restoreSession();
