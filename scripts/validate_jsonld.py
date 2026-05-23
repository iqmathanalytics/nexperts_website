#!/usr/bin/env python3
import json, re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
files = [
    "index.html",
    "ccna.html",
    "courses/aws-solutions-architect-associate.html",
    "courses/cisco-dccor.html",
    "courses/cisco-spcor.html",
    "courses/excel-advanced-analytics.html",
    "courses/excel-basic.html",
]
for rel in files:
    p = root / rel
    h = p.read_text(encoding="utf-8")
    blocks = re.findall(
        r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
        h,
        re.S,
    )
    errs = []
    for i, b in enumerate(blocks, 1):
        try:
            json.loads(b)
        except Exception as e:
            errs.append(f"block {i}: {e}")
    status = "OK" if not errs else "; ".join(errs)
    print(f"{rel}: {len(blocks)} blocks — {status}")
