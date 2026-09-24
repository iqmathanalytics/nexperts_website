# -*- coding: utf-8 -*-
"""
Inject Google Tag Manager (GTM) head + body noscript across public HTML.

Replaces the older direct GA4 (nexperts-ga4:v1) snippets so analytics loads
through GTM only (avoids double-counting if GA4 is also configured in GTM).

Resolution order for the container ID:
  1. Environment variable NEXPERTS_GTM_ID
  2. config/gtm.json → "container_id"

If no ID is set, existing GTM + GA4 marker blocks are removed and nothing is injected.

Run from repo root: python scripts/inject_gtm.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GA4_START = "<!-- nexperts-ga4:v1 -->"
GA4_END = "<!-- /nexperts-ga4:v1 -->"
GTM_HEAD_START = "<!-- nexperts-gtm:v1 -->"
GTM_HEAD_END = "<!-- /nexperts-gtm:v1 -->"
GTM_BODY_START = "<!-- nexperts-gtm-noscript:v1 -->"
GTM_BODY_END = "<!-- /nexperts-gtm-noscript:v1 -->"

VIEWPORT_RE = re.compile(
    r'(<meta\s+name=["\']viewport["\']\s+content=["\']width=device-width,\s*initial-scale=1\.0["\']\s*/?>)',
    re.I,
)
BODY_RE = re.compile(r"(<body\b[^>]*>)", re.I)
GTM_ID_RE = re.compile(r"^GTM-[A-Z0-9]+$")

SKIP_DIRS = frozenset(
    {
        "admin",
        "snippets",
        "node_modules",
        ".git",
        "netlify",
        "functions",
    }
)


def load_container_id() -> str:
    env = os.environ.get("NEXPERTS_GTM_ID", "").strip()
    if env:
        return env
    path = ROOT / "config" / "gtm.json"
    if not path.is_file():
        return ""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""
    return str(data.get("container_id", "")).strip()


def remove_marked_block(html: str, start: str, end: str) -> str:
    pattern = re.compile(
        re.escape(start) + r".*?" + re.escape(end),
        re.DOTALL | re.I,
    )
    return pattern.sub("", html)


def strip_legacy_blocks(html: str) -> str:
    html = remove_marked_block(html, GA4_START, GA4_END)
    html = remove_marked_block(html, GTM_HEAD_START, GTM_HEAD_END)
    html = remove_marked_block(html, GTM_BODY_START, GTM_BODY_END)
    # Clean leftover blank runs after removals (keep one newline max cluster).
    html = re.sub(r"\n{4,}", "\n\n\n", html)
    return html


def build_head_snippet(container_id: str) -> str:
    return (
        f"\n{GTM_HEAD_START}\n"
        "<!-- Google Tag Manager -->\n"
        "<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':\n"
        "new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],\n"
        "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=\n"
        f"'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);\n"
        f"}})(window,document,'script','dataLayer','{container_id}');</script>\n"
        "<!-- End Google Tag Manager -->\n"
        f"{GTM_HEAD_END}\n"
    )


def build_body_snippet(container_id: str) -> str:
    return (
        f"\n{GTM_BODY_START}\n"
        "<!-- Google Tag Manager (noscript) -->\n"
        f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={container_id}"\n'
        'height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n'
        "<!-- End Google Tag Manager (noscript) -->\n"
        f"{GTM_BODY_END}\n"
    )


def inject_after_viewport(html: str, snippet: str) -> str | None:
    if VIEWPORT_RE.search(html) is None:
        return None
    return VIEWPORT_RE.sub(r"\1" + snippet, html, count=1)


def inject_after_body(html: str, snippet: str) -> str | None:
    if BODY_RE.search(html) is None:
        return None
    return BODY_RE.sub(r"\1" + snippet, html, count=1)


def iter_public_html() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*.html"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def process_file(path: Path, container_id: str | None) -> str:
    """Return status: ok | skip-viewport | skip-body | error."""
    try:
        html = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR read {path.relative_to(ROOT)}: {exc}", file=sys.stderr)
        return "error"

    html = strip_legacy_blocks(html)

    if not container_id:
        path.write_text(html, encoding="utf-8", newline="\n")
        return "ok"

    head = build_head_snippet(container_id)
    body = build_body_snippet(container_id)

    out = inject_after_viewport(html, head)
    if out is None:
        path.write_text(html, encoding="utf-8", newline="\n")
        print(f"SKIP (no viewport meta): {path.relative_to(ROOT)}", file=sys.stderr)
        return "skip-viewport"

    out2 = inject_after_body(out, body)
    if out2 is None:
        path.write_text(out, encoding="utf-8", newline="\n")
        print(f"SKIP (no body tag): {path.relative_to(ROOT)}", file=sys.stderr)
        return "skip-body"

    path.write_text(out2, encoding="utf-8", newline="\n")
    return "ok"


def main() -> int:
    cid = load_container_id()
    if cid and not GTM_ID_RE.match(cid):
        print(
            "Invalid GTM container ID (expected format GTM-XXXXXXX): "
            + repr(cid[:24] + ("…" if len(cid) > 24 else "")),
            file=sys.stderr,
        )
        return 1

    ok = 0
    fail = 0
    for path in iter_public_html():
        status = process_file(path, cid or None)
        rel = path.relative_to(ROOT).as_posix()
        if status == "ok":
            ok += 1
            print(f"OK {rel}")
        else:
            fail += 1

    if not cid:
        print(
            "GTM: no container id — stripped markers only. "
            "Set NEXPERTS_GTM_ID or config/gtm.json, then re-run.",
            file=sys.stderr,
        )
    else:
        print(f"GTM {cid}: updated {ok} file(s), {fail} skip/error(s)")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
