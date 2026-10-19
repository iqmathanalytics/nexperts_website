# -*- coding: utf-8 -*-
"""Generate two new cybersecurity blog pages and wire nav/inject/blog hub."""
from __future__ import annotations

import html as html_lib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from site_nav import NAV_ASSET_TAGS, render_site_nav, render_whatsapp_float  # noqa: E402

SITE = "https://www.nexpertsacademy.com"


def esc(s: str) -> str:
    return html_lib.escape(s, quote=False)


def slugify(text: str) -> str:
    t = re.sub(r"<[^>]+>", "", text)
    t = re.sub(r"[^a-zA-Z0-9\s-]", "", t.lower())
    t = re.sub(r"\s+", "-", t.strip())
    return t[:90] or "section"


def linkify(text: str) -> str:
    """Escape then add safe internal/external links for known phrases."""
    s = esc(text)
    replacements = [
        (
            "Nexperts Academy’s website",
            '<a href="/">Nexperts Academy’s website</a>',
        ),
        (
            "Nexperts Academy's website",
            '<a href="/">Nexperts Academy\'s website</a>',
        ),
        (
            "https://www.nexpertsacademy.com/",
            '<a href="/">https://www.nexpertsacademy.com/</a>',
        ),
        (
            "Nexperts’ currently listed courses",
            '<a href="/#courses">Nexperts’ currently listed courses</a>',
        ),
        (
            "Nexperts' currently listed courses",
            '<a href="/#courses">Nexperts\' currently listed courses</a>',
        ),
        (
            "current Nexperts course information",
            '<a href="/#courses">current Nexperts course information</a>',
        ),
        (
            "Nexperts Academy’s current course information",
            '<a href="/#courses">Nexperts Academy’s current course information</a>',
        ),
        (
            "Cisco CCNA",
            '<a href="/courses/ccna">Cisco CCNA</a>',
        ),
        (
            "CompTIA Network+",
            '<a href="/courses/comptia-network-plus">CompTIA Network+</a>',
        ),
        (
            "CompTIA Security+",
            '<a href="/courses/comptia-security-plus">CompTIA Security+</a>',
        ),
        (
            "CompTIA CySA+",
            '<a href="/courses/comptia-cysa-plus">CompTIA CySA+</a>',
        ),
        (
            "CompTIA PenTest+",
            '<a href="/courses/comptia-pentest-plus">CompTIA PenTest+</a>',
        ),
        (
            "ISC2 Certified in Cybersecurity",
            '<a href="/courses/cc-certified-in-cybersecurity">ISC2 Certified in Cybersecurity</a>',
        ),
        (
            "Certified Ethical Hacker",
            '<a href="/courses/ceh">Certified Ethical Hacker</a>',
        ),
        (
            " CEH,",
            ' <a href="/courses/ceh">CEH</a>,',
        ),
        (
            "CPENT AI",
            '<a href="/courses/cpent-ai">CPENT AI</a>',
        ),
        (
            "CHFI",
            '<a href="/courses/chfi-v11">CHFI</a>',
        ),
        (
            "CND",
            '<a href="/courses/cnd-v3">CND</a>',
        ),
        (
            "CCISO",
            '<a href="/courses/cciso">CCISO</a>',
        ),
        (
            "ECIH",
            '<a href="/courses/ecih">ECIH</a>',
        ),
        (
            "cyber-security-bootcamp",
            "cyber-security-bootcamp",
        ),
    ]
    for a, b in replacements:
        s = s.replace(a, b)
    # Avoid double-linking CEH inside Certified Ethical Hacker
    s = s.replace(
        '<a href="/courses/ceh"><a href="/courses/ceh">Certified Ethical Hacker</a></a>',
        '<a href="/courses/ceh">Certified Ethical Hacker</a>',
    )
    return s


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
.blog-video{position:relative;padding-bottom:56.25%;height:0;margin:1.5rem 0;border-radius:12px;overflow:hidden;border:1px solid var(--line)}
.blog-video iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
footer{background:#0d1117;color:rgba(255,255,255,.5);text-align:center;padding:32px 24px;font-size:.75rem}
footer a{color:rgba(255,255,255,.65);text-decoration:none}
</style>
<link rel="stylesheet" href="/css/whatsapp-float.css">"""


def page_shell(
    *,
    slug: str,
    meta_title: str,
    meta_desc: str,
    hero_title_html: str,
    hero_crumb: str,
    hero_meta: str,
    body_html: str,
    toc_items: list[tuple[str, str]],
    cards_html: str,
) -> str:
    toc = "".join(
        f'<li><a href="#{sid}">{esc(label)}</a></li>' for sid, label in toc_items
    )
    nav = render_site_nav(variant="inner", current_path=f"/blog/{slug}")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
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
<link rel="canonical" href="{SITE}/blog/{slug}">
<meta property="og:title" content="{html_lib.escape(meta_title, quote=True)}">
<meta property="og:description" content="{html_lib.escape(meta_desc, quote=True)}">
<meta property="og:url" content="{SITE}/blog/{slug}">
<meta property="og:image" content="{SITE}/image/nexperts-logo.png">
<meta property="og:site_name" content="Nexperts Academy">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html_lib.escape(meta_title, quote=True)}">
<meta name="twitter:description" content="{html_lib.escape(meta_desc, quote=True)}">
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
  <p style="margin-top:2rem"><a href="/contact-us#enquire" style="color:var(--blue);font-weight:700">Enquire about cybersecurity training →</a></p>
</section>
<footer>
  <p>© Nexperts Academy Sdn Bhd · <a href="/">Home</a> · <a href="/blog">Blog</a> · <a href="/privacy-policy">Privacy</a></p>
</footer>
<script src="/js/site-nav-mobile.js" defer></script>
{render_whatsapp_float()}
</body>
</html>
"""


def table_html(headers: list[str], rows: list[list[str]]) -> str:
    th = "".join(f"<th scope=\"col\">{esc(h)}</th>" for h in headers)
    body = []
    for row in rows:
        tds = "".join(f"<td>{esc(c)}</td>" for c in row)
        body.append(f"<tr>{tds}</tr>")
    return (
        '<div class="blog-table-wrap"><table class="blog-table blog-table--compare">'
        f"<thead><tr>{th}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"
    )


def build_cybersecurity_courses() -> None:
    slug = "cybersecurity-courses-malaysia-students"
    meta_title = (
        "Cyber Security Courses in Malaysia for Computer Science Students | Nexperts Academy"
    )
    meta_desc = (
        "Compare cyber security courses in Malaysia for computer science students, "
        "including degree options, entry requirements, hands-on labs and certification paths."
    )
    toc: list[tuple[str, str]] = [
        ("key-takeaways", "Key Takeaways"),
        (
            "how-to-choose-cyber-security-courses-in-malaysia-for-computer-science-students",
            "How to Choose Cyber Security Courses in Malaysia for Computer Science Students",
        ),
        (
            "what-prerequisites-do-malaysian-cyber-security-programs-set",
            "What Prerequisites Do Malaysian Cyber Security Programs Set?",
        ),
        (
            "how-do-the-available-programs-compare-in-course-content",
            "How Do the Available Programs Compare in Course Content?",
        ),
        (
            "what-should-hands-on-cyber-security-labs-include",
            "What Should Hands-On Cyber Security Labs Include?",
        ),
        (
            "which-certification-roadmap-fits-your-career-goal",
            "Which Certification Roadmap Fits Your Career Goal?",
        ),
        (
            "which-course-is-the-best-fit-for-your-situation",
            "Which Course Is the Best Fit for Your Situation?",
        ),
        ("conclusion", "Conclusion"),
        ("faq", "Frequently Asked Questions"),
    ]

    parts: list[str] = []
    parts.append(
        "<p>A computer science student who knows some programming may still be unsure whether to start with networking, defensive work, or penetration testing. Choosing a course before identifying that starting point can lead to lessons that feel too advanced or too broad.</p>"
    )
    parts.append(
        "<p>A degree program offers a university qualification, while a short course provides focused provider training. An authorized isolated lab is a sandboxed environment where learners test only systems they own or have explicit permission to use. Course fit depends on your skills and intended work, not the longest list of topics.</p>"
    )
    parts.append(
        "<p>Prerequisites, practical labs, path focus, and certification alignment offer useful comparison points. Mathematics, a science ICT subject, and SPM-level results may also matter for entry to some degree programs. The right first step varies with what you already know and what you want to do.</p>"
    )
    parts.append('<h2 id="key-takeaways">Key Takeaways</h2>')
    parts.append(
        "<ul>"
        "<li>Match study format to your goal.</li>"
        "<li>Check entry requirements and mathematics conditions.</li>"
        "<li>Look for practical, authorized lab work.</li>"
        "<li>Compare degree programs with short courses fairly.</li>"
        "<li>Choose training that fits your current skills.</li>"
        "</ul>"
    )
    parts.append(
        '<h2 id="how-to-choose-cyber-security-courses-in-malaysia-for-computer-science-students">How to Choose Cyber Security Courses in Malaysia for Computer Science Students</h2>'
    )
    parts.append(
        "<p>The best starting point is a course that matches your current foundations and intended role. Start where you are, then build the skills and knowledge needed for the next step, rather than choosing a path by its title alone.</p>"
    )
    parts.append(
        "<p>Choose a course that fits your foundations and intended role, then build toward more advanced security work.</p>"
    )
    parts.append(
        "<p>Networking basics and Linux command-line skills make later cyber security topics easier to understand. An IP address identifies a device on a network; DNS links names to addresses, while ports and traffic flows show how systems communicate.</p>"
    )
    parts.append(
        '<div class="blog-video"><iframe src="https://www.youtube.com/embed/qjFxwmTuZHM" title="Cyber security foundations overview" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>'
    )
    parts.append(
        "<h3>Build networking and Linux foundations before specializing</h3>"
    )
    parts.append(
        "<p>Linux is common in security work, so practice using its command line, managing users and permissions, and reading logs. These tasks help you see how a system is configured and what activity it records. Introductory programming, especially Python, can help you automate simple tasks and understand scripts.</p>"
    )
    parts.append("<p>Use this quick checklist to see what you have already covered:</p>")
    parts.append(
        "<ul><li>Networking basics</li><li>Linux command line</li><li>Introductory Python</li><li>A clear career interest</li></ul>"
    )
    parts.append("<h3>Choose between defensive and offensive work</h3>")
    parts.append(
        "<p>A blue-team path centers on monitoring systems, detecting suspicious activity, and responding to incidents. A red-team path tests defenses within an authorized scope, then reports weaknesses so they can be fixed. Both need careful reasoning, and neither requires you to be an expert programmer before you begin.</p>"
    )
    parts.append(
        "<p>Consider which work holds your attention: following an alert through system logs, or testing a defined target and explaining its weaknesses. Mathematics can support technical problem-solving, but the amount you use varies by task and role. Interest helps you choose a direction; it does not confirm that you meet a program’s entry rules.</p>"
    )
    parts.append(
        "<p>Check the exact entry requirements next, because Malaysian programs may set different conditions for school leavers, foundation students, and diploma applicants.</p>"
    )
    parts.append(
        '<h2 id="what-prerequisites-do-malaysian-cyber-security-programs-set">What Prerequisites Do Malaysian Cyber Security Programs Set?</h2>'
    )
    parts.append(
        "<p>A Mathematics credit can count differently across programs, even when the stated Foundation or Matriculation minimum CGPA is similar. Check the exact route for your qualification, including any extra Mathematics module or diploma threshold.</p>"
    )
    parts.append(
        "<p>APU, City University, and LSBF Malaysia’s University of Suffolk pathway each state a minimum CGPA of 2.0 for Foundation or Matriculation applicants, but their Mathematics conditions differ. A credit in Additional Mathematics is not always interchangeable with Mathematics plus another relevant subject.</p>"
    )
    parts.append(
        table_html(
            [
                "Program",
                "Stated Foundation or Matriculation CGPA",
                "Mathematics condition",
                "Additional condition or remedy",
            ],
            [
                [
                    "APU, three-year BSc pathway",
                    "2.0",
                    "Additional Mathematics credit, or Mathematics and Science or ICT credits at SPM or equivalent",
                    "Equivalent Foundation or Matriculation Mathematics may qualify for exemption; Further Mathematics module may be required",
                ],
                [
                    "City University, Bachelor of Computer Science (Cyber Security)",
                    "2.0",
                    "Stated SPM-level Mathematics routes",
                    "Reinforcement Mathematics if equivalent Mathematics condition is unmet; computing diploma CGPA 2.50, Science and Technology diploma CGPA 2.75",
                ],
                [
                    "LSBF Malaysia, University of Suffolk pathway",
                    "2.00",
                    "Additional Mathematics credit, or Mathematics plus one Science, Technology, or Engineering subject at SPM or equivalent",
                    "Pass in Matriculation or Foundation studies",
                ],
            ],
        )
    )
    parts.append("<h3>Entry routes for school leavers and foundation students</h3>")
    parts.append(
        "<p>For APU’s three-year BSc pathway, applicants need a pass in Matriculation or Foundation studies with a minimum CGPA of 2.0. They also need either a credit in Additional Mathematics or credits in Mathematics and a Science or ICT subject at SPM or equivalent.</p>"
    )
    parts.append(
        "<p>APU may exempt the Additional Mathematics condition when Foundation or Matriculation Mathematics is equivalent to or higher than SPM Additional Mathematics. It may still require a Further Mathematics prerequisite module. LSBF Malaysia’s University of Suffolk pathway accepts a pass in Matriculation or Foundation studies with minimum CGPA 2.00, plus its stated SPM-level Mathematics route.</p>"
    )
    parts.append("<h3>Mathematics and diploma requirements to check</h3>")
    parts.append(
        "<p>City University’s Bachelor of Computer Science (Cyber Security) is a 36-month full-time program. Its stated Foundation or Matriculation minimum CGPA is 2.0, alongside stated SPM-level Mathematics routes. Candidates who do not meet the equivalent Mathematics requirement must take reinforcement Mathematics.</p>"
    )
    parts.append(
        "<p>City University says some diploma applicants below its stated CGPA thresholds may be considered after rigorous assessment. A minimum grade or credit can also depend on the qualification and institution’s equivalency decision. Check whether your mathematics SPM result, Additional Mathematics SPM result, or other subject meets the route you plan to use.</p>"
    )
    parts.append(
        "<p>These entry conditions help you assess eligibility; after admission, the next question is what each programme actually teaches.</p>"
    )
    parts.append(
        '<h2 id="how-do-the-available-programs-compare-in-course-content">How Do the Available Programs Compare in Course Content?</h2>'
    )
    parts.append(
        "<p>A degree program and a short course serve different study needs, so compare each by its stated content and format. Look at the structure, not simply the number of security subjects named.</p>"
    )
    parts.append(
        "<p>The three degree pathways below list distinct study timelines and subject sequences; they are not interchangeable qualifications. APU includes networking and programming early, City University lists several security subjects in Years 2 and 3, and the LSBF pathway introduces its cyber security route toward the end of Year 1.</p>"
    )
    parts.append(
        table_html(
            [
                "Program",
                "Duration or pathway timing",
                "Named security subjects",
                "Practical or workplace component",
            ],
            [
                [
                    "APU, BSc pathway",
                    "Three years; first-level modules include networking and Python",
                    "Introduction to Security and Forensic Technologies",
                    "16-week internship listed at Degree Level 2",
                ],
                [
                    "City University, Bachelor of Computer Science (Cyber Security)",
                    "36 months full time; security subjects listed in Years 2 and 3",
                    "Cryptography and Information Security, Cyber Security, Computer Intrusion Detection, Malware Analysis, Digital Forensics, Penetration Testing and Vulnerability Assessment, Ethical Hacking, Cyber Threat Intelligence, Security Analytics and Incident Response",
                    "No workplace component stated here",
                ],
                [
                    "LSBF Malaysia, University of Suffolk pathway",
                    "Three years full time or five years and eight months part time; pathway choice near end of Year 1",
                    "Security Testing, Cyber-Physical Security, Cyber Forensics and Intrusion Management, Cyber Security: Attack and Defence",
                    "Industrial Training",
                ],
            ],
        )
    )
    parts.append(
        "<p>APU’s first-level modules also include Introduction to Networking, Python Programming, and databases. The internship appears at Degree Level 2. City University’s listed subjects move from cryptography and detection to testing, threat intelligence, and incident response.</p>"
    )
    parts.append(
        f"<p>{linkify('For Nexperts, treat each currently listed course as short-course training, not as a degree program. Compare its published course name, prerequisites, learning outcomes, and any stated certification alignment with your goal. A short course may suit focused training alongside a degree, but its qualification is not the same as a university degree.')}</p>"
    )
    parts.append(
        f"<p>{linkify('Do not assume details that a course page does not state, such as lab features or certification links. Check the current Nexperts course information and ask about any point that matters to your choice. Then judge whether the hands-on work produces evidence you can explain.')}</p>"
    )
    parts.append(
        '<h2 id="what-should-hands-on-cyber-security-labs-include">What Should Hands-On Cyber Security Labs Include?</h2>'
    )
    parts.append(
        "<p>A useful lab might ask you to investigate an alert, identify what happened, and recommend a response. Good practice is active: you make a decision, observe the result, and explain your reasoning.</p>"
    )
    parts.append(
        "<p>An authorized isolated lab should keep every exercise on systems you own or have explicit permission to test. A demonstration alone is not enough; you need a task, a safe scope, observable evidence, and feedback or a way to check your results.</p>"
    )
    parts.append("<h3>Practice in a controlled, authorized environment</h3>")
    parts.append(
        "<p>A well-planned progression can start with inspecting a system and its logs. Next, identify a weakness in a deliberately vulnerable environment, then test a defensive control. Each activity should have clear boundaries, so you know which machines and actions are allowed.</p>"
    )
    parts.append(
        "<p>For example, a lab may ask you to review login records and decide whether an unusual pattern needs investigation. You should be able to point to the relevant evidence, not just name a possible threat. A clear scope also prevents a practice task from drifting onto a public system.</p>"
    )
    parts.append("<h3>Keep evidence of the work and explain the findings</h3>")
    parts.append(
        "<p>Record what you checked, what you observed, and how you reached your conclusion. A useful report explains the weakness, the risk it creates, and a practical remediation. That record shows how you think, even when the exercise uses a small test environment.</p>"
    )
    parts.append(
        "<p>Look for tasks with a defined goal and a way to confirm whether your action worked. Feedback can come from an instructor, a lab result, or a checklist tied to the task. If the course only shows tools without giving you work to complete, it may offer less practice than you need.</p>"
    )
    parts.append(
        "<p>Practical evidence can help you judge a course’s value and give you useful material to build on during certification study.</p>"
    )
    parts.append(
        '<h2 id="which-certification-roadmap-fits-your-career-goal">Which Certification Roadmap Fits Your Career Goal?</h2>'
    )
    parts.append(
        "<p>A certification roadmap should follow the work you want to do, not the appeal of collecting certificates. Pick by role, then choose a credential that fits your current knowledge and study plan.</p>"
    )
    parts.append(
        f"<p>{linkify('Certifications can structure learning, but they do not replace core skills or an academic qualification. You might investigate Network+ or Cisco CCNA for networking confidence, then explore broad security fundamentals through ISC2 Certified in Cybersecurity or CompTIA Security+.')}</p>"
    )
    parts.append("<h3>Start with networking and broad security knowledge</h3>")
    parts.append(
        f"<p>{linkify('If IP addresses, routing, and network services still feel unfamiliar, a networking credential may help you organize the basics. CompTIA Network+ and Cisco CCNA are examples to compare. A beginner who wants a wider security overview can look at ISC2 Certified in Cybersecurity or CompTIA Security+.')}</p>"
    )
    parts.append("<h3>Add role-focused credentials after choosing a path</h3>")
    parts.append(
        f"<p>{linkify('For a blue-team path focused on security operations center (SOC) analysis or incident response, CompTIA CySA+ is one option to investigate. For a red-team path involving authorized penetration testing, CompTIA PenTest+ is another. These are choices, not required steps or promises of a job.')}</p>"
    )
    parts.append(
        "<p>Use this simple planning list to connect a credential with work you can demonstrate:</p>"
    )
    parts.append(
        "<ul>"
        f"<li>{linkify('Goal: networking confidence; foundation: network concepts; possible certification: Network+ or CCNA; practical proof: explain a basic network flow.')}</li>"
        f"<li>{linkify('Goal: broad security basics; foundation: core computer skills; possible certification: Certified in Cybersecurity or Security+; practical proof: describe a common security risk.')}</li>"
        f"<li>{linkify('Goal: blue-team analysis; foundation: networking and log review; possible certification: CySA+; practical proof: investigate an alert in a lab.')}</li>"
        f"<li>{linkify('Goal: authorized testing; foundation: networking and Linux; possible certification: PenTest+; practical proof: document a permitted test and remediation.')}</li>"
        "</ul>"
    )
    parts.append(
        "<p>Exam objectives, eligibility rules, and fees can change, so check current details before enrolling. Pair study with practice you can explain, rather than relying on a certificate name alone. Your final choice should also fit the course format, actual entry requirements, and your schedule.</p>"
    )
    parts.append(
        '<h2 id="which-course-is-the-best-fit-for-your-situation">Which Course Is the Best Fit for Your Situation?</h2>'
    )
    parts.append(
        "<p>Two computer science students may choose different paths: one prefers monitoring and response, while the other wants to test defenses. Your best fit depends on your starting skills, preferred work, and study situation.</p>"
    )
    parts.append(
        table_html(
            [
                "Student situation",
                "Best-fit study direction",
                "What to verify before enrolling",
            ],
            [
                [
                    "SPM or Foundation student still building fundamentals",
                    "Degree programme or introductory short course",
                    "Minimum grade, mathematics route, prerequisites, and delivery schedule",
                ],
                [
                    "Computer science student seeking defensive operations skills",
                    "Blue-team path with monitoring and incident-response practice",
                    "Lab scope, assessment format, and practice with alerts or logs",
                ],
                [
                    "Student interested in authorized penetration testing",
                    "Red-team path with permitted testing exercises",
                    "Safe lab scope, prerequisites, assessment format, and certification alignment",
                ],
                [
                    "Student seeking focused training alongside a degree",
                    "Short course that complements current studies",
                    "Workload, delivery schedule, entry requirements, and stated certification links",
                ],
            ],
        )
    )
    parts.append(
        "<p>Compare the entry rules, practical work, and schedule before choosing a programme. A course can support preparation for roles such as SOC analyst, incident-response analyst, penetration tester, cyber security engineer, or digital forensics analyst, but completion does not guarantee employment.</p>"
    )
    parts.append(
        "<p>Choose based on the work you want to practise, then confirm the course requirements and format.</p>"
    )
    parts.append(
        "<p>A minimum grade may shape which degree programme you can enter, while a short course may fit a different schedule. Check how assessments work and whether lab practice matches the role you have in mind. Career titles are examples, not promised outcomes.</p>"
    )
    parts.append(
        f"<p>{linkify('Review Nexperts’ currently listed courses, then ask the provider to confirm prerequisites, lab work, and certification alignment for your goal. Verify those course-specific details before making an enrollment decision.')}</p>"
    )
    parts.append('<h2 id="conclusion">Conclusion</h2>')
    parts.append(
        "<p>Shortlist courses by fit, not by title alone. Your intended work and the skills you want to build should guide the choice between a degree program and focused short-course training.</p>"
    )
    parts.append(
        "<p>Check prerequisites and practical work before you commit. Confirm that the entry route matches your qualification and that hands-on tasks give you a chance to apply what you learn. A clear match can make study more useful alongside your current computer science work.</p>"
    )
    parts.append(
        f"<p>{linkify('Visit Nexperts Academy’s current course information and confirm the course fit with the provider before enrolling.')}</p>"
    )
    parts.append('<h2 id="faq">Frequently Asked Questions</h2><section class="blog-faq">')
    faqs = [
        (
            "How much do cyber security courses in Malaysia cost?",
            "Costs depend on the course type, its duration, and whether training or exam fees are included. A university degree program and a focused short course have different structures, so compare what each fee covers. Nexperts pricing can change by course; check the provider’s current course information for its listed fees and any separate exam costs.",
        ),
        (
            "Can I start learning cyber security while I am still studying computer science?",
            "Yes, you can start while studying computer science, as long as the extra workload fits your academic schedule. Use coursework in networking, programming, and operating systems as a base for security topics. A short course can add focused practice, but plan study time around exams and major assignments so you can complete both well.",
        ),
        (
            "Do I need programming experience before taking a beginner course?",
            "Programming helps with some security tasks, but requirements vary by course and role. Many beginner topics can start with basic computer and networking knowledge, while scripting can make later work easier. Python is a useful language to investigate because it can help automate simple tasks and read basic scripts. Check course prerequisites before signing up.",
        ),
        (
            "Is an online cyber security course recognized in Malaysia?",
            "Recognition depends on the qualification and provider, not simply whether the course is online. For a degree program, confirm its stated accreditation and awarding institution. For a certificate, check who issues it and what status that issuer has. Also confirm whether the course grants a formal qualification or only records completion of training.",
        ),
        (
            "Do I need a certification to apply for an entry-level security job?",
            "No single certification is required for every entry-level security job. Employer expectations vary by role, and practical evidence, relevant knowledge, and academic qualifications may also matter. Review job postings for the work you want, then compare their stated requirements with your experience. A certificate can support an application, but it does not guarantee an interview or offer.",
        ),
        (
            "Can I practise penetration testing on websites I find online?",
            "No, you should not test websites without ownership or explicit permission. Even a basic scan can affect a system or violate its rules. Use an authorized isolated lab, which limits practice to systems you own or have clear permission to test. Follow the lab’s scope and avoid probing public websites, even when your intent is only to learn.",
        ),
    ]
    for q, a in faqs:
        parts.append(
            f'<div class="faq-item"><p class="faq-q"><strong>{esc(q)}</strong></p>'
            f"<p>{linkify(a)}</p></div>"
        )
    parts.append("</section>")

    cards = """      <a class="card" href="/courses/ceh">
        <h3>CEH Ethical Hacking</h3>
        <p>Hands-on ethical hacking training for learners building offensive security skills.</p>
        <span class="card-link">Learn more →</span>
      </a>
      <a class="card" href="/blog/how-to-become-ethical-hacker-malaysia">
        <h3>Become an Ethical Hacker</h3>
        <p>Practical Malaysia-focused roadmap for ethical hacking training and careers.</p>
        <span class="card-link">Learn more →</span>
      </a>
      <a class="card" href="/contact-us">
        <h3>Contact</h3>
        <p>Ask about student-friendly cybersecurity pathways.</p>
        <span class="card-link">Learn more →</span>
      </a>"""

    html = page_shell(
        slug=slug,
        meta_title=meta_title,
        meta_desc=meta_desc,
        hero_title_html="Cyber Security Courses in Malaysia<br><em>for Computer Science Students</em>",
        hero_crumb="Cyber Security Courses Malaysia",
        hero_meta="October 2026 · Nexperts Cybersecurity Practice",
        body_html="\n        ".join(parts),
        toc_items=toc,
        cards_html=cards,
    )
    out = ROOT / "blog" / f"{slug}.html"
    out.write_text(html, encoding="utf-8", newline="\n")
    print("Wrote", out.relative_to(ROOT))


def build_ethical_hacker() -> None:
    slug = "how-to-become-ethical-hacker-malaysia"
    meta_title = "How to Become an Ethical Hacker in Malaysia Training | Nexperts Academy"
    meta_desc = (
        "Learn how to become an ethical hacker in Malaysia, including IT skills, "
        "training options, certifications, safe labs and cybersecurity career paths."
    )
    toc: list[tuple[str, str]] = [
        ("key-takeaways", "Key Takeaways"),
        (
            "how-to-become-an-ethical-hacker-in-malaysia",
            "How to Become an Ethical Hacker in Malaysia",
        ),
        (
            "which-technical-skills-should-you-build-first",
            "Which technical skills should you build first?",
        ),
        (
            "what-should-ethical-hacking-training-cover",
            "What should ethical hacking training cover?",
        ),
        (
            "how-do-you-choose-an-ethical-hacking-course-in-malaysia",
            "How do you choose an ethical hacking course in Malaysia?",
        ),
        (
            "how-can-you-gain-hands-on-experience-safely",
            "How can you gain hands-on experience safely?",
        ),
        (
            "which-certifications-and-cybersecurity-roles-can-you-pursue",
            "Which certifications and cybersecurity roles can you pursue?",
        ),
        ("conclusion", "Conclusion"),
        ("faq", "Frequently Asked Questions"),
    ]

    parts: list[str] = []
    parts.append(
        "<p>You can work toward becoming an ethical hacker in Malaysia by building IT foundations and practicing responsibly. A technical background helps, but you can develop one through steady study. A penetration test is an authorized, scoped attempt to find and safely demonstrate security weaknesses so they can be fixed.</p>"
    )
    parts.append(
        "<p>The route combines core IT learning, structured training, practice in authorized labs, and continued learning as cybersecurity changes. A course can build useful skills, but completing one does not guarantee a job. Employers may also look for practical ability, clear communication, and responsible conduct.</p>"
    )
    parts.append(
        "<p>Your starting point may be a technical background, a related IT job, or independent study. What matters is building knowledge in stages and showing how you apply it. Begin with a staged learning plan and the first practical steps.</p>"
    )
    parts.append('<h2 id="key-takeaways">Key Takeaways</h2>')
    parts.append(
        "<ul>"
        "<li>Start with core computer and networking knowledge.</li>"
        "<li>Use authorized labs for hands-on practice.</li>"
        "<li>Choose training that fits your experience and schedule.</li>"
        "<li>Document exercises and explain how you would fix risks.</li>"
        "<li>Keep learning; a course alone does not secure a job.</li>"
        "</ul>"
    )
    parts.append(
        '<h2 id="how-to-become-an-ethical-hacker-in-malaysia">How to Become an Ethical Hacker in Malaysia</h2>'
    )
    parts.append(
        "<p>A staged route is more useful than jumping straight into advanced hacking tools. Beginner study can prepare you for ethical hacking without requiring you to master every tool first.</p>"
    )
    parts.append(
        "<p>Build knowledge in a sequence that connects learning to safe practice. Skipping networking and operating-system basics to start with exploit tools is a common mistake. It can leave you unable to understand what a test result means.</p>"
    )
    parts.append(
        "<p>Use these four steps to move from interest toward entry-level readiness:</p>"
    )
    parts.append(
        "<ol>"
        "<li>Learn core IT concepts, including how computers, networks, and operating systems work.</li>"
        "<li>Practice in authorized labs where exercises are designed for safe testing.</li>"
        "<li>Take structured ethical hacking training that teaches a clear testing process.</li>"
        "<li>Build evidence of your skills through documented exercises and clear explanations.</li>"
        "</ol>"
    )
    parts.append(
        "<p>You can begin with beginner materials and work through unfamiliar ideas one at a time. You do not need to know every tool before your first course. A useful training program should help you apply concepts, not just memorize tool names.</p>"
    )
    parts.append(
        "<p>Keep each exercise within its authorized environment and record what you tried, what you observed, and what the result means. That habit helps you explain your work rather than simply list techniques.</p>"
    )
    parts.append(
        "<p>The sequence becomes easier when you understand the technical foundations behind each test. Networking and operating-system basics are the first areas to strengthen.</p>"
    )
    parts.append(
        '<h2 id="which-technical-skills-should-you-build-first">Which technical skills should you build first?</h2>'
    )
    parts.append(
        "<p>A learner may identify an open network service but still need to understand what it does before assessing it. That distinction is why core computer knowledge matters in security work.</p>"
    )
    parts.append(
        "<p>Build familiarity with operating systems, TCP/IP networking, command-line use, scripting basics, and security concepts. Understanding how systems communicate helps you test vulnerabilities with care and explain what you find.</p>"
    )
    parts.append("<h3>Networking and operating-system basics</h3>")
    parts.append(
        "<p>IP addressing helps you identify where a device sits on a network. Ports and protocols show how services communicate, while permissions control what a user or process can do.</p>"
    )
    parts.append(
        "<p>Operating-system behavior matters because the same service can act differently across systems. Before testing a reachable service, trace its path: check the address, identify the port and protocol, then learn what process listens there.</p>"
    )
    parts.append(
        "<p>That simple sequence helps you ask whether access is expected and what the service is meant to do. It also gives you a reason to stop if the system is outside your authorized scope.</p>"
    )
    parts.append("<h3>Scripting, security concepts, and analytical thinking</h3>")
    parts.append(
        "<p>Basic scripting can help you repeat routine tasks and handle simple data. You do not need advanced software development skills to begin, but you should be willing to read commands and understand their effects.</p>"
    )
    parts.append(
        "<p>Careful observation is just as important. Compare expected behavior with actual results, keep notes, and reason from evidence instead of assuming every alert proves a weakness.</p>"
    )
    parts.append(
        "<p>These foundations make later exercises more meaningful. A suitable course should teach them in context, not assume every learner already has them.</p>"
    )
    parts.append(
        '<h2 id="what-should-ethical-hacking-training-cover">What should ethical hacking training cover?</h2>'
    )
    parts.append(
        "<p>If you find an exposed service, you still need to assess its purpose, validate the risk safely, and explain what should change. A useful course teaches that process, not just a set of tools.</p>"
    )
    parts.append(
        "<p>Look for connected stages: reconnaissance, scanning, vulnerability assessment, controlled testing, and remediation. Tool familiarity alone does not prove you can assess risk or explain a fix.</p>"
    )
    parts.append("<h3>Reconnaissance and vulnerability assessment</h3>")
    parts.append(
        "<p>Reconnaissance gathers information about an approved target before testing begins. Course topics may include footprinting, open-source intelligence, protocol enumeration, and scanning.</p>"
    )
    parts.append(
        "<p>Vulnerability analysis helps you judge whether a finding is relevant and what could happen if someone misused it. Training may also cover malware threats and social engineering, with practice limited to authorized scenarios.</p>"
    )
    parts.append(
        "<p>The goal is to connect each observation to evidence. A list of open ports is not yet an assessment; you need to understand what is exposed and why it matters.</p>"
    )
    parts.append("<h3>Exploitation, web testing, and remediation</h3>")
    parts.append(
        "<p>Controlled exploitation can show whether a suspected weakness is real, but it must stay within the agreed scope. Metasploit is one example of a framework used in hands-on training.</p>"
    )
    parts.append(
        "<p>Web application testing and wireless security are distinct practice areas. Web topics can include SQL injection, while wireless exercises examine the security of wireless networks.</p>"
    )
    parts.append(
        "<p>After testing, learners should explain the impact and suggest a practical fix. A course that teaches tools without risk analysis or remediation leaves an important gap.</p>"
    )
    parts.append(
        "<p>Once the syllabus makes sense, compare course formats, practice access, and learner support before choosing a program.</p>"
    )
    parts.append(
        '<h2 id="how-do-you-choose-an-ethical-hacking-course-in-malaysia">How do you choose an ethical hacking course in Malaysia?</h2>'
    )
    parts.append(
        "<p>The best course is the one whose format, practice, and assessment fit your starting point and schedule. Compare the delivery as well as the topics before committing.</p>"
    )
    parts.append(
        "<p>Online, blended, and face-to-face training can each work for learners in Malaysia. Check what access and feedback are included, rather than judging a program by its format alone.</p>"
    )
    parts.append(
        table_html(
            ["Format", "How it is delivered", "Best fit", "What to verify"],
            [
                [
                    "Online",
                    "Lessons and activities accessed over the internet",
                    "Learners needing flexible study hours",
                    "Instructor access, lab access, and feedback timing",
                ],
                [
                    "Blended",
                    "Online learning combined with scheduled in-person sessions",
                    "Learners who want flexibility and live support",
                    "Session dates, attendance expectations, and lab access",
                ],
                [
                    "Face-to-face",
                    "Instructor-led sessions at a physical location",
                    "Learners who prefer direct classroom guidance",
                    "Location, class schedule, equipment, and practice time",
                ],
            ],
        )
    )
    parts.append("<h3>Match the format to your schedule</h3>")
    parts.append(
        "<p>Think through your work, family, and study commitments. An online program may offer more control over study time, while scheduled sessions can provide a set pace and direct contact.</p>"
    )
    parts.append(
        "<p>Ask what the course prerequisites are and whether they match your current skills. Professionals changing fields may need more time for foundational topics than learners already working with IT systems.</p>"
    )
    parts.append("<h3>Check the learning support and assessment</h3>")
    parts.append(
        "<p>Find out how learners reach instructors, whether labs are available for practice, and how work is assessed. Ask what a completion document represents and what you must do to earn it.</p>"
    )
    parts.append(
        f"<p>{linkify('A course completion certificate or badge records course completion; it is not automatically an industry certification. Nexperts Academy is one provider to explore. Visit Nexperts Academy’s website and check its current course details before enrolling.')}</p>"
    )
    parts.append(
        '<h2 id="how-can-you-gain-hands-on-experience-safely">How can you gain hands-on experience safely?</h2>'
    )
    parts.append(
        "<p>Practice belongs in a lab or another environment where testing is explicitly authorized. Permission and scope must be clear before you touch a real system.</p>"
    )
    parts.append(
        "<p>Intentionally vulnerable labs and simulations are built for safe exercises. Real systems are different: public accessibility is not permission to test a website or network.</p>"
    )
    parts.append("<h3>Practice only in authorized environments</h3>")
    parts.append(
        "<p>Use an authorized lab for practice when you are learning a new technique. If a real assessment is approved, confirm which systems are in scope and what actions are allowed.</p>"
    )
    parts.append(
        "<p>Do not assume that a public-facing service is open for testing, even if you can reach it from your computer. Testing without permission can affect systems, services, and data.</p>"
    )
    parts.append(
        "<p>Good habits include limiting activity to the agreed target and stopping if you encounter information outside the approved scope. Responsible practice includes knowing when not to proceed.</p>"
    )
    parts.append("<h3>Build a portfolio from documented work</h3>")
    parts.append(
        "<p>Choose exercises that let you explain your process and decisions. Keep a small portfolio with these four artifacts:</p>"
    )
    parts.append(
        "<ul>"
        "<li>Lab notes describing the steps, observations, and results.</li>"
        "<li>A scoped assessment report explaining an authorized test.</li>"
        "<li>Prioritized remediation recommendations tied to identified risks.</li>"
        "<li>A skills log tracking exercises, tools, and concepts practiced.</li>"
        "</ul>"
    )
    parts.append(
        "<p>Write assessment reports so a reader can understand the impact and the recommended fix. Do not expose sensitive data, credentials, or private system details in a portfolio.</p>"
    )
    parts.append(
        "<p>Clear records show how you think, not only which tools you have tried. Documented, responsible practice can help you demonstrate readiness for role-specific work.</p>"
    )
    parts.append(
        '<h2 id="which-certifications-and-cybersecurity-roles-can-you-pursue">Which certifications and cybersecurity roles can you pursue?</h2>'
    )
    parts.append(
        "<p>If vulnerability testing interests you, you may build experience around authorized assessments. Someone drawn to monitoring may focus instead on spotting threats and investigating alerts. Your preferred work should guide your choices.</p>"
    )
    parts.append(
        "<p>Ethical hackers, security analysts, and SOC engineers handle different tasks, though employers may define roles differently. A certification can support your profile, but it does not guarantee employment.</p>"
    )
    parts.append(
        table_html(
            ["Role", "Typical focus", "Example work"],
            [
                [
                    "Ethical hacker",
                    "Authorized testing for security weaknesses",
                    "Assess an approved system and explain a vulnerability",
                ],
                [
                    "Security analyst",
                    "Reviewing security information and investigating risks",
                    "Examine an alert and document what it may indicate",
                ],
                [
                    "SOC engineer",
                    "Supporting security monitoring systems and operations",
                    "Improve how a monitoring system detects a threat",
                ],
            ],
        )
    )
    parts.append(
        "<p>Choose training and credentials for the work you want to do. A respected title cannot replace relevant skills or experience.</p>"
    )
    parts.append(
        f"<p>{linkify('CEH, also called Certified Ethical Hacker, and ECSA are certification names to research. Other EC-Council credentials include CPENT AI, CHFI, CND, CCSE, ECDE, CCISO, and ECIH.')}</p>"
    )
    parts.append(
        "<p>Employers set different credential and experience requirements. Compare those expectations with the work you want, and do not choose an exam only because its title sounds prestigious.</p>"
    )
    parts.append(
        "<p>Narrow your options to training and experience that match a relevant role, then take a clear next step toward building them.</p>"
    )
    parts.append('<h2 id="conclusion">Conclusion</h2>')
    parts.append(
        "<p>Progress comes from combining structured training with consistent, responsible practice. Strong foundations and documented work matter alongside formal learning.</p>"
    )
    parts.append(
        f"<p>{linkify('Review Nexperts Academy’s current information at https://www.nexpertsacademy.com/ and consider whether its program fits your experience and goals. Compare the details with the skills you want to build, then choose one useful area to strengthen.')}</p>"
    )
    parts.append(
        "<p>Take that next step and keep building your security skills through authorized exercises. Clear notes and careful scope will help you show how you work, not just what you have studied.</p>"
    )
    parts.append('<h2 id="faq">Frequently Asked Questions</h2><section class="blog-faq">')
    faqs = [
        (
            "Can I become an ethical hacker without a computer science degree?",
            "Yes, a computer science degree is not the only route into ethical hacking. You still need to demonstrate relevant IT foundations, practical ability, and responsible conduct. You can build those through study, authorized lab work, and documented exercises. Employers set their own requirements, so check the education and experience listed for roles that interest you.",
        ),
        (
            "Do I need to know programming before taking an ethical hacking course?",
            "No, advanced software development is not always required before you begin. Basic scripting familiarity can help you understand commands, automate simple tasks, and work with data. Course prerequisites vary, so check whether a program expects prior coding or networking knowledge. If scripting is new to you, introductory practice can make technical lessons easier to follow.",
        ),
        (
            "How long does it take to learn ethical hacking?",
            "There is no single timeline for learning ethical hacking. Your starting IT skills, weekly study time, and course format all affect how quickly you progress. Completing a course is not the same as becoming job-ready: readiness also depends on applying skills, explaining findings, and practicing responsibly. Set goals around demonstrated ability, not just a course end date.",
        ),
        (
            "Is a course completion certificate the same as a Certified Ethical Hacker certification?",
            "No, a course completion certificate or badge usually documents that you finished a particular program. A Certified Ethical Hacker certification is a professional credential with its own exam or credential requirements. Check what each document proves before presenting it to an employer. Course completion can support learning, but it does not automatically award an industry certification.",
        ),
        (
            "Can I practice ethical hacking on a public website?",
            "No, a public website is not open for testing simply because anyone can access it. Test only when you have explicit authorization and a defined scope. Without both, your activity could affect a real service or expose data. Use intentionally vulnerable labs or simulations for practice, and stop if an authorized exercise moves beyond its agreed limits.",
        ),
        (
            "What is the difference between an ethical hacker and a security analyst?",
            "An ethical hacker focuses on authorized testing to find and demonstrate security weaknesses. A security analyst often reviews alerts and other security information to assess risks or investigate possible incidents. The exact duties can vary by employer, and some teams may share work across roles. Compare job descriptions to see which daily tasks fit your interests and current skills.",
        ),
    ]
    for q, a in faqs:
        parts.append(
            f'<div class="faq-item"><p class="faq-q"><strong>{esc(q)}</strong></p>'
            f"<p>{linkify(a)}</p></div>"
        )
    parts.append("</section>")

    cards = """      <a class="card" href="/courses/ceh">
        <h3>CEH Training</h3>
        <p>Structured ethical hacking programme with practical lab-focused learning.</p>
        <span class="card-link">Learn more →</span>
      </a>
      <a class="card" href="/blog/cybersecurity-courses-malaysia-students">
        <h3>Cyber Courses for Students</h3>
        <p>Compare degree and short-course cyber security options for CS students.</p>
        <span class="card-link">Learn more →</span>
      </a>
      <a class="card" href="/contact-us">
        <h3>Contact</h3>
        <p>Talk to the team about ethical hacking pathways in Malaysia.</p>
        <span class="card-link">Learn more →</span>
      </a>"""

    html = page_shell(
        slug=slug,
        meta_title=meta_title,
        meta_desc=meta_desc,
        hero_title_html="How to Become an Ethical Hacker<br><em>in Malaysia Training</em>",
        hero_crumb="Ethical Hacker Malaysia",
        hero_meta="October 2026 · Nexperts Cybersecurity Practice",
        body_html="\n        ".join(parts),
        toc_items=toc,
        cards_html=cards,
    )
    out = ROOT / "blog" / f"{slug}.html"
    out.write_text(html, encoding="utf-8", newline="\n")
    print("Wrote", out.relative_to(ROOT))


def wire_site() -> None:
    # site_nav.py blog links
    nav_path = ROOT / "scripts" / "site_nav.py"
    nav = nav_path.read_text(encoding="utf-8")
    marker = (
        '            (\n'
        '                "Azure Certification Path 2026",\n'
        '                "/blog/microsoft-azure-certification-guide",\n'
        "            ),\n"
    )
    addition = (
        marker
        + '            (\n'
        '                "Cyber Security Courses for CS Students",\n'
        '                "/blog/cybersecurity-courses-malaysia-students",\n'
        "            ),\n"
        + '            (\n'
        '                "Become an Ethical Hacker in Malaysia",\n'
        '                "/blog/how-to-become-ethical-hacker-malaysia",\n'
        "            ),\n"
    )
    if "/blog/cybersecurity-courses-malaysia-students" not in nav:
        if marker not in nav:
            raise SystemExit("site_nav marker not found")
        nav_path.write_text(nav.replace(marker, addition), encoding="utf-8")
        print("Updated site_nav.py")
    else:
        print("site_nav.py already wired")

    inject_path = ROOT / "scripts" / "inject_addons_nav.py"
    inj = inject_path.read_text(encoding="utf-8")
    inj_marker = '    "blog/microsoft-azure-certification-guide.html",\n'
    inj_add = (
        inj_marker
        + '    "blog/cybersecurity-courses-malaysia-students.html",\n'
        + '    "blog/how-to-become-ethical-hacker-malaysia.html",\n'
    )
    if "cybersecurity-courses-malaysia-students.html" not in inj:
        if inj_marker not in inj:
            raise SystemExit("inject marker not found")
        inject_path.write_text(inj.replace(inj_marker, inj_add), encoding="utf-8")
        print("Updated inject_addons_nav.py")
    else:
        print("inject_addons_nav.py already wired")

    # blog hub cards
    blog_hub = ROOT / "blog.html"
    hub = blog_hub.read_text(encoding="utf-8")
    card_marker = '      <a class="card" href="/blog/ccna-certification-guide">'
    new_cards = (
        '      <a class="card" href="/blog/cybersecurity-courses-malaysia-students">\n'
        "        <h3>Cyber Security Courses for CS Students</h3>\n"
        "        <p>Compare Malaysian degree and short-course options, labs, and certification paths.</p>\n"
        '        <span class="card-link">Learn more →</span>\n'
        "      </a>\n"
        '      <a class="card" href="/blog/how-to-become-ethical-hacker-malaysia">\n'
        "        <h3>Become an Ethical Hacker in Malaysia</h3>\n"
        "        <p>Staged skills, safe labs, training formats, certifications and career roles.</p>\n"
        '        <span class="card-link">Learn more →</span>\n'
        "      </a>\n"
        + card_marker
    )
    if "/blog/cybersecurity-courses-malaysia-students" not in hub.split('<div class="card-grid">')[-1]:
        if card_marker not in hub:
            raise SystemExit("blog hub card marker not found")
        blog_hub.write_text(hub.replace(card_marker, new_cards, 1), encoding="utf-8")
        print("Updated blog.html cards")
    else:
        print("blog.html cards already present")

    # Pretty URL 200 rewrites (safe even if host auto-resolves .html)
    redirects = ROOT / "_redirects"
    rtxt = redirects.read_text(encoding="utf-8")
    rules = [
        "/blog/cybersecurity-courses-malaysia-students /blog/cybersecurity-courses-malaysia-students.html 200",
        "/blog/how-to-become-ethical-hacker-malaysia /blog/how-to-become-ethical-hacker-malaysia.html 200",
        "/blog/cybersecurity-courses-malaysia-students.html /blog/cybersecurity-courses-malaysia-students 301",
        "/blog/how-to-become-ethical-hacker-malaysia.html /blog/how-to-become-ethical-hacker-malaysia 301",
    ]
    added = False
    for rule in rules:
        if rule.split()[0] not in rtxt:
            # insert before legacy post section if present
            needle = "# Legacy Wix URLs"
            if needle in rtxt:
                rtxt = rtxt.replace(needle, rule + "\n" + needle, 1)
            else:
                rtxt = rtxt.rstrip() + "\n" + rule + "\n"
            added = True
    if added:
        redirects.write_text(rtxt, encoding="utf-8", newline="\n")
        print("Updated _redirects")
    else:
        print("_redirects already has blog rules")


def main() -> None:
    build_cybersecurity_courses()
    build_ethical_hacker()
    wire_site()


if __name__ == "__main__":
    main()
