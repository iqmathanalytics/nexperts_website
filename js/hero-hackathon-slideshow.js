/**
 * Hero hackathon carousel — automatic advance every 2s, pause on hover / hidden tab.
 * Images live under /image/hackathon/ (see HACKATHON_FILES).
 */
(function () {
  "use strict";

  var INTERVAL_MS = 2000;
  var BASE = "/image/hackathon/";

  var FILES = [
    "WhatsApp Image 2026-05-13 at 11.53.20.jpeg",
    "WhatsApp Image 2026-05-13 at 11.53.20 (1).jpeg",
    "WhatsApp Image 2026-05-13 at 11.53.20 (3).jpeg",
    "WhatsApp Image 2026-05-13 at 11.53.20 (4).jpeg",
    "WhatsApp Image 2026-05-13 at 11.53.20 (5).jpeg",
    "WhatsApp Image 2026-05-13 at 11.53.20 (6).jpeg",
    "WhatsApp Image 2026-05-13 at 11.53.20 (7).jpeg",
    "WhatsApp Image 2026-05-13 at 11.53.20 (8).jpeg",
    "WhatsApp Image 2026-05-13 at 11.53.20 (9).jpeg",
    "WhatsApp Image 2026-05-13 at 11.53.20 (10).jpeg",
    "WhatsApp Image 2026-05-13 at 11.53.20 (11).jpeg",
    "WhatsApp Image 2026-05-13 at 11.53.20 (12).jpeg",
    "WhatsApp Image 2026-05-13 at 11.53.21.jpeg",
  ];

  function srcFor(name) {
    return BASE + encodeURIComponent(name);
  }

  function prefersReducedMotion() {
    return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function init() {
    var root = document.getElementById("heroHackathon");
    var track = document.getElementById("heroHackathonTrack");
    var dotsWrap = document.getElementById("heroHackathonDots");
    var bar = document.getElementById("heroHackathonProgressBar");
    var btnPrev = document.getElementById("heroHackathonPrev");
    var btnNext = document.getElementById("heroHackathonNext");
    if (!root || !track || !dotsWrap || !bar) return;

    var slides = [];
    var dots = [];
    var idx = 0;
    var timer = null;
    var paused = false;

    FILES.forEach(function (file, i) {
      var fig = document.createElement("figure");
      fig.className = "hero-h-slide" + (i === 0 ? " is-active" : "");
      fig.setAttribute("aria-hidden", i === 0 ? "false" : "true");

      var img = document.createElement("img");
      img.src = srcFor(file);
      img.alt = "Nexperts Academy hackathon — event photo " + (i + 1) + " of " + FILES.length;
      img.loading = i === 0 ? "eager" : "lazy";
      img.decoding = "async";
      img.sizes = "(max-width: 1024px) 96vw, min(94vw, 1040px)";
      fig.appendChild(img);
      track.appendChild(fig);
      slides.push(fig);

      var dot = document.createElement("button");
      dot.type = "button";
      dot.className = "hero-h-dot" + (i === 0 ? " is-active" : "");
      dot.setAttribute("role", "tab");
      dot.setAttribute("aria-selected", i === 0 ? "true" : "false");
      dot.setAttribute("aria-label", "Show hackathon photo " + (i + 1));
      dot.addEventListener("click", function () {
        goTo(i, true);
      });
      dotsWrap.appendChild(dot);
      dots.push(dot);
    });

    function setActive(i) {
      slides.forEach(function (el, j) {
        var on = j === i;
        el.classList.toggle("is-active", on);
        el.setAttribute("aria-hidden", on ? "false" : "true");
      });
      dots.forEach(function (d, j) {
        var on = j === i;
        d.classList.toggle("is-active", on);
        d.setAttribute("aria-selected", on ? "true" : "false");
      });
      idx = i;
    }

    function kickProgress() {
      bar.classList.remove("is-anim");
      void bar.offsetWidth;
      bar.classList.add("is-anim");
    }

    function goTo(i, user) {
      var n = ((i % slides.length) + slides.length) % slides.length;
      if (n === idx && user) return;
      setActive(n);
      kickProgress();
      if (user) {
        clearTimer();
        schedule();
      }
    }

    function next() {
      goTo(idx + 1, false);
    }

    function prev() {
      goTo(idx - 1, false);
    }

    function clearTimer() {
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
    }

    function schedule() {
      clearTimer();
      if (paused || prefersReducedMotion() || slides.length < 2) return;
      timer = window.setInterval(next, INTERVAL_MS);
    }

    function onVis() {
      if (document.hidden) {
        paused = true;
        clearTimer();
        bar.classList.remove("is-anim");
      } else {
        paused = false;
        kickProgress();
        schedule();
      }
    }

    if (btnNext) btnNext.addEventListener("click", function () {
      goTo(idx + 1, true);
    });
    if (btnPrev) btnPrev.addEventListener("click", function () {
      goTo(idx - 1, true);
    });

    root.addEventListener("mouseenter", function () {
      paused = true;
      clearTimer();
      bar.classList.remove("is-anim");
    });
    root.addEventListener("mouseleave", function () {
      paused = false;
      kickProgress();
      schedule();
    });

    document.addEventListener("visibilitychange", onVis);

    root.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") {
        e.preventDefault();
        goTo(idx + 1, true);
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        goTo(idx - 1, true);
      }
    });

    if (!prefersReducedMotion() && slides.length > 1) {
      kickProgress();
      schedule();
    } else {
      bar.classList.remove("is-anim");
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
