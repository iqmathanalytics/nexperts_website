# Phase 4 — Harden, Standard custom fields, retire the sheet

Do this only after the team works Leads in Zoho daily on Free. Website payload (`first`, `last`, `email`, `phone`, `office`, `course`, `type`, `message`, `source`, `pageUrl`) does not change on Free.

Free-tier email templates: [TEMPLATE_FIELD_MAP.md](TEMPLATE_FIELD_MAP.md), [TEMPLATE_EDIT_GUIDE.md](TEMPLATE_EDIT_GUIDE.md), [TEMPLATE_SEND_CHECKLIST.md](TEMPLATE_SEND_CHECKLIST.md), [IMPLEMENTATION_REPORT.md](IMPLEMENTATION_REPORT.md).

---

## 1. When you upgrade to Standard — custom Lead fields

Free has **no custom fields**. After **Standard**, create fields aligned with [`docs/updates_on_p2.txt`](../updates_on_p2.txt), then map templates to real merges.

### Minimum (website + email templates)

| Label | Type | Suggested API name | Env override |
|-------|------|--------------------|--------------|
| Interested Course / Course | Single Line or Picklist | `Course` | `ZOHO_FIELD_COURSE` |
| Enquiry Type | Picklist | `Enquiry_Type` | `ZOHO_FIELD_ENQUIRY_TYPE` |
| Preferred Office | Picklist | `Preferred_Office` | `ZOHO_FIELD_OFFICE` |
| Page URL | URL | `Page_URL` | `ZOHO_FIELD_PAGE_URL` |
| Form Source | Single Line | `Form_Source` | `ZOHO_FIELD_FORM_SOURCE` |

Code already supports these five when `ZOHO_USE_CUSTOM_FIELDS=1`.

### Training / commercial (create in Zoho; extend mapper later)

| Label | Type |
|-------|------|
| Training Fee | Currency |
| Training Duration | Single Line |
| Training Mode | Picklist (Online / On-site / Hybrid) |
| Training Location | Single Line |
| Intake Date | Date |
| Training Start Date | Date |
| Training End Date | Date |
| Training Time | Single Line |
| Payment Link | URL |
| Joining Link | URL |
| Lead Type | Picklist (Individual / Corporate / Group) |
| Number of Participants | Number |
| Corporate Training Required | Checkbox |
| Preferred Training Date | Date |
| Preferred Training Location | Single Line |
| Corporate Requirements | Multi Line |
| HRD Corp Required | Checkbox |
| HRD Corp Account Number | Single Line |
| Company Registration Number | Single Line |
| Employee Count | Number |
| HRD Corp Application Status | Picklist |
| Future Follow-up Date | Date |
| Enrolment Status | Picklist |

Copy **API names** from Zoho after create (they may get suffixes). Then:

1. Set Cloudflare env API name overrides as needed.  
2. Set **`ZOHO_USE_CUSTOM_FIELDS=1`** and redeploy.  
3. Extend `mapEnquiryToLead` for any new website fields.  
4. Re-edit Zoho templates: replace Manual `[PLACEHOLDERS]` with real merges.

### Professional — Quotes / Invoices

Quotes, Invoices, Products, and payment-status automation need **Professional+**. Do not build a second quotation system on Free. When upgraded, point templates 6–7 at Quote/Invoice modules and attach PDFs from those records.

---

## 2. WhatsApp process (Free has no WhatsApp Business API)

Floating widget: `wa.me/601112216870`. Chats do not auto-create Leads.

For every new WhatsApp enquiry:

1. **Leads → Create**.  
2. First / last / phone / email if they share it.  
3. **Lead Source** = `WhatsApp`.  
4. **Industry** = enquiry type if known.  
5. **Company** = **course name** (same as website mapping for email templates).  
6. **Description** = office + message + context.  
7. Same follow-up task habit (4 business hours).

Optional later: Zoho SalesIQ; WhatsApp Business is Standard+ and uses credits.

---

## 3. Turnstile (spam)

Website forms have no CAPTCHA today. Spam that reaches Brevo will also reach Zoho.

When you want it:

1. Cloudflare dashboard → **Turnstile** → add `www.nexpertsacademy.com` + `localhost`.  
2. Put the **site key** on contact, home modal, course sidebar.  
3. Verify the token in `enquiry-brevo-core.mjs` before Brevo/Zoho.  
4. Do not put the **secret key** in frontend JS.

---

## 4. Retire the Google Sheet

Keep the sheet until Zoho has been the daily tool for several weeks.

1. Confirm `zohoLogged: true` on a real enquiry.  
2. Set **`APPS_SCRIPT_ENQUIRY_DISABLED=1`** (or `APPS_SCRIPT_ENQUIRY_URL=off`) and redeploy.  
3. Export the sheet once for archive.  
4. Leave Apps Script deployed in case you need logging again.

---

## 5. When to leave Free

Upgrade to **Standard** (~USD 14/user/month) when you need:

- More than 3 CRM users  
- More than ~5,000 records  
- Filterable Course / fee / HRD fields (custom fields)  
- Dynamic merges for most of the 10 templates  
- Gmail/Outlook sync, tags, assignment rules  

**Professional** when you need Quotes/Invoices inside Zoho and payment-status send guards.
