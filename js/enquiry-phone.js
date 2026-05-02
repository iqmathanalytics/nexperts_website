/**
 * Fills country-code <select name="phoneCountry"> on enquiry forms.
 * Desktop: full country names. Mobile & tablet (max-width: 1024px): dial code only.
 */
(function (global) {
  "use strict";

  var COMPACT_MQ = "(max-width: 1024px)";

  var OPTIONS = [
    ["+60", "Malaysia (+60)"],
    ["+1", "United States / Canada (+1)"],
    ["+65", "Singapore (+65)"],
    ["+62", "Indonesia (+62)"],
    ["+66", "Thailand (+66)"],
    ["+63", "Philippines (+63)"],
    ["+91", "India (+91)"],
    ["+44", "United Kingdom (+44)"],
    ["+61", "Australia (+61)"],
    ["+64", "New Zealand (+64)"],
    ["+86", "China (+86)"],
    ["+852", "Hong Kong (+852)"],
    ["+886", "Taiwan (+886)"],
    ["+81", "Japan (+81)"],
    ["+82", "South Korea (+82)"],
    ["+971", "United Arab Emirates (+971)"],
    ["+966", "Saudi Arabia (+966)"],
    ["+27", "South Africa (+27)"],
    ["+353", "Ireland (+353)"],
    ["+49", "Germany (+49)"],
    ["+33", "France (+33)"],
    ["+92", "Pakistan (+92)"],
    ["+880", "Bangladesh (+880)"],
    ["+94", "Sri Lanka (+94)"],
    ["+673", "Brunei (+673)"],
    ["+84", "Vietnam (+84)"],
  ];

  function useCompactLabels() {
    try {
      return global.matchMedia(COMPACT_MQ).matches;
    } catch (_) {
      return global.innerWidth <= 1024;
    }
  }

  function syncPhoneCountrySelects() {
    var doc = global.document;
    if (!doc || !doc.querySelectorAll) return;

    var compact = useCompactLabels();

    doc.querySelectorAll('select[name="phoneCountry"]').forEach(function (sel) {
      var prev = String(sel.value || "").trim();
      sel.textContent = "";
      OPTIONS.forEach(function (pair) {
        var o = doc.createElement("option");
        o.value = pair[0];
        o.textContent = compact ? pair[0] : pair[1];
        sel.appendChild(o);
      });
      var hasPrev = OPTIONS.some(function (p) {
        return p[0] === prev;
      });
      sel.value = hasPrev ? prev : "+60";
    });
  }

  function bindViewport() {
    try {
      var mq = global.matchMedia(COMPACT_MQ);
      if (mq.addEventListener) {
        mq.addEventListener("change", syncPhoneCountrySelects);
      } else if (mq.addListener) {
        mq.addListener(syncPhoneCountrySelects);
      }
    } catch (_) {
      /* ignore */
    }
    var t;
    global.addEventListener(
      "resize",
      function () {
        clearTimeout(t);
        t = setTimeout(syncPhoneCountrySelects, 120);
      },
      { passive: true }
    );
  }

  if (global.document) {
    if (global.document.readyState === "loading") {
      global.document.addEventListener("DOMContentLoaded", function () {
        syncPhoneCountrySelects();
        bindViewport();
      });
    } else {
      syncPhoneCountrySelects();
      bindViewport();
    }
  }
})(window);
