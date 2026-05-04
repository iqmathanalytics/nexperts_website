# -*- coding: utf-8 -*-
"""
Inject Google Analytics 4 (gtag.js) after the viewport meta tag in public HTML.

Resolution order for the Measurement ID:
  1. Environment variable NEXPERTS_GA4_ID (recommended for Netlify)
  2. config/ga4.json → "measurement_id"

If no ID is set, any existing GA4 block is removed and nothing is injected.

Run from repo root: python scripts/inject_ga4.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MARKER_START = "<!-- nexperts-ga4:v1 -->"
MARKER_END = "<!-- /nexperts-ga4:v1 -->"

# Must match pages produced by the site templates (after charset, before title).
VIEWPORT_RE = re.compile(
    r'(<meta\s+name="viewport"\s+content="width=device-width,\s*initial-scale=1\.0"\s*>)',
    re.I,
)

GA4_ID_RE = re.compile(r"^G-[A-Z0-9]+$")


def load_measurement_id() -> str:
    env = os.environ.get("NEXPERTS_GA4_ID", "").strip()
    if env:
        return env
    path = ROOT / "config" / "ga4.json"
    if not path.is_file():
        return ""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""
    return str(data.get("measurement_id", "")).strip()


def remove_ga4_block(html: str) -> str:
    pattern = re.compile(
        re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
        re.DOTALL | re.I,
    )
    return pattern.sub("", html)


def build_snippet(measurement_id: str) -> str:
    # measurement_id validated before calling
    return (
        f"\n{MARKER_START}\n"
        f'<script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>\n'
        "<script>\n"
        "  window.dataLayer = window.dataLayer || [];\n"
        "  function gtag(){dataLayer.push(arguments);}\n"
        "  gtag('js', new Date());\n"
        f"  gtag('config', '{measurement_id}');\n"
        "</script>\n"
        f"{MARKER_END}\n"
    )


def inject_after_viewport(html: str, snippet: str) -> str | None:
    if VIEWPORT_RE.search(html) is None:
        return None
    return VIEWPORT_RE.sub(r"\1" + snippet, html, count=1)


def process_file(path: Path, measurement_id: str | None) -> bool:
    html = path.read_text(encoding="utf-8")
    html = remove_ga4_block(html)
    if not measurement_id:
        path.write_text(html, encoding="utf-8", newline="\n")
        return True
    snippet = build_snippet(measurement_id)
    out = inject_after_viewport(html, snippet)
    if out is None:
        path.write_text(html, encoding="utf-8", newline="\n")
        print(f"SKIP (no viewport meta): {path.relative_to(ROOT)}", file=sys.stderr)
        return False
    path.write_text(out, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    mid = load_measurement_id()
    if mid and not GA4_ID_RE.match(mid):
        print(
            "Invalid GA4 Measurement ID (expected format G-XXXXXXXXXX): "
            + repr(mid[:20] + ("…" if len(mid) > 20 else "")),
            file=sys.stderr,
        )
        return 1

    ok = 0
    fail = 0

    for path in sorted((ROOT / "course_pages").glob("*.html")):
        if process_file(path, mid or None):
            ok += 1
            print(f"OK course_pages/{path.name}")
        else:
            fail += 1

    for fname in (
        "index.html",
        "about.html",
        "contact.html",
        "privacy-policy.html",
        "Nexperts beyond.html",
    ):
        path = ROOT / fname
        if not path.is_file():
            continue
        if process_file(path, mid or None):
            ok += 1
            print(f"OK {fname}")
        else:
            fail += 1

    if not mid:
        print(
            "GA4: no measurement id - stripped markers only. "
            "Set NEXPERTS_GA4_ID or config/ga4.json, then re-run.",
            file=sys.stderr,
        )
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
