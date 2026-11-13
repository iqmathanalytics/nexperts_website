/**
 * Stripe webhook — on checkout.session.completed, send Brevo email + PDF once.
 * Idempotency: skip if session metadata.email_sent === "1" after marking via Stripe update,
 * or use in-memory / Blob set of processed session ids when available.
 */

import Stripe from "stripe";
import { sendEnrollmentConfirmation } from "./enrollment-email.mjs";
import { corsHeaders, jsonResponse } from "./stripe-http.mjs";

const processedSessions = new Set();

function getHeader(headers, name) {
  if (!headers) return "";
  const lower = name.toLowerCase();
  for (const [k, v] of Object.entries(headers)) {
    if (String(k).toLowerCase() === lower) return String(v || "");
  }
  return "";
}

export async function stripeWebhookHandler(event) {
  const method = String(event.httpMethod || event.method || "GET").toUpperCase();
  if (method === "OPTIONS") {
    return { statusCode: 204, headers: corsHeaders(), body: "" };
  }
  if (method !== "POST") {
    return jsonResponse(405, { ok: false, error: "method_not_allowed" });
  }

  const secret = String(process.env.STRIPE_SECRET_KEY || "").trim();
  const whSecret = String(process.env.STRIPE_WEBHOOK_SECRET || "").trim();
  if (!secret || !whSecret) {
    return jsonResponse(500, { ok: false, error: "stripe_webhook_not_configured" });
  }

  const stripe = new Stripe(secret);
  const signature = getHeader(event.headers, "stripe-signature");

  let rawBody = event.body || "";
  if (event.isBase64Encoded && typeof rawBody === "string") {
    rawBody = Buffer.from(rawBody, "base64").toString("utf8");
  }
  if (typeof rawBody !== "string") {
    rawBody = String(rawBody || "");
  }

  let stripeEvent;
  try {
    stripeEvent = stripe.webhooks.constructEvent(rawBody, signature, whSecret);
  } catch (err) {
    console.error("stripe_webhook_signature", err && err.message);
    return jsonResponse(400, { ok: false, error: "invalid_signature" });
  }

  if (stripeEvent.type !== "checkout.session.completed") {
    return jsonResponse(200, { ok: true, ignored: stripeEvent.type });
  }

  const session = stripeEvent.data.object;
  const sessionId = session && session.id;
  if (!sessionId) {
    return jsonResponse(200, { ok: true, skipped: "no_session" });
  }

  if (processedSessions.has(sessionId)) {
    return jsonResponse(200, { ok: true, duplicate: true });
  }

  const md = session.metadata || {};
  if (md.email_sent === "1") {
    processedSessions.add(sessionId);
    return jsonResponse(200, { ok: true, duplicate: true });
  }

  try {
    await sendEnrollmentConfirmation({ session });
    processedSessions.add(sessionId);
    try {
      await stripe.checkout.sessions.update(sessionId, {
        metadata: { ...md, email_sent: "1" },
      });
    } catch (updErr) {
      console.warn("stripe_metadata_update", updErr && updErr.message);
    }
    return jsonResponse(200, { ok: true, emailed: true });
  } catch (err) {
    console.error("enrollment_email_failed", err && err.message);
    return jsonResponse(500, {
      ok: false,
      error: "email_failed",
      detail: String((err && err.message) || "").slice(0, 160),
    });
  }
}
