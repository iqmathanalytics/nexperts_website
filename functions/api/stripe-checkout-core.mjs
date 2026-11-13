/**
 * Create Stripe Checkout Session for allowlisted courses only.
 */

import Stripe from "stripe";
import {
  getStripeCourse,
  resolveIntake,
  resolveMode,
  formatRmFromSen,
} from "./stripe-courses.mjs";
import { corsHeaders, jsonResponse, siteBaseUrl } from "./stripe-http.mjs";

function clean(s, max) {
  return String(s || "")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, max || 200);
}

function isEmail(v) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(v || "").trim());
}

export async function stripeCheckoutHandler(event) {
  const method = String(event.httpMethod || event.method || "GET").toUpperCase();
  const origin = (event.headers && (event.headers.origin || event.headers.Origin)) || "";

  if (method === "OPTIONS") {
    return { statusCode: 204, headers: corsHeaders(origin), body: "" };
  }
  if (method !== "POST") {
    return jsonResponse(405, { ok: false, error: "method_not_allowed" });
  }

  const secret = String(process.env.STRIPE_SECRET_KEY || "").trim();
  if (!secret) {
    return jsonResponse(503, {
      ok: false,
      error: "stripe_not_configured",
      message: "Payment option is currently unavailable.",
    });
  }

  let body = {};
  try {
    body =
      typeof event.body === "string"
        ? JSON.parse(event.body || "{}")
        : event.body || {};
  } catch {
    return jsonResponse(400, { ok: false, error: "invalid_json" });
  }

  const courseSlug = clean(body.courseSlug || body.slug, 120);
  const course = getStripeCourse(courseSlug);
  if (!course) {
    return jsonResponse(400, { ok: false, error: "course_not_enrollable" });
  }

  const intake = resolveIntake(course, body.intakeId || body.intake);
  if (!intake) {
    return jsonResponse(400, { ok: false, error: "invalid_intake" });
  }

  const trainingMode = resolveMode(course, body.trainingMode || body.mode);
  if (!trainingMode) {
    return jsonResponse(400, { ok: false, error: "invalid_training_mode" });
  }

  const firstName = clean(body.firstName, 80);
  const lastName = clean(body.lastName, 80);
  const email = clean(body.email, 120).toLowerCase();
  const phone = clean(body.phone, 40);
  const participantName = clean(`${firstName} ${lastName}`, 160);

  if (!firstName || !lastName) {
    return jsonResponse(400, { ok: false, error: "name_required" });
  }
  if (!isEmail(email)) {
    return jsonResponse(400, { ok: false, error: "email_invalid" });
  }
  if (!phone || phone.length < 8) {
    return jsonResponse(400, { ok: false, error: "phone_required" });
  }

  const base = siteBaseUrl(event);
  const returnMode = String(body.returnMode || body.ui || "").trim().toLowerCase();
  const usePopupReturn = returnMode === "popup" || returnMode === "window";
  // Popup return pages postMessage to the course tab and close; full-page uses completed/cancelled.
  // Do not add matching 200 rewrites for enrollment paths in Cloudflare _redirects.
  const successUrl = usePopupReturn
    ? `${base}/enrollment/popup-done?result=success&session_id={CHECKOUT_SESSION_ID}&course=${encodeURIComponent(course.slug)}`
    : `${base}/enrollment/completed?session_id={CHECKOUT_SESSION_ID}`;
  const cancelUrl = usePopupReturn
    ? `${base}/enrollment/popup-done?result=cancel&course=${encodeURIComponent(course.slug)}`
    : `${base}/enrollment/cancelled?course=${encodeURIComponent(course.slug)}`;

  const stripe = new Stripe(secret);

  try {
    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      customer_email: email,
      client_reference_id: `${course.slug}:${intake.id}`,
      line_items: [
        {
          quantity: 1,
          price_data: {
            currency: course.currency,
            unit_amount: course.amountSen,
            product_data: {
              name: course.name,
              description: `${intake.label} · ${trainingMode}`,
            },
          },
        },
      ],
      success_url: successUrl,
      cancel_url: cancelUrl,
      metadata: {
        course_slug: course.slug,
        course_name: course.name,
        intake_id: intake.id,
        intake_label: intake.label,
        training_mode: trainingMode,
        first_name: firstName,
        last_name: lastName,
        participant_name: participantName,
        email,
        phone,
        amount_sen: String(course.amountSen),
        amount_label: formatRmFromSen(course.amountSen),
      },
      payment_intent_data: {
        metadata: {
          course_slug: course.slug,
          intake_id: intake.id,
          email,
        },
      },
    });

    return jsonResponse(200, {
      ok: true,
      id: session.id,
      url: session.url,
    });
  } catch (err) {
    console.error("stripe_checkout_error", err && err.message);
    return jsonResponse(500, {
      ok: false,
      error: "checkout_failed",
      message: "Payment option is currently unavailable.",
    });
  }
}
