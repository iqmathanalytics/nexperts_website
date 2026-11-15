/**
 * Nexperts Academy — Enquiry Webhook (Google Apps Script)
 *
 * - Website enquiries → "Enquiries" tab
 * - Stripe paid enrollments → "Paid Enrollments" tab (same spreadsheet file)
 * Email is handled elsewhere (Brevo + Netlify / Cloudflare).
 *
 * SETUP:
 * 1. Extensions → Apps Script → paste this file (bound or standalone).
 * 2. Script properties (Project settings):
 *    - SPREADSHEET_ID = Google Sheet ID (optional; defaults below)
 *    - ENQUIRY_SECRET = same as secret in js/enquiry-config.js (optional)
 * 3. Run setupSheetHeaders() and setupPaidEnrollmentsHeaders() once.
 * 4. Deploy → Web app → Execute as: Me, Who has access: Anyone → New version.
 * 5. webAppUrl in js/enquiry-config.js + APPS_SCRIPT_ENQUIRY_URL on hosting (optional override).
 *
 * If executions show "Completed" but no rows appear:
 * - Open tab "WebhookLog" on the same spreadsheet (last 200 webhook attempts).
 * - If error is "forbidden", fix ENQUIRY_SECRET or remove it from Script properties.
 * - Confirm you are viewing the spreadsheet matching SPREADSHEET_ID.
 */

var SHEET_NAME = "Enquiries";
var PAID_SHEET_NAME = "Paid Enrollments";
var RECEIPT_INDEX_NAME = "Receipt Index";
var LOG_SHEET_NAME = "WebhookLog";
var COL_COUNT = 12;
var PAID_COL_COUNT = 18;
var RECEIPT_INDEX_COLS = 6;
var LOG_COL_COUNT = 7;
var MAX_LOG_ROWS = 200;

/** Master leads sheet — same as NEXPERTS_LEADS_SHEET_URL in hosting env. */
var DEFAULT_SPREADSHEET_ID = "1vuZbvwAkuwIFU1F-CLjz8xMOKRXpJp0vqKCGbiZt0PE";

function doGet() {
  return jsonOut_({
    ok: true,
    service: "nexperts-enquiry-webhook",
    version: 7,
    spreadsheetId: getSpreadsheetId_(),
    sheets: [SHEET_NAME, PAID_SHEET_NAME, RECEIPT_INDEX_NAME, LOG_SHEET_NAME],
  });
}

function doPost(e) {
  var log = {
    ok: false,
    error: "",
    source: "",
    email: "",
    row: 0,
    sheet: "",
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

    log.source = trim_(data.source || data.action);
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

    // Allocate / reuse professional receipt numbers (NXA-RCP-YYYY-###### / NXA-ORD-YYYY-######)
    if (trim_(data.action).toLowerCase() === "allocate_receipt") {
      var allocated = allocateReceiptNumbers_(data);
      log.ok = true;
      log.source = "allocate_receipt";
      log.email = trim_(data.stripeSessionId || data.paymentIntent);
      writeWebhookLog_(log);
      return jsonOut_({
        ok: true,
        invoiceNo: allocated.invoiceNo,
        orderRef: allocated.orderRef,
        year: allocated.year,
        seq: allocated.seq,
        reused: !!allocated.reused,
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

    var target = resolveTargetSheet_(data);
    log.sheet = target;

    var beforeLast = 0;
    try {
      if (target === PAID_SHEET_NAME) {
        beforeLast = getOrCreateSheet_(PAID_SHEET_NAME).getLastRow();
      }
    } catch (ignoreBefore) {
      beforeLast = 0;
    }

    var rowNum =
      target === PAID_SHEET_NAME
        ? writePaidEnrollmentRow_(data)
        : writeEnquiryRow_(data);

    var duplicate =
      target === PAID_SHEET_NAME && beforeLast > 0 && rowNum > 0 && rowNum <= beforeLast;

    log.ok = true;
    log.row = rowNum;
    writeWebhookLog_(log);
    return jsonOut_({
      ok: true,
      saved: true,
      row: rowNum,
      duplicate: !!duplicate,
      spreadsheetId: getSpreadsheetId_(),
      sheet: target,
    });
  } catch (err) {
    log.error = String(err && err.message ? err.message : err);
    writeWebhookLog_(log);
    return jsonOut_({ ok: false, error: log.error });
  }
}

/**
 * Route paid Stripe enrollments to "Paid Enrollments"; everything else → "Enquiries".
 * Server should send targetSheet / sheet / recordType explicitly.
 */
function resolveTargetSheet_(data) {
  var explicit = trim_(data.targetSheet || data.sheet || data.sheetName);
  if (explicit) {
    var lower = explicit.toLowerCase();
    if (
      lower === "paid enrollments" ||
      lower === "paid_enrollments" ||
      lower === "payments" ||
      lower === "enrollments"
    ) {
      return PAID_SHEET_NAME;
    }
    if (lower === "enquiries" || lower === "enquiry") {
      return SHEET_NAME;
    }
  }
  var recordType = trim_(data.recordType || data.record_type).toLowerCase();
  if (
    recordType === "paid_enrollment" ||
    recordType === "payment" ||
    recordType === "stripe"
  ) {
    return PAID_SHEET_NAME;
  }
  var source = trim_(data.source).toLowerCase();
  var type = trim_(data.type).toLowerCase();
  if (
    source === "stripe-checkout" ||
    source.indexOf("stripe") === 0 ||
    type === "paid enrollment"
  ) {
    return PAID_SHEET_NAME;
  }
  return SHEET_NAME;
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

/** One-time: (re)creates "Paid Enrollments" tab with payment headers. */
function setupPaidEnrollmentsHeaders() {
  var sh = getOrCreateSheet_(PAID_SHEET_NAME);
  sh.clear();
  sh.getRange(1, 1, 1, PAID_COL_COUNT).setValues([paidEnrollmentHeaders_()]);
}

/** One-time: Receipt Index for durable invoice/order allocation. */
function setupReceiptIndexHeaders() {
  var sh = getOrCreateSheet_(RECEIPT_INDEX_NAME);
  if (sh.getLastRow() > 0) return;
  sh.getRange(1, 1, 1, RECEIPT_INDEX_COLS).setValues([
    [
      "Allocated At (ISO)",
      "Year",
      "Seq",
      "Invoice No",
      "Order Ref",
      "Stripe Session ID",
    ],
  ]);
}

function paidEnrollmentHeaders_() {
  return [
    "Paid At (ISO)",
    "Invoice No",
    "Order Ref",
    "Stripe Session ID",
    "Payment Intent",
    "First",
    "Last",
    "Email",
    "Phone",
    "Course",
    "Intake",
    "Training Mode",
    "Amount",
    "Currency",
    "Payment Method",
    "Payment Status",
    "Page URL",
    "Source",
  ];
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

/** Manual smoke test — check "Paid Enrollments" after Run. */
function testAppendPaidEnrollmentRow() {
  var nums = allocateReceiptNumbers_({
    stripeSessionId: "cs_test_sample_" + Date.now(),
  });
  var rowNum = writePaidEnrollmentRow_({
    submittedAt: new Date().toISOString(),
    stripeSessionId: "cs_test_sample",
    paymentIntent: "pi_test_sample",
    invoiceNo: nums.invoiceNo,
    orderRef: nums.orderRef,
    receiptNumber: nums.invoiceNo,
    first: "Paid",
    last: "Sample",
    email: "paid-sample@example.com",
    phone: "+91 98765 43210",
    course: "Claude AI Masterclass",
    intakeLabel: "28–29 Nov 2026",
    trainingMode: "Live Online",
    amountLabel: "RM 599",
    currency: "MYR",
    paymentMethod: "Visa ending 4242",
    paymentStatus: "paid",
    pageUrl: "https://www.nexpertsacademy.com/courses/claude-ai-productivity-90-minutes",
    source: "stripe-checkout",
  });
  Logger.log(
    "Wrote row " + rowNum + " to " + PAID_SHEET_NAME + " " + nums.invoiceNo
  );
}

/** Manual: allocate next receipt numbers. */
function testAllocateReceipt() {
  var nums = allocateReceiptNumbers_({
    stripeSessionId: "cs_manual_" + Date.now(),
  });
  Logger.log(JSON.stringify(nums));
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

function ensurePaidHeaders_(sh) {
  if (sh.getLastRow() === 0) {
    setupPaidEnrollmentsHeaders();
    return;
  }
  var first = String(sh.getRange(1, 1).getValue() || "");
  if (!first) {
    setupPaidEnrollmentsHeaders();
    return;
  }
  // Upgrade header row in place when older 14-col layout is detected (no Invoice No).
  var header = sh.getRange(1, 1, 1, Math.max(sh.getLastColumn(), PAID_COL_COUNT)).getValues()[0];
  var joined = header.join(" | ").toLowerCase();
  if (joined.indexOf("invoice no") < 0) {
    sh.getRange(1, 1, 1, PAID_COL_COUNT).setValues([paidEnrollmentHeaders_()]);
  }
}

function nextDataRowIndex_(sh) {
  if (sh.getLastRow() === 0) {
    if (sh.getName() === SHEET_NAME) {
      setupSheetHeaders();
    } else if (sh.getName() === PAID_SHEET_NAME) {
      setupPaidEnrollmentsHeaders();
    } else if (sh.getName() === RECEIPT_INDEX_NAME) {
      setupReceiptIndexHeaders();
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

function buildPaidRowArray_(data) {
  return [
    escapeSheetCell_(data.submittedAt || data.paidAt || new Date().toISOString()),
    escapeSheetCell_(data.invoiceNo || data.receiptNumber || ""),
    escapeSheetCell_(data.orderRef || ""),
    escapeSheetCell_(data.stripeSessionId || data.sessionId || ""),
    escapeSheetCell_(data.paymentIntent || ""),
    escapeSheetCell_(data.first || ""),
    escapeSheetCell_(data.last || ""),
    escapeSheetCell_(data.email || ""),
    trim_(data.phone),
    escapeSheetCell_(data.course || ""),
    escapeSheetCell_(data.intakeLabel || data.intake || ""),
    escapeSheetCell_(data.trainingMode || data.mode || ""),
    escapeSheetCell_(data.amountLabel || data.amount || ""),
    escapeSheetCell_(data.currency || "MYR"),
    escapeSheetCell_(data.paymentMethod || "Card (Stripe)"),
    escapeSheetCell_(data.paymentStatus || "paid"),
    escapeSheetCell_(data.pageUrl || ""),
    escapeSheetCell_(data.source || "stripe-checkout"),
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

/**
 * If this Stripe session id was already logged, return that row instead of appending.
 * Locates the "Stripe Session ID" column from the header row.
 */
function findPaidRowBySessionId_(sh, sessionId) {
  var id = trim_(sessionId);
  if (!id) return 0;
  var last = sh.getLastRow();
  if (last < 2) return 0;
  var lastCol = Math.max(sh.getLastColumn(), 1);
  var headers = sh.getRange(1, 1, 1, lastCol).getValues()[0];
  var col = 4; // default for new layout
  for (var h = 0; h < headers.length; h++) {
    if (String(headers[h] || "").toLowerCase() === "stripe session id") {
      col = h + 1;
      break;
    }
  }
  var values = sh.getRange(2, col, last, col).getValues();
  for (var i = 0; i < values.length; i++) {
    if (trim_(values[i][0]) === id) return i + 2;
  }
  return 0;
}

function padSeq6_(n) {
  var s = String(Math.max(0, Number(n) || 0));
  while (s.length < 6) s = "0" + s;
  return s.slice(-6);
}

/**
 * Allocate NXA-RCP-YYYY-###### and NXA-ORD-YYYY-###### atomically.
 * Reuses an existing assignment for the same Stripe session id.
 */
function allocateReceiptNumbers_(data) {
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    setupReceiptIndexHeaders();
    var sessionId = trim_(data.stripeSessionId || data.sessionId || "");
    var index = getOrCreateSheet_(RECEIPT_INDEX_NAME);
    if (sessionId && index.getLastRow() >= 2) {
      var existing = index.getRange(2, 1, index.getLastRow(), RECEIPT_INDEX_COLS).getValues();
      for (var i = 0; i < existing.length; i++) {
        if (trim_(existing[i][5]) === sessionId) {
          return {
            invoiceNo: trim_(existing[i][3]),
            orderRef: trim_(existing[i][4]),
            year: trim_(existing[i][1]),
            seq: Number(existing[i][2]) || 0,
            reused: true,
          };
        }
      }
    }

    var year = String(new Date().getFullYear());
    var props = PropertiesService.getScriptProperties();
    var key = "RECEIPT_SEQ_" + year;
    var next = parseInt(props.getProperty(key) || "0", 10) + 1;
    if (!isFinite(next) || next < 1) next = 1;
    props.setProperty(key, String(next));
    var seq = padSeq6_(next);
    var invoiceNo = "NXA-RCP-" + year + "-" + seq;
    var orderRef = "NXA-ORD-" + year + "-" + seq;

    index.appendRow([
      new Date().toISOString(),
      year,
      next,
      invoiceNo,
      orderRef,
      sessionId,
    ]);

    return {
      invoiceNo: invoiceNo,
      orderRef: orderRef,
      year: year,
      seq: next,
      reused: false,
    };
  } finally {
    lock.releaseLock();
  }
}

function writePaidEnrollmentRow_(data) {
  var sh = getOrCreateSheet_(PAID_SHEET_NAME);
  ensurePaidHeaders_(sh);
  var existing = findPaidRowBySessionId_(
    sh,
    data.stripeSessionId || data.sessionId || ""
  );
  if (existing) {
    return existing;
  }
  var row = buildPaidRowArray_(data);
  if (row.length !== PAID_COL_COUNT) {
    throw new Error("paid_row_length_mismatch");
  }
  var r = nextDataRowIndex_(sh);
  var range = sh.getRange(r, 1, 1, PAID_COL_COUNT);
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
        trim_(log.source) + (log.sheet ? " → " + log.sheet : ""),
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
