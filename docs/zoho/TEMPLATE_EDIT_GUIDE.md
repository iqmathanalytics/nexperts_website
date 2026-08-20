# Zoho Free — edit the 10 email templates (UI guide)

Do this **in Zoho CRM** (Setup → Email → Templates, or Email Templates under Leads).  
Do **not** redesign HTML. Keep logo `https://www.nexpertsacademy.com/image/nexperts-logo.png`, colours `#081722` / `#c8f36b`, and email-safe tables.

Exact template names (no parentheses):

1. First follow-up individual  
2. First follow-up corporate group  
3. HRD Corp claim next steps  
4. Pricing payment options  
5. Schedule intake dates  
6. Quote attached  
7. Invoice payment reminder  
8. Enrolment confirmation  
9. Lost not now  
10. Workshop event invite  

Module for all: **Leads**.

---

## How to insert a merge field

1. Open the template → Edit HTML / body.  
2. Place cursor where the placeholder is.  
3. Use Zoho **Insert → Fields** (or equivalent) → pick **Leads** → choose the field.  
4. Do **not** type invent API names. Use what Zoho inserts.

---

## Global replacements (all templates that mention course / name)

| Find (literal) | Replace with (via Insert Fields) |
|----------------|----------------------------------|
| `${Leads.First Name}` | Keep if already present |
| `[COURSE NAME]` | Insert **Company** (website stores course here) |
| Course block that only says `[COURSE NAME]` | Same — Company |

Optional enrichment (once per template, not required):

| Find | Replace |
|------|---------|
| Long “interest / message” block | Insert **Description** |

---

## Per-template checklist

### 1. First follow-up individual

- [ ] First Name merge works  
- [ ] `[COURSE NAME]` → Company  
- [ ] Optional: Description for interest details  
- [ ] Leave fee/dates as Manual if present  

### 2. First follow-up corporate group

- [ ] First Name → merge  
- [ ] Course → Company  
- [ ] Requirements / message → Description  
- [ ] Participants, preferred date, mode, location → leave Manual placeholders  
- [ ] HRD: use Industry when applicable, else Manual  

### 3. HRD Corp claim next steps

- [ ] First Name + Company (course) merges  
- [ ] Keep `hrdcorp@nexpertsacademy.com` as static text  
- [ ] Registration number, employee count, HRD account, fee, status → Manual  
- [ ] Copy must not promise automatic approval  

### 4. Pricing payment options

- [ ] First Name + Company merges  
- [ ] `[AMOUNT]`, duration, mode, intake, payment link → Manual  
- [ ] If no payment link, remove or blank the CTA before Send  

### 5. Schedule intake dates

- [ ] First Name + Company merges  
- [ ] All date/time/location/fee/intake lists → Manual  

### 6. Quote attached

- [ ] First Name + Company merges  
- [ ] Quote number/date/total/validity/payment link → Manual  
- [ ] Do not paste PDF HTML into body — attach PDF on Send  

### 7. Invoice payment reminder

- [ ] First Name + Company merges  
- [ ] Invoice fields → Manual  
- [ ] Before Send: confirm not already paid (checklist)  

### 8. Enrolment confirmation

- [ ] First Name + Company merges  
- [ ] Dates, mode, location, joining link → Manual  
- [ ] Only send after payment/enrolment confirmed  

### 9. Lost not now

- [ ] First Name + Company merges  
- [ ] Lead Status → Insert Lead Status  
- [ ] Lead Owner → Insert if available  
- [ ] Future follow-up date → Manual + create Task  

### 10. Workshop event invite

- [ ] First Name merge only from Lead  
- [ ] All event fields stay Manual (no Events module on Free)  

---

## After editing

1. Save each template.  
2. Open a test Lead with First Name, Company (course), Description, Industry filled.  
3. Send / Preview each template to yourself.  
4. Confirm: no `[COURSE NAME]` left where Company should merge; other `[PLACEHOLDERS]` remain only where Manual.  
5. Tick results in [IMPLEMENTATION_REPORT.md](IMPLEMENTATION_REPORT.md) section J.
