/**
 * Allocate / resolve professional receipt numbers:
 *   Invoice (Receipt No.): NXA-RCP-YYYY-000123
 *   Order Ref.:            NXA-ORD-YYYY-000123
 *
 * Preferred source: Google Apps Script (atomic Script Properties + Receipt Index).
 * Fallback: deterministic sequence from payment intent / session id (last resort).
 */

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

function pad6(n) {
  const s = String(Math.max(0, Number(n) || 0));
  return s.length >= 6 ? s.slice(-6) : ("000000" + s).slice(-6);
}

function formatPair(year, seq) {
  const y = String(year || new Date().getUTCFullYear());
  const s = pad6(seq);
  return {
    invoiceNo: `NXA-RCP-${y}-${s}`,
    orderRef: `NXA-ORD-${y}-${s}`,
    year: y,
    seq: Number(seq) || 0,
  };
}

/** Stable fallback when Apps Script is unavailable — not ideal, but unique per payment. */
function fallbackFromPayment(sessionId, paymentIntentId) {
  const year = new Date().getUTCFullYear();
  const seed = String(paymentIntentId || sessionId || "")
    .replace(/[^a-zA-Z0-9]/g, "")
    .slice(-8);
  let n = 0;
  for (let i = 0; i < seed.length; i++) n = (n * 33 + seed.charCodeAt(i)) % 1000000;
  if (n < 1) n = 1;
  return { ...formatPair(year, n), source: "fallback" };
}

async function postAllocate(webAppUrl, payload) {
  const base = normalizeAppsScriptUrl(webAppUrl);
  if (!base) return null;
  const jsonStr = JSON.stringify(payload);
  const formBody = new URLSearchParams();
  formBody.set("payload", jsonStr);

  const tryOnce = async (body, contentType) => {
    const res = await fetch(base, {
      method: "POST",
      headers: {
        "Content-Type": contentType,
        Accept: "application/json, text/plain, */*",
      },
      body,
      redirect: "follow",
    });
    const text = await res.text();
    let json = null;
    try {
      json = text ? JSON.parse(text) : null;
    } catch {
      json = null;
    }
    return { res, json, text };
  };

  let r = await tryOnce(formBody.toString(), "application/x-www-form-urlencoded;charset=UTF-8");
  if (!(r.res.ok && r.json && r.json.ok)) {
    r = await tryOnce(jsonStr, "application/json;charset=UTF-8");
  }
  if (r.res.ok && r.json && r.json.ok && r.json.invoiceNo && r.json.orderRef) {
    return {
      invoiceNo: String(r.json.invoiceNo),
      orderRef: String(r.json.orderRef),
      year: r.json.year,
      seq: r.json.seq,
      source: "apps_script",
      reused: !!r.json.reused,
    };
  }
  return null;
}

/**
 * Resolve numbers already stored on the Checkout Session, else allocate.
 * Persists onto session metadata when a Stripe client is provided.
 */
export async function resolveReceiptNumbers({ session, stripe } = {}) {
  const md = (session && session.metadata) || {};
  const existingInvoice = String(md.invoice_no || md.receipt_no || "").trim();
  const existingOrder = String(md.order_ref || "").trim();
  if (existingInvoice && existingOrder) {
    return {
      invoiceNo: existingInvoice,
      orderRef: existingOrder,
      source: "metadata",
      reused: true,
    };
  }

  const sessionId = String((session && session.id) || "").trim();
  const paymentIntentId = String(
    (session && session.payment_intent) || md.payment_intent || ""
  ).trim();
  const secret = env("APPS_SCRIPT_ENQUIRY_SECRET") || env("BREVO_ENQUIRY_SECRET");
  const appsUrl = env("APPS_SCRIPT_ENQUIRY_URL");

  let nums = null;
  if (appsUrl) {
    try {
      const payload = {
        action: "allocate_receipt",
        stripeSessionId: sessionId,
        paymentIntent: paymentIntentId,
      };
      if (secret) payload.secret = secret;
      nums = await postAllocate(appsUrl, payload);
    } catch (err) {
      console.warn("receipt_allocate_failed", err && err.message);
    }
  }

  if (!nums) {
    nums = fallbackFromPayment(sessionId, paymentIntentId);
  }

  if (stripe && sessionId) {
    try {
      const fresh = await stripe.checkout.sessions.retrieve(sessionId);
      const nextMd = { ...(fresh.metadata || {}) };
      nextMd.invoice_no = nums.invoiceNo;
      nextMd.order_ref = nums.orderRef;
      await stripe.checkout.sessions.update(sessionId, { metadata: nextMd });
    } catch (err) {
      console.warn("receipt_metadata_persist", err && err.message);
    }
  }

  return nums;
}
