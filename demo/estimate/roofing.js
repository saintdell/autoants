// Roofing quote engine: a replacement priced by the square, from the roofer's own book.
//
// Same contract as engine.js (tree work): the price comes from the table and plain
// arithmetic, a blank rate stops the quote, and the customer sees only the range
// (customerView is shared). This is also Category 7's task 5 ("measurements ->
// proposal/estimate") in its first, staff-only form.
//
// ROOFING_SAMPLE_BOOK holds placeholder rates for the walk-through, not a market
// survey. Repairs and insurance claims never get an instant number: a repair needs
// eyes on the roof, and a claim follows the carrier's estimate, not the price book.
import { customerView, proposalItems } from "./engine.js";

export { customerView, proposalItems };

export const ROOFING_SAMPLE_BOOK = {
  name: "Sample roofing rates (set to the roofer's before use)",
  version: "roof-sample-1",
  material_cost_per_square: { "architectural": 135, "3-tab": 110, "metal": 390 },
  accessories_cost_per_square: 35,   // underlayment, drip edge, vents, nails
  labor_cost_per_square: 95,         // install, per square on a walkable roof
  tearoff_cost_per_square_per_layer: 45,
  waste_pct: 0.10,                   // extra material ordered over measured squares
  pitch_factor: { "low": 1.0, "standard": 1.0, "steep": 1.2, "very-steep": 1.4 },
  story_factor: { "1": 1.0, "2": 1.1, "3": 1.25 },
  decking_cost_per_sheet: 75,
  dumpster_cost: 450,
  squares_per_dumpster: 25,
  markup: 1.45,
  minimum: 1500,
  range_pct: 0.10,
  valid_days: 30,
  terms: "Includes tear-off, disposal and cleanup. Rotten decking found beyond the estimate is billed per sheet at the quoted rate.",
};

const RATES = ["accessories_cost_per_square", "labor_cost_per_square", "tearoff_cost_per_square_per_layer",
               "waste_pct", "decking_cost_per_sheet", "dumpster_cost", "squares_per_dumpster",
               "markup", "minimum", "range_pct"];

export function checkRoofBook(book) {
  const missing = RATES.filter(k => typeof book[k] !== "number" || !Number.isFinite(book[k]));
  for (const t of ["material_cost_per_square", "pitch_factor", "story_factor"])
    for (const [k, v] of Object.entries(book[t] || {})) if (typeof v !== "number") missing.push(`${t}.${k}`);
  if (missing.length) throw new Error(`price book is missing: ${missing.join(", ")}`);
}

const round = (n, to) => Math.round(n / to) * to;

export function quoteRoof(job, book = ROOFING_SAMPLE_BOOK) {
  checkRoofBook(book);
  const j = { job: "replace", squares: 25, pitch: "standard", stories: "1", layers: 1,
              decking_sheets: 0, material: "architectural", ...job };
  j.stories = String(j.stories);
  const visit = [];
  if (j.job === "repair") visit.push("Repairs need someone on the roof before there's a price.");
  if (j.job === "insurance") visit.push("Insurance work follows the carrier's estimate, not this price book.");
  if (j.pitch === "very-steep" && j.stories === "3") visit.push("Very steep and three stories: check access and safety setup first.");
  for (const [k, table] of [["material", book.material_cost_per_square], ["pitch", book.pitch_factor], ["stories", book.story_factor]])
    if (!(j[k] in table)) throw new Error(`price book has no ${k} "${j[k]}"`);
  const sq = Number(j.squares);
  if (!(sq > 0)) throw new Error("squares must come from a measurement, not a guess");

  const factor = book.pitch_factor[j.pitch] * book.story_factor[j.stories];
  const ordered = sq * (1 + book.waste_pct);
  const lines = [
    { label: `Material, ${ordered.toFixed(1)} sq ${j.material}`, cost: ordered * book.material_cost_per_square[j.material], group: `New ${j.material} roof, materials` },
    { label: `Underlayment and accessories, ${ordered.toFixed(1)} sq`, cost: ordered * book.accessories_cost_per_square, group: `New ${j.material} roof, materials` },
    { label: `Install labor, ${sq} sq × ${factor.toFixed(2)}`, cost: sq * book.labor_cost_per_square * factor, group: "Installation" },
  ];
  const layers = Math.max(0, Number(j.layers) || 0);
  if (layers) lines.push({ label: `Tear-off, ${layers} layer${layers > 1 ? "s" : ""}`, cost: sq * layers * book.tearoff_cost_per_square_per_layer * factor, group: "Tear-off and disposal" });
  const decking = Math.max(0, Number(j.decking_sheets) || 0);
  if (decking) lines.push({ label: `Decking, ${decking} sheets`, cost: decking * book.decking_cost_per_sheet, group: `Decking replacement (${decking} sheets)` });
  const dumpsters = Math.max(1, Math.ceil((sq * Math.max(layers, 1)) / book.squares_per_dumpster));
  lines.push({ label: `Dumpster${dumpsters > 1 ? "s" : ""} × ${dumpsters}`, cost: dumpsters * book.dumpster_cost, group: "Tear-off and disposal" });

  const cost = lines.reduce((a, l) => a + l.cost, 0);
  const raw = cost * book.markup;
  const price = round(Math.max(raw, book.minimum), 25);
  return {
    book_version: book.version,
    needs_visit: visit.length > 0,
    visit_reasons: visit,
    lines: lines.map(l => ({ ...l, cost: Math.round(l.cost) })),
    cost: Math.round(cost),
    price,
    margin_pct: Math.round((1 - cost / price) * 100),
    minimum_applied: raw < book.minimum,
    low: round(price * (1 - book.range_pct), 50),
    high: round(price * (1 + book.range_pct), 50),
    valid_days: book.valid_days,
    terms: book.terms,
  };
}
