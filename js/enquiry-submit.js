/**
 * Shared enquiry submitter — contact.html + index modal + any page that loads this script.
 * Providers: Google Apps Script (direct) or Brevo via Netlify Function.
 * Configure js/enquiry-config.js (provider, endpoints, secret).
 *
 * Local development: on localhost / 127.0.0.1 / ::1 / file (empty host), the effective provider
 * becomes `apps_script` so forms hit Google directly (no `/.netlify/functions/`). Production hostnames
 * keep `provider` from config. To test Brevo + Netlify locally, run `npm run dev` and open any page with
 * `?enquiry=brevo`, or set `localProvider: "brevo"` on `NEXPERTS_ENQUIRY_CONFIG`.
 */
(function (global) {
  "use strict";

  function isLocalDevelopmentHost() {
    const h = String(global.location && global.location.hostname ? global.location.hostname : "")
      .toLowerCase();
    if (!h || h === "localhost" || h === "127.0.0.1" || h === "[::1]" || h === "0.0.0.0") {
      return true;
    }
    if (h.endsWith(".local") || h.endsWith(".localhost")) return true;
    return false;
  }

  /** User wants Netlify + Brevo on a local machine (e.g. netlify dev). */
  function explicitLocalBrevo_(c) {
    try {
      if (String((c && c.localProvider) || "").toLowerCase().trim() === "brevo") {
        return true;
      }
      const q = new URLSearchParams(global.location.search || "");
      return String(q.get("enquiry") || "").toLowerCase() === "brevo";
    } catch (_) {
      return false;
    }
  }

  function forceAppsScriptOnLocal_(c) {
    return isLocalDevelopmentHost() && !explicitLocalBrevo_(c);
  }

  function looksLikeEmail(s) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(s || "").trim());
  }

  /** Public inbox for mailto + error hints — keep in sync with BREVO_INTERNAL_TO on Netlify. */
  function getTeamInbox() {
    const c = global.NEXPERTS_ENQUIRY_CONFIG || {};
    const e = String(c.teamInbox || "").trim();
    return looksLikeEmail(e) ? e : "";
  }

  function enquiryFallbackHint() {
    const m = getTeamInbox();
    return m
      ? `Could not send your enquiry. Please try again or email ${m}.`
      : "Could not send your enquiry. Please try again or use the address on our Contact page.";
  }

  /** Cloudflare Pages uses `/api/enquiry-brevo`; Netlify uses `/.netlify/functions/enquiry-brevo`. */
  function defaultBrevoEndpoint_() {
    try {
      const h = String(global.location && global.location.hostname ? global.location.hostname : "")
        .toLowerCase();
      if (h.endsWith(".netlify.app")) return "/.netlify/functions/enquiry-brevo";
    } catch (_) {
      /* ignore */
    }
    return "/api/enquiry-brevo";
  }

  function getConfig() {
    const c = global.NEXPERTS_ENQUIRY_CONFIG || {};
    let provider = String(c.provider || "apps_script").toLowerCase().trim();
    if (forceAppsScriptOnLocal_(c)) {
      provider = "apps_script";
    }
    const explicitEndpoint = String(c.brevoEndpoint || "").trim();
    return {
      provider,
      webAppUrl: String(c.webAppUrl || "").trim(),
      brevoEndpoint: explicitEndpoint || defaultBrevoEndpoint_(),
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

  /** Full E.164-style phone when country select is present; else legacy single field. */
  function combineInternationalPhone(form) {
    const ccEl = form.elements.namedItem("phoneCountry");
    if (!ccEl) return fieldValue(form, "phone");
    const cc = String(fieldValue(form, "phoneCountry") || "+60").trim() || "+60";
    let num = String(fieldValue(form, "phone") || "").trim();
    if (!num) return "";
    if (/^\+/.test(num)) return num.replace(/\s+/g, " ").trim();
    return (cc + " " + num).replace(/\s+/g, " ").trim();
  }

  /**
   * Relative path to the course detail page (e.g. course_pages/ceh-v13-ai.html) for email "View curriculum".
   * Prefer the course dropdown (data-curriculum on <option>); else use current URL if already on a course page.
   */
  function curriculumPageFromForm_(form) {
    let fromSelect = "";
    try {
      const courseEl = form && form.elements ? form.elements.namedItem("course") : null;
      if (courseEl && courseEl.options && courseEl.selectedIndex >= 0) {
        const opt = courseEl.options[courseEl.selectedIndex];
        if (opt) {
          fromSelect = String(
            opt.getAttribute("data-curriculum") || opt.dataset.curriculum || ""
          ).trim();
        }
      }
    } catch (_) {
      /* ignore */
    }
    let fromPath = "";
    try {
      const p = new URL(global.location.href).pathname || "";
      if (/\/course_pages\/[^/]+\.html$/i.test(p)) {
        fromPath = p.replace(/^\//, "");
      }
    } catch (_) {
      /* ignore */
    }
    return fromSelect || fromPath;
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
      phone: combineInternationalPhone(form),
      office: fieldValue(form, "office"),
      course: fieldValue(form, "course"),
      type: fieldValue(form, "type"),
      message: fieldValue(form, "message"),
      source: meta.source || "unknown",
      pageUrl: global.location.href,
      userAgent: global.navigator.userAgent || "",
      submittedAt: new Date().toISOString(),
      curriculumPage: curriculumPageFromForm_(form),
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
      let msg = (data && (data.hint || data.detail || data.error)) || enquiryFallbackHint();
      if (data && data.error === "forbidden") {
        msg =
          data.hint ||
          "Secret mismatch: set js/enquiry-config.js secret to match Netlify BREVO_ENQUIRY_SECRET, or clear BREVO_ENQUIRY_SECRET on Netlify.";
      }
      throw new Error(String(msg));
    }
    if (data && data.ok === false) {
      let msg2 = data.hint || data.error || "Enquiry rejected.";
      if (data.error === "forbidden") {
        msg2 =
          data.hint ||
          "Secret mismatch between the website and Netlify. Check enquiry-config.js and BREVO_ENQUIRY_SECRET.";
      }
      throw new Error(String(msg2));
    }
  }

  function setFormSending(form, on) {
    if (!form) return;
    const btn = form.querySelector('button[type="submit"]');
    if (!btn) return;
    btn.classList.toggle("nexperts-enquiry-sending", on);
    btn.disabled = on;
    btn.setAttribute("aria-busy", on ? "true" : "false");
    if (on) {
      if (!btn.dataset.nexpertsSubmitHtml) {
        btn.dataset.nexpertsSubmitHtml = btn.innerHTML;
      }
      btn.innerHTML =
        '<span class="nexperts-enquiry-submit-inner"><span class="nexperts-enquiry-spinner" aria-hidden="true"></span><span class="nexperts-enquiry-send-label">Sending…</span></span>';
    } else if (btn.dataset.nexpertsSubmitHtml) {
      btn.innerHTML = btn.dataset.nexpertsSubmitHtml;
      delete btn.dataset.nexpertsSubmitHtml;
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

    setFormSending(form, true);
    try {
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
    } finally {
      setFormSending(form, false);
    }
  }

  function hydrateTeamInboxInDom() {
    const email = getTeamInbox();
    if (!email || !global.document) return;
    try {
      global.document.querySelectorAll("a.nexperts-team-inbox").forEach((a) => {
        a.setAttribute("href", "mailto:" + email);
        const lab = a.querySelector(".nexperts-team-inbox-label");
        if (lab) lab.textContent = email;
      });
    } catch (_) {
      /* ignore */
    }
  }

  if (global.document) {
    if (global.document.readyState === "loading") {
      global.document.addEventListener("DOMContentLoaded", hydrateTeamInboxInDom);
    } else {
      hydrateTeamInboxInDom();
    }
  }

  global.NexpertsEnquiry = {
    submit: submitNexpertsEnquiry,
    buildPayload,
    getTeamInbox,
    /** Resolved provider/endpoints after local-dev rules — useful in DevTools. */
    getEffectiveConfig: getConfig,
  };
})(window);
