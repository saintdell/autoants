/* autoants Demo Room: a small "conversation player".
 * Renders a phone frame and plays a script of events with Play / Step / Replay.
 * No framework, no external scripts. Respects prefers-reduced-motion (no slide-ins,
 * no blinking dots, instant scroll). Everything it shows is sample data.
 *
 *   DemoPhone.mount(document.getElementById("phone"), {
 *     title: "Sample Air & Heat", subtitle: "Text message", avatar: "SA", me: "customer",
 *     events: [
 *       {t: "call", title: "Incoming call", text: "(504) 555-0134", say: "A customer calls."},
 *       {t: "missed", title: "Missed call", text: "Rang out. The crew is on a roof."},
 *       {t: "typing", from: "business"},
 *       {t: "text", from: "business", text: "..."},
 *       {t: "view", title: "Sam (owner)", subtitle: "Owner's phone", avatar: "S", me: "owner", chip: "Now: the owner's phone"},
 *       {t: "notify", title: "Sample Air & Heat Ants", tag: "Text-Back", text: "..."},
 *       {t: "draft", title: "Draft reply", text: "...", note: "Nothing sends until you approve."},
 *       {t: "action", buttons: [{label: "Approve and send"}, {label: "Edit", ghost: true}]},
 *       {t: "action", choice: true, buttons: [{label: "Tue 2:00 PM", value: "Tue 2:00 PM"}, ...]},
 *       {t: "text", from: "customer", text: "{pick} works"},   // {pick} = the chosen button's value
 *       {t: "chip", text: "Next day, 5:00 PM"},
 *       {t: "card", k: "Instagram comment", title: "dana.sample", text: "QUOTE"},
 *     ]
 *   });
 *
 * Bubbles sent by the phone's current owner ("me") sit on the right; everything else on the left.
 * An "action" pauses Play until someone taps it; Step taps the first button.
 * Add ?all to the page URL to render the whole script at once (used for screenshots).
 */
(function () {
  "use strict";
  var reduce = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : { matches: false };

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function mount(root, cfg) {
    var events = cfg.events || [];
    var view = { title: cfg.title, subtitle: cfg.subtitle, avatar: cfg.avatar, me: cfg.me || "customer" };
    var i = 0, playing = false, timer = null, waiting = null, typingNode = null, vars = {};

    // ---- frame
    root.classList.add("stage");
    var phone = el("div", "phone" + (cfg.skin === "web" ? " web" : ""));
    phone.setAttribute("role", "group");
    phone.setAttribute("aria-label", cfg.label || "Sample phone screen");
    var screen = el("div", "screen");
    var bar = el("div", "bar");
    bar.appendChild(el("span", "", cfg.clock || "9:41"));
    var dots = el("span", "dots", "●●●");
    dots.setAttribute("aria-hidden", "true");
    bar.appendChild(dots);
    var head = el("div", "head");
    var avatar = el("div", "avatar");
    avatar.setAttribute("aria-hidden", "true");
    var who = el("div", "who");
    var whoB = el("b"), whoS = el("small");
    who.appendChild(whoB); who.appendChild(whoS);
    head.appendChild(avatar); head.appendChild(who);
    screen.appendChild(bar);
    screen.appendChild(head);
    var wp = null;
    if (cfg.web) {
      wp = el("div", "webpage");
      wp.appendChild(el("b", "", cfg.web.name));
      wp.appendChild(el("span", "", cfg.web.line));
      screen.appendChild(wp);
    }
    var log = el("div", "log");
    log.setAttribute("role", "log");
    log.setAttribute("aria-live", "polite");
    log.setAttribute("tabindex", "0");
    screen.appendChild(log);
    phone.appendChild(screen);
    root.appendChild(phone);

    var caption = el("p", "caption");
    caption.setAttribute("aria-live", "polite");
    root.appendChild(caption);

    var controls = el("div", "controls");
    var bPlay = el("button", "btn primary", "Play");
    var bStep = el("button", "btn", "Step");
    var bReplay = el("button", "btn", "Replay");
    [bPlay, bStep, bReplay].forEach(function (b) { b.type = "button"; controls.appendChild(b); });
    root.appendChild(controls);
    var progress = el("div", "progress");
    root.appendChild(progress);

    function sub(s) {
      return String(s == null ? "" : s).replace(/\{(\w+)\}/g, function (m, k) { return k in vars ? vars[k] : m; });
    }
    function setHead() {
      if (wp) wp.hidden = view.me !== (cfg.me || "customer");
      whoB.textContent = view.title || "";
      whoS.textContent = view.subtitle || "";
      avatar.textContent = view.avatar || (view.title || "?").slice(0, 1);
    }
    function scroll() { log.scrollTop = log.scrollHeight; }
    function add(node) {
      if (!reduce.matches) node.classList.add("pop");
      log.appendChild(node);
      scroll();
      return node;
    }
    function clearTyping() {
      if (typingNode && typingNode.parentNode) typingNode.parentNode.removeChild(typingNode);
      typingNode = null;
    }
    function updateUI() {
      progress.textContent = i === 0 ? "Sample script, " + events.length + " steps" : "Step " + Math.min(i, events.length) + " of " + events.length;
      bPlay.textContent = playing ? "Pause" : (i >= events.length ? "Play again" : (i === 0 ? "Play" : "Resume"));
      bStep.disabled = i >= events.length && !waiting;
    }

    function render(ev) {
      clearTyping();
      if (ev.say) caption.textContent = sub(ev.say);
      var n;
      switch (ev.t) {
        case "view":
          // Switching phones: what came before stays visible, dimmed, above a divider.
          Array.prototype.forEach.call(log.children, function (c) { c.classList.add("past"); });
          view = { title: ev.title, subtitle: ev.subtitle, avatar: ev.avatar, me: ev.me || view.me };
          setHead();
          if (ev.chip) add(el("div", "chipline", sub(ev.chip)));
          return null;
        case "chip":
          return add(el("div", "chipline", sub(ev.text)));
        case "typing":
          typingNode = el("div", "typing" + (ev.from === view.me ? " out" : ""));
          typingNode.setAttribute("aria-label", "typing");
          typingNode.appendChild(el("i")); typingNode.appendChild(el("i")); typingNode.appendChild(el("i"));
          return add(typingNode);
        case "text":
          n = el("div", "msg " + (ev.from === view.me ? "out" : "in"));
          if (ev.label) n.appendChild(el("span", "from", sub(ev.label)));
          n.appendChild(document.createTextNode(sub(ev.text)));
          return add(n);
        case "action":
          n = el("div", "acts");
          var btns = [];
          (ev.buttons || []).forEach(function (b, k) {
            var bt = el("button", b.ghost ? "ghost" : "", sub(b.label));
            bt.type = "button";
            bt.addEventListener("click", function () { choose(ev, n, btns, k); });
            btns.push(bt);
            n.appendChild(bt);
          });
          waiting = { ev: ev, node: n, btns: btns };
          add(n);
          if (btns[0]) { try { btns[0].focus({ preventScroll: true }); } catch (e) { /* old browsers */ } }
          return n;
        default: // call, missed, notify, draft, card
          n = el("div", "event " + ev.t);
          if (ev.k || ev.t === "draft") n.appendChild(el("span", "k", sub(ev.k || "Draft, not sent")));
          if (ev.tag) n.appendChild(el("span", "tag", sub(ev.tag)));
          if (ev.title) n.appendChild(el("b", "", sub(ev.title)));
          if (ev.text) n.appendChild(el("div", "body", sub(ev.text)));
          if (ev.note) n.appendChild(el("small", "muted", sub(ev.note)));
          return add(n);
      }
    }

    function choose(ev, node, btns, k) {
      if (!waiting || waiting.ev !== ev) return;
      var b = ev.buttons[k];
      if (ev.choice || ev.key) vars[ev.key || "pick"] = b.value != null ? b.value : b.label;
      btns.forEach(function (x, j) { x.disabled = true; if (j === k) x.classList.add("chosen"); });
      waiting = null;
      if (b.say) caption.textContent = sub(b.say);
      updateUI();
      if (playing) schedule(ev.wait != null ? ev.wait : 700);
    }

    function stepOnce() {
      if (waiting) { choose(waiting.ev, waiting.node, waiting.btns, 0); return; }
      if (i >= events.length) return;
      var ev = events[i++];
      render(ev);
      updateUI();
      return ev;
    }

    function schedule(ms) {
      clearTimeout(timer);
      timer = setTimeout(tick, ms);
    }
    function tick() {
      if (!playing) return;
      if (waiting) { updateUI(); return; } // pause on a tap-to-continue step
      if (i >= events.length) { playing = false; updateUI(); return; }
      var ev = stepOnce();
      if (waiting) return;
      var base = ev.t === "typing" ? 1100 : ev.t === "chip" || ev.t === "view" ? 900 : 1700;
      schedule(ev.wait != null ? ev.wait : base);
    }

    function reset() {
      clearTimeout(timer);
      playing = false; waiting = null; typingNode = null; i = 0; vars = {};
      view = { title: cfg.title, subtitle: cfg.subtitle, avatar: cfg.avatar, me: cfg.me || "customer" };
      setHead();
      log.innerHTML = "";
      var e = el("p", "empty", cfg.empty || "Tap Play to watch it, or Step to go one move at a time.");
      log.appendChild(e);
      caption.textContent = cfg.intro || "";
      updateUI();
    }
    function start() {
      var e = log.querySelector(".empty");
      if (e) log.removeChild(e);
    }

    bPlay.addEventListener("click", function () {
      if (playing) { playing = false; clearTimeout(timer); updateUI(); return; }
      if (i >= events.length && !waiting) reset();
      start();
      playing = true;
      updateUI();
      tick();
    });
    bStep.addEventListener("click", function () {
      playing = false; clearTimeout(timer);
      start();
      stepOnce();
      updateUI();
    });
    bReplay.addEventListener("click", function () {
      reset();
      start();
      playing = true;
      updateUI();
      tick();
    });

    reset();
    if (/[?&]all\b/.test(location.search)) {
      start();
      var guard = 0;
      while ((i < events.length || waiting) && guard++ < 500) stepOnce();
      clearTyping();
      updateUI();
    }
    return { reset: reset };
  }

  // Sample dates that always look current: the next weekday at or after `ahead` days.
  function day(ahead, opts) {
    var d = new Date();
    d.setHours(12, 0, 0, 0);
    d.setDate(d.getDate() + (ahead || 0));
    while (d.getDay() === 0 || (opts && opts.noSat && d.getDay() === 6)) d.setDate(d.getDate() + 1);
    return d;
  }
  var DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  var MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function short(d) { return DOW[d.getDay()] + " " + (d.getMonth() + 1) + "/" + d.getDate(); }
  function long(d) { return DOW[d.getDay()] + " " + MON[d.getMonth()] + " " + d.getDate(); }
  function nextDow(dow, minAhead) { // next given weekday (0=Sun) at least minAhead days out
    var d = day(minAhead || 1);
    while (d.getDay() !== dow) d.setDate(d.getDate() + 1);
    return d;
  }

  window.DemoPhone = { mount: mount, day: day, short: short, long: long, nextDow: nextDow, DOW: DOW };
})();
