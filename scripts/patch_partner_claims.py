# -*- coding: utf-8 -*-
"""Remove non-CompTIA / non-EC-Council partner claims from course pages."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from _partner_claims import sanitize_partner_html  # noqa: E402


def course_html_paths() -> list[Path]:
    paths = sorted((ROOT / "courses").glob("*.html"))
    for name in ("ccna.html", "ceh.html", "python-bootcamp.html", "data-science-with-python.html"):
        p = ROOT / name
        if p.is_file():
            paths.append(p)
    return paths


def main() -> None:
    changed = 0
    for path in course_html_paths():
        text = path.read_text(encoding="utf-8")
        updated = sanitize_partner_html(text)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
            print(f"  {path.relative_to(ROOT)}")
    print(f"Patched {changed} course pages.")


if __name__ == "__main__":
    main()
