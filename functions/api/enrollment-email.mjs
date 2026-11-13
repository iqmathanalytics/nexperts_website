/**
 * Post-payment confirmation email (Brevo) + PDF receipt (pdf-lib).
 */

import { PDFDocument, StandardFonts, rgb } from "pdf-lib";
import { formatRmFromSen } from "./stripe-courses.mjs";

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
    if (Number.isNaN(d.getTime())) return new Date().toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
    return d.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
  } catch {
    return "";
  }
}

export async function buildReceiptPdf(meta) {
  const doc = await PDFDocument.create();
  const page = doc.addPage([595.28, 841.89]); // A4
  const font = await doc.embedFont(StandardFonts.Helvetica);
  const bold = await doc.embedFont(StandardFonts.HelveticaBold);
  const margin = 48;
  let y = 780;

  const draw = (text, size, f, color) => {
    page.drawText(String(text || ""), {
      x: margin,
      y,
      size,
      font: f || font,
      color: color || rgb(0.1, 0.1, 0.12),
    });
    y -= size + 10;
  };

  draw("Nexperts Academy", 18, bold, rgb(0.05, 0.35, 0.55));
  draw("Payment Receipt", 14, bold);
  y -= 8;

  const lines = [
    ["Receipt Number", meta.receiptNumber],
    ["Payment Date", meta.paymentDate],
    ["Participant Name", meta.participantName],
    ["Email", meta.email],
    ["Phone", meta.phone || "—"],
    ["Course", meta.courseName],
    ["Intake", meta.intakeLabel],
    ["Training Mode", meta.trainingMode],
    ["Amount Paid", meta.amountLabel],
    ["Payment Method", meta.paymentMethod || "Card (Stripe)"],
    ["Status", "Paid"],
  ];

  for (const [label, value] of lines) {
    page.drawText(`${label}:`, { x: margin, y, size: 10, font: bold, color: rgb(0.25, 0.25, 0.28) });
    page.drawText(String(value || "—"), { x: margin + 140, y, size: 10, font, color: rgb(0.1, 0.1, 0.12), maxWidth: 360 });
    y -= 22;
  }

  y -= 20;
  draw("Thank you for enrolling with Nexperts Academy.", 10, font, rgb(0.35, 0.35, 0.38));
  draw("www.nexpertsacademy.com", 9, font, rgb(0.05, 0.35, 0.55));

  const bytes = await doc.save();
  if (typeof Buffer !== "undefined") {
    return Buffer.from(bytes).toString("base64");
  }
  let binary = "";
  const arr = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  for (let i = 0; i < arr.length; i++) binary += String.fromCharCode(arr[i]);
  return btoa(binary);
}

function buildHtmlEmail(meta) {
  const name = escapeHtml(meta.participantName);
  const course = escapeHtml(meta.courseName);
  const intake = escapeHtml(meta.intakeLabel);
  const mode = escapeHtml(meta.trainingMode);
  const amount = escapeHtml(meta.amountLabel);
  const receipt = escapeHtml(meta.receiptNumber);
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
        <tr><td style="background:#0a4d68;padding:24px 28px;">
          <div style="color:#fff;font-size:20px;font-weight:700;">Nexperts Academy</div>
          <div style="color:#c8e6f0;font-size:13px;margin-top:4px;">Enrollment Confirmation</div>
        </td></tr>
        <tr><td style="padding:28px;">
          <p style="margin:0 0 16px;font-size:16px;">Hi ${name},</p>
          <p style="margin:0 0 16px;font-size:15px;line-height:1.55;">
            Thank you for enrolling with <strong>Nexperts Academy</strong>. Your payment was successful and your seat is confirmed.
          </p>
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f0f7fa;border-radius:6px;margin:20px 0;">
            <tr><td style="padding:16px 18px;font-size:14px;line-height:1.7;">
              <strong>Course:</strong> ${course}<br>
              <strong>Intake:</strong> ${intake}<br>
              <strong>Training Mode:</strong> ${mode}<br>
              <strong>Amount Paid:</strong> ${amount}<br>
              <strong>Receipt Number:</strong> ${receipt}<br>
              <strong>Payment Date:</strong> ${date}<br>
              <strong>Email:</strong> ${email}<br>
              <strong>Phone:</strong> ${phone}
            </td></tr>
          </table>
          <p style="margin:0 0 12px;font-size:14px;line-height:1.55;">
            Your payment receipt is attached as a PDF. Please keep it for your records.
          </p>
          <p style="margin:0 0 12px;font-size:14px;line-height:1.55;">
            Our team will contact you shortly with joining instructions and course materials.
          </p>
          <p style="margin:24px 0 0;font-size:14px;">
            Regards,<br>
            <strong>Nexperts Academy</strong><br>
            <a href="https://www.nexpertsacademy.com" style="color:#0a4d68;">www.nexpertsacademy.com</a>
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
    `Receipt Number: ${meta.receiptNumber}`,
    `Payment Date: ${meta.paymentDate}`,
    `Email: ${meta.email}`,
    `Phone: ${meta.phone || "—"}`,
    "",
    "Your payment receipt is attached as a PDF.",
    "Our team will contact you shortly with joining instructions.",
    "",
    "Regards,",
    "Nexperts Academy",
    "www.nexpertsacademy.com",
  ].join("\n");
}

/**
 * @param {object} opts
 * @param {object} opts.session - Stripe Checkout Session (expanded or with metadata)
 */
export async function sendEnrollmentConfirmation({ session }) {
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

  const receiptNumber =
    String(session.payment_intent || session.id || "").trim() || session.id;

  const meta = {
    participantName: String(md.participant_name || session.customer_details?.name || "Participant").trim(),
    email: String(md.email || session.customer_details?.email || session.customer_email || "").trim(),
    phone: String(md.phone || "").trim(),
    courseName: String(md.course_name || "Course").trim(),
    intakeLabel: String(md.intake_label || md.intake_id || "").trim(),
    trainingMode: String(md.training_mode || "").trim(),
    amountLabel,
    receiptNumber,
    paymentDate: paymentDateLabel(
      session.created ? session.created * 1000 : Date.now()
    ),
    paymentMethod: "Card (Stripe)",
  };

  if (!meta.email) throw new Error("missing_participant_email");

  const pdfBase64 = await buildReceiptPdf(meta);
  const filename = `Payment Receipt – ${receiptNumber}.pdf`;

  const toPayload = {
    sender: { name: senderName, email: senderEmail },
    to: [{ email: meta.email, name: meta.participantName }],
    bcc: notifyTo && notifyTo.toLowerCase() !== meta.email.toLowerCase()
      ? [{ email: notifyTo, name: "Nexperts Academy" }]
      : undefined,
    subject: `Enrollment Confirmed – ${meta.courseName}`,
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
  return { ok: true, receiptNumber, email: meta.email };
}
