/**
 * Cloudflare Pages — GET /api/fx-rates
 */
import { fxRatesHandler } from "./fx-rates-core.mjs";
import { applyCfEnv, headersToObject, netlifyToCfResponse } from "./stripe-http.mjs";

export async function onRequestOptions(context) {
  applyCfEnv(context.env || {});
  const result = await fxRatesHandler({
    httpMethod: "OPTIONS",
    headers: headersToObject(context.request.headers),
  });
  return netlifyToCfResponse(result);
}

export async function onRequestGet(context) {
  applyCfEnv(context.env || {});
  const result = await fxRatesHandler({
    httpMethod: "GET",
    headers: headersToObject(context.request.headers),
  });
  return netlifyToCfResponse(result);
}
