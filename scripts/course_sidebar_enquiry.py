"""Inline enquiry form for course page price box (sidebar)."""
from __future__ import annotations

import html
import re
from urllib.parse import parse_qs, unquote, urlparse

ENROLL_BTN_RE = re.compile(
    r'<a\s+href="(?P<href>[^"]*)"\s+class="enroll-btn"\s*>Enroll Now →</a>\s*',
    re.IGNORECASE,
)


def parse_enroll_href(href: str) -> tuple[str, str]:
    """Return (course_slug, course_title) from legacy Enroll Now link."""
    slug = ""
    title = ""
    try:
        parsed = urlparse(href)
        qs = parse_qs(parsed.query or "")
        slug = (qs.get("course") or [""])[0].strip()
        title = unquote((qs.get("title") or [""])[0]).strip()
    except Exception:
        pass
    if not title and slug:
        title = slug.replace("-", " ").title()
    return slug, title


def render_sidebar_enquiry_form(*, course_title: str, course_slug: str = "") -> str:
    """HTML fragment replacing the Enroll Now button inside .enroll-card."""
    title_esc = html.escape(course_title or course_slug or "Course enquiry", quote=True)
    slug_attr = html.escape(course_slug or "", quote=True)
    return f"""  <div class="course-sidebar-enquiry" id="courseEnquiry" data-nx-course-slug="{slug_attr}">
    <p class="cef-heading">Enquire about this course</p>
    <form class="course-enquiry-form" novalidate>
      <input type="hidden" name="course" value="{title_esc}">
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
        <label>Phone / WhatsApp</label>
        <div class="enquiry-phone-row">
          <select name="phoneCountry" class="enquiry-phone-cc enquiry-phone-cc--dial-only" aria-label="Country calling code"></select>
          <input type="tel" name="phone" class="enquiry-phone-num" placeholder="12-345 6789" autocomplete="tel-national" inputmode="tel">
        </div>
      </div>
      <div class="cef-field">
        <label>Preferred office</label>
        <select name="office">
          <option>Malaysia — Petaling Jaya (HQ)</option>
          <option>United States — Albany, NY</option>
          <option>Online / Virtual</option>
        </select>
      </div>
      <div class="cef-field">
        <label>Enquiry type</label>
        <select name="type">
          <option>Individual enrolment</option>
          <option>Corporate / group training (5+ people)</option>
          <option>HRD Corp claim assistance</option>
          <option>Schedule / intake dates</option>
          <option>Pricing &amp; payment options</option>
          <option>Course eligibility question</option>
          <option>Other</option>
        </select>
      </div>
      <div class="cef-field">
        <label>Message</label>
        <textarea name="message" placeholder="Background, preferred dates, team size, or questions…" rows="3"></textarea>
      </div>
      <p class="cef-note">We reply within 4 business hours. Your data is not shared with third parties.</p>
      <p class="course-enquiry-err" role="alert" hidden></p>
      <button type="submit" class="cef-submit">Send Enquiry <span class="cef-arr" aria-hidden="true">→</span></button>
    </form>
    <div class="course-enquiry-success" hidden>
      <div class="cef-check" aria-hidden="true">✓</div>
      <p class="cef-success-title">Enquiry received</p>
      <p class="cef-success-text">We will reply to your email within 4 business hours.</p>
    </div>
  </div>
"""
