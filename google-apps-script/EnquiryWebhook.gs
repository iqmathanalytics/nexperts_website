/**
 * Nexperts Academy — Enquiry Webhook (Google Apps Script)
 *
 * SETUP (once):
 * 1. Create a new Google Sheet while signed in as info@nexpertsai.com
 * 2. Extensions → Apps Script → paste this entire file
 * 3. Project Settings → Script properties → Add:
 *      ENQUIRY_SECRET = (optional) same value as js/enquiry-config.js secret
 * 4. Run setupSheetHeaders() once from the editor (select function → Run)
 * 5. Deploy → New deployment → Type: Web app
 *      - Execute as: Me (info@nexpertsai.com)
 *      - Who has access: Anyone
 * 6. Copy the Web App URL into js/enquiry-config.js → webAppUrl
 *
 * EMAIL BEHAVIOUR:
 * - MailApp sends as the account that OWNS and AUTHORISES this script.
 *   If you create the script as info@nexpertsai.com, mail typically sends
 *   from that mailbox (Workspace / Gmail "Send mail as" may apply).
 * - Two messages per enquiry:
 *     A) Student: acknowledgement
 *     B) enquiry@nexpertsacademy.com: full lead details
 */

var SHEET_NAME = "Enquiries";
var INTERNAL_NOTIFY = "enquiry@nexpertsacademy.com";
var REPLY_TO = INTERNAL_NOTIFY;

/** Optional: Script property OPTIONAL_BCC = your personal Gmail for debugging (copy of both emails). */
function _bccDebug_() {
  var v = PropertiesService.getScriptProperties().getProperty("OPTIONAL_BCC");
  return v ? String(v).trim() : "";
}

/** Plain text → minimal HTML (helps some spam filters accept multipart/alternative). */
function _htmlBody_(plain) {
  var esc = String(plain || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return (
    "<!doctype html><html><head><meta charset=\"utf-8\"></head><body><pre style=\"font-family:system-ui,sans-serif;white-space:pre-wrap\">" +
    esc +
    "</pre></body></html>"
  );
}

function doPost(e) {
  try {
    var raw = "";
    if (e && e.parameter && e.parameter.payload) {
      raw = e.parameter.payload;
    } else if (e && e.postData && e.postData.contents) {
      raw = e.postData.contents;
    }
    if (!raw) {
      return jsonOut({ ok: false, error: "empty_payload" });
    }

    var data = JSON.parse(raw);
    var props = PropertiesService.getScriptProperties();
    var expected = props.getProperty("ENQUIRY_SECRET");
    if (expected && String(data.secret || "") !== String(expected)) {
      return jsonOut({ ok: false, error: "forbidden" });
    }

    var row = buildRow_(data);
    appendRow_(row);

    sendStudentAck_(data);
    sendInternalNotify_(data);

    return jsonOut({ ok: true });
  } catch (err) {
    return jsonOut({ ok: false, error: String(err && err.message ? err.message : err) });
  }
}

/** One-time: creates sheet tab + header row */
function setupSheetHeaders() {
  var sh = getSheet_();
  sh.clear();
  sh.appendRow([
    "Submitted At (ISO)",
    "Source",
    "Page URL",
    "First",
    "Last",
    "Email",
    "Phone",
    "Office",
    "Course",
    "Type",
    "Message",
    "User Agent",
  ]);
}

function buildRow_(data) {
  return [
    data.submittedAt || new Date().toISOString(),
    data.source || "",
    data.pageUrl || "",
    data.first || "",
    data.last || "",
    data.email || "",
    data.phone || "",
    data.office || "",
    data.course || "",
    data.type || "",
    data.message || "",
    data.userAgent || "",
  ];
}

function getSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME);
  }
  return sh;
}

function appendRow_(row) {
  var sh = getSheet_();
  if (sh.getLastRow() === 0) {
    setupSheetHeaders();
  }
  sh.appendRow(row);
}

function sendStudentAck_(data) {
  var to = String(data.email || "").trim();
  if (!to) return;
  var name = (String(data.first || "").trim() + " " + String(data.last || "").trim()).trim();
  var subject = "We received your enquiry — Nexperts Academy";
  var body =
    "Hi " +
    (name || "there") +
    ",\n\n" +
    "Thanks for contacting Nexperts Academy. Our team will reply within 4 business hours (KL time).\n\n" +
    "If your question is urgent, you can also email us directly at " +
    INTERNAL_NOTIFY +
    ".\n\n" +
    "— Nexperts Academy\n";

  var opts = {
    to: to,
    subject: subject,
    body: body,
    htmlBody: _htmlBody_(body),
    replyTo: REPLY_TO,
    name: "Nexperts Academy",
  };
  var bcc = _bccDebug_();
  if (bcc) opts.bcc = bcc;
  MailApp.sendEmail(opts);
}

function sendInternalNotify_(data) {
  var subject =
    "[Website enquiry] " +
    String(data.first || "").trim() +
    " " +
    String(data.last || "").trim() +
    " — " +
    String(data.course || "Course not selected").slice(0, 80);

  var body =
    "New enquiry from the website\n" +
    "============================\n\n" +
    "Submitted: " +
    (data.submittedAt || "") +
    "\n" +
    "Source: " +
    (data.source || "") +
    "\n" +
    "Page: " +
    (data.pageUrl || "") +
    "\n\n" +
    "Name: " +
    (data.first || "") +
    " " +
    (data.last || "") +
    "\n" +
    "Email: " +
    (data.email || "") +
    "\n" +
    "Phone: " +
    (data.phone || "") +
    "\n" +
    "Office: " +
    (data.office || "") +
    "\n" +
    "Course: " +
    (data.course || "") +
    "\n" +
    "Type: " +
    (data.type || "") +
    "\n\n" +
    "Message:\n" +
    (data.message || "") +
    "\n\n" +
    "User-Agent:\n" +
    (data.userAgent || "") +
    "\n";

  var stu = String(data.email || "").trim();
  var opts2 = {
    to: INTERNAL_NOTIFY,
    subject: subject,
    body: body,
    htmlBody: _htmlBody_(body),
    replyTo: stu || REPLY_TO,
    name: "Nexperts Academy",
  };
  var bcc2 = _bccDebug_();
  if (bcc2) opts2.bcc = bcc2;
  MailApp.sendEmail(opts2);
}

/**
 * Run this manually from the Apps Script editor (▶ Run) to test delivery.
 * Check BOTH inboxes + Spam. If this arrives but webhook mail does not,
 * the issue is specific to the webhook payload or throttling — not Gmail.
 */
function testEmailDelivery() {
  MailApp.sendEmail({
    to: Session.getActiveUser().getEmail(),
    subject: "[Test] Nexperts enquiry mail path",
    body:
      "If you see this in Inbox, MailApp delivery works.\n\n" +
      "Next: search Spam for subject containing [Website enquiry]\n" +
      "and ask your Workspace admin to check Admin > Reporting > Email log search.\n",
    htmlBody:
      "<p>If you see this in <strong>Inbox</strong>, MailApp delivery works.</p>" +
      "<p>Next: check <strong>Spam</strong> for subjects containing <code>[Website enquiry]</code>.</p>",
    name: "Nexperts Academy",
  });
}

/** Change this if you want to test another inbox. */
var TEST_EXTERNAL_TO = "harijo560@gmail.com";

/**
 * Run manually: select function testEmailToExternalGmail → Run → Authorise.
 * Sends one message to TEST_EXTERNAL_TO (same style as live enquiry mail).
 * If it lands in Spam, improve SPF/DKIM/DMARC for the SENDING domain and
 * avoid “From” / brand domain mismatch where possible.
 */
function testEmailToExternalGmail() {
  var plain =
    "This is a manual deliverability test from your Nexperts Academy Apps Script project.\n\n" +
    "If you see this in Spam, open the message → Report not spam (helps Gmail learn).\n\n" +
    "Sending account: " +
    Session.getActiveUser().getEmail() +
    "\n";

  MailApp.sendEmail({
    to: TEST_EXTERNAL_TO,
    subject: "[Nexperts test] External Gmail deliverability",
    body: plain,
    htmlBody: _htmlBody_(plain),
    replyTo: REPLY_TO,
    name: "Nexperts Academy",
  });
}

function jsonOut(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(
    ContentService.MimeType.JSON
  );
}
