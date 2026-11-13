/**
 * Cloudflare Pages — POST /api/stripe-webhook
 * Needs raw body for signature verification.
 */
import { stripeWebhookHandler } from "./stripe-webhook-core.mjs";
import { applyCfEnv, headersToObject, netlifyToCfResponse } from "./stripe-http.mjs";

export async function onRequestOptions(context) {
  applyCfEnv(context.env || {});
  const result = await stripeWebhookHandler({
    httpMethod: "OPTIONS",
    headers: headersToObject(context.request.headers),
  });
  return netlifyToCfResponse(result);
}

export async function onRequestPost(context) {
  applyCfEnv(context.env || {});
  const text = await context.request.text();
  const result = await stripeWebhookHandler({
    httpMethod: "POST",
    headers: headersToObject(context.request.headers),
    body: text,
    isBase64Encoded: false,
  });
  return netlifyToCfResponse(result);
}
