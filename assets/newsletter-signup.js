/* Permits Pulled sign-up: THE ONE PLACE the form's destination is set.
 *
 * PLACEHOLDER (2026-10-08): no Kit account exists yet, so `action` is empty and every sign-up form posts to the
 * autoants-leads worker (POST /subscribe), which keeps a consent record in KV and pings Lane on Telegram. Opt-in only.
 *
 * The "I mostly…" select (name="segment") tags each reader so later paid editions and offers reach the right
 * segment. Our values: trades · sells-to-business · real-estate · other.
 *
 * To wire it once Lane has the account (steps in tle-main/content/newsletter/README.md):
 *   Kit (recommended: tags are free):
 *     provider "kit", action "https://app.kit.com/forms/<form id>/subscriptions", emailField "email_address",
 *     segmentField "tags[]", segmentValues {trades: "<tag id>", "sells-to-business": "<tag id>", ...}
 *     (copy the field name and the numeric tag ids from the Kit form's HTML embed after adding a Tag dropdown)
 *   Buttondown (tags are a paid add-on):
 *     provider "buttondown", action "https://buttondown.com/api/emails/embed-subscribe/<username>",
 *     emailField "email", segmentField "tag", segmentValues {} (our values become the tag names)
 * Pages using it: index.html (#permit-report) and who-we-help.html (#permit-report, built by
 * brand/pages/who_we_help.py). Any form with the data-newsletter attribute picks this up.
 */
window.AUTOANTS_NEWSLETTER = {
  provider: "",        // PLACEHOLDER: "kit" or "buttondown"
  action: "",          // PLACEHOLDER: the platform's embed form action URL
  emailField: "email", // "email_address" for Kit, "email" for Buttondown
  segmentField: "",    // PLACEHOLDER: "tags[]" for Kit, "tag" for Buttondown
  segmentValues: {}    // PLACEHOLDER: our value -> the platform's tag id (Kit); leave {} to send our value as is
};

(function () {
  var SUBSCRIBE = "https://autoants-leads.saintdell.workers.dev/subscribe";
  var cfg = window.AUTOANTS_NEWSLETTER || {};
  var forms = document.querySelectorAll("form[data-newsletter]");
  Array.prototype.forEach.call(forms, function (f) {
    var email = f.querySelector("input[type=email]");
    var seg = f.querySelector("select[name=segment]");
    if (cfg.action) {
      f.setAttribute("action", cfg.action);
      f.setAttribute("method", "post");
      f.removeAttribute("enctype"); // harmless if absent
      if (email) email.setAttribute("name", cfg.emailField || "email");
      if (seg) {
        seg.setAttribute("name", cfg.segmentField || "segment");
        Array.prototype.forEach.call(seg.options, function (o) {
          var v = (cfg.segmentValues || {})[o.value];
          if (o.value && v) o.value = v;
        });
      }
      if (cfg.provider === "buttondown" && !f.querySelector("input[name=embed]")) {
        var h = document.createElement("input");     // Buttondown needs this to accept an embedded form
        h.type = "hidden"; h.name = "embed"; h.value = "1";
        f.appendChild(h);
      }
      return;
    }
    // No platform yet: send the sign-up to our own lead worker, which keeps the consent record and pings Lane.
    // (hello@autoants.com can't receive mail until Email Routing is set up, so no mailto here.)
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var btn = f.querySelector("button[type=submit]");
      var note = f.querySelector(".nl-consent");
      var said = note ? note.textContent : "";
      if (btn) btn.disabled = true;
      fetch(SUBSCRIBE, { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email ? email.value.trim() : "", segment: seg ? seg.value : "",
                               page: (location.pathname.replace(/^\//, "") || "index") + "#permit-report" }) })
        .then(function (r) {
          if (!r.ok) throw new Error(String(r.status));
          f.reset();
          if (note) note.textContent = "You're on the list. The next report comes at the start of the month.";
        })
        .catch(function () {
          if (note) note.textContent = "That didn't go through. Check the email and try again in a minute.";
          setTimeout(function () { if (note) note.textContent = said; }, 6000);
        })
        .then(function () { if (btn) btn.disabled = false; });
    });
  });
})();
