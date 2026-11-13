/**
 * Cloudflare Pages — POST /api/stripe-fulfill
 */
import { stripeFulfillHandler } from "./stripe-fulfill-core.mjs";
import { applyCfEnv, headersToObject, netlifyToCfResponse } from "./stripe-http.mjs";

export async function onRequestOptions(context) {
  applyCfEnv(context.env || {});
  const result = await stripeFulfillHandler({
    httpMethod: "OPTIONS",
    headers: headersToObject(context.request.headers),
  });
  return netlifyToCfResponse(result);
}

export async function onRequestPost(context) {
  applyCfEnv(context.env || {});
  const text = await context.request.text();
  const result = await stripeFulfillHandler({
    httpMethod: "POST",
    headers: headersToObject(context.request.headers),
    body: text,
  });
  return netlifyToCfResponse(result);
}
