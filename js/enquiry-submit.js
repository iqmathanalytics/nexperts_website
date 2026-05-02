/**
 * Shared enquiry submitter — contact.html + index modal.
 * Providers: Google Apps Script (legacy) or Brevo via Netlify Function.
 * Configure js/enquiry-config.js (provider, endpoints, secret).
 */
(function (global) {
  "use strict";

  function getConfig() {
    const c = global.NEXPERTS_ENQUIRY_CONFIG || {};
    return {
      provider: String(c.provider || "apps_script").toLowerCase().trim(),
      webAppUrl: String(c.webAppUrl || "").trim(),
      brevoEndpoint: String(c.brevoEndpoint || "/.netlify/functions/enquiry-brevo").trim(),
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
   * Apps Script: application/x-www-form-urlencoded, no-cors (response not readable).
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

  function resolveBrevoUrl(endpoint) {
    const e = String(endpoint || "").trim();
    if (!e) return "";
    if (/^https?:\/\//i.test(e)) return e;
    try {
      return new URL(e, global.location.origin).href;
    } catch {
      return e;
    }
  }

  /**
   * Brevo path: JSON POST to Netlify function (same origin on Netlify).
   */
  async function postToBrevo(endpoint, payload) {
    const url = resolveBrevoUrl(endpoint);
    if (!url) {
      throw new Error("Brevo endpoint is not configured. Set brevoEndpoint in js/enquiry-config.js.");
    }
    const res = await global.fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      mode: "cors",
      cache: "no-store",
    });
    let data = null;
    try {
      data = await res.json();
    } catch (_) {
      data = null;
    }
    if (!res.ok) {
      const msg =
        (data && (data.detail || data.error || data.hint)) ||
        "Could not send your enquiry. Please try again or email enquiry@nexpertsacademy.com.";
      throw new Error(String(msg));
    }
    if (data && data.ok === false) {
      throw new Error(String(data.error || "Enquiry rejected."));
    }
  }

  /**
   * @param {HTMLFormElement} form
   * @param {{ source: string }} meta
   * @returns {Promise<void>}
   */
  async function submitNexpertsEnquiry(form, meta) {
    const cfg = getConfig();
    const payload = buildPayload(form, meta);
    if (!payload.first || !payload.last || !payload.email) {
      throw new Error("Please fill in your name and email.");
    }

    const useBrevo = cfg.provider === "brevo";

    if (useBrevo) {
      await postToBrevo(cfg.brevoEndpoint, payload);
      return;
    }

    if (!cfg.webAppUrl || !/^https:\/\/script\.google\.com\//.test(cfg.webAppUrl)) {
      throw new Error(
        "Enquiry endpoint is not configured. Use provider \"brevo\" with Netlify, or set webAppUrl in js/enquiry-config.js for Apps Script."
      );
    }
    await postToAppsScript(cfg.webAppUrl, payload);
  }

  global.NexpertsEnquiry = {
    submit: submitNexpertsEnquiry,
    buildPayload,
  };
})(window);
