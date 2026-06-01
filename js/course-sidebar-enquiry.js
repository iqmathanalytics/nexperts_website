/**
 * Course page sidebar enquiry — same payload flow as contact.html (NexpertsEnquiry).
 */
(function (global) {
  "use strict";

  function teamInboxHint() {
    try {
      if (global.NexpertsEnquiry && global.NexpertsEnquiry.getTeamInbox) {
        var m = global.NexpertsEnquiry.getTeamInbox();
        if (m) return "Could not send your enquiry. Please try again or email " + m + ".";
      }
    } catch (_) {
      /* ignore */
    }
    return "Could not send your enquiry. Please try again or use the address on our Contact page.";
  }

  function bindForm(form) {
    if (!form || form.dataset.nxEnquiryBound === "1") return;
    form.dataset.nxEnquiryBound = "1";

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var wrap = form.closest(".course-sidebar-enquiry");
      var errEl = wrap && wrap.querySelector(".course-enquiry-err");
      var okEl = wrap && wrap.querySelector(".course-enquiry-success");

      if (!global.NexpertsEnquiry || !global.NexpertsEnquiry.submit) {
        if (errEl) {
          errEl.textContent = "Enquiry script failed to load. Refresh the page.";
          errEl.hidden = false;
        }
        return;
      }

      if (errEl) {
        errEl.hidden = true;
        errEl.textContent = "";
      }

      global.NexpertsEnquiry.submit(form, { source: "course_sidebar" })
        .then(function () {
          form.hidden = true;
          if (okEl) okEl.hidden = false;
          try {
            wrap.scrollIntoView({ behavior: "smooth", block: "nearest" });
          } catch (_) {
            /* ignore */
          }
        })
        .catch(function (x) {
          if (errEl) {
            errEl.textContent = (x && x.message) ? x.message : teamInboxHint();
            errEl.hidden = false;
          }
        });
    });
  }

  function init() {
    global.document.querySelectorAll(".course-enquiry-form").forEach(bindForm);
  }

  if (global.document) {
    if (global.document.readyState === "loading") {
      global.document.addEventListener("DOMContentLoaded", init);
    } else {
      init();
    }
  }
})(window);
