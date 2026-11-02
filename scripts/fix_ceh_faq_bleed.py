# -*- coding: utf-8 -*-
"""
Replace inherited CEH FAQ blocks (and leftover CEH meta) on non-CEH course pages.

Keeps ceh.html untouched. Safe to re-run.
"""
from __future__ import annotations

import html as html_lib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CEH_FAQ_HEAD = "Certified Ethical Hacker (CEH v13)<br><em>FAQs.</em>"
CEH_KEYWORDS = (
    "CEH v13, Certified Ethical Hacker, EC-Council, ethical hacking training "
    "Malaysia, CEH certification, penetration testing"
)
CEH_META_MARKERS = (
    "CEH v13",
    "Certified Ethical Hacker",
    "ethical hacking training",
    "EC-Council CEH",
)

FAQ_SECTION_RE = re.compile(
    r'<div id="sec-faq" class="content-sec"[^>]*>.*?</div>\s*</div>\s*(?=\s*</div><!-- /main -->)',
    re.DOTALL | re.I,
)
COURSE_TITLE_RE = re.compile(
    r'<h1\s+class="course-title">(.*?)</h1>',
    re.DOTALL | re.I,
)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL | re.I)
TAG_RE = re.compile(r"<[^>]+>")


def strip_tags(s: str) -> str:
    t = TAG_RE.sub(" ", s)
    t = html_lib.unescape(t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def course_display_name(html: str, path: Path) -> str:
    m = COURSE_TITLE_RE.search(html)
    if m:
        name = strip_tags(m.group(1))
        if name and "Certified Ethical Hacker" not in name:
            return name
    m = TITLE_RE.search(html)
    if m:
        raw = strip_tags(m.group(1))
        for sep in (" | ", " — ", " – ", " - "):
            if sep in raw:
                raw = raw.split(sep)[0].strip()
                break
        raw = re.sub(
            r"\s*(Training|Course)\s+Malaysia\s*$",
            "",
            raw,
            flags=re.I,
        ).strip()
        if raw and "Certified Ethical Hacker" not in raw and "CEH" not in raw:
            return raw
    slug = path.stem.replace("-", " ").title()
    return slug


def esc(s: str) -> str:
    return html_lib.escape(s, quote=True)


def build_faq_section(name: str) -> str:
    n = esc(name)
    return f"""  <div id="sec-faq" class="content-sec" style="display:none">
    <div class="eyebrow">FAQs</div>
    <h2 class="sec-head">{n}<br><em>FAQs.</em></h2>
    <div class="modules" style="margin-top:18px">
      <button class="module open" onclick="toggleModule(this)">
        <div class="module-header">
          <span class="module-num">01</span>
          <h4>Who is {n} for?</h4>
          <span class="module-arrow">›</span>
        </div>
        <div class="module-body">
          <div class="body-text" style="margin-top:12px">Professionals and learners who want practical, instructor-led {n} training with Malaysian workplace examples and clear next-step guidance.</div>
        </div>
      </button>
      <button class="module" onclick="toggleModule(this)">
        <div class="module-header">
          <span class="module-num">02</span>
          <h4>Is this online or classroom?</h4>
          <span class="module-arrow">›</span>
        </div>
        <div class="module-body">
          <div class="body-text" style="margin-top:12px">Both — on-site, virtual and hybrid cohorts are available. Ask enrolment for the next intake format.</div>
        </div>
      </button>
      <button class="module" onclick="toggleModule(this)">
        <div class="module-header">
          <span class="module-num">03</span>
          <h4>What certificate or outcome do I get?</h4>
          <span class="module-arrow">›</span>
        </div>
        <div class="module-body">
          <div class="body-text" style="margin-top:12px">You receive structured training toward the {n} learning outcomes. Where a vendor exam applies, our team confirms voucher inclusion and exam readiness support at enrolment.</div>
        </div>
      </button>
      <button class="module" onclick="toggleModule(this)">
        <div class="module-header">
          <span class="module-num">04</span>
          <h4>Can my company claim HRD Corp?</h4>
          <span class="module-arrow">›</span>
        </div>
        <div class="module-body">
          <div class="body-text" style="margin-top:12px">Eligible employers can request claim support — share your company details with our enrolment team.</div>
        </div>
      </button>
      <button class="module" onclick="toggleModule(this)">
        <div class="module-header">
          <span class="module-num">05</span>
          <h4>How do I enrol for {n}?</h4>
          <span class="module-arrow">›</span>
        </div>
        <div class="module-body">
          <div class="body-text" style="margin-top:12px">Use the enquiry form on this page or Contact Us. We reply within 4 business hours with intake dates, fees and delivery options.</div>
        </div>
      </button>
    </div>
  </div>"""


def page_title_short(html: str, fallback: str) -> str:
    m = TITLE_RE.search(html)
    if not m:
        return fallback
    raw = strip_tags(m.group(1))
    for sep in (" | ", " — ", " – "):
        if sep in raw:
            return raw.split(sep)[0].strip() or fallback
    return raw or fallback


def page_description_fallback(name: str) -> str:
    return (
        f"{name} training in Malaysia with Nexperts Academy. "
        f"Practical instructor-led training, labs and enrolment support."
    )


def looks_like_ceh_meta(value: str) -> bool:
    v = value or ""
    return any(m in v for m in CEH_META_MARKERS)


def replace_meta_content(html: str, attr: str, new_value: str) -> str:
    """Replace content= for name= or property= meta tags."""
    safe = html_lib.escape(new_value, quote=True).replace("&#x27;", "'")

    def _sub(m: re.Match[str]) -> str:
        return m.group(1) + safe + m.group(3)

    patterns = [
        rf'(<meta\s+name="{re.escape(attr)}"\s+content=")(.*?)("\s*/?>)',
        rf'(<meta\s+property="{re.escape(attr)}"\s+content=")(.*?)("\s*/?>)',
        rf'(<meta\s+content=")(.*?)("\s+name="{re.escape(attr)}"\s*/?>)',
        rf'(<meta\s+content=")(.*?)("\s+property="{re.escape(attr)}"\s*/?>)',
    ]
    for pat in patterns:
        out, n = re.subn(pat, _sub, html, count=1, flags=re.I)
        if n:
            return out
    return html


def fix_meta(html: str, name: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    title_short = page_title_short(html, name)
    desc_fallback = page_description_fallback(name)
    keywords = (
        f"{name} training Malaysia, {name} course, "
        f"{title_short}, Nexperts Academy"
    )[:220]

    # keywords
    km = re.search(
        r'<meta\s+name="keywords"\s+content="([^"]*)"',
        html,
        re.I,
    )
    if km and (km.group(1).strip() == CEH_KEYWORDS or looks_like_ceh_meta(km.group(1))):
        html = replace_meta_content(html, "keywords", keywords)
        changes.append("keywords")

    for prop, fallback in (
        ("og:title", title_short),
        ("twitter:title", title_short),
        ("og:description", desc_fallback),
        ("twitter:description", desc_fallback),
        ("description", desc_fallback),
    ):
        # description uses name=
        attr = "description" if prop == "description" else prop
        if prop == "description":
            m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html, re.I)
        else:
            m = re.search(
                rf'<meta\s+property="{re.escape(prop)}"\s+content="([^"]*)"',
                html,
                re.I,
            )
            if not m and prop.startswith("twitter:"):
                m = re.search(
                    rf'<meta\s+name="{re.escape(prop)}"\s+content="([^"]*)"',
                    html,
                    re.I,
                )
        if m and looks_like_ceh_meta(m.group(1)):
            # Prefer existing non-CEH title page description if og was wrong but name description ok
            if prop.endswith("description"):
                dm = re.search(
                    r'<meta\s+name="description"\s+content="([^"]*)"',
                    html,
                    re.I,
                )
                value = (
                    dm.group(1)
                    if dm and not looks_like_ceh_meta(dm.group(1))
                    else fallback
                )
            else:
                # titles: prefer <title> short
                value = title_short
            html = replace_meta_content(html, attr if prop != "description" else "description", value)
            # twitter uses name= often
            if prop.startswith("twitter:"):
                html = re.sub(
                    rf'(<meta\s+name="{re.escape(prop)}"\s+content=")(.*?)("\s*/?>)',
                    lambda m, v=value: m.group(1)
                    + html_lib.escape(v, quote=True).replace("&#x27;", "'")
                    + m.group(3),
                    html,
                    count=1,
                    flags=re.I,
                )
            changes.append(prop)

    return html, changes


def is_ceh_page(path: Path) -> bool:
    return path.name.lower() == "ceh.html"


def process_file(path: Path) -> str:
    if is_ceh_page(path):
        return "skip-ceh"
    try:
        html = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR {path}: {exc}", file=sys.stderr)
        return "error"

    changed = False
    notes: list[str] = []
    name = course_display_name(html, path)

    if CEH_FAQ_HEAD in html or "Is CEH certification worth it in Malaysia?" in html:
        m = FAQ_SECTION_RE.search(html)
        if not m:
            print(f"WARN no FAQ block match: {path.relative_to(ROOT)}", file=sys.stderr)
            return "warn-faq"
        html = FAQ_SECTION_RE.sub(build_faq_section(name), html, count=1)
        changed = True
        notes.append("faq")

    html2, meta_notes = fix_meta(html, name)
    if meta_notes:
        html = html2
        changed = True
        notes.extend(meta_notes)

    if not changed:
        return "unchanged"

    path.write_text(html, encoding="utf-8", newline="\n")
    return "ok:" + ",".join(notes)


def iter_targets() -> list[Path]:
    files: list[Path] = []
    courses = ROOT / "courses"
    if courses.is_dir():
        files.extend(sorted(courses.glob("*.html")))
    # Root vanity course pages that may have inherited CEH FAQ
    for name in ("ccna.html", "python-bootcamp.html", "data-science-with-python.html"):
        p = ROOT / name
        if p.is_file():
            files.append(p)
    return files


def main() -> int:
    ok = 0
    skip = 0
    fail = 0
    for path in iter_targets():
        status = process_file(path)
        rel = path.relative_to(ROOT).as_posix()
        if status.startswith("ok:"):
            ok += 1
            print(f"OK {rel} ({status[3:]})")
        elif status in ("unchanged", "skip-ceh"):
            skip += 1
        else:
            fail += 1
            print(f"FAIL {rel} ({status})", file=sys.stderr)
    print(f"Fixed {ok} page(s); skipped {skip}; failed {fail}")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
