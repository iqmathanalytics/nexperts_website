/**
 * Enquiry form delivery
 * ----------------------
 * Choose ONE provider:
 *
 * 1) brevo — Recommended if Google mail is blocked or unreliable.
 *    Deploy site on Netlify, set environment variables (see google-apps-script/README.md),
 *    set provider: "brevo" below, use the same optional `secret` as BREVO_ENQUIRY_SECRET,
 *    and set `teamInbox` to the same address as BREVO_INTERNAL_TO (for mailto links + error text).
 *
 * 2) apps_script — Legacy: Google Apps Script Web App + Sheet (see /google-apps-script/).
 */
window.NEXPERTS_ENQUIRY_CONFIG = {
  /** "brevo" for Netlify + Brevo; "apps_script" for Google Web App. */
  provider: "brevo",

  /** Apps Script (only when provider is "apps_script") */
  webAppUrl:
    "https://script.google.com/macros/s/AKfycbyKfumS-VFf4N8DZRpPkDHACoeV3tHimUneMBHfj1zrgX3Q952XwTt6gTI4Kjb6nUJu5A/exec",

  /** Brevo / Netlify function (when provider is "brevo"). Relative = same host as the page. */
  brevoEndpoint: "/.netlify/functions/enquiry-brevo",

  /** Same value as BREVO_ENQUIRY_SECRET on Netlify (and local .env for netlify dev). */
  secret: "JsdQGNFXr0iEiVr1HfKo8fQ-Wi3Plcn8oN8gOgeA_EM",

  /** General enquiries — must match BREVO_INTERNAL_TO (or BREVO_ENQUIRY_TO / NEXPERTS_ENQUIRY_EMAIL) on Netlify. */
  teamInbox: "eneeyannirmaran@gmail.com",
};
