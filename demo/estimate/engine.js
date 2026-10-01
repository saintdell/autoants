// Quote engine: the owner's price book + arithmetic. No model, no guessing.
//
// Used by the walk-through demo (index.html) and the back-test (backtest.mjs).
// The quote-assistant skill's rule: the price comes from this table and this code,
// so the same job always gives the same number and every number can be audited.
// A model may READ a voicemail or crew notes into a `job`; it never sets a price.
//
// SAMPLE_BOOK holds demo rates for tree work. They are placeholders for the
// walk-through, not anyone's real prices and not a market survey. A client's book
// replaces them before step 6 (the back-test against his last 20 quotes).

export const SAMPLE_BOOK = {
  name: "Sample rates (set to the owner's before use)",
  version: "sample-1",
  crew_cost_per_hour: 150,        // loaded labor for the crew, per on-site hour
  equipment_cost_per_hour: 60,    // truck + chipper, per on-site hour
  markup: 1.6,                    // price = cost x markup
  minimum: 300,                   // smallest job the crew rolls out for
  removal_hours: { "under-30": 2, "30-60": 4, "60-80": 6.5, "over-80": 10 },
  trim_factor: 0.45,              // a trim takes this share of a removal's hours
  inch_hours_over_12: 0.08,       // extra hours per inch of trunk over 12"
  location_factor: { "open": 1.0, "near-house": 1.25, "over-house": 1.5 },
  access_factor: { "truck": 1.0, "backyard-climb": 1.35 },
  haul_off_cost: { "under-30": 35, "30-60": 70, "60-80": 110, "over-80": 160 },
  stump_price_per_inch: 4,
  stump_minimum: 100,
  range_pct: 0.15,                // the customer sees price +/- this
  valid_days: 14,
  terms: "Includes cleanup of all debris we cut. Estimate confirmed on site.",
};

export const HEIGHTS = ["under-30", "30-60", "60-80", "over-80"];

const round = (n, to) => Math.round(n / to) * to;

const REQUIRED_RATES = ["crew_cost_per_hour", "equipment_cost_per_hour", "markup", "minimum",
                        "stump_price_per_inch", "stump_minimum", "trim_factor", "inch_hours_over_12", "range_pct"];

// A blank rate stops the quote. A guessed rate would go to a customer.
export function checkBook(book) {
  const missing = REQUIRED_RATES.filter(k => typeof book[k] !== "number" || !Number.isFinite(book[k]));
  for (const t of ["removal_hours", "location_factor", "access_factor", "haul_off_cost"])
    for (const [k, v] of Object.entries(book[t] || {})) if (typeof v !== "number") missing.push(`${t}.${k}`);
  if (missing.length) throw new Error(`price book is missing: ${missing.join(", ")}`);
}

export function quote(job, book = SAMPLE_BOOK) {
  checkBook(book);
  const j = {
    service: "removal", height: "30-60", diameter: 18, location: "open",
    access: "truck", haul_off: true, stump: false, stump_diameter: 0,
    power_lines: false, ...job,
  };
  const visit = [];
  if (j.power_lines) visit.push("Lines run through or near the tree. The utility may have to clear them first.");
  if (j.height === "over-80" && j.location === "over-house") visit.push("Over 80 ft and over the house: likely a crane job.");
  for (const [k, table] of [["height", book.removal_hours], ["location", book.location_factor], ["access", book.access_factor]]) {
    if (j.service !== "stump-only" && !(j[k] in table)) throw new Error(`price book has no ${k} "${j[k]}"`);
  }

  const lines = [];
  let cost = 0, hours = 0;
  if (j.service !== "stump-only") {
    const base = book.removal_hours[j.height] * (j.service === "trim" ? book.trim_factor : 1);
    const extra = Math.max(0, (Number(j.diameter) || 0) - 12) * book.inch_hours_over_12;
    hours = (base + extra) * book.location_factor[j.location] * book.access_factor[j.access];
    const labor = hours * book.crew_cost_per_hour;
    const equip = hours * book.equipment_cost_per_hour;
    lines.push({ label: `Crew, ${hours.toFixed(1)} h`, cost: labor, group: j.service === "trim" ? "Tree trimming" : "Tree removal" });
    lines.push({ label: `Truck and chipper, ${hours.toFixed(1)} h`, cost: equip, group: j.service === "trim" ? "Tree trimming" : "Tree removal" });
    cost += labor + equip;
    if (j.haul_off) {
      const dump = book.haul_off_cost[j.height] * (j.service === "trim" ? 0.5 : 1);
      lines.push({ label: "Haul-off and dump fee", cost: dump, group: "Haul-off and disposal" });
      cost += dump;
    }
  }
  let price = cost * book.markup;
  if (j.stump || j.service === "stump-only") {
    const stump = Math.max(book.stump_minimum, (Number(j.stump_diameter) || Number(j.diameter) || 0) * book.stump_price_per_inch);
    lines.push({ label: "Stump grinding", cost: stump / book.markup, group: "Stump grinding" });
    cost += stump / book.markup;
    price += stump;
  }
  const minimumApplied = price < book.minimum;
  price = round(Math.max(price, book.minimum), 5);
  return {
    book_version: book.version,
    needs_visit: visit.length > 0,
    visit_reasons: visit,
    hours: Number(hours.toFixed(2)),
    lines: lines.map(l => ({ ...l, cost: Math.round(l.cost) })),
    cost: Math.round(cost),
    price,
    margin_pct: price ? Math.round((1 - cost / price) * 100) : 0,
    minimum_applied: minimumApplied,
    low: round(price * (1 - book.range_pct), 25),
    high: round(price * (1 + book.range_pct), 25),
    valid_days: book.valid_days,
    terms: book.terms,
  };
}

// What the customer may see. Built by WHITELIST, so a field added to quote()
// later can't leak cost, markup or margin to a customer by default.
export function customerView(q) {
  if (q.needs_visit) {
    return { needs_visit: true, message: "This one needs a quick look in person before we can price it.",
             reasons: q.visit_reasons };
  }
  return { needs_visit: false, low: q.low, high: q.high,
           label: "Estimate, confirmed on site", valid_days: q.valid_days, terms: q.terms };
}

// Customer-facing proposal lines: each group's share of the final price, so the
// items add up to exactly the quoted price and no cost, hour or markup appears.
// Refuses a job that needs a site visit: there is no price to propose yet.
export function proposalItems(q) {
  if (q.needs_visit) throw new Error("needs a site visit before there's a price to propose: " + q.visit_reasons.join(" "));
  const groups = new Map();
  for (const l of q.lines) groups.set(l.group || l.label, (groups.get(l.group || l.label) || 0) + l.cost);
  const total = [...groups.values()].reduce((a, b) => a + b, 0) || 1;
  const items = [...groups].map(([label, cost]) => ({ label, price: Math.round((q.price * cost / total) / 5) * 5 }));
  const diff = q.price - items.reduce((a, i) => a + i.price, 0);
  if (items.length) items.reduce((a, b) => (b.price > a.price ? b : a)).price += diff;
  return items;
}
