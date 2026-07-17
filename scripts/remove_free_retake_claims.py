# -*- coding: utf-8 -*-
"""Remove free-retake / free-retake-voucher claims from course batches and HTML."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_GUARANTEE = (
    "Follow our programme and clear the mock threshold before booking. "
    "Dedicated exam coaching and instructor support included."
)

RETAKE_TOKEN = re.compile(
    r"free (?:single )?retake|retake voucher|voucher on us|cover one retake|"
    r"free exam retake|complimentary remediation|free retake \(lf policy\)|"
    r"free single retake \(linux foundation policy\)",
    re.IGNORECASE,
)


def _is_retake_phrase(s: str) -> bool:
    return bool(RETAKE_TOKEN.search(s))


def clean_batch_text(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Drop whats_included string items about free retake
        if stripped.startswith('"') and _is_retake_phrase(stripped) and (
            "retake" in stripped.lower()
        ):
            # Keep lines that are not include/pill items (e.g. long guarantee already handled)
            if stripped.endswith(",") or stripped.endswith('",') or stripped.endswith('"'):
                # Likely a list item
                if "guarantee_text" not in stripped and "pass_pills" not in stripped:
                    i += 1
                    continue

        # Drop exam table Retake rows
        if re.search(r'\(\s*"Retake"\s*,\s*"(?:One complimentary|One included)"\s*\)', line, re.I):
            i += 1
            continue

        # Replace guarantee_text values that mention retake/voucher-on-us
        if "guarantee_text=" in line and _is_retake_phrase(line):
            indent = line[: len(line) - len(line.lstrip())]
            out.append(f'{indent}guarantee_text="{DEFAULT_GUARANTEE}",\n')
            i += 1
            continue

        # Clean pass_pills inline lists
        if "pass_pills=" in line and _is_retake_phrase(line):
            cleaned = re.sub(
                r',\s*"[^"]*(?:[Ff]ree (?:single )?retake|[Rr]etake voucher)[^"]*"',
                "",
                line,
            )
            cleaned = re.sub(
                r'"[^"]*(?:[Ff]ree (?:single )?retake|[Rr]etake voucher)[^"]*"\s*,\s*',
                "",
                cleaned,
            )
            out.append(cleaned)
            i += 1
            continue

        out.append(line)
        i += 1

    text = "".join(out)
    text = re.sub(r",\s*,", ",", text)
    text = re.sub(r"\[\s*,", "[", text)
    text = re.sub(r",\s*\]", "]", text)
    return text


def clean_html_text(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        low = line.lower()
        if 'class="include-item"' in line and _is_retake_phrase(line):
            continue
        if 'class="ppill' in line and _is_retake_phrase(line):
            continue
        if "<p>" in line and "</p>" in line and _is_retake_phrase(line) and (
            "retake" in low or "voucher on us" in low
        ):
            # guarantee paragraph
            if "follow our programme" in low or "hit the" in low or "hit our" in low or "clear the" in low or "don't pass" in low or "attend full course" in low:
                indent = re.match(r"^(\s*)", line).group(1)
                out.append(f"{indent}<p>{DEFAULT_GUARANTEE}</p>\n")
                continue
        out.append(line)

    text = "".join(out)

    # Bootcamp / legacy free-exam-retake sentence
    text = text.replace(
        "If a participant does not pass on the first attempt, Nexperts Academy provides a free exam retake and exam preparation support.",
        "Nexperts Academy provides structured exam preparation support for certification candidates.",
    )
    text = text.replace(
        "If a participant does not pass on the first attempt, Nexperts Academy provides a free exam retake and exam preparation support",
        "Nexperts Academy provides structured exam preparation support for certification candidates",
    )

    # FAQ / body-text blocks with retake voucher offers
    text = re.sub(
        r'(<div class="body-text"[^>]*>)([^<]*(?:retake voucher|free exam retake|cover one[^<]*retake)[^<]*)(</div>)',
        rf'\1{DEFAULT_GUARANTEE}\3',
        text,
        flags=re.IGNORECASE,
    )
    return text


def main() -> None:
    batch_files = sorted(ROOT.glob("_course_batch*.py"))
    changed_batches = 0
    for path in batch_files:
        print(f"scanning batch {path.name}...", flush=True)
        orig = path.read_text(encoding="utf-8")
        new = clean_batch_text(orig)
        if new != orig:
            path.write_text(new, encoding="utf-8", newline="\n")
            changed_batches += 1
            print(f"  updated batch: {path.name}", flush=True)

    html_paths = list(ROOT.glob("courses/*.html"))
    for name in (
        "ceh.html",
        "ccna.html",
        "index.html",
        "about.html",
        "python-bootcamp.html",
        "data-science-with-python.html",
    ):
        html_paths.append(ROOT / name)
    html_paths.extend((ROOT / "blog").glob("*.html"))

    changed_html = 0
    for path in html_paths:
        if not path.is_file():
            continue
        orig = path.read_text(encoding="utf-8")
        new = clean_html_text(orig)
        if new != orig:
            path.write_text(new, encoding="utf-8", newline="\n")
            changed_html += 1
            print(f"  updated html: {path.relative_to(ROOT)}", flush=True)

    print(f"Updated {changed_batches} batch files, {changed_html} HTML files.", flush=True)


if __name__ == "__main__":
    main()
