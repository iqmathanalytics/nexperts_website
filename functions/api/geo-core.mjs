/**
 * Shared geo country helper for display pricing (Cloudflare + Netlify).
 * Production: Cloudflare edge country only.
 * Local / netlify dev: NEXPERTS_DEV_GEO_COUNTRY or ?country=IN (dev hosts only).
 */

function headerGet(headers, name) {
  if (!headers) return "";
  const want = String(name).toLowerCase();
  for (const [k, v] of Object.entries(headers)) {
    if (String(k).toLowerCase() === want) return String(v || "").trim();
  }
  return "";
}

function normalizeCountry(raw) {
  const country = String(raw || "")
    .trim()
    .toUpperCase();
  if (!country || country === "XX" || country === "T1") return "";
  if (!/^[A-Z]{2}$/.test(country)) return "";
  return country;
}

function requestHost(headers) {
  return String(headerGet(headers, "x-forwarded-host") || headerGet(headers, "host") || "")
    .split(",")[0]
    .trim()
    .toLowerCase();
}

function isDevHost(host) {
  const h = String(host || "").split(":")[0];
  return h === "localhost" || h === "127.0.0.1" || h.endsWith(".netlify.app");
}

function queryCountry(event) {
  const q = event && event.queryStringParameters;
  if (q && q.country) return normalizeCountry(q.country);
  try {
    const rawUrl = event && (event.rawUrl || event.url);
    if (rawUrl) {
      const u = new URL(rawUrl, "http://localhost");
      return normalizeCountry(u.searchParams.get("country"));
    }
  } catch (_) {
    /* ignore */
  }
  return "";
}

/**
 * @param {object} event - Netlify-style event { headers, queryStringParameters, rawUrl }
 * @param {{ cfCountry?: string }} [opts]
 */
export function resolveGeoCountry(event, opts) {
  const headers = (event && event.headers) || {};
  const host = requestHost(headers);
  const allowDevOverride =
    isDevHost(host) || String(process.env.NEXPERTS_ALLOW_GEO_OVERRIDE || "").trim() === "1";

  if (allowDevOverride) {
    const fromQuery = queryCountry(event);
    if (fromQuery) return fromQuery;
    const fromEnv = normalizeCountry(process.env.NEXPERTS_DEV_GEO_COUNTRY);
    if (fromEnv) return fromEnv;
  }

  const fromCf = normalizeCountry(opts && opts.cfCountry);
  if (fromCf) return fromCf;

  return normalizeCountry(headerGet(headers, "cf-ipcountry"));
}

export function geoJsonResponse(country) {
  return {
    statusCode: 200,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "private, max-age=300",
      "Access-Control-Allow-Origin": "*",
    },
    body: JSON.stringify({ country: country || "" }),
  };
}

export function geoHandler(event, opts) {
  const method = String((event && (event.httpMethod || event.method)) || "GET").toUpperCase();
  if (method === "OPTIONS") {
    return {
      statusCode: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
      body: "",
    };
  }
  if (method !== "GET") {
    return {
      statusCode: 405,
      headers: { "Content-Type": "application/json; charset=utf-8" },
      body: JSON.stringify({ ok: false, error: "method_not_allowed" }),
    };
  }
  return geoJsonResponse(resolveGeoCountry(event, opts));
}
