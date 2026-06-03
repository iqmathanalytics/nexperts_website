# -*- coding: utf-8 -*-
"""Convert overview-tab .eyebrow divs to semantic h2 on all course detail pages."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

H2_EYEBROW_CSS = """#sec-overview h2.eyebrow{font-family:'Fraunces',serif;font-weight:300;font-size:clamp(1.2rem,1.75vw,1.5rem);line-height:1.25;letter-spacing:-.01em;text-transform:none;color:var(--ink);margin:0 0 14px;display:flex;align-items:center;gap:10px}
#sec-overview h2.eyebrow::before{content:'';width:18px;height:3px;background:var(--blue);border-radius:2px;flex-shrink:0}
#sec-overview h2.eyebrow.m::before{background:var(--marM)}
#sec-overview h2.eyebrow.g::before{background:var(--green)}"""

OLD_H2_EYEBROW_CSS = (
    "h2.eyebrow{font-family:inherit;font-size:.68rem;font-weight:700;margin:0;"
    "line-height:1.4;letter-spacing:.12em;text-transform:uppercase}"
)

EYEBROW_DIV = re.compile(
    r'<div class="(eyebrow[^"]*)"([^>]*)>(.*?)</div>',
    re.DOTALL,
)

OVERVIEW_START = re.compile(r'id="sec-overview"')
NEXT_SECTION = re.compile(r'\n  <div id="sec-')


def course_html_paths() -> list[Path]:
    paths = sorted((ROOT / "courses").glob("*.html"))
    for name in ("ccna.html", "ceh.html", "python-bootcamp.html", "data-science-with-python.html"):
        p = ROOT / name
        if p.is_file():
            paths.append(p)
    return paths


def overview_slice(html: str) -> tuple[int, int] | None:
    m = OVERVIEW_START.search(html)
    if not m:
        return None
    chunk_start = html.rfind("<div", 0, m.start())
    if chunk_start < 0:
        chunk_start = m.start()
    rest = html[m.end() :]
    nm = NEXT_SECTION.search(rest)
    if not nm:
        return None
    return chunk_start, m.end() + nm.start()


def ensure_h2_eyebrow_css(html: str) -> str:
    if "#sec-overview h2.eyebrow{" in html:
        while OLD_H2_EYEBROW_CSS in html:
            html = html.replace(OLD_H2_EYEBROW_CSS, "", 1)
        return html
    if OLD_H2_EYEBROW_CSS in html:
        return html.replace(OLD_H2_EYEBROW_CSS, H2_EYEBROW_CSS, 1)
    needle = ".eyebrow.g{color:var(--green)}.eyebrow.g::before{background:var(--green)}"
    if needle in html:
        return html.replace(needle, needle + "\n" + H2_EYEBROW_CSS, 1)
    alt = ".eyebrow.m{color:var(--marM)}.eyebrow.m::before{background:var(--marM)}"
    if alt in html:
        return html.replace(alt, alt + "\n" + H2_EYEBROW_CSS, 1)
    return html


def patch_overview_eyebrows(html: str) -> tuple[str, int]:
    bounds = overview_slice(html)
    if not bounds:
        return html, 0
    start, end = bounds
    chunk = html[start:end]
    count = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal count
        inner = m.group(3).strip()
        if "<div" in inner or "<h" in inner:
            return m.group(0)
        count += 1
        return f'<h2 class="{m.group(1)}"{m.group(2)}>{m.group(3)}</h2>'

    patched = EYEBROW_DIV.sub(repl, chunk)
    if count == 0 and patched == chunk:
        return ensure_h2_eyebrow_css(html), 0
    html = html[:start] + patched + html[end:]
    html = ensure_h2_eyebrow_css(html)
    return html, count


def main() -> None:
    total_files = 0
    total_headings = 0
    css_files = 0
    for path in course_html_paths():
        text = path.read_text(encoding="utf-8")
        updated, n = patch_overview_eyebrows(text)
        final = ensure_h2_eyebrow_css(updated)
        if final != text:
            path.write_text(final, encoding="utf-8", newline="\n")
            total_files += 1
            total_headings += n
            if n:
                print(f"  {path.relative_to(ROOT)}: {n} heading(s)")
            else:
                css_files += 1
                print(f"  {path.relative_to(ROOT)}: CSS updated")
    print(
        f"Patched {total_files} files ({total_headings} overview eyebrows to h2, "
        f"{css_files} CSS upgrades)."
    )


if __name__ == "__main__":
    main()
