# -*- coding: utf-8 -*-
"""Build legacy Wix SEO pages: courses/*.html + static content pages + redirects.

Run from repo root:
    python scripts/build_legacy_seo_pages.py
"""
from __future__ import annotations

import html as html_lib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from _build_course_pages import build_page  # noqa: E402
from _course_batch_legacy_wix import BATCH as LEGACY_COURSES  # noqa: E402
from site_nav import NAV_ASSET_TAGS, render_site_nav  # noqa: E402

SITE = "https://www.nexpertsacademy.com"

# 301 redirects: legacy path → canonical destination
REDIRECT_301: dict[str, str] = {
    "/sql": "/courses/sql-for-data-professionals",
    "/enarsi": "/courses/ccnp-enterprise",
    "/ccnp-enarsi-sdwan": "/courses/ccnp-enterprise",
    "/microsoft-excel-2019-basic": "/courses/excel-basic",
    "/microsoft-excel-2019-advanced": "/courses/excel-advanced-analytics",
    "/microsoft-excel-2019-intermediate": "/courses/excel-advanced-analytics",
    "/javascript-front-end": "/courses/full-stack-web-development",
    "/machine-learning-with-python": "/courses/dp-100",
    "/ethical-hacking-workshop": "/ceh",
    "/power-bi-workshop": "/courses/pl-300",
}
for _c in LEGACY_COURSES:
    REDIRECT_301[f"/{_c['slug']}"] = f"/courses/{_c['slug']}"


def inject_canonical(html: str, path: str) -> str:
    canon = f"{SITE}{path}"
    if "rel=\"canonical\"" in html:
        html = re.sub(
            r'<link rel="canonical" href="[^"]*">',
            f'<link rel="canonical" href="{canon}">',
            html,
            count=1,
        )
    if 'property="og:url"' in html:
        html = re.sub(
            r'<meta property="og:url" content="[^"]*">',
            f'<meta property="og:url" content="{canon}">',
            html,
            count=1,
        )
    return html


def build_courses() -> None:
    courses_dir = ROOT / "courses"
    for c in LEGACY_COURSES:
        slug = c["slug"]
        page = build_page(c)
        page = inject_canonical(page, f"/courses/{slug}")
        (courses_dir / f"{slug}.html").write_text(page, encoding="utf-8", newline="\n")
        print(f"  courses/{slug}.html")


STATIC_PAGES: list[dict] = [
    {
        "path": "/workshops",
        "file": "workshops.html",
        "title": "Workshops",
        "title_em": "Hands-on learning",
        "description": "Nexperts Academy workshops — ethical hacking, Power BI, data analysis, mobile development and more. View upcoming sessions and past highlights.",
        "hero_sub": "Practical, instructor-led workshops for teams and individuals — from cybersecurity labs to data storytelling.",
        "sections": [
            ("What we run", "Our workshops are shorter, outcome-focused sessions alongside full certification programmes. They are ideal when you need skills this quarter, not a six-month study plan."),
            ("Popular formats", "Half-day executive briefings, two-day technical deep dives, and corporate cohorts with customised briefs. All workshops include hands-on labs or defended artefacts — not slide-only sessions."),
            ("How to book", "Browse upcoming public dates below or contact us for a closed-team quote. HRD Corp claim support is available for eligible Malaysian employers."),
        ],
        "cards": [
            ("Ethical Hacking Workshop", "Safe offensive labs in an isolated range — ideal security champion training.", "/ethical-hacking-workshop"),
            ("Power BI Workshop", "Dashboard design and DAX fundamentals for finance and ops teams.", "/power-bi-workshop"),
            ("Netflix Data Analysis", "pandas + visualization storytelling using a streaming catalogue dataset.", "/courses/netflix-data-analysis"),
            ("Cyber Security Bootcamp", "Five-day blue/red blend with SOC-style tabletop.", "/courses/cyber-security-bootcamp"),
        ],
    },
    {
        "path": "/upcoming-events",
        "file": "upcoming-events.html",
        "title": "Upcoming Events",
        "title_em": "Join us live",
        "description": "Upcoming Nexperts Academy events — workshops, community sessions, university partnerships and corporate training dates in Malaysia.",
        "hero_sub": "Hackathons, workshops, partner events and open-house sessions across Kuala Lumpur and virtual streams.",
        "sections": [
            ("Public calendar", "We publish open cohort dates for bootcamps and vendor certification courses on our homepage. This page highlights community-facing events that do not appear in the standard course catalogue."),
            ("Corporate & university", "Partner programmes (including UiTM collaborations) run on dedicated schedules. Contact us to align intake dates with your academic or fiscal calendar."),
            ("Stay informed", "Follow our announcements or enquire to receive event invitations for your team."),
        ],
        "cards": [
            ("AI & ML Bootcamp", "Sep 2026 intake — five-day practitioner sprint.", "/courses/ai-ml-bootcamp"),
            ("Cyber Security Bootcamp", "Sep 2026 — range labs + IR tabletop.", "/courses/cyber-security-bootcamp"),
            ("Netflix Data Workshop", "Oct 2026 — two-day pandas storytelling.", "/courses/netflix-data-analysis"),
            ("Contact for private dates", "Closed-team scheduling year-round.", "/contact-us"),
        ],
    },
    {
        "path": "/past-events",
        "file": "past-events.html",
        "title": "Past Events",
        "title_em": "Community highlights",
        "description": "Past Nexperts Academy events — workshops, hackathons, university partnerships and community technology programmes in Malaysia.",
        "hero_sub": "A snapshot of sessions we have delivered for students, enterprises and community partners.",
        "sections": [
            ("Community impact", "Nexperts has run ethical hacking workshops, data visualisation labs, mobile dev intro days and career talks for universities and GLCs across Malaysia."),
            ("Partnerships", "Collaborations include UiTM and corporate innovation programmes — blending certification depth with accessible community entry points."),
            ("Archives", "Photo highlights and write-ups are shared on our blog when available. Enquire if you are researching a specific past session."),
        ],
        "cards": [
            ("Catalyst for Change", "Community technology empowerment programme.", "/catalyst-for-change"),
            ("UiTM × Nexperts", "University partnership event series.", "/nexpert-x-universiti-teknologi-mara"),
            ("Chinese New Year Event", "Annual community celebration & tech talk.", "/chinese-new-year"),
            ("Tan Boon Heong Event", "Special guest session highlight.", "/tan-boon-heong-event"),
        ],
    },
    {
        "path": "/blog",
        "file": "blog.html",
        "title": "Blog",
        "title_em": "Insights & updates",
        "description": "Nexperts Academy blog — data science, cybersecurity, cloud certification tips and training news from Malaysia.",
        "hero_sub": "Practical articles from instructors and alumni — certification roadmaps, lab techniques and industry context for Malaysian IT teams.",
        "sections": [
            ("Featured", "Long-form perspectives on skills that matter locally — from SOC hiring trends to Excel analytics maturity."),
            ("Categories", "Data & AI · Cybersecurity · Networking · Cloud · Career · Community"),
            ("Contributors", "Articles are written by certified instructors with active delivery schedules — not generic content farms."),
        ],
        "cards": [
            ("Unlocking Data Science", "Applications, challenges and realistic adoption paths for Malaysian enterprises.", "/post/unlocking-the-power-of-data-science-applications-and-challenges"),
            ("Browse courses", "Full certification catalogue.", "/#courses"),
            ("Workshops", "Short-format hands-on sessions.", "/workshops"),
            ("Contact editorial", "Suggest a topic or partnership.", "/contact-us"),
        ],
    },
    {
        "path": "/catalyst-for-change",
        "file": "catalyst-for-change.html",
        "title": "Catalyst for Change",
        "title_em": "Community programme",
        "description": "Catalyst for Change — Nexperts Academy community initiative empowering Malaysians through practical technology education and mentorship.",
        "hero_sub": "Bridging ambition and opportunity with free and subsidised tech touchpoints for underserved communities.",
        "sections": [
            ("Mission", "Technology skills should not be gated by postcode or school brand. Catalyst for Change delivers intro workshops, mentorship circles and career navigation for youth and career returnees."),
            ("What happens", "Saturday labs, speaker series and partner NGO collaborations — always hands-on, never keynote-only."),
            ("Get involved", "Corporate sponsors, volunteer mentors and community organisers are welcome. Contact us to partner on the next cohort."),
        ],
        "cards": None,
    },
    {
        "path": "/empowering-community-throught-technology",
        "file": "empowering-community-throught-technology.html",
        "title": "Empowering Community Through Technology",
        "title_em": "Outreach",
        "description": "Empowering community through technology — Nexperts Academy outreach bringing digital literacy and IT career pathways to Malaysian communities.",
        "hero_sub": "Grassroots programmes that pair volunteer instructors with local partners — from rural digital literacy to urban youth coding clubs.",
        "sections": [
            ("Why it matters", "Malaysia's digital economy needs breadth, not only elite pipelines. We volunteer instructor time and donated lab seats where partners align on measurable outcomes."),
            ("Programme pillars", "Digital literacy · Safe internet · Intro to coding · Career storytelling · Parent & teacher briefings"),
            ("Partner with us", "NGOs, schools and councils can propose a cohort. We prioritise programmes with follow-up mentorship, not one-off photo ops."),
        ],
        "cards": [
            ("Catalyst for Change", "Flagship community initiative.", "/catalyst-for-change"),
            ("Upcoming events", "See public dates.", "/upcoming-events"),
            ("Volunteer", "Instructor volunteer roster.", "/contact-us"),
        ],
    },
    {
        "path": "/chinese-new-year",
        "file": "chinese-new-year.html",
        "title": "Chinese New Year Event",
        "title_em": "Community celebration",
        "description": "Nexperts Academy Chinese New Year community event — celebration, networking and technology talks in Malaysia.",
        "hero_sub": "Annual open-house bringing alumni, partners and families together — with short tech talks and student showcases.",
        "sections": [
            ("About the event", "Our Chinese New Year gathering blends cultural celebration with light technical programming — demo tables from recent bootcamp graduates and networking for hiring managers."),
            ("Who attends", "Alumni, corporate partners, university clubs and prospective students exploring certification paths."),
            ("Next edition", "Dates are announced via our upcoming events page and email list. Corporate table sponsorships available."),
        ],
        "cards": [
            ("Upcoming events", "Full public calendar.", "/upcoming-events"),
            ("Past events", "Photo archives & highlights.", "/past-events"),
            ("Enquire", "Sponsorship or attendance.", "/contact-us"),
        ],
    },
    {
        "path": "/tan-boon-heong-event",
        "file": "tan-boon-heong-event.html",
        "title": "Tan Boon Heong Event",
        "title_em": "Special session",
        "description": "Tan Boon Heong event at Nexperts Academy — special guest session on excellence, discipline and career mastery.",
        "hero_sub": "An inspiring evening session with Malaysia's badminton legend — mindset, preparation and performance lessons transferable to tech careers.",
        "sections": [
            ("Event recap", "Nexperts hosted Tan Boon Heong for a community and student audience, drawing parallels between elite sports preparation and disciplined certification study."),
            ("Key themes", "Consistency beats motivation · Coaching accelerates progress · Measure what matters · Recovery is part of performance"),
            ("Future sessions", "We occasionally host non-technical leadership speakers to complement our technical depth. Watch upcoming events for announcements."),
        ],
        "cards": [
            ("Past events", "More community highlights.", "/past-events"),
            ("Courses", "Build disciplined skills daily.", "/#courses"),
            ("Contact", "Propose a speaker collaboration.", "/contact-us"),
        ],
    },
    {
        "path": "/nexpert-x-universiti-teknologi-mara",
        "file": "nexpert-x-universiti-teknologi-mara.html",
        "title": "Nexperts × Universiti Teknologi MARA",
        "title_em": "Partnership",
        "description": "Nexperts Academy partnership with Universiti Teknologi MARA (UiTM) — certification pathways, workshops and graduate readiness programmes.",
        "hero_sub": "Combining UiTM's academic reach with Nexperts' vendor-aligned labs and employer-trusted certification delivery.",
        "sections": [
            ("Partnership goals", "Improve graduate employability in cloud, security and data roles through hands-on labs, subsidised cohorts and career briefing sessions."),
            ("What students gain", "Access to the same rack environments and instructors used for corporate deliveries — plus roadmap guidance for CCNA, Azure, AWS and security tracks."),
            ("For faculty", "Co-branded workshops, train-the-trainer briefings and exam voucher programmes can be arranged per faculty request."),
        ],
        "cards": [
            ("Upcoming events", "UiTM-related dates when published.", "/upcoming-events"),
            ("Course catalogue", "Full certification list.", "/#courses"),
            ("Faculty enquiry", "Co-branded programme design.", "/contact-us"),
        ],
    },
]

BLOG_POST = {
    "path": "/post/unlocking-the-power-of-data-science-applications-and-challenges",
    "file": "post/unlocking-the-power-of-data-science-applications-and-challenges.html",
    "title": "Unlocking the Power of Data Science",
    "title_em": "Applications & challenges",
    "description": "Unlocking the power of data science — applications and challenges for Malaysian enterprises adopting analytics and machine learning.",
    "date": "12 March 2025",
    "author": "Nexperts Data Practice",
    "body": [
        "Data science is no longer a Silicon Valley headline — Malaysian banks, telcos, retailers and government agencies run production models for fraud, churn, demand forecasting and personalisation. The gap is not awareness; it is disciplined execution.",
        "Applications that work locally share traits: labelled data with ownership, a sponsor who accepts imperfection in v1, and engineers who can deploy — not only notebook heroes. Common wins include credit risk feature stores, network fault prediction, inventory optimisation and customer lifetime value segmentation.",
        "Challenges are equally consistent: siloed spreadsheets as 'source of truth', under-funded data engineering, metric gaming, and procurement cycles that buy GPUs before governance. PDPA and sector guidelines (BNM, MCMC) mean consent, retention and explainability are design requirements, not legal footnotes.",
        "A pragmatic roadmap: (1) fix data access and definitions, (2) ship one measurable model with monitoring, (3) industrialise feature pipelines, (4) scale team skills via hybrid hiring and targeted upskilling — bootcamps for literacy, certifications for platform depth.",
        "Nexperts runs SQL for Data Professionals, AI/ML bootcamps and Microsoft DP-100 / AI-102 programmes with MY-context labs. If you are sponsoring a pilot, start with a problem owner, a baseline metric and an eight-week delivery window — not a generic 'AI strategy' slide.",
    ],
}


def _static_page_html(
    *,
    title: str,
    title_em: str,
    description: str,
    path: str,
    hero_sub: str,
    sections: list[tuple[str, str]],
    cards: list[tuple[str, str, str]] | None,
) -> str:
    crumb_leaf = title
    section_html = ""
    for h, p in sections:
        section_html += f"    <h2>{html_lib.escape(h)}</h2>\n    <p>{html_lib.escape(p)}</p>\n"
    cards_html = ""
    if cards:
        cards_html = '    <div class="card-grid">\n'
        for name, desc, href in cards:
            cards_html += (
                f'      <a class="card" href="{html_lib.escape(href)}">\n'
                f"        <h3>{html_lib.escape(name)}</h3>\n"
                f"        <p>{html_lib.escape(desc)}</p>\n"
                f'        <span class="card-link">Learn more →</span>\n'
                f"      </a>\n"
            )
        cards_html += "    </div>\n"
    canon = f"{SITE}{path}"
    nav = render_site_nav(variant="inner", current_path=path, enroll_href="/contact-us#enquire")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_lib.escape(title)} | Nexperts Academy</title>
<meta name="description" content="{html_lib.escape(description)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{html_lib.escape(title)} | Nexperts Academy">
<meta property="og:description" content="{html_lib.escape(description)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/image/nexperts-logo.png">
<meta property="og:site_name" content="Nexperts Academy">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,300;1,9..144,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/site-nav-mobile.css">
{NAV_ASSET_TAGS}
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#f8fbff;--ink:#0f1b2d;--ink2:#2a3f5f;--ink3:#4b6284;--ink4:#7e97b8;--blue:#1d4ed8;--line:#d7e6fb;--line2:#bfd5f2}}
html{{scroll-behavior:smooth;background:var(--bg)}}
body{{font-family:'Plus Jakarta Sans',sans-serif;background:var(--bg);color:var(--ink);line-height:1.65;font-size:15px;padding-top:62px}}
.hero{{padding:48px 40px 48px;text-align:center;background:linear-gradient(180deg,#eef6ff,#f8fbff);border-bottom:1px solid var(--line)}}
.hero h1{{font-family:'Fraunces',serif;font-weight:300;font-size:clamp(2rem,4vw,2.8rem);margin-bottom:12px}}
.hero h1 em{{font-style:italic;color:var(--blue)}}
.hero p{{color:var(--ink2);max-width:640px;margin:0 auto}}
.content{{max-width:720px;margin:0 auto;padding:48px 24px 80px}}
.content h2{{font-family:'Fraunces',serif;font-weight:300;font-size:1.35rem;margin:2rem 0 .75rem}}
.content p{{color:var(--ink2);margin-bottom:1rem}}
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
<body>
{nav}
<section class="hero">
  <p style="font-size:.72rem;color:var(--ink3);margin-bottom:14px"><a href="/" style="color:inherit;text-decoration:none">Home</a> / {html_lib.escape(crumb_leaf)}</p>
  <h1>{html_lib.escape(title)}<br><em>{html_lib.escape(title_em)}</em></h1>
  <p>{html_lib.escape(hero_sub)}</p>
</section>
<section class="content legal-prose">
{section_html}{cards_html}
  <p style="margin-top:2rem"><a href="/contact-us#enquire" style="color:var(--blue);font-weight:700">Enquire about this programme →</a></p>
</section>
<footer>
  <p>© Nexperts Academy Sdn Bhd · <a href="/">Home</a> · <a href="/privacy-policy">Privacy</a></p>
</footer>
<script src="/js/site-nav-mobile.js" defer></script>
</body>
</html>
"""


def build_static_pages() -> None:
    for spec in STATIC_PAGES:
        out = ROOT / spec["file"]
        out.parent.mkdir(parents=True, exist_ok=True)
        html = _static_page_html(
            title=spec["title"],
            title_em=spec["title_em"],
            description=spec["description"],
            path=spec["path"],
            hero_sub=spec["hero_sub"],
            sections=spec["sections"],
            cards=spec.get("cards"),
        )
        out.write_text(html, encoding="utf-8", newline="\n")
        print(f"  static: {spec['file']}")

    post = BLOG_POST
    out = ROOT / post["file"]
    out.parent.mkdir(parents=True, exist_ok=True)
    body_parts = "".join(f"    <p>{html_lib.escape(p)}</p>\n" for p in post["body"])
    canon = f"{SITE}{post['path']}"
    post_html = _static_page_html(
        title=post["title"],
        title_em=post["title_em"],
        description=post["description"],
        path=post["path"],
        hero_sub=f"{post['date']} · {post['author']}",
        sections=[],
        cards=[
            ("AI & ML Bootcamp", "Practitioner sprint.", "/courses/ai-ml-bootcamp"),
            ("SQL for Data Professionals", "Enterprise analytics foundation.", "/courses/sql-for-data-professionals"),
            ("Contact", "Corporate training enquiry.", "/contact-us"),
        ],
    )
    post_html = post_html.replace(
        '<section class="content legal-prose">\n',
        f'<section class="content legal-prose">\n{body_parts}',
        1,
    )
    post_html = re.sub(r"<title>[^<]+</title>", f"<title>{html_lib.escape(post['title'])} | Nexperts Academy Blog</title>", post_html, count=1)
    out.write_text(post_html, encoding="utf-8", newline="\n")
    print(f"  blog post: {post['file']}")


def patch_redirects() -> None:
    redirects_path = ROOT / "_redirects"
    text = redirects_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    out_lines: list[str] = []
    skip_404 = False
    existing_src: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("/* /404.html 404"):
            skip_404 = True
            continue
        m = re.match(r"^(\S+)\s+\S+\s+301", stripped)
        if m:
            existing_src.add(m.group(1))
        out_lines.append(line)

    insert_at = len(out_lines)
    for i, line in enumerate(out_lines):
        if line.strip().startswith("# Filename & legacy paths"):
            insert_at = i
            break

    new_rules: list[str] = []
    for src, dst in sorted(REDIRECT_301.items()):
        if src not in existing_src:
            new_rules.append(f"{src} {dst} 301")

    if new_rules:
        block = ["", "# Legacy Wix URLs → canonical courses (301)"] + new_rules
        out_lines[insert_at:insert_at] = block

    if skip_404:
        out_lines.extend(
            [
                "",
                "# Unknown paths: set Custom 404 document to /404.html in Cloudflare Pages (Dashboard).",
                "# Do not use /* /404.html 404 here — Cloudflare Pages rejects status 404 in _redirects.",
            ]
        )

    redirects_path.write_text("\n".join(out_lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"  patched _redirects (+{len(new_rules)} rules, removed invalid 404 if present)")


def remove_root_course_duplicates() -> None:
    for c in LEGACY_COURSES:
        p = ROOT / f"{c['slug']}.html"
        if p.is_file():
            p.unlink()
            print(f"  removed root duplicate: {p.name}")


def main() -> None:
    print("Building legacy course pages (courses/)…")
    build_courses()
    remove_root_course_duplicates()
    print("Building static content pages…")
    build_static_pages()
    print("Patching _redirects…")
    patch_redirects()
    print("Done.")


if __name__ == "__main__":
    main()
