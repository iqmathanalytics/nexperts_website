/**
 * contact.html only: ?course=... pre-selects the course field and scrolls to #enquire.
 */
(function () {
  "use strict";

  function apply() {
    try {
      var params = new URLSearchParams(window.location.search);
      var raw = params.get("course");
      if (!raw) return;
      var course = "";
      try {
        course = decodeURIComponent(String(raw).trim());
      } catch (_) {
        course = String(raw).trim();
      }
      course = course.trim();
      if (!course) return;

      var form = document.getElementById("enquiryForm");
      if (!form) return;
      var sel = form.elements.namedItem("course");
      if (!sel || sel.tagName !== "SELECT") return;

      var i;
      var found = false;
      for (i = 0; i < sel.options.length; i++) {
        var o = sel.options[i];
        if (o.value === course || String(o.textContent || "").trim() === course) {
          sel.selectedIndex = i;
          found = true;
          break;
        }
      }
      if (!found) {
        var opt = document.createElement("option");
        opt.value = course;
        opt.textContent = course;
        if (sel.options.length > 1) {
          sel.add(opt, 1);
        } else {
          sel.add(opt);
        }
        sel.value = course;
      }

      if (window.location.hash !== "#enquire") {
        window.location.hash = "enquire";
      }
      var sec = document.getElementById("enquire");
      if (sec) {
        sec.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    } catch (_) {
      /* ignore */
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", apply);
  } else {
    apply();
  }
})();
