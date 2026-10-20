/* Testimonial recording page (static; no framework, no third-party scripts).
 *
 * Flow: written consent first -> record up to 20 s in the browser -> watch it back -> send.
 * Config: clients/<c>.json beside this page, picked by ?c=<slug>; the invite link carries ?t=<token>.
 *   {"slug","business","uses":[...],"consent_text","consent_text_version":"tc-consent/1","upload_endpoint":"","sample"}
 * consent_text is written by products/testimonial-capture (tclib.consent_text), so the words the customer sees are
 * exactly the words stored in the consent record.
 * upload_endpoint "" (the default, and the only state on this branch) = DEMO: nothing leaves the phone.
 * With an endpoint (NOT deployed; see the product README's storage design): POST {consent} to <endpoint>/consent
 * -> {put_url} (a one-time presigned R2 URL for this token) -> PUT the video there.
 */
(function () {
  "use strict";
  var MAX_SECS = 20;
  var $ = function (id) { return document.getElementById(id); };
  var params = new URLSearchParams(location.search);
  var slug = (params.get("c") || "sample-hvac").replace(/[^a-z0-9-]/gi, "");
  var token = (params.get("t") || "").replace(/[^A-Za-z0-9_-]/g, "");
  var cfg = null, stream = null, rec = null, chunks = [], blob = null, timer = null;

  function show(step) {
    ["consent", "record", "review", "done"].forEach(function (s) { $("step-" + s).hidden = s !== step; });
  }

  function ready() {
    var ok = $("c-agree").checked && $("c-unpaid").checked && $("first").value.trim().length > 0 &&
      $("signed").value.trim().split(/\s+/).length >= 2;
    $("to-record").disabled = !ok;
  }

  function hex(buf) {
    return Array.prototype.map.call(new Uint8Array(buf), function (b) { return ("0" + b.toString(16)).slice(-2); }).join("");
  }

  fetch("clients/" + slug + ".json", { cache: "no-store" }).then(function (r) {
    if (!r.ok) throw new Error("no config");
    return r.json();
  }).then(function (c) {
    cfg = c;
    $("biz").textContent = c.business;
    $("consent-text").textContent = c.consent_text;
    $("sample").hidden = !c.sample;
    document.title = "Record a short video for " + c.business;
  }).catch(function () {
    $("consent-text").textContent = "This link isn't set up. Please ask the business for a new one.";
  });

  ["c-agree", "c-unpaid", "first", "signed"].forEach(function (id) { $(id).addEventListener("input", ready); });
  ["c-agree", "c-unpaid"].forEach(function (id) { $(id).addEventListener("change", ready); });

  $("to-record").addEventListener("click", function () {
    show("record");
    if (!navigator.mediaDevices || !window.MediaRecorder) {
      $("cam-err").hidden = false;
      $("cam-err").textContent = "This browser can't record video. Try Safari or Chrome on your phone.";
      return;
    }
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "user", width: { ideal: 1080 }, height: { ideal: 1920 } },
      audio: true }).then(function (s) {
      stream = s;
      $("live").srcObject = s;
    }).catch(function () {
      $("cam-err").hidden = false;
      $("cam-err").textContent = "We couldn't open the camera. Allow camera and microphone access, then try again.";
    });
  });

  function stopRec() {
    if (rec && rec.state === "recording") rec.stop();
    clearInterval(timer);
    $("stop").hidden = true;
    $("rec").hidden = false;
  }

  $("rec").addEventListener("click", function () {
    if (!stream) return;
    chunks = [];
    var type = ["video/mp4", "video/webm;codecs=vp9,opus", "video/webm"].filter(function (t) {
      return MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(t);
    })[0];
    rec = new MediaRecorder(stream, type ? { mimeType: type } : undefined);
    rec.ondataavailable = function (e) { if (e.data && e.data.size) chunks.push(e.data); };
    rec.onstop = function () {
      blob = new Blob(chunks, { type: rec.mimeType || "video/mp4" });
      $("playback").src = URL.createObjectURL(blob);
      show("review");
    };
    rec.start(250);
    var left = MAX_SECS;
    $("timer").textContent = "0:" + ("0" + left).slice(-2);
    $("rec").hidden = true;
    $("stop").hidden = false;
    timer = setInterval(function () {
      left -= 1;
      $("timer").textContent = "0:" + ("0" + Math.max(0, left)).slice(-2);
      if (left <= 0) stopRec();
    }, 1000);
  });
  $("stop").addEventListener("click", stopRec);
  $("again").addEventListener("click", function () { blob = null; show("record"); });

  $("send").addEventListener("click", function () {
    if (!blob || !cfg) return;
    $("send").disabled = true;
    blob.arrayBuffer().then(function (buf) { return crypto.subtle.digest("SHA-256", buf); }).then(function (d) {
      var kinds = ["video_testimonial"];
      if ($("c-review").checked) kinds.push("review_to_video");
      var consent = {
        schema: "testimonial-consent/1", client: cfg.slug, token: token,
        customer_first: $("first").value.trim(), signed_name: $("signed").value.trim(),
        signed_at: new Date().toISOString(), consent_text: cfg.consent_text,
        consent_text_version: cfg.consent_text_version, uses: cfg.uses, kinds: kinds,
        show_first_name: $("c-name").checked, compensation: "none", attested_unpaid: $("c-unpaid").checked,
        relationship: "none", origin: "customer_upload", video_sha256: hex(d), video_type: blob.type,
        video_bytes: blob.size, withdrawn: null
      };
      $("record-json").textContent = JSON.stringify(consent, null, 1);
      if (!cfg.upload_endpoint) {
        $("done-msg").textContent = "Demo page: nothing was sent and nothing left your phone. On a live link, your " +
          "video and this permission record go privately to " + cfg.business + ", who checks it before using it.";
        show("done");
        return null;
      }
      return fetch(cfg.upload_endpoint.replace(/\/$/, "") + "/consent", {
        method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(consent)
      }).then(function (r) { if (!r.ok) throw new Error("consent " + r.status); return r.json(); })
        .then(function (j) {
          return fetch(j.put_url, { method: "PUT", headers: { "content-type": blob.type }, body: blob });
        }).then(function (r) {
          if (!r.ok) throw new Error("upload " + r.status);
          $("done-msg").textContent = "Got it. " + cfg.business + " will check it before using it. To take it " +
            "down later, just reply to their message.";
          show("done");
        });
    }).catch(function () {
      $("send").disabled = false;
      alert("That didn't send. Check your connection and try again.");
    });
  });
})();
