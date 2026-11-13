/**
 * Server-side allowlist for Stripe-enrollable courses.
 * Amounts are in sen (MYR * 100). Never trust client-posted prices.
 */

export const STRIPE_COURSES = {
  "agentic-ai": {
    slug: "agentic-ai",
    name: "Agentic AI Engineering",
    amountSen: 79900,
    currency: "myr",
    intakes: [
      {
        id: "2026-11-16",
        label: "16 Nov 2026 – 2 Jan 2027 (Mon · Wed · Fri · 6pm–10pm)",
      },
    ],
    modes: ["Live Online", "Classroom"],
    pagePath: "/courses/agentic-ai",
  },
  "claude-ai-productivity-90-minutes": {
    slug: "claude-ai-productivity-90-minutes",
    name: "Claude AI Masterclass",
    amountSen: 59900,
    currency: "myr",
    intakes: [
      {
        id: "2026-11-28",
        label: "28–29 Nov 2026 · 2 days · 9am–5pm",
      },
    ],
    modes: ["Live Online", "Classroom"],
    pagePath: "/courses/claude-ai-productivity-90-minutes",
  },
};

export function getStripeCourse(slug) {
  const key = String(slug || "").trim();
  return STRIPE_COURSES[key] || null;
}

export function resolveIntake(course, intakeId) {
  if (!course || !Array.isArray(course.intakes)) return null;
  const id = String(intakeId || "").trim();
  return course.intakes.find((i) => i.id === id) || null;
}

export function resolveMode(course, mode) {
  const m = String(mode || "").trim();
  if (!course || !Array.isArray(course.modes)) return null;
  return course.modes.includes(m) ? m : null;
}

export function formatRmFromSen(sen) {
  const n = Number(sen);
  if (!Number.isFinite(n)) return "";
  return "RM " + (n / 100).toLocaleString("en-MY", { minimumFractionDigits: 0, maximumFractionDigits: 2 });
}
