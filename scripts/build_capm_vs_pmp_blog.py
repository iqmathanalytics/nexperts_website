# -*- coding: utf-8 -*-
"""Generate CAPM vs PMP Malaysia blog page and wire nav/hub/sitemap/courses."""
from __future__ import annotations

import html as html_lib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from site_nav import NAV_ASSET_TAGS, render_site_nav, render_whatsapp_float  # noqa: E402

SITE = "https://www.nexpertsacademy.com"
SLUG = "capm-vs-pmp-malaysia"
IMG = f"/image/blog/{SLUG}"
OG_IMAGE = f"{SITE}{IMG}/image1.jpg"


def esc(s: str) -> str:
    return html_lib.escape(s, quote=False)


def table_html(headers: list[str], rows: list[list[str]]) -> str:
    th = "".join(f'<th scope="col">{esc(h)}</th>' for h in headers)
    body = []
    for row in rows:
        tds = "".join(f"<td>{esc(c)}</td>" for c in row)
        body.append(f"<tr>{tds}</tr>")
    return (
        '<div class="blog-table-wrap"><table class="blog-table blog-table--compare">'
        f"<thead><tr>{th}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"
    )


def figure(src: str, alt: str) -> str:
    return (
        f'<figure class="blog-figure"><img src="{src}" alt="{html_lib.escape(alt, quote=True)}" '
        'loading="lazy" width="720" height="405"></figure>'
    )


HEAD_STYLE = """<link rel="stylesheet" href="/css/blog.css">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#f8fbff;--ink:#0f1b2d;--ink2:#2a3f5f;--ink3:#4b6284;--ink4:#7e97b8;--blue:#1d4ed8;--line:#d7e6fb;--line2:#bfd5f2}
html{scroll-behavior:smooth;background:var(--bg)}
body{font-family:'Plus Jakarta Sans',sans-serif;background:var(--bg);color:var(--ink);line-height:1.65;font-size:15px;padding-top:62px}
.hero{padding:48px 40px 48px;text-align:center;background:linear-gradient(180deg,#eef6ff,#f8fbff);border-bottom:1px solid var(--line)}
.hero h1{font-family:'Fraunces',serif;font-weight:300;font-size:clamp(2rem,4vw,2.8rem);margin-bottom:12px}
.hero h1 em{font-style:italic;color:var(--blue)}
.hero p{color:var(--ink2);max-width:720px;margin:0 auto}
.card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-top:32px}
.card{display:block;padding:20px;background:#fff;border:1px solid var(--line);border-radius:12px;text-decoration:none;color:inherit;transition:transform .2s,box-shadow .2s}
.card:hover{transform:translateY(-3px);box-shadow:0 12px 32px rgba(29,78,216,.12)}
.card h3{font-size:.95rem;margin-bottom:8px;color:var(--ink)}
.card p{font-size:.82rem;color:var(--ink3);margin:0}
.card-link{display:inline-block;margin-top:12px;font-size:.78rem;font-weight:700;color:var(--blue)}
.blog-faq{margin-top:1.5rem}
.faq-item{margin-bottom:1.25rem;padding-bottom:1.25rem;border-bottom:1px solid var(--line)}
.faq-q{margin-bottom:.5rem;color:var(--ink)}
footer{background:#0d1117;color:rgba(255,255,255,.5);text-align:center;padding:32px 24px;font-size:.75rem}
footer a{color:rgba(255,255,255,.65);text-decoration:none}
</style>
<link rel="stylesheet" href="/css/whatsapp-float.css">"""


def page_shell(
    *,
    meta_title: str,
    meta_desc: str,
    hero_title_html: str,
    hero_crumb: str,
    hero_meta: str,
    body_html: str,
    toc_items: list[tuple[str, str]],
    cards_html: str,
) -> str:
    toc = "".join(f'<li><a href="#{sid}">{esc(label)}</a></li>' for sid, label in toc_items)
    nav = render_site_nav(variant="inner", current_path=f"/blog/{SLUG}")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- nexperts-ga4:v1 -->
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-V7NE6K78L4"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', 'G-V7NE6K78L4');
</script>
<!-- /nexperts-ga4:v1 -->

<!-- nexperts-gtm:v1 -->
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','GTM-5PRVNR2');</script>
<!-- End Google Tag Manager -->
<!-- /nexperts-gtm:v1 -->



<title>{esc(meta_title)}</title>
<meta name="description" content="{html_lib.escape(meta_desc, quote=True)}">
<link rel="canonical" href="{SITE}/blog/{SLUG}">
<meta property="og:title" content="{html_lib.escape(meta_title, quote=True)}">
<meta property="og:description" content="{html_lib.escape(meta_desc, quote=True)}">
<meta property="og:url" content="{SITE}/blog/{SLUG}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:site_name" content="Nexperts Academy">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html_lib.escape(meta_title, quote=True)}">
<meta name="twitter:description" content="{html_lib.escape(meta_desc, quote=True)}">
<meta name="twitter:image" content="{OG_IMAGE}">
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,300;1,9..144,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/site-nav-mobile.css">
{NAV_ASSET_TAGS}
{HEAD_STYLE}
</head>
<body class="blog-page">
<!-- nexperts-gtm-noscript:v1 -->
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-5PRVNR2"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
<!-- /nexperts-gtm-noscript:v1 -->



{nav}
<section class="hero">
  <p style="font-size:.72rem;color:var(--ink3);margin-bottom:14px"><a href="/" style="color:inherit;text-decoration:none">Home</a> / <a href="/blog" style="color:inherit;text-decoration:none">Blog</a> / {esc(hero_crumb)}</p>
  <h1>{hero_title_html}</h1>
  <p>{esc(hero_meta)}</p>
</section>
<section class="content legal-prose">
  <a class="blog-back" href="/blog">← Back to Blog</a>
<nav class="blog-toc" aria-label="Table of contents">
      <h2 class="blog-toc-title">Table of Contents</h2>
      <ol class="blog-toc-list">{toc}</ol>
    </nav>
{body_html}
    <div class="card-grid">
{cards_html}
    </div>
  <p style="margin-top:2rem"><a href="/contact-us#enquire" style="color:var(--blue);font-weight:700">Enquire about CAPM or PMP training →</a></p>
</section>
<footer>
  <p>© Nexperts Academy Sdn Bhd · <a href="/">Home</a> · <a href="/blog">Blog</a> · <a href="/privacy-policy">Privacy</a></p>
</footer>
<script src="/js/site-nav-mobile.js" defer></script>
{render_whatsapp_float()}
</body>
</html>
"""


def build_page() -> None:
    meta_title = "CAPM vs PMP in Malaysia: Which Certification Is Better?"
    meta_desc = (
        "Compare CAPM vs PMP in Malaysia, including eligibility, exam formats, costs and "
        "career opportunities. Find out which project management certification suits your experience."
    )

    toc = [
        ("difference", "CAPM vs PMP: What Is the Difference?"),
        ("who-capm", "Who Should Choose CAPM Certification?"),
        ("who-pmp", "Who Should Choose PMP Certification?"),
        ("exam-difference", "What Is the Difference Between the Exams?"),
        ("cost", "Which Certification Costs More?"),
        ("career", "Which Certification Is Better for Your Career?"),
        ("capm-to-pmp", "Can CAPM Help You Qualify for PMP Later?"),
        ("maintain", "How Do You Maintain CAPM and PMP?"),
        ("faq", "Frequently Asked Questions"),
        ("conclusion", "Conclusion"),
    ]

    parts: list[str] = []
    parts.append(
        "<p>Choosing between CAPM and PMP certification depends on your project management experience, "
        "career goals and eligibility. Both certifications are offered by the Project Management Institute (PMI), "
        "but they serve different professional needs.</p>"
    )
    parts.append(
        "<p>The <a href=\"/courses/capm\">CAPM (Certified Associate in Project Management)</a> certification is designed "
        "for individuals building foundational project management knowledge, while the "
        "<a href=\"/courses/pmp\">PMP (Project Management Professional)</a> certification is intended for professionals "
        "with experience leading and managing projects.</p>"
    )
    parts.append(
        "<p>For professionals in Malaysia, understanding the differences between CAPM and PMP can help you choose "
        "the right certification before investing in training and examination fees.</p>"
    )
    parts.append(
        "<p>In this guide, we compare CAPM vs PMP, including eligibility requirements, examination formats, "
        "costs, career opportunities and certification renewal.</p>"
    )
    parts.append(
        figure(
            f"{IMG}/image1.jpg",
            "CAPM vs PMP certification pathways for project professionals in Malaysia",
        )
    )

    parts.append('<h2 id="difference">CAPM vs PMP in Malaysia: What Is the Difference?</h2>')
    parts.append(
        "<p>The main difference between CAPM and PMP is the level of project management knowledge and "
        "professional experience each certification validates.</p>"
    )
    parts.append(
        "<p>CAPM focuses on foundational project management concepts, while PMP evaluates the ability to "
        "lead and manage projects in professional environments.</p>"
    )
    parts.append(
        "<p>Both certifications cover project management principles, but their eligibility requirements, "
        "examination structures and intended audiences differ.</p>"
    )
    parts.append(
        "<p>The two certifications are separate qualifications rather than compulsory stages of one certification "
        "pathway. You do not need to earn CAPM before applying for PMP if you already meet the PMP eligibility requirements.</p>"
    )
    parts.append(
        table_html(
            ["Comparison", "CAPM", "PMP"],
            [
                ["Full form", "Certified Associate in Project Management", "Project Management Professional"],
                ["Certification provider", "Project Management Institute (PMI)", "Project Management Institute (PMI)"],
                ["Certification level", "Foundational", "Professional"],
                [
                    "Target audience",
                    "Graduates, beginners and aspiring project professionals",
                    "Experienced project professionals",
                ],
                ["Project experience", "Not required", "Required"],
                [
                    "Education requirement",
                    "Secondary degree or equivalent",
                    "Depends on educational qualification",
                ],
                ["Project management education", "23 hours", "35 hours or an active CAPM"],
                ["Exam questions", "150", "180"],
                ["Examination duration", "3 hours", "4 hours"],
                [
                    "Main focus",
                    "Project management fundamentals, predictive, agile and business analysis",
                    "Project leadership, people, processes and business environment",
                ],
            ],
        )
    )

    parts.append('<h2 id="who-capm">Who Should Choose CAPM Certification?</h2>')
    parts.append(
        "<p>CAPM certification is suitable for individuals who want to develop foundational project management "
        "knowledge or enter the project management profession.</p>"
    )
    parts.append(
        "<p>You do not need previous project management work experience to apply for CAPM. This makes it an "
        "accessible option for graduates, career changers and professionals who support project teams.</p>"
    )
    parts.append("<p>CAPM may be suitable for:</p>")
    parts.append(
        "<ul>"
        "<li><strong>Fresh graduates:</strong> Individuals who want to develop project management knowledge before entering the workforce.</li>"
        "<li><strong>Project coordinators:</strong> Professionals who assist project managers with schedules, documentation and coordination.</li>"
        "<li><strong>Business analysts:</strong> Individuals interested in understanding project requirements, stakeholder engagement and business analysis.</li>"
        "<li><strong>Team members:</strong> Professionals who contribute to projects and want to understand project management processes.</li>"
        "<li><strong>Career changers:</strong> Individuals transitioning from another professional field into project-related roles.</li>"
        "</ul>"
    )
    parts.append(
        "<p>CAPM can help demonstrate your understanding of project management concepts, but obtaining the "
        "certification does not automatically guarantee employment or a promotion.</p>"
    )
    parts.append("<h3>CAPM Certification Eligibility Requirements</h3>")
    parts.append(
        "<p>To apply for CAPM certification, candidates must meet PMI's education and age requirements.</p>"
    )
    parts.append(
        table_html(
            ["Requirement", "Details"],
            [
                ["Educational qualification", "Secondary degree, high school diploma, GED or global equivalent"],
                ["Minimum age", "18 years"],
                ["Project management education", "At least 23 hours"],
                ["Previous project experience", "Not required"],
                ["Previous certification", "Not required"],
            ],
        )
    )
    parts.append(
        "<p>Candidates must complete the required 23 hours of project management education before taking the examination.</p>"
    )
    parts.append(
        "<p>For individuals starting their project management careers, CAPM provides an opportunity to demonstrate "
        "foundational knowledge without first meeting the professional experience requirements associated with PMP.</p>"
    )

    parts.append('<h2 id="who-pmp">Who Should Choose PMP Certification?</h2>')
    parts.append(
        "<p>PMP certification is designed for professionals who have experience leading and directing projects.</p>"
    )
    parts.append(
        "<p>Unlike CAPM, PMP requires applicants to demonstrate qualifying project management experience based on "
        "their educational background.</p>"
    )
    parts.append(
        "<p>It is particularly relevant for professionals who are responsible for project planning, stakeholder "
        "management, project delivery, risk management and business outcomes.</p>"
    )
    parts.append("<p>PMP may be suitable for:</p>")
    parts.append(
        "<ul>"
        "<li><strong>Project managers:</strong> Professionals responsible for planning and delivering projects.</li>"
        "<li><strong>Senior project coordinators:</strong> Individuals who have developed substantial project leadership responsibilities.</li>"
        "<li><strong>Programme professionals:</strong> Individuals involved in coordinating multiple related projects.</li>"
        "<li><strong>Business transformation professionals:</strong> Professionals managing organisational initiatives and changes.</li>"
        "<li><strong>Experienced team leaders:</strong> Individuals who direct project activities, manage resources and coordinate stakeholders.</li>"
        "</ul>"
    )
    parts.append(
        "<p>PMP validates professional project management experience and knowledge. However, employers may also "
        "consider industry experience, leadership responsibilities and practical project delivery skills.</p>"
    )
    parts.append("<h3>PMP Certification Eligibility Requirements</h3>")
    parts.append(
        "<p>PMI provides different eligibility pathways depending on the candidate's educational qualification.</p>"
    )
    parts.append(
        "<p>Under the 2026 PMP examination requirements, candidates must demonstrate non-overlapping project "
        "leadership experience gained within the previous 10 years.</p>"
    )
    parts.append(
        table_html(
            ["Educational qualification", "Required project leadership experience"],
            [
                ["Secondary or high school qualification", "60 months (5 years)"],
                [
                    "Recognised associate-level or qualifying technical/vocational qualification",
                    "48 months (4 years)",
                ],
                ["Bachelor's degree or higher", "36 months (3 years)"],
                [
                    "Bachelor's or postgraduate degree from a PMI GAC-accredited programme",
                    "24 months (2 years)",
                ],
            ],
        )
    )
    parts.append(
        "<p>Candidates must also complete 35 hours of project management training or hold an active CAPM certification.</p>"
    )
    parts.append(
        "<p>The exact qualification level and equivalency must satisfy PMI's eligibility criteria. Applicants "
        "should review the official requirements before submitting their applications.</p>"
    )
    parts.append("<h3>PMP Training Requirement Changes From 1 December 2026</h3>")
    parts.append(
        "<p>PMI is introducing updated eligibility requirements for live instructor-led PMP training from 1 December 2026.</p>"
    )
    parts.append(
        "<p>For training completed on or after this date, live classes delivered in person or virtually will "
        "qualify only when provided through:</p>"
    )
    parts.append(
        "<ul>"
        "<li>A PMI Authorized Training Partner (ATP).</li>"
        "<li>A China Registered Education Provider (REP).</li>"
        "<li>An eligible accredited higher education programme, including PMI Global Accreditation Center (GAC) programmes.</li>"
        "</ul>"
    )
    parts.append(
        "<p>Self-paced, on-demand training remains available through eligible providers without the same "
        "live-class provider restriction.</p>"
    )
    parts.append(
        "<p>Training completed before 1 December 2026 remains eligible under the previous requirements.</p>"
    )
    parts.append(
        "<p>Candidates planning to enrol in PMP training should verify the provider's eligibility before "
        "choosing a live instructor-led programme.</p>"
    )

    parts.append(
        figure(
            f"{IMG}/image2.jpg",
            "CAPM and PMP exam preparation study materials and planning workspace",
        )
    )

    parts.append('<h2 id="exam-difference">CAPM vs PMP: What Is the Difference Between the Exams?</h2>')
    parts.append(
        "<p>Both CAPM and PMP require candidates to pass a PMI examination, but the exams assess different "
        "knowledge areas and professional competencies.</p>"
    )
    parts.append(
        "<p>CAPM focuses on foundational project management knowledge, while PMP evaluates project leadership "
        "across different delivery approaches and organisational environments.</p>"
    )
    parts.append("<h3>CAPM Exam Format</h3>")
    parts.append(
        "<p>The CAPM examination includes 150 questions and has a total duration of three hours.</p>"
    )
    parts.append(
        table_html(
            ["Exam detail", "Information"],
            [
                ["Total questions", "150"],
                ["Scored questions", "135"],
                ["Unscored questions", "15"],
                ["Examination duration", "180 minutes"],
                ["Examination languages", "Multiple languages, including English"],
                ["Examination delivery", "Pearson VUE test centre or secure online testing"],
            ],
        )
    )
    parts.append("<p>The CAPM examination covers four domains:</p>")
    parts.append(
        table_html(
            ["CAPM Exam Domain", "Weight"],
            [
                ["Project Management Fundamentals and Core Concepts", "36%"],
                ["Predictive, Plan-Based Methodologies", "17%"],
                ["Agile Frameworks and Methodologies", "20%"],
                ["Business Analysis Frameworks", "27%"],
            ],
        )
    )
    parts.append(
        "<p>The examination includes multiple-choice, drag-and-drop, animation or comic-strip, and hotspot-style questions.</p>"
    )
    parts.append(
        "<p>Candidates should prepare across all four domains rather than concentrating only on project management terminology.</p>"
    )
    parts.append("<h3>PMP Exam Format</h3>")
    parts.append(
        "<p>The 2026 PMP examination consists of 180 questions with a total examination duration of 240 minutes.</p>"
    )
    parts.append(
        table_html(
            ["Exam detail", "Information"],
            [
                ["Total questions", "180"],
                ["Scored questions", "170"],
                ["Unscored questions", "10"],
                ["Examination duration", "240 minutes"],
                ["Examination delivery", "Pearson VUE test centre or applicable secure online testing"],
            ],
        )
    )
    parts.append("<p>The updated PMP examination evaluates three domains:</p>")
    parts.append(
        table_html(
            ["PMP Exam Domain", "Weight"],
            [
                ["People", "33%"],
                ["Process", "41%"],
                ["Business Environment", "26%"],
            ],
        )
    )
    parts.append(
        "<p>The examination includes multiple-choice questions, multiple-response questions, drag-and-drop "
        "activities and practical scenario-based assessment elements.</p>"
    )
    parts.append(
        "<p>The updated examination places emphasis on practical project situations, decision-making, "
        "leadership and delivering business value across different project environments.</p>"
    )

    parts.append('<h2 id="cost">CAPM vs PMP: Which Certification Costs More?</h2>')
    parts.append(
        "<p>The overall cost of CAPM and PMP certification depends on the examination fee, PMI membership, "
        "training programme and preparation resources.</p>"
    )
    parts.append(
        "<p>Candidates in Malaysia should consider the following expenses when comparing both certifications.</p>"
    )
    parts.append(
        table_html(
            ["Cost component", "CAPM", "PMP"],
            [
                ["PMI examination fee", "Applicable CAPM examination fee", "Applicable PMP examination fee"],
                ["PMI membership", "Optional", "Optional"],
                ["Training programme", "Depends on the provider", "Depends on the provider"],
                ["Study materials", "Depends on preparation requirements", "Depends on preparation requirements"],
                ["Practice examinations", "Depends on the selected resources", "Depends on the selected resources"],
            ],
        )
    )
    parts.append(
        "<p>PMI examination fees can vary according to membership and applicable regional pricing. Candidates "
        "should verify the current amount through their PMI account before scheduling their examination.</p>"
    )
    parts.append(
        "<p>Training fees are separate from examination fees unless a training provider explicitly includes "
        "the examination voucher in its course package.</p>"
    )
    parts.append(
        "<p>When comparing CAPM and PMP training in Malaysia, check the course duration, instructor qualifications, "
        "learning materials, mock examinations and examination voucher inclusions.</p>"
    )

    parts.append(
        figure(
            f"{IMG}/image3.jpg",
            "Career growth pathway from project coordinator roles toward project leadership in Malaysia",
        )
    )

    parts.append(
        '<h2 id="career">CAPM vs PMP: Which Certification Is Better for Your Career in Malaysia?</h2>'
    )
    parts.append(
        "<p>There is no single answer to whether CAPM or PMP is better. The right option depends on your "
        "current experience and the responsibilities you want to take on.</p>"
    )
    parts.append("<h3>Career Opportunities After CAPM</h3>")
    parts.append(
        "<p>CAPM can support individuals who are beginning their project management careers or moving into "
        "project-related responsibilities.</p>"
    )
    parts.append("<p>Potential career directions include:</p>")
    parts.append(
        "<ul>"
        "<li>Project coordinator</li>"
        "<li>Project management assistant</li>"
        "<li>Project support specialist</li>"
        "<li>Junior project analyst</li>"
        "<li>Business analyst</li>"
        "</ul>"
    )
    parts.append(
        "<p>The certification demonstrates foundational project management knowledge, which can complement "
        "practical experience and other professional skills.</p>"
    )
    parts.append("<h3>Career Opportunities After PMP</h3>")
    parts.append(
        "<p>PMP is designed for professionals with qualifying project leadership experience who want to "
        "demonstrate their ability to manage complex projects.</p>"
    )
    parts.append("<p>Potential career directions include:</p>")
    parts.append(
        "<ul>"
        "<li>Project manager</li>"
        "<li>Senior project manager</li>"
        "<li>Programme manager</li>"
        "<li>Project management consultant</li>"
        "<li>Business transformation manager</li>"
        "</ul>"
    )
    parts.append(
        "<p>The actual responsibilities associated with these roles vary between employers and industries. "
        "A PMP certification does not replace the experience and practical capabilities expected by employers.</p>"
    )
    parts.append("<h3>What Should Professionals in Malaysia Consider?</h3>")
    parts.append(
        "<p>Before selecting a certification, review job descriptions for the positions you want to pursue.</p>"
    )
    parts.append("<p>Look at:</p>")
    parts.append(
        "<ul>"
        "<li>Whether the employer requires CAPM or PMP certification.</li>"
        "<li>Whether project management experience is mandatory.</li>"
        "<li>Whether the role involves project coordination or project leadership.</li>"
        "<li>Which project management methodologies the organisation uses.</li>"
        "<li>Whether the certification aligns with your longer-term career plans.</li>"
        "</ul>"
    )
    parts.append(
        "<p>For early-career professionals, CAPM may be a suitable starting point. For professionals who already "
        "meet PMP eligibility requirements, applying directly for PMP may be more appropriate.</p>"
    )

    parts.append('<h2 id="capm-to-pmp">Can CAPM Help You Qualify for PMP Later?</h2>')
    parts.append(
        "<p>An active CAPM certification can satisfy the PMP project management training requirement of 35 hours.</p>"
    )
    parts.append(
        "<p>However, CAPM does not replace the project leadership experience required for PMP eligibility.</p>"
    )
    parts.append(
        "<p>Candidates must still meet the relevant education and project experience requirements before applying for PMP.</p>"
    )
    parts.append(
        "<p>For example, a professional who holds CAPM but does not yet have the required PMP project leadership "
        "experience must continue developing their practical experience before becoming eligible.</p>"
    )
    parts.append(
        "<p>CAPM can therefore support professional development, but it does not automatically convert into a PMP certification.</p>"
    )

    parts.append('<h2 id="maintain">How Do You Maintain CAPM and PMP Certifications?</h2>')
    parts.append(
        "<p>Both CAPM and PMP certifications require ongoing professional development to maintain active status.</p>"
    )
    parts.append(
        "<p>PMI uses Professional Development Units (PDUs) to measure qualifying learning and professional contribution activities.</p>"
    )
    parts.append("<p>The PMI Talent Triangle consists of three areas:</p>")
    parts.append(
        "<ul>"
        "<li>Ways of Working</li>"
        "<li>Power Skills</li>"
        "<li>Business Acumen</li>"
        "</ul>"
    )
    parts.append(
        table_html(
            ["Renewal requirement", "CAPM", "PMP"],
            [
                ["Renewal cycle", "3 years", "3 years"],
                ["Total PDUs required", "15", "60"],
                ["Minimum Education PDUs", "9", "35"],
                ["Maximum Giving Back PDUs", "6", "25"],
                ["Minimum PDUs in each Talent Triangle area", "2", "8"],
            ],
        )
    )
    parts.append(
        "<p>Certification holders should track their professional development activities throughout the renewal "
        "cycle and ensure they satisfy the minimum requirements for their certification.</p>"
    )

    parts.append('<h2 id="faq">Frequently Asked Questions About CAPM vs PMP</h2>')
    parts.append('<div class="blog-faq">')
    faqs = [
        (
            "Is CAPM better than PMP?",
            "CAPM and PMP serve different professional needs. CAPM is suitable for individuals developing "
            "foundational project management knowledge, while PMP is intended for professionals with qualifying "
            "project leadership experience. The better option depends on your career stage and eligibility.",
        ),
        (
            "Can I take the PMP exam without CAPM certification?",
            "Yes. CAPM is not a mandatory prerequisite for PMP. Candidates can apply directly for PMP if they "
            "meet the educational, project leadership experience and training requirements.",
        ),
        (
            "Does CAPM certification count towards PMP eligibility?",
            "An active CAPM certification can satisfy PMI's 35-hour project management training requirement for "
            "PMP. However, candidates must still meet the separate project leadership experience requirements.",
        ),
        (
            "Which certification is suitable for fresh graduates in Malaysia?",
            "CAPM is generally more suitable for fresh graduates because it does not require previous project "
            "management work experience. Candidates must meet the minimum educational, age and project management "
            "education requirements.",
        ),
        (
            "How many hours of training are required for CAPM and PMP?",
            "CAPM requires at least 23 hours of project management education. PMP requires 35 hours of project "
            "management training, unless the candidate holds an active CAPM certification.",
        ),
        (
            "Are CAPM and PMP examinations available online?",
            "Yes. PMI provides secure online examination options, subject to applicable scheduling, technical and "
            "testing requirements. Candidates can also choose available Pearson VUE test centre appointments.",
        ),
        (
            "Do CAPM and PMP certifications expire?",
            "Both certifications require renewal through PMI's Continuing Certification Requirements programme. "
            "CAPM holders must earn 15 PDUs and PMP holders must earn 60 PDUs during each three-year renewal cycle.",
        ),
        (
            "Does PMP guarantee a higher salary than CAPM?",
            "No certification guarantees a specific salary increase. Compensation depends on professional "
            "experience, industry, job responsibilities, location and employer requirements. Candidates should "
            "evaluate certification as part of their broader professional development.",
        ),
    ]
    for q, a in faqs:
        parts.append(
            f'<div class="faq-item"><p class="faq-q"><strong>{esc(q)}</strong></p><p>{esc(a)}</p></div>'
        )
    parts.append("</div>")

    parts.append('<h2 id="conclusion">Conclusion: Should You Choose CAPM or PMP?</h2>')
    parts.append(
        "<p>CAPM and PMP are valuable project management credentials, but they are designed for different "
        "stages of professional development.</p>"
    )
    parts.append(
        "<p>If you are a graduate, career changer or professional building foundational project management "
        "knowledge, CAPM may be the right starting point.</p>"
    )
    parts.append(
        "<p>If you already have qualifying experience leading projects and want to demonstrate your project "
        "management capabilities, PMP may be more suitable.</p>"
    )
    parts.append(
        "<p>Before choosing, review the official PMI eligibility requirements, compare the examination structure "
        "and identify the certification that aligns with your career objectives.</p>"
    )
    parts.append("<p><strong>Explore project management training at Nexperts Academy:</strong></p>")
    parts.append(
        "<ul>"
        '<li><a href="/courses/capm">CAPM Certification Training</a></li>'
        '<li><a href="/courses/pmp">PMP Certification Training</a></li>'
        "</ul>"
    )
    parts.append(
        "<p>Choose the certification that matches your current experience and the project management "
        "responsibilities you want to pursue.</p>"
    )
    parts.append("<h3>Official References</h3>")
    parts.append(
        "<ul>"
        '<li><a href="https://www.pmi.org/certifications/certified-associate-capm" rel="noopener noreferrer" target="_blank">PMI – CAPM Certification and Eligibility Requirements</a></li>'
        '<li><a href="https://www.pmi.org/certifications/certified-associate-capm" rel="noopener noreferrer" target="_blank">PMI – CAPM Examination Content Outline</a></li>'
        '<li><a href="https://www.pmi.org/certifications/project-management-pmp" rel="noopener noreferrer" target="_blank">PMI – PMP Certification and Eligibility Requirements</a></li>'
        '<li><a href="https://www.pmi.org/certifications/project-management-pmp" rel="noopener noreferrer" target="_blank">PMI – PMP Examination Content Outline 2026</a></li>'
        '<li><a href="https://www.pmi.org/certifications/certification-resources/maintain" rel="noopener noreferrer" target="_blank">PMI – Maintaining and Renewing Certifications</a></li>'
        "</ul>"
    )

    cards = f"""      <a class="card" href="/courses/capm">
        <h3>CAPM Certification Training</h3>
        <p>Instructor-led CAPM preparation covering PMI exam domains, agile and business analysis.</p>
        <span class="card-link">Learn more →</span>
      </a>
      <a class="card" href="/courses/pmp">
        <h3>PMP Certification Training</h3>
        <p>Prepare for PMP with structured learning across people, process and business environment.</p>
        <span class="card-link">Learn more →</span>
      </a>
      <a class="card" href="/blog">
        <h3>More Articles</h3>
        <p>Browse certification guides, career pathways and training insights from Nexperts Academy.</p>
        <span class="card-link">Learn more →</span>
      </a>"""

    html = page_shell(
        meta_title=meta_title,
        meta_desc=meta_desc,
        hero_title_html="CAPM vs PMP in Malaysia:<br><em>Which Certification Should You Choose?</em>",
        hero_crumb="CAPM vs PMP",
        hero_meta="November 2026 · Project Management Practice",
        body_html="\n        ".join(parts),
        toc_items=toc,
        cards_html=cards,
    )
    out = ROOT / "blog" / f"{SLUG}.html"
    out.write_text(html, encoding="utf-8", newline="\n")
    print("Wrote", out.relative_to(ROOT))


def wire_site() -> None:
    nav_path = ROOT / "scripts" / "site_nav.py"
    nav = nav_path.read_text(encoding="utf-8")
    if f"/blog/{SLUG}" not in nav:
        marker = (
            '            (\n'
            '                "Become an Ethical Hacker in Malaysia",\n'
            '                "/blog/how-to-become-ethical-hacker-malaysia",\n'
            "            ),\n"
        )
        addition = (
            marker
            + '            (\n'
            '                "CAPM vs PMP in Malaysia",\n'
            f'                "/blog/{SLUG}",\n'
            "            ),\n"
        )
        if marker not in nav:
            raise SystemExit("site_nav marker not found")
        nav_path.write_text(nav.replace(marker, addition), encoding="utf-8")
        print("Updated site_nav.py")
    else:
        print("site_nav.py already wired")

    inject_path = ROOT / "scripts" / "inject_addons_nav.py"
    inj = inject_path.read_text(encoding="utf-8")
    inj_entry = f'    "blog/{SLUG}.html",\n'
    if inj_entry not in inj:
        inj_marker = '    "blog/how-to-become-ethical-hacker-malaysia.html",\n'
        if inj_marker not in inj:
            raise SystemExit("inject marker not found")
        inject_path.write_text(inj.replace(inj_marker, inj_marker + inj_entry), encoding="utf-8")
        print("Updated inject_addons_nav.py")
    else:
        print("inject_addons_nav.py already wired")

    blog_hub = ROOT / "blog.html"
    hub = blog_hub.read_text(encoding="utf-8")
    if f"/blog/{SLUG}" not in hub:
        card_marker = '      <a class="card" href="/blog/cybersecurity-courses-malaysia-students">'
        new_card = (
            f'      <a class="card" href="/blog/{SLUG}">\n'
            "        <h3>CAPM vs PMP in Malaysia</h3>\n"
            "        <p>Compare eligibility, exams, costs and career paths to choose the right PMI certification.</p>\n"
            '        <span class="card-link">Learn more →</span>\n'
            "      </a>\n"
            + card_marker
        )
        if card_marker not in hub:
            raise SystemExit("blog hub card marker not found")
        blog_hub.write_text(hub.replace(card_marker, new_card, 1), encoding="utf-8")
        print("Updated blog.html cards")
    else:
        print("blog.html cards already present")

    sitemap = ROOT / "sitemap.xml"
    sm = sitemap.read_text(encoding="utf-8")
    entry = (
        f"  <url><loc>{SITE}/blog/{SLUG}</loc>"
        "<changefreq>monthly</changefreq><priority>0.7</priority></url>\n"
    )
    if f"/blog/{SLUG}" not in sm:
        # Insert after blog home
        marker = (
            "  <url><loc>https://www.nexpertsacademy.com/blog</loc>"
            "<changefreq>weekly</changefreq><priority>0.6</priority></url>\n"
        )
        if marker not in sm:
            raise SystemExit("sitemap blog marker not found")
        sitemap.write_text(sm.replace(marker, marker + entry), encoding="utf-8")
        print("Updated sitemap.xml")
    else:
        print("sitemap.xml already wired")

    # Link from CAPM course comparison CTA if present
    capm = ROOT / "courses" / "capm.html"
    if capm.exists():
        chtml = capm.read_text(encoding="utf-8")
        blog_link = f'<a href="/blog/{SLUG}" style="color:var(--blue);font-weight:600;text-decoration:none">CAPM vs PMP guide</a>'
        if f"/blog/{SLUG}" not in chtml:
            needle = (
                '<a href="/courses/pmp" style="color:var(--blue);font-weight:600;text-decoration:none">'
                "PMP Certification Training</a>"
            )
            if needle in chtml:
                chtml = chtml.replace(
                    needle,
                    needle + " · " + blog_link,
                    1,
                )
                capm.write_text(chtml, encoding="utf-8")
                print("Linked blog from courses/capm.html")
            else:
                print("CAPM course CTA needle not found; skipped course link")
        else:
            print("CAPM course already links blog")

    pmp = ROOT / "courses" / "pmp.html"
    if pmp.exists():
        phtml = pmp.read_text(encoding="utf-8")
        if f"/blog/{SLUG}" not in phtml:
            insert = (
                f'  <p class="body-text" style="margin-top:16px">'
                f'<a href="/blog/{SLUG}" style="color:var(--blue);font-weight:600;text-decoration:none">'
                f"Read the CAPM vs PMP comparison guide →</a></p>\n"
            )
            # Insert just before roadmap section closes (before reviews).
            close_and_reviews = "  </div>\n\n  <div id=\"sec-reviews\" class=\"content-sec\""
            reviews = phtml.find(close_and_reviews)
            roadmap = phtml.find('id="sec-roadmap"')
            if roadmap > 0 and reviews > roadmap:
                phtml = (
                    phtml[:reviews]
                    + insert
                    + phtml[reviews:]
                )
                pmp.write_text(phtml, encoding="utf-8")
                print("Linked blog from courses/pmp.html")
            else:
                print("PMP roadmap marker not found; skipped course link")
        else:
            print("PMP course already links blog")


def main() -> None:
    # Wire nav sources first so rendered blog nav includes this article.
    wire_site()
    build_page()


if __name__ == "__main__":
    main()
