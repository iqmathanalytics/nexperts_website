/**
 * Cloudflare Pages — POST /api/stripe-checkout
 */
import { stripeCheckoutHandler } from "./stripe-checkout-core.mjs";
import { applyCfEnv, headersToObject, netlifyToCfResponse } from "./stripe-http.mjs";

export async function onRequestOptions(context) {
  applyCfEnv(context.env || {});
  const result = await stripeCheckoutHandler({
    httpMethod: "OPTIONS",
    headers: headersToObject(context.request.headers),
  });
  return netlifyToCfResponse(result);
}

export async function onRequestPost(context) {
  applyCfEnv(context.env || {});
  const text = await context.request.text();
  const result = await stripeCheckoutHandler({
    httpMethod: "POST",
    headers: headersToObject(context.request.headers),
    body: text,
  });
  return netlifyToCfResponse(result);
}
