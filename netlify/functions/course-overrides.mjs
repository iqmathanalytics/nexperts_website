/**
 * Published course overrides (admin → live site).
 * GET  — returns overrides (Netlify Blobs, else static data/course-overrides.json).
 * POST — saves overrides to Blobs (Basic auth: ADMIN_USER / ADMIN_PASS env).
 *
 * Uses Netlify classic handler(event) — same as enquiry-brevo.mjs.
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

function corsHeaders(event) {
  const origin =
    event.headers.origin ||
    event.headers.Origin ||
    process.env.ADMIN_ALLOWED_ORIGIN ||
    "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Content-Type": "application/json; charset=utf-8",
  };
}

function checkAuth(event) {
  const auth =
    event.headers.authorization || event.headers.Authorization || "";
  const user = process.env.ADMIN_USER || "admin";
  const pass = process.env.ADMIN_PASS || "admin123";
  const secret = process.env.ADMIN_PUBLISH_SECRET;
  if (secret && auth === `Bearer ${secret}`) return true;
  if (!auth.startsWith("Basic ")) return false;
  try {
    const decoded = Buffer.from(auth.slice(6), "base64").toString("utf8");
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

async function loadStaticFallback(event) {
  const base =
    event.headers.origin ||
    event.headers.Origin ||
    process.env.URL ||
    "https://www.nexpertsacademy.com";
  const url = `${String(base).replace(/\/$/, "")}/data/course-overrides.json`;
  try {
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) return { ...EMPTY };
    return normalizePayload(await res.json());
  } catch {
    return { ...EMPTY };
  }
}

export async function handler(event) {
  const method = (event.httpMethod || "GET").toUpperCase();
  const headers = corsHeaders(event);

  if (method === "OPTIONS") {
    return { statusCode: 204, headers, body: "" };
  }

  const store = getStore({ name: STORE_NAME, consistency: "strong" });

  if (method === "GET") {
    try {
      const blob = await store.get(BLOB_KEY, { type: "json" });
      if (blob && typeof blob === "object") {
        const data = normalizePayload(blob);
        const has =
          Object.keys(data.courses).length > 0 ||
          (data.custom_courses && data.custom_courses.length > 0);
        if (has) {
          return {
            statusCode: 200,
            headers,
            body: JSON.stringify(data),
          };
        }
      }
    } catch (e) {
      console.warn("course-overrides GET blob:", e);
    }
    const fallback = await loadStaticFallback(event);
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(fallback),
    };
  }

  if (method === "POST") {
    if (!checkAuth(event)) {
      return {
        statusCode: 401,
        headers,
        body: JSON.stringify({ error: "Unauthorized" }),
      };
    }
    let body;
    try {
      body = normalizePayload(JSON.parse(event.body || "{}"));
    } catch {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: "Invalid JSON body" }),
      };
    }
    try {
      await store.setJSON(BLOB_KEY, body);
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          ok: true,
          published_at: new Date().toISOString(),
        }),
      };
    } catch (e) {
      console.error("course-overrides POST:", e);
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ error: "Could not save published overrides" }),
      };
    }
  }

  return {
    statusCode: 405,
    headers,
    body: JSON.stringify({ error: "Method not allowed" }),
  };
}
