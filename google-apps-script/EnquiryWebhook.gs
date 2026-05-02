/**
 * Nexperts Academy — Enquiry Webhook (Google Apps Script)
 *
 * Saves each enquiry as one row in the bound spreadsheet tab "Enquiries".
 * Email is handled elsewhere (e.g. Brevo + Netlify).
 *
 * SETUP:
 * 1. Bound script: Extensions → Apps Script → paste this file.
 * 2. Script properties (optional): ENQUIRY_SECRET = same as `secret` in js/enquiry-config.js
 * 3. Run setupSheetHeaders() once if the tab is empty or you want headers reset.
 * 4. Deploy → Web app → Execute as: Me, Who has access: Anyone
 * 5. Put the Web App URL in enquiry-config.js → webAppUrl and Netlify APPS_SCRIPT_ENQUIRY_URL if used.
 *
 * Phone numbers: stored as plain text using column format "@" (Plain text). Do not prefix with "'"
 * in the same cell as "@" — that pattern triggers #ERROR! in Google Sheets. "@" is the correct API
 * way to force text for values like +60… / 01….
 */

var SHEET_NAME = "Enquiries";
var COL_COUNT = 12;

function doPost(e) {
  try {
    var raw = extractRawPayload_(e);
    if (!raw) {
      return jsonOut_({ ok: false, error: "empty_payload" });
    }

    var data = JSON.parse(raw);
    var expected = PropertiesService.getScriptProperties().getProperty(
      "ENQUIRY_SECRET"
    );
    if (
      expected &&
      String(data.secret || "").trim() !== String(expected).trim()
    ) {
      return jsonOut_({ ok: false, error: "forbidden" });
    }

    var first = trim_(data.first);
    var last = trim_(data.last);
    var email = trim_(data.email);
    if (!first || !last || !email) {
      return jsonOut_({ ok: false, error: "missing_name_or_email" });
    }

    writeEnquiryRow_(data);
    return jsonOut_({ ok: true, saved: true });
  } catch (err) {
    return jsonOut_({
      ok: false,
      error: String(err && err.message ? err.message : err),
    });
  }
}

/** One-time: (re)creates "Enquiries" tab with header row only. */
function setupSheetHeaders() {
  var sh = getOrCreateSheet_();
  sh.clear();
  sh.getRange(1, 1, 1, COL_COUNT).setValues([
    [
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
    ],
  ]);
}

/** Manual smoke test — check "Enquiries" after Run. */
function testAppendSampleRow() {
  writeEnquiryRow_({
    submittedAt: new Date().toISOString(),
    source: "manual_test",
    pageUrl: "https://example.com/test",
    first: "Test",
    last: "User",
    email: "test@example.com",
    phone: "+60 82347982",
    office: "Malaysia — Petaling Jaya (HQ)",
    course: "CEH — sample",
    type: "Individual enrolment",
    message: "Hello from testAppendSampleRow()",
    userAgent: "AppsScriptEditor/1.0",
  });
}

// --- Internals ---

function jsonOut_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(
    ContentService.MimeType.JSON
  );
}

function trim_(v) {
  return String(v == null ? "" : v).trim();
}

/**
 * Leading = + - @ in Sheets start formulas or number patterns. Prefix with ASCII apostrophe for those cells only.
 * Phone is handled separately (plain string + "@" format), never use this for phone.
 */
function escapeSheetCell_(v) {
  var s = String(v == null ? "" : v);
  if (s === "") return "";
  if (/^[=+\-@]/.test(s)) {
    return "'" + s;
  }
  return s;
}

function extractRawPayload_(e) {
  var raw = "";
  if (e && e.parameter && e.parameter.payload) {
    raw = String(e.parameter.payload);
  }
  if (!raw && e && e.postData && e.postData.contents) {
    var contents = String(e.postData.contents);
    var ct = String((e.postData && e.postData.type) || "").toLowerCase();
    if (ct.indexOf("application/x-www-form-urlencoded") >= 0) {
      raw = extractPayloadFromWwwForm_(contents);
    } else if (ct.indexOf("application/json") >= 0) {
      raw = contents;
    } else {
      raw = extractPayloadFromWwwForm_(contents);
      if (!raw) raw = contents;
    }
  }
  return raw;
}

function extractPayloadFromWwwForm_(contents) {
  if (!contents) return "";
  var pairs = String(contents).split("&");
  for (var i = 0; i < pairs.length; i++) {
    var eq = pairs[i].indexOf("=");
    if (eq <= 0) continue;
    var key = decodeURIComponent(
      pairs[i].substring(0, eq).replace(/\+/g, " ")
    );
    if (key !== "payload") continue;
    return decodeURIComponent(
      pairs[i].substring(eq + 1).replace(/\+/g, " ")
    );
  }
  return "";
}

function getOrCreateSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME);
  }
  return sh;
}

/**
 * Next row index for a new data row (row 1 = headers).
 * If sheet is empty, creates headers first.
 */
function nextDataRowIndex_(sh) {
  if (sh.getLastRow() === 0) {
    setupSheetHeaders();
  }
  return sh.getLastRow() + 1;
}

/**
 * Sheet.getRange(row, column, numRows, numColumns) — third/fourth args are COUNTS, not end coordinates.
 */
function buildRowArray_(data) {
  return [
    escapeSheetCell_(data.submittedAt || new Date().toISOString()),
    escapeSheetCell_(data.source || ""),
    escapeSheetCell_(data.pageUrl || ""),
    escapeSheetCell_(data.first || ""),
    escapeSheetCell_(data.last || ""),
    escapeSheetCell_(data.email || ""),
    trim_(data.phone),
    escapeSheetCell_(data.office || ""),
    escapeSheetCell_(data.course || ""),
    escapeSheetCell_(data.type || ""),
    escapeSheetCell_(data.message || ""),
    escapeSheetCell_(data.userAgent || ""),
  ];
}

function writeEnquiryRow_(data) {
  var sh = getOrCreateSheet_();
  var row = buildRowArray_(data);
  if (row.length !== COL_COUNT) {
    throw new Error("row_length_mismatch");
  }
  var r = nextDataRowIndex_(sh);
  // A1 avoids ambiguity: some APIs use (row,col,endRow,endCol) instead of (row,col,numRows,numCols).
  var range = sh.getRange("A" + r + ":L" + r);
  var formats = [];
  for (var c = 0; c < COL_COUNT; c++) {
    formats.push("@");
  }
  range.setNumberFormats([formats]);
  range.setValues([row]);
}
