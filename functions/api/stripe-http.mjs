/** Shared HTTP helpers for Stripe + FX Pages/Netlify handlers. */

export function corsHeaders(origin) {
  const allow = String(process.env.BREVO_ALLOWED_ORIGINS || "*").trim() || "*";
  const o = String(origin || "").trim();
  const acao = allow === "*" ? "*" : o && allow.split(",").map((s) => s.trim()).includes(o) ? o : allow.split(",")[0].trim() || "*";
  return {
    "Access-Control-Allow-Origin": acao,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Stripe-Signature",
    "Access-Control-Max-Age": "86400",
  };
}

export function jsonResponse(status, body, extraHeaders) {
  return {
    statusCode: status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      ...corsHeaders(),
      ...(extraHeaders || {}),
    },
    body: JSON.stringify(body),
  };
}

export function siteBaseUrl(event) {
  const headers = (event && event.headers) || {};
  const host = String(headers["x-forwarded-host"] || headers.host || headers.Host || "")
    .split(",")[0]
    .trim();
  const hostOnly = host.split(":")[0].toLowerCase();
  const isLocal = hostOnly === "localhost" || hostOnly === "127.0.0.1";
  const proto = String(
    headers["x-forwarded-proto"] || (isLocal ? "http" : "https")
  )
    .split(",")[0]
    .trim();

  // Local netlify dev / static servers must return to this host — never production env URL.
  if (isLocal && host) {
    return `${proto}://${host}`.replace(/\/$/, "");
  }

  const env = String(
    process.env.NEXPERTS_PUBLIC_SITE_URL || process.env.NEXPERTS_EMAIL_SITE_URL || ""
  ).trim();
  if (env) return env.replace(/\/$/, "");
  if (host) return `${proto}://${host}`.replace(/\/$/, "");
  return "https://www.nexpertsacademy.com";
}

export function applyCfEnv(env) {
  const prev =
    typeof globalThis.process !== "undefined" &&
    globalThis.process &&
    globalThis.process.env &&
    typeof globalThis.process.env === "object"
      ? { ...globalThis.process.env }
      : {};
  globalThis.process = globalThis.process || {};
  globalThis.process.env = { ...prev, ...env };
}

export function headersToObject(headers) {
  const out = {};
  try {
    if (headers && typeof headers.entries === "function") {
      for (const [k, v] of headers.entries()) {
        out[String(k).toLowerCase()] = v;
      }
    }
  } catch (_) {
    /* ignore */
  }
  return out;
}

export function netlifyToCfResponse(result) {
  return new Response(result.body, {
    status: result.statusCode || 200,
    headers: result.headers || {},
  });
}
