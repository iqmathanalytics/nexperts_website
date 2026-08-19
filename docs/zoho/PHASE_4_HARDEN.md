# Phase 4 — Harden, Standard custom fields, retire the sheet

Do this only after the team works Leads in Zoho daily. Website payload (`first`, `last`, `email`, `phone`, `office`, `course`, `type`, `message`, `source`, `pageUrl`) does not change.

---

## 1. Standard custom-field mapper (code already supports this)

Free has **no custom fields**. After you upgrade to **Standard**:

1. **Setup → Modules and Fields → Leads** — create:

   | Label | Type | Suggested API name |
   |-------|------|--------------------|
   | Course | Single line | `Course` |
   | Enquiry Type | Picklist (same options as the website) | `Enquiry_Type` |
   | Preferred Office | Picklist | `Preferred_Office` |
   | Page URL | URL | `Page_URL` |
   | Form Source | Single line | `Form_Source` |

2. Copy the **API names** from Zoho (they may get a suffix like `Course_of_Interest`). If they differ, set:

   ```
   ZOHO_FIELD_COURSE=...
   ZOHO_FIELD_ENQUIRY_TYPE=...
   ZOHO_FIELD_OFFICE=...
   ZOHO_FIELD_PAGE_URL=...
   ZOHO_FIELD_FORM_SOURCE=...
   ```

3. Set Cloudflare env **`ZOHO_USE_CUSTOM_FIELDS=1`** and redeploy.

`functions/api/zoho-crm.mjs` then writes those API names **in addition to** Description / Industry / Company so old records stay readable.

---

## 2. WhatsApp process (Free has no WhatsApp Business API)

Floating widget: `wa.me/601112216870`. Chats do not auto-create Leads.

For every new WhatsApp enquiry:

1. **Leads → Create**.
2. First / last / phone / email if they share it.
3. **Lead Source** = `WhatsApp`.
4. **Industry** = enquiry type if known.
5. **Company** = preferred office if known.
6. **Description** = paste the first message + course name.
7. Same follow-up task habit as website leads (4 business hours).

Optional later: Zoho SalesIQ (visitor chat) is listed on Free integrations; WhatsApp Business messaging is **Standard+** and uses credits.

---

## 3. Turnstile (spam)

Website forms have no CAPTCHA today. Spam that reaches Brevo will also reach Zoho.

When you want it:

1. Cloudflare dashboard → **Turnstile** → add `www.nexpertsacademy.com` + `localhost`.
2. Put the **site key** in the three form pages (contact, home modal, course sidebar).
3. Verify the token in `enquiry-brevo-core.mjs` with Turnstile siteverify **before** Brevo/Zoho.
4. Do not put the **secret key** in frontend JS.

Do not enable until a site key and secret exist. Ask in a later session to wire the widgets (contact.html, index.html, course sidebar template).

---

## 4. Retire the Google Sheet

Keep the sheet until Zoho has been the daily tool for several weeks.

To stop new rows:

1. Confirm `zohoLogged: true` on a real enquiry (browser Network tab → `/api/enquiry-brevo`).
2. Clear **`APPS_SCRIPT_ENQUIRY_URL`** is not enough (a built-in Apps Script URL is used as fallback). Set Cloudflare env **`APPS_SCRIPT_ENQUIRY_DISABLED=1`** (or `APPS_SCRIPT_ENQUIRY_URL=off`) and redeploy. New enquiries will skip the sheet (`sheetLogged: false`, hint says disabled).
3. Export the sheet once more for archive (Drive / CSV).
4. Leave Apps Script deployed in case you need to turn logging back on.

Internal Brevo mail still links the sheet URL via `NEXPERTS_LEADS_SHEET_URL` until you change that copy.

---

## 5. When to leave Free

Upgrade to **Standard** (~USD 14/user/month) when you need any of:

- More than 3 CRM users
- More than ~5,000 records
- Filterable Course / office fields (custom fields)
- Gmail/Outlook sync, tags, assignment rules

**Professional** is only needed for quotes/invoices inside Zoho. Training invoices can stay outside CRM on Free.
