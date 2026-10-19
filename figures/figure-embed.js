/* Embeds a Colorfigures figure (a self-contained page in this folder) in an iframe sized to its content, and shows
   the page's failed-state box (.figbook: a note, and on a shop's page its "Book a check" link) only while the figure
   is in its failed state (the figure exposes window.__isFailed).
   Markup: <div class="figframe"><iframe src="figure.html?embed=1"></iframe><div class="figbook" hidden>...</div></div> */
(() => {
  for (const box of document.querySelectorAll('.figframe')) {
    const fr = box.querySelector('iframe'), book = box.querySelector('.figbook');
    let started = false;
    const fit = () => {
      try {
        const d = fr.contentDocument, end = d && d.querySelector('.made-with');
        if (end) fr.style.height = Math.ceil(end.getBoundingClientRect().bottom + 10) + 'px';
      } catch (e) { /* not same-origin: keep the CSS height */ }
    };
    const start = () => {
      if (started) return; started = true;
      fit();
      setInterval(() => {
        fit();
        let failed = false;
        try { failed = !!(fr.contentWindow.__isFailed && fr.contentWindow.__isFailed()); } catch (e) {}
        if (book) book.hidden = !failed;
      }, 250);
    };
    fr.addEventListener('load', start);
    try { if (fr.contentDocument && fr.contentDocument.readyState === 'complete' && fr.contentWindow.__isFailed) start(); } catch (e) {}
    addEventListener('resize', fit);
  }
})();
