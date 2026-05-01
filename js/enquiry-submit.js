/**
 * Shared enquiry submitter — used by contact.html and index.html (modal).
 * Posts to Google Apps Script Web App (see js/enquiry-config.js).
 */
(function (global) {
  "use strict";

  function getConfig() {
    const c = global.NEXPERTS_ENQUIRY_CONFIG || {};
    return {
      webAppUrl: String(c.webAppUrl || "").trim(),
      secret: String(c.secret || "").trim(),
    };
  }

  function fieldValue(form, name) {
    const el = form.elements.namedItem(name);
    if (!el) return "";
    if (el instanceof RadioNodeList) {
      return String(el.value || "").trim();
    }
    if ("value" in el) return String(el.value || "").trim();
    return "";
  }

  /**
   * @param {HTMLFormElement} form
   * @param {{ source: string }} meta
   */
  function buildPayload(form, meta) {
    const payload = {
      first: fieldValue(form, "first"),
      last: fieldValue(form, "last"),
      email: fieldValue(form, "email"),
      phone: fieldValue(form, "phone"),
      office: fieldValue(form, "office"),
      course: fieldValue(form, "course"),
      type: fieldValue(form, "type"),
      message: fieldValue(form, "message"),
      source: meta.source || "unknown",
      pageUrl: global.location.href,
      userAgent: global.navigator.userAgent || "",
      submittedAt: new Date().toISOString(),
    };
    const cfg = getConfig();
    if (cfg.secret) payload.secret = cfg.secret;
    return payload;
  }

  /**
   * Apps Script receives application/x-www-form-urlencoded with key "payload".
   * We use mode:no-cors so the browser does not require CORS headers from Google.
   * (The script still runs; we cannot read the response body in this mode.)
   */
  function postToAppsScript(url, payload) {
    const body = new URLSearchParams();
    body.set("payload", JSON.stringify(payload));
    return global.fetch(url, {
      method: "POST",
      mode: "no-cors",
      cache: "no-store",
      body,
    });
  }

  /**
   * @param {HTMLFormElement} form
   * @param {{ source: string }} meta
   * @returns {Promise<void>}
   */
  async function submitNexpertsEnquiry(form, meta) {
    const cfg = getConfig();
    if (!cfg.webAppUrl || !/^https:\/\/script\.google\.com\//.test(cfg.webAppUrl)) {
      throw new Error(
        "Enquiry endpoint is not configured. Paste your Web App URL into js/enquiry-config.js (webAppUrl)."
      );
    }
    const payload = buildPayload(form, meta);
    if (!payload.first || !payload.last || !payload.email) {
      throw new Error("Please fill in your name and email.");
    }
    await postToAppsScript(cfg.webAppUrl, payload);
  }

  global.NexpertsEnquiry = {
    submit: submitNexpertsEnquiry,
    buildPayload,
  };
})(window);
