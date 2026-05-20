# -*- coding: utf-8 -*-
"""Remove inline setupNavHighlight, add nav-highlight.js, rename Add-ons → Explore."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP = {"admin", "node_modules", ".git"}


def remove_inline_setup(html: str) -> str:
    marker = "function setupNavHighlight"
    start = html.find(marker)
    if start < 0:
        return html
    call = html.find("setupNavHighlight();", start)
    if call < 0:
        return html
    end = call + len("setupNavHighlight();")
    if end < len(html) and html[end] == "\r":
        end += 1
    if end < len(html) and html[end] == "\n":
        end += 1
    return html[:start] + html[end:]


def rename_explore(html: str) -> str:
    return html.replace(
        'Add-ons <span class="nav-addons-caret"',
        'Explore <span class="nav-addons-caret"',
    )


def ensure_highlight_script(html: str, path: Path) -> str:
    if "nav-highlight.js" in html:
        return html
    if "courses" in path.parts:
        needle = '<script src="../js/nav-addons.js" defer></script>'
        insert = (
            '<script src="../js/nav-highlight.js" defer></script>\n'
            + needle
        )
    elif path.name == "index.html":
        needle = '<script src="js/nav-addons.js" defer></script>'
        insert = (
            '<script src="js/nav-highlight.js" defer></script>\n' + needle
        )
    else:
        for needle, hl in (
            (
                '<script src="/js/nav-addons.js" defer></script>',
                '<script src="/js/nav-highlight.js" defer></script>\n',
            ),
            (
                '<script src="js/nav-addons.js" defer></script>',
                '<script src="js/nav-highlight.js" defer></script>\n',
            ),
        ):
            if needle in html:
                return html.replace(needle, hl + needle, 1)
        return html
    if needle in html:
        return html.replace(needle, insert, 1)
    return html


def iter_html() -> list[Path]:
    out: list[Path] = []
    for p in ROOT.rglob("*.html"):
        if any(s in p.parts for s in SKIP):
            continue
        out.append(p)
    return out


def main() -> None:
    changed = 0
    for path in iter_html():
        html = path.read_text(encoding="utf-8")
        orig = html
        html = rename_explore(html)
        html = remove_inline_setup(html)
        html = ensure_highlight_script(html, path)
        if html != orig:
            path.write_text(html, encoding="utf-8", newline="\n")
            print(f"  patched: {path.relative_to(ROOT)}")
            changed += 1
    print(f"Done. Patched {changed} files.")


if __name__ == "__main__":
    main()
