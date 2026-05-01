# Website enquiries → Google Sheet + email (Apps Script)

This folder contains the **Google Apps Script** code that powers the enquiry forms on the static site (`contact.html` and the landing-page “Enquire Now” modal).

## What it does

1. **Appends one row** to a Google Sheet for every submission.
2. Sends **two emails** via `MailApp`:
   - **To the student** (the address they typed): short acknowledgement.
   - **To `enquiry@nexpertsacademy.com`**: full enquiry details (student’s address is set as **Reply-To** so you can hit “Reply”).

Emails are sent **from the Google account that owns the script** (the account you choose under *Execute as* when you deploy). If you create the Sheet + Script while signed in as **`info@nexpertsai.com`**, that is the mailbox Apps Script uses — this matches your plan.

> **Google Workspace note:** “Send mail as” aliases are a mailbox setting. If `info@nexpertsai.com` is the primary user authorising the script, you are in the normal case. If you need a different *display* name only, you can adjust the deployment account or use the Gmail API with a send-as alias (advanced).

## One-time setup

1. Sign in to Google as **`info@nexpertsai.com`**.
2. **Sheets → Blank** (this workbook will hold enquiry rows).
3. **Extensions → Apps Script** → delete any boilerplate → paste **`EnquiryWebhook.gs`**.
4. In the script editor, select **`setupSheetHeaders`** → **Run** → approve permissions.
5. *(Recommended)* **Project Settings → Script properties** → add:
   - `ENQUIRY_SECRET` = a long random string (same value you paste into `js/enquiry-config.js` as `secret`).
6. **Deploy → New deployment**
   - Type: **Web app**
   - **Execute as:** *Me (info@nexpertsai.com)*
   - **Who has access:** *Anyone* (required so anonymous visitors on your public website can POST)
7. Copy the **Web App URL** (starts with `https://script.google.com/macros/...`).
8. In the website repo, edit **`js/enquiry-config.js`**:
   - `webAppUrl`: paste that URL
   - `secret`: same as `ENQUIRY_SECRET` (or leave both empty to skip verification — not recommended in production)

## Testing

- Submit the form on `http://localhost:8000/contact.html` after configuring `webAppUrl`.
- Check the Sheet tab **`Enquiries`** for a new row.
- Check **inbox + spam** on both the student address and `enquiry@nexpertsacademy.com`.

## “Sent” in Gmail but nothing in Inbox?

If rows appear in the Sheet and messages show under **Sent** in `info@nexpertsai.com`, Apps Script **did send** the mail. When recipients still see nothing, it is almost always **delivery after Google’s hand-off** (spam, quarantine, or group rules).

### Checklist (do in order)

1. **Spam / Promotions / Updates** (Gmail) on **both** the student mailbox and every inbox that receives `enquiry@nexpertsacademy.com` (group members see mail in **their** spam too).
2. Gmail search: `in:anywhere subject:(Website enquiry)` or the student subject `We received your enquiry`.
3. **`enquiry@nexpertsacademy.com` is a Google Group?** In Google Groups: allow **external** senders if the script sends from `info@nexpertsai.com` (another domain). Check **moderated messages** / **rejected** queue for the group.
4. **Google Workspace** for `nexpertsacademy.com`: Admin console → **Reporting** → **Email log search** (or **Security** → **Quarantine**) for blocked messages to that user/group.
5. **Cross-domain reputation**: Mail is **From** `info@nexpertsai.com`. Receiving servers for `@nexpertsacademy.com` may score that path stricter. Ensure **SPF/DKIM** (and DMARC if used) are valid for the **sending** domain; consider an **inbound gateway** or sending from a mailbox on the same domain if your host recommends it.
6. **Debug copy**: In Apps Script → **Project settings** → **Script properties**, add `OPTIONAL_BCC` = your personal Gmail (not the same as `to`). Redeploy the web app, submit once — you should get **BCC copies** of both messages in that inbox. If BCC arrives but `enquiry@…` does not, the problem is **routing to that address**, not the script.
7. In the script editor, run **`testEmailDelivery`** once (select function → Run). That sends a simple test **to your own** `info@…` inbox. If that lands in Inbox, MailApp is fine; focus on the `enquiry@…` path and spam policies.

### Script updates in `EnquiryWebhook.gs`

- Sends **multipart** mail (`body` + `htmlBody`) and sets sender **display name** `Nexperts Academy`.
- Optional **`OPTIONAL_BCC`** script property for a debug inbox.
- Manual test function **`testEmailDelivery`**.

After changing `.gs`, use **Deploy → Manage deployments → Edit** (same version) or **New version** so the live Web App picks up changes.

## Security (practical)

- **Always set `ENQUIRY_SECRET`** once you go live; it is not encryption, but it stops casual script spam.
- Apps Script quotas apply (emails/day, execution time). For very high volume, move to a paid backend.
