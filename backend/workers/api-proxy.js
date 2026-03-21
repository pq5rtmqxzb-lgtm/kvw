/**
 * Cloudflare Worker — JTF Compliance API Proxy
 *
 * Proxies requests to Supabase REST API, injects the service key,
 * and adds CORS headers so GitHub Pages can call it.
 *
 * Deploy:
 *   npm install -g wrangler
 *   wrangler deploy
 *
 * Environment variables (set in Cloudflare dashboard or wrangler.toml):
 *   SUPABASE_URL         = https://xxxx.supabase.co
 *   SUPABASE_ANON_KEY    = eyJ...
 */

const ALLOWED_ORIGINS = [
  "https://pq5rtmqxzb-lgtm.github.io",
  "http://localhost:8765",
  "http://localhost:3000",
];

const CORS_HEADERS = (origin) => ({
  "Access-Control-Allow-Origin": ALLOWED_ORIGINS.includes(origin)
    ? origin
    : ALLOWED_ORIGINS[0],
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, apikey",
  "Access-Control-Max-Age": "86400",
});

// Public endpoints (no auth required)
const PUBLIC_PATHS = [
  "/rest/v1/projects",
  "/rest/v1/v_project_compliance",
  "/rest/v1/v_platform_stats",
];

function isPublicPath(path) {
  return PUBLIC_PATHS.some((p) => path.startsWith(p));
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const url = new URL(request.url);

    // Preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: CORS_HEADERS(origin),
      });
    }

    // Only proxy /api/* paths
    if (!url.pathname.startsWith("/api/")) {
      return new Response(JSON.stringify({ error: "Not found" }), {
        status: 404,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Strip /api prefix → Supabase path
    const supabasePath = url.pathname.replace(/^\/api/, "");
    const targetURL = `${env.SUPABASE_URL}${supabasePath}${url.search}`;

    // Check auth for protected endpoints
    const authHeader = request.headers.get("Authorization");
    if (!isPublicPath(supabasePath) && !authHeader) {
      return new Response(JSON.stringify({ error: "Authentication required" }), {
        status: 401,
        headers: {
          "Content-Type": "application/json",
          ...CORS_HEADERS(origin),
        },
      });
    }

    // Forward request to Supabase
    const headers = new Headers(request.headers);
    headers.set("apikey", env.SUPABASE_ANON_KEY);
    headers.set("Content-Type", "application/json");
    if (!authHeader) {
      // Public access: use anon key
      headers.set("Authorization", `Bearer ${env.SUPABASE_ANON_KEY}`);
    }
    // Remove host header to avoid Supabase rejecting
    headers.delete("Host");
    headers.delete("CF-Connecting-IP");

    try {
      const response = await fetch(targetURL, {
        method: request.method,
        headers,
        body: request.method !== "GET" ? request.body : undefined,
      });

      const body = await response.text();

      return new Response(body, {
        status: response.status,
        headers: {
          "Content-Type": response.headers.get("Content-Type") || "application/json",
          "Cache-Control": isPublicPath(supabasePath) ? "public, max-age=300" : "no-store",
          ...CORS_HEADERS(origin),
        },
      });
    } catch (err) {
      return new Response(JSON.stringify({ error: "Upstream error", detail: err.message }), {
        status: 502,
        headers: {
          "Content-Type": "application/json",
          ...CORS_HEADERS(origin),
        },
      });
    }
  },
};
