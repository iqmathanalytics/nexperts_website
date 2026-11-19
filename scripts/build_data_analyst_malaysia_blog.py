# -*- coding: utf-8 -*-
"""Generate How to Become a Data Analyst in Malaysia blog and wire sitewide."""
from __future__ import annotations

import html as html_lib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from site_nav import NAV_ASSET_TAGS, render_site_nav, render_whatsapp_float  # noqa: E402

SITE = "https://www.nexpertsacademy.com"
SLUG = "how-to-become-a-data-analyst-in-malaysia"
IMG = f"/image/blog/{SLUG}"
OG_IMAGE = f"{SITE}{IMG}/image1.jpg"

# Course links
C_SQL = "/courses/sql-for-data-professionals"
C_PY = "/courses/python-for-data-analytics"
C_PL300 = "/courses/pl-300"
C_TAB_SPEC = "/courses/tableau-desktop-specialist"
C_TAB_VIS = "/courses/advanced-data-visualization-tableau"
C_DS = "/courses/data-science-foundation"
C_EXCEL = "/courses/excel-basic"


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


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def p(text: str) -> str:
    return f"<p>{text}</p>"


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
  <p style="margin-top:2rem"><a href="/contact-us#enquire" style="color:var(--blue);font-weight:700">Enquire about data analytics training →</a></p>
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
    meta_title = "How to Become a Data Analyst in Malaysia: Skills & Career Path"
    meta_desc = (
        "Learn how to become a data analyst in Malaysia. Explore essential skills, SQL, Python, "
        "Power BI, certifications, courses and career opportunities."
    )
    toc = [
        ("what-does-a-data-analyst-do", "What Does a Data Analyst Do?"),
        ("skills", "Skills You Need"),
        ("tools-first", "Which Tools to Learn First"),
        ("roadmap", "Step-by-Step Roadmap"),
        ("portfolio", "Portfolio Projects"),
        ("certifications", "Certifications"),
        ("career", "Career Opportunities"),
        ("timeline", "How Long Does It Take?"),
        ("courses", "Training Courses at Nexperts"),
        ("faq", "Frequently Asked Questions"),
        ("conclusion", "Conclusion"),
    ]

    parts: list[str] = []
    parts.append(
        p(
            "Becoming a data analyst is an attractive career direction for graduates, working professionals "
            "and individuals looking to transition into the technology industry. Businesses across industries "
            "generate large amounts of data, but they need professionals who can organise, analyse and interpret "
            "that information to support better decisions."
        )
    )
    parts.append(
        p(
            "In Malaysia, data analytics skills are relevant across industries such as banking, finance, retail, "
            "telecommunications, manufacturing, healthcare and logistics. Professionals with the ability to work "
            "with spreadsheets, SQL, Python and business intelligence tools can support organisations in "
            "understanding business performance and identifying opportunities for improvement."
        )
    )
    parts.append(
        p(
            "However, becoming a data analyst involves more than learning software or creating dashboards. "
            "You need to understand business requirements, work with different data sources, identify patterns, "
            "interpret results and communicate findings to stakeholders."
        )
    )
    parts.append(
        p(
            "Whether you are a fresh graduate, an Excel user or an experienced professional exploring a career "
            "change, this guide explains how to become a data analyst in Malaysia, including the essential "
            "skills, tools, certifications, learning roadmap and career opportunities."
        )
    )
    parts.append(
        figure(
            f"{IMG}/image1.jpg",
            "How to become a data analyst in Malaysia — skills, tools and career pathway",
        )
    )

    parts.append('<h2 id="what-does-a-data-analyst-do">What Does a Data Analyst Do?</h2>')
    parts.append(
        p(
            "A data analyst collects, cleans, processes and analyses information to help businesses make informed decisions."
        )
    )
    parts.append(
        p(
            "Organisations use data from multiple sources, including customer transactions, website activity, "
            "sales records, financial systems, operational reports and customer feedback."
        )
    )
    parts.append(
        p(
            "A data analyst examines this information to identify patterns, measure performance and provide "
            "insights that help organisations solve business problems."
        )
    )
    parts.append(
        p(
            "For example, consider a retail company operating multiple stores across Malaysia. Management wants "
            "to understand why sales have decreased in certain locations."
        )
    )
    parts.append("<p>A data analyst may:</p>")
    parts.append(
        ul(
            [
                "Collect sales information from different stores.",
                "Use SQL to retrieve and combine transaction records.",
                "Clean incomplete or inconsistent data.",
                "Analyse sales performance by product, location and time period.",
                "Create a Power BI dashboard to display important performance indicators.",
                "Identify factors contributing to declining sales.",
                "Present findings and recommendations to management.",
            ]
        )
    )
    parts.append(
        p("The objective is not simply to produce reports. It is to transform raw information into useful business insights.")
    )
    parts.append("<h3>Key Responsibilities of a Data Analyst</h3>")
    parts.append("<p>Although responsibilities vary between organisations, common tasks include:</p>")
    parts.append(
        "<ol>"
        "<li><strong>Data collection</strong> — Gather information from databases, spreadsheets, business applications, APIs and other available sources.</li>"
        "<li><strong>Data cleaning</strong> — Identify missing values, remove duplicate records, correct inconsistencies and prepare information for analysis.</li>"
        "<li><strong>Data analysis</strong> — Use statistical techniques, SQL queries and analytical tools to identify trends, relationships and performance patterns.</li>"
        "<li><strong>Data visualisation</strong> — Create dashboards, charts and reports that help stakeholders understand important business metrics.</li>"
        "<li><strong>Reporting and communication</strong> — Explain findings, present recommendations and communicate analytical results to technical and non-technical stakeholders.</li>"
        "<li><strong>Business performance monitoring</strong> — Track KPIs, compare performance across periods and identify opportunities for operational improvement.</li>"
        "</ol>"
    )

    parts.append('<h2 id="skills">What Skills Do You Need to Become a Data Analyst in Malaysia?</h2>')
    parts.append(
        p(
            "A successful data analyst needs a combination of technical, analytical and communication skills. "
            "You do not need to master every programming language before starting, but you should develop a "
            "strong foundation in working with data."
        )
    )
    parts.append("<p>Here are the essential skills to focus on.</p>")

    parts.append("<h3>1. Microsoft Excel and Spreadsheet Skills</h3>")
    parts.append(p("Excel is one of the most useful starting points for individuals learning data analytics."))
    parts.append(
        p(
            "Many organisations use spreadsheets for financial reporting, sales tracking, operational analysis "
            "and business planning."
        )
    )
    parts.append(
        p(
            "Before moving into advanced analytical tools, develop the ability to work with datasets and perform "
            f'basic analysis using Excel. Explore <a href="{C_EXCEL}">Excel training at Nexperts Academy</a>.'
        )
    )
    parts.append("<p>Important Excel skills include:</p>")
    parts.append(
        ul(
            [
                "Sorting and filtering datasets.",
                "Using formulas and functions.",
                "VLOOKUP, XLOOKUP and INDEX-MATCH.",
                "Pivot tables and pivot charts.",
                "Conditional formatting.",
                "Data validation.",
                "Removing duplicates and handling missing information.",
                "Creating basic reports and dashboards.",
            ]
        )
    )
    parts.append(
        p(
            "For example, a sales analyst may use Excel to calculate monthly revenue, compare product performance "
            "and identify changes in regional sales."
        )
    )

    parts.append("<h3>2. SQL for Data Analysis</h3>")
    parts.append(p("SQL (Structured Query Language) is an essential skill for working with relational databases."))
    parts.append(
        p(
            "Businesses store information in databases containing customer details, orders, transactions, "
            "product records and operational information."
        )
    )
    parts.append(p("Data analysts use SQL to retrieve, combine, filter and summarise this information."))
    parts.append("<p>Important SQL concepts include:</p>")
    parts.append(
        ul(
            [
                "SELECT and FROM statements.",
                "WHERE conditions.",
                "ORDER BY and GROUP BY.",
                "Aggregate functions such as SUM, COUNT and AVG.",
                "INNER JOIN, LEFT JOIN and other joins.",
                "Subqueries and Common Table Expressions.",
                "Window functions.",
                "Data filtering and aggregation.",
            ]
        )
    )
    parts.append(
        p(
            "For example, an analyst working for an ecommerce business may use SQL to identify the top-performing "
            "products, calculate monthly revenue and compare repeat customers with first-time buyers."
        )
    )
    parts.append(
        p(
            f'Recommended learning: <a href="{C_SQL}">SQL for Data Analytics at Nexperts Academy</a>.'
        )
    )

    parts.append("<h3>3. Python for Data Analytics</h3>")
    parts.append(
        p("Python is a widely used programming language for data analysis, automation and data science.")
    )
    parts.append(
        p(
            "It helps analysts work with larger datasets, automate repetitive tasks and perform more advanced analysis."
        )
    )
    parts.append(
        p(
            "You do not need to become a software developer to start learning Python for data analytics. Begin with "
            "basic programming concepts and gradually develop your analytical capabilities."
        )
    )
    parts.append("<p>Important Python topics include:</p>")
    parts.append(
        ul(
            [
                "Variables and data types.",
                "Lists, dictionaries and loops.",
                "Functions and conditional statements.",
                "Reading CSV and Excel files.",
                "Working with Pandas and NumPy.",
                "Data cleaning and transformation.",
                "Exploratory data analysis.",
                "Data visualisation using Matplotlib and Seaborn.",
            ]
        )
    )
    parts.append(
        p(
            "For example, a data analyst may use Python to combine several monthly sales files, remove duplicate "
            "transactions, calculate revenue and generate charts for further analysis."
        )
    )
    parts.append(
        p(
            f'Recommended learning: <a href="{C_PY}">Python for Data Analytics Training in Malaysia</a>.'
        )
    )

    parts.append(
        figure(
            f"{IMG}/image2.jpg",
            "Data analyst skills workspace covering Excel, SQL, Python and dashboard tools",
        )
    )

    parts.append("<h3>4. Power BI and Data Visualisation</h3>")
    parts.append(
        p(
            "Data analysis is not complete when you discover a pattern. You also need to communicate that information clearly."
        )
    )
    parts.append(
        p(
            "Power BI is a business intelligence platform used to transform data into interactive reports and dashboards."
        )
    )
    parts.append(
        p(
            "It helps analysts connect to data sources, prepare datasets, build data models, create calculations "
            "and share insights with business stakeholders."
        )
    )
    parts.append("<p>Important Power BI skills include:</p>")
    parts.append(
        ul(
            [
                "Connecting to Excel, SQL and other data sources.",
                "Data cleaning using Power Query.",
                "Creating relationships between tables.",
                "Data modelling.",
                "Writing DAX measures.",
                "Developing interactive dashboards.",
                "Using filters and slicers.",
                "Publishing and managing reports.",
                "Implementing row-level security.",
            ]
        )
    )
    parts.append(
        p(
            "Microsoft's PL-300 certification focuses on preparing data, modelling data, visualising and analysing "
            "data, and managing and securing Power BI. It also expects proficiency in Power Query and DAX."
        )
    )
    parts.append(
        p(
            f'Recommended learning: <a href="{C_PL300}">Microsoft Power BI PL-300 Certification Training in Malaysia</a>.'
        )
    )

    parts.append("<h3>5. Tableau for Data Analytics</h3>")
    parts.append(
        p("Tableau is another widely used business intelligence and data visualisation platform.")
    )
    parts.append(
        p(
            "It enables analysts to explore datasets, create interactive visualisations and communicate business "
            "insights through dashboards."
        )
    )
    parts.append("<p>Important Tableau skills include:</p>")
    parts.append(
        ul(
            [
                "Connecting to Excel, CSV and database sources.",
                "Understanding dimensions and measures.",
                "Creating charts and visualisations.",
                "Working with filters and parameters.",
                "Creating calculated fields.",
                "Building interactive dashboards.",
                "Using joins and data relationships.",
                "Publishing and sharing dashboards.",
            ]
        )
    )
    parts.append(
        p(
            "Power BI and Tableau serve similar business intelligence purposes, but organisations may prefer one "
            "platform based on their existing technology environment."
        )
    )
    parts.append("<p>Recommended learning options:</p>")
    parts.append(
        ul(
            [
                f'<a href="{C_TAB_SPEC}">Tableau Desktop Specialist Training</a>',
                f'<a href="{C_TAB_VIS}">Data Analytics and Visualisation with Tableau</a>',
            ]
        )
    )

    parts.append("<h3>6. Statistics and Analytical Thinking</h3>")
    parts.append(
        p(
            "Technical tools help you process information, but statistical knowledge helps you interpret it correctly."
        )
    )
    parts.append(
        p(
            "Data analysts should understand how to interpret numerical information, identify patterns and "
            "distinguish meaningful changes from random variation."
        )
    )
    parts.append("<p>Important statistical concepts include:</p>")
    parts.append(
        ul(
            [
                "Mean, median and mode.",
                "Percentages and percentage changes.",
                "Variance and standard deviation.",
                "Probability.",
                "Correlation.",
                "Distribution.",
                "Sampling.",
                "Hypothesis testing.",
                "Descriptive statistics.",
            ]
        )
    )
    parts.append(
        p(
            "Understanding statistics helps analysts avoid presenting misleading conclusions — for example, "
            "investigating whether a 15% sales increase came from demand, promotions, seasonality or pricing."
        )
    )

    parts.append("<h3>7. Communication and Data Storytelling</h3>")
    parts.append(
        p("A data analyst must explain findings in a way that stakeholders can understand and act upon.")
    )
    parts.append("<p>Develop the ability to:</p>")
    parts.append(
        ul(
            [
                "Understand business questions.",
                "Explain analytical findings clearly.",
                "Present important KPIs.",
                "Highlight trends and anomalies.",
                "Support recommendations with evidence.",
                "Communicate with technical and non-technical teams.",
            ]
        )
    )
    parts.append(
        p(
            "A useful analytical report should explain what happened, why it may have happened, what impact it has "
            "and what action the organisation should consider."
        )
    )

    parts.append('<h2 id="tools-first">Which Tools Should You Learn First as a Beginner?</h2>')
    parts.append(
        p(
            "There are several tools available for data analytics, but beginners should avoid trying to learn everything simultaneously."
        )
    )
    parts.append(p("Start with the tools that help you complete a practical end-to-end analytical task."))
    parts.append(p("A practical starting sequence is:"))
    parts.append("<p><strong>Excel → SQL → Power BI → Python → Advanced Analytics</strong></p>")
    parts.append(
        table_html(
            ["Tool", "Primary purpose", "Learning priority"],
            [
                ["Microsoft Excel", "Data organisation and basic analysis", "High"],
                ["SQL", "Database querying and data retrieval", "High"],
                ["Power BI", "Dashboards and business reporting", "High"],
                ["Python", "Data processing and automation", "Medium"],
                ["Tableau", "Data visualisation and dashboards", "Medium"],
                ["Statistics", "Interpreting analytical results", "High"],
            ],
        )
    )
    parts.append(
        p(
            "Tableau can be learned alongside or after Power BI, depending on the tools used by your target employers. "
            "You do not need to master both Power BI and Tableau before applying for entry-level roles."
        )
    )

    parts.append('<h2 id="roadmap">Step-by-Step Roadmap: How to Become a Data Analyst in Malaysia</h2>')
    parts.append(
        p(
            "If you are starting without previous data analytics experience, follow a structured learning roadmap "
            "rather than jumping between different courses."
        )
    )
    steps = [
        (
            "Step 1: Understand Data Analytics Fundamentals",
            "Start by understanding what data analytics means and how organisations use information to make decisions.",
            [
                "Types of data.",
                "Structured and unstructured data.",
                "Data sources.",
                "Data collection.",
                "Data cleaning.",
                "Data transformation.",
                "Exploratory data analysis.",
                "Key performance indicators.",
            ],
        ),
        (
            "Step 2: Develop Excel Skills",
            "Learn spreadsheet fundamentals and practise working with small datasets such as sales records, "
            "employee information, customer transactions or operational data. Practise calculating totals, "
            "percentages, averages and performance comparisons.",
            [],
        ),
        (
            "Step 3: Learn SQL",
            "Once you are comfortable working with spreadsheets, learn SQL to retrieve and analyse information "
            "from relational databases. Practise writing queries, combining tables and calculating business metrics.",
            [],
        ),
        (
            "Step 4: Learn a Business Intelligence Tool",
            "Choose Power BI or Tableau as your primary visualisation platform. Start with connecting to datasets, "
            "cleaning data and creating basic charts, then develop data modelling, DAX calculations, interactive "
            "filters and dashboard design.",
            [],
        ),
        (
            "Step 5: Develop Python Skills",
            "After developing basic database and reporting skills, introduce Python. Start with Pandas for data "
            "manipulation and NumPy for numerical operations.",
            [
                "Loading datasets.",
                "Handling missing values.",
                "Removing duplicates.",
                "Combining multiple files.",
                "Calculating metrics.",
                "Exploring trends.",
                "Creating visualisations.",
            ],
        ),
        (
            "Step 6: Understand Statistics and Business Analysis",
            "Develop your ability to investigate business questions and interpret analytical results. Learn how to "
            "identify changes, compare performance, interpret relationships and explain business implications.",
            [],
        ),
        (
            "Step 7: Build a Data Analytics Portfolio",
            "Create projects using publicly available datasets or appropriately anonymised sample data. Your "
            "portfolio should demonstrate the entire analytical process, including the business problem, data "
            "preparation, analysis, visualisation and recommendations.",
            [],
        ),
        (
            "Step 8: Prepare for Data Analyst Job Applications",
            "Highlight SQL and database skills, Excel analysis, Power BI or Tableau dashboards, Python data "
            "processing, statistical knowledge, practical portfolio projects, and communication abilities. Tailor "
            "your resume to each job advertisement.",
            [],
        ),
    ]
    for title, body, bullets in steps:
        parts.append(f"<h3>{esc(title)}</h3>")
        parts.append(p(body))
        if bullets:
            parts.append("<p>Learn about / practise:</p>")
            parts.append(ul(bullets))

    parts.append(
        figure(
            f"{IMG}/image3.jpg",
            "Data analyst career growth pathway from foundational skills to senior insights roles",
        )
    )

    parts.append('<h2 id="portfolio">Data Analytics Portfolio Projects You Should Build</h2>')
    parts.append(
        p("Practical projects help demonstrate that you can use analytical tools to solve business problems.")
    )
    projects = [
        (
            "1. Sales Performance Analysis Dashboard",
            "A retail business wants to understand its sales performance across different stores and product categories.",
            "Excel, SQL and Power BI.",
            [
                "Analyse sales transactions.",
                "Calculate total revenue.",
                "Identify top-performing products.",
                "Compare monthly performance.",
                "Analyse regional sales.",
                "Create an interactive dashboard.",
            ],
            "A sales performance dashboard with revenue trends, product performance and regional comparisons.",
        ),
        (
            "2. Customer Segmentation Analysis",
            "An ecommerce company wants to understand customer purchasing behaviour.",
            "Python, Pandas and Power BI.",
            [
                "Clean customer transaction records.",
                "Identify repeat customers.",
                "Calculate purchasing frequency.",
                "Analyse average order value.",
                "Segment customers based on purchasing behaviour.",
                "Visualise customer groups.",
            ],
            "A customer analysis report showing purchasing patterns and customer segments.",
        ),
        (
            "3. Financial Performance Analysis",
            "A finance department wants to monitor monthly expenses and budget performance.",
            "Excel, SQL and Power BI.",
            [
                "Organise financial transaction data.",
                "Compare actual spending with budget.",
                "Calculate monthly variances.",
                "Identify categories with higher expenses.",
                "Build financial reporting dashboards.",
            ],
            "A financial performance dashboard with expense trends, budget comparisons and variance analysis.",
        ),
        (
            "4. Website Traffic Analysis",
            "A marketing team wants to understand website performance and identify opportunities to improve conversions.",
            "Python, SQL and Power BI.",
            [
                "Analyse website sessions.",
                "Compare traffic sources.",
                "Examine landing-page performance.",
                "Monitor conversion rates.",
                "Identify traffic trends.",
                "Present recommendations.",
            ],
            "A marketing analytics dashboard with traffic, engagement and conversion metrics.",
        ),
        (
            "5. Operational Performance Analysis",
            "A logistics company wants to understand delivery performance and identify delays.",
            "SQL, Excel and Tableau.",
            [
                "Analyse delivery records.",
                "Calculate average delivery time.",
                "Compare regional performance.",
                "Identify delayed deliveries.",
                "Examine operational trends.",
                "Build a performance dashboard.",
            ],
            "An operational dashboard showing delivery performance, delays and regional comparisons.",
        ),
    ]
    for title, problem, tools, tasks, output in projects:
        parts.append(f"<h3>{esc(title)}</h3>")
        parts.append(p(f"<strong>Business problem:</strong> {esc(problem)}"))
        parts.append(p(f"<strong>Tools:</strong> {esc(tools)}"))
        parts.append("<p><strong>Tasks:</strong></p>")
        parts.append(ul(tasks))
        parts.append(p(f"<strong>Expected output:</strong> {esc(output)}"))
    parts.append(
        p(
            "For every portfolio project, document the business problem, dataset, tools used, analytical approach, "
            "key findings and recommendations. Avoid uploading confidential employer or customer information."
        )
    )

    parts.append('<h2 id="certifications">What Certifications Should You Consider for a Data Analyst Career?</h2>')
    parts.append(
        p(
            "Certifications can help you develop structured knowledge and demonstrate proficiency in specific tools. "
            "However, a certification alone does not guarantee employment. Employers may also assess practical skills, "
            "project experience, communication and problem-solving ability."
        )
    )
    parts.append("<h3>1. Microsoft Power BI Data Analyst Associate (PL-300)</h3>")
    parts.append(
        p(
            f'The Microsoft <a href="{C_PL300}">PL-300 certification</a> focuses on data preparation, modelling, '
            "visualisation, analysis and Power BI administration. Key areas include Power Query, data modelling, "
            "DAX, dashboards and data security."
        )
    )
    parts.append("<h3>2. Tableau Desktop Specialist</h3>")
    parts.append(
        p(
            f'The <a href="{C_TAB_SPEC}">Tableau Desktop Specialist</a> credential is an entry-level certification '
            "focused on fundamental Tableau knowledge — connecting to datasets, exploring information, creating "
            "visualisations and building dashboards."
        )
    )
    parts.append("<h3>3. Practical Data Analytics Training</h3>")
    parts.append(
        p(
            "Apart from vendor certifications, practical training can help learners build the technical skills needed "
            "to perform data analysis. Consider learning SQL, Python, Excel and business intelligence tools through "
            "guided exercises and portfolio projects."
        )
    )

    parts.append('<h2 id="career">Data Analyst Career Opportunities in Malaysia</h2>')
    parts.append(
        p(
            "Data analytics skills can be applied across several industries in Malaysia. Organisations use data to "
            "monitor operations, understand customer behaviour, improve financial performance and support business planning."
        )
    )
    parts.append(
        table_html(
            ["Industry", "Example data analyst responsibilities"],
            [
                ["Banking and finance", "Financial reporting, transaction analysis and customer segmentation"],
                ["Retail and ecommerce", "Sales analysis, product performance and customer behaviour"],
                ["Telecommunications", "Customer analytics, usage trends and churn analysis"],
                ["Manufacturing", "Production reporting, quality analysis and operational performance"],
                ["Healthcare", "Service utilisation, operational reporting and resource analysis"],
                ["Logistics", "Delivery performance, shipment analysis and operational efficiency"],
                ["Marketing", "Campaign reporting, customer acquisition and conversion analysis"],
            ],
        )
    )
    parts.append("<h3>Common Data Analyst Job Titles</h3>")
    parts.append("<p>Depending on your experience and technical skills, you may encounter job titles such as:</p>")
    parts.append(
        ul(
            [
                "Junior Data Analyst",
                "Data Analyst",
                "Business Intelligence Analyst",
                "Reporting Analyst",
                "Business Analyst",
                "Sales Analyst",
                "Marketing Analyst",
                "Financial Analyst",
                "Operations Analyst",
            ]
        )
    )
    parts.append(
        p(
            "These roles can have different requirements even when their job titles appear similar. Read the job "
            "description carefully before selecting your learning pathway."
        )
    )

    parts.append('<h2 id="timeline">How Long Does It Take to Become a Data Analyst?</h2>')
    parts.append(
        p(
            "The time required to develop data analytics skills depends on your starting knowledge, learning schedule "
            "and practical experience."
        )
    )
    parts.append(
        p(
            "Here is an illustrative six-month learning roadmap. This is a suggested learning sequence, not a "
            "guaranteed job-readiness timeline. Consistency and practical application are more important than "
            "simply completing courses quickly."
        )
    )
    parts.append(
        table_html(
            ["Month", "Learning focus", "Practical outcome"],
            [
                ["Month 1", "Excel and analytics fundamentals", "Spreadsheet analysis"],
                ["Month 2", "SQL and database querying", "SQL analysis project"],
                ["Month 3", "Power BI and dashboard development", "Interactive dashboard"],
                ["Month 4", "Python and data processing", "Data cleaning project"],
                ["Month 5", "Statistics and advanced analysis", "Analytical report"],
                ["Month 6", "Portfolio and interview preparation", "Completed portfolio"],
            ],
        )
    )

    parts.append('<h2 id="courses">Data Analyst Training Courses in Malaysia at Nexperts Academy</h2>')
    parts.append(
        p(
            "For individuals looking to develop data analytics skills, Nexperts Academy offers training programmes "
            "covering different areas of the analytical workflow."
        )
    )
    courses = [
        (
            "1. SQL for Data Analytics",
            "SQL training helps learners retrieve, combine, clean and summarise data from relational databases. "
            "The course includes practical business scenarios involving sales performance, customer activity and "
            "operational reporting.",
            "Beginners and professionals who want to develop database querying and data analysis skills.",
            C_SQL,
            "Explore SQL for Data Analytics Training",
        ),
        (
            "2. Python for Data Analytics",
            "Python training introduces learners to programming techniques used in data processing, analysis and "
            "automation. Practical exercises help participants apply Python to workplace-related analytical tasks.",
            "Excel or SQL users, aspiring data analysts and professionals looking to expand their analytical capabilities.",
            C_PY,
            "Explore Python for Data Analytics Training",
        ),
        (
            "3. Microsoft Power BI PL-300 Certification Training",
            "This programme focuses on Power BI, Power Query, DAX, data modelling, dashboard development and reporting. "
            "It is relevant for learners preparing for the Microsoft Power BI Data Analyst Associate certification.",
            "Aspiring data analysts, business intelligence professionals, finance executives and reporting specialists.",
            C_PL300,
            "Explore Power BI PL-300 Training in Malaysia",
        ),
        (
            "4. Tableau Desktop Specialist Training",
            "This training covers Tableau fundamentals, data connections, visualisation, dashboard development and "
            "sharing insights. It is relevant for professionals preparing for the Tableau Desktop Specialist credential.",
            "Beginners, business analysts, marketing analysts and reporting professionals.",
            C_TAB_SPEC,
            "Explore Tableau Desktop Specialist Training",
        ),
        (
            "5. Data Analytics and Visualisation with Tableau",
            "This practical programme focuses on connecting datasets, preparing information, creating charts and "
            "developing interactive Tableau dashboards. It develops applied visual analytics skills rather than "
            "preparation for an external certification examination.",
            "Aspiring data analysts, business analysts, finance professionals and operations teams.",
            C_TAB_VIS,
            "Explore Data Analytics and Visualisation with Tableau",
        ),
        (
            "6. Data Science Foundation",
            "The Data Science Foundation programme introduces the broader data science lifecycle, including problem "
            "framing, data wrangling, exploratory data analysis, basic modelling and communicating findings.",
            "Analysts, students, developers and professionals exploring data science.",
            C_DS,
            "Explore Data Science Foundation Training",
        ),
    ]
    for title, body, suitable, href, cta in courses:
        parts.append(f"<h3>{esc(title)}</h3>")
        parts.append(p(body))
        parts.append(p(f"<strong>Suitable for:</strong> {esc(suitable)}"))
        parts.append(p(f'<a href="{href}">{esc(cta)} →</a>'))

    parts.append('<h2 id="faq">Frequently Asked Questions About Becoming a Data Analyst in Malaysia</h2>')
    parts.append('<div class="blog-faq">')
    faqs = [
        (
            "How can I become a data analyst in Malaysia?",
            "Start by learning Excel, SQL, statistics and a business intelligence tool such as Power BI or Tableau. "
            "Develop Python skills as you progress, build practical portfolio projects and prepare for relevant job opportunities.",
        ),
        (
            "Is data analytics a good career choice in Malaysia?",
            "Data analytics is relevant across industries such as finance, retail, telecommunications, manufacturing, "
            "healthcare and logistics. Career prospects depend on skills, experience and employer requirements.",
        ),
        (
            "What qualifications do I need to become a data analyst?",
            "Requirements vary by employer. Some positions require a degree in computer science, information technology, "
            "statistics, mathematics, business analytics or a related discipline. Other employers may consider relevant "
            "technical skills, certifications, practical projects and professional experience.",
        ),
        (
            "Can I become a data analyst without coding experience?",
            "Yes. You can begin with Excel, SQL fundamentals and Power BI before moving into Python. However, learning "
            "programming can expand the types of analytical tasks you can perform.",
        ),
        (
            "Is SQL necessary for data analysts?",
            "SQL is an important skill because it allows analysts to retrieve, combine and summarise information stored "
            "in relational databases. Many business analytics workflows involve working with database information.",
        ),
        (
            "Should I learn Python or Power BI first?",
            "If your main objective is business reporting and dashboard development, Power BI is a practical starting "
            "point after learning spreadsheet and SQL fundamentals. Python is useful for more advanced data manipulation, "
            "automation and statistical analysis.",
        ),
        (
            "Which certification is best for data analysts?",
            "The Microsoft Power BI Data Analyst Associate (PL-300) and Tableau Desktop Specialist credentials are "
            "relevant options. The best choice depends on your target role and the technologies used by employers.",
        ),
        (
            "How long does it take to learn data analytics?",
            "The learning period varies according to your previous knowledge, study time and practical experience. "
            "A structured six-month learning plan can provide a foundation, but becoming job-ready requires consistent "
            "practice and portfolio development.",
        ),
        (
            "What is the difference between a data analyst and a data scientist?",
            "A data analyst generally focuses on collecting, preparing, analysing and visualising information to answer "
            "business questions. A data scientist often works with more advanced statistical modelling, machine learning "
            "and predictive techniques. The roles can overlap depending on the organisation.",
        ),
        (
            "Can Excel alone make me a data analyst?",
            "Excel is a useful starting tool, but many data analyst roles require additional skills such as SQL, Power BI, "
            "Python, statistical analysis and data visualisation.",
        ),
    ]
    for q, a in faqs:
        parts.append(
            f'<div class="faq-item"><p class="faq-q"><strong>{esc(q)}</strong></p><p>{esc(a)}</p></div>'
        )
    parts.append("</div>")

    parts.append('<h2 id="conclusion">Conclusion: Start Your Data Analyst Career in Malaysia</h2>')
    parts.append(
        p(
            "Becoming a data analyst requires a combination of technical knowledge, analytical thinking, practical "
            "experience and communication skills."
        )
    )
    parts.append(
        p(
            "Start with Excel and SQL, develop your understanding of statistics, and learn a business intelligence "
            "platform such as Power BI or Tableau. As your skills progress, introduce Python and work on practical "
            "projects that demonstrate your ability to solve business problems."
        )
    )
    parts.append(
        p(
            "Certifications such as Microsoft PL-300 and Tableau Desktop Specialist can support your professional "
            "development, while hands-on projects help demonstrate how you apply those skills."
        )
    )
    parts.append(
        p(
            "For individuals planning to enter the data analytics field, choosing a structured learning pathway is "
            "an important first step."
        )
    )
    parts.append("<p><strong>Explore data analytics training at Nexperts Academy:</strong></p>")
    parts.append(
        "<ul>"
        f'<li><a href="{C_SQL}">SQL for Data Professionals</a></li>'
        f'<li><a href="{C_PY}">Python for Data Analytics</a></li>'
        f'<li><a href="{C_PL300}">Power BI PL-300</a></li>'
        f'<li><a href="{C_TAB_SPEC}">Tableau Desktop Specialist</a></li>'
        f'<li><a href="{C_DS}">Data Science Foundation</a></li>'
        "</ul>"
    )

    cards = f"""      <a class="card" href="{C_PL300}">
        <h3>Power BI PL-300 Training</h3>
        <p>Prepare data, model with DAX and build interactive dashboards for the Microsoft PL-300 exam.</p>
        <span class="card-link">Learn more →</span>
      </a>
      <a class="card" href="{C_PY}">
        <h3>Python for Data Analytics</h3>
        <p>Learn Pandas, data cleaning and visualisation for practical analytics workflows.</p>
        <span class="card-link">Learn more →</span>
      </a>
      <a class="card" href="{C_SQL}">
        <h3>SQL for Data Professionals</h3>
        <p>Query, join and summarise business data from relational databases with confidence.</p>
        <span class="card-link">Learn more →</span>
      </a>"""

    html = page_shell(
        meta_title=meta_title,
        meta_desc=meta_desc,
        hero_title_html="How to Become a Data Analyst in Malaysia:<br><em>Skills, Tools, Certifications and Career Path</em>",
        hero_crumb="Data Analyst Career",
        hero_meta="November 2026 · Data & Analytics Practice",
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
            '                "CAPM vs PMP in Malaysia",\n'
            '                "/blog/capm-vs-pmp-malaysia",\n'
            "            ),\n"
        )
        addition = (
            marker
            + '            (\n'
            '                "Become a Data Analyst in Malaysia",\n'
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
        inj_marker = '    "blog/capm-vs-pmp-malaysia.html",\n'
        if inj_marker not in inj:
            raise SystemExit("inject marker not found")
        inject_path.write_text(inj.replace(inj_marker, inj_marker + inj_entry), encoding="utf-8")
        print("Updated inject_addons_nav.py")
    else:
        print("inject_addons_nav.py already wired")

    blog_hub = ROOT / "blog.html"
    hub = blog_hub.read_text(encoding="utf-8")
    if f"/blog/{SLUG}" not in hub:
        card_marker = '      <a class="card" href="/blog/capm-vs-pmp-malaysia">'
        new_card = (
            f'      <a class="card" href="/blog/{SLUG}">\n'
            "        <h3>Become a Data Analyst in Malaysia</h3>\n"
            "        <p>Skills, tools, certifications, portfolio projects and a practical learning roadmap.</p>\n"
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
        marker = (
            f"  <url><loc>{SITE}/blog/capm-vs-pmp-malaysia</loc>"
            "<changefreq>monthly</changefreq><priority>0.7</priority></url>\n"
        )
        if marker not in sm:
            raise SystemExit("sitemap marker not found")
        sitemap.write_text(sm.replace(marker, marker + entry), encoding="utf-8")
        print("Updated sitemap.xml")
    else:
        print("sitemap.xml already wired")


def main() -> None:
    wire_site()
    build_page()


if __name__ == "__main__":
    main()
