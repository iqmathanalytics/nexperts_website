/**
 * Stripe Register & Pay — Agentic AI + Claude Masterclass only.
 * Pay opens Stripe Checkout in a popup; a modal on this page covers waiting /
 * success / cancelled / failed so browser Back on Stripe never dumps users home.
 */
(function (global) {
  "use strict";

  var COURSE_CONFIG = {
    "agentic-ai": {
      amountRm: 799,
      intakes: [
        {
          id: "2026-11-16",
          label: "16 Nov 2026 – 2 Jan 2027 (Mon · Wed · Fri · 6pm–10pm)",
        },
      ],
    },
    "claude-ai-productivity-90-minutes": {
      amountRm: 599,
      intakes: [
        { id: "2026-11-28", label: "28–29 Nov 2026 · 2 days · 9am–5pm" },
      ],
    },
  };

  var MSG_SOURCE = "nexperts-stripe-checkout";
  var POLL_MS = 2000;
  var POLL_MAX = 150; // ~5 minutes

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

  function fulfillUrls() {
    try {
      var h = (location.hostname || "").toLowerCase();
      if (h.endsWith(".netlify.app") || h === "localhost" || h === "127.0.0.1") {
        return ["/.netlify/functions/stripe-fulfill", "/api/stripe-fulfill"];
      }
    } catch (_) {
      /* ignore */
    }
    return ["/api/stripe-fulfill", "/.netlify/functions/stripe-fulfill"];
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

  function payButtonHtml(label) {
    return String(label || "Pay") + ' <span aria-hidden="true">→</span>';
  }

  function syncPayButton(wrap) {
    if (!wrap) return;
    var btn = wrap.querySelector(".cse-submit");
    if (!btn) return;
    var card = wrap.closest(".enroll-card") || wrap.parentElement;
    var priceEl = card && card.querySelector(".price");
    var priceText = priceEl ? String(priceEl.textContent || "").replace(/\s+/g, " ").trim() : "";
    var cfg = COURSE_CONFIG[String(wrap.getAttribute("data-nx-course-slug") || "").trim()];
    var label = "";
    if (priceText && !/^enquire\b/i.test(priceText) && /\d/.test(priceText)) {
      label = "Pay " + priceText;
    } else if (cfg && cfg.amountRm) {
      label = "Pay RM " + cfg.amountRm;
    } else {
      label = btn.dataset.cseLabel || "Pay";
    }
    btn.dataset.cseLabel = label;
    if (btn.getAttribute("aria-busy") === "true") return;
    btn.innerHTML = payButtonHtml(label);
  }

  function setBusy(form, busy) {
    var btn = form.querySelector(".cse-submit");
    if (btn) {
      btn.disabled = !!busy;
      btn.setAttribute("aria-busy", busy ? "true" : "false");
      if (busy) {
        btn.dataset.cseLabel = btn.dataset.cseLabel || (btn.textContent || "").replace(/\s+/g, " ").trim();
        btn.textContent = "Opening payment…";
      } else if (btn.dataset.cseLabel) {
        btn.innerHTML = payButtonHtml(btn.dataset.cseLabel);
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
    if (c === "popup_blocked") {
      return "Your browser blocked the payment window. Please allow pop-ups for this site and try again.";
    }
    return "Payment option is currently unavailable. Please enquire instead, or contact us for assistance.";
  }

  async function postJson(urls, payload) {
    var lastCode = "request_failed";
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
        if (res.ok && data) return data;
        lastCode = (data && data.error) || "request_failed";
        if (res.status === 404 || res.status === 405) continue;
        if (data) {
          var err = new Error(lastCode);
          err.data = data;
          err.status = res.status;
          throw err;
        }
        break;
      } catch (e) {
        if (e && e.data) throw e;
        lastCode = "network_error";
      }
    }
    throw new Error(lastCode);
  }

  function createCheckout(payload) {
    return postJson(checkoutUrls(), payload);
  }

  function fetchSessionStatus(sessionId) {
    return postJson(fulfillUrls(), { session_id: sessionId, status_only: true });
  }

  function fulfillSession(sessionId) {
    return postJson(fulfillUrls(), { session_id: sessionId });
  }

  function ensureModal() {
    var el = global.document.getElementById("nx-pay-modal");
    if (el) return el;
    el = global.document.createElement("div");
    el.id = "nx-pay-modal";
    el.className = "nx-pay-modal";
    el.hidden = true;
    el.setAttribute("role", "dialog");
    el.setAttribute("aria-modal", "true");
    el.setAttribute("aria-labelledby", "nx-pay-modal-title");
    el.innerHTML =
      '<div class="nx-pay-modal__backdrop" data-nx-pay-dismiss="1"></div>' +
      '<div class="nx-pay-modal__panel">' +
      '<div class="nx-pay-modal__icon" id="nx-pay-modal-icon" aria-hidden="true"></div>' +
      '<h2 class="nx-pay-modal__title" id="nx-pay-modal-title"></h2>' +
      '<p class="nx-pay-modal__body" id="nx-pay-modal-body"></p>' +
      '<div class="nx-pay-modal__actions" id="nx-pay-modal-actions"></div>' +
      "</div>";
    global.document.body.appendChild(el);
    return el;
  }

  function setModalState(state) {
    var el = ensureModal();
    var icon = el.querySelector("#nx-pay-modal-icon");
    var title = el.querySelector("#nx-pay-modal-title");
    var body = el.querySelector("#nx-pay-modal-body");
    var actions = el.querySelector("#nx-pay-modal-actions");
    el.hidden = false;
    el.dataset.state = state.id;
    global.document.documentElement.classList.add("nx-pay-modal-open");

    icon.className = "nx-pay-modal__icon nx-pay-modal__icon--" + (state.tone || "wait");
    icon.textContent = state.icon || "";
    title.textContent = state.title || "";
    body.textContent = state.body || "";
    actions.innerHTML = "";

    (state.actions || []).forEach(function (a) {
      var btn = global.document.createElement("button");
      btn.type = "button";
      btn.className = "nx-pay-modal__btn" + (a.primary ? " nx-pay-modal__btn--primary" : "");
      btn.textContent = a.label;
      btn.addEventListener("click", function () {
        if (typeof a.onClick === "function") a.onClick();
      });
      actions.appendChild(btn);
    });
  }

  function closeModal() {
    var el = global.document.getElementById("nx-pay-modal");
    if (el) {
      el.hidden = true;
      el.dataset.state = "";
    }
    global.document.documentElement.classList.remove("nx-pay-modal-open");
  }

  function popupFeatures() {
    var w = Math.min(520, Math.max(420, Math.floor((global.screen && global.screen.width) || 520) * 0.9));
    var h = Math.min(760, Math.max(640, Math.floor((global.screen && global.screen.height) || 760) * 0.85));
    var left = Math.max(0, Math.floor(((global.screen && global.screen.width) || w) - w) / 2);
    var top = Math.max(0, Math.floor(((global.screen && global.screen.height) || h) - h) / 2);
    return (
      "popup=yes,noopener=no,noreferrer=no,width=" +
      w +
      ",height=" +
      h +
      ",left=" +
      left +
      ",top=" +
      top +
      ",scrollbars=yes,resizable=yes"
    );
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

    var active = {
      sessionId: "",
      popup: null,
      pollTimer: null,
      pollCount: 0,
      settled: false,
      messageHandler: null,
    };

    function showEnquire() {
      wrap.hidden = true;
      if (enquireWrap) enquireWrap.hidden = false;
    }
    function showPayForm() {
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
        showPayForm();
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
        showPayForm();
      });
    }

    if (enquireWrap) enquireWrap.hidden = true;

    syncPayButton(wrap);
    var card = wrap.closest(".enroll-card") || wrap.parentElement;
    var priceEl = card && card.querySelector(".price");
    if (priceEl && typeof MutationObserver !== "undefined") {
      var mo = new MutationObserver(function () {
        syncPayButton(wrap);
      });
      mo.observe(priceEl, { childList: true, characterData: true, subtree: true });
    }
    var tries = 0;
    var pollBtn = global.setInterval(function () {
      syncPayButton(wrap);
      tries += 1;
      if (tries >= 20) global.clearInterval(pollBtn);
    }, 250);

    function stopWatching() {
      if (active.pollTimer) {
        global.clearInterval(active.pollTimer);
        active.pollTimer = null;
      }
      if (active.messageHandler) {
        global.removeEventListener("message", active.messageHandler);
        active.messageHandler = null;
      }
    }

    function closePopupQuietly() {
      try {
        if (active.popup && !active.popup.closed) active.popup.close();
      } catch (_) {
        /* ignore */
      }
      active.popup = null;
    }

    function resetFlow() {
      stopWatching();
      closePopupQuietly();
      active.sessionId = "";
      active.settled = false;
      active.pollCount = 0;
      if (form) setBusy(form, false);
      closeModal();
    }

    function showCancelled() {
      if (active.settled) return;
      active.settled = true;
      stopWatching();
      closePopupQuietly();
      if (form) setBusy(form, false);
      setModalState({
        id: "cancelled",
        tone: "warn",
        icon: "!",
        title: "Payment cancelled",
        body: "No charge was made. You can try again whenever you are ready, or enquire instead.",
        actions: [
          {
            label: "Try again",
            primary: true,
            onClick: function () {
              closeModal();
            },
          },
          {
            label: "Enquire instead",
            onClick: function () {
              closeModal();
              showEnquire();
            },
          },
        ],
      });
    }

    function showFailed(message) {
      if (active.settled) return;
      active.settled = true;
      stopWatching();
      closePopupQuietly();
      if (form) setBusy(form, false);
      setModalState({
        id: "failed",
        tone: "error",
        icon: "×",
        title: "Payment could not be completed",
        body: message || "Something went wrong while confirming payment. Please try again or enquire for help.",
        actions: [
          {
            label: "Try again",
            primary: true,
            onClick: function () {
              closeModal();
            },
          },
          {
            label: "Enquire instead",
            onClick: function () {
              closeModal();
              showEnquire();
            },
          },
        ],
      });
    }

    function showSuccess() {
      if (active.settled) return;
      active.settled = true;
      stopWatching();
      closePopupQuietly();
      if (form) setBusy(form, false);
      setModalState({
        id: "success",
        tone: "ok",
        icon: "✓",
        title: "Payment successful",
        body: "Your seat is confirmed. A confirmation email with your PDF receipt is on the way — please also check spam or promotions.",
        actions: [
          {
            label: "Done",
            primary: true,
            onClick: function () {
              closeModal();
            },
          },
        ],
      });
    }

    function markPaidAndFulfill(sessionId) {
      setModalState({
        id: "confirming",
        tone: "wait",
        icon: "",
        title: "Confirming payment…",
        body: "Please wait while we confirm your enrollment and send your receipt.",
        actions: [],
      });
      fulfillSession(sessionId)
        .then(function () {
          showSuccess();
        })
        .catch(function (err) {
          // Payment may still have succeeded; avoid alarming if status was paid.
          if (err && err.status === 402) {
            showFailed("Payment is still processing. If you were charged, contact us with your email and we will confirm your seat.");
            return;
          }
          showSuccess();
        });
    }

    function handleStatus(data) {
      if (!data || active.settled) return;
      var pay = String(data.payment_status || "").toLowerCase();
      var st = String(data.status || "").toLowerCase();
      if (pay === "paid") {
        markPaidAndFulfill(data.sessionId || active.sessionId);
        return true;
      }
      if (st === "expired") {
        showFailed("This payment session expired. Please try again.");
        return true;
      }
      return false;
    }

    function startPolling(sessionId) {
      active.pollCount = 0;
      if (active.pollTimer) global.clearInterval(active.pollTimer);
      active.pollTimer = global.setInterval(function () {
        if (active.settled) {
          stopWatching();
          return;
        }
        active.pollCount += 1;
        if (active.pollCount > POLL_MAX) {
          showFailed("We could not confirm payment in time. If you were charged, contact us and we will help.");
          return;
        }
        try {
          if (active.popup && active.popup.closed && !active.settled) {
            // Popup closed — one more status check, then treat as cancel if unpaid.
            fetchSessionStatus(sessionId)
              .then(function (data) {
                if (handleStatus(data)) return;
                showCancelled();
              })
              .catch(function () {
                showCancelled();
              });
            return;
          }
        } catch (_) {
          /* ignore */
        }
        fetchSessionStatus(sessionId)
          .then(function (data) {
            handleStatus(data);
          })
          .catch(function () {
            /* keep waiting */
          });
      }, POLL_MS);
    }

    function watchPopupMessages(sessionId) {
      active.messageHandler = function (event) {
        try {
          if (!event || event.origin !== location.origin) return;
          var data = event.data;
          if (!data || data.source !== MSG_SOURCE) return;
          if (active.settled) return;
          if (data.session_id && sessionId && data.session_id !== sessionId) return;
          if (data.result === "success") {
            markPaidAndFulfill(data.session_id || sessionId);
          } else if (data.result === "cancel") {
            showCancelled();
          }
        } catch (_) {
          /* ignore */
        }
      };
      global.addEventListener("message", active.messageHandler);
    }

    ensureModal().addEventListener("click", function (e) {
      var t = e.target;
      if (!t || !t.getAttribute) return;
      if (t.getAttribute("data-nx-pay-dismiss") === "1") {
        var state = ensureModal().dataset.state;
        if (state === "waiting" || state === "opening" || state === "confirming") return;
        resetFlow();
      }
    });

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

      resetFlow();
      active.settled = false;

      // Open immediately from the user gesture so the browser allows the popup.
      var popup = null;
      try {
        popup = global.open("about:blank", "nx_stripe_pay", popupFeatures());
      } catch (_) {
        popup = null;
      }
      if (!popup) {
        showError(wrap, friendlyCheckoutError("popup_blocked"));
        return;
      }
      try {
        popup.document.write(
          "<!doctype html><title>Nexperts Academy</title><body style=\"font-family:system-ui;padding:24px;color:#334\">Preparing secure payment…</body>"
        );
        popup.document.close();
      } catch (_) {
        /* cross-write may fail; ok */
      }
      active.popup = popup;

      setBusy(form, true);
      setModalState({
        id: "opening",
        tone: "wait",
        icon: "",
        title: "Preparing secure payment…",
        body: "A Stripe payment window is opening. Keep this page open.",
        actions: [],
      });

      createCheckout({
        courseSlug: slug,
        firstName: firstName,
        lastName: lastName,
        email: email,
        phone: phone,
        intakeId: intakeId,
        trainingMode: trainingMode,
        returnMode: "popup",
      })
        .then(function (data) {
          if (!data || !data.url || !data.id) throw new Error("checkout_failed");
          active.sessionId = data.id;
          try {
            if (!popup || popup.closed) throw new Error("popup_blocked");
            popup.location = data.url;
          } catch (_) {
            throw new Error("popup_blocked");
          }
          setModalState({
            id: "waiting",
            tone: "wait",
            icon: "",
            title: "Complete payment in the Stripe window",
            body: "Finish checkout in the popup. This page will update automatically for success or cancel. Do not close this tab.",
            actions: [
              {
                label: "I cancelled / close",
                onClick: function () {
                  showCancelled();
                },
              },
            ],
          });
          watchPopupMessages(data.id);
          startPolling(data.id);
        })
        .catch(function (err) {
          try {
            if (popup && !popup.closed) popup.close();
          } catch (_) {
            /* ignore */
          }
          active.popup = null;
          setBusy(form, false);
          closeModal();
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
