"""Generate Phase-1 course detail pages from the CEH template.

Reads course_pages/ceh-v13-ai.html as the structural template, then for each
course in COURSES below applies surgical text substitutions to produce a
unique HTML page under course_pages/<slug>.html.
"""
from pathlib import Path
import re
from urllib.parse import quote

ROOT = Path(__file__).parent
TEMPLATE_PATH = ROOT / "course_pages" / "ceh-v13-ai.html"
TEMPLATE = TEMPLATE_PATH.read_text(encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────────────
# RENDERERS
# ──────────────────────────────────────────────────────────────────────────────

def render_badges(badges):
    return "\n          ".join(f'<span class="cbadge {cls}">{txt}</span>' for cls, txt in badges)


def render_meta(meta):
    return "\n          ".join(
        f'<div class="hmeta"><span class="hmeta-icon">{icon}</span><span>{label}: <strong{f" style=\"color:{color}\"" if color else ""}>{val}</strong></span></div>'
        for icon, label, val, color in meta
    )


def render_quick_wins(qw):
    out = []
    for i, (icon, h, p) in enumerate(qw):
        d = f" d{i}" if i > 0 else ""
        out.append(
            f'    <div class="qw reveal{d}">\n      <span class="qw-icon">{icon}</span>\n      <div><h4>{h}</h4><p>{p}</p></div>\n    </div>'
        )
    return "\n".join(out)


def render_who_grid(who):
    return "\n    ".join(
        f'<div class="who-card">\n      <span class="who-icon">{icon}</span>\n      <div><h4>{h}</h4><p>{p}</p></div>\n    </div>'
        for icon, h, p in who
    )


def render_prereqs(items, note):
    rows = "\n    ".join(
        f'<div style="display:flex;align-items:center;gap:10px;font-size:.83rem;color:var(--ink2)"><span style="color:var(--green);font-weight:700">✓</span> {x}</div>'
        for x in items
    )
    return f'{rows}\n    <div style="display:flex;align-items:center;gap:10px;font-size:.83rem;color:var(--ink4);font-style:italic"><span>→</span> {note}</div>'


def render_modules(modules):
    out = []
    for i, (num, title, topics) in enumerate(modules):
        open_cls = " open" if i == 0 else ""
        topic_html = "\n        ".join(f'<div class="topic">{t}</div>' for t in topics)
        out.append(
            f'  <button class="module{open_cls}" onclick="toggleModule(this)">\n'
            f'    <div class="module-header">\n'
            f'      <span class="module-num">{num}</span>\n'
            f'      <h4>{title}</h4>\n'
            f'      <span class="module-count">{len(topics)} topics</span>\n'
            f'      <span class="module-arrow">›</span>\n'
            f'    </div>\n'
            f'    <div class="module-body">\n'
            f'      <div class="module-topics">\n'
            f'        {topic_html}\n'
            f'      </div>\n'
            f'    </div>\n'
            f'  </button>'
        )
    return "\n".join(out)


def render_labs(labs):
    out = []
    for i, (num, title, desc, tag_cls, tag_label) in enumerate(labs):
        d = f" d{i % 3}" if i % 3 else ""
        if i % 3 == 0:
            d = ""
        out.append(
            f'      <div class="lab-card reveal{d}">\n'
            f'        <div class="lab-num">{num}</div>\n'
            f'        <h4>{title}</h4>\n'
            f'        <p>{desc}</p>\n'
            f'        <span class="lab-tag {tag_cls}">{tag_label}</span>\n'
            f'      </div>'
        )
    return "\n".join(out)


def render_exam_card(card):
    rows = "\n        ".join(f'<div class="exam-row"><span>{k}</span><strong>{v}</strong></div>' for k, v in card["rows"])
    return (
        f'      <div class="exam-card">\n'
        f'        <h4>{card["name"]}</h4>\n'
        f'        {rows}\n'
        f'      </div>'
    )


def render_mock_program(items):
    out = []
    for num, head, body in items:
        out.append(
            f'    <div style="background:#fff;padding:18px 16px">\n'
            f'      <div style="font-family:\'Fraunces\',serif;font-size:1.6rem;font-weight:300;color:var(--blue);opacity:.4;margin-bottom:8px">{num}</div>\n'
            f'      <h4 style="font-size:.83rem;font-weight:600;color:var(--ink);margin-bottom:5px">{head}</h4>\n'
            f'      <p style="font-size:.75rem;color:var(--ink3);line-height:1.6">{body}</p>\n'
            f'    </div>'
        )
    return "\n".join(out)


def render_pass_compare(items):
    cards = []
    for i, (head, body) in enumerate(items):
        bg = "var(--bg2)" if i == 0 else "var(--marP)"
        bd = "var(--line)" if i == 0 else "var(--marL)"
        head_color = "var(--ink)" if i == 0 else "var(--marM)"
        body_color = "var(--ink3)" if i == 0 else "var(--marM)"
        body_extra = "" if i == 0 else ";opacity:.8"
        cards.append(
            f'        <div style="padding:20px;background:{bg};border-radius:10px;border:1px solid {bd}">\n'
            f'          <h4 style="font-size:.85rem;font-weight:600;color:{head_color};margin-bottom:8px">{head}</h4>\n'
            f'          <p style="font-size:.78rem;color:{body_color}{body_extra};line-height:1.65">{body}</p>\n'
            f'        </div>'
        )
    return "\n".join(cards)


def render_pass_pills(pills):
    classes = ["pp-b", "pp-m", "pp-g"]
    return "\n          ".join(f'<span class="ppill {classes[i % 3]}">{p}</span>' for i, p in enumerate(pills))


def render_next_cards(cards):
    klasses = ["nc-prev", "nc-this", "nc-next"]
    out = []
    for i, (label, name, sub, link) in enumerate(cards):
        link_color = ' style="color:var(--blue)"' if i == 1 else ""
        out.append(
            f'      <div class="next-card {klasses[i]}">\n'
            f'        <div class="nc-label">{label}</div>\n'
            f'        <div class="nc-name">{name}</div>\n'
            f'        <p class="nc-sub">{sub}</p>\n'
            f'        <a href="#" class="nc-link"{link_color}>{link}</a>\n'
            f'      </div>'
        )
    return "\n".join(out)


def render_path_chips(chips):
    out = []
    for i, (text, kind) in enumerate(chips):
        if kind == "you":
            chip = f'<span style="font-size:.75rem;font-weight:700;color:#93c5fd;padding:5px 12px;border:1px solid rgba(29,78,216,.35);border-radius:6px;background:rgba(29,78,216,.14)">{text} ← You</span>'
        elif kind == "next":
            chip = f'<span style="font-size:.75rem;font-weight:600;color:#bfdbfe;padding:5px 12px;border:1px solid rgba(30,64,175,.4);border-radius:6px;background:rgba(30,64,175,.15)">{text}</span>'
        else:
            chip = f'<span style="font-size:.75rem;font-weight:600;color:rgba(255,255,255,.4);padding:5px 12px;border:1px solid rgba(255,255,255,.12);border-radius:6px">{text}</span>'
        out.append(chip)
        if i < len(chips) - 1:
            out.append('<span style="color:rgba(255,255,255,.2);font-size:.9rem">→</span>')
    return "\n        ".join(out)


def render_review_summary(summary):
    rating, p5, p4, p3, count = summary
    return (
        f'    <div style="text-align:center;flex-shrink:0">\n'
        f'      <div style="font-family:\'Fraunces\',serif;font-size:3rem;font-weight:300;color:var(--ink);letter-spacing:-.03em;line-height:1">{rating}</div>\n'
        f'      <div style="display:flex;gap:2px;justify-content:center;margin:4px 0">\n'
        f'        <span style="color:var(--amber)">★★★★★</span>\n'
        f'      </div>\n'
        f'      <div style="font-size:.7rem;color:var(--ink4)">{count} reviews</div>\n'
        f'    </div>\n'
        f'    <div style="flex:1;display:flex;flex-direction:column;gap:6px">\n'
        f'      <div style="display:flex;align-items:center;gap:10px"><span style="font-size:.72rem;color:var(--ink3);min-width:16px">5★</span><div style="flex:1;height:6px;background:var(--line);border-radius:3px;overflow:hidden"><div style="width:{p5}%;height:100%;background:var(--amber);border-radius:3px"></div></div><span style="font-size:.72rem;color:var(--ink4)">{p5}%</span></div>\n'
        f'      <div style="display:flex;align-items:center;gap:10px"><span style="font-size:.72rem;color:var(--ink3);min-width:16px">4★</span><div style="flex:1;height:6px;background:var(--line);border-radius:3px;overflow:hidden"><div style="width:{p4}%;height:100%;background:var(--amber);opacity:.6;border-radius:3px"></div></div><span style="font-size:.72rem;color:var(--ink4)">{p4}%</span></div>\n'
        f'      <div style="display:flex;align-items:center;gap:10px"><span style="font-size:.72rem;color:var(--ink3);min-width:16px">3★</span><div style="flex:1;height:6px;background:var(--line);border-radius:3px;overflow:hidden"><div style="width:{p3}%;height:100%;background:var(--amber);opacity:.4;border-radius:3px"></div></div><span style="font-size:.72rem;color:var(--ink4)">{p3}%</span></div>\n'
        f'    </div>'
    )


def render_reviews(reviews):
    out = []
    for stars, text, rav, initials, name, role, score in reviews:
        star_html = "".join(f'<span class="star">★</span>' for _ in range(len(stars)))
        out.append(
            f'      <div class="review-card">\n'
            f'        <div class="review-stars">{star_html}</div>\n'
            f'        <p class="review-text">"{text}"</p>\n'
            f'        <div class="review-author">\n'
            f'          <div class="rav {rav}">{initials}</div>\n'
            f'          <div>\n'
            f'            <div class="rname">{name}</div>\n'
            f'            <div class="rrole">{role}</div>\n'
            f'            <div class="review-pass">{score}</div>\n'
            f'          </div>\n'
            f'        </div>\n'
            f'      </div>'
        )
    return "\n".join(out)


def render_sidebar_meta(rows):
    return "\n    ".join(f'<div class="smeta-row"><span>{k}</span><strong>{v}</strong></div>' for k, v in rows)


def render_includes(items):
    return "\n  ".join(f'<div class="include-item">{x}</div>' for x in items)


def render_verify(items):
    return "\n  ".join(f'<div class="verify-row"><span class="verify-dot"></span>{x}</div>' for x in items)


def contact_link_query(c, intent=None):
    """Query string for contact.html pre-fill (?course=slug&title=…&intent=corporate)."""
    slug = c["slug"]
    title = c["title"]
    q = f"course={quote(str(slug), safe='')}&title={quote(str(title), safe='')}"
    if intent == "corporate":
        q += "&intent=corporate"
    return q


def contact_href(c, intent=None):
    return f"../contact.html?{contact_link_query(c, intent)}#enquire"


# ──────────────────────────────────────────────────────────────────────────────
# PAGE BUILDER
# ──────────────────────────────────────────────────────────────────────────────

def build_page(c):
    """Take a course dict and return the final HTML."""
    html = TEMPLATE

    # ── <title> + meta
    html = re.sub(r'<title>.*?</title>', f'<title>{c["title"]} — {c["vendor_short"]} | Nexperts Academy</title>', html, count=1)

    # ── Hero ::after watermark (smart-quoted)
    html = html.replace("content:\u2018CEH\u2019", f"content:\u2018{c['watermark']}\u2019", 1)

    # ── Crumb (vendor + leaf)
    crumb_block = (
        f'          <a href="../index.html">Home</a><span>/</span>\n'
        f'          <a href="../index.html#courses">Courses</a><span>/</span>\n'
        f'          <a href="#">{c["crumb_vendor"]}</a><span>/</span>\n'
        f'          <span style="color:rgba(255,255,255,.6)">{c["title"]}</span>'
    )
    html = re.sub(
        r'          <a href="\.\./index\.html">Home</a><span>/</span>.*?<span style="color:rgba\(255,255,255,\.6\)">CEH v13 AI</span>',
        crumb_block, html, count=1, flags=re.DOTALL,
    )

    # ── Course badges
    badges_html = render_badges(c["badges"])
    html = re.sub(
        r'<div class="course-badges">.*?</div>\n        <h1 class="course-title">',
        f'<div class="course-badges">\n          {badges_html}\n        </div>\n        <h1 class="course-title">',
        html, count=1, flags=re.DOTALL,
    )

    # ── Course title
    html = re.sub(
        r'<h1 class="course-title">.*?</h1>',
        f'<h1 class="course-title">{c["title_html"]}</h1>',
        html, count=1, flags=re.DOTALL,
    )

    # ── Subtitle
    html = re.sub(
        r'<p class="course-subtitle">.*?</p>',
        f'<p class="course-subtitle">{c["subtitle"]}</p>',
        html, count=1, flags=re.DOTALL,
    )

    # ── Hero meta
    meta_html = render_meta(c["hero_meta"])
    html = re.sub(
        r'<div class="hero-meta">.*?</div>\n      </div>\n      <div class="course-hero-shot reveal">',
        f'<div class="hero-meta">\n          {meta_html}\n        </div>\n      </div>\n      <div class="course-hero-shot reveal">',
        html, count=1, flags=re.DOTALL,
    )

    # ── Hero image
    html = re.sub(
        r'<img src="\.\./image/happy-student-girl-holding-notebook\.jpg"[^>]*>',
        f'<img src="{c["hero_img"]}" alt="{c["title"]} training session at Nexperts Academy" width="400" height="300" loading="lazy">',
        html, count=1,
    )

    # ── Quick wins (4 entries)
    qw_html = render_quick_wins(c["quick_wins"])
    html = re.sub(
        r'  <div class="quick-wins">\n.*?\n  </div>\n\n  <!-- TABS -->',
        f'  <div class="quick-wins">\n{qw_html}\n  </div>\n\n  <!-- TABS -->',
        html, count=1, flags=re.DOTALL,
    )

    # ── Overview section (everything between <!-- OVERVIEW --> and <!-- CURRICULUM -->)
    overview_html = build_overview(c)
    html = re.sub(
        r'  <!-- OVERVIEW -->\n\n  <div id="sec-overview" class="content-sec">.*?\n  </div>\n\n  <!-- CURRICULUM -->',
        f'  <!-- OVERVIEW -->\n\n  <div id="sec-overview" class="content-sec">\n{overview_html}\n  </div>\n\n  <!-- CURRICULUM -->',
        html, count=1, flags=re.DOTALL,
    )

    # ── Curriculum
    curr_html = build_curriculum(c)
    html = re.sub(
        r'  <!-- CURRICULUM -->\n\n  <div id="sec-curriculum" class="content-sec" style="display:none">.*?\n  </div>\n\n  <!-- LABS -->',
        f'  <!-- CURRICULUM -->\n\n  <div id="sec-curriculum" class="content-sec" style="display:none">\n{curr_html}\n  </div>\n\n  <!-- LABS -->',
        html, count=1, flags=re.DOTALL,
    )

    # ── Labs
    labs_html = build_labs(c)
    html = re.sub(
        r'  <!-- LABS -->\n\n  <div id="sec-labs" class="content-sec" style="display:none">.*?\n  </div>\n\n  <!-- EXAM INFO -->',
        f'  <!-- LABS -->\n\n  <div id="sec-labs" class="content-sec" style="display:none">\n{labs_html}\n  </div>\n\n  <!-- EXAM INFO -->',
        html, count=1, flags=re.DOTALL,
    )

    # ── Exam info
    exam_html = build_exam(c)
    html = re.sub(
        r'  <!-- EXAM INFO -->\n\n  <div id="sec-exam" class="content-sec" style="display:none">.*?\n  </div>\n\n  <!-- PASS RATE -->',
        f'  <!-- EXAM INFO -->\n\n  <div id="sec-exam" class="content-sec" style="display:none">\n{exam_html}\n  </div>\n\n  <!-- PASS RATE -->',
        html, count=1, flags=re.DOTALL,
    )

    # ── Pass rate band
    pass_html = build_pass(c)
    html = re.sub(
        r'  <!-- PASS RATE -->\n\n  <div id="sec-passrate" class="content-sec" style="display:none;padding:0">.*?\n  </div>\n\n  <!-- ROADMAP / NEXT STEPS -->',
        f'  <!-- PASS RATE -->\n\n  <div id="sec-passrate" class="content-sec" style="display:none;padding:0">\n{pass_html}\n  </div>\n\n  <!-- ROADMAP / NEXT STEPS -->',
        html, count=1, flags=re.DOTALL,
    )

    # ── Roadmap / next steps
    next_html = build_next(c)
    html = re.sub(
        r'  <!-- ROADMAP / NEXT STEPS -->\n\n  <div id="sec-roadmap" class="content-sec" style="display:none">.*?\n  </div>\n\n  <!-- REVIEWS -->',
        f'  <!-- ROADMAP / NEXT STEPS -->\n\n  <div id="sec-roadmap" class="content-sec" style="display:none">\n{next_html}\n  </div>\n\n  <!-- REVIEWS -->',
        html, count=1, flags=re.DOTALL,
    )

    # ── Reviews
    reviews_html = build_reviews(c)
    html = re.sub(
        r'  <!-- REVIEWS -->\n\n  <div id="sec-reviews" class="content-sec" style="display:none">.*?\n  </div>\n\n</div><!-- /main -->',
        f'  <!-- REVIEWS -->\n\n  <div id="sec-reviews" class="content-sec" style="display:none">\n{reviews_html}\n  </div>\n\n</div><!-- /main -->',
        html, count=1, flags=re.DOTALL,
    )

    # ── Sidebar
    sidebar_html = build_sidebar(c)
    html = re.sub(
        r'<aside class="sidebar">\n  <div class="sidebar-inner">\n\n.*?  </div>\n</aside>',
        f'<aside class="sidebar">\n  <div class="sidebar-inner">\n\n{sidebar_html}\n  </div>\n</aside>',
        html, count=1, flags=re.DOTALL,
    )

    # Nav "Enquire Now" → contact form with this course pre-selected (template may ship any prior contact href)
    html = re.sub(
        r'(<a )href="\.\./contact\.html[^"]*"( class="nav-enroll">Enquire Now</a>)',
        rf'\1href="{contact_href(c)}"\2',
        html,
        count=1,
    )

    return html


def build_overview(c):
    h_lead, h_em = c["overview_head"]
    pull = c.get("overview_quote")
    pull_html = (
        f'    <div class="pull-text">{pull}</div>\n'
        if pull
        else ""
    )
    return (
        f'    <div class="eyebrow">{c["overview_eyebrow"]}</div>\n'
        f'    <h2 class="sec-head">{h_lead}<br><em>{h_em}</em></h2>\n'
        f'    <p class="body-text">{c["overview_p1"]}</p>\n'
        f'    <p class="body-text">{c["overview_p2"]}</p>\n'
        f'{pull_html}'
        f'    <p class="body-text">{c["overview_p3"]}</p>\n\n'
        f'<div style="margin-top:36px">\n'
        f'  <div class="eyebrow m">Who should take this course</div>\n'
        f'  <div class="who-grid">\n'
        f'    {render_who_grid(c["who_for"])}\n'
        f'  </div>\n'
        f'</div>\n\n'
        f'<div style="margin-top:36px">\n'
        f'  <div class="eyebrow g">Prerequisites</div>\n'
        f'  <div style="display:flex;flex-direction:column;gap:8px;margin-top:16px">\n'
        f'    {render_prereqs(c["prereqs"], c["prereqs_note"])}\n'
        f'  </div>\n'
        f'</div>'
    )


def build_curriculum(c):
    h_lead, h_em = c["curriculum_head"]
    return (
        f'    <div class="eyebrow">{c["curriculum_eyebrow"]}</div>\n'
        f'    <h2 class="sec-head">{h_lead} <em>{h_em}</em></h2>\n'
        f'    <p class="body-text">{c["curriculum_intro"]}</p>\n\n'
        f'<div class="modules">\n'
        f'{render_modules(c["modules"])}\n'
        f'</div>'
    )


def build_labs(c):
    h_lead, h_em = c["labs_head"]
    return (
        f'    <div class="eyebrow">{c["labs_eyebrow"]}</div>\n'
        f'    <h2 class="sec-head">{h_lead} <em class="m">{h_em}</em></h2>\n'
        f'    <p class="body-text">{c["labs_intro"]}</p>\n'
        f'    <div class="labs-grid">\n'
        f'{render_labs(c["labs"])}\n'
        f'    </div>\n'
        f'    <p style="font-size:.78rem;color:var(--ink3);margin-top:20px;font-style:italic">{c["labs_footer"]}</p>'
    )


def build_exam(c):
    h_lead, h_em = c["exam_head"]
    main = render_exam_card(c["exam_main"])
    extra = render_exam_card(c["exam_optional"]) if c.get("exam_optional") else ""
    grid = (
        f'    <div class="exam-grid">\n{main}'
        + (f'\n{extra}' if extra else "")
        + '\n    </div>'
    )
    mock_html = ""
    if c.get("mock_programme"):
        mock_html = (
            '\n\n<div style="margin-top:32px;padding:24px;background:var(--bg2);border:1px solid var(--line);border-radius:10px">\n'
            f'  <div class="eyebrow g" style="margin-bottom:16px">{c.get("mock_title", "Our 3-Mock Exam Programme")}</div>\n'
            '  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:var(--line);border:1px solid var(--line);border-radius:8px;overflow:hidden">\n'
            f'{render_mock_program(c["mock_programme"])}\n'
            '  </div>\n'
            '</div>'
        )
    return (
        f'    <div class="eyebrow">{c["exam_eyebrow"]}</div>\n'
        f'    <h2 class="sec-head">{h_lead}<br><em>{h_em}</em></h2>\n'
        f'    <p class="body-text">{c["exam_intro"]}</p>\n'
        f'{grid}{mock_html}'
    )


def build_pass(c):
    pills = render_pass_pills(c["pass_pills"])
    cmp_html = render_pass_compare(c["pass_compare"])
    return (
        f'    <div class="pass-band" id="passRingEl">\n'
        f'      <div class="pass-ring-wrap">\n'
        f'        <div class="pring" id="pring" data-target="{c["pass_rate"]}">\n'
        f'          <svg viewBox="0 0 120 120">\n'
        f'            <circle class="ring-bg" cx="60" cy="60" r="52"/>\n'
        f'            <circle class="ring-fill" cx="60" cy="60" r="52"/>\n'
        f'          </svg>\n'
        f'          <div class="pct-center">\n'
        f'            <div class="pct-n" id="pctNum">0<em>%</em></div>\n'
        f'            <div class="pct-l">Pass Rate</div>\n'
        f'          </div>\n'
        f'        </div>\n'
        f'      </div>\n'
        f'      <div class="pass-right">\n'
        f'        <h3>{c["pass_head_html"]}</h3>\n'
        f'        <p>{c["pass_intro"]}</p>\n'
        f'        <div class="pass-pills">\n          {pills}\n        </div>\n'
        f'      </div>\n'
        f'    </div>\n'
        f'    <div class="content-sec" style="border-top:1px solid var(--line)">\n'
        f'      <div class="eyebrow m">Why our pass rate is {c["pass_rate"]}%</div>\n'
        f'      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px">\n'
        f'{cmp_html}\n'
        f'      </div>\n'
        f'    </div>'
    )


def build_next(c):
    h_lead, h_em = c["next_head"]
    cards = render_next_cards(c["next_steps"])
    chips = render_path_chips(c["path_chips"])
    return (
        f'    <div class="eyebrow">{c["next_eyebrow"]}</div>\n'
        f'    <h2 class="sec-head">{h_lead}<br><em>{h_em}</em></h2>\n'
        f'    <p class="body-text">{c["next_steps_intro"]}</p>\n'
        f'    <div class="next-grid">\n'
        f'{cards}\n'
        f'    </div>\n\n'
        f'<div style="margin-top:32px;padding:24px;background:var(--ink);border-radius:12px;position:relative;overflow:hidden">\n'
        f'  <div style="position:absolute;right:-16px;top:50%;transform:translateY(-50%);font-family:\'Fraunces\',serif;font-size:8rem;font-weight:300;color:rgba(255,255,255,.03);pointer-events:none">Path</div>\n'
        f'  <div style="position:relative;z-index:1">\n'
        f'    <div class="eyebrow" style="color:rgba(255,255,255,.3)"><span style="width:14px;height:2px;background:rgba(255,255,255,.2);border-radius:2px;display:block"></span>Full {c["path_name"]} career path</div>\n'
        f'    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-top:16px">\n'
        f'      <div style="display:flex;align-items:center;gap:8px">\n'
        f'        {chips}\n'
        f'      </div>\n'
        f'    </div>\n'
        f'    <p style="font-size:.75rem;color:rgba(255,255,255,.3);margin-top:14px">{c["salary_html"]}</p>\n'
        f'  </div>\n'
        f'</div>'
    )


def build_reviews(c):
    h_lead, h_em = c["reviews_head"]
    summary = render_review_summary(c["reviews_summary"])
    rows = render_reviews(c["reviews"])
    return (
        f'    <div class="eyebrow">{c["reviews_eyebrow"]}</div>\n'
        f'    <h2 class="sec-head">{h_lead}<br><em>{h_em}</em></h2>\n'
        f'    <div style="display:flex;align-items:center;gap:24px;margin-top:4px;margin-bottom:32px;padding:20px;background:var(--bg2);border:1px solid var(--line);border-radius:10px">\n'
        f'{summary}\n'
        f'    </div>\n'
        f'    <div class="reviews-grid">\n'
        f'{rows}\n'
        f'    </div>'
    )


def build_sidebar(c):
    meta = render_sidebar_meta(c["sidebar_meta"])
    inc = render_includes(c["whats_included"])
    ver = render_verify(c["verify_items"])
    href_enroll = contact_href(c)
    href_corp = contact_href(c, intent="corporate")
    return (
        f'<div class="enroll-card" id="enroll">\n'
        f'  <div class="price-row">\n'
        f'    <span class="price">{c["price"]}</span>\n'
        f'    <span class="price-orig">{c["price_orig"]}</span>\n'
        f'    <span class="price-save">{c["price_save"]}</span>\n'
        f'  </div>\n'
        f'  <p class="price-note">{c["price_note"]}</p>\n'
        f'  <a href="{href_enroll}" class="enroll-btn">Enroll Now →</a>\n'
        f'  <a href="{href_corp}" class="corp-btn">Corporate / Group Pricing</a>\n'
        f'  <div class="guarantee">\n'
        f'    <span class="guarantee-icon">🛡️</span>\n'
        f'    <div>\n'
        f'      <h5>{c["pass_rate"]}% Pass Guarantee</h5>\n'
        f'      <p>{c["guarantee_text"]}</p>\n'
        f'    </div>\n'
        f'  </div>\n'
        f'  <div class="sidebar-meta">\n'
        f'    {meta}\n'
        f'  </div>\n'
        f'</div>\n\n'
        f'<div class="sidebar-includes">\n'
        f'  <h4>What\'s included</h4>\n'
        f'  {inc}\n'
        f'</div>\n\n'
        f'<div class="verify-strip">\n'
        f'  <h4>Cert Verification</h4>\n'
        f'  {ver}\n'
        f'</div>\n\n'
        f'<div class="share-strip">\n'
        f'  <button type="button" class="share-btn nx-share-copy" aria-haspopup="dialog">📤 Share</button>\n'
        f'  <button type="button" class="share-btn nx-share-copy" aria-haspopup="dialog">💾 Save</button>\n'
        f'  <a href="{href_enroll}" class="share-btn">✉️ Enquire</a>\n'
        f'</div>'
    )


# ──────────────────────────────────────────────────────────────────────────────
# COURSES (data only — see _course_data.py)
# ──────────────────────────────────────────────────────────────────────────────
from _course_data import COURSES  # noqa: E402


# ──────────────────────────────────────────────────────────────────────────────
# DRIVER
# ──────────────────────────────────────────────────────────────────────────────

def main():
    out_dir = ROOT / "course_pages"
    for c in COURSES:
        slug = c["slug"]
        page = build_page(c)
        (out_dir / f"{slug}.html").write_text(page, encoding="utf-8")
        print(f"  wrote {slug}.html")
    print(f"Generated {len(COURSES)} detail pages")


if __name__ == "__main__":
    main()
