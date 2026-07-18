# -*- coding: utf-8 -*-
"""Align page URL / og:url / schema url with the canonical URL site-wide.

Run from repo root:
    python scripts/align_canonical_urls.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from site_paths import (  # noqa: E402
    ROOT_CANONICAL_FILES,
    canonical_path_for_slug,
    detail_html_path,
)
from _course_schema_loader import align_schema_urls  # noqa: E402

SITE = "https://www.nexpertsacademy.com"


def expected_canon_for_file(path: Path) -> str | None:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return f"{SITE}/"
    if path.parent.name == "blog":
        return f"{SITE}/blog/{path.stem}"
    if path.parent.name == "courses":
        slug = path.stem
        if slug in ROOT_CANONICAL_FILES or slug == "ceh-v13-ai":
            # Prefer root canonical; /courses/ccna should not be indexed as primary
            return f"{SITE}{canonical_path_for_slug(slug if slug != 'ceh-v13-ai' else 'ceh')}"
        return f"{SITE}{canonical_path_for_slug(slug)}"
    if path.name in ROOT_CANONICAL_FILES.values():
        slug = next(s for s, f in ROOT_CANONICAL_FILES.items() if f == path.name)
        return f"{SITE}{canonical_path_for_slug(slug)}"
    # Other root HTML pages: /about, /contact, etc.
    if path.parent == ROOT and path.suffix == ".html":
        if path.name == "Nexperts beyond.html":
            return f"{SITE}/Nexperts%20beyond.html"
        return f"{SITE}/{path.stem}"
    return None


def align_file(path: Path) -> bool:
    canon = expected_canon_for_file(path)
    if not canon:
        return False
    html = path.read_text(encoding="utf-8")
    original = html

    if 'property="og:url"' in html:
        html = re.sub(
            r'<meta property="og:url" content="[^"]*">',
            f'<meta property="og:url" content="{canon}">',
            html,
            count=1,
        )
    if 'rel="canonical"' in html:
        html = re.sub(
            r'<link rel="canonical" href="[^"]*">',
            f'<link rel="canonical" href="{canon}">',
            html,
            count=1,
        )

    def _align_schema(m: re.Match[str]) -> str:
        body = align_schema_urls(m.group(1).strip(), canon)
        return f"<!-- nexperts-schema:v1 -->\n{body}\n<!-- /nexperts-schema:v1 -->"

    if "<!-- nexperts-schema:v1 -->" in html:
        html = re.sub(
            r"<!-- nexperts-schema:v1 -->\s*(.*?)\s*<!-- /nexperts-schema:v1 -->",
            _align_schema,
            html,
            count=1,
            flags=re.DOTALL,
        )
    else:
        # Loose JSON-LD Course blocks without marker
        def fix_script(m: re.Match[str]) -> str:
            body = m.group(1)
            if '"Course"' not in body and '"Product"' not in body:
                return m.group(0)
            return f'<script type="application/ld+json">\n{align_schema_urls(body, canon)}\n</script>'

        html = re.sub(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            fix_script,
            html,
            flags=re.DOTALL,
        )

    if html != original:
        path.write_text(html, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    paths: list[Path] = []
    paths.extend(sorted((ROOT / "courses").glob("*.html")))
    for fname in ROOT_CANONICAL_FILES.values():
        p = ROOT / fname
        if p.exists():
            paths.append(p)
    paths.extend(sorted((ROOT / "blog").glob("*.html")))
    for name in (
        "index.html",
        "about.html",
        "contact.html",
        "workshops.html",
        "upcoming-events.html",
        "privacy-policy.html",
        "blog.html",
    ):
        p = ROOT / name
        if p.exists():
            paths.append(p)

    changed = 0
    for p in paths:
        if align_file(p):
            print(f"aligned {p.relative_to(ROOT).as_posix()}")
            changed += 1
    print(f"Updated {changed} file(s)")


if __name__ == "__main__":
    main()
