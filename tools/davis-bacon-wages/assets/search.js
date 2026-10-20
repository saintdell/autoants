// Davis-Bacon wage lookup search: loads the static search-index.json once, then filters as you type.
// Every word typed must appear in the page title or its keyword list. No network calls beyond the index file.
(function () {
  var q = document.getElementById("q"), hits = document.getElementById("hits");
  if (!q || !hits) return;
  var idx = null, loading = false, waiting = function () {};
  function load(cb) {
    if (idx) return cb();
    waiting = cb;                       // run again once the index arrives, with whatever is typed by then
    if (loading) return;
    loading = true;
    var urls = (q.getAttribute("data-index") || "").split(" ").filter(Boolean);
    Promise.all(urls.map(function (u) { return fetch(u).then(function (r) { return r.json(); }); }))
      .then(function (ds) { idx = []; ds.forEach(function (d) { idx = idx.concat(d.pages || []); }); waiting(); })
      .catch(function () { loading = false; });
  }
  function norm(s) { return s.toLowerCase().replace(/\bst\.?\s/g, "st ").replace(/[^a-z0-9 ]+/g, " "); }
  function run() {
    var words = norm(q.value).split(/\s+/).filter(function (w) { return w.length > 1; });
    hits.innerHTML = "";
    if (!words.length) return;
    var out = [];
    for (var i = 0; i < idx.length && out.length < 12; i++) {
      var e = idx[i], hay = norm(e.t + " " + e.w);
      if (words.every(function (w) { return hay.indexOf(w) !== -1; })) out.push(e);
    }
    if (!out.length) { hits.innerHTML = "<li><a>No page matches yet.</a></li>"; return; }
    out.forEach(function (e) {
      var li = document.createElement("li"), a = document.createElement("a");
      a.href = e.u; a.textContent = e.t;
      var s = document.createElement("span"); s.textContent = e.n + " rates"; a.appendChild(s);
      li.appendChild(a); hits.appendChild(li);
    });
  }
  q.addEventListener("input", function () { load(run); });
  if (q.value) load(run);               // typed before this script ran
  q.addEventListener("focus", function () { load(function () {}); });
})();
