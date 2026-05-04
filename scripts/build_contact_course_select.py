# -*- coding: utf-8 -*-
"""Rebuild course <select> options on contact.html and index.html (enquiry modal) from CARDS + P1.

Run from repo root after catalog changes:
    python scripts/build_contact_course_select.py
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTACT = ROOT / "contact.html"
INDEX = ROOT / "index.html"
CATALOG = ROOT / "_build_catalog.py"

MARK_CONTACT_BEGIN = "<!-- NX_CONTACT_COURSE_OPTIONS_BEGIN -->"
MARK_CONTACT_END = "<!-- NX_CONTACT_COURSE_OPTIONS_END -->"
MARK_INDEX_BEGIN = "<!-- NX_INDEX_COURSE_OPTIONS_BEGIN -->"
MARK_INDEX_END = "<!-- NX_INDEX_COURSE_OPTIONS_END -->"


def load_catalog():
    spec = importlib.util.spec_from_file_location("_build_catalog", CATALOG)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_build_catalog"] = mod
    spec.loader.exec_module(mod)
    return mod


def escape_attr(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
    )


def escape_text(s: str) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_inner_html(mod, *, base_indent: str) -> str:
    """base_indent: spaces before top-level <option>/<optgroup> (differs for contact vs index)."""
    P1 = mod.P1
    CARDS = mod.CARDS
    name_to_slug = mod.name_to_slug
    brand_labels = {bm[0]: bm[1] for bm in mod.BRANDS}
    opt_indent = base_indent + "  "

    lines: list[str] = [
        f'{base_indent}<option value="">-- Select a course --</option>',
    ]

    current_brand: str | None = None
    for row in CARDS:
        brand_key = row[0]
        name = row[4]
        slug = P1.get(name) or name_to_slug(name)
        path = f"course_pages/{slug}.html"

        if brand_key != current_brand:
            if current_brand is not None:
                lines.append(f"{base_indent}</optgroup>")
            og = escape_attr(brand_labels.get(brand_key, brand_key))
            lines.append(f'{base_indent}<optgroup label="{og}">')
            current_brand = brand_key

        lines.append(
            f'{opt_indent}<option data-curriculum="{escape_attr(path)}">{escape_text(name)}</option>'
        )

    if current_brand is not None:
        lines.append(f"{base_indent}</optgroup>")

    lines.append(f"{base_indent}<option>Corporate / Group Training (multiple courses)</option>")
    lines.append(f"{base_indent}<option>Not sure — need advice</option>")

    return "\n".join(lines)


def _replace_markers(path: Path, begin: str, end: str, inner: str) -> None:
    text = path.read_text(encoding="utf-8")
    if begin not in text or end not in text:
        raise SystemExit(f"{path.name}: missing markers {begin!r} … {end!r}")
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.DOTALL)
    replacement = begin + "\n" + inner + "\n" + end
    new_text, n = pattern.subn(replacement, text, count=1)
    if n != 1:
        raise SystemExit(f"{path.name}: could not replace course options block")
    path.write_text(new_text, encoding="utf-8")


def main():
    mod = load_catalog()
    inner_contact = build_inner_html(mod, base_indent="              ")
    inner_index = build_inner_html(mod, base_indent="            ")

    _replace_markers(CONTACT, MARK_CONTACT_BEGIN, MARK_CONTACT_END, inner_contact)
    _replace_markers(INDEX, MARK_INDEX_BEGIN, MARK_INDEX_END, inner_index)

    n = len(mod.CARDS)
    print(f"Updated {CONTACT.relative_to(ROOT)} and {INDEX.relative_to(ROOT)} ({n} courses + 2 general options each).")


if __name__ == "__main__":
    main()
