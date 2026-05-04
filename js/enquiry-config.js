/**
 * Enquiry form delivery
 * ----------------------
 * Choose ONE provider:
 *
 * 1) brevo — Recommended if Google mail is blocked or unreliable.
 *    Deploy on Netlify or Cloudflare Pages, set environment variables (see google-apps-script/README.md),
 *    set provider: "brevo" below, use the same optional `secret` as BREVO_ENQUIRY_SECRET,
 *    and set `teamInbox` to the same address as BREVO_INTERNAL_TO (for mailto links + error text).
 *    Sheet rows: set APPS_SCRIPT_ENQUIRY_URL in hosting env (same URL as webAppUrl below) so the Brevo function can forward each lead to Apps Script after mail sends.
 *
 * 2) apps_script — Google Apps Script Web App + Sheet (see /google-apps-script/).
 *
 * Local (localhost / 127.0.0.1 / file://): js/enquiry-submit.js forces apps_script so every enquiry
 * form posts straight to webAppUrl without Netlify. Use ?enquiry=brevo in the URL, or set
 * localProvider: "brevo" below, to keep the Brevo Netlify path when running `npm run dev`.
 */
window.NEXPERTS_ENQUIRY_CONFIG = {
  /** "brevo" for Netlify + Brevo on real deploys; overridden to apps_script on local hosts (see header). */
  provider: "brevo",

  /** When "brevo" on localhost: keep using /.netlify/functions/enquiry-brevo (needs `npm run dev`). */
  // localProvider: "brevo",

  /** Apps Script — used when provider is apps_script, and on local dev when submit forces apps_script. */
  webAppUrl:
    "https://script.google.com/macros/s/AKfycbyNSKTV_CkeClhp0_dNkDRmWZR67iAvzvZe4e_uSjNV1djhswzm1W6SE1_D1Ky2d47ULQ/exec",

  /**
   * Optional. When omitted, `enquiry-submit.js` uses `/api/enquiry-brevo` (Cloudflare Pages) or
   * `/.netlify/functions/enquiry-brevo` on `*.netlify.app`. On Netlify with a **custom domain**,
   * set `brevoEndpoint: "/.netlify/functions/enquiry-brevo"` here.
   */
  // brevoEndpoint: "/.netlify/functions/enquiry-brevo",

  /** Same value as BREVO_ENQUIRY_SECRET on Netlify (and local .env for netlify dev). */
  secret: "JsdQGNFXr0iEiVr1HfKo8fQ-Wi3Plcn8oN8gOgeA_EM",

  /** General enquiries — must match BREVO_INTERNAL_TO (or aliases) on Netlify. */
  teamInbox: "enquiry@nexpertsacademy.com",
};
