/**
 * Published course overrides (admin → live site).
 * GET  — returns overrides (Netlify Blobs, else static data/course-overrides.json).
 * POST — saves overrides to Blobs (Basic auth: ADMIN_USER / ADMIN_PASS env).
 */

import { getStore } from "@netlify/blobs";

const BLOB_KEY = "published";
const STORE_NAME = "nexperts-course-overrides";
const EMPTY = {
  version: 2,
  courses: {},
  card_order: {},
  brand_order: null,
  custom_brands: {},
  custom_courses: [],
};

function corsHeaders(origin) {
  const allow = process.env.ADMIN_ALLOWED_ORIGIN || origin || "*";
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Content-Type": "application/json; charset=utf-8",
  };
}

function checkAuth(req) {
  const auth = req.headers.get("authorization") || "";
  const user = process.env.ADMIN_USER || "admin";
  const pass = process.env.ADMIN_PASS || "admin123";
  const secret = process.env.ADMIN_PUBLISH_SECRET;
  if (secret && auth === `Bearer ${secret}`) return true;
  if (!auth.startsWith("Basic ")) return false;
  try {
    const decoded = atob(auth.slice(6));
    const colon = decoded.indexOf(":");
    if (colon < 0) return false;
    const u = decoded.slice(0, colon);
    const p = decoded.slice(colon + 1);
    return u === user && p === pass;
  } catch {
    return false;
  }
}

function normalizePayload(obj) {
  if (!obj || typeof obj !== "object") return { ...EMPTY };
  return {
    version: 2,
    courses: obj.courses && typeof obj.courses === "object" ? obj.courses : {},
    card_order:
      obj.card_order && typeof obj.card_order === "object" ? obj.card_order : {},
    brand_order: Array.isArray(obj.brand_order) ? obj.brand_order : null,
    custom_brands:
      obj.custom_brands && typeof obj.custom_brands === "object"
        ? obj.custom_brands
        : {},
    custom_courses: Array.isArray(obj.custom_courses) ? obj.custom_courses : [],
  };
}

async function loadStaticFallback(origin) {
  const base = origin || process.env.URL || "https://www.nexpertsacademy.com";
  const url = `${base.replace(/\/$/, "")}/data/course-overrides.json`;
  try {
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) return { ...EMPTY };
    return normalizePayload(await res.json());
  } catch {
    return { ...EMPTY };
  }
}

export default async (req, context) => {
  const origin = req.headers.get("origin") || "";
  const headers = corsHeaders(origin);

  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers });
  }

  const store = getStore({ name: STORE_NAME, consistency: "strong" });

  if (req.method === "GET") {
    try {
      const blob = await store.get(BLOB_KEY, { type: "json" });
      if (blob && typeof blob === "object") {
        const data = normalizePayload(blob);
        const has =
          Object.keys(data.courses).length > 0 ||
          (data.custom_courses && data.custom_courses.length > 0);
        if (has) {
          return new Response(JSON.stringify(data), { status: 200, headers });
        }
      }
    } catch (e) {
      console.warn("course-overrides GET blob:", e);
    }
    const fallback = await loadStaticFallback(
      origin || new URL(req.url).origin
    );
    return new Response(JSON.stringify(fallback), { status: 200, headers });
  }

  if (req.method === "POST") {
    if (!checkAuth(req)) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers,
      });
    }
    let body;
    try {
      body = normalizePayload(await req.json());
    } catch {
      return new Response(JSON.stringify({ error: "Invalid JSON body" }), {
        status: 400,
        headers,
      });
    }
    try {
      await store.setJSON(BLOB_KEY, body);
      return new Response(
        JSON.stringify({ ok: true, published_at: new Date().toISOString() }),
        { status: 200, headers }
      );
    } catch (e) {
      console.error("course-overrides POST:", e);
      return new Response(
        JSON.stringify({ error: "Could not save published overrides" }),
        { status: 500, headers }
      );
    }
  }

  return new Response(JSON.stringify({ error: "Method not allowed" }), {
    status: 405,
    headers,
  });
};
