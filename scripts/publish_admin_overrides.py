# -*- coding: utf-8 -*-
"""Apply data/course-overrides.json to static HTML (detail pages + catalog cards).

Run from repo root:
  python scripts/publish_admin_overrides.py
"""
from __future__ import annotations

import html as html_module
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from site_paths import canonical_slug, detail_html_path

OVERRIDES_PATH = ROOT / "data" / "course-overrides.json"
INDEX_PATH = ROOT / "index.html"

PRICE_RX = re.compile(
    r'(<span class="price">)\s*([^<]*?)\s*(</span>)', re.IGNORECASE
)
PRICE_ORIG_RX = re.compile(
    r'(<span class="price-orig">)\s*([^<]*?)\s*(</span>)', re.IGNORECASE
)
PRICE_SAVE_RX = re.compile(
    r'(<span class="price-save">)\s*([^<]*?)\s*(</span>)', re.IGNORECASE
)
META_ROW_RX = re.compile(
    r'(<(?:motion\.)?div class="smeta-row"><span>([^<]+)</span><strong>)\s*([^<]*?)\s*(</strong></(?:motion\.)?div>)',
    re.IGNORECASE,
)
HERO_DURATION_RX = re.compile(
    r"(<span>Duration:\s*<strong>)\s*([^<]*?)\s*(</strong>)",
    re.IGNORECASE,
)
HERO_INTAKE_RX = re.compile(
    r"(<span>Next intake:\s*<strong>)\s*([^<]*?)\s*(</strong>)",
    re.IGNORECASE,
)


def parse_currency(s: str) -> float | None:
    if not s:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)", s.replace(",", ""))
    if not m:
        return None
    v = float(m.group(1))
    return v if v > 0 else None


def format_save_label(price: str, price_original: str) -> str | None:
    p = parse_currency(price)
    o = parse_currency(price_original)
    if not p or not o or o <= p:
        return None
    pct = round(((o - p) / o) * 100)
    if pct <= 0:
        return None
    return f"Save {pct}%"


def sub_meta(html: str, label: str, value: str) -> str:
    if not value:
        return html
    target = label.strip().lower()

    def repl(m: re.Match) -> str:
        if m.group(2).strip().lower() != target:
            return m.group(0)
        return m.group(1) + html_module.escape(value.strip()) + m.group(4)

    return META_ROW_RX.sub(repl, html)


def apply_detail_html(html: str, ov: dict) -> str:
    if ov.get("price"):
        html = PRICE_RX.sub(
            lambda m: m.group(1) + html_module.escape(str(ov["price"]).strip()) + m.group(3),
            html,
            count=1,
        )
    if ov.get("price_original"):
        html = PRICE_ORIG_RX.sub(
            lambda m: m.group(1)
            + html_module.escape(str(ov["price_original"]).strip())
            + m.group(3),
            html,
            count=1,
        )
    if ov.get("price") and ov.get("price_original"):
        label = format_save_label(str(ov["price"]), str(ov["price_original"]))
        if label:
            html = PRICE_SAVE_RX.sub(
                lambda m: m.group(1) + html_module.escape(label) + m.group(3),
                html,
                count=1,
            )
    if ov.get("duration"):
        html = sub_meta(html, "Duration", str(ov["duration"]))
        html = HERO_DURATION_RX.sub(
            lambda m: m.group(1) + html_module.escape(str(ov["duration"]).strip()) + m.group(3),
            html,
            count=1,
        )
    if ov.get("next_intake"):
        html = sub_meta(html, "Next intake", str(ov["next_intake"]))
        html = HERO_INTAKE_RX.sub(
            lambda m: m.group(1) + html_module.escape(str(ov["next_intake"]).strip()) + m.group(3),
            html,
            count=1,
        )
    return html


def patch_index_catalog(html: str, courses: dict) -> str:
    for slug, ov in courses.items():
        if not ov:
            continue
        name = (ov.get("name") or "").strip()
        desc = (ov.get("description") or "").strip()
        if not name and not desc:
            continue
        slug_esc = re.escape(slug)
        block_pat = re.compile(
            rf'(<a\b[^>]*\bdata-slug="{slug_esc}"[^>]*>)([\s\S]*?)(</a>)',
            re.IGNORECASE,
        )

        def repl(m: re.Match, n=name, d=desc) -> str:
            inner = m.group(2)
            if n:
                inner = re.sub(
                    r'(<div class="cname2">)\s*[^<]*?\s*(</div>)',
                    lambda x: x.group(1) + html_module.escape(n) + x.group(2),
                    inner,
                    count=1,
                    flags=re.IGNORECASE,
                )
            if d:
                inner = re.sub(
                    r'(<div class="cdesc2">)\s*[^<]*?\s*(</div>)',
                    lambda x: x.group(1) + html_module.escape(d) + x.group(2),
                    inner,
                    count=1,
                    flags=re.IGNORECASE,
                )
            return m.group(1) + inner + m.group(3)

        html = block_pat.sub(repl, html)
    return html


def main() -> int:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else OVERRIDES_PATH
    if not src.exists():
        print(f"No overrides file at {src.relative_to(ROOT)} — skip")
        return 0

    data = json.loads(src.read_text(encoding="utf-8"))
    courses = data.get("courses") or {}
    if not courses:
        print("No course overrides to apply")
        return 0

    updated = 0
    for slug, ov in courses.items():
        if not ov or not isinstance(ov, dict):
            continue
        slug = canonical_slug(slug)
        path = detail_html_path(ROOT, slug)
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        new_html = apply_detail_html(html, ov)
        if new_html != html:
            path.write_text(new_html, encoding="utf-8", newline="\n")
            updated += 1
            print(f"  detail: {path.relative_to(ROOT)}")

    if INDEX_PATH.exists():
        html = INDEX_PATH.read_text(encoding="utf-8")
        new_html = patch_index_catalog(html, courses)
        if new_html != html:
            INDEX_PATH.write_text(new_html, encoding="utf-8", newline="\n")
            updated += 1
            print(f"  catalog: {INDEX_PATH.relative_to(ROOT)}")

    print(f"Done — {updated} file(s) updated from {src.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
