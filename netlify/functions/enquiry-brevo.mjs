/**
 * Netlify Function: website enquiry → Brevo Transactional Email API.
 */

const BREVO_URL = "https://api.brevo.com/v3/smtp/email";

const DEFAULT_SHEET_URL =
  "https://docs.google.com/spreadsheets/d/1vuZbvwAkuwIFU1F-CLjz8xMOKRXpJp0vqKCGbiZt0PE/edit?usp=sharing";

function corsHeaders() {
  const allow = String(process.env.BREVO_ALLOWED_ORIGINS || "*").trim() || "*";
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Content-Type": "application/json; charset=utf-8",
  };
}

function escapeHtml(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function dash(v) {
  const s = String(v ?? "").trim();
  return s ? s : "—";
}

const INTERNAL_INBOX_ENV_KEYS = [
  "BREVO_INTERNAL_TO",
  "BREVO_ENQUIRY_TO",
  "NEXPERTS_ENQUIRY_EMAIL",
  "ENQUIRY_EMAIL",
];

const FALLBACK_INTERNAL_INBOX = "enquiry@nexpertsacademy.com";

/** First non-empty env among common names (avoids typos / wrong var on Netlify). */
function resolveInternalInboxRaw(env) {
  const e = env || process.env || {};
  for (const k of INTERNAL_INBOX_ENV_KEYS) {
    const v = String(e[k] || "").trim();
    if (v) return v;
  }
  return "";
}

function isLikelyEmail(s) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(s || "").trim());
}

/** Brevo `to` list: supports comma/semicolon-separated addresses in env. */
function internalRecipientsList(env) {
  const raw = resolveInternalInboxRaw(env);
  if (!raw) {
    return [{ email: FALLBACK_INTERNAL_INBOX, name: "Nexperts Enquiries" }];
  }
  const parts = raw
    .split(/[,;]+/)
    .map((x) => x.trim())
    .filter(isLikelyEmail);
  if (!parts.length) {
    return [{ email: FALLBACK_INTERNAL_INBOX, name: "Nexperts Enquiries" }];
  }
  return parts.map((email) => ({ email, name: "Nexperts Enquiries" }));
}

function primaryInternalInbox(env) {
  return internalRecipientsList(env)[0].email;
}

function getCtx(data, env) {
  const site = String(env.NEXPERTS_PUBLIC_SITE_URL || "https://www.nexpertsacademy.com").replace(/\/$/, "");
  const sheet = String(env.NEXPERTS_LEADS_SHEET_URL || DEFAULT_SHEET_URL).trim();
  const internal = primaryInternalInbox(env);
  const first = String(data.first || "").trim();
  const last = String(data.last || "").trim();
  const fullName = `${first} ${last}`.trim() || "there";
  return { site, sheet, internal, first, last, fullName };
}

/** Table row: label | value (email-safe layout) */
function trRow(label, value) {
  const v = escapeHtml(dash(value));
  return `<tr>
  <td style="padding:12px 16px;border-bottom:1px solid #e2e8f0;font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#64748b;width:34%;vertical-align:top;font-weight:600;">${escapeHtml(label)}</td>
  <td style="padding:12px 16px;border-bottom:1px solid #e2e8f0;font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#0f172a;vertical-align:top;">${v.replace(/\n/g, "<br/>")}</td>
</tr>`;
}

function ctaButton(href, label, bg = "#1d4ed8") {
  const u = escapeHtml(href);
  const t = escapeHtml(label);
  return `<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:0 8px 12px 0;display:inline-table;">
  <tr><td style="border-radius:10px;background:${bg};">
    <a href="${u}" target="_blank" rel="noopener" style="display:inline-block;padding:14px 22px;font-family:Arial,Helvetica,sans-serif;font-size:14px;font-weight:700;color:#ffffff;text-decoration:none;">${t}</a>
  </td></tr></table>`;
}

function emailWrapper(inner, footerLines) {
  const foot = footerLines || [
    "Nexperts Academy · IT certifications &amp; training Malaysia",
    "You received this because you submitted an enquiry on our website.",
  ];
  const footHtml = foot.map((l) => `${l}<br/>`).join("");
  return `<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="X-UA-Compatible" content="IE=edge"></head>
<body style="margin:0;padding:0;background:#f1f5f9;-webkit-text-size-adjust:100%;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f1f5f9;padding:24px 12px;">
<tr><td align="center">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(15,23,42,.08);border:1px solid #e2e8f0;">
  ${inner}
  </table>
  <p style="font-family:Arial,Helvetica,sans-serif;font-size:11px;color:#94a3b8;max-width:560px;margin:16px auto 0;line-height:1.5;">
    ${footHtml}
  </p>
</td></tr></table>
</body></html>`;
}

function buildStudentEmailHtml(data, ctx) {
  const { site, internal, fullName } = ctx;
  const inner = `
<tr><td style="background:linear-gradient(135deg,#1e40af 0%,#2563eb 55%,#3b82f6 100%);padding:28px 28px 24px;">
  <p style="margin:0 0 6px;font-family:Georgia,'Times New Roman',serif;font-size:22px;font-weight:400;color:#ffffff;line-height:1.25;">Thank you, ${escapeHtml(fullName)}</p>
  <p style="margin:0;font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#dbeafe;line-height:1.55;opacity:.95;">Your enquiry is in good hands. A member of our team will respond within <strong style="color:#fff;">4 business hours</strong> (Kuala Lumpur time).</p>
</td></tr>
<tr><td style="padding:26px 24px 8px;">
  <p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#1d4ed8;">What you sent us</p>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;">
    ${trRow("Full name", `${data.first || ""} ${data.last || ""}`.trim())}
    ${trRow("Email", data.email)}
    ${trRow("Phone / WhatsApp", data.phone)}
    ${trRow("Preferred office", data.office)}
    ${trRow("Course interest", data.course)}
    ${trRow("Enquiry type", data.type)}
    ${trRow("Your message", data.message)}
    ${trRow("Submitted", data.submittedAt)}
  </table>
</td></tr>
<tr><td style="padding:8px 24px 20px;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:12px;">
    <tr><td style="padding:18px 20px;font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#1e3a8a;line-height:1.6;">
      <strong style="display:block;margin-bottom:8px;color:#1d4ed8;">What happens next</strong>
      · We review your goals and match you to the right intake.<br/>
      · If you asked about <strong>corporate training</strong> or <strong>HRD Corp</strong>, we may include a tailored outline.<br/>
      · Need something sooner? Reply to this email or write to <a href="mailto:${escapeHtml(internal)}" style="color:#1d4ed8;font-weight:600;">${escapeHtml(internal)}</a>
    </td></tr>
  </table>
</td></tr>
<tr><td style="padding:4px 24px 28px;">
  <p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#64748b;">Explore more</p>
  ${ctaButton(`${site}/index.html#courses`, "Browse certification courses")}
  ${ctaButton(`${site}/contact.html`, "Contact & offices", "#0f172a")}
  <p style="margin:16px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#475569;">
    <a href="https://nexpertsai.com" target="_blank" rel="noopener" style="color:#1d4ed8;font-weight:700;text-decoration:none;">Nexperts AI →</a>
    <span style="color:#94a3b8;"> &nbsp;·&nbsp; </span>
    <a href="${escapeHtml(site)}/index.html#roadmap" target="_blank" rel="noopener" style="color:#1d4ed8;font-weight:600;text-decoration:none;">Career roadmaps</a>
  </p>
</td></tr>`;
  return emailWrapper(inner);
}

function buildInternalEmailHtml(data, ctx) {
  const { site, sheet, fullName } = ctx;
  const inner = `
<tr><td style="background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);padding:24px 26px;">
  <p style="margin:0 0 4px;font-family:Arial,Helvetica,sans-serif;font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#fbbf24;">New website lead</p>
  <p style="margin:0;font-family:Georgia,'Times New Roman',serif;font-size:21px;color:#ffffff;line-height:1.3;">${escapeHtml(fullName)}</p>
  <p style="margin:8px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#94a3b8;">${escapeHtml(dash(data.course))}</p>
</td></tr>
<tr><td style="padding:24px;">
  <p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#1d4ed8;">Submission details</p>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;">
    ${trRow("First name", data.first)}
    ${trRow("Last name", data.last)}
    ${trRow("Email", data.email)}
    ${trRow("Phone / WhatsApp", data.phone)}
    ${trRow("Preferred office", data.office)}
    ${trRow("Course", data.course)}
    ${trRow("Enquiry type", data.type)}
    ${trRow("Message", data.message)}
    ${trRow("Source", data.source)}
    ${trRow("Page URL", data.pageUrl)}
    ${trRow("Submitted (ISO)", data.submittedAt)}
    ${trRow("User-Agent", (data.userAgent || "").slice(0, 280) + ((data.userAgent || "").length > 280 ? "…" : ""))}
  </table>
</td></tr>
<tr><td style="padding:0 24px 12px;" align="center">
  <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:8px auto 0;">
    <tr><td style="border-radius:10px;background:#16a34a;">
      <a href="${escapeHtml(sheet)}" target="_blank" rel="noopener" style="display:inline-block;padding:16px 28px;font-family:Arial,Helvetica,sans-serif;font-size:15px;font-weight:700;color:#ffffff;text-decoration:none;">Open leads spreadsheet</a>
    </td></tr>
  </table>
  <p style="margin:14px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#64748b;line-height:1.5;">
    Your master <strong style="color:#0f172a;">Enquiries</strong> log lives in Google Sheets — open it to file this lead next to your pipeline.<br/>
    <a href="${escapeHtml(sheet)}" target="_blank" rel="noopener" style="color:#1d4ed8;word-break:break-all;">${escapeHtml(sheet)}</a>
  </p>
</td></tr>
<tr><td style="padding:8px 24px 26px;">
  <p style="margin:0;font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#94a3b8;">Quick links: <a href="${escapeHtml(site)}/admin/" style="color:#64748b;">Admin</a> · <a href="${escapeHtml(site)}/contact.html" style="color:#64748b;">Contact page</a></p>
</td></tr>`;
  return emailWrapper(inner, [
    "Internal lead notification · Nexperts Academy",
    "Do not forward this email to untrusted recipients (contains lead data).",
  ]);
}

function buildStudentEmailText(data, ctx) {
  const { internal, fullName, site } = ctx;
  return (
    `Hi ${fullName},\n\n` +
    `Thank you for contacting Nexperts Academy. We will reply within 4 business hours (KL time).\n\n` +
    `WHAT YOU SENT\n` +
    `-------------\n` +
    `Name: ${dash(`${data.first || ""} ${data.last || ""}`.trim())}\n` +
    `Email: ${dash(data.email)}\n` +
    `Phone: ${dash(data.phone)}\n` +
    `Office: ${dash(data.office)}\n` +
    `Course: ${dash(data.course)}\n` +
    `Type: ${dash(data.type)}\n` +
    `Message:\n${dash(data.message)}\n` +
    `Submitted: ${dash(data.submittedAt)}\n\n` +
    `Urgent? Email us: ${internal}\n\n` +
    `Explore: ${site}/index.html#courses\n` +
    `Contact: ${site}/contact.html\n` +
    `Nexperts AI: https://nexpertsai.com\n\n` +
    `— Nexperts Academy\n`
  );
}

function buildInternalEmailText(data, ctx) {
  const { sheet } = ctx;
  return (
    `NEW WEBSITE LEAD\n` +
    `================\n\n` +
    `Name: ${data.first || ""} ${data.last || ""}\n` +
    `Email: ${data.email || ""}\n` +
    `Phone: ${data.phone || ""}\n` +
    `Office: ${data.office || ""}\n` +
    `Course: ${data.course || ""}\n` +
    `Type: ${data.type || ""}\n` +
    `Message:\n${data.message || ""}\n\n` +
    `Source: ${data.source || ""}\n` +
    `Page: ${data.pageUrl || ""}\n` +
    `Submitted: ${data.submittedAt || ""}\n` +
    `User-Agent: ${data.userAgent || ""}\n\n` +
    `GOOGLE SHEET (all leads):\n${sheet}\n`
  );
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

const APPS_SCRIPT_URL_ENV_KEYS = [
  "APPS_SCRIPT_ENQUIRY_URL",
  "NEXPERTS_APPS_SCRIPT_WEBAPP_URL",
  "GOOGLE_APPS_SCRIPT_ENQUIRY_URL",
];

function resolveAppsScriptEnquiryUrl(env) {
  const e = env || process.env || {};
  for (const k of APPS_SCRIPT_URL_ENV_KEYS) {
    const v = String(e[k] || "").trim();
    if (v && /^https:\/\/script\.google\.com\/macros\//i.test(v)) return normalizeAppsScriptUrl(v);
  }
  return "";
}

/** Strip query/hash so POST targets the web app endpoint cleanly. */
function normalizeAppsScriptUrl(raw) {
  let u = String(raw || "").trim();
  if (!u) return "";
  const h = u.indexOf("#");
  if (h >= 0) u = u.slice(0, h);
  const q = u.indexOf("?");
  if (q >= 0) u = u.slice(0, q);
  return u;
}

function parseJsonSafe(text) {
  try {
    return text ? JSON.parse(text) : null;
  } catch {
    return null;
  }
}

/**
 * Sheet POST must use the secret Google Apps Script expects (Script properties ENQUIRY_SECRET).
 * Prefer server env so Netlify can match Google even if the browser payload is stale.
 */
function buildPayloadForSheet(data, env) {
  const e = env || process.env || {};
  const out = { ...data };
  const s = String(e.APPS_SCRIPT_ENQUIRY_SECRET || e.BREVO_ENQUIRY_SECRET || "").trim();
  if (s) out.secret = s;
  return out;
}

/**
 * Web app returns 302 to googleusercontent.com — Node fetch with redirect:"follow"
 * keeps POST and returns JSON (manual POST to the Location URL returns 405).
 */
async function fetchAppsScriptOnce(url, bodyString, contentType) {
  const u = normalizeAppsScriptUrl(url);
  if (!u) throw new Error("apps_script_bad_url");
  const res = await fetch(u, {
    method: "POST",
    headers: {
      "Content-Type": contentType,
      Accept: "application/json, text/plain, */*",
    },
    body: bodyString,
    redirect: "follow",
  });
  const text = await res.text();
  return { res, text };
}

function describeAppsScriptFailure(res, json, text) {
  const t = String(text || "").trim();
  const looksHtml = t.startsWith("<") || t.includes("<!DOCTYPE");
  const err = (json && json.error) || (looksHtml ? "non_json_html" : null) || res.statusText || `http_${res.status}`;
  let hint = looksHtml
    ? " (Apps Script returned HTML — redeploy Web app as Execute as Me / Anyone, or wrong URL)"
    : "";
  if (json && json.error === "forbidden") {
    hint +=
      " | Set Apps Script Project Settings → Script properties ENQUIRY_SECRET to the same value as BREVO_ENQUIRY_SECRET / secret in enquiry-config.js, or remove ENQUIRY_SECRET.";
  }
  return `${String(err).slice(0, 120)}${hint} · ${t.slice(0, 100)}`;
}

/**
 * Append row in bound Sheet (same contract as browser → Apps Script).
 * Tries x-www-form-urlencoded payload=, then JSON body on the resolved URL.
 */
async function forwardEnquiryToAppsScript(webAppUrl, data) {
  const base = normalizeAppsScriptUrl(webAppUrl);
  if (!base) return { skipped: true };

  const sheetPayload = buildPayloadForSheet(data, process.env);
  const jsonStr = JSON.stringify(sheetPayload);
  const formBody = new URLSearchParams();
  formBody.set("payload", jsonStr);

  let r = await fetchAppsScriptOnce(
    base,
    formBody.toString(),
    "application/x-www-form-urlencoded;charset=UTF-8",
  );
  let parsed = parseJsonSafe(r.text);
  if (r.res.ok && parsed && parsed.ok === true) {
    return { skipped: false, ok: true };
  }

  const firstErr = describeAppsScriptFailure(r.res, parsed, r.text);

  let r2 = await fetchAppsScriptOnce(base, jsonStr, "application/json;charset=UTF-8");
  let p2 = parseJsonSafe(r2.text);
  if (r2.res.ok && p2 && p2.ok === true) {
    return { skipped: false, ok: true };
  }

  throw new Error(
    `${describeAppsScriptFailure(r2.res, p2, r2.text)} | form_try: ${firstErr}`.slice(0, 380),
  );
}

export async function handler(event) {
  const h = corsHeaders();

  if (event.httpMethod === "OPTIONS") {
    return { statusCode: 204, headers: h, body: "" };
  }

  if (event.httpMethod !== "POST") {
    return {
      statusCode: 405,
      headers: h,
      body: JSON.stringify({ ok: false, error: "method_not_allowed" }),
    };
  }

  const apiKey = process.env.BREVO_API_KEY || "";
  const senderEmail = process.env.BREVO_SENDER_EMAIL || "";
  const senderName = process.env.BREVO_SENDER_NAME || "Nexperts Academy";
  const internalRecipients = internalRecipientsList(process.env);
  const internalTo = internalRecipients[0].email;
  const expectedSecret = String(process.env.BREVO_ENQUIRY_SECRET || "").trim();

  if (!apiKey || !senderEmail) {
    return {
      statusCode: 503,
      headers: h,
      body: JSON.stringify({
        ok: false,
        error: "server_misconfigured",
        hint: "Set BREVO_API_KEY and BREVO_SENDER_EMAIL on Netlify.",
      }),
    };
  }

  let data;
  try {
    const ct = (event.headers["content-type"] || "").toLowerCase();
    if (ct.includes("application/json")) {
      data = JSON.parse(event.body || "{}");
    } else if (ct.includes("application/x-www-form-urlencoded")) {
      const params = new URLSearchParams(event.body || "");
      const raw = params.get("payload");
      data = raw ? JSON.parse(raw) : {};
    } else {
      data = JSON.parse(event.body || "{}");
    }
  } catch {
    return {
      statusCode: 400,
      headers: h,
      body: JSON.stringify({ ok: false, error: "invalid_json" }),
    };
  }

  if (
    expectedSecret &&
    String(data.secret || "").trim() !== expectedSecret
  ) {
    return {
      statusCode: 403,
      headers: h,
      body: JSON.stringify({
        ok: false,
        error: "forbidden",
        hint:
          "BREVO_ENQUIRY_SECRET is set on Netlify but the form did not send the same secret. Either remove BREVO_ENQUIRY_SECRET in Netlify, or set the same value as secret in js/enquiry-config.js and redeploy the site.",
      }),
    };
  }

  const first = String(data.first || "").trim();
  const last = String(data.last || "").trim();
  const email = String(data.email || "").trim();
  if (!first || !last || !email) {
    return {
      statusCode: 400,
      headers: h,
      body: JSON.stringify({ ok: false, error: "missing_fields" }),
    };
  }

  const studentName = `${first} ${last}`.trim();
  const internalSubject = `[Website enquiry] ${studentName} — ${String(data.course || "Course not selected").slice(0, 80)}`;
  const ctx = getCtx(data, process.env);

  const studentHtml = buildStudentEmailHtml(data, ctx);
  const studentText = buildStudentEmailText(data, ctx);
  const internalHtml = buildInternalEmailHtml(data, ctx);
  const internalText = buildInternalEmailText(data, ctx);

  try {
    await brevoSend(apiKey, {
      sender: { name: senderName, email: senderEmail },
      to: [{ email, name: studentName }],
      replyTo: { email: internalTo, name: senderName },
      subject: "We received your enquiry — Nexperts Academy",
      textContent: studentText,
      htmlContent: studentHtml,
    });

    await brevoSend(apiKey, {
      sender: { name: senderName, email: senderEmail },
      to: internalRecipients,
      replyTo: { email, name: studentName },
      subject: internalSubject,
      textContent: internalText,
      htmlContent: internalHtml,
    });
  } catch (e) {
    return {
      statusCode: 502,
      headers: h,
      body: JSON.stringify({
        ok: false,
        error: "email_send_failed",
        detail: String(e.message || e).slice(0, 200),
      }),
    };
  }

  const appsScriptUrl = resolveAppsScriptEnquiryUrl(process.env);
  let sheetLogged = false;
  let sheetError = null;
  if (appsScriptUrl) {
    try {
      await forwardEnquiryToAppsScript(appsScriptUrl, data);
      sheetLogged = true;
    } catch (e) {
      sheetError = String(e.message || e).slice(0, 220);
    }
  }

  const bodyOut = {
    ok: true,
    sheetLogged,
    ...(sheetError ? { sheetError } : {}),
  };
  if (!appsScriptUrl) {
    bodyOut.sheetHint =
      "APPS_SCRIPT_ENQUIRY_URL is not set — add it to .env (netlify dev) or Netlify site env (same URL as webAppUrl in js/enquiry-config.js), then restart dev server / redeploy.";
  }

  return {
    statusCode: 200,
    headers: h,
    body: JSON.stringify(bodyOut),
  };
}
