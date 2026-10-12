/* autoants chat widget: a small, dependency-free chat launcher that talks to the autoants-leads worker's POST /chat.
   Add to a page (with chat-widget.css):
     <script src="/assets/chat/chat-widget.js" data-endpoint="https://autoants-leads.saintdell.workers.dev/chat" defer></script>
   Optional attributes: data-contact (fallback link, default https://autoants.com/#contact), data-phone (shown on failure).
   The conversation lives only in this browser tab (sessionStorage) and on autoants' side only if a lead is captured. */
(function () {
  "use strict";
  if (window.__aacChat) return;
  window.__aacChat = true;

  var me = document.currentScript || document.querySelector('script[src*="chat-widget"][data-endpoint]');
  var ENDPOINT = (me && me.getAttribute("data-endpoint")) || "";
  var CONTACT = (me && me.getAttribute("data-contact")) || "https://autoants.com/#contact";
  var PHONE = (me && me.getAttribute("data-phone")) || "";
  var KEY = "aac-chat-v1";
  var MAX_CHARS = 800;
  var GREETING = "Hi, I'm autoants' AI assistant. Ask me what we do, what it costs, or how the free video audit works. " +
    "If you'd like Lane to follow up, I can pass your details along.";
  var SUGGEST = ["What does it cost?", "How does the free video audit work?", "I'd like Lane to call me"];
  var NOTE = "Messages are answered by an AI and sent to autoants. Don't share sensitive info.";

  var ANT = '<svg viewBox="-2 -2 66 90" aria-hidden="true" focusable="false"><g stroke="#ebe8e2" stroke-width="4" stroke-linecap="round">' +
    '<path d="M24 31 15 9M38 31l9-22"/></g><circle cx="15" cy="7.5" r="3.6" fill="#ebe8e2"/><circle cx="47" cy="7.5" r="3.6" fill="#ebe8e2"/>' +
    '<circle cx="31" cy="57" r="29" fill="#3ddcae"/><circle cx="21.5" cy="53" r="4.3" fill="#0f5132"/><circle cx="40.5" cy="53" r="4.3" fill="#0f5132"/></svg>';
  var SEND = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  // ---- state (this tab only) ----
  var history = [];          // [{role, content, sig?}] exactly what the worker needs back
  try { history = JSON.parse(sessionStorage.getItem(KEY) || "[]") || []; } catch (e) { history = []; }
  if (!Array.isArray(history)) history = [];
  function save() { try { sessionStorage.setItem(KEY, JSON.stringify(history)); } catch (e) { /* private mode: fine */ } }
  function ref() {
    var r = "";
    try { r = new URLSearchParams(location.search).get("ref") || sessionStorage.getItem("aa-ref") || ""; } catch (e) { r = ""; }
    return r.replace(/[^a-z0-9_-]/gi, "").slice(0, 40);
  }

  // ---- DOM ----
  var root = document.createElement("div");
  root.className = "aac";
  root.innerHTML =
    '<button type="button" class="aac-launch" aria-expanded="false" aria-controls="aac-panel" aria-label="Chat with autoants\' AI assistant">' + ANT + "</button>" +
    '<div id="aac-panel" class="aac-panel" role="dialog" aria-modal="false" aria-labelledby="aac-title" hidden>' +
      '<header class="aac-head">' + ANT +
        '<div class="aac-title"><h2 id="aac-title">autoants</h2><span class="aac-badge">AI assistant</span></div>' +
        '<button type="button" class="aac-close" aria-label="Close chat">&times;</button></header>' +
      '<p class="aac-note" id="aac-note"></p>' +
      '<div class="aac-log" role="log" aria-live="polite" aria-label="Conversation with the AI assistant" tabindex="0"></div>' +
      '<div class="aac-suggest" role="group" aria-label="Suggested questions"></div>' +
      '<form class="aac-form" novalidate><label class="aac-sr" for="aac-input">Your message to the AI assistant</label>' +
        '<textarea id="aac-input" class="aac-input" rows="1" maxlength="' + MAX_CHARS + '" aria-describedby="aac-note" placeholder="Ask a question…"></textarea>' +
        '<button type="submit" class="aac-send" aria-label="Send message">' + SEND + "</button></form>" +
    "</div>";
  var launch = root.querySelector(".aac-launch"), panel = root.querySelector(".aac-panel"), closeBtn = root.querySelector(".aac-close");
  var log = root.querySelector(".aac-log"), suggest = root.querySelector(".aac-suggest"), form = root.querySelector(".aac-form");
  var input = root.querySelector(".aac-input"), sendBtn = root.querySelector(".aac-send");
  root.querySelector(".aac-note").textContent = NOTE;

  // ---- rendering (text only; URLs become links) ----
  var URL_RE = /(https?:\/\/[^\s<>"]+[^\s<>".,:;!?')\]])/g;
  function fill(el, text) {
    var last = 0, m;
    URL_RE.lastIndex = 0;
    while ((m = URL_RE.exec(text))) {
      if (m.index > last) el.appendChild(document.createTextNode(text.slice(last, m.index)));
      el.appendChild(link(m[1], m[1].replace(/^https?:\/\//, "")));
      last = m.index + m[1].length;
    }
    if (last < text.length) el.appendChild(document.createTextNode(text.slice(last)));
  }
  function link(href, label) {
    var a = document.createElement("a");
    a.href = href; a.textContent = label;
    var same = false;
    try { same = new URL(href, location.href).host === location.host; } catch (e) { same = false; }
    if (!same) { a.target = "_blank"; a.rel = "noopener"; }
    // A link to this page's own contact form closes the chat so the form is visible.
    if (same && /#contact$/.test(href) && document.getElementById("contact")) a.addEventListener("click", function () { setOpen(false, true); });
    return a;
  }
  function bubble(role, text) {
    var d = document.createElement("div");
    d.className = "aac-msg " + (role === "user" ? "aac-me" : "aac-bot");
    var who = document.createElement("span");
    who.className = "aac-sr";
    who.textContent = role === "user" ? "You said: " : "AI assistant: ";
    d.appendChild(who);
    fill(d, text);
    log.appendChild(d);
    log.scrollTop = log.scrollHeight;
    return d;
  }
  function helpBlock(text) {
    var d = document.createElement("div");
    d.className = "aac-msg aac-help";
    fill(d, text || "Sorry, the chat isn't working right now.");
    var row = document.createElement("div");
    row.className = "aac-actions";
    var href = CONTACT;
    try {   // already on the page with the form: jump to it instead of reloading
      var c = new URL(CONTACT, location.href);
      if (c.host === location.host && c.hash === "#contact" && document.getElementById("contact")) href = location.origin + location.pathname + "#contact";
    } catch (e) { href = CONTACT; }
    row.appendChild(link(href, "Use the contact form"));
    if (PHONE) row.appendChild(link("tel:" + PHONE.replace(/[^\d+]/g, ""), "Call " + PHONE));
    d.appendChild(row);
    log.appendChild(d);
    log.scrollTop = log.scrollHeight;
  }
  function renderAll() {
    log.textContent = "";
    bubble("assistant", GREETING);
    for (var i = 0; i < history.length; i++) bubble(history[i].role, history[i].content);
    suggest.textContent = "";
    if (!history.length) SUGGEST.forEach(function (q) {
      var b = document.createElement("button");
      b.type = "button"; b.className = "aac-chip"; b.textContent = q;
      b.addEventListener("click", function () { send(q); });
      suggest.appendChild(b);
    });
  }

  // ---- open / close ----
  function setOpen(open, quiet) {
    panel.hidden = !open;
    root.classList.toggle("aac-open", open);
    launch.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) { input.focus(); log.scrollTop = log.scrollHeight; }
    else if (!quiet) launch.focus();
  }
  launch.addEventListener("click", function () { setOpen(true); });
  closeBtn.addEventListener("click", function () { setOpen(false); });
  root.addEventListener("keydown", function (e) { if (e.key === "Escape" && !panel.hidden) { e.preventDefault(); setOpen(false); } });

  // ---- sending ----
  var busy = false;
  function typing(on) {
    var t = log.querySelector(".aac-typing");
    if (on && !t) {
      t = document.createElement("div");
      t.className = "aac-msg aac-bot aac-typing";
      t.setAttribute("role", "status");
      t.innerHTML = '<span class="aac-sr">The AI assistant is typing</span><i></i><i></i><i></i>';
      log.appendChild(t); log.scrollTop = log.scrollHeight;
    } else if (!on && t) t.remove();
  }
  function send(text) {
    text = String(text || "").trim().slice(0, MAX_CHARS);
    if (!text || busy) return;
    if (!ENDPOINT) { helpBlock("The chat isn't set up on this page."); return; }
    busy = true; sendBtn.disabled = true; suggest.textContent = "";
    history.push({ role: "user", content: text });
    bubble("user", text);
    input.value = ""; grow();
    typing(true);
    var ctl = window.AbortController ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctl) ctl.abort(); }, 30000);
    fetch(ENDPOINT, { method: "POST", headers: { "Content-Type": "application/json" }, signal: ctl ? ctl.signal : undefined,
                      body: JSON.stringify({ messages: history, ref: ref() }) })
      .then(function (r) { return r.json().catch(function () { return { ok: false }; }); })
      .then(function (d) {
        typing(false);
        if (d && d.ok && typeof d.reply === "string" && d.sig) {
          history.push({ role: "assistant", content: d.reply, sig: d.sig });
          bubble("assistant", d.reply);
          if (d.fallback) helpBlock("");
        } else {
          history.pop();                               // that question wasn't answered; keep the turns alternating
          if (d && d.error === "history") history = [];  // the saved conversation no longer checks out: start over
          helpBlock(d && d.reply ? d.reply : "Sorry, I couldn't reach the chat just now. You can still reach Lane directly:");
        }
      })
      .catch(function () {
        typing(false); history.pop();
        helpBlock("Sorry, I couldn't reach the chat just now. You can still reach Lane directly:");
      })
      .then(function () { clearTimeout(timer); save(); busy = false; sendBtn.disabled = false; });
  }
  form.addEventListener("submit", function (e) { e.preventDefault(); send(input.value); });
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); send(input.value); }
  });
  function grow() { input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 120) + "px"; }
  input.addEventListener("input", grow);

  // ---- keep clear of a fixed bottom bar (autoants.com's mobile .mbar) ----
  function place() {
    var bar = document.querySelector(".mbar"), h = 0;
    if (bar) { var cs = getComputedStyle(bar); if (cs.display !== "none" && cs.position === "fixed") h = bar.offsetHeight; }
    root.style.setProperty("--aac-bottom", (h + 16) + "px");
  }

  function start() {
    document.body.appendChild(root);
    renderAll(); place();
    window.addEventListener("resize", place, { passive: true });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
