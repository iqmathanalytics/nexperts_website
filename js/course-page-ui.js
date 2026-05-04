/**
 * Course detail pages: copy page URL (Share / Save) via a small modal; uses <link rel="canonical"> when present.
 * Also mirrors enquiry links into sessionStorage so contact.html still pre-fills after redirects that drop ?query.
 */
(function () {
  "use strict";

  var SS_COURSE = "nx_enquiry_course";
  var SS_TITLE = "nx_enquiry_title";
  var SS_INTENT = "nx_enquiry_intent";

  document.addEventListener(
    "click",
    function (e) {
      var a = e.target && e.target.closest ? e.target.closest('a[href*="contact.html"]') : null;
      if (!a || !a.href) return;
      try {
        var abs = new URL(a.href, window.location.href);
        var pn = (abs.pathname || "").replace(/\/$/, "");
        var isContact =
          pn.indexOf("contact.html") !== -1 ||
          pn === "/contact" ||
          pn.endsWith("/contact");
        if (!isContact) return;
        var q = abs.searchParams.get("course");
        if (!q) return;
        sessionStorage.setItem(SS_COURSE, q);
        var t = abs.searchParams.get("title");
        if (t) sessionStorage.setItem(SS_TITLE, t);
        else sessionStorage.removeItem(SS_TITLE);
        var i = abs.searchParams.get("intent");
        if (i) sessionStorage.setItem(SS_INTENT, i);
        else sessionStorage.removeItem(SS_INTENT);
      } catch (_) {}
    },
    true
  );

  function pageUrl() {
    var link = document.querySelector('link[rel="canonical"]');
    if (link && link.href) return link.href;
    return String(window.location.href || "").split("#")[0];
  }

  function closeModal() {
    var m = document.getElementById("nx-copy-modal");
    if (!m) return;
    m.hidden = true;
    m.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  function openModal(url) {
    var m = document.getElementById("nx-copy-modal");
    var inp = document.getElementById("nx-copy-url");
    var ok = document.getElementById("nx-copy-feedback");
    if (!m || !inp) return;
    inp.value = url;
    if (ok) {
      ok.textContent = "";
      ok.style.display = "none";
    }
    m.hidden = false;
    m.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    setTimeout(function () {
      try {
        inp.focus();
        inp.select();
      } catch (_) {}
    }, 50);
  }

  async function copyUrl(url) {
    var ok = document.getElementById("nx-copy-feedback");
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(url);
      } else {
        var inp = document.getElementById("nx-copy-url");
        if (inp) {
          inp.select();
          document.execCommand("copy");
        }
      }
      if (ok) {
        ok.textContent = "Copied to clipboard";
        ok.style.display = "block";
      }
    } catch (_) {
      if (ok) {
        ok.textContent = "Select the link and copy (Ctrl+C)";
        ok.style.display = "block";
      }
    }
  }

  document.addEventListener("click", function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    if (t.closest("[data-nx-close-modal]") || t.classList.contains("nx-modal-backdrop")) {
      e.preventDefault();
      closeModal();
      return;
    }
    var copyBtn = t.closest(".nx-share-copy");
    if (copyBtn) {
      e.preventDefault();
      openModal(pageUrl());
      return;
    }
    var doCopy = t.closest("#nx-copy-do");
    if (doCopy) {
      e.preventDefault();
      copyUrl(pageUrl());
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      var m = document.getElementById("nx-copy-modal");
      if (m && !m.hidden) {
        e.preventDefault();
        closeModal();
      }
    }
  });
})();
