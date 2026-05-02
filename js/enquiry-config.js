/**
 * Enquiry form delivery
 * ----------------------
 * Choose ONE provider:
 *
 * 1) brevo — Recommended if Google mail is blocked or unreliable.
 *    Deploy site on Netlify, set environment variables (see google-apps-script/README.md),
 *    set provider: "brevo" below, and use the same optional `secret` as BREVO_ENQUIRY_SECRET.
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

  /** Optional: set the same value as BREVO_ENQUIRY_SECRET on Netlify (and ENQUIRY_SECRET in Apps Script if used). */
  secret: "",
};
