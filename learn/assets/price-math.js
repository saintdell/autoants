/* Price math: a margin-dollars calculator for trades owners. Used on /learn/price-math/ and embedded in
 * /learn/orange-apron/ (aisle 8). Plain JS + inline SVG, no libraries, nothing leaves the browser.
 *
 *   PriceMath.mount(el, { syncUrl: true })            full page: inputs live in the URL query, so a link shares them
 *   PriceMath.mount(el, { fullUrl: "/learn/price-math/" })   embed: shows an "Open the full calculator" link instead
 *
 * The math (all monthly):
 *   margin per job       = average job × gross margin            (cost per job = average job × (1 − margin))
 *   a price change of p  : new price = job × (1 + p); cost per job unchanged, so margin per job = job × (margin + p)
 *   jobs to keep margin $ = jobs × margin / (margin + p)
 *   faster quotes        : extra jobs = quotes × (close-rate gain in points / 100), close rate capped at 100%
 *   fewer missed calls   : extra jobs = calls × unanswered share × share you catch × share of those that book
 *   with the change      : jobs' = jobs + extra jobs; margin $ = jobs' × job × (margin + p)
 *   break-even jobs      = overhead / margin per job
 * Every number shown is arithmetic on the visitor's own inputs ("from your numbers"); the levers are their guesses.
 * The defaults are an example shop for the visitor to overwrite, not industry statistics.
 */
(function () {
  "use strict";
  var FIELDS = [
    // key, label, prefix, suffix, default, min, max, step
    ["job", "Average job", "$", "", 850, 1, 1000000, 1],
    ["jobs", "Jobs a month", "", "", 45, 0, 10000, 1],
    ["gm", "Gross margin", "", "%", 45, 1, 95, 0.5],
    ["oh", "Monthly overhead", "$", "", 14000, 0, 100000000, 100],
    ["q", "Quotes sent a month", "", "", 70, 0, 100000, 1],
    ["cr", "Close rate on quotes", "", "%", 35, 0, 100, 1],
    ["calls", "Calls a month", "", "", 260, 0, 1000000, 1],
    ["miss", "Calls that go unanswered", "", "%", 25, 0, 100, 1]
  ];
  var LEVERS = [
    ["price", -5, -30, 30, 1],
    ["qx", 5, 0, 30, 1],
    ["rec", 40, 0, 100, 5],
    ["book", 30, 0, 100, 5]
  ];
  var DEFAULTS = {};
  FIELDS.forEach(function (f) { DEFAULTS[f[0]] = f[4]; });
  LEVERS.forEach(function (l) { DEFAULTS[l[0]] = l[1]; });
  var LIMITS = {};
  FIELDS.forEach(function (f) { LIMITS[f[0]] = [f[5], f[6]]; });
  LEVERS.forEach(function (l) { LIMITS[l[0]] = [l[2], l[3]]; });

  var nInst = 0;
  function clamp(k, v) {
    v = Number(v);
    if (!isFinite(v)) v = DEFAULTS[k];
    return Math.min(LIMITS[k][1], Math.max(LIMITS[k][0], v));
  }
  function money(v) {
    var r = Math.round(Math.abs(v));
    return (v < -0.5 ? "−$" : "$") + r.toLocaleString("en-US");
  }
  function signed(v) { return Math.abs(v) < 0.5 ? "$0" : (v > 0 ? "+" : "") + money(v); }
  function jobsFmt(v) {
    var r = Math.round(v * 10) / 10;
    return (r < 0 ? "−" : "") + Math.abs(r).toLocaleString("en-US", { maximumFractionDigits: 1 });
  }
  function jobsSigned(v) { var r = Math.round(v * 10) / 10; return r === 0 ? "0" : (r > 0 ? "+" : "") + jobsFmt(r); }
  function pctFmt(v) { var r = Math.round(v * 10) / 10; return (r < 0 ? "−" : "") + Math.abs(r) + "%"; }

  /* The model. s = state with percents as whole numbers. Returns everything the ledger and chart need. */
  function compute(s) {
    var g = s.gm / 100, p = s.price / 100, A = s.job, J = s.jobs, O = s.oh;
    var mNow = A * g, mNew = A * (g + p);
    var closeNew = Math.min(100, s.cr + s.qx);
    var dq = s.q * (closeNew - s.cr) / 100;
    var missed = s.calls * s.miss / 100;
    var dc = missed * (s.rec / 100) * (s.book / 100);
    var Js = J + dq + dc;
    var r = {
      g: g, p: p, A: A, As: A * (1 + p), J: J, Js: Js, dq: dq, dc: dc, missed: missed, closeNew: closeNew,
      R0: J * A, Rs: Js * A * (1 + p),
      gs: (1 + p) > 0 ? (g + p) / (1 + p) : NaN,
      M0: J * mNow, Ms: Js * mNew, O: O,
      mNow: mNow, mNew: mNew,
      stepPrice: J * A * p, stepQuotes: dq * mNew, stepCalls: dc * mNew
    };
    r.P0 = r.M0 - O; r.Ps = r.Ms - O; r.dM = r.Ms - r.M0;
    r.BE0 = mNow > 0 ? O / mNow : Infinity;
    r.BEs = mNew > 0 ? O / mNew : Infinity;
    r.keepJobs = mNew > 0 ? J * mNow / mNew : Infinity;
    return r;
  }

  function el(tag, attrs, html) {
    var e = document.createElement(tag);
    if (attrs) for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (html != null) e.innerHTML = html;
    return e;
  }

  function mount(root, opts) {
    opts = opts || {};
    var id = "pm" + (++nInst), state = {};
    Object.keys(DEFAULTS).forEach(function (k) { state[k] = DEFAULTS[k]; });
    if (opts.syncUrl) {
      try {
        var qs = new URLSearchParams(location.search);
        Object.keys(DEFAULTS).forEach(function (k) { if (qs.has(k) && qs.get(k) !== "") state[k] = clamp(k, qs.get(k)); });
      } catch (e) { /* old browser: defaults */ }
    }

    var fieldsHtml = FIELDS.map(function (f) {
      var k = f[0];
      return '<div class="pm-field"><label for="' + id + k + '">' + f[1] + '</label><div class="pm-in">' +
        (f[2] ? '<span aria-hidden="true">' + f[2] + '</span>' : '') +
        '<input id="' + id + k + '" data-k="' + k + '" type="number" inputmode="decimal" min="' + f[5] + '" max="' + f[6] + '" step="' + f[7] + '" value="' + state[k] + '">' +
        (f[3] ? '<span class="after" aria-hidden="true">' + f[3] + '</span>' : '') + '</div></div>';
    }).join("");
    function range(k, label, guess) {
      var L = LIMITS[k], step = LEVERS.filter(function (l) { return l[0] === k; })[0][4];
      return '<div class="pm-range"><label for="' + id + k + '">' + label + (guess ? '<em>your guess</em>' : '') + '</label>' +
        '<input id="' + id + k + '" data-k="' + k + '" type="range" min="' + L[0] + '" max="' + L[1] + '" step="' + step + '" value="' + state[k] + '">' +
        '<output id="' + id + k + 'o" for="' + id + k + '"></output></div>';
    }

    root.classList.add("pm");
    root.innerHTML =
      '<div class="pm-grid">' +
        '<fieldset><legend>Your shop today</legend><div class="pm-fields">' + fieldsHtml + '</div></fieldset>' +
        '<fieldset><legend>Try a change</legend>' +
          '<div class="pm-lever"><h4><b>01</b>Change your price</h4><p class="hint">A cut or a raise on every job. Your cost per job stays the same.</p>' +
            range("price", "Price change") + '<p class="pm-keep" id="' + id + 'keep"></p></div>' +
          '<div class="pm-lever"><h4><b>02</b>Quote faster</h4><p class="hint">If quotes went out sooner, how many more points of your quotes would close?</p>' +
            range("qx", "Close rate goes up by", true) + '</div>' +
          '<div class="pm-lever"><h4><b>03</b>Miss fewer calls</h4><p class="hint">Of the calls that go unanswered today, how many would you catch, and how many of those become jobs?</p>' +
            range("rec", "Unanswered calls you catch", true) + range("book", "Caught calls that become jobs", true) + '</div>' +
        '</fieldset>' +
      '</div>' +
      '<div class="pm-out">' +
        '<div><p class="pm-from">From your numbers</p>' +
          '<table class="pm-ledger"><caption class="sr">Your month now and after the change, from the numbers you entered</caption>' +
          '<thead><tr><th scope="col">Per month</th><th scope="col">Now</th><th scope="col">After</th><th scope="col">Change</th></tr></thead>' +
          '<tbody id="' + id + 'body"></tbody></table>' +
          '<p class="pm-verdict" id="' + id + 'verdict" aria-live="polite"></p></div>' +
        '<figure class="pm-chart" style="margin:0"><h4>Where the margin dollars move</h4>' +
          '<p>Monthly margin dollars, drawn to scale from $0. The dashed line is your overhead: above it you make money.</p>' +
          '<p class="pm-ohl"><i aria-hidden="true"></i><span id="' + id + 'ohl"></span></p>' +
          '<div class="pm-svg" id="' + id + 'svg"></div></figure>' +
      '</div>' +
      '<div class="pm-actions">' +
        (opts.syncUrl ? '<button type="button" data-act="copy">Copy a link to these numbers</button>' :
          '<a id="' + id + 'full" href="' + (opts.fullUrl || "/learn/price-math/") + '">Open the full calculator</a>') +
        '<button type="button" data-act="reset">Reset to the example</button><span class="msg" id="' + id + 'msg" role="status"></span>' +
      '</div>' +
      '<p class="pm-note">This is arithmetic on the numbers you typed. It is not a forecast, and it is not a promise of what autoants or anyone else will deliver. ' +
      'It assumes your cost per job stays the same when the price moves, and that new jobs look like your average job. The starting numbers are an example shop; replace them with yours.</p>';

    var $ = function (s) { return root.querySelector(s); };
    var inputs = root.querySelectorAll("input[data-k]");

    function query() {
      var qs = new URLSearchParams();
      Object.keys(DEFAULTS).forEach(function (k) { qs.set(k, String(state[k])); });
      return qs.toString();
    }
    var urlTimer;
    function syncUrl() {
      if (!opts.syncUrl || !history.replaceState) return;
      clearTimeout(urlTimer);
      urlTimer = setTimeout(function () {
        try { history.replaceState(null, "", location.pathname + "?" + query() + location.hash); } catch (e) { /* ignore */ }
      }, 250);
    }

    function row(label, a, b, c, cls, cCls) {
      return '<tr' + (cls ? ' class="' + cls + '"' : '') + '><td>' + label + '</td><td>' + a + '</td><td>' + b + '</td><td' + (cCls ? ' class="' + cCls + '"' : '') + '>' + c + '</td></tr>';
    }
    function dir(v) { return v > 0.5 ? "up" : (v < -0.5 ? "down" : ""); }

    function render() {
      var r = compute(state);
      $("#" + id + "priceo").textContent = (state.price > 0 ? "+" : "") + pctFmt(state.price);
      $("#" + id + "qxo").textContent = "+" + state.qx + " pts";
      $("#" + id + "reco").textContent = state.rec + "%";
      $("#" + id + "booko").textContent = state.book + "%";

      var keep = $("#" + id + "keep");
      if (r.mNew <= 0) keep.innerHTML = "At that price every job loses money: the price no longer covers your cost per job.";
      else if (state.price === 0) keep.innerHTML = "No price change. Move the slider to see how many jobs a cut or a raise needs.";
      else keep.innerHTML = "To keep today's margin dollars at " + pctFmt(state.price) + " you need <b>" + jobsFmt(r.keepJobs) + " jobs a month</b> (" + jobsSigned(r.keepJobs - r.J) + ").";

      var be = function (v) { return isFinite(v) ? jobsFmt(v) : "never"; };
      $("#" + id + "body").innerHTML =
        row("Jobs", jobsFmt(r.J), jobsFmt(r.Js), jobsSigned(r.Js - r.J), "", dir(r.Js - r.J)) +
        row("Average job", money(r.A), money(r.As), signed(r.As - r.A), "", dir(r.As - r.A)) +
        row("Revenue", money(r.R0), money(r.Rs), signed(r.Rs - r.R0), "", dir(r.Rs - r.R0)) +
        row("Gross margin", pctFmt(r.g * 100), isFinite(r.gs) ? pctFmt(r.gs * 100) : "n/a", isFinite(r.gs) ? (r.gs - r.g >= 0 ? "+" : "") + pctFmt((r.gs - r.g) * 100).replace(/%$/, " pts") : "") +
        row("Margin dollars", money(r.M0), money(r.Ms), signed(r.dM), "key", dir(r.dM)) +
        row("Overhead", money(r.O), money(r.O), "") +
        row("Left after overhead", money(r.P0), money(r.Ps), signed(r.Ps - r.P0), "", dir(r.Ps - r.P0)) +
        row("Break-even jobs", be(r.BE0), be(r.BEs), isFinite(r.BE0) && isFinite(r.BEs) ? jobsSigned(r.BEs - r.BE0) : "");

      var v;
      if (r.mNew <= 0) v = "From your numbers: at a " + pctFmt(state.price) + " price change the margin on every job is gone, so more jobs only lose more money.";
      else {
        v = "From your numbers: margin dollars go from <b>" + money(r.M0) + "</b> to <b>" + money(r.Ms) + "</b> a month (" + signed(r.dM) + "). ";
        v += r.Ps >= 0 ? "That leaves " + money(r.Ps) + " after overhead" : "That is " + money(-r.Ps) + " short of your overhead";
        v += isFinite(r.BEs) ? "; you break even at " + jobsFmt(r.BEs) + " jobs a month." : ".";
      }
      $("#" + id + "verdict").innerHTML = v;
      drawChart(r);
      var full = $("#" + id + "full");
      if (full) full.href = (opts.fullUrl || "/learn/price-math/") + "?" + query();
      syncUrl();
      if (typeof opts.onChange === "function") opts.onChange(api);
    }

    /* Waterfall, to scale: now → price → faster quotes → missed calls → with the change; overhead as a dashed line. */
    var NS = "http://www.w3.org/2000/svg";
    function svgEl(tag, a, text) {
      var e = document.createElementNS(NS, tag);
      for (var k in a) e.setAttribute(k, a[k]);
      if (text != null) e.textContent = text;
      return e;
    }
    function drawChart(r) {
      var box = $("#" + id + "svg"), W = Math.max(280, Math.round(box.clientWidth || 320));
      var small = W < 460, H = small ? 250 : 270;
      var m = { t: 26, r: 8, b: small ? 44 : 38, l: 8 };
      var steps = [
        { lab: ["Now"], v: r.M0, total: true },
        { lab: ["Price", "change"], v: r.stepPrice },
        { lab: ["Faster", "quotes"], v: r.stepQuotes },
        { lab: ["Missed", "calls"], v: r.stepCalls },
        { lab: ["With the", "change"], v: r.Ms, total: true }
      ];
      var run = 0, lo = 0, hi = r.O;
      steps.forEach(function (s) {
        if (s.total) { s.a = 0; s.b = s.v; run = s.v; }
        else { s.a = run; s.b = run + s.v; run = s.b; }
        lo = Math.min(lo, s.a, s.b); hi = Math.max(hi, s.a, s.b);
      });
      if (hi - lo <= 0) hi = lo + 1;
      hi += (hi - lo) * 0.1;
      var y = function (v) { return m.t + (hi - v) / (hi - lo) * (H - m.t - m.b); };
      var slot = (W - m.l - m.r) / steps.length, bw = Math.min(64, slot * 0.62);
      var svg = svgEl("svg", { viewBox: "0 0 " + W + " " + H, width: W, height: H, role: "img",
        "aria-label": "Waterfall chart. Margin dollars now " + money(r.M0) + ", price change " + signed(r.stepPrice) +
          ", faster quotes " + signed(r.stepQuotes) + ", missed calls " + signed(r.stepCalls) + ", with the change " + money(r.Ms) +
          ". Overhead " + money(r.O) + "." });
      var defs = svgEl("defs", {});
      var pat = svgEl("pattern", { id: id + "hatch", width: 6, height: 6, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)" });
      pat.appendChild(svgEl("rect", { width: 6, height: 6, fill: "rgba(235,232,226,.08)" }));
      pat.appendChild(svgEl("line", { x1: 0, y1: 0, x2: 0, y2: 6, stroke: "rgba(235,232,226,.55)", "stroke-width": 2 }));
      defs.appendChild(pat); svg.appendChild(defs);
      svg.appendChild(svgEl("line", { x1: m.l, x2: W - m.r, y1: y(0), y2: y(0), stroke: "rgba(244,241,232,.35)", "stroke-width": 1 }));
      steps.forEach(function (s, i) {
        var cx = m.l + slot * i + slot / 2, top = y(Math.max(s.a, s.b)), bot = y(Math.min(s.a, s.b));
        var h = Math.max(1, bot - top), up = s.v >= 0;
        var fill = s.total ? "#ebe8e2" : (up ? "#3ddcae" : "url(#" + id + "hatch)");
        svg.appendChild(svgEl("rect", { x: cx - bw / 2, y: top, width: bw, height: h, rx: 3, fill: fill,
          stroke: !s.total && !up ? "rgba(235,232,226,.7)" : "none", "stroke-width": 1 }));
        if (i < steps.length - 1) {
          var nx = m.l + slot * (i + 1) + slot / 2;
          svg.appendChild(svgEl("line", { x1: cx + bw / 2, x2: nx - bw / 2, y1: y(s.b), y2: y(s.b), stroke: "rgba(244,241,232,.3)", "stroke-dasharray": "2 3" }));
        }
        var label = s.total ? money(s.v) : signed(s.v);
        var ty = s.total || up ? top - 6 : bot + 14;
        if (!s.total && Math.abs(s.v) < 0.5) ty = top - 6;
        svg.appendChild(svgEl("text", { x: cx, y: ty, "text-anchor": "middle", "class": "v" }, label));
        s.lab.forEach(function (t, j) {
          svg.appendChild(svgEl("text", { x: cx, y: H - m.b + 16 + j * 13, "text-anchor": "middle" }, t));
        });
      });
      var oy = y(r.O);
      svg.appendChild(svgEl("line", { x1: m.l, x2: W - m.r, y1: oy, y2: oy, stroke: "#3ddcae", "stroke-width": 1.5, "stroke-dasharray": "6 4" }));
      var ol = $("#" + id + "ohl"); if (ol) ol.textContent = "Overhead " + money(r.O) + ": your break-even line";
      box.innerHTML = ""; box.appendChild(svg);
    }

    function onInput(e) {
      var t = e.target; if (!t || !t.getAttribute) return;
      var k = t.getAttribute("data-k"); if (!k) return;
      if (t.value === "" || !isFinite(Number(t.value))) return; // let them finish typing
      state[k] = clamp(k, t.value);
      render();
    }
    root.addEventListener("input", onInput);
    root.addEventListener("change", function (e) {
      var t = e.target, k = t && t.getAttribute && t.getAttribute("data-k"); if (!k) return;
      state[k] = clamp(k, t.value); t.value = state[k]; render();
    });
    root.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest("[data-act]") : null; if (!b) return;
      var msg = $("#" + id + "msg");
      if (b.getAttribute("data-act") === "reset") {
        Object.keys(DEFAULTS).forEach(function (k) { state[k] = DEFAULTS[k]; });
        Array.prototype.forEach.call(inputs, function (i) { i.value = state[i.getAttribute("data-k")]; });
        render(); msg.textContent = "Back to the example shop.";
      } else if (b.getAttribute("data-act") === "copy") {
        var url = location.origin + location.pathname + "?" + query();
        var ok = function () { msg.textContent = "Link copied. It carries these numbers and nothing else."; };
        var fail = function () { msg.textContent = "Copy this link: " + url; };
        try { navigator.clipboard.writeText(url).then(ok, fail); } catch (err) { fail(); }
      }
      setTimeout(function () { msg.textContent = ""; }, 5000);
    });
    if (window.ResizeObserver) {
      var lastW = 0;
      new ResizeObserver(function () {
        var w = Math.round($("#" + id + "svg").clientWidth);
        if (Math.abs(w - lastW) > 4) { lastW = w; drawChart(compute(state)); }
      }).observe($("#" + id + "svg"));
    }

    var api = {
      state: function () { var c = {}; for (var k in state) c[k] = state[k]; return c; },
      result: function () { return compute(state); },
      /* One plain-text line for the lead form, sent only if the visitor ticks the box. */
      summary: function () {
        var s = state, r = compute(s);
        return "Calculator (their own numbers): avg job $" + s.job + ", " + s.jobs + " jobs/mo, " + s.gm + "% gross margin, overhead $" + s.oh +
          "/mo, " + s.q + " quotes/mo at " + s.cr + "% close, " + s.calls + " calls/mo with " + s.miss + "% unanswered. Levers: price " +
          (s.price > 0 ? "+" : "") + s.price + "%, close +" + s.qx + " pts, catch " + s.rec + "% of missed, " + s.book + "% of those book. " +
          "Margin $ now " + money(r.M0) + " -> " + money(r.Ms) + "/mo.";
      },
      query: query
    };
    render();
    return api;
  }

  window.PriceMath = { mount: mount, compute: compute, DEFAULTS: DEFAULTS };
})();
