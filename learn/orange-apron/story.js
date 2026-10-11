/* The Orange Apron, trades edition: aisle progress, the cart and receipt, "Email me my receipt",
 * the embedded price-math calculator, and three D3 charts (sales climb, Nardelli years, stores vs sales per store).
 * Motion: opacity/transform only (tooltip fade, cart bump). */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- aisle progress ---------- */
  var nav = $("#aisleNav"), aisles = $$("section[data-aisle]");
  aisles.forEach(function (sec) {
    var n = sec.getAttribute("data-aisle"), a = document.createElement("a");
    var h = $("h2", sec), name = n === "17" ? "Checkout" : "Aisle " + n + ": " + (h ? h.textContent : "");
    a.href = "#" + sec.id; a.setAttribute("aria-label", name); a.title = name;
    a.innerHTML = "<span>" + (n === "17" ? "$" : n) + "</span>";
    nav.appendChild(a);
  });
  var links = $$("a", nav), visible = {};
  function paint() {
    var idx = -1;
    aisles.forEach(function (s, i) { if (visible[i]) idx = i; });
    if (idx < 0) { // fall back to the last section whose top has passed
      aisles.forEach(function (s, i) { if (s.getBoundingClientRect().top < innerHeight * 0.35) idx = i; });
    }
    links.forEach(function (a, i) { a.classList.toggle("here", i === idx); a.classList.toggle("done", idx >= 0 && i < idx); });
  }
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { visible[aisles.indexOf(e.target)] = e.isIntersecting; });
      paint();
    }, { rootMargin: "-35% 0px -60% 0px" });
    aisles.forEach(function (s) { io.observe(s); });
  }
  paint();

  /* ---------- cart + receipt ---------- */
  var KEY = "orange-apron-trades-cart";
  var CODES = (window.OA && window.OA.codes) || [];
  var tagsById = {};
  $$(".tag[data-id]").forEach(function (t) { tagsById[t.getAttribute("data-id")] = t; });
  var cart = [];
  try { cart = JSON.parse(localStorage.getItem(KEY) || "[]"); } catch (e) { cart = []; }
  cart = cart.filter(function (id) { return tagsById[id]; });
  function save() { try { localStorage.setItem(KEY, JSON.stringify(cart)); } catch (e) { /* private mode: cart lasts this visit */ } }
  function items() { return CODES.filter(function (id) { return cart.indexOf(id) >= 0; }); }
  function title(id) { return $("h4", tagsById[id]).textContent; }
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function render() {
    $$(".tag button[data-id]").forEach(function (b) {
      var on = cart.indexOf(b.getAttribute("data-id")) >= 0;
      b.setAttribute("aria-pressed", on ? "true" : "false");
      b.textContent = on ? "In your cart ✓" : "Add to cart";
    });
    $("#cartCount").textContent = cart.length;
    var list = items(), ds = "";
    try { ds = new Date().toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" }); } catch (e) { /* skip */ }
    $("#receipt").innerHTML = '<div class="head"><strong>The Orange Apron</strong><span>Trades edition · autoants</span><br><span>' + ds + "</span></div>" +
      (list.length ? "<ol>" + list.map(function (id) {
        return '<li><span class="code">A' + id.slice(0, 2) + "</span><span>" + esc(title(id)) + "</span></li>";
      }).join("") + '</ol><div class="tot"><span>Lessons</span><span>' + list.length + "</span></div>"
        : '<div class="empty">Your cart is empty. Add lessons from the shelf tags as you read, or start with the top five for trades.</div>') +
      '<div class="foot">Keep the values · Let the tactics go</div><div class="bars" aria-hidden="true"></div>';
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest(".tag button[data-id]") : null; if (!b) return;
    var id = b.getAttribute("data-id");
    cart = cart.indexOf(id) >= 0 ? cart.filter(function (x) { return x !== id; }) : cart.concat([id]);
    save(); render();
    var cb = $("#cartBtn"); cb.classList.remove("bump"); void cb.offsetWidth; if (!reduce) cb.classList.add("bump");
  });
  $("#cartBtn").addEventListener("click", function () { $("#checkout").scrollIntoView({ behavior: reduce ? "auto" : "smooth" }); });
  $("#clearBtn").addEventListener("click", function () { cart = []; save(); render(); });
  $("#fillBtn").addEventListener("click", function () {
    ((window.OA && window.OA.top) || []).forEach(function (id) { if (cart.indexOf(id) < 0 && tagsById[id]) cart.push(id); });
    save(); render();
  });
  function receiptText() {
    var list = items();
    return "The Orange Apron (trades edition): my lessons\n\n" +
      (list.length ? list.map(function (id) { return "A" + id.slice(0, 2) + "  " + title(id); }).join("\n") : "(empty cart)") +
      "\n\nhttps://autoants.com/learn/orange-apron/\nAn independent retelling inspired by Acquired, \"The Home Depot\" (2026).";
  }
  $("#copyBtn").addEventListener("click", function () {
    var msg = $("#copyMsg");
    var ok = function () { msg.textContent = "Copied to your clipboard."; };
    var fallback = function () {
      var r = document.createRange(); r.selectNodeContents($("#receipt"));
      var s = getSelection(); s.removeAllRanges(); s.addRange(r);
      msg.textContent = "Selected. Press Ctrl+C or ⌘C to copy.";
    };
    try { navigator.clipboard.writeText(receiptText()).then(ok, fallback); } catch (e) { fallback(); }
  });
  render();

  /* ---------- "Email me my receipt": the autoants-leads worker POST /subscribe ----------
   * Contract (tle-main workers/autoants-leads/index.js, handleSubscribe): JSON {email, segment, page, website}.
   * segment must be one of trades · sells-to-business · real-estate · other; page is cut to 60 chars of [a-z0-9#._/-].
   * The worker keeps a consent record (KV, sub:<time>) and pings Lane. It stores no other fields, so the cart rides in
   * `page` as one base-36 character per lesson, indexed into window.OA.codes (the lesson ids in page order):
   *   learn/orange-apron#r-<chars>   e.g. "#r-6fg" = OA.codes[6], OA.codes[15], OA.codes[16].
   * "Sent" shows only on a 200. */
  var SUBSCRIBE = "https://autoants-leads.saintdell.workers.dev/subscribe";
  function receiptCode() {
    return items().map(function (id) { return CODES.indexOf(id).toString(36); }).join("");
  }
  (function () {
    var f = $("#receiptForm"), note = $("#mailNote");
    function show(t, ok) { note.textContent = t; note.className = "sent " + (ok ? "ok" : "err"); }
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var email = f.email.value.trim();
      if (!items().length) { show("Your cart is empty. Add a lesson or two first.", false); return; }
      if (!/^[^\s@<>",]+@[^\s@<>",]+\.[a-z]{2,}$/i.test(email)) { show("Please check the email address.", false); return; }
      if (!f.ok.checked) { show("Tick the box to say yes first.", false); return; }
      var body = { email: email, segment: f.segment.value, page: ("learn/orange-apron#r-" + receiptCode()).slice(0, 60),
                   website: f.website ? f.website.value : "" };
      var btn = f.querySelector("button[type=submit]"); btn.disabled = true;
      fetch(SUBSCRIBE, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })
        .then(function (r) {
          if (r.status !== 200) throw new Error(String(r.status));
          show("Sent. Your receipt is on its way, and Permits Pulled arrives at the start of each month.", true);
          f.email.value = ""; f.ok.checked = false;
        })
        .catch(function () { show("That didn't go through. Check the email and try again in a minute.", false); })
        .then(function () { btn.disabled = false; });
    });
  })();

  /* ---------- the calculator (aisle 8) ---------- */
  if (window.PriceMath && $("#priceMath")) window.PriceMath.mount($("#priceMath"), { fullUrl: "../price-math/" });

  /* ---------- charts ---------- */
  if (!window.d3 || !window.HD) return;
  var d3 = window.d3, H = window.HD;
  var css = function (n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); };
  var A = H.annual.map(function (r) { var o = {}; H.annualCols.forEach(function (c, i) { o[c] = r[i]; }); return o; });
  var LW = H.lowes.map(function (r) { return { fy: r[0], sales: r[1] }; });
  var S = H.stock.map(function (r) { return { m: r[0], hd: r[1], low: r[2], sptr: r[3] }; });
  var money = function (v) {
    return v == null ? "n/a" : (v >= 1000 ? "$" + (v / 1000).toFixed(v >= 100000 ? 0 : 1) + "B" : (v >= 100 ? "$" + Math.round(v) + "M" : "$" + v.toFixed(1) + "M"));
  };
  function colors() {
    return { o: css("--hd"), b: css("--lowes"), m: css("--market"), ink: css("--text"), g: css("--graphite"), f: css("--soft"),
             r: css("--rule"), p2: css("--paper-2"), paper: css("--paper") };
  }
  function frame(fig, ratio, mob) {
    var wrap = $(".svgwrap", fig), svg = d3.select($("svg", wrap)), W = Math.max(300, wrap.clientWidth);
    var Hh = Math.round(W < 560 ? (mob || ratio * 1.35) * W : ratio * W);
    svg.attr("viewBox", "0 0 " + W + " " + Hh).attr("width", W).attr("height", Hh); svg.selectAll("*").remove();
    return { svg: svg, W: W, H: Hh, wrap: wrap, tip: $(".tip", wrap), small: W < 560 };
  }
  function showTip(tip, html, x, y, wrapW) {
    tip.innerHTML = html;
    var w = tip.offsetWidth, left = Math.max(0, Math.min(wrapW - w, x - w / 2));
    tip.style.transform = "translate(" + Math.round(left) + "px," + Math.round(y - tip.offsetHeight - 12) + "px)";
    tip.classList.add("on");
  }
  function hideTip(tip) { tip.classList.remove("on"); }
  function axisStyle(g, c) { g.selectAll("path").remove(); g.selectAll("line").attr("stroke", c.r); g.selectAll("text").attr("fill", c.g); }

  /* 1. the climb */
  var climbScale = "log";
  var ERAS = [["Marcus", 1979, 1996.5], ["Blank", 1996.5, 2000.5], ["Nardelli", 2000.5, 2006.5], ["Blake", 2006.5, 2014.5], ["Menear", 2014.5, 2021.5], ["Decker", 2021.5, 2025.5]];
  function drawClimb() {
    var fig = $("#climb"); if (!fig) return;
    var F = frame(fig, 0.48, 0.8), svg = F.svg, W = F.W, Hh = F.H, c = colors(), small = F.small;
    var m = { t: 28, r: small ? 46 : 64, b: 28, l: small ? 42 : 52 };
    var x = d3.scaleLinear([1979, 2025], [m.l, W - m.r]);
    var y = climbScale === "log" ? d3.scaleLog([5, 200000], [Hh - m.b, m.t]) : d3.scaleLinear([0, 180000], [Hh - m.b, m.t]);
    ERAS.forEach(function (e, i) {
      svg.append("rect").attr("x", x(e[1])).attr("y", m.t - 14).attr("width", x(e[2]) - x(e[1])).attr("height", Hh - m.b - m.t + 14).attr("fill", i % 2 ? c.p2 : "transparent");
      if (!small || x(e[2]) - x(e[1]) > 34) svg.append("text").attr("x", x(e[1]) + 4).attr("y", m.t - 3).text(e[0].toUpperCase()).attr("font-size", small ? 9 : 10).attr("fill", c.f).attr("letter-spacing", ".06em");
    });
    var yt = climbScale === "log" ? [10, 100, 1000, 10000, 100000] : [0, 50000, 100000, 150000];
    var gy = svg.append("g").attr("transform", "translate(" + m.l + ",0)").call(d3.axisLeft(y).tickValues(yt).tickFormat(money).tickSize(-(W - m.l - m.r)));
    axisStyle(gy, c); gy.selectAll("line").attr("stroke-dasharray", "2 3");
    var gx = svg.append("g").attr("transform", "translate(0," + (Hh - m.b) + ")").call(d3.axisBottom(x).tickValues(small ? [1980, 1995, 2010, 2025] : [1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025]).tickFormat(d3.format("d")).tickSize(0).tickPadding(8));
    axisStyle(gx, c);
    var line = d3.line().x(function (d) { return x(d.fy); }).y(function (d) { return y(d.v); }).curve(d3.curveMonotoneX);
    var hd = A.map(function (d) { return { fy: d.fy, v: d.sales }; }), lw = LW.filter(function (d) { return d.sales; }).map(function (d) { return { fy: d.fy, v: d.sales }; });
    svg.append("path").datum(lw).attr("d", line).attr("fill", "none").attr("stroke", c.b).attr("stroke-width", 2);
    svg.append("path").datum(hd).attr("d", line).attr("fill", "none").attr("stroke", c.o).attr("stroke-width", 3).attr("stroke-linecap", "round");
    var last = hd[hd.length - 1]; svg.append("text").attr("x", x(last.fy) + 6).attr("y", y(last.v) + 4).text(money(last.v)).attr("fill", c.o).attr("font-weight", 700);
    var ll = lw[lw.length - 1]; svg.append("text").attr("x", x(ll.fy) + 6).attr("y", y(ll.v) + (climbScale === "log" ? 14 : 4)).text(money(ll.v)).attr("fill", c.b).attr("font-weight", 700);
    var notes = [[1989, "Passes Lowe's", -1], [1981, "IPO", -1]].concat(small ? [] : [[2007, "Sells HD Supply", 1], [2020, "COVID surge", -1]]);
    notes.forEach(function (n) {
      var d = A.filter(function (a) { return a.fy === n[0]; })[0]; if (!d) return;
      var px = x(n[0]), py = y(d.sales), oy = n[2] < 0 ? -26 : 26;
      svg.append("line").attr("x1", px).attr("x2", px).attr("y1", py + (n[2] < 0 ? -5 : 5)).attr("y2", py + oy).attr("stroke", c.g);
      svg.append("text").attr("x", px).attr("y", py + oy + (n[2] < 0 ? -4 : 12)).attr("text-anchor", n[0] > 2015 ? "end" : "middle").text(n[1]).attr("fill", c.ink).attr("font-size", small ? 10 : 12);
    });
    var rule = svg.append("line").attr("y1", m.t).attr("y2", Hh - m.b).attr("stroke", c.ink).attr("opacity", 0);
    var dot = svg.append("circle").attr("r", 4.5).attr("fill", c.o).attr("stroke", c.paper).attr("stroke-width", 2).attr("opacity", 0);
    svg.append("rect").attr("x", m.l).attr("y", m.t).attr("width", W - m.l - m.r).attr("height", Hh - m.t - m.b).attr("fill", "transparent").style("cursor", "crosshair")
      .on("pointermove", function (ev) {
        var fy = Math.round(x.invert(d3.pointer(ev)[0])), d = A.filter(function (a) { return a.fy === fy; })[0]; if (!d) return;
        var lo = LW.filter(function (l) { return l.fy === fy; })[0];
        rule.attr("x1", x(fy)).attr("x2", x(fy)).attr("opacity", 0.35); dot.attr("cx", x(fy)).attr("cy", y(d.sales)).attr("opacity", 1);
        var k = F.wrap.clientWidth / W;
        showTip(F.tip, "<b>Fiscal " + fy + "</b><br>Sales " + money(d.sales) + " · " + d.stores.toLocaleString() + " stores" +
          (lo && lo.sales ? '<br><span style="color:' + c.b + '">Lowe\'s ' + money(lo.sales) + "</span>" : ""), x(fy) * k, y(d.sales) * k, F.wrap.clientWidth);
      })
      .on("pointerleave", function () { hideTip(F.tip); rule.attr("opacity", 0); dot.attr("opacity", 0); });
  }
  $$("#climb .seg button").forEach(function (b) {
    b.addEventListener("click", function () {
      climbScale = b.getAttribute("data-scale");
      $$("#climb .seg button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      drawClimb();
    });
  });

  /* 2. the Nardelli years: growth of $100, anchored to the exact daily-close endpoints */
  function drawNardelli() {
    var fig = $("#nardelli"); if (!fig) return;
    var F = frame(fig, 0.42, 0.75), svg = F.svg, W = F.W, Hh = F.H, c = colors(), small = F.small;
    var era = H.eras.filter(function (e) { return e.era === "Nardelli"; })[0];
    var tr = { hd: era.hd_pct, low: era.low_pct, sptr: era.sp500_total_return_pct };
    var rows = S.filter(function (r) { return r.m >= "2000-11" && r.m <= "2006-12" && r.hd && r.low && r.sptr; });
    var b = rows[0], z = rows[rows.length - 1];
    var ser = function (k) {
      var scale = (1 + tr[k] / 100) / (z[k] / b[k]);
      return [{ d: new Date("2000-12-04"), v: 100 }].concat(rows.slice(1).map(function (r) {
        return { d: new Date(r.m === "2006-12" ? "2006-12-29" : r.m + "-28"), v: 100 * (r[k] / b[k]) * scale };
      }));
    };
    var H1 = ser("hd"), L1 = ser("low"), S1 = ser("sptr");
    var m = { t: 16, r: small ? 52 : 96, b: 28, l: 40 };
    var x = d3.scaleTime([H1[0].d, H1[H1.length - 1].d], [m.l, W - m.r]);
    var y = d3.scaleLinear([40, d3.max(L1, function (d) { return d.v; }) * 1.05], [Hh - m.b, m.t]).nice();
    var gy = svg.append("g").attr("transform", "translate(" + m.l + ",0)").call(d3.axisLeft(y).ticks(5).tickFormat(function (v) { return "$" + v; }).tickSize(-(W - m.l - m.r)));
    axisStyle(gy, c); gy.selectAll("line").attr("stroke-dasharray", "2 3");
    svg.append("line").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(100)).attr("y2", y(100)).attr("stroke", c.ink);
    var gx = svg.append("g").attr("transform", "translate(0," + (Hh - m.b) + ")").call(d3.axisBottom(x).ticks(small ? 4 : 7).tickSize(0).tickPadding(8));
    axisStyle(gx, c);
    var line = d3.line().x(function (d) { return x(d.d); }).y(function (d) { return y(d.v); }).curve(d3.curveMonotoneX);
    [[S1, c.m, 2], [L1, c.b, 2.2], [H1, c.o, 3]].forEach(function (s) { svg.append("path").datum(s[0]).attr("d", line).attr("fill", "none").attr("stroke", s[1]).attr("stroke-width", s[2]); });
    var endLabel = function (d, col, name, dy) { var e = d[d.length - 1]; svg.append("text").attr("x", x(e.d) + 6).attr("y", y(e.v) + 4 + dy).attr("fill", col).attr("font-weight", 700).text(small ? "$" + Math.round(e.v) : name + " $" + Math.round(e.v)); };
    endLabel(L1, c.b, "Lowe's", 0); endLabel(S1, c.m, "S&P", -6); endLabel(H1, c.o, "HD", 10);
    var meet = new Date("2006-05-25");
    svg.append("line").attr("x1", x(meet)).attr("x2", x(meet)).attr("y1", m.t + 18).attr("y2", Hh - m.b).attr("stroke", c.g).attr("stroke-dasharray", "3 3");
    svg.append("text").attr("x", x(meet) - 4).attr("y", m.t + 12).attr("text-anchor", "end").attr("fill", c.ink).attr("font-size", small ? 10 : 12).text("Wilmington meeting");
    var rule = svg.append("line").attr("y1", m.t).attr("y2", Hh - m.b).attr("stroke", c.ink).attr("opacity", 0);
    svg.append("rect").attr("x", m.l).attr("y", m.t).attr("width", W - m.l - m.r).attr("height", Hh - m.t - m.b).attr("fill", "transparent")
      .on("pointermove", function (ev) {
        var t = x.invert(d3.pointer(ev)[0]), i = d3.bisector(function (d) { return d.d; }).center(H1, t);
        var h = H1[i], l = L1[i], s = S1[i]; rule.attr("x1", x(h.d)).attr("x2", x(h.d)).attr("opacity", 0.3);
        var k = F.wrap.clientWidth / W;
        showTip(F.tip, "<b>" + d3.timeFormat("%b %Y")(h.d) + '</b><br><span style="color:' + c.o + '">Home Depot $' + h.v.toFixed(0) +
          '</span><br><span style="color:' + c.b + '">Lowe\'s $' + l.v.toFixed(0) + "</span><br>S&amp;P 500 $" + s.v.toFixed(0),
          x(h.d) * k, y(Math.max(h.v, l.v)) * k, F.wrap.clientWidth);
      })
      .on("pointerleave", function () { hideTip(F.tip); rule.attr("opacity", 0); });
  }

  /* 3. stores vs sales per store */
  function drawStores() {
    var fig = $("#stores"); if (!fig) return;
    var F = frame(fig, 0.42, 1.05), svg = F.svg, W = F.W, Hh = F.H, c = colors(), small = F.small;
    var rows = A.filter(function (d) { return d.fy >= 1990; }).map(function (d) { return { fy: d.fy, stores: d.stores, sps: d.sales / d.stores }; });
    var gap = small ? 36 : 48, pw = small ? W - 56 : (W - 56 - gap) / 2, ph = small ? (Hh - 90) / 2 : Hh - 60;
    var panels = [
      { k: "stores", t: "Stores at year-end", fmt: function (v) { return v.toLocaleString(); }, x0: 44, y0: 24 },
      { k: "sps", t: "Sales per store", fmt: function (v) { return "$" + v.toFixed(0) + "M"; }, x0: small ? 44 : 44 + pw + gap, y0: small ? 24 + ph + 50 : 24 }
    ];
    var find = function (fy) { return rows.filter(function (r) { return r.fy === fy; })[0]; };
    panels.forEach(function (P) {
      var g = svg.append("g").attr("transform", "translate(" + P.x0 + "," + P.y0 + ")");
      var x = d3.scaleBand(rows.map(function (r) { return r.fy; }), [0, pw]).padding(0.18);
      var y = d3.scaleLinear([0, d3.max(rows, function (r) { return r[P.k]; }) * 1.08], [ph, 0]).nice();
      var bx = d3.scaleLinear([1990, 2025], [x(1990) + x.bandwidth() / 2, x(2025) + x.bandwidth() / 2]);
      g.append("rect").attr("x", bx(2006.5)).attr("width", bx(2014.5) - bx(2006.5)).attr("y", -6).attr("height", ph + 6).attr("fill", c.p2);
      g.append("text").attr("x", bx(2006.5) + 4).attr("y", 8).text("BLAKE").attr("font-size", 10).attr("fill", c.f).attr("letter-spacing", ".08em");
      var gy = g.append("g").call(d3.axisLeft(y).ticks(4).tickFormat(P.fmt).tickSize(-pw)); axisStyle(gy, c); gy.selectAll("line").attr("stroke-dasharray", "2 3");
      var gx = g.append("g").attr("transform", "translate(0," + ph + ")").call(d3.axisBottom(x).tickValues([1990, 2000, 2010, 2020]).tickSize(0).tickPadding(6)); axisStyle(gx, c);
      g.append("text").attr("x", 0).attr("y", -10).text(P.t).attr("fill", c.ink).attr("font-weight", 700).attr("font-size", 13);
      if (P.k === "stores") {
        var blake = function (d) { return d.fy >= 2007 && d.fy <= 2014; };
        g.selectAll("rect.b").data(rows).join("rect").attr("class", "b").attr("x", function (d) { return x(d.fy); }).attr("width", x.bandwidth())
          .attr("y", function (d) { return y(d.stores); }).attr("height", function (d) { return ph - y(d.stores); })
          .attr("fill", function (d) { return blake(d) ? c.o : c.g; }).attr("opacity", function (d) { return blake(d) ? 1 : 0.5; });
      } else {
        var ln = d3.line().x(function (d) { return bx(d.fy); }).y(function (d) { return y(d.sps); }).curve(d3.curveMonotoneX);
        g.append("path").datum(rows.filter(function (d) { return d.fy <= 2019; })).attr("d", ln).attr("fill", "none").attr("stroke", c.o).attr("stroke-width", 2.6);
        g.append("path").datum(rows.filter(function (d) { return d.fy >= 2019; })).attr("d", ln).attr("fill", "none").attr("stroke", c.o).attr("stroke-width", 2.6).attr("stroke-dasharray", "2 4");
        var d06 = find(2006); g.append("circle").attr("cx", bx(2006)).attr("cy", y(d06.sps)).attr("r", 4).attr("fill", c.paper).attr("stroke", c.o).attr("stroke-width", 2);
        [[2009, 16], [2019, -9]].forEach(function (p) {
          var d = find(p[0]);
          g.append("circle").attr("cx", bx(p[0])).attr("cy", y(d.sps)).attr("r", 3.5).attr("fill", c.o);
          g.append("text").attr("x", bx(p[0])).attr("y", y(d.sps) + p[1]).attr("text-anchor", "middle").text("$" + d.sps.toFixed(0) + "M").attr("fill", c.ink).attr("font-weight", 700);
        });
      }
      g.append("rect").attr("width", pw).attr("height", ph).attr("fill", "transparent")
        .on("pointermove", function (ev) {
          var fy = Math.round(bx.invert(d3.pointer(ev)[0])), d = find(fy); if (!d) return;
          var k = F.wrap.clientWidth / W;
          showTip(F.tip, "<b>Fiscal " + fy + "</b><br>" + d.stores.toLocaleString() + " stores<br>$" + d.sps.toFixed(1) + "M sales per store",
            (P.x0 + bx(fy)) * k, (P.y0 + y(d[P.k])) * k, F.wrap.clientWidth);
        })
        .on("pointerleave", function () { hideTip(F.tip); });
    });
  }

  function drawAll() {
    [drawClimb, drawNardelli, drawStores].forEach(function (f) { try { f(); } catch (e) { if (window.console) console.error(e); } });
  }
  drawAll();
  var rt, lastW = innerWidth;
  addEventListener("resize", function () {
    if (Math.abs(innerWidth - lastW) < 8) return; // ignore mobile URL-bar height changes
    lastW = innerWidth; clearTimeout(rt); rt = setTimeout(drawAll, 150);
  });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(drawAll);
})();
