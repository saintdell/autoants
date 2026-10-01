// Card check: how much a business leaves on the table with the card it uses now.
//
// Rewards math only, from a dated table of card terms (cards.json, each card with the
// issuer page it was checked on). It is not financial advice and it never sees a card
// number, a statement or a bank login: the owner gives rough monthly spend by category.
//
// Three honesty rules are enforced here, not in the copy:
//   1. Pays in full or nothing. Carrying a balance at 20%+ APR wipes out 1-2% rewards
//      many times over, so the check stops and says so.
//   2. Surcharges count. A supplier that adds 3% for card payments turns a 2% card into
//      a 1% loss; that spend goes to check/ACH and earns nothing.
//   3. Recurring money only. Sign-up bonuses are excluded: the number is what the setup
//      earns every year, not once.

export const CATEGORIES = {
  materials_home_improvement: "Materials (Home Depot, Lowe's, supply yards)",
  fuel: "Fuel",
  equipment_rental: "Equipment rental and parts",
  insurance: "Insurance",
  internet_cable_phone: "Phone and internet",
  advertising_online: "Online ads (Google, Facebook)",
  software_cloud: "Software",
  office_supplies: "Office supplies",
  shipping: "Shipping",
  restaurants: "Restaurants",
  travel: "Travel",
  utilities: "Utilities",
  other: "Everything else",
};

const round = n => Math.round(n);

// One card's earning rules, normalized: [{categories, rate, cap, after}], base rate, value per point.
// Rules with the same cap_id draw on one shared cap (Bank of America's 3% and 2% share
// $50k). A top_n rule earns only on the owner's n biggest categories among `of` (Amex Gold).
function rulesOf(card, spendYear = {}) {
  const pools = {};
  return (card.rules || []).map((r, i) => {
    let cats = r.categories;
    if (r.top_n) cats = [...r.of].sort((a, b) => (spendYear[b] || 0) - (spendYear[a] || 0)).slice(0, r.top_n);
    const id = r.cap_id || `rule${i}`;
    pools[id] = pools[id] || { left: r.cap_amount ?? Infinity };
    return { categories: cats, rate: r.rate, pool: pools[id] };
  });
}

// Allocate a year of spend across a set of cards: each dollar goes to the best rate still
// available for its category (respecting combined caps), net of any surcharge.
export function allocate(spendYear, cards, surcharge = {}) {
  const books = cards.map(c => ({ card: c, rules: rulesOf(c, spendYear), pv: c.point_value ?? 0.01 }));
  const lines = [];
  // Highest-spend categories first, so the biggest dollars claim the capped bonus rates.
  const cats = Object.entries(spendYear).filter(([, v]) => v > 0).sort((a, b) => b[1] - a[1]);
  for (const [cat, amount] of cats) {
    let remaining = amount;
    const sur = surcharge[cat] || 0;
    while (remaining > 0.005) {
      let best = null;
      for (const b of books) {
        for (const r of b.rules) {
          if (!r.categories.includes(cat) || r.pool.left <= 0) continue;
          const v = r.rate * b.pv;
          if (!best || v > best.v) best = { b, r, v, room: r.pool.left };
        }
        const base = b.card.base_rate * b.pv;
        if (!best || base > best.v) best = { b, r: null, v: base, room: Infinity };
      }
      const take = Math.min(remaining, best.room);
      const net = best.v - sur;
      if (net <= 0) {
        lines.push({ category: cat, amount: remaining, card: null, rate: 0, earned: 0,
                     note: sur ? `supplier adds ${(sur * 100).toFixed(1)}% for cards: pay by check or ACH` : "" });
        break;
      }
      lines.push({ category: cat, amount: take, card: best.b.card.id, rate: net, earned: take * net });
      if (best.r) best.r.pool.left -= take;
      remaining -= take;
    }
  }
  const fees = cards.reduce((a, c) => a + (c.annual_fee || 0), 0);
  const earned = lines.reduce((a, l) => a + l.earned, 0);
  return { cards: cards.map(c => c.id), lines, earned: round(earned), fees, net: round(earned - fees) };
}

export function check({ monthlySpend, paysInFull, currentCardId = "none", surcharge = {}, table, maxCards = 2 }) {
  if (!paysInFull) {
    return { stop: true, message: "Pay the balance down first. Card interest runs 20% or more a year, and no rewards card earns anywhere close to that. A rewards card only helps a business that pays in full every month." };
  }
  const spendYear = Object.fromEntries(Object.entries(monthlySpend).map(([k, v]) => [k, (Number(v) || 0) * 12]));
  const total = Object.values(spendYear).reduce((a, b) => a + b, 0);
  const cards = table.cards.filter(c => c.open !== false);
  const byId = Object.fromEntries(cards.map(c => [c.id, c]));
  const current = byId[currentCardId] ? allocate(spendYear, [byId[currentCardId]], surcharge)
                                      : { cards: [], lines: [], earned: 0, fees: 0, net: 0 };
  let bestOne = null, bestTwo = null;
  for (const c of cards) {
    const r = allocate(spendYear, [c], surcharge);
    if (!bestOne || r.net > bestOne.net) bestOne = r;
  }
  if (maxCards >= 2) {
    for (let i = 0; i < cards.length; i++) for (let j = i + 1; j < cards.length; j++) {
      const r = allocate(spendYear, [cards[i], cards[j]], surcharge);
      if (!bestTwo || r.net > bestTwo.net) bestTwo = r;
    }
  }
  // A second card has to earn its keep: worth it only if it adds $250+/yr over the best single card.
  const recommended = bestTwo && bestTwo.net - bestOne.net >= 250 ? bestTwo : bestOne;
  return { stop: false, annual_spend: round(total), checked_on: table.checked_on, current, best_one: bestOne,
           best_two: bestTwo, recommended, gain: recommended.net - current.net,
           names: Object.fromEntries(cards.map(c => [c.id, c.name])) };
}
