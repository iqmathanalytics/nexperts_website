/**
 * Nexperts Academy — Enquiry Webhook (Google Apps Script)
 *
 * Saves each enquiry as one row in the "Enquiries" tab.
 * Email is handled elsewhere (e.g. Brevo + Netlify / Cloudflare).
 *
 * SETUP:
 * 1. Extensions → Apps Script → paste this file (bound or standalone).
 * 2. Script properties (Project settings):
 *    - SPREADSHEET_ID = Google Sheet ID (optional; defaults below)
 *    - ENQUIRY_SECRET = same as secret in js/enquiry-config.js (optional)
 * 3. Run setupSheetHeaders() once.
 * 4. Deploy → Web app → Execute as: Me, Who has access: Anyone → New version.
 * 5. webAppUrl in js/enquiry-config.js + APPS_SCRIPT_ENQUIRY_URL on hosting (optional override).
 *
 * If executions show "Completed" but no rows appear:
 * - Open tab "WebhookLog" on the same spreadsheet (last 200 webhook attempts).
 * - If error is "forbidden", fix ENQUIRY_SECRET or remove it from Script properties.
 * - Confirm you are viewing the spreadsheet matching SPREADSHEET_ID.
 */

var SHEET_NAME = "Enquiries";
var LOG_SHEET_NAME = "WebhookLog";
var COL_COUNT = 12;
var LOG_COL_COUNT = 7;
var MAX_LOG_ROWS = 200;

/** Master leads sheet — same as NEXPERTS_LEADS_SHEET_URL in hosting env. */
var DEFAULT_SPREADSHEET_ID = "1vuZbvwAkuwIFU1F-CLjz8xMOKRXpJp0vqKCGbiZt0PE";

function doGet() {
  return jsonOut_({
    ok: true,
    service: "nexperts-enquiry-webhook",
    version: 4,
    spreadsheetId: getSpreadsheetId_(),
  });
}

function doPost(e) {
  var log = {
    ok: false,
    error: "",
    source: "",
    email: "",
    row: 0,
  };
  try {
    var raw = extractRawPayload_(e);
    if (!raw) {
      log.error = "empty_payload";
      writeWebhookLog_(log);
      return jsonOut_({ ok: false, error: log.error });
    }

    var data;
    try {
      data = JSON.parse(raw);
    } catch (parseErr) {
      log.error = "invalid_json";
      writeWebhookLog_(log);
      return jsonOut_({ ok: false, error: log.error });
    }

    log.source = trim_(data.source);
    log.email = trim_(data.email);

    var expected = PropertiesService.getScriptProperties().getProperty(
      "ENQUIRY_SECRET"
    );
    if (
      expected &&
      String(data.secret || "").trim() !== String(expected).trim()
    ) {
      log.error = "forbidden";
      writeWebhookLog_(log);
      return jsonOut_({
        ok: false,
        error: "forbidden",
        hint:
          "ENQUIRY_SECRET in Script properties does not match the secret sent by the website. Fix or remove ENQUIRY_SECRET.",
      });
    }

    var first = trim_(data.first);
    var last = trim_(data.last);
    var email = trim_(data.email);
    if (!first || !last || !email) {
      log.error = "missing_name_or_email";
      writeWebhookLog_(log);
      return jsonOut_({ ok: false, error: log.error });
    }

    var rowNum = writeEnquiryRow_(data);
    log.ok = true;
    log.row = rowNum;
    writeWebhookLog_(log);
    return jsonOut_({
      ok: true,
      saved: true,
      row: rowNum,
      spreadsheetId: getSpreadsheetId_(),
      sheet: SHEET_NAME,
    });
  } catch (err) {
    log.error = String(err && err.message ? err.message : err);
    writeWebhookLog_(log);
    return jsonOut_({ ok: false, error: log.error });
  }
}

/** One-time: (re)creates "Enquiries" tab with header row only. */
function setupSheetHeaders() {
  var sh = getOrCreateSheet_(SHEET_NAME);
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

/** One-time: headers for WebhookLog tab. */
function setupWebhookLogHeaders() {
  var sh = getOrCreateSheet_(LOG_SHEET_NAME);
  if (sh.getLastRow() > 0) return;
  sh.getRange(1, 1, 1, LOG_COL_COUNT).setValues([
    [
      "Logged At (ISO)",
      "OK",
      "Error",
      "Source",
      "Email",
      "Row",
      "Spreadsheet ID",
    ],
  ]);
}

/** Manual smoke test — check "Enquiries" after Run. */
function testAppendSampleRow() {
  var rowNum = writeEnquiryRow_({
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
  Logger.log("Wrote row " + rowNum + " to " + SHEET_NAME);
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

function getSpreadsheetId_() {
  var props = PropertiesService.getScriptProperties();
  var id = trim_(props.getProperty("SPREADSHEET_ID"));
  if (id) return id;
  var active = SpreadsheetApp.getActiveSpreadsheet();
  if (active) return active.getId();
  return DEFAULT_SPREADSHEET_ID;
}

function getSpreadsheet_() {
  return SpreadsheetApp.openById(getSpreadsheetId_());
}

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

function getOrCreateSheet_(name) {
  var ss = getSpreadsheet_();
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
  }
  return sh;
}

function nextDataRowIndex_(sh) {
  if (sh.getLastRow() === 0) {
    if (sh.getName() === SHEET_NAME) {
      setupSheetHeaders();
    } else if (sh.getName() === LOG_SHEET_NAME) {
      setupWebhookLogHeaders();
    }
  }
  return sh.getLastRow() + 1;
}

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
  var sh = getOrCreateSheet_(SHEET_NAME);
  var row = buildRowArray_(data);
  if (row.length !== COL_COUNT) {
    throw new Error("row_length_mismatch");
  }
  var r = nextDataRowIndex_(sh);
  var range = sh.getRange(r, 1, 1, COL_COUNT);
  range.setNumberFormat("@");
  range.setValues([row]);
  return r;
}

function writeWebhookLog_(log) {
  try {
    var sh = getOrCreateSheet_(LOG_SHEET_NAME);
    setupWebhookLogHeaders();
    var r = sh.getLastRow() + 1;
    sh.getRange(r, 1, 1, LOG_COL_COUNT).setValues([
      [
        new Date().toISOString(),
        log.ok ? "yes" : "no",
        trim_(log.error),
        trim_(log.source),
        trim_(log.email),
        log.row ? String(log.row) : "",
        getSpreadsheetId_(),
      ],
    ]);
    trimWebhookLog_(sh);
  } catch (ignore) {
    /* never block webhook response on log failure */
  }
}

function trimWebhookLog_(sh) {
  var last = sh.getLastRow();
  var max = MAX_LOG_ROWS + 1;
  if (last > max) {
    sh.deleteRows(2, last - max);
  }
}
