/**
 * Nexperts Academy — Enquiry Webhook (Google Apps Script)
 *
 * This deployment only SAVES each enquiry as a new row in the bound Google Sheet.
 * Email (student + team) is handled separately — e.g. Brevo via Netlify (`enquiry-brevo.mjs`).
 *
 * SETUP (once):
 * 1. Create or open the Google Sheet that should store leads.
 * 2. Extensions → Apps Script → paste this entire file (bound to that spreadsheet).
 * 3. Project Settings → Script properties → Add (recommended):
 *      ENQUIRY_SECRET = same value as `secret` in js/enquiry-config.js (if you POST here from the site).
 * 4. Run setupSheetHeaders() once from the editor (select function → Run) to create the "Enquiries" tab + headers.
 * 5. Deploy → New deployment → Type: Web app
 *      - Execute as: Me
 *      - Who has access: Anyone (required for anonymous website POSTs)
 * 6. Copy the Web App URL into js/enquiry-config.js → webAppUrl, and into Netlify env APPS_SCRIPT_ENQUIRY_URL (same URL) so the Brevo Netlify function can forward leads to this script for sheet rows.
 */

var SHEET_NAME = "Enquiries";

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
    if (
      expected &&
      String(data.secret || "").trim() !== String(expected).trim()
    ) {
      return jsonOut({ ok: false, error: "forbidden" });
    }

    var first = String(data.first || "").trim();
    var last = String(data.last || "").trim();
    var email = String(data.email || "").trim();
    if (!first || !last || !email) {
      return jsonOut({ ok: false, error: "missing_name_or_email" });
    }

    var row = buildRow_(data);
    appendRow_(row);

    return jsonOut({ ok: true, saved: true });
  } catch (err) {
    return jsonOut({ ok: false, error: String(err && err.message ? err.message : err) });
  }
}

/** One-time: creates "Enquiries" tab + header row (clears that tab if it already exists). */
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

/**
 * Force plain text in Sheets so leading +, =, -, @ are not parsed as formulas.
 */
function asSheetPlain_(v) {
  var s = String(v == null ? "" : v);
  if (s === "") return "";
  if (/^[=+\-@]/.test(s)) return "'" + s;
  return s;
}

function buildRow_(data) {
  return [
    asSheetPlain_(data.submittedAt || new Date().toISOString()),
    asSheetPlain_(data.source || ""),
    asSheetPlain_(data.pageUrl || ""),
    asSheetPlain_(data.first || ""),
    asSheetPlain_(data.last || ""),
    asSheetPlain_(data.email || ""),
    asSheetPlain_(data.phone || ""),
    asSheetPlain_(data.office || ""),
    asSheetPlain_(data.course || ""),
    asSheetPlain_(data.type || ""),
    asSheetPlain_(data.message || ""),
    asSheetPlain_(data.userAgent || ""),
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
  var r = sh.getLastRow();
  var n = row.length;
  if (r > 0 && n > 0) {
    sh.getRange(r, 1, r, n).setNumberFormat("@");
  }
}

/**
 * Optional: run manually to verify a row is written (no website required).
 * Check the "Enquiries" tab after Run.
 */
function testAppendSampleRow() {
  appendRow_([
    new Date().toISOString(),
    "manual_test",
    "https://example.com/test",
    "Test",
    "User",
    "test@example.com",
    "+60 000",
    "Malaysia — Petaling Jaya (HQ)",
    "CEH — sample",
    "Individual enrolment",
    "Hello from Apps Script testAppendSampleRow()",
    "AppsScriptEditor/1.0",
  ]);
}

function jsonOut(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(
    ContentService.MimeType.JSON
  );
}
