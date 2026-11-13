/**
 * After a paid Checkout Session: send confirmation email (+ PDF) and log to the
 * "Paid Enrollments" tab (same Google Spreadsheet as Enquiries — not the Enquiries tab).
 *
 * Idempotent under concurrent callers (webhook + popup poll + success page):
 * claim email_sent / sheet_logged as "pending" in Stripe metadata BEFORE side effects.
 */

import Stripe from "stripe";
import { sendEnrollmentConfirmation } from "./enrollment-email.mjs";
import { getStripeCourse } from "./stripe-courses.mjs";

function env(name, fallback = "") {
  return String(process.env[name] || fallback).trim();
}

function normalizeAppsScriptUrl(url) {
  const u = String(url || "").trim();
  if (!u) return "";
  try {
    const parsed = new URL(u);
    if (!parsed.hostname.includes("script.google.com")) return "";
    return parsed.toString();
  } catch {
    return "";
  }
}

function claimToken() {
  return `p${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
}

/**
 * Compare-and-set style claim on Checkout Session metadata.
 * Returns claimed:true only for the winner of the race.
 */
async function claimSessionFlag(stripe, sessionId, flagKey) {
  const tokKey = `${flagKey}_tok`;
  const session = await stripe.checkout.sessions.retrieve(sessionId);
  const md = { ...(session.metadata || {}) };
  const cur = String(md[flagKey] || "");
  if (cur === "1" || cur === "pending") {
    return { claimed: false, alreadyDone: cur === "1", session, md };
  }

  const token = claimToken();
  md[flagKey] = "pending";
  md[tokKey] = token;
  await stripe.checkout.sessions.update(sessionId, { metadata: md });

  const fresh = await stripe.checkout.sessions.retrieve(sessionId);
  const fmd = { ...(fresh.metadata || {}) };
  if (String(fmd[tokKey] || "") !== token) {
    return { claimed: false, alreadyDone: String(fmd[flagKey] || "") === "1", session: fresh, md: fmd };
  }
  return { claimed: true, alreadyDone: false, session: fresh, md: fmd, token };
}

async function finalizeSessionFlag(stripe, sessionId, flagKey, ok) {
  try {
    const session = await stripe.checkout.sessions.retrieve(sessionId);
    const md = { ...(session.metadata || {}) };
    const tokKey = `${flagKey}_tok`;
    if (ok) {
      md[flagKey] = "1";
    } else if (String(md[flagKey] || "") === "pending") {
      // Allow a later retry if this attempt failed.
      md[flagKey] = "";
    }
    md[tokKey] = "";
    await stripe.checkout.sessions.update(sessionId, { metadata: md });
  } catch (err) {
    console.warn("stripe_metadata_finalize", flagKey, err && err.message);
  }
}

async function postToAppsScript(webAppUrl, payload) {
  const base = normalizeAppsScriptUrl(webAppUrl);
  if (!base) return { skipped: true };

  const jsonStr = JSON.stringify(payload);
  const formBody = new URLSearchParams();
  formBody.set("payload", jsonStr);

  const res = await fetch(base, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
      Accept: "application/json, text/plain, */*",
    },
    body: formBody.toString(),
    redirect: "follow",
  });
  const text = await res.text();
  let json = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    json = null;
  }
  if (res.ok && json && json.ok === true) {
    return { skipped: false, ok: true, row: json.row || null, duplicate: !!json.duplicate };
  }

  const res2 = await fetch(base, {
    method: "POST",
    headers: {
      "Content-Type": "application/json;charset=UTF-8",
      Accept: "application/json, text/plain, */*",
    },
    body: jsonStr,
    redirect: "follow",
  });
  const text2 = await res2.text();
  let json2 = null;
  try {
    json2 = text2 ? JSON.parse(text2) : null;
  } catch {
    json2 = null;
  }
  if (res2.ok && json2 && json2.ok === true) {
    return { skipped: false, ok: true, row: json2.row || null, duplicate: !!json2.duplicate };
  }
  throw new Error(
    String((json2 && json2.error) || (json && json.error) || text2 || text || "sheet_failed").slice(
      0,
      220
    )
  );
}

function sheetPayloadFromSession(session) {
  const md = (session && session.metadata) || {};
  const first = String(md.first_name || "").trim();
  const last = String(md.last_name || "").trim();
  const email = String(
    md.email || session.customer_details?.email || session.customer_email || ""
  )
    .trim()
    .toLowerCase();
  const courseSlug = String(md.course_slug || "").trim();
  const course = getStripeCourse(courseSlug);
  const pagePath = (course && course.pagePath) || (courseSlug ? `/courses/${courseSlug}` : "");
  const amountLabel = String(md.amount_label || "").trim();
  const secret = env("APPS_SCRIPT_ENQUIRY_SECRET") || env("BREVO_ENQUIRY_SECRET");
  const receiptNumber = String(session.payment_intent || session.id || "").trim();

  const payload = {
    targetSheet: "Paid Enrollments",
    recordType: "paid_enrollment",
    first: first || "Paid",
    last: last || "Enrollment",
    email,
    phone: String(md.phone || "").trim(),
    course: String(md.course_name || courseSlug || "Course").trim(),
    intakeLabel: String(md.intake_label || md.intake_id || "").trim(),
    trainingMode: String(md.training_mode || "").trim(),
    amountLabel,
    paymentStatus: String(session.payment_status || "paid").trim(),
    stripeSessionId: String(session.id || "").trim(),
    receiptNumber,
    type: "Paid Enrollment",
    source: "stripe-checkout",
    pageUrl: pagePath ? `https://www.nexpertsacademy.com${pagePath}` : "",
    userAgent: "stripe-fulfill",
    submittedAt: new Date().toISOString(),
    curriculumPage: pagePath ? pagePath.replace(/^\//, "") : "",
  };
  if (secret) payload.secret = secret;
  return payload;
}

/**
 * Send email + sheet log once for a paid session. Safe under concurrent callers.
 */
export async function fulfillPaidEnrollment(session, stripe) {
  if (!session || !session.id) {
    return { ok: false, error: "no_session" };
  }
  if (String(session.payment_status || "") === "unpaid") {
    return { ok: false, error: "not_paid" };
  }
  if (!stripe) {
    return { ok: false, error: "stripe_client_required" };
  }

  const sessionId = session.id;
  const result = {
    ok: true,
    sessionId,
    emailed: false,
    sheetLogged: false,
    emailSkipped: false,
    sheetSkipped: false,
  };

  // --- Email (claim before send) ---
  const emailClaim = await claimSessionFlag(stripe, sessionId, "email_sent");
  if (emailClaim.alreadyDone) {
    result.emailed = true;
    result.emailSkipped = true;
  } else if (!emailClaim.claimed) {
    result.emailed = false;
    result.emailSkipped = true;
  } else {
    try {
      await sendEnrollmentConfirmation({ session: emailClaim.session || session });
      await finalizeSessionFlag(stripe, sessionId, "email_sent", true);
      result.emailed = true;
    } catch (err) {
      await finalizeSessionFlag(stripe, sessionId, "email_sent", false);
      throw err;
    }
  }

  // --- Sheet (claim before write) ---
  const sheetClaim = await claimSessionFlag(stripe, sessionId, "sheet_logged");
  if (sheetClaim.alreadyDone) {
    result.sheetLogged = true;
    result.sheetSkipped = true;
  } else if (!sheetClaim.claimed) {
    result.sheetLogged = false;
    result.sheetSkipped = true;
  } else {
    const appsUrl = env("APPS_SCRIPT_ENQUIRY_URL");
    if (!appsUrl) {
      await finalizeSessionFlag(stripe, sessionId, "sheet_logged", false);
      result.sheetLogged = false;
      result.sheetSkipped = true;
    } else {
      try {
        const sheetRes = await postToAppsScript(
          appsUrl,
          sheetPayloadFromSession(sheetClaim.session || session)
        );
        await finalizeSessionFlag(stripe, sessionId, "sheet_logged", true);
        result.sheetLogged = !sheetRes.skipped;
        if (sheetRes.row) result.sheetRow = sheetRes.row;
        if (sheetRes.duplicate) result.sheetDuplicate = true;
      } catch (err) {
        await finalizeSessionFlag(stripe, sessionId, "sheet_logged", false);
        console.warn("enrollment_sheet_failed", err && err.message);
        result.sheetError = String((err && err.message) || err).slice(0, 180);
      }
    }
  }

  return result;
}

function normalizeSessionId(sessionId) {
  const id = String(sessionId || "").trim();
  if (!id || !/^cs_[a-zA-Z0-9_]+$/.test(id)) return "";
  return id;
}

/**
 * Read-only session status for the waiting modal (no email/sheet side effects).
 */
export async function getCheckoutSessionStatus(sessionId) {
  const secret = env("STRIPE_SECRET_KEY");
  if (!secret) return { ok: false, error: "stripe_not_configured" };
  const id = normalizeSessionId(sessionId);
  if (!id) return { ok: false, error: "invalid_session" };
  const stripe = new Stripe(secret);
  const session = await stripe.checkout.sessions.retrieve(id);
  const md = (session && session.metadata) || {};
  const emailFlag = String(md.email_sent || "");
  const sheetFlag = String(md.sheet_logged || "");
  return {
    ok: true,
    sessionId: session.id,
    status: session.status,
    payment_status: session.payment_status,
    email_sent: emailFlag === "1",
    sheet_logged: sheetFlag === "1",
    email_pending: emailFlag === "pending",
    sheet_pending: sheetFlag === "pending",
    course_slug: md.course_slug || "",
  };
}

/**
 * Load session by id and fulfill (used by success-page API).
 */
export async function fulfillCheckoutSessionById(sessionId) {
  const secret = env("STRIPE_SECRET_KEY");
  if (!secret) return { ok: false, error: "stripe_not_configured" };
  const id = normalizeSessionId(sessionId);
  if (!id) return { ok: false, error: "invalid_session" };
  const stripe = new Stripe(secret);
  const session = await stripe.checkout.sessions.retrieve(id);
  return fulfillPaidEnrollment(session, stripe);
}
