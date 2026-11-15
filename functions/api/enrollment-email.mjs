/**
 * Post-payment confirmation email (Brevo) + official PDF receipt.
 */

import { formatRmFromSen } from "./stripe-courses.mjs";
import { buildOfficialReceiptPdf } from "./receipt-pdf.mjs";
import { resolveReceiptNumbers } from "./receipt-numbers.mjs";

const BREVO_URL = "https://api.brevo.com/v3/smtp/email";

function env(name, fallback = "") {
  return String(process.env[name] || fallback).trim();
}

async function brevoSend(apiKey, body) {
  const res = await fetch(BREVO_URL, {
    method: "POST",
    headers: {
      accept: "application/json",
      "content-type": "application/json",
      "api-key": apiKey,
    },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  let json = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    json = { message: text };
  }
  if (!res.ok) {
    const msg = json?.message || json?.error || res.statusText || "brevo_error";
    throw new Error(String(msg).slice(0, 200));
  }
  return json;
}

function escapeHtml(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function paymentDateLabel(isoOrMs) {
  try {
    const d = isoOrMs ? new Date(isoOrMs) : new Date();
    if (Number.isNaN(d.getTime())) {
      return new Date().toLocaleDateString("en-GB", {
        day: "numeric",
        month: "short",
        year: "numeric",
      });
    }
    return d.toLocaleDateString("en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  } catch {
    return "";
  }
}

function paidOnLabel(isoOrMs) {
  try {
    const d = isoOrMs ? new Date(isoOrMs) : new Date();
    if (Number.isNaN(d.getTime())) return paymentDateLabel(isoOrMs);
    const date = d.toLocaleDateString("en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
    const time = d.toLocaleTimeString("en-GB", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
    return `${date}, ${time}`;
  } catch {
    return paymentDateLabel(isoOrMs);
  }
}

function parseAmountMyr(amountLabel, amountTotalSen) {
  if (Number.isFinite(Number(amountTotalSen))) return Number(amountTotalSen) / 100;
  const m = String(amountLabel || "").replace(/,/g, "").match(/(\d+(?:\.\d+)?)/);
  return m ? Number(m[1]) : 0;
}

async function resolveCardMethod(stripe, session) {
  try {
    const piRef = session && session.payment_intent;
    if (!stripe || !piRef) return "Card (Stripe)";
    const piId = typeof piRef === "string" ? piRef : piRef.id;
    if (!piId) return "Card (Stripe)";
    const pi = await stripe.paymentIntents.retrieve(piId, {
      expand: ["payment_method"],
    });
    const card =
      (pi.payment_method && pi.payment_method.card) ||
      (pi.charges &&
        pi.charges.data &&
        pi.charges.data[0] &&
        pi.charges.data[0].payment_method_details &&
        pi.charges.data[0].payment_method_details.card);
    if (card && card.brand && card.last4) {
      const brand = String(card.brand).replace(/^\w/, (c) => c.toUpperCase());
      return `${brand} ending ${card.last4}`;
    }
  } catch (_) {
    /* ignore */
  }
  return "Card (Stripe)";
}

/** @deprecated use buildOfficialReceiptPdf — kept as alias for older imports */
export async function buildReceiptPdf(meta) {
  return buildOfficialReceiptPdf(meta);
}

function buildHtmlEmail(meta) {
  const name = escapeHtml(meta.participantName);
  const course = escapeHtml(meta.courseName);
  const intake = escapeHtml(meta.intakeLabel);
  const mode = escapeHtml(meta.trainingMode);
  const amount = escapeHtml(meta.amountLabel);
  const invoice = escapeHtml(meta.invoiceNo || meta.receiptNumber);
  const orderRef = escapeHtml(meta.orderRef || "—");
  const date = escapeHtml(meta.paymentDate);
  const email = escapeHtml(meta.email);
  const phone = escapeHtml(meta.phone || "—");

  return `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Enrollment Confirmation</title></head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:Arial,Helvetica,sans-serif;color:#1a1a1a;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f4f6f8;padding:24px 12px;">
    <tr><td align="center">
      <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background:#ffffff;border-radius:8px;overflow:hidden;max-width:600px;">
        <tr><td style="background:#7a1f1f;padding:24px 28px;">
          <div style="color:#fff;font-size:20px;font-weight:700;">Nexperts Academy</div>
          <div style="color:#f0d0d0;font-size:13px;margin-top:4px;">Official Payment Receipt</div>
        </td></tr>
        <tr><td style="padding:28px;">
          <p style="margin:0 0 16px;font-size:16px;">Hi ${name},</p>
          <p style="margin:0 0 16px;font-size:15px;line-height:1.55;">
            Thank you for enrolling with <strong>Nexperts Academy</strong>. Your payment was successful and your seat is confirmed.
          </p>
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f8f1f1;border-radius:6px;margin:20px 0;">
            <tr><td style="padding:16px 18px;font-size:14px;line-height:1.7;">
              <strong>Course:</strong> ${course}<br>
              <strong>Intake:</strong> ${intake}<br>
              <strong>Training Mode:</strong> ${mode}<br>
              <strong>Amount Paid:</strong> ${amount}<br>
              <strong>Receipt No.:</strong> ${invoice}<br>
              <strong>Order Ref.:</strong> ${orderRef}<br>
              <strong>Payment Date:</strong> ${date}<br>
              <strong>Email:</strong> ${email}<br>
              <strong>Phone:</strong> ${phone}
            </td></tr>
          </table>
          <p style="margin:0 0 12px;font-size:14px;line-height:1.55;">
            Your official payment receipt is attached as a PDF. Please keep it for your records.
          </p>
          <p style="margin:0 0 12px;font-size:14px;line-height:1.55;">
            Our team will contact you shortly with joining instructions and course materials.
          </p>
          <p style="margin:24px 0 0;font-size:14px;">
            Regards,<br>
            <strong>Nexperts Academy</strong><br>
            <a href="https://www.nexpertsacademy.com" style="color:#7a1f1f;">www.nexpertsacademy.com</a>
          </p>
        </td></tr>
        <tr><td style="padding:14px 28px;background:#eef2f5;font-size:12px;color:#667;">
          This is an automated confirmation for a paid enrollment.
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>`;
}

function buildTextEmail(meta) {
  return [
    `Hi ${meta.participantName},`,
    "",
    "Thank you for enrolling with Nexperts Academy. Your payment was successful and your seat is confirmed.",
    "",
    `Course: ${meta.courseName}`,
    `Intake: ${meta.intakeLabel}`,
    `Training Mode: ${meta.trainingMode}`,
    `Amount Paid: ${meta.amountLabel}`,
    `Receipt No.: ${meta.invoiceNo || meta.receiptNumber}`,
    `Order Ref.: ${meta.orderRef || "—"}`,
    `Payment Date: ${meta.paymentDate}`,
    `Email: ${meta.email}`,
    `Phone: ${meta.phone || "—"}`,
    "",
    "Your official payment receipt is attached as a PDF.",
    "Our team will contact you shortly with joining instructions.",
    "",
    "Regards,",
    "Nexperts Academy",
    "www.nexpertsacademy.com",
  ].join("\n");
}

/**
 * @param {object} opts
 * @param {object} opts.session - Stripe Checkout Session
 * @param {object} [opts.stripe] - Stripe client (for card details + metadata persist)
 * @param {object} [opts.numbers] - pre-allocated { invoiceNo, orderRef }
 */
export async function sendEnrollmentConfirmation({ session, stripe, numbers } = {}) {
  const apiKey = env("BREVO_API_KEY");
  if (!apiKey) throw new Error("BREVO_API_KEY missing");

  const senderEmail = env("BREVO_SENDER_EMAIL", "enquiry@nexpertsacademy.com");
  const senderName = env("BREVO_SENDER_NAME", "Nexperts Academy");
  const notifyTo =
    env("BREVO_INTERNAL_TO") ||
    env("BREVO_NOTIFY_TO") ||
    env("BREVO_ENQUIRY_TO") ||
    "enquiry@nexpertsacademy.com";

  const md = (session && session.metadata) || {};
  const amountTotal = Number(session.amount_total);
  const amountLabel =
    md.amount_label ||
    (Number.isFinite(amountTotal) ? formatRmFromSen(amountTotal) : "—");
  const amountNumeric = parseAmountMyr(amountLabel, amountTotal);

  const nums =
    numbers && numbers.invoiceNo && numbers.orderRef
      ? numbers
      : await resolveReceiptNumbers({ session, stripe });

  const transactionId = String(session.payment_intent || session.id || "").trim();
  const createdMs = session.created ? session.created * 1000 : Date.now();
  const paymentMethod = await resolveCardMethod(stripe, session);

  const meta = {
    participantName: String(
      md.participant_name || session.customer_details?.name || "Participant"
    ).trim(),
    email: String(
      md.email || session.customer_details?.email || session.customer_email || ""
    ).trim(),
    phone: String(md.phone || "").trim(),
    courseName: String(md.course_name || "Course").trim(),
    intakeLabel: String(md.intake_label || md.intake_id || "").trim(),
    trainingMode: String(md.training_mode || "").trim(),
    durationNote: String(md.intake_label || "").trim(),
    amountLabel,
    amountNumeric,
    currency: String(session.currency || "myr").toUpperCase(),
    invoiceNo: nums.invoiceNo,
    orderRef: nums.orderRef,
    receiptNumber: nums.invoiceNo,
    transactionId,
    paymentDate: paymentDateLabel(createdMs),
    paidOn: paidOnLabel(createdMs),
    paymentMethod,
    processor: "Stripe",
  };

  if (!meta.email) throw new Error("missing_participant_email");

  const pdfBase64 = await buildOfficialReceiptPdf(meta);
  const safeName = String(nums.invoiceNo || "receipt").replace(/[^\w.-]+/g, "_");
  const filename = `Nexperts-Receipt-${safeName}.pdf`;

  const toPayload = {
    sender: { name: senderName, email: senderEmail },
    to: [{ email: meta.email, name: meta.participantName }],
    bcc:
      notifyTo && notifyTo.toLowerCase() !== meta.email.toLowerCase()
        ? [{ email: notifyTo, name: "Nexperts Academy" }]
        : undefined,
    subject: `Enrollment Confirmed – ${meta.courseName} (${nums.invoiceNo})`,
    htmlContent: buildHtmlEmail(meta),
    textContent: buildTextEmail(meta),
    attachment: [
      {
        name: filename,
        content: pdfBase64,
      },
    ],
  };

  if (!toPayload.bcc) delete toPayload.bcc;

  await brevoSend(apiKey, toPayload);
  return {
    ok: true,
    receiptNumber: nums.invoiceNo,
    invoiceNo: nums.invoiceNo,
    orderRef: nums.orderRef,
    email: meta.email,
  };
}
