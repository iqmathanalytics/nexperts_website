# -*- coding: utf-8 -*-
"""JSON-LD schema blocks for /courses/oscp (from schema_imp.txt)."""

from pathlib import Path

_SCHEMA_FILE = Path(__file__).parent / "schema_imp.txt"
OSCP_SCHEMA_MARKUP = _SCHEMA_FILE.read_text(encoding="utf-8").strip()
