"""Convert a Google Sheets Enquiries export into a Zoho CRM Leads import CSV.

Free edition: 1,000 rows per import batch and 5,000 records in the whole org.
Deduplicate by email (keep the latest submittedAt). Default cap is 4,000 rows
so live website upserts still have headroom.

Usage:
  python scripts/zoho_sheet_to_leads_csv.py path/to/Enquiries.csv
  python scripts/zoho_sheet_to_leads_csv.py Enquiries.csv --since 2025-01-01 --limit 4000
  python scripts/zoho_sheet_to_leads_csv.py Enquiries.csv -o zoho-leads-import.csv

Then in Zoho: Leads → Import → upload the output CSV (UTF-8).
Map columns using the header names in the output file.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import date, datetime
from pathlib import Path

SHEET_HEADERS = {
    "submitted": ("submitted at (iso)", "submitted at", "submittedat"),
    "source": ("source",),
    "page": ("page url", "pageurl", "page"),
    "first": ("first", "first name", "firstname"),
    "last": ("last", "last name", "lastname"),
    "email": ("email",),
    "phone": ("phone", "phone / whatsapp"),
    "office": ("office", "preferred office"),
    "course": ("course",),
    "type": ("type", "enquiry type"),
    "message": ("message",),
    "ua": ("user agent", "useragent"),
}

SOURCE_MAP = {
    "contact_page": "Website - Contact",
    "landing_modal": "Website - Homepage",
    "course_sidebar": "Website - Course",
}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


def build_index(fieldnames: list[str]) -> dict[str, str]:
    by_norm = {norm(h): h for h in fieldnames if h}
    found: dict[str, str] = {}
    for key, aliases in SHEET_HEADERS.items():
        for alias in aliases:
            if alias in by_norm:
                found[key] = by_norm[alias]
                break
    return found


def map_lead_source(source: str) -> str:
    s = str(source or "").strip()
    return SOURCE_MAP.get(s, "Google Sheet Import")


def map_industry(typ: str) -> str:
    t = str(typ or "").strip()
    if not t:
        return ""
    if re.search(r"corporate", t, re.I):
        return "Corporate / group training"
    if re.search(r"hrd", t, re.I):
        return "HRD Corp"
    if re.search(r"schedule|intake", t, re.I):
        return "Schedule / intake"
    if re.search(r"pricing|payment", t, re.I):
        return "Pricing"
    if re.search(r"eligib", t, re.I):
        return "Eligibility"
    if re.fullmatch(r"other", t, re.I):
        return "Other"
    if re.search(r"individual", t, re.I):
        return "Individual enrolment"
    return t[:120]


def parse_when(raw: str) -> datetime | None:
    s = str(raw or "").strip()
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s[:19], fmt)
        except ValueError:
            continue
    return None


def get(row: dict, idx: dict[str, str], key: str) -> str:
    h = idx.get(key)
    if not h:
        return ""
    return str(row.get(h) or "").strip()


def description(row: dict, idx: dict[str, str]) -> str:
    lines = [
        "Imported from Google Sheet Enquiries",
        f"Course: {get(row, idx, 'course') or '—'}",
        f"Enquiry type: {get(row, idx, 'type') or '—'}",
        f"Preferred office: {get(row, idx, 'office') or '—'}",
        f"Source: {get(row, idx, 'source') or '—'}",
        f"Page: {get(row, idx, 'page') or '—'}",
        f"Submitted: {get(row, idx, 'submitted') or '—'}",
        "",
        "Message:",
        get(row, idx, "message") or "—",
    ]
    return "\n".join(lines)[:30000]


def to_lead(row: dict, idx: dict[str, str]) -> dict[str, str] | None:
    email = get(row, idx, "email")
    last = get(row, idx, "last") or "Unknown"
    first = get(row, idx, "first")
    if not email or "@" not in email:
        return None
    phone = get(row, idx, "phone")
    page = get(row, idx, "page")
    return {
        "First Name": first[:40],
        "Last Name": last[:80],
        "Email": email,
        "Phone": phone,
        "Mobile": phone,
        "Company": get(row, idx, "office")[:200],
        "Website": page[:255],
        "Lead Source": map_lead_source(get(row, idx, "source")),
        "Industry": map_industry(get(row, idx, "type")),
        "Lead Status": "Not Contacted",
        "Description": description(row, idx),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input_csv", type=Path, help="CSV exported from the Enquiries Google Sheet")
    p.add_argument("-o", "--output", type=Path, default=None, help="Output CSV path")
    p.add_argument("--since", default="", help="Keep rows on/after this date (YYYY-MM-DD)")
    p.add_argument("--limit", type=int, default=4000, help="Max unique emails to write (default 4000)")
    args = p.parse_args()

    src: Path = args.input_csv
    if not src.is_file():
        print(f"File not found: {src}", file=sys.stderr)
        return 1

    since_d: date | None = None
    if args.since.strip():
        since_d = date.fromisoformat(args.since.strip())

    with src.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("CSV has no header row.", file=sys.stderr)
            return 1
        idx = build_index(list(reader.fieldnames))
        if "email" not in idx:
            print("Could not find an Email column. Headers:", reader.fieldnames, file=sys.stderr)
            return 1
        rows = list(reader)

    dated: list[tuple[datetime, dict]] = []
    skipped = 0
    for row in rows:
        when = parse_when(get(row, idx, "submitted")) or datetime.min
        if since_d and when.date() < since_d:
            skipped += 1
            continue
        dated.append((when, row))

    dated.sort(key=lambda x: x[0], reverse=True)

    by_email: dict[str, dict] = {}
    for when, row in dated:
        email = get(row, idx, "email").lower()
        if not email or email in by_email:
            continue
        lead = to_lead(row, idx)
        if not lead:
            continue
        by_email[email] = lead
        if len(by_email) >= max(1, args.limit):
            break

    out_path = args.output or src.with_name(src.stem + "-zoho-leads.csv")
    fieldnames = [
        "First Name",
        "Last Name",
        "Email",
        "Phone",
        "Mobile",
        "Company",
        "Website",
        "Lead Source",
        "Industry",
        "Lead Status",
        "Description",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(by_email.values())

    print(f"Read {len(rows)} sheet rows; skipped {skipped} before --since.")
    print(f"Wrote {len(by_email)} unique emails to {out_path}")
    if len(by_email) > 1000:
        print(
            "Zoho Free import is 1,000 rows per batch. Split this file before uploading.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
