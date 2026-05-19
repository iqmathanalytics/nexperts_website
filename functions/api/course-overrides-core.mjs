/**
 * Shared course-overrides API logic (Cloudflare Pages + optional Netlify).
 * Storage is injected: KV on Cloudflare, Blobs on Netlify.
 */

const BLOB_KEY = "published";
const EMPTY = {
  version: 2,
  courses: {},
  card_order: {},
  brand_order: null,
  custom_brands: {},
  custom_courses: [],
};

export function corsHeaders(event) {
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

export function checkAuth(event) {
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

export function normalizePayload(obj) {
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

export async function loadStaticFallback(event) {
  const base =
    event.headers.origin ||
    event.headers.Origin ||
    process.env.URL ||
    process.env.NEXPERTS_PUBLIC_SITE_URL ||
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

/**
 * @param {object} event — { httpMethod, headers, body }
 * @param {{ getPublished?: () => Promise<object|null>, setPublished?: (data: object) => Promise<void> }} storage
 */
export async function handler(event, storage = {}) {
  const method = (event.httpMethod || "GET").toUpperCase();
  const headers = corsHeaders(event);

  if (method === "OPTIONS") {
    return { statusCode: 204, headers, body: "" };
  }

  if (method === "GET") {
    if (storage.getPublished) {
      try {
        const blob = await storage.getPublished();
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
        console.warn("course-overrides GET storage:", e);
      }
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
    if (!storage.setPublished) {
      return {
        statusCode: 503,
        headers,
        body: JSON.stringify({
          error: "Publish storage not configured",
          hint:
            "On Cloudflare Pages: bind KV namespace COURSE_OVERRIDES in project Settings → Functions. Or Export JSON, commit data/course-overrides.json, and redeploy.",
        }),
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
      await storage.setPublished(body);
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

export { BLOB_KEY as STORAGE_KEY };
