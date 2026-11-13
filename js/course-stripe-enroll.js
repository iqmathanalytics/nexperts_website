/**
 * Stripe Register & Pay — Agentic AI + Claude Masterclass only.
 */
(function (global) {
  "use strict";

  var COURSE_CONFIG = {
    "agentic-ai": {
      intakes: [
        {
          id: "2026-11-16",
          label: "16 Nov 2026 – 2 Jan 2027 (Mon · Wed · Fri · 6pm–10pm)",
        },
      ],
    },
    "claude-ai-productivity-90-minutes": {
      intakes: [
        { id: "2026-11-28", label: "28–29 Nov 2026 · 2 days · 9am–5pm" },
      ],
    },
  };

  function checkoutUrls() {
    try {
      var h = (location.hostname || "").toLowerCase();
      if (h.endsWith(".netlify.app") || h === "localhost" || h === "127.0.0.1") {
        return ["/.netlify/functions/stripe-checkout", "/api/stripe-checkout"];
      }
    } catch (_) {
      /* ignore */
    }
    return ["/api/stripe-checkout", "/.netlify/functions/stripe-checkout"];
  }

  function fillIntakes(select, slug) {
    if (!select) return;
    var cfg = COURSE_CONFIG[slug];
    select.innerHTML = "";
    if (!cfg || !cfg.intakes.length) return;
    cfg.intakes.forEach(function (intake, i) {
      var opt = document.createElement("option");
      opt.value = intake.id;
      opt.textContent = intake.label;
      if (i === 0) opt.selected = true;
      select.appendChild(opt);
    });
  }

  function phoneFromForm(form) {
    var ccEl = form.elements.namedItem("phoneCountry");
    var numEl = form.elements.namedItem("phone");
    var cc = (ccEl && ccEl.value ? String(ccEl.value) : "+60").trim() || "+60";
    var num = (numEl && numEl.value ? String(numEl.value) : "").replace(/\s+/g, "").trim();
    if (!num) return "";
    if (num.charAt(0) === "+") return num;
    return cc + num.replace(/^0+/, "");
  }

  function setBusy(form, busy) {
    var btn = form.querySelector(".cse-submit");
    if (btn) {
      btn.disabled = !!busy;
      btn.setAttribute("aria-busy", busy ? "true" : "false");
      if (busy) {
        btn.dataset.cseLabel = btn.dataset.cseLabel || btn.textContent;
        btn.textContent = "Redirecting to payment…";
      } else if (btn.dataset.cseLabel) {
        btn.textContent = btn.dataset.cseLabel;
      }
    }
  }

  function showError(wrap, msg) {
    var err = wrap.querySelector(".course-enroll-err");
    if (!err) return;
    err.textContent = msg || "";
    err.hidden = !msg;
  }

  function friendlyCheckoutError(code) {
    var c = String(code || "").toLowerCase();
    if (
      c === "stripe_not_configured" ||
      c.indexOf("not_configured") >= 0 ||
      c.indexOf("not configured") >= 0
    ) {
      return "Payment option is currently unavailable. Please enquire instead, or contact us for assistance.";
    }
    if (c === "course_not_enrollable" || c === "invalid_intake" || c === "invalid_training_mode") {
      return "Online payment is not available for this selection. Please enquire instead.";
    }
    if (c === "name_required" || c === "email_invalid" || c === "phone_required") {
      return "Please check your details and try again.";
    }
    // Never surface raw API/HTTP/network strings to learners.
    return "Payment option is currently unavailable. Please enquire instead, or contact us for assistance.";
  }

  async function createCheckout(payload) {
    var urls = checkoutUrls();
    var lastCode = "checkout_failed";
    for (var i = 0; i < urls.length; i++) {
      try {
        var res = await fetch(urls[i], {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify(payload),
        });
        var data = null;
        try {
          data = await res.json();
        } catch (_) {
          data = null;
        }
        if (res.ok && data && data.url) return data;
        lastCode = (data && data.error) || "checkout_failed";
        if (res.status === 404 || res.status === 405) continue;
        break;
      } catch (e) {
        lastCode = "network_error";
      }
    }
    throw new Error(lastCode);
  }

  function bindEnroll(wrap) {
    if (!wrap || wrap.dataset.nxEnrollBound === "1") return;
    wrap.dataset.nxEnrollBound = "1";

    var slug = String(wrap.getAttribute("data-nx-course-slug") || "").trim();
    var form = wrap.querySelector(".course-enroll-form");
    var intakeSel = form && form.querySelector('select[name="intakeId"]');
    fillIntakes(intakeSel, slug);

    var enquireWrap = wrap.parentElement && wrap.parentElement.querySelector(".course-sidebar-enquiry");
    var toggleEnquire = wrap.querySelector(".cse-toggle-enquire");
    var togglePay = enquireWrap && enquireWrap.querySelector(".cse-toggle-pay");

    function showEnquire() {
      wrap.hidden = true;
      if (enquireWrap) enquireWrap.hidden = false;
    }
    function showPay() {
      if (enquireWrap) enquireWrap.hidden = true;
      wrap.hidden = false;
    }

    if (toggleEnquire) {
      toggleEnquire.addEventListener("click", function (e) {
        e.preventDefault();
        showEnquire();
      });
    }
    if (togglePay) {
      togglePay.addEventListener("click", function (e) {
        e.preventDefault();
        showPay();
      });
    }

    if (enquireWrap && !togglePay) {
      var heading = enquireWrap.querySelector(".cef-heading");
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "cse-toggle-pay";
      btn.textContent = "← Back to Register & Pay";
      if (heading && heading.parentNode) {
        heading.parentNode.insertBefore(btn, heading.nextSibling);
      } else {
        enquireWrap.insertBefore(btn, enquireWrap.firstChild);
      }
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        showPay();
      });
    }

    // Default: pay form visible, enquire secondary
    if (enquireWrap) enquireWrap.hidden = true;

    if (!form) return;

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      showError(wrap, "");

      var firstName = String((form.elements.namedItem("first") || {}).value || "").trim();
      var lastName = String((form.elements.namedItem("last") || {}).value || "").trim();
      var email = String((form.elements.namedItem("email") || {}).value || "").trim();
      var phone = phoneFromForm(form);
      var intakeId = String((form.elements.namedItem("intakeId") || {}).value || "").trim();
      var trainingMode = String((form.elements.namedItem("trainingMode") || {}).value || "").trim();

      if (!firstName || !lastName) {
        showError(wrap, "Please enter your first and last name.");
        return;
      }
      if (!email || email.indexOf("@") < 1) {
        showError(wrap, "Please enter a valid email address.");
        return;
      }
      if (!phone || phone.replace(/\D/g, "").length < 8) {
        showError(wrap, "Please enter a valid phone / WhatsApp number.");
        return;
      }
      if (!intakeId) {
        showError(wrap, "Please select an intake.");
        return;
      }
      if (!trainingMode) {
        showError(wrap, "Please select a training mode.");
        return;
      }

      setBusy(form, true);
      createCheckout({
        courseSlug: slug,
        firstName: firstName,
        lastName: lastName,
        email: email,
        phone: phone,
        intakeId: intakeId,
        trainingMode: trainingMode,
      })
        .then(function (data) {
          global.location.href = data.url;
        })
        .catch(function (err) {
          setBusy(form, false);
          showError(wrap, friendlyCheckoutError(err && err.message));
        });
    });
  }

  function init() {
    global.document.querySelectorAll(".course-stripe-enroll").forEach(bindEnroll);
  }

  if (global.document) {
    if (global.document.readyState === "loading") {
      global.document.addEventListener("DOMContentLoaded", init);
    } else {
      init();
    }
  }
})(window);
