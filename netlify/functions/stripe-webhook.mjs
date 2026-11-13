/**
 * Netlify Function — Stripe webhook.
 * Raw body is required for signature verification (configured in netlify.toml).
 */
export { stripeWebhookHandler as handler } from "../../functions/api/stripe-webhook-core.mjs";
