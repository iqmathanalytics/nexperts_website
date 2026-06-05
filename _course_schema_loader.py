# -*- coding: utf-8 -*-
"""Load Course + FAQPage JSON-LD blocks from schema_imp.txt."""

from __future__ import annotations

import re
from pathlib import Path

_DEFAULT_SCHEMA_FILE = Path(__file__).parent / "schema_imp.txt"


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
    blocks = _json_blocks(src.read_text(encoding="utf-8"))
    page_blocks = [b for b in blocks if '"@type": "Course"' in b or '"@type": "FAQPage"' in b]
    scripts = []
    for block in page_blocks:
        block = re.sub(r"\n\s+", "\n", block)
        scripts.append(f'<script type="application/ld+json">\n{block}\n</script>')
    return "\n".join(scripts)
