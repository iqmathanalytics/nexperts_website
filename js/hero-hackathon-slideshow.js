/**
 * Hero hackathon carousel — lighter paint: optimized images, adjacent preload only,
 * slower cadence, pause when hero is off-screen / tab hidden / hover.
 */
(function () {
  "use strict";

  var INTERVAL_MS = 4000;
  var BASE = "/image/hackathon/sm/";

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
    var bar = document.getElementById("heroHackathonProgressBar");
    var hero = document.getElementById("heroSection");
    if (!root || !track || !bar) return;

    var slides = [];
    var imgs = [];
    var idx = 0;
    var timer = null;
    var paused = false;
    var heroVisible = true;

    FILES.forEach(function (file, i) {
      var fig = document.createElement("figure");
      fig.className = "hero-h-slide" + (i === 0 ? " is-active" : "");
      fig.setAttribute("aria-hidden", i === 0 ? "false" : "true");

      var img = document.createElement("img");
      img.alt = "Nexperts Academy hackathon — event photo " + (i + 1) + " of " + FILES.length;
      img.decoding = "async";
      img.width = 960;
      img.height = 540;
      img.sizes = "(max-width: 1024px) 96vw, min(60vw, 720px)";
      if (i === 0) {
        img.src = srcFor(file);
        img.loading = "eager";
        img.fetchPriority = "high";
      } else {
        img.loading = "lazy";
        img.dataset.src = srcFor(file);
      }
      fig.appendChild(img);
      track.appendChild(fig);
      slides.push(fig);
      imgs.push(img);
    });

    function ensureSrc(i) {
      var img = imgs[i];
      if (!img) return;
      if (!img.getAttribute("src") && img.dataset.src) {
        img.src = img.dataset.src;
        delete img.dataset.src;
      }
    }

    function preloadNeighbors(i) {
      ensureSrc(i);
      ensureSrc((i + 1) % imgs.length);
      if (imgs.length > 2) ensureSrc((i + imgs.length - 1) % imgs.length);
    }

    function setActive(i) {
      slides.forEach(function (el, j) {
        var on = j === i;
        el.classList.toggle("is-active", on);
        el.setAttribute("aria-hidden", on ? "false" : "true");
      });
      idx = i;
      preloadNeighbors(i);
    }

    function kickProgress() {
      bar.classList.remove("is-anim");
      void bar.offsetWidth;
      if (!paused && heroVisible && !prefersReducedMotion()) {
        bar.classList.add("is-anim");
      }
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

    function clearTimer() {
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
    }

    function schedule() {
      clearTimer();
      if (paused || !heroVisible || prefersReducedMotion() || slides.length < 2) return;
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

    if (hero && "IntersectionObserver" in window) {
      var io = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (en) {
            heroVisible = en.isIntersecting;
            if (!heroVisible) {
              clearTimer();
              bar.classList.remove("is-anim");
            } else if (!paused) {
              kickProgress();
              schedule();
            }
          });
        },
        { threshold: 0.12 }
      );
      io.observe(hero);
    }

    root.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") {
        e.preventDefault();
        goTo(idx + 1, true);
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        goTo(idx - 1, true);
      }
    });

    preloadNeighbors(0);

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
