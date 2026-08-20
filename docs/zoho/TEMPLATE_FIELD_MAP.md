# Zoho Free — email template field map

Plan edition: **Zoho CRM Free** (no custom fields).  
Source requirements: [`docs/updates_on_p2.txt`](../updates_on_p2.txt)  
Website → Zoho mapper: [`functions/api/zoho-crm.mjs`](../../functions/api/zoho-crm.mjs)

**Legend**

| Tag | Meaning |
|-----|---------|
| **Dynamic (Free)** | Use Zoho merge field from a standard Lead field the website already fills |
| **Manual** | Salesperson types/replaces at send time; keep `[PLACEHOLDER]` or fill before Send |
| **Deferred** | Needs Standard custom fields and/or Professional Quotes/Invoices — do not invent merge syntax |

Exact merge labels must be inserted via Zoho’s template editor (**Insert → Fields**). Display names below match typical Zoho English UI; if your org uses different labels, use the editor’s inserted token.

---

## Website payload → Zoho Lead (current Free mapping)

| Website form field | Zoho Lead (API) | Zoho merge (typical) | Notes |
|--------------------|-----------------|----------------------|--------|
| `first` | `First_Name` | `${Leads.First Name}` | Dynamic |
| `last` | `Last_Name` | `${Leads.Last Name}` | Dynamic |
| `email` | `Email` | `${Leads.Email}` | Upsert key |
| `phone` | `Phone`, `Mobile` | `${Leads.Phone}` | Dynamic |
| `course` | `Company` | `${Leads.Company}` | **Course name only** (for clean email merges) |
| `message` | (in `Description`) | `${Leads.Description}` | Full text under Message: |
| `office` | (in `Description`) | `${Leads.Description}` | Preferred office line |
| `type` | `Industry` | `${Leads.Industry}` | Mapped enquiry type |
| `source` | `Lead_Source` | `${Leads.Lead Source}` | Website - Contact / Homepage / Course |
| `pageUrl` | `Website` | `${Leads.Website}` | Dynamic |
| (auto) | `Lead_Status` | `${Leads.Lead Status}` | Default Not Contacted |
| (all of above) | `Description` | `${Leads.Description}` | Full labelled enquiry block |

Not collected on website today (Deferred until forms + Standard fields): Number of Participants, Preferred Training Date, HRD Corp Account Number, Training Fee, Payment Link, Quote/Invoice fields, Event fields.

---

## Standard Free merge fields (safe to use)

| Need | Use this merge |
|------|----------------|
| First name | `${Leads.First Name}` |
| Course (short) | `${Leads.Company}` |
| Full enquiry (course, office, message, URL) | `${Leads.Description}` |
| Enquiry / lead-type signal | `${Leads.Industry}` |
| Email | `${Leads.Email}` |
| Phone | `${Leads.Phone}` |
| Lead source | `${Leads.Lead Source}` |
| Lead status | `${Leads.Lead Status}` |
| Page / curriculum URL | `${Leads.Website}` |
| Lead owner | `${Leads.Lead Owner}` (if Insert Fields offers it) |

**Do not** invent tokens such as `${Leads.Interested Course}`, `${Leads.Training Fee}`, `${Leads.Quote Number}` on Free — those fields do not exist.

---

## Template 1 — First follow-up individual

| Doc need | Classification | Free approach |
|----------|----------------|---------------|
| First Name | Dynamic (Free) | `${Leads.First Name}` |
| Course | Dynamic (Free) | `${Leads.Company}` — replace `[COURSE NAME]` |
| Training / interest | Dynamic (Free) | `${Leads.Description}` (or Industry) |
| Salesperson details | Manual | Keep signature / owner name typed or Lead Owner if available |

---

## Template 2 — First follow-up corporate group

| Doc need | Classification | Free approach |
|----------|----------------|---------------|
| First Name | Dynamic (Free) | `${Leads.First Name}` |
| Company (org name) | Manual / partial | Website puts **course** in Company. For true company name, type over or put org name in Description when editing the Lead before send |
| Interested Course | Dynamic (Free) | `${Leads.Company}` or Description |
| Number of Participants | Deferred | Keep `[NUMBER OF PARTICIPANTS]` or manual |
| Preferred Training Date | Deferred / Manual | Manual |
| Training Mode | Manual | Manual (Online / On-site / Hybrid) |
| Training Location | Manual / Description | Prefer Description office line or manual |
| Corporate Requirements | Dynamic (Free) | `${Leads.Description}` (message) |
| HRD Corp Required | Partial Dynamic | `${Leads.Industry}` when value is HRD Corp; else manual |

---

## Template 3 — HRD Corp claim next steps

| Doc need | Classification | Free approach |
|----------|----------------|---------------|
| First Name | Dynamic (Free) | `${Leads.First Name}` |
| Company | Manual / Description | Manual org name; Industry may be HRD Corp |
| Company Registration Number | Deferred | Manual |
| Employee Count | Deferred | Manual |
| HRD Corp Account Number | Deferred | Manual |
| Interested Course | Dynamic (Free) | `${Leads.Company}` |
| Training Fee | Deferred | Keep `[AMOUNT]` — fill before send |
| HRD Corp Application Status | Deferred | Manual |
| HRD email | Static | `hrdcorp@nexpertsacademy.com` (hardcode OK — not lead data) |

Do not claim automatic HRD Corp approval in copy.

---

## Template 4 — Pricing payment options

| Doc need | Classification | Free approach |
|----------|----------------|---------------|
| First Name | Dynamic (Free) | `${Leads.First Name}` |
| Interested Course | Dynamic (Free) | `${Leads.Company}` |
| Training Fee | Deferred | Manual `[AMOUNT]` |
| Training Duration | Deferred | Manual |
| Training Mode | Manual | Manual |
| Intake Date | Deferred | Manual `[DATE]` |
| Certification | Manual | Manual |
| Payment Link | Deferred | Manual — hide CTA if no link |
| HRD Corp Required | Partial | `${Leads.Industry}` |

Do not hard-code course prices into the HTML.

---

## Template 5 — Schedule intake dates

| Doc need | Classification | Free approach |
|----------|----------------|---------------|
| First Name | Dynamic (Free) | `${Leads.First Name}` |
| Course | Dynamic (Free) | `${Leads.Company}` |
| Start / End Date | Deferred | Manual |
| Duration / Mode / Location / Time | Manual | Manual |
| Training Fee | Deferred | Manual |
| Available Intake Dates | Deferred | Manual (no intakes module on Free) |

---

## Template 6 — Quote attached

| Doc need | Classification | Free approach |
|----------|----------------|---------------|
| First Name | Dynamic (Free) | `${Leads.First Name}` |
| Course | Dynamic (Free) | `${Leads.Company}` |
| Quote Number / Date / Total / Valid Until | Deferred | Manual (no Quotes module on Free) |
| Confirmation / Payment Link | Deferred | Manual |
| Quote PDF | Manual | Attach PDF on Send — do not embed quote body in HTML |

---

## Template 7 — Invoice payment reminder

| Doc need | Classification | Free approach |
|----------|----------------|---------------|
| First Name | Dynamic (Free) | `${Leads.First Name}` |
| Course | Dynamic (Free) | `${Leads.Company}` |
| Invoice Number / Date / Amount / Due Date | Deferred | Manual (no Invoices on Free) |
| Payment Link / Method / Reference / Status | Deferred | Manual |
| Paid guard | Process | See [TEMPLATE_SEND_CHECKLIST.md](TEMPLATE_SEND_CHECKLIST.md) — do not send if already paid |

---

## Template 8 — Enrolment confirmation

| Doc need | Classification | Free approach |
|----------|----------------|---------------|
| First Name | Dynamic (Free) | `${Leads.First Name}` |
| Course | Dynamic (Free) | `${Leads.Company}` |
| Start / End / Mode / Location / Joining Link | Deferred / Manual | Manual |
| Enrolment Status | Deferred | Manual — only send when Confirmed |

---

## Template 9 — Lost not now

| Doc need | Classification | Free approach |
|----------|----------------|---------------|
| First Name | Dynamic (Free) | `${Leads.First Name}` |
| Course | Dynamic (Free) | `${Leads.Company}` |
| Lead Status | Dynamic (Free) | `${Leads.Lead Status}` |
| Future Follow-up Date | Deferred | Manual + create Zoho Task for owner |
| Lead Owner | Dynamic (Free) | `${Leads.Lead Owner}` if available |

Do not delete the Lead — set Lost Lead / Not Contacted per Phase 2.

---

## Template 10 — Workshop event invite

| Doc need | Classification | Free approach |
|----------|----------------|---------------|
| First Name | Dynamic (Free) | `${Leads.First Name}` |
| Event Name / Description / Date / Time / Format / Location | Deferred | Manual (no Events CRM module) |
| Registration Link / Deadline | Deferred | Manual |
| Learning Outcomes 1–4 / Target Audience | Deferred | Manual |

Site has static workshop/event HTML pages; they are **not** synced into Zoho on Free.

---

## Placeholder inventory (from updates_on_p2.txt)

| Placeholder | Free classification |
|-------------|---------------------|
| `[COURSE NAME]` | Dynamic → `${Leads.Company}` |
| `[AMOUNT]` / `[TOTAL]` | Manual |
| `[TRAINING DURATION]` | Manual |
| `[DATE]` / `[START DATE]` / `[END DATE]` / `[TIME]` | Manual |
| `[FORMAT]` / `[LOCATION]` | Manual |
| `[PAYMENT LINK]` / `[CONFIRMATION / PAYMENT LINK]` / `[JOINING LINK OR DETAILS]` | Manual |
| `[QUOTE NUMBER]` / `[QUOTE DATE]` / `[VALIDITY DATE]` | Manual |
| `[INVOICE NUMBER]` / `[INVOICE DATE]` / `[DUE DATE]` | Manual |
| `[PAYMENT METHOD]` / `[PAYMENT REFERENCE]` | Manual |
| `[EVENT NAME]` … `[REGISTRATION LINK]` / outcomes | Manual |

---

## Automations (Free)

| Automation | Status |
|------------|--------|
| New Lead → follow-up Task (4 business hours) | Keep (Phase 0/2) |
| Auto-send any of the 10 templates to the lead | **Not added** — Free workflow email cannot reliably mail the lead |
| Quote sent → quote email | Deferred (no Quotes) |
| Invoice overdue → reminder | Deferred |
| Payment confirmed → enrolment email | Deferred |

See [TEMPLATE_SEND_CHECKLIST.md](TEMPLATE_SEND_CHECKLIST.md) and [TEMPLATE_EDIT_GUIDE.md](TEMPLATE_EDIT_GUIDE.md).
