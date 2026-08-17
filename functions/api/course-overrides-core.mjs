/**
 * Shared course-overrides API logic (Cloudflare Pages + optional Netlify).
 * Storage is injected: KV on Cloudflare, Blobs on Netlify.
 */

export const KV_KEY = "published";

export const DEFAULT_PRICING = {
  enabled: true,
  base: "my",
  regions: {
    my: {
      label: "Malaysia",
      countries: ["MY"],
      currency: "MYR",
      symbol: "RM",
      rate_from_myr: 1,
    },
    uk: {
      label: "United Kingdom",
      countries: ["GB"],
      currency: "GBP",
      symbol: "£",
      rate_from_myr: 0.18,
      rounding: 10,
    },
    dubai: {
      label: "Dubai / UAE",
      countries: ["AE"],
      currency: "AED",
      symbol: "AED",
      rate_from_myr: 0.85,
      rounding: 10,
    },
    india: {
      label: "India",
      countries: ["IN"],
      currency: "INR",
      symbol: "₹",
      rate_from_myr: 20,
      rounding: 10,
    },
  },
};

const REGION_KEYS = ["my", "uk", "dubai", "india"];

function cloneDefaultPricing() {
  return JSON.parse(JSON.stringify(DEFAULT_PRICING));
}

export function normalizePricing(raw) {
  const fallback = cloneDefaultPricing();
  if (!raw || typeof raw !== "object") return fallback;
  const regions = {};
  for (const key of REGION_KEYS) {
    const d = fallback.regions[key];
    const r = raw.regions && typeof raw.regions[key] === "object" ? raw.regions[key] : {};
    const rate = Number(r.rate_from_myr);
    const rounding = Number(r.rounding);
    const countries = Array.isArray(r.countries)
      ? r.countries.map((c) => String(c || "").toUpperCase()).filter(Boolean)
      : [];
    regions[key] = {
      label: String(r.label || d.label),
      countries: countries.length ? countries : d.countries.slice(),
      currency: String(r.currency || d.currency),
      symbol: String(r.symbol != null && r.symbol !== "" ? r.symbol : d.symbol),
      rate_from_myr: Number.isFinite(rate) && rate > 0 ? rate : d.rate_from_myr,
      rounding: Number.isFinite(rounding) && rounding > 0 ? rounding : d.rounding || 1,
    };
  }
  return {
    enabled: raw.enabled !== false,
    base: "my",
    regions,
  };
}

const EMPTY = {
  version: 2,
  courses: {},
  card_order: {},
  brand_order: null,
  custom_brands: {},
  custom_courses: [],
  pricing: cloneDefaultPricing(),
};

function payloadHasPublishedData(normalized, raw) {
  if (!normalized) return false;
  return (
    Object.keys(normalized.courses || {}).length > 0 ||
    (normalized.custom_courses && normalized.custom_courses.length > 0) ||
    Object.keys(normalized.custom_brands || {}).length > 0 ||
    (normalized.brand_order && normalized.brand_order.length > 0) ||
    Object.keys(normalized.card_order || {}).length > 0 ||
    !!(raw && raw.pricing && typeof raw.pricing === "object")
  );
}

/** Merge process.env with Cloudflare Pages `context.env` (string vars only; skip KV/D1 bindings). */
export function mergeRuntimeEnv(runtimeEnv = {}) {
  const fromProcess =
    typeof process !== "undefined" &&
    process.env &&
    typeof process.env === "object"
      ? process.env
      : {};
  const fromCf = {};
  if (runtimeEnv && typeof runtimeEnv === "object") {
    for (const [k, v] of Object.entries(runtimeEnv)) {
      if (
        v != null &&
        (typeof v === "string" ||
          typeof v === "number" ||
          typeof v === "boolean")
      ) {
        fromCf[k] = typeof v === "string" ? v : String(v);
      }
    }
  }
  return { ...fromProcess, ...fromCf };
}

export function adminCredentials(runtimeEnv = {}) {
  const env = mergeRuntimeEnv(runtimeEnv);
  const user =
    env.ADMIN_USER != null && String(env.ADMIN_USER).trim() !== ""
      ? String(env.ADMIN_USER).trim()
      : "admin";
  const pass =
    env.ADMIN_PASS != null && String(env.ADMIN_PASS).trim() !== ""
      ? String(env.ADMIN_PASS).trim()
      : "123";
  return { user, pass };
}

/** Decode HTTP Basic credentials (Workers-safe: atob, Node fallback: Buffer). */
export function decodeBasicCredentials(authHeader) {
  if (!authHeader || !authHeader.startsWith("Basic ")) return null;
  try {
    const b64 = authHeader.slice(6).trim();
    let decoded;
    if (typeof atob === "function") {
      decoded = atob(b64);
    } else if (typeof Buffer !== "undefined") {
      decoded = Buffer.from(b64, "base64").toString("utf8");
    } else {
      return null;
    }
    const colon = decoded.indexOf(":");
    if (colon < 0) return null;
    return { user: decoded.slice(0, colon), pass: decoded.slice(colon + 1) };
  } catch {
    return null;
  }
}

export function corsHeaders(event, runtimeEnv = {}) {
  const env = mergeRuntimeEnv(runtimeEnv);
  const origin =
    event.headers.origin ||
    event.headers.Origin ||
    env.ADMIN_ALLOWED_ORIGIN ||
    "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Content-Type": "application/json; charset=utf-8",
  };
}

export function checkAuth(event, runtimeEnv = {}) {
  const auth =
    event.headers.authorization || event.headers.Authorization || "";
  const env = mergeRuntimeEnv(runtimeEnv);
  const secret = String(env.ADMIN_PUBLISH_SECRET || "").trim();
  if (secret && auth === `Bearer ${secret}`) return true;

  const { user, pass } = adminCredentials(runtimeEnv);
  const creds = decodeBasicCredentials(auth);
  if (!creds) return false;
  return creds.user === user && creds.pass === pass;
}

export function normalizePayload(obj) {
  if (!obj || typeof obj !== "object") {
    return {
      version: 2,
      courses: {},
      card_order: {},
      brand_order: null,
      custom_brands: {},
      custom_courses: [],
      pricing: cloneDefaultPricing(),
    };
  }
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
    pricing: normalizePricing(obj.pricing),
  };
}

export async function loadStaticFallback(event, runtimeEnv = {}) {
  const env = mergeRuntimeEnv(runtimeEnv);
  const base =
    event.headers.origin ||
    event.headers.Origin ||
    env.URL ||
    env.NEXPERTS_PUBLIC_SITE_URL ||
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
export async function handler(event, storage = {}, runtimeEnv = {}) {
  const method = (event.httpMethod || "GET").toUpperCase();
  const headers = corsHeaders(event, runtimeEnv);

  if (method === "OPTIONS") {
    return { statusCode: 204, headers, body: "" };
  }

  if (method === "GET") {
    if (storage.getPublished) {
      try {
        const blob = await storage.getPublished();
        if (blob && typeof blob === "object") {
          const data = normalizePayload(blob);
          const has = payloadHasPublishedData(data, blob);
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
    const fallback = await loadStaticFallback(event, runtimeEnv);
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(fallback),
    };
  }

  if (method === "POST") {
    if (!checkAuth(event, runtimeEnv)) {
      return {
        statusCode: 401,
        headers,
        body: JSON.stringify({
          error: "Unauthorized",
          hint:
            "Set ADMIN_USER and ADMIN_PASS in Cloudflare Pages → Settings → Environment variables (Production), then redeploy.",
        }),
      };
    }
    let parsed = {};
    try {
      parsed = JSON.parse(event.body || "{}");
    } catch {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: "Invalid JSON body" }),
      };
    }
    if (parsed && parsed._verify === true) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({ ok: true, verify: true }),
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
    const body = normalizePayload(parsed);
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

