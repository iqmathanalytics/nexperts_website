#!/usr/bin/env python3
"""Apply recommended meta title/description from CEH-duplicates spreadsheet."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    import openpyxl
except ImportError:
    print("openpyxl required", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "nexperts_academy ceh_duplicates.xlsx"


def escape_attr(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def resolve_html(url: str) -> Path | None:
    path = urlparse(url).path.rstrip("/")
    if not path:
        return None
    # /courses/slug -> courses/slug.html
    if path.startswith("/courses/"):
        slug = path[len("/courses/") :]
        cand = ROOT / "courses" / f"{slug}.html"
        if cand.is_file():
            return cand
    # root vanity e.g. /ceh -> ceh.html
    slug = path.lstrip("/")
    for cand in (ROOT / f"{slug}.html", ROOT / "courses" / f"{slug}.html"):
        if cand.is_file():
            return cand
    return None


def patch_file(html_path: Path, title: str, description: str) -> bool:
    text = html_path.read_text(encoding="utf-8")
    orig = text
    t = escape_attr(title)
    d = escape_attr(description)

    text, n1 = re.subn(
        r"<title>[^<]*</title>",
        f"<title>{t}</title>",
        text,
        count=1,
        flags=re.I,
    )
    text, n2 = re.subn(
        r'(<meta\s+name=["\']description["\']\s+content=["\'])(.*?)(["\'])',
        rf"\g<1>{d}\g<3>",
        text,
        count=1,
        flags=re.I,
    )
    text, n3 = re.subn(
        r'(<meta\s+property=["\']og:title["\']\s+content=["\'])(.*?)(["\'])',
        rf"\g<1>{t}\g<3>",
        text,
        count=1,
        flags=re.I,
    )
    text, n4 = re.subn(
        r'(<meta\s+property=["\']og:description["\']\s+content=["\'])(.*?)(["\'])',
        rf"\g<1>{d}\g<3>",
        text,
        count=1,
        flags=re.I,
    )
    text, n5 = re.subn(
        r'(<meta\s+name=["\']twitter:title["\']\s+content=["\'])(.*?)(["\'])',
        rf"\g<1>{t}\g<3>",
        text,
        count=1,
        flags=re.I,
    )
    text, n6 = re.subn(
        r'(<meta\s+name=["\']twitter:description["\']\s+content=["\'])(.*?)(["\'])',
        rf"\g<1>{d}\g<3>",
        text,
        count=1,
        flags=re.I,
    )

    if text == orig:
        return False
    html_path.write_text(text, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb.active
    updated = skipped = missing = 0
    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        addr, _et, _ed, rec_title, rec_desc, _kw = (list(row) + [None] * 6)[:6]
        if not addr or not rec_title or not rec_desc:
            skipped += 1
            continue
        path = resolve_html(str(addr).strip())
        if not path:
            print(f"MISSING row {i}: {addr}")
            missing += 1
            continue
        if patch_file(path, str(rec_title).strip(), str(rec_desc).strip()):
            print(f"OK {path.relative_to(ROOT)}")
            updated += 1
        else:
            print(f"UNCHANGED {path.relative_to(ROOT)}")
            skipped += 1
    print(f"\nupdated={updated} skipped={skipped} missing={missing}")
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
