// autoants converters: upload -> convert -> free slice -> buy or redeem a plan key. No signup.
(() => {
  const API = document.querySelector('meta[name="report-shop-api"]').content.replace(/\/$/, "");
  const form = document.getElementById("convert"), err = document.getElementById("err"), go = document.getElementById("go");
  const panel = document.getElementById("status"), tool = form.dataset.tool;
  const $ = (id) => document.getElementById(id);
  const money = (c) => "$" + (c / 100).toLocaleString("en-US", { maximumFractionDigits: 2 });
  const store = { get(k) { try { return localStorage.getItem(k) || ""; } catch { return ""; } },
                  set(k, v) { try { localStorage.setItem(k, v); } catch {} } };
  const timed = (url, opts = {}, ms = 30000) => { const c = new AbortController(), t = setTimeout(() => c.abort(), ms);
    return fetch(url, { ...opts, signal: c.signal }).finally(() => clearTimeout(t)); };
  const params = new URLSearchParams(location.search);
  let job = params.get("job") || "", polls = 0;

  function say(html) { panel.hidden = false; $("state").innerHTML = html; }
  function setJob(id) { job = id; const u = new URL(location.href); u.searchParams.set("job", id); u.searchParams.delete("session_id"); history.replaceState(null, "", u); }

  function found(s) {
    if (!s) return "";
    const cells = tool === "wh347"
      ? [[s.workers, "workers this week"], [s.fixes, "items to fix before signing"], [s.checks, "items to check"], ["$" + s.shortfall_total, "wage shortfall found"]]
      : [[s.certificates, "certificates"], [s.policies, "policy rows"], [s.needs_check, "rows to check by hand"], [s.expired, "expiration dates passed"], [s.expiring_30, "expire within 30 days"]];
    return `<div class="found">${cells.map(([n, l]) => `<div><b>${n}</b><span>${l}</span></div>`).join("")}</div>`;
  }

  function prices(v) {
    return `<div class="prices">${[...v.prices].sort((a, b) => a.cents - b.cents).map((p) => `<div class="price"><b>${p.name}</b><span class="amt">${money(p.cents)}${p.mode === "subscription" ? "/mo" : ""}</span><p>${p.blurb}</p><button class="btn btn-mint" data-buy="${p.key}" type="button">Buy</button></div>`).join("")}</div>
      <p class="help">${v.status_note ? "Test mode: these prices are proposed. " : ""}Payment is on Stripe's secure page; we never see your card number.</p>
      <div class="row"><label style="flex:1 1 16rem">Have a plan key? <input type="text" id="pk" value="${store.get("aa-plan-" + tool)}" placeholder="pk_…" autocomplete="off"></label><button class="btn btn-ghost" type="button" id="redeem">Use my plan</button></div>`;
  }

  function render(v) {
    if (v.status === "uploaded" || v.status === "processing") {
      say(`<p><span class="spin" aria-hidden="true"></span>Converting${v.status === "uploaded" ? " (in line)" : ""}… this page updates by itself.</p>`);
      return false;
    }
    if (v.status === "failed") { say(`<p class="err">${v.error || "We couldn't convert that file."}</p><p class="help">Nothing was kept: your upload was deleted.</p>`); return true; }
    if (v.expired) { say(`<p>This conversion's files have been deleted (72 hours after conversion). Upload the file again.</p>`); return true; }
    let h = `<h2>Done.</h2>${found(v.summary)}`;
    if (v.full_url) h += `<div class="row"><a class="btn btn-mint" href="${v.full_url}">Download everything (.zip)</a><span class="help">Link works until ${new Date(v.expires).toLocaleString()}.</span></div>`;
    else {
      if (v.free_url) h += `<div class="row"><a class="btn btn-ghost" href="${v.free_url}">Download the free part (.zip)</a><span class="help">${tool === "wh347" ? "Worker #1, the full draft for one worker-week." : `The first ${v.free_allow} certificate(s).`}</span></div>`;
      else h += `<p class="help">You've used this month's free ${tool === "wh347" ? "worker-week" : "certificates"}. Buy below to download the result.</p>`;
      h += prices(v);
    }
    say(h);
    return true;
  }

  async function poll() {
    if (!job) return;
    try {
      const r = await timed(`${API}/api/convert/job?id=${job}`);
      const v = await r.json();
      if (!r.ok) { say(`<p class="err">${v.error || "Something went wrong."}</p>`); return; }
      if (!render(v) && polls++ < 400) setTimeout(poll, 2500);
    } catch { if (polls++ < 400) setTimeout(poll, 4000); }
  }

  async function afterCheckout(sid) {
    for (let i = 0; i < 40; i++) {
      try {
        const r = await timed(`${API}/api/convert/session?session_id=${encodeURIComponent(sid)}&job=${job}`);
        const s = await r.json();
        if (s.status === "paid") {
          if (s.plan_key) {
            store.set("aa-plan-" + tool, s.plan_key);
            $("planbox").hidden = false;
            $("planbox").innerHTML = `<p><b>Your plan key</b> (we show it once; it's saved in this browser too):</p><p class="key">${s.plan_key}</p><p class="help">Paste it next time to use your plan. Keep it like a password.</p>`;
          }
          break;
        }
      } catch {}
      await new Promise((ok) => setTimeout(ok, 2000));
    }
    poll();
  }

  panel.addEventListener("click", async (e) => {
    const b = e.target.closest("[data-buy]");
    if (b) {
      b.disabled = true;
      try {
        const r = await timed(`${API}/api/convert/checkout`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ job, product: b.dataset.buy }) });
        const j = await r.json();
        if (r.ok && j.url) { location.href = j.url; return; }
        err.textContent = j.error || "Checkout couldn't start.";
      } catch { err.textContent = "Checkout couldn't start. Check your connection."; }
      b.disabled = false;
    }
    if (e.target.id === "redeem") {
      const key = $("pk").value.trim();
      try {
        const r = await timed(`${API}/api/convert/redeem`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ job, plan_key: key }) });
        const v = await r.json();
        if (!r.ok) { err.textContent = v.error || "That key didn't work."; return; }
        store.set("aa-plan-" + tool, key);
        err.textContent = "";
        render(v);
      } catch { err.textContent = "Couldn't reach the converter."; }
    }
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    err.textContent = "";
    const fd = new FormData();
    fd.set("tool", tool);
    if (tool === "wh347") {
      const p = $("payroll").files[0];
      if (!p) { err.textContent = "Add your payroll export."; return; }
      fd.append("payroll", p);
      if ($("workers").files[0]) fd.append("workers", $("workers").files[0]);
      if ($("time").files[0]) fd.append("time", $("time").files[0]);
      const o = { provider: $("provider").value, wd_number: $("wd").value.trim().toUpperCase(), wd_mod: $("mod").value.trim(),
        week_ending: $("week").value, contractor_name: $("cname").value.trim(), project_name: $("pname").value.trim(),
        project_number: $("pno").value.trim(), location: $("ploc").value.trim(), role: $("prime").checked ? "prime" : "subcontractor",
        cwhssa: $("cwhssa").checked, payroll_no: $("payno").value.trim() };
      if (!/^[A-Z]{2}\d{8}$/.test(o.wd_number)) { err.textContent = "Enter the wage determination number from your contract, like LA20260041."; return; }
      if (!o.week_ending) { err.textContent = "Enter the week ending date."; return; }
      fd.set("options", JSON.stringify(o));
    } else {
      const fs = [...$("certs").files];
      if (!fs.length) { err.textContent = "Add at least one certificate PDF."; return; }
      fs.forEach((f) => fd.append("cert", f));
      fd.set("options", "{}");
    }
    go.disabled = true; go.textContent = "Uploading…";
    try {
      const r = await timed(`${API}/api/convert/upload`, { method: "POST", body: fd }, 120000);
      const j = await r.json();
      if (!r.ok) { err.textContent = j.error || "Upload failed."; return; }
      setJob(j.job); polls = 0; poll();
    } catch { err.textContent = "Upload failed. Check your connection and try again."; }
    finally { go.disabled = false; go.textContent = "Convert"; }
  });

  if (job && params.get("session_id")) afterCheckout(params.get("session_id"));
  else if (job) poll();
})();
