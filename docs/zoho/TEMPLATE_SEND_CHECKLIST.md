# Zoho Free — template send checklist

Use before sending any of the 10 Lead email templates.  
Free edition cannot auto-block bad sends — this checklist is the safeguard.

## Every send

1. Lead has a valid **Email**.
2. Open the correct template (exact name, no parentheses).
3. Preview: **First Name** and **Company** (course) look correct.
4. Replace every remaining `[PLACEHOLDER]` with real values, **or** delete that line/CTA.
5. Do not leave broken links or empty `https://` CTAs.
6. Send from the Lead record so Zoho can log the email when email integration allows (Free often has limited IMAP — see limitations below).

## By template

| Template | Extra checks |
|----------|----------------|
| First follow-up individual | Course in Company; optional note from Description |
| First follow-up corporate group | Fill participants / dates / mode if mentioned; HRD only if relevant |
| HRD Corp claim next steps | Fill company registration / HRD account if known; never promise auto-approval; CC/contact `hrdcorp@nexpertsacademy.com` as needed |
| Pricing payment options | Type fee manually; remove Payment CTA if no real link |
| Schedule intake dates | Fill dates/times/locations manually |
| Quote attached | Attach Quote **PDF** before Send; fill quote number/total/validity; no PDF → do not send |
| Invoice payment reminder | **Do not send** if payment already received; fill invoice fields; no broken payment link |
| Enrolment confirmation | **Only after** payment/enrolment confirmed; fill joining details |
| Lost not now | Set Lead Status appropriately; create Task for future follow-up date if promised |
| Workshop event invite | Do not send if event cancelled; fill all event placeholders |

## Automations intentionally not used (Free)

- Do **not** auto-send these templates on Lead create.
- Keep only: new Lead → Task “Follow up within 4 business hours”.
- Student acknowledgement remains on **Brevo** (website), not Zoho templates.

## Email logging limitation (Free)

- Prefer sending from Zoho CRM so activity can attach to the Lead.
- Without Standard email integration (Gmail/Outlook), logging may be incomplete.
- If you send outside Zoho, paste a Note on the Lead: template name + date.
