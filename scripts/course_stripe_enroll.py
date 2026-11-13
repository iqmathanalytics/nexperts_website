"""Stripe Register & Pay sidebar fragment for allowlisted course pages.

Keep in sync with functions/api/stripe-courses.mjs and js/course-stripe-enroll.js.
"""
from __future__ import annotations

import html
import re

# Server allowlist — amounts in MYR (display); Stripe charges MYR sen server-side.
STRIPE_COURSES: dict[str, dict] = {
    "agentic-ai": {
        "name": "Agentic AI Engineering",
        "amount_rm": 799,
        "intakes": [
            {
                "id": "2026-11-16",
                "label": "16 Nov 2026 – 2 Jan 2027 (Mon · Wed · Fri · 6pm–10pm)",
            },
        ],
        "modes": ["Live Online", "Classroom"],
    },
    "claude-ai-productivity-90-minutes": {
        "name": "Claude AI Masterclass",
        "amount_rm": 599,
        "intakes": [
            {
                "id": "2026-11-28",
                "label": "28–29 Nov 2026 · 2 days · 9am–5pm",
            },
        ],
        "modes": ["Live Online", "Classroom"],
    },
}


def is_stripe_course(slug: str) -> bool:
    return str(slug or "").strip() in STRIPE_COURSES


def render_stripe_enroll(*, course_slug: str) -> str:
    cfg = STRIPE_COURSES.get(str(course_slug or "").strip())
    if not cfg:
        return ""
    slug = html.escape(course_slug, quote=True)
    amount = int(cfg["amount_rm"])
    mode_opts = "\n".join(
        f'          <option value="{html.escape(m, quote=True)}">{html.escape(m)}</option>'
        for m in cfg["modes"]
    )
    intake_opts = "\n".join(
        f'          <option value="{html.escape(i["id"], quote=True)}">{html.escape(i["label"])}</option>'
        for i in cfg["intakes"]
    )
    return f"""<div class="course-stripe-enroll" data-nx-course-slug="{slug}">
    <p class="cse-heading">Register &amp; Pay</p>
    <form class="course-enroll-form" novalidate>
      <div class="cef-row">
        <div class="cef-field">
          <label>First name <span class="cef-req">*</span></label>
          <input type="text" name="first" placeholder="Ahmad" required autocomplete="given-name">
        </div>
        <div class="cef-field">
          <label>Last name <span class="cef-req">*</span></label>
          <input type="text" name="last" placeholder="Raza" required autocomplete="family-name">
        </div>
      </div>
      <div class="cef-field">
        <label>Email <span class="cef-req">*</span></label>
        <input type="email" name="email" placeholder="ahmad@company.com.my" required autocomplete="email">
      </div>
      <div class="cef-field">
        <label>Phone / WhatsApp <span class="cef-req">*</span></label>
        <div class="enquiry-phone-row">
          <select name="phoneCountry" class="enquiry-phone-cc enquiry-phone-cc--dial-only" aria-label="Country calling code"></select>
          <input type="tel" name="phone" class="enquiry-phone-num" placeholder="12-345 6789" required autocomplete="tel-national" inputmode="tel">
        </div>
      </div>
      <div class="cef-field">
        <label>Training mode <span class="cef-req">*</span></label>
        <select name="trainingMode" required>
{mode_opts}
        </select>
      </div>
      <div class="cef-field">
        <label>Intake <span class="cef-req">*</span></label>
        <select name="intakeId" required>
{intake_opts}
        </select>
      </div>
      <p class="cse-note">Secure payment via Stripe. Checkout is charged in MYR; the price above is shown in your local currency. You will receive a confirmation email with your PDF receipt after payment.</p>
      <p class="course-enroll-err" role="alert" hidden></p>
      <button type="submit" class="cse-submit">Pay RM {amount} <span aria-hidden="true">→</span></button>
    </form>
    <button type="button" class="cse-toggle-enquire">Enquire instead</button>
  </div>
"""


def ensure_stripe_assets(html: str) -> str:
    """Ensure Stripe enroll CSS/JS tags exist on the page."""
    if "course-stripe-enroll.css" not in html:
        if re.search(r'course-sidebar-enquiry\.css', html):
            html = re.sub(
                r'(<link rel="stylesheet" href="/css/course-sidebar-enquiry\.css">)',
                r'\1\n<link rel="stylesheet" href="/css/course-stripe-enroll.css">',
                html,
                count=1,
            )
        else:
            html = html.replace(
                "</head>",
                '<link rel="stylesheet" href="/css/course-stripe-enroll.css">\n</head>',
                1,
            )
    if "course-stripe-enroll.js" not in html:
        if "course-sidebar-enquiry.js" in html:
            html = html.replace(
                '<script src="/js/course-sidebar-enquiry.js" defer></script>',
                '<script src="/js/course-sidebar-enquiry.js" defer></script>\n'
                '<script src="/js/course-stripe-enroll.js" defer></script>',
                1,
            )
        else:
            html = html.replace(
                "</body>",
                '<script src="/js/course-stripe-enroll.js" defer></script>\n</body>',
                1,
            )
    return html
