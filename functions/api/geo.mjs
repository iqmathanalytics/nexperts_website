/**
 * Cloudflare Pages Function — GET `/api/geo`.
 * Returns the visitor country from the Cloudflare edge (no third-party IP API).
 * Used only for client-side enroll-card display; HTML/schema stay Malaysia RM.
 * Local Netlify uses netlify/functions/geo.mjs → same geo-core.
 */
import { geoHandler } from "./geo-core.mjs";
import { headersToObject, netlifyToCfResponse } from "./stripe-http.mjs";

export async function onRequestOptions(context) {
  const result = geoHandler(
    {
      httpMethod: "OPTIONS",
      headers: headersToObject(context.request.headers),
      rawUrl: context.request.url,
    },
    {}
  );
  return netlifyToCfResponse(result);
}

export async function onRequestGet(context) {
  const { request } = context;
  const cf = request && request.cf ? request.cf : {};
  const result = geoHandler(
    {
      httpMethod: "GET",
      headers: headersToObject(request.headers),
      rawUrl: request.url,
    },
    { cfCountry: typeof cf.country === "string" ? cf.country : "" }
  );
  return netlifyToCfResponse(result);
}
