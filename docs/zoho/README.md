# Zoho CRM (Nexperts Academy)

Website enquiries already email via Brevo and log to Google Sheets. Zoho CRM is the sales system of record. Public HTML forms are unchanged.

| Phase | Doc | Who |
|-------|-----|-----|
| 0 | [PHASE_0_SETUP.md](PHASE_0_SETUP.md) | You — Zoho org, picklists, Self Client token |
| 1 | Code in `functions/api/zoho-crm.mjs` + env in [DEPLOY_CLOUDFLARE.md](../DEPLOY_CLOUDFLARE.md) | Deploy after Phase 0 |
| 2 | [PHASE_2_SALES_PROCESS.md](PHASE_2_SALES_PROCESS.md) | You — statuses, convert, Deal stages, templates |
| 2b Free templates | [TEMPLATE_FIELD_MAP.md](TEMPLATE_FIELD_MAP.md) · [TEMPLATE_EDIT_GUIDE.md](TEMPLATE_EDIT_GUIDE.md) · [TEMPLATE_SEND_CHECKLIST.md](TEMPLATE_SEND_CHECKLIST.md) · [IMPLEMENTATION_REPORT.md](IMPLEMENTATION_REPORT.md) | Free-safe merges + manual placeholders |
| 3 | [PHASE_3_SHEET_IMPORT.md](PHASE_3_SHEET_IMPORT.md) | One-off CSV import (`scripts/zoho_sheet_to_leads_csv.py`) |
| 4 | [PHASE_4_HARDEN.md](PHASE_4_HARDEN.md) | Upgrade path — custom fields, WhatsApp, Turnstile, retire sheet |

Grant token helper: `node scripts/zoho_exchange_grant.mjs <grant_code>`

**Free edition:** do not invent custom merge fields. Upgrade when ready; we will wire `ZOHO_USE_CUSTOM_FIELDS` then.
