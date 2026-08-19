# Zoho CRM (Nexperts Academy)

Website enquiries already email via Brevo and log to Google Sheets. Zoho CRM is the sales system of record. Public HTML forms are unchanged.

| Phase | Doc | Who |
|-------|-----|-----|
| 0 | [PHASE_0_SETUP.md](PHASE_0_SETUP.md) | You — Zoho org, picklists, Self Client token |
| 1 | Code in `functions/api/zoho-crm.mjs` + env in [DEPLOY_CLOUDFLARE.md](../DEPLOY_CLOUDFLARE.md) | Deploy after Phase 0 |
| 2 | [PHASE_2_SALES_PROCESS.md](PHASE_2_SALES_PROCESS.md) | You — statuses, convert, Deal stages, templates |
| 3 | [PHASE_3_SHEET_IMPORT.md](PHASE_3_SHEET_IMPORT.md) | One-off CSV import (`scripts/zoho_sheet_to_leads_csv.py`) |
| 4 | [PHASE_4_HARDEN.md](PHASE_4_HARDEN.md) | Optional — custom fields, WhatsApp, Turnstile, retire sheet |

Grant token helper: `node scripts/zoho_exchange_grant.mjs <grant_code>`
