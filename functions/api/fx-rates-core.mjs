/**
 * Live MYR → GBP / AED / INR rates with ~6h cache and fixed fallbacks.
 */

import { corsHeaders, jsonResponse } from "./stripe-http.mjs";

export const FX_FALLBACK = {
  GBP: 0.18,
  AED: 0.85,
  INR: 20,
};

const CACHE_MS = 6 * 60 * 60 * 1000;
let memoryCache = null;

function roundRate(n, digits) {
  const d = digits == null ? 6 : digits;
  const x = Number(n);
  if (!Number.isFinite(x) || x <= 0) return null;
  return Number(x.toFixed(d));
}

async function fetchFrankfurter() {
  const url =
    "https://api.frankfurter.app/latest?from=MYR&to=GBP,AED,INR";
  const res = await fetch(url, { headers: { Accept: "application/json" } });
  if (!res.ok) throw new Error("frankfurter_" + res.status);
  const data = await res.json();
  const r = data && data.rates;
  if (!r) throw new Error("frankfurter_empty");
  return {
    GBP: roundRate(r.GBP),
    AED: roundRate(r.AED),
    INR: roundRate(r.INR),
    source: "frankfurter",
    asOf: data.date || null,
  };
}

async function fetchOpenErApi() {
  const url = "https://open.er-api.com/v6/latest/MYR";
  const res = await fetch(url, { headers: { Accept: "application/json" } });
  if (!res.ok) throw new Error("erapi_" + res.status);
  const data = await res.json();
  if (data.result !== "success" || !data.rates) throw new Error("erapi_bad");
  const r = data.rates;
  return {
    GBP: roundRate(r.GBP),
    AED: roundRate(r.AED),
    INR: roundRate(r.INR),
    source: "open.er-api.com",
    asOf: data.time_last_update_utc || null,
  };
}

function validBundle(b) {
  return (
    b &&
    Number.isFinite(b.GBP) &&
    b.GBP > 0 &&
    Number.isFinite(b.AED) &&
    b.AED > 0 &&
    Number.isFinite(b.INR) &&
    b.INR > 0
  );
}

export async function getFxRates() {
  const now = Date.now();
  if (memoryCache && now - memoryCache.fetchedAt < CACHE_MS && validBundle(memoryCache.rates)) {
    return {
      ...memoryCache.rates,
      cached: true,
      fetchedAt: memoryCache.fetchedAt,
      fallback: false,
    };
  }

  let live = null;
  try {
    live = await fetchFrankfurter();
  } catch (e1) {
    try {
      live = await fetchOpenErApi();
    } catch (e2) {
      console.warn("fx_live_failed", e1 && e1.message, e2 && e2.message);
    }
  }

  if (validBundle(live)) {
    const rates = {
      GBP: live.GBP,
      AED: live.AED,
      INR: live.INR,
      source: live.source,
      asOf: live.asOf,
    };
    memoryCache = { rates, fetchedAt: now };
    return { ...rates, cached: false, fetchedAt: now, fallback: false };
  }

  return {
    ...FX_FALLBACK,
    source: "fallback",
    asOf: null,
    cached: false,
    fetchedAt: now,
    fallback: true,
  };
}

export async function fxRatesHandler(event) {
  const method = String(event.httpMethod || event.method || "GET").toUpperCase();
  const origin = (event.headers && (event.headers.origin || event.headers.Origin)) || "";

  if (method === "OPTIONS") {
    return { statusCode: 204, headers: corsHeaders(origin), body: "" };
  }
  if (method !== "GET") {
    return jsonResponse(405, { ok: false, error: "method_not_allowed" });
  }

  const rates = await getFxRates();
  return jsonResponse(
    200,
    {
      ok: true,
      base: "MYR",
      rates: {
        GBP: rates.GBP,
        AED: rates.AED,
        INR: rates.INR,
      },
      source: rates.source,
      asOf: rates.asOf,
      fallback: !!rates.fallback,
      cached: !!rates.cached,
      fetchedAt: rates.fetchedAt,
    },
    {
      "Cache-Control": rates.fallback
        ? "public, max-age=300"
        : "public, max-age=3600",
    }
  );
}
