# -*- coding: utf-8 -*-
"""Load Course + FAQPage JSON-LD blocks and align page URLs to the canonical."""

from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).parent
_DEFAULT_SCHEMA_FILE = _ROOT / "schema_imp.txt"
_SCHEMAS_DIR = _ROOT / "_schemas"
_SITE = "https://www.nexpertsacademy.com"

# Page URLs under the site (not bare homepage / org ids).
_PAGE_URL_RE = (
    r"https://www\.nexpertsacademy\.com/"
    r"(?:courses/[A-Za-z0-9_-]+|[A-Za-z0-9_%.-]+)"
)


def _json_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    depth = 0
    start: int | None = None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                blocks.append(text[start : i + 1].strip())
                start = None
    return blocks


def schema_markup_from_file(path: Path | None = None) -> str:
    src = path or _DEFAULT_SCHEMA_FILE
    text = src.read_text(encoding="utf-8")
    if src.suffix == ".htmlfrag" or "<script" in text:
        return text.strip()
    blocks = _json_blocks(text)
    page_blocks = [
        b
        for b in blocks
        if re.search(
            r'"@type"\s*:\s*"(?:Course|FAQPage|BreadcrumbList|EducationalOrganization|EducationalOccupationalCredential|Product|AggregateRating|Review)"',
            b,
        )
    ]
    scripts = []
    for block in page_blocks:
        block = re.sub(r"\n\s+", "\n", block)
        scripts.append(f'<script type="application/ld+json">\n{block}\n</script>')
    return "\n".join(scripts)


def schema_markup_for_slug(slug: str) -> str:
    """Prefer per-course schema fragment; fall back to schema_imp.txt."""
    frag = _SCHEMAS_DIR / f"{slug}.htmlfrag"
    if frag.exists():
        return schema_markup_from_file(frag)
    return schema_markup_from_file()


def align_schema_urls(markup: str, canon_url: str) -> str:
    """Rewrite course page URLs / @ids in JSON-LD to match the page canonical.

    Leaves bare homepage URLs (organization) untouched.
    Ensures Course objects include a url equal to the canonical.
    """
    if not markup or not canon_url:
        return markup

    # Replace "url": "<page-url>"
    markup = re.sub(
        rf'("url"\s*:\s*")({_PAGE_URL_RE})(")',
        rf"\1{canon_url}\3",
        markup,
    )
    # Replace "@id": "<page-url>#fragment"
    markup = re.sub(
        rf'("@id"\s*:\s*")({_PAGE_URL_RE})(#[^"]*)(")',
        rf"\1{canon_url}\3\4",
        markup,
    )
    # Replace "@id": "<page-url>" without fragment
    markup = re.sub(
        rf'("@id"\s*:\s*")({_PAGE_URL_RE})(")',
        rf"\1{canon_url}\3",
        markup,
    )

    def ensure_course_url(block: str) -> str:
        if not re.search(r'"@type"\s*:\s*"Course"', block):
            return block
        # Prefer keys between @type Course and provider (top-level course fields)
        m = re.search(
            r'("@type"\s*:\s*"Course"\s*,)([\s\S]*?)("provider"\s*:)',
            block,
        )
        if m:
            mid = m.group(2)
            if re.search(r'"url"\s*:', mid):
                mid = re.sub(
                    r'("url"\s*:\s*")[^"]*(")',
                    rf'\1{canon_url}\2',
                    mid,
                    count=1,
                )
            else:
                mid = f'\n  "url": "{canon_url}",' + mid
            return block[: m.start()] + m.group(1) + mid + m.group(3) + block[m.end() :]
        # No provider — insert or rewrite a top-level url after @type
        if re.search(r'"@type"\s*:\s*"Course"\s*,[\s\S]*?"url"\s*:', block):
            return re.sub(
                r'("@type"\s*:\s*"Course"\s*,[\s\S]*?"url"\s*:\s*")[^"]*(")',
                rf"\1{canon_url}\2",
                block,
                count=1,
            )
        return re.sub(
            r'("@type"\s*:\s*"Course"\s*,)',
            rf'\1\n  "url": "{canon_url}",',
            block,
            count=1,
        )

    def fix_script(m: re.Match[str]) -> str:
        body = m.group(1)
        parts = _json_blocks(body) if "{" in body else []
        if not parts:
            return m.group(0)
        fixed = "\n".join(ensure_course_url(p) for p in parts)
        return f'<script type="application/ld+json">\n{fixed}\n</script>'

    if "<script" in markup:
        markup = re.sub(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            fix_script,
            markup,
            flags=re.DOTALL,
        )
    else:
        parts = _json_blocks(markup)
        if parts:
            markup = "\n".join(ensure_course_url(p) for p in parts)

    return markup
