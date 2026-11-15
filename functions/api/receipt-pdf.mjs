/**
 * Official Nexperts Academy payment receipt PDF (matches Nexperts-Receipt-Sample.pdf).
 */

import { PDFDocument, StandardFonts, rgb } from "pdf-lib";

const MAROON = rgb(0.48, 0.12, 0.12);
const GREEN = rgb(0.13, 0.55, 0.33);
const INK = rgb(0.12, 0.14, 0.16);
const MUTED = rgb(0.35, 0.38, 0.42);
const LINE = rgb(0.82, 0.84, 0.86);
const BG_SOFT = rgb(0.96, 0.97, 0.98);
const WHITE = rgb(1, 1, 1);

const ONES = [
  "",
  "One",
  "Two",
  "Three",
  "Four",
  "Five",
  "Six",
  "Seven",
  "Eight",
  "Nine",
  "Ten",
  "Eleven",
  "Twelve",
  "Thirteen",
  "Fourteen",
  "Fifteen",
  "Sixteen",
  "Seventeen",
  "Eighteen",
  "Nineteen",
];
const TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"];

function chunkToWords(n) {
  if (n < 20) return ONES[n];
  if (n < 100) {
    const t = TENS[Math.floor(n / 10)];
    const o = ONES[n % 10];
    return o ? `${t}-${o}` : t;
  }
  const h = ONES[Math.floor(n / 100)];
  const rest = n % 100;
  return rest ? `${h} Hundred and ${chunkToWords(rest)}` : `${h} Hundred`;
}

/** Convert a MYR amount to words, e.g. 599 → "Malaysian Ringgit Five Hundred and Ninety-Nine Only" */
export function amountInWordsMyr(amount) {
  const n = Math.round(Number(amount) || 0);
  if (n <= 0) return "Malaysian Ringgit Zero Only";
  if (n >= 1000000) return `Malaysian Ringgit ${n.toLocaleString("en-MY")} Only`;

  const thousands = Math.floor(n / 1000);
  const rem = n % 1000;
  let body = "";
  if (thousands) {
    body = `${chunkToWords(thousands)} Thousand`;
    if (rem) body += rem < 100 ? ` and ${chunkToWords(rem)}` : ` ${chunkToWords(rem)}`;
  } else {
    body = chunkToWords(rem);
  }
  return `Malaysian Ringgit ${body} Only`;
}

function money(n) {
  const v = Number(n);
  if (!Number.isFinite(v)) return "0.00";
  return v.toLocaleString("en-MY", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function wrapLines(font, text, size, maxWidth) {
  const words = String(text || "").split(/\s+/).filter(Boolean);
  const lines = [];
  let cur = "";
  for (const w of words) {
    const trial = cur ? `${cur} ${w}` : w;
    if (font.widthOfTextAtSize(trial, size) <= maxWidth) {
      cur = trial;
    } else {
      if (cur) lines.push(cur);
      cur = w;
    }
  }
  if (cur) lines.push(cur);
  return lines.length ? lines : [""];
}

/**
 * @param {object} meta
 */
export async function buildOfficialReceiptPdf(meta) {
  const doc = await PDFDocument.create();
  const page = doc.addPage([595.28, 841.89]);
  const font = await doc.embedFont(StandardFonts.Helvetica);
  const bold = await doc.embedFont(StandardFonts.HelveticaBold);

  const W = page.getWidth();
  const margin = 40;
  let y = 800;

  const drawText = (text, x, yy, size, f, color) => {
    page.drawText(String(text || ""), {
      x,
      y: yy,
      size,
      font: f || font,
      color: color || INK,
    });
  };

  // --- Header: company (left) + RECEIPT (right) ---
  drawText("NEXPERTS ACADEMY", margin, y, 14, bold, MAROON);
  y -= 14;
  drawText("The Networking Experts.", margin, y, 8, font, MUTED);
  y -= 18;
  drawText("Nexperts Academy Sdn Bhd (SSM No.: 804273-K)", margin, y, 8, bold, INK);
  y -= 11;
  const addrLines = [
    "E-313, Phileo Damansara 1, Jalan 16/11,",
    "Off Jalan Damansara, 46350 Petaling Jaya, Selangor, Malaysia",
    "+60 11-1221 6870  ·  enquiry@nexpertsacademy.com",
  ];
  for (const line of addrLines) {
    drawText(line, margin, y, 7.5, font, MUTED);
    y -= 10;
  }

  const rightX = W - margin;
  drawText("RECEIPT", rightX - bold.widthOfTextAtSize("RECEIPT", 22), 792, 22, bold, MAROON);
  const sub = "OFFICIAL PAYMENT RECEIPT";
  drawText(sub, rightX - font.widthOfTextAtSize(sub, 8), 776, 8, font, MUTED);

  // PAID badge
  const badgeW = 52;
  const badgeH = 18;
  const badgeX = rightX - badgeW;
  const badgeY = 752;
  page.drawRectangle({
    x: badgeX,
    y: badgeY,
    width: badgeW,
    height: badgeH,
    borderColor: GREEN,
    borderWidth: 1.5,
    color: WHITE,
  });
  const paidLabel = "PAID";
  drawText(
    paidLabel,
    badgeX + (badgeW - bold.widthOfTextAtSize(paidLabel, 10)) / 2,
    badgeY + 5,
    10,
    bold,
    GREEN
  );

  y = Math.min(y, 735);
  page.drawLine({
    start: { x: margin, y },
    end: { x: W - margin, y },
    thickness: 1,
    color: LINE,
  });
  y -= 22;

  // --- Received From / Receipt Details ---
  const colMid = margin + 280;
  drawText("RECEIVED FROM", margin, y, 8, bold, MAROON);
  drawText("RECEIPT DETAILS", colMid, y, 8, bold, MAROON);
  y -= 14;

  const name = String(meta.participantName || "Participant");
  drawText(name, margin, y, 11, bold, INK);
  const details = [
    ["Receipt No.", meta.invoiceNo || meta.receiptNumber || "—"],
    ["Date", meta.paymentDate || "—"],
    ["Order Ref.", meta.orderRef || "—"],
    ["Currency", meta.currency || "MYR"],
  ];
  let dy = y;
  for (const [label, value] of details) {
    drawText(label, colMid, dy, 8, font, MUTED);
    drawText(String(value), colMid + 70, dy, 8, bold, INK);
    dy -= 12;
  }

  y -= 12;
  drawText(String(meta.email || ""), margin, y, 8, font, MUTED);
  y -= 11;
  drawText(String(meta.phone || "—"), margin, y, 8, font, MUTED);
  y = Math.min(y, dy) - 16;

  page.drawLine({
    start: { x: margin, y },
    end: { x: W - margin, y },
    thickness: 0.8,
    color: LINE,
  });
  y -= 18;

  // --- Line items table ---
  const tableX = margin;
  const tableW = W - margin * 2;
  const cols = [
    { key: "desc", label: "DESCRIPTION", w: 220 },
    { key: "intake", label: "INTAKE / MODE", w: 180 },
    { key: "qty", label: "QTY", w: 40 },
    { key: "amt", label: "AMOUNT", w: tableW - 220 - 180 - 40 },
  ];

  page.drawRectangle({
    x: tableX,
    y: y - 4,
    width: tableW,
    height: 18,
    color: MAROON,
  });
  let cx = tableX + 6;
  for (const c of cols) {
    drawText(c.label, cx, y, 7.5, bold, WHITE);
    cx += c.w;
  }
  y -= 28;

  const descMain = String(meta.courseName || "Course");
  const descSub = String(meta.durationNote || "").trim();
  const intakeMain = String(meta.intakeLabel || "").trim();
  const modeMain = String(meta.trainingMode || "").trim();
  const amountNum = Number(meta.amountNumeric);
  const amountStr = money(Number.isFinite(amountNum) ? amountNum : 0);

  drawText(descMain, tableX + 6, y, 9, bold, INK);
  if (descSub) drawText(descSub, tableX + 6, y - 11, 7.5, font, MUTED);
  drawText(intakeMain || "—", tableX + cols[0].w + 6, y, 8, font, INK);
  if (modeMain) drawText(modeMain, tableX + cols[0].w + 6, y - 11, 7.5, font, MUTED);
  drawText("1", tableX + cols[0].w + cols[1].w + 12, y, 9, font, INK);
  const amtX =
    tableX + cols[0].w + cols[1].w + cols[2].w + cols[3].w - 6 - font.widthOfTextAtSize(amountStr, 9);
  drawText(amountStr, amtX, y, 9, bold, INK);
  y -= 36;

  page.drawLine({
    start: { x: margin, y },
    end: { x: W - margin, y },
    thickness: 0.8,
    color: LINE,
  });
  y -= 18;

  // --- Amount in words + totals ---
  const wordsBoxW = 280;
  const words = amountInWordsMyr(Number.isFinite(amountNum) ? amountNum : 0);
  page.drawRectangle({
    x: margin,
    y: y - 42,
    width: wordsBoxW,
    height: 48,
    color: BG_SOFT,
    borderColor: LINE,
    borderWidth: 0.8,
  });
  drawText("AMOUNT IN WORDS", margin + 8, y - 4, 7, bold, MAROON);
  const wordLines = wrapLines(font, words, 8, wordsBoxW - 16);
  let wy = y - 18;
  for (const wl of wordLines.slice(0, 2)) {
    drawText(wl, margin + 8, wy, 8, font, INK);
    wy -= 11;
  }

  const totalsX = margin + wordsBoxW + 24;
  const labelX = totalsX;
  const valueRight = W - margin;
  const rows = [
    ["Subtotal", money(amountNum), false],
    ["Discount", money(0), false],
    ["Tax", money(0), false],
    ["Total", `RM ${money(amountNum)}`, "total"],
    ["Amount Paid", `RM ${money(amountNum)}`, "paid"],
    ["Balance Due", `RM ${money(0)}`, false],
  ];
  let ty = y;
  for (const [label, value, tone] of rows) {
    if (tone === "total") {
      page.drawRectangle({
        x: labelX - 6,
        y: ty - 3,
        width: valueRight - labelX + 12,
        height: 16,
        color: MAROON,
      });
      drawText(label, labelX, ty, 9, bold, WHITE);
      drawText(value, valueRight - bold.widthOfTextAtSize(value, 9), ty, 9, bold, WHITE);
    } else if (tone === "paid") {
      drawText(label, labelX, ty, 9, bold, GREEN);
      drawText(value, valueRight - bold.widthOfTextAtSize(value, 9), ty, 9, bold, GREEN);
    } else {
      drawText(label, labelX, ty, 8, font, MUTED);
      drawText(value, valueRight - font.widthOfTextAtSize(value, 8), ty, 8, font, INK);
    }
    ty -= 16;
  }
  y = Math.min(y - 56, ty) - 10;

  // --- Payment information ---
  page.drawRectangle({
    x: margin,
    y: y - 48,
    width: W - margin * 2,
    height: 56,
    color: BG_SOFT,
    borderColor: LINE,
    borderWidth: 0.8,
  });
  drawText("PAYMENT INFORMATION", margin + 10, y - 6, 8, bold, MAROON);
  drawText(`Method  ${meta.paymentMethod || "Card (Stripe)"}`, margin + 10, y - 22, 8, font, INK);
  drawText(`Processor  ${meta.processor || "Stripe"}`, margin + 260, y - 22, 8, font, INK);
  drawText(
    `Transaction ID  ${meta.transactionId || meta.receiptNumber || "—"}`,
    margin + 10,
    y - 36,
    8,
    font,
    INK
  );
  drawText(`Paid on  ${meta.paidOn || meta.paymentDate || "—"}`, margin + 260, y - 36, 8, font, INK);
  y -= 70;

  // --- Notes ---
  const notes = [
    "Training is delivered Live Online unless otherwise stated. Intake dates and training mode are subject to change with due notice and the consent of both parties.",
    "Joining instructions (venue details or online session link) will be emailed before the class starts.",
    "Fees are subject to our refund and rescheduling policy. Please keep this receipt for your records and any claims.",
  ];
  for (const note of notes) {
    const lines = wrapLines(font, `•  ${note}`, 7, W - margin * 2);
    for (const line of lines) {
      drawText(line, margin, y, 7, font, MUTED);
      y -= 9;
    }
    y -= 3;
  }

  y -= 8;
  drawText("Thank you for enrolling with ", margin, y, 9, font, INK);
  const thanksPrefixW = font.widthOfTextAtSize("Thank you for enrolling with ", 9);
  drawText("Nexperts Academy.", margin + thanksPrefixW, y, 9, bold, MAROON);
  y -= 14;
  drawText(
    "www.nexpertsacademy.com  ·  EC-Council ATC of the Year 2025  ·  CompTIA Partner  ·  HRD Corp Registered Training Provider",
    margin,
    y,
    6.5,
    font,
    MUTED
  );
  y -= 10;
  drawText("Malaysia  ·  United Kingdom  ·  United States", margin, y, 7, font, MUTED);
  y -= 16;
  page.drawLine({
    start: { x: margin, y },
    end: { x: W - margin, y },
    thickness: 0.6,
    color: LINE,
  });
  y -= 12;
  drawText("This is a computer-generated receipt. No signature is required.", margin, y, 7, font, MUTED);

  const bytes = await doc.save();
  if (typeof Buffer !== "undefined") {
    return Buffer.from(bytes).toString("base64");
  }
  let binary = "";
  const arr = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  for (let i = 0; i < arr.length; i++) binary += String.fromCharCode(arr[i]);
  return btoa(binary);
}
