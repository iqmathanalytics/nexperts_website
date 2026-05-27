# -*- coding: utf-8 -*-
"""Build blog article pages from docx and migrate /post → /blog URLs."""
from __future__ import annotations

import html as html_lib
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from site_nav import NAV_ASSET_TAGS, render_site_nav  # noqa: E402

SITE = "https://www.nexpertsacademy.com"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"

DATA_SCIENCE_SLUG = "unlocking-the-power-of-data-science-applications-and-challenges"
CCNA_SLUG = "ccna-certification-guide"
CCNA_IMG_SLUG = "ccna-certification-guide-complete-beginner-roadmap-2026"
CCNA_META_TITLE = "CCNA Certification Guide 2026: Complete Beginner Roadmap"
CCNA_META_DESC = (
    "Learn what CCNA is, exam details, salary, career paths, study roadmap, "
    "and how beginners can pass the Cisco CCNA 200-301 certification"
)
DOCX = ROOT / "CCNA Certification Guide_ Complete Beginner Roadmap in 2026.docx"
IMG_DIR = ROOT / "image" / "blog" / CCNA_IMG_SLUG


def _esc(s: str) -> str:
    return html_lib.escape(s, quote=False)


def _run_text(run: ET.Element) -> str:
    parts: list[str] = []
    if run.find(f"{W}rPr/{W}b") is not None:
        wrap = lambda t: f"<strong>{_esc(t)}</strong>" if t else ""
    else:
        wrap = _esc
    for node in run:
        tag = node.tag
        if tag == f"{W}t":
            parts.append(wrap(node.text or ""))
        elif tag == f"{W}tab":
            parts.append(" ")
        elif tag == f"{W}br":
            parts.append("<br>")
    return "".join(parts)


def _paragraph_html(p: ET.Element, rel_map: dict[str, str], img_counter: list[int]) -> str | None:
  # images
    for drawing in p.iter(f"{W}drawing"):
        for blip in drawing.iter(f"{A}blip"):
            rid = blip.get(f"{R_NS}embed")
            if not rid or rid not in rel_map:
                continue
            media = rel_map[rid].split("/")[-1]
            img_counter[0] += 1
            fname = f"image{img_counter[0]}{Path(media).suffix.lower()}"
            src = f"/image/blog/{CCNA_IMG_SLUG}/{fname}"
            return (
                f'<figure class="blog-figure"><img src="{src}" alt="" loading="lazy" width="720" height="405">'
                f"</figure>"
            )

    texts: list[str] = []
    for child in p:
        if child.tag == f"{W}r":
            texts.append(_run_text(child))
    text = "".join(texts).strip()
    if not text:
        return None

    p_pr = p.find(f"{W}pPr")
    style = ""
    if p_pr is not None:
        ps = p_pr.find(f"{W}pStyle")
        if ps is not None:
            style = ps.get(f"{W}val") or ""

    num = p_pr.find(f"{W}numPr") if p_pr is not None else None
    if num is not None:
        return f"<li>{text}</li>"

    if style == "Heading1":
        return None  # title handled in hero
    if style == "Heading2":
        return f"<h2>{text}</h2>"
    if style == "Heading3":
        return f"<h3>{text}</h3>"
    if text == "Key Takeaways":
        return "<h2>Key Takeaways</h2>"
    return f"<p>{text}</p>"


def docx_to_body(docx_path: Path) -> tuple[str, str, str]:
    """Return title, description, body HTML."""
    z = zipfile.ZipFile(docx_path)
    rels = ET.fromstring(z.read("word/_rels/document.xml.rels"))
    rel_map = {
        rel.get("Id"): rel.get("Target")
        for rel in rels.findall(f"{REL_NS}Relationship")
    }
    root = ET.fromstring(z.read("word/document.xml"))
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    img_counter = [0]
    saved_media: dict[str, str] = {}

    blocks: list[str] = []
    list_buf: list[str] = []
    title = ""

    def flush_list() -> None:
        nonlocal list_buf
        if list_buf:
            blocks.append("<ul>" + "".join(list_buf) + "</ul>")
            list_buf = []

    for p in root.iter(f"{W}p"):
        # extract images first and save files
        for drawing in p.iter(f"{W}drawing"):
            for blip in drawing.iter(f"{A}blip"):
                rid = blip.get(f"{R_NS}embed")
                if rid and rid in rel_map:
                    target = rel_map[rid]
                    media_name = target.split("/")[-1]
                    if rid not in saved_media:
                        img_counter[0] += 1
                        ext = Path(media_name).suffix.lower() or ".jpg"
                        fname = f"image{img_counter[0]}{ext}"
                        saved_media[rid] = fname
                        (IMG_DIR / fname).write_bytes(z.read(f"word/{target.lstrip('/')}"))
                    fname = saved_media[rid]
                    flush_list()
                    blocks.append(
                        f'<figure class="blog-figure"><img src="/image/blog/{CCNA_IMG_SLUG}/{fname}" '
                        f'alt="CCNA certification guide illustration" loading="lazy" width="720" height="405"></figure>'
                    )
                    break

        p_pr = p.find(f"{W}pPr")
        style = ""
        is_list = False
        if p_pr is not None:
            ps = p_pr.find(f"{W}pStyle")
            if ps is not None:
                style = ps.get(f"{W}val") or ""
            if p_pr.find(f"{W}numPr") is not None:
                is_list = True

        texts: list[str] = []
        for child in p:
            if child.tag == f"{W}r":
                texts.append(_run_text(child))
        text = "".join(texts).strip()
        if not text:
            continue

        if style == "Heading1" and not title:
            title = re.sub(r"<[^>]+>", "", text)
            continue

        if is_list:
            list_buf.append(f"<li>{text}</li>")
            continue

        flush_list()

        if style == "Heading2" or (not style and text == "Key Takeaways"):
            blocks.append(f"<h2>{text}</h2>")
        elif style == "Heading3":
            blocks.append(f"<h3>{text}</h3>")
        else:
            blocks.append(f"<p>{text}</p>")

    flush_list()
    body = "\n    ".join(blocks)
    desc = ""
    for b in blocks:
        if b.startswith("<p>"):
            desc = re.sub(r"<[^>]+>", "", b)[:160]
            break
    if not title:
        title = "CCNA Certification Guide: Complete Beginner Roadmap in 2026"
    return title, desc, body


EXAM_DETAILS_TABLE = """
        <div class="blog-table-wrap">
          <table class="blog-table">
            <thead><tr><th scope="col">Feature</th><th scope="col">Details</th><th scope="col">Key Insight</th></tr></thead>
            <tbody>
              <tr><td>Exam Duration</td><td>120 Minutes</td><td>Time management is critical.</td></tr>
              <tr><td>Question Types</td><td>Multiple-choice, Labs, Drag-and-drop</td><td>Practical skills are tested.</td></tr>
              <tr><td>Passing Score</td><td>Scaled (Not Public)</td><td>Aim for full topic mastery.</td></tr>
              <tr><td>Language Options</td><td>English, Japanese</td><td>Check local testing centers.</td></tr>
            </tbody>
          </table>
        </div>"""

STUDY_METHOD_TABLE = """
        <div class="blog-table-wrap">
          <table class="blog-table">
            <thead><tr><th scope="col">Study Method</th><th scope="col">Primary Benefit</th><th scope="col">Recommended Frequency</th></tr></thead>
            <tbody>
              <tr><td>Video Courses</td><td>Visual Learning</td><td>Daily</td></tr>
              <tr><td>Hands-on Labs</td><td>Practical Skill</td><td>3-4 Times Weekly</td></tr>
              <tr><td>Practice Exams</td><td>Exam Readiness</td><td>Weekly (Final Month)</td></tr>
            </tbody>
          </table>
        </div>"""

COMPARE_TABLE = """
        <div class="blog-table-wrap">
          <table class="blog-table blog-table--compare">
            <thead><tr><th scope="col">Feature</th><th scope="col">Network+</th><th scope="col">CCNA</th></tr></thead>
            <tbody>
              <tr><td>Focus</td><td>Vendor-Neutral</td><td>Cisco-Specific</td></tr>
              <tr><td>Difficulty</td><td>Beginner</td><td>Intermediate</td></tr>
              <tr><td>Career Value</td><td>General IT Support</td><td>Network Engineering</td></tr>
            </tbody>
          </table>
        </div>"""


def _fix_ccna_body_tables(body: str) -> str:
    """Replace docx-exported table paragraphs with HTML tables."""
    exam_old = (
        "<p><strong>Feature</strong></p>\n"
        "        <p><strong>Details</strong></p>\n"
        "        <p><strong>Key Insight</strong></p>\n"
        "        <p>Exam Duration</p>\n"
        "        <p>120 Minutes</p>\n"
        "        <p>Time management is critical.</p>\n"
        "        <p>Question Types</p>\n"
        "        <p>Multiple-choice, Labs, Drag-and-drop</p>\n"
        "        <p>Practical skills are tested.</p>\n"
        "        <p>Passing Score</p>\n"
        "        <p>Scaled (Not Public)</p>\n"
        "        <p>Aim for full topic mastery.</p>\n"
        "        <p>Language Options</p>\n"
        "        <p>English, Japanese</p>\n"
        "        <p>Check local testing centers.</p>"
    )
    study_old = (
        "<p><strong>Study Method</strong></p>\n"
        "        <p><strong>Primary Benefit</strong></p>\n"
        "        <p><strong>Recommended Frequency</strong></p>\n"
        "        <p>Video Courses</p>\n"
        "        <p>Visual Learning</p>\n"
        "        <p>Daily</p>\n"
        "        <p>Hands-on Labs</p>\n"
        "        <p>Practical Skill</p>\n"
        "        <p>3-4 Times Weekly</p>\n"
        "        <p>Practice Exams</p>\n"
        "        <p>Exam Readiness</p>\n"
        "        <p>Weekly (Final Month)</p>"
    )
    compare_old = (
        "<p><strong>Feature</strong></p>\n"
        "        <p><strong>Network+</strong></p>\n"
        "        <p><strong>CCNA</strong></p>\n"
        "        <p>Focus</p>\n"
        "        <p>Vendor-Neutral</p>\n"
        "        <p>Cisco-Specific</p>\n"
        "        <p>Difficulty</p>\n"
        "        <p>Beginner</p>\n"
        "        <p>Intermediate</p>\n"
        "        <p>Career Value</p>\n"
        "        <p>General IT Support</p>\n"
        "        <p>Network Engineering</p>"
    )
    body = body.replace(exam_old, EXAM_DETAILS_TABLE)
    body = body.replace(study_old, STUDY_METHOD_TABLE)
    body = body.replace(compare_old, COMPARE_TABLE)
    body = body.replace(
        '<p>"Tell me and I forget, teach me and I may remember, involve me and I learn."</p>\n'
        "        <p>Benjamin Franklin</p>",
        '<blockquote class="blog-quote"><p>"Tell me and I forget, teach me and I may remember, involve me and I learn."</p><cite>Benjamin Franklin</cite></blockquote>',
    )
    return body


def _blog_article_html(
    *,
    path: str,
    title: str,
    title_em: str,
    description: str,
    hero_meta: str,
    body_html: str,
    related_cards: list[tuple[str, str, str]],
) -> str:
    canon = f"{SITE}{path}"
    nav = render_site_nav(variant="inner", current_path=path)
    cards_html = ""
    if related_cards:
        cards_html = '    <div class="card-grid">\n'
        for name, desc, href in related_cards:
            cards_html += (
                f'      <a class="card" href="{html_lib.escape(href)}">\n'
                f"        <h3>{_esc(name)}</h3>\n"
                f"        <p>{_esc(desc)}</p>\n"
                f'        <span class="card-link">Learn more →</span>\n'
                f"      </a>\n"
            )
        cards_html += "    </div>\n"

    crumb = title.split(":")[0] if ":" in title else title
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_esc(title)} | Nexperts Academy Blog</title>
<meta name="description" content="{_esc(description)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{_esc(title)} | Nexperts Academy">
<meta property="og:description" content="{_esc(description)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/image/nexperts-logo.png">
<meta property="og:site_name" content="Nexperts Academy">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,300;1,9..144,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/site-nav-mobile.css">
{NAV_ASSET_TAGS}
<link rel="stylesheet" href="/css/blog.css">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#f8fbff;--ink:#0f1b2d;--ink2:#2a3f5f;--ink3:#4b6284;--ink4:#7e97b8;--blue:#1d4ed8;--line:#d7e6fb;--line2:#bfd5f2}}
html{{scroll-behavior:smooth;background:var(--bg)}}
body{{font-family:'Plus Jakarta Sans',sans-serif;background:var(--bg);color:var(--ink);line-height:1.65;font-size:15px;padding-top:62px}}
.hero{{padding:48px 40px 48px;text-align:center;background:linear-gradient(180deg,#eef6ff,#f8fbff);border-bottom:1px solid var(--line)}}
.hero h1{{font-family:'Fraunces',serif;font-weight:300;font-size:clamp(2rem,4vw,2.8rem);margin-bottom:12px}}
.hero h1 em{{font-style:italic;color:var(--blue)}}
.hero p{{color:var(--ink2);max-width:720px;margin:0 auto}}
.card-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-top:32px}}
.card{{display:block;padding:20px;background:#fff;border:1px solid var(--line);border-radius:12px;text-decoration:none;color:inherit;transition:transform .2s,box-shadow .2s}}
.card:hover{{transform:translateY(-3px);box-shadow:0 12px 32px rgba(29,78,216,.12)}}
.card h3{{font-size:.95rem;margin-bottom:8px;color:var(--ink)}}
.card p{{font-size:.82rem;color:var(--ink3);margin:0}}
.card-link{{display:inline-block;margin-top:12px;font-size:.78rem;font-weight:700;color:var(--blue)}}
footer{{background:#0d1117;color:rgba(255,255,255,.5);text-align:center;padding:32px 24px;font-size:.75rem}}
footer a{{color:rgba(255,255,255,.65);text-decoration:none}}
</style>
</head>
<body class="blog-page">
{nav}
<section class="hero">
  <p style="font-size:.72rem;color:var(--ink3);margin-bottom:14px"><a href="/" style="color:inherit;text-decoration:none">Home</a> / <a href="/blog" style="color:inherit;text-decoration:none">Blog</a> / {_esc(crumb[:48])}</p>
  <h1>{_esc(title.split(":")[0] if ":" in title else title)}<br><em>{_esc(title_em)}</em></h1>
  <p>{_esc(hero_meta)}</p>
</section>
<section class="content legal-prose">
  <a class="blog-back" href="/blog">← Back to Blog</a>
    {body_html}
{cards_html}
  <p style="margin-top:2rem"><a href="/contact-us#enquire" style="color:var(--blue);font-weight:700">Enquire about CCNA training →</a></p>
</section>
<footer>
  <p>© Nexperts Academy Sdn Bhd · <a href="/">Home</a> · <a href="/blog">Blog</a> · <a href="/privacy-policy">Privacy</a></p>
</footer>
<script src="/js/site-nav-mobile.js" defer></script>
</body>
</html>
"""


def build_data_science_post() -> None:
    old = ROOT / "post" / f"{DATA_SCIENCE_SLUG}.html"
    body_parts = """    <p>Data science is no longer a Silicon Valley headline — Malaysian banks, telcos, retailers and government agencies run production models for fraud, churn, demand forecasting and personalisation. The gap is not awareness; it is disciplined execution.</p>
    <p>Applications that work locally share traits: labelled data with ownership, a sponsor who accepts imperfection in v1, and engineers who can deploy — not only notebook heroes. Common wins include credit risk feature stores, network fault prediction, inventory optimisation and customer lifetime value segmentation.</p>
    <p>Challenges are equally consistent: siloed spreadsheets as 'source of truth', under-funded data engineering, metric gaming, and procurement cycles that buy GPUs before governance. PDPA and sector guidelines (BNM, MCMC) mean consent, retention and explainability are design requirements, not legal footnotes.</p>
    <p>A pragmatic roadmap: (1) fix data access and definitions, (2) ship one measurable model with monitoring, (3) industrialise feature pipelines, (4) scale team skills via hybrid hiring and targeted upskilling — bootcamps for literacy, certifications for platform depth.</p>
    <p>Nexperts runs SQL for Data Professionals, AI/ML bootcamps and Microsoft DP-100 / AI-102 programmes with MY-context labs. If you are sponsoring a pilot, start with a problem owner, a baseline metric and an eight-week delivery window — not a generic 'AI strategy' slide.</p>"""

    html = _blog_article_html(
        path=f"/blog/{DATA_SCIENCE_SLUG}",
        title="Unlocking the Power of Data Science",
        title_em="Applications & challenges",
        description="Unlocking the power of data science — applications and challenges for Malaysian enterprises adopting analytics and machine learning.",
        hero_meta="12 March 2025 · Nexperts Data Practice",
        body_html=body_parts,
        related_cards=[
            ("AI & ML Bootcamp", "Practitioner sprint.", "/courses/ai-ml-bootcamp"),
            ("SQL for Data Professionals", "Enterprise analytics foundation.", "/courses/sql-for-data-professionals"),
            ("Contact", "Corporate training enquiry.", "/contact-us"),
        ],
    )
    html = html.replace("Enquire about CCNA training →", "Enquire about this programme →")
    out = ROOT / "blog" / f"{DATA_SCIENCE_SLUG}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8", newline="\n")
    print(f"  blog: {out.relative_to(ROOT)}")
    if old.is_file():
        old.unlink()
        print(f"  removed: {old.relative_to(ROOT)}")


def build_ccna_post() -> None:
    if not DOCX.is_file():
        raise SystemExit(f"Missing docx: {DOCX}")
    title, desc, body = docx_to_body(DOCX)
    body = _fix_ccna_body_tables(body)
    body_html = "    " + body.replace("\n", "\n    ")
    body_html = body_html.replace(
        "clear grasp of the CCNA certification.",
        'clear grasp of the <a href="https://www.nexpertsacademy.com/ccna">CCNA certification</a>.',
    )
    html = _blog_article_html(
        path=f"/blog/{CCNA_SLUG}",
        title=title,
        title_em="Complete beginner roadmap in 2026",
        description=CCNA_META_DESC,
        hero_meta="May 2026 · Nexperts Cisco Practice",
        body_html=body_html,
        related_cards=[
            ("CCNA Training", "Official Cisco CCNA 200-301 programme.", "/ccna"),
            ("CCNP Enterprise", "Next step after CCNA.", "/courses/ccnp-enterprise"),
            ("Contact", "Corporate training enquiry.", "/contact-us"),
        ],
    )
    html = html.replace(
        f"<title>{_esc(title)} | Nexperts Academy Blog</title>",
        f"<title>{_esc(CCNA_META_TITLE)}</title>",
    )
    html = html.replace(
        f'<meta property="og:title" content="{_esc(title)} | Nexperts Academy">',
        f'<meta property="og:title" content="{_esc(CCNA_META_TITLE)}">',
    )
    out = ROOT / "blog" / f"{CCNA_SLUG}.html"
    out.write_text(html, encoding="utf-8", newline="\n")
    print(f"  blog: {out.relative_to(ROOT)} ({len(body)} chars body)")


def patch_redirects() -> None:
    path = ROOT / "_redirects"
    text = path.read_text(encoding="utf-8")
    rules = [
        f"/post/{DATA_SCIENCE_SLUG} /blog/{DATA_SCIENCE_SLUG} 301",
        f"/post/{DATA_SCIENCE_SLUG}.html /blog/{DATA_SCIENCE_SLUG} 301",
    ]
    for rule in rules:
        src = rule.split()[0]
        if src not in text:
            text = text.rstrip() + f"\n{rule}\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    print("  patched _redirects")


def patch_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    old = f"{SITE}/post/{DATA_SCIENCE_SLUG}"
    new_urls = [
        f"  <url><loc>{SITE}/blog/{DATA_SCIENCE_SLUG}</loc><changefreq>yearly</changefreq><priority>0.6</priority></url>",
        f"  <url><loc>{SITE}/blog/{CCNA_SLUG}</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>",
    ]
    text = text.replace(
        f"  <url><loc>{old}</loc><changefreq>yearly</changefreq><priority>0.6</priority></url>",
        "\n".join(new_urls),
    )
    if CCNA_SLUG not in text:
        text = text.replace(
            f"  <url><loc>{SITE}/blog</loc>",
            f"  <url><loc>{SITE}/blog/{CCNA_SLUG}</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>\n  <url><loc>{SITE}/blog</loc>",
        )
    path.write_text(text, encoding="utf-8", newline="\n")
    print("  patched sitemap.xml")


def main() -> None:
    build_data_science_post()
    build_ccna_post()
    patch_redirects()
    patch_sitemap()
    print("Done. Run: python scripts/inject_addons_nav.py")


if __name__ == "__main__":
    main()
