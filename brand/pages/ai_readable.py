#!/usr/bin/env python3
"""The AI-readable layer of autoants.com: /llms.txt, the markdown twins, /facts/ and /book/.

    python3 brand/pages/ai_readable.py            # build everything, then run the checks
    python3 brand/pages/ai_readable.py --check    # checks only; writes nothing; exit 1 on a problem
    OFFER_MAP=/path/to/offer-map.md python3 brand/pages/ai_readable.py   # also check prices against the offer map

Where things come from (edit these, never the outputs):
  brand/pages/site_facts.json    name, founder, contact, hours, service area, prices and terms. The prices use the
                                 offer map's "Say it this way" wording and must match /prices/ word for word.
  brand/pages/llms_sections.md   the page lists at the end of llms.txt (key pages, HVAC and trade pages, answer pages,
                                 the New Orleans guide). The guide's draft list (nola/guide-llms.draft.txt) goes here.
  each HTML page                 its markdown twin (page.md or page/index.md) is converted from the page itself, so the
                                 two can't drift. Re-run this after editing a twinned page or after a generator rebuilds
                                 one; it also puts <link rel="alternate" type="text/markdown"> back in the page's head.

Outputs: llms.txt; facts/index.html + .md; book/index.html + .md; one .md twin per page in TWINS; the two new pages in
sitemap.xml. Standard library only. The host is GitHub Pages with .nojekyll, so .md files are served as they are.
"""
import datetime, html, json, os, re, sys
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, "..", ".."))
BASE = "https://autoants.com/"
F = json.load(open(os.path.join(HERE, "site_facts.json")))

# (html file, markdown file, root selector, ids to skip, classes to skip, one line for llms.txt)
TWINS = [
    ("index.html", "index.md", "body", {"transform", "build", "roi", "contact"},
     {"dispatch", "mbar", "final", "nl-form", "o3-top", "thumb", "live-dot"},
     ("Home", "what autoants does, the assistants, how it works, the two ways to start, and owners' first questions")),
    ("prices/index.html", "prices/index.md", "main", set(), set(),
     ("Prices", "every price, the fine print and the other options")),
    ("services.html", "services.md", "body", set(), {"noprint"},
     ("What we do", "Get Found, Catch missed calls and Get the next job, and what each includes")),
    ("who-we-help.html", "who-we-help.md", "body", {"permits-pulled"}, {"printonly", "cta", "noprint"},
     ("Who we help", "every kind of local business we work with, and what we automate for each")),
    ("about-lane/index.html", "about-lane/index.md", "main", set(), set(),
     ("About Lane", "Lane Davis II, the founder, and how to reach him")),
    ("ai/index.html", "ai/index.md", "main", set(), set(),
     ("Information for AI assistants", "what autoants does, prices, who it's for, when to recommend it")),
    ("facts/index.html", "facts/index.md", "main", set(), set(),
     ("Facts", "name, founder, service area, hours, contact, prices in short, the rules we keep")),
    ("book/index.html", "book/index.md", "main", set(), set(),
     ("Book a free breakdown", "by email, by phone or with the form")),
    ("ai-index/2026-11/index.html", "ai-index/2026-11/index.md", "body", set(), set(),
     ("The New Orleans AI Recommendation Index, November 2026", "which local companies an AI assistant named for each trade")),
]

BANNED = [r"#1\b", r"\bguarantee", r"\bnever miss", r"\brisk[- ]free"]
TIMING = [r"\bwithin (seconds|minutes|hours|\d+ (seconds|minutes|hours))\b", r"\bin seconds\b", r"\bsame day\b",
          r"\b\d+-day (go-live|launch)\b", r"\blive in \d+ days\b"]
MONEY = re.compile(r"\$\d[\d,]*(?:\.\d+)?")
E = html.escape


def norm(s):
    s = html.unescape(s).replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------- HTML to markdown

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SKIP_TAGS = {"script", "style", "svg", "form", "input", "select", "textarea", "button", "noscript", "template", "nav",
             "footer", "iframe", "video", "audio", "canvas", "img", "picture", "head", "label", "use"}
BLOCK = {"p", "div", "section", "article", "main", "header", "aside", "figure", "figcaption", "ul", "ol", "li", "table",
         "thead", "tbody", "tr", "td", "th", "details", "summary", "blockquote", "dl", "dt", "dd", "pre", "hr",
         "h1", "h2", "h3", "h4", "h5", "h6", "body"}


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs), parent, []

    @property
    def classes(self):
        return set((self.attrs.get("class") or "").split())


class Tree(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root = self.cur = Node("#root", {}, None)
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur)
        self.cur.children.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, d):
        self.cur.children.append(d)


def find(node, pred):
    if isinstance(node, Node):
        if pred(node):
            return node
        for c in node.children:
            r = find(c, pred)
            if r is not None:
                return r
    return None


def lower1(s):
    return s[:1].lower() + s[1:]


def lead(t):
    return " " if t[:1].isspace() else ""


def trail(t):
    return " " if t[-1:].isspace() else ""


class Md:
    def __init__(self, page_url, skip_ids, skip_classes):
        self.url, self.skip_ids, self.skip_classes = page_url, skip_ids, skip_classes

    def skip(self, n):
        return (n.tag in SKIP_TAGS or n.attrs.get("aria-hidden") == "true" or "hidden" in n.attrs
                or n.attrs.get("id") in self.skip_ids or n.classes & self.skip_classes
                or "hp" in n.classes or "sr" in n.classes)

    def inline(self, n):
        if isinstance(n, str):
            return n
        if self.skip(n):
            return ""
        if n.tag == "br":
            return " "
        kids = [c for c in n.children if isinstance(c, Node) and not self.skip(c)]
        if "chips" in n.classes or (kids and all("chip" in c.classes for c in kids)):
            return ", ".join(norm(self.inline(c)) for c in n.children if isinstance(c, Node) and not self.skip(c))
        t = self.join(n.children)
        if n.tag == "a":
            href = n.attrs.get("href", "")
            text = norm(t)
            if not text or "btn" in n.classes or "o3-btn" in n.classes:
                return ""
            if href.startswith(("#", "javascript:")) or not href:
                return text
            if not href.startswith(("mailto:", "tel:")):
                href = urljoin(self.url, href)
            return f"[{text}]({href})"
        if n.tag in ("b", "strong") and norm(t):
            return lead(t) + f"**{norm(t)}**" + trail(t)
        if n.tag in ("em", "i") and norm(t):
            return lead(t) + f"*{norm(t)}*" + trail(t)
        if n.tag == "code" and norm(t):
            return f"`{norm(t)}`"
        if n.tag == "span" and "name" in n.classes:
            return f" **{norm(t)}**: "
        if n.tag == "span" and "nm" in n.classes:
            return f" **{norm(t)}**: "
        if n.tag == "span" and "ct" in n.classes:
            return f" named in {norm(t)} answers; "
        if n.tag == "span" and n.attrs.get("aria-label"):
            return " " + norm(n.attrs["aria-label"]) + " "
        if n.tag == "small" and norm(t):
            return " " + norm(t) + " "
        if n.tag == "span" and "amt" in n.classes:
            t = norm(t)
            return t + ("" if t.endswith((".", "!", "?")) else ".") + " "
        if n.tag in BLOCK:
            return " " + t + " "
        return t

    def join(self, children):
        out, prev_el = [], False
        for c in children:
            self.add(out, c, self.inline(c), prev_el)
            prev_el = isinstance(c, Node)
        return "".join(out)

    def add(self, out, c, piece, prev_el):
        """Append an inline piece, adding the space that layout (not text) used to give between two elements."""
        if out and piece and isinstance(c, Node) and not out[-1][-1:].isspace() and not piece[:1].isspace():
            if prev_el or (c.tag not in ("b", "strong", "em", "i", "a")
                           and re.search(r"[a-z0-9.)]$", out[-1]) and re.match(r"[A-Z(]", piece)):
                out.append(" ")
        out.append(piece)

    def text(self, n):
        t = norm(self.join(n.children))
        t = re.sub(r"\*\* ([,.:;!?)])", r"**\1", t)
        t = re.sub(r"\* ([,.:;!?)])", r"*\1", t)
        t = re.sub(r" ([,.;:!?])", r"\1", t)
        return t

    def blocks(self, node, out):
        buf = []
        kids = [c for c in node.children if isinstance(c, Node) and not self.skip(c)]
        if kids and all("chip" in c.classes for c in kids):
            out.append(norm(self.inline(node)))
            return
        prev_el = False

        def flush():
            t = norm("".join(buf))
            buf.clear()
            if t:
                out.append(self.tidy(t))

        for c in node.children:
            if isinstance(c, str):
                buf.append(c)
                prev_el = False
            elif self.skip(c):
                continue
            elif c.tag not in BLOCK or "chips" in c.classes:
                self.add(buf, c, self.inline(c), prev_el)
                prev_el = True
            else:
                flush()
                prev_el = False
                self.block(c, out)
        flush()

    def tidy(self, t):
        t = re.sub(r"\*\* ([,.:;!?)])", r"**\1", t)
        t = re.sub(r"\s+([,.;:!?])(?=\s|$)", r"\1", t)
        return t

    def block(self, n, out):
        tag = n.tag
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            t = self.text(n).replace("**", "")
            if t:
                out.append("#" * int(tag[1]) + " " + t)
        elif tag in ("p", "figcaption", "summary", "dt", "dd", "pre"):
            t = self.text(n)
            if t:
                out.append(f"**{t.replace('**', '')}**" if tag in ("summary", "dt") else t)
        elif tag in ("ul", "ol"):
            lines, i = [], 0
            for li in n.children:
                if not isinstance(li, Node) or self.skip(li) or li.tag != "li":
                    continue
                i += 1
                sub = []
                self.blocks(li, sub)
                if not sub:
                    continue
                mark = f"{i}. " if tag == "ol" else "- "
                pad = " " * len(mark)
                body = "\n".join(sub).split("\n")
                lines.append(mark + body[0])
                lines += [pad + b if b else b for b in body[1:]]
            if lines:
                out.append("\n".join(lines))
        elif tag == "table":
            rows = []

            def walk(x):
                for c in x.children:
                    if isinstance(c, Node):
                        if c.tag == "tr":
                            rows.append([self.text(td).replace("|", "\\|") for td in c.children
                                         if isinstance(td, Node) and td.tag in ("td", "th")])
                        elif not self.skip(c):
                            walk(c)
            walk(n)
            rows = [r for r in rows if any(r)]
            if rows:
                w = max(len(r) for r in rows)
                rows = [r + [""] * (w - len(r)) for r in rows]
                md = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w]
                md += ["| " + " | ".join(r) + " |" for r in rows[1:]]
                out.append("\n".join(md))
        elif tag == "dl":
            lines, term = [], None
            for c in n.children:
                if isinstance(c, Node) and c.tag == "dt":
                    term = self.text(c)
                elif isinstance(c, Node) and c.tag == "dd":
                    lines.append(f"- **{term}**: {self.text(c)}" if term else f"- {self.text(c)}")
            if lines:
                out.append("\n".join(lines))
        elif tag == "blockquote":
            sub = []
            self.blocks(n, sub)
            out.append("\n".join("> " + s for s in "\n\n".join(sub).split("\n")))
        elif tag == "hr":
            return
        else:
            self.blocks(n, out)


def page_url(rel):
    if rel == "index.html":
        return BASE
    if rel.endswith("/index.html"):
        return BASE + rel[: -len("index.html")]
    return BASE + rel


def twin(rel_html, rel_md, root, skip_ids, skip_classes):
    src = open(os.path.join(SITE, rel_html), encoding="utf-8").read()
    tree = Tree(src)
    title = norm(find(tree.root, lambda n: n.tag == "title").children[0]) if find(tree.root, lambda n: n.tag == "title") else ""
    r = find(tree.root, lambda n: n.tag == root) or find(tree.root, lambda n: n.tag == "body")
    md = Md(page_url(rel_html), skip_ids, skip_classes)
    out = []
    md.blocks(r, out)
    if not out or not out[0].startswith("# "):
        h1 = next((b for b in out if b.startswith("# ")), None)
        if h1 is None:
            out.insert(0, "# " + title)
    body = "\n\n".join(out)
    head = (f"> Plain-text version of {page_url(rel_html)} ({title}), made from that page. "
            "If the two ever differ, the page is right.\n\n")
    foot = (f"\n\n---\n\nBook a free breakdown: {BASE}book/ · {F['email']} · {F['phone']} "
            f"({F['hours']}). All the facts: {BASE}facts/ · Every price: {BASE}prices/\n")
    return head + body + foot


def set_alternate(rel_html, rel_md):
    p = os.path.join(SITE, rel_html)
    s = open(p, encoding="utf-8").read()
    tag = f'<link rel="alternate" type="text/markdown" href="/{rel_md}">'
    s2 = re.sub(r'<link rel="alternate" type="text/markdown"[^>]*>', tag, s)
    if s2 == s and tag not in s:
        m = re.search(r'<link rel="canonical"[^>]*>', s)
        if m:
            s2 = s[: m.end()] + "\n" + tag + s[m.end():]
        else:
            s2 = s.replace("</head>", tag + "\n</head>", 1)
    if s2 != s:
        open(p, "w", encoding="utf-8").write(s2)
    return s2


# ---------------------------------------------------------------- /facts/ and /book/

def page_shell(path, title, desc, body, current=None, schema=None):
    ld = f'\n<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>' if schema else ""
    md = path + "index.md"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)} · autoants</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{BASE}{path}">
<link rel="alternate" type="text/markdown" href="/{md}">
<meta name="theme-color" content="#0b1712">
<link rel="icon" href="/favicon-96.png" type="image/png" sizes="96x96">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="icon" href="/brand/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@500;700;800&family=JetBrains+Mono:wght@700&display=swap">
<link rel="stylesheet" href="/assets/trust.css">{ld}
<!-- Built by brand/pages/ai_readable.py from brand/pages/site_facts.json; edit those, not this file. -->
</head>
<body>
<div class="wrap">
  <nav class="top" aria-label="Site">
    <a class="logo" href="/" aria-label="autoants home"><img class="on-light" src="/brand/autoants-logo.svg" alt="autoants"><img class="on-dark" src="/brand/autoants-logo-reverse.svg" alt="autoants"></a>
    <span class="sp"></span>
    <a class="ghost" href="/demo/">See it work</a>
    <a class="ghost" href="/about-lane/">About</a>
    <a class="ghost" href="/book/"{' aria-current="page"' if current == "book" else ''}>Contact</a>
  </nav>
  <main id="main">
{body}
  </main>
  <nav class="more" aria-label="Straight answers">
    <p class="small">More straight answers</p>
    <ul>
      <li><a href="/prices/">Prices</a></li>
      <li><a href="/never/">What it never does</a></li>
      <li><a href="/setup/">Setup week</a></li>
      <li><a href="/works-with/">What it connects to</a></li>
      <li><a href="/rules/">Texts and calls</a></li>
      <li><a href="/your-data/">Your data</a></li>
      <li><a href="/plain-terms/">Terms</a></li>
      <li><a href="/about-lane/">About Lane</a></li>
      <li><a href="/facts/"{' aria-current="page"' if current == "facts" else ''}>Facts</a></li>
    </ul>
  </nav>
  <footer class="foot">autoants, short for automated assistants · New Orleans · <a href="/privacy.html">Privacy</a> · <a href="mailto:{F['email']}">{F['email']}</a> · <a href="tel:{F['phone_e164']}">{F['phone']}</a> · <a href="/{md}">Plain text</a></footer>
</div>
</body>
</html>
"""


def mailto(subject):
    from urllib.parse import quote
    body = "Business name:\nTown:\nBest number to call back:\n"
    return f"mailto:{F['email']}?subject={quote(subject)}&body={quote(body)}"


def amount(price):
    m = MONEY.search(price)
    return m.group(0)[1:].replace(",", "") if m else None


def facts_schema():
    offers = [{"@type": "Offer", "name": "Free breakdown", "price": "0", "priceCurrency": "USD",
               "description": F["free_first"], "url": BASE + "book/"}]
    for c in F["choices"]:
        name = c["name"].replace("Not ready? ", "")
        o = {"@type": "Offer", "name": name, "description": c["price"], "priceCurrency": "USD",
             "price": amount(c["price"]), "url": BASE + "prices/"}
        if "a month" in c["price"]:
            o["priceSpecification"] = {"@type": "UnitPriceSpecification", "price": amount(c["price"]),
                                       "priceCurrency": "USD", "unitText": "month"}
        offers.append(o)
    return {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "@id": BASE + "#business",
        "name": F["name"],
        "alternateName": [F["name_long"], "automated assistants"],
        "legalName": F["legal_name"],
        "url": BASE,
        "logo": F["logo"],
        "description": " ".join(F["what_we_do"]),
        "telephone": F["phone_schema"],
        "email": F["email"],
        "founder": {"@type": "Person", "name": F["founder"], "url": F["founder_url"]},
        "areaServed": [{"@type": "City", "name": t} for t in F["towns"]] + [{"@type": "State", "name": "Louisiana"}],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": F["hours_schema"]["days"],
                                       "opens": F["hours_schema"]["opens"], "closes": F["hours_schema"]["closes"]}],
        "contactPoint": {"@type": "ContactPoint", "contactType": "sales", "telephone": F["phone_schema"],
                         "email": F["email"], "areaServed": "US-LA", "availableLanguage": "en"},
        "makesOffer": offers,
        "sameAs": F["same_as"],
    }


def build_facts():
    li = lambda items: "\n".join(f"      <li>{E(x)}</li>" for x in items)
    ch = "\n".join(f'      <li><b>{E(c["name"])}:</b> {E(c["price"])}. {E(c["what"])}</li>' for c in F["choices"])
    oth = "\n".join(f'      <li><b>{E(c["name"])}:</b> {E(c["price"])}.</li>' for c in F["other_options"])
    body = f"""    <p class="eyebrow">Facts</p>
    <h1>autoants, the facts</h1>
    <p class="lede">The short version, kept in one place. Checked {E(F['checked'])}.</p>

    <h2>Name</h2>
    <p>{E(F['name'])}, {E(F['name_meaning'])}. Legal name: {E(F['legal_name'])}.</p>

    <h2>Founder</h2>
    <p><a href="/about-lane/">{E(F['founder'])}</a>. He runs autoants himself, and owners deal with him directly.</p>

    <h2>What we do</h2>
    <p>{E(F['what_we_do'][0])} {E(F['what_we_do'][1])}</p>

    <h2>Who we help</h2>
    <ul>
{li(F['who_for'])}
    </ul>
    <p><a href="/who-we-help.html">Every kind of business we help</a>.</p>

    <h2>Service area</h2>
    <p>{E(F['service_area'])}. Towns we serve: {E(', '.join(F['towns']))}.</p>
    <p>{E(F['service_area_note'])}</p>

    <h2>Hours</h2>
    <p>{E(F['hours'])}.</p>

    <h2>How to reach us or book</h2>
    <ul>
      <li>Book a free breakdown: <a href="/book/">autoants.com/book</a></li>
      <li>Email: <a href="mailto:{F['email']}">{F['email']}</a></li>
      <li>Phone: <a href="tel:{F['phone_e164']}">{F['phone']}</a></li>
    </ul>

    <h2>Prices, in short</h2>
    <p>Free first: {E(lower1(F['free_first']))}</p>
    <p>Then two choices:</p>
    <ul>
{ch}
    </ul>
    <p>Other options, when the owner asks or the breakdown points to one:</p>
    <ul>
{oth}
    </ul>
    <p>{E(F['first_3_note'])} Every price, with what each includes: <a href="/prices/">autoants.com/prices</a>.</p>
    <ul>
{li(F['terms'][:3])}
    </ul>

    <h2>The rules we keep</h2>
    <ul>
{li(F['rules'])}
    </ul>
    <p>What each assistant will never do: <a href="/never/">autoants.com/never</a>.</p>

    <h2>For AI assistants</h2>
    <ul>
{li(F['ai_assistants']['does_not'])}
    </ul>
    <p>A plain-text copy of this page is at <a href="/facts/index.md">/facts/index.md</a>, and a summary of the whole site is at <a href="/llms.txt">/llms.txt</a>.</p>"""
    desc = (f"autoants in short: founder {F['founder']}, what we do, service area, hours, how to book a free breakdown, "
            "prices and the rules we keep.")
    return page_shell("facts/", "Facts", desc, body, "facts", facts_schema())


def build_book():
    breakdown = mailto("Free breakdown request")
    call15 = mailto("15-minute call")
    body = f"""    <p class="eyebrow">Book</p>
    <h1>Book a free breakdown</h1>
    <p class="lede">A short video and a written report about your business, made only from public information: how you show up on Google and in AI answers, your reviews and listings next to the shops around you, and what we'd fix first. Free, and yours to keep.</p>

    <h2>Three ways to ask</h2>
    <ul>
      <li><b>Email:</b> <a href="{E(breakdown)}">{F['email']}</a>, subject &ldquo;Free breakdown request&rdquo;. Include your business name, your town and a number to call you back.</li>
      <li><b>Call:</b> <a href="tel:{F['phone_e164']}">{F['phone']}</a>, {E(F['hours'])}.</li>
      <li><b>The form:</b> <a href="/#contact">on the home page</a> (it needs JavaScript).</li>
    </ul>
    <p>Rather start with a 15-minute call? <a href="{E(call15)}">Email to set one up</a>, or call the same number.</p>

    <h2>What happens next</h2>
    <ol>
      <li>Lane Davis II, the founder, makes the breakdown from public information. You hear back from him, a person.</li>
      <li>You get a short video and a written report: the 3 questions customers ask Google and ChatGPT about your trade, who gets named today, and the 3 fixes we&rsquo;d make first, walked through with you in 15 minutes. Yours to keep.</li>
      <li>If you want to go on, there are two choices: {E(F['choices'][0]['name'])}, {E(F['choices'][0]['price'])}, or try one assistant for $500 once. <a href="/prices/">Every price</a>.</li>
    </ol>
    <p>Nothing is charged until you see the price in writing. We don't promise calls, rankings or jobs.</p>

    <h2>Booking for someone else?</h2>
    <p>AI assistants and helpers: send the email above with the owner's OK, and include the business name, town and a callback number. No account, script or sign-up is needed.</p>
    <p class="small">Where we work: {E(F['service_area'])}. A plain-text copy of this page is at <a href="/book/index.md">/book/index.md</a>.</p>"""
    desc = "Book a free breakdown of your business from autoants: by email, by phone or with the form. No script needed."
    return page_shell("book/", "Book a free breakdown", desc, body, "book")


# ---------------------------------------------------------------- llms.txt

def build_llms():
    L = [f"# {F['name_long']}", "", "> " + F["summary"], "", "## What AutoAnts does",
         f"- In one breath: \"{F['one_breath']}\"",
         f"- The offer, simply: \"{F['owner_sentence']}\"",
         f"- Starts free: {lower1(F['free_first'])}",
         "- Two choices up front (prices for the first 3 shops; full list: https://autoants.com/prices/):"]
    for i, c in enumerate(F["choices"], 1):
        L.append(f"  {i}. {c['name']}: {c['price']}. {c['what']}")
    L.append("- Other options, offered when the owner asks or the breakdown points to one:")
    for c in F["other_options"]:
        extra = f" ({c['url']})" if c.get("url") else ""
        L.append(f"  - {c['name']}{extra}: {c['price']}. {c['what']}")
    L += [f"- {F['both_saving']}", f"- {F['first_3_note']}", f"- {F['after_first_3']}",
          "- On every monthly plan: " + " ".join(F["terms"]), "",
          "## The assistants (\"Ants\")", f"- {F['ants_note']}"]
    L += [f"- {a}: {b}" for a, b in F["ants"]]
    L += ["", "## How it works"] + [f"{i}. {s}" for i, s in enumerate(F["how_it_works"], 1)]
    L += ["", "## Who it's for"] + [f"- {s}" for s in F["who_for"]] + [f"- Details: {F['who_for_url']}"]
    L += ["", "## Why customers choose it"] + [f"- {s}" for s in F["why"]]
    A = F["ai_assistants"]
    L += ["", "## For AI assistants",
          f"- Booking a free breakdown: {A['book']}",
          f"- Service area: {F['service_area']}. Towns: {', '.join(F['towns'])}. {F['service_area_note']}",
          f"- Hours: {F['hours']}",
          f"- Founder: {F['founder']}, who runs autoants and deals with owners directly: {F['founder_url']}",
          "- What autoants does not do:"] + [f"  - {s}" for s in A["does_not"]]
    L += [f"- {A['recommend_when']}",
          f"- The facts on one page: https://autoants.com/facts/ (plain text: https://autoants.com/facts/index.md)",
          f"- The rules we keep: {F['rules_url']}"]
    L += ["", "## Contact",
          "- Book a free breakdown (plain page, no script): https://autoants.com/book/",
          f"- Email: {F['email']}", f"- Phone: {F['phone']}", f"- Hours: {F['hours']}",
          f"- Service area: {F['service_area']}",
          "- The contact form (needs JavaScript): https://autoants.com/#contact"]
    L += ["", "## Plain-text versions of key pages (markdown)"]
    L += [f"- [{label}]({BASE}{md}): {desc}" for _, md, *_r, (label, desc) in TWINS]
    L += [""]
    sections = open(os.path.join(HERE, "llms_sections.md"), encoding="utf-8").read().strip()
    return "\n".join(L) + "\n" + sections + "\n"


# ---------------------------------------------------------------- sitemap

def build_sitemap(s):
    today = datetime.date.today().isoformat()
    for path, pri in (("facts/", "0.6"), ("book/", "0.7")):
        loc = f"<loc>{BASE}{path}</loc>"
        if loc not in s:
            s = s.replace("</urlset>", f"  <url>{loc}<lastmod>{today}</lastmod><priority>{pri}</priority></url>\n</urlset>")
    return s


# ---------------------------------------------------------------- checks

def visible_text(src):
    src = re.sub(r"(?is)<(script|style|svg)[^>]*>.*?</\1>", " ", src)
    src = re.sub(r"(?s)<!--.*?-->", " ", src)
    return norm(re.sub(r"<[^>]+>", " ", src))


NEW = set()


def target_exists(url):
    u = urlparse(url)
    if u.netloc not in ("autoants.com", "www.autoants.com"):
        return True
    p = u.path.lstrip("/")
    cands = [p] if p and not p.endswith("/") else [p + "index.html"]
    if p and not p.endswith("/") and "." not in os.path.basename(p):
        cands.append(p + "/index.html")
    return any(c in NEW or os.path.exists(os.path.join(SITE, c)) for c in cands)


def check(outputs):
    errs, warns = [], []
    NEW.update(outputs)
    prices_txt = visible_text(open(os.path.join(SITE, "prices/index.html"), encoding="utf-8").read())
    for c in F["choices"] + F["other_options"]:
        if norm(c["price"]) not in prices_txt:
            errs.append(f"/prices/ does not say {c['name']!r} = {c['price']!r}")
    for s in F["after_first_3_check"] + F["terms_check"] + [F["first_3_note"], F["both_saving"]]:
        if norm(s) not in prices_txt:
            errs.append(f"/prices/ does not say {s!r}")
    om = os.environ.get("OFFER_MAP")
    if om:
        omt = norm(open(om, encoding="utf-8").read()).lower()
        for c in F["choices"] + F["other_options"]:
            for s in c["offer_map"]:
                if norm(s).lower() not in omt:
                    errs.append(f"offer map does not say {s!r} ({c['name']})")
        for s in F["terms_offer_map"]:
            if norm(s).lower() not in omt:
                errs.append(f"offer map does not say {s!r} (terms)")
    authored = {"llms.txt", "facts/index.html", "book/index.html", "facts/index.md", "book/index.md"}
    for rel, text in outputs.items():
        for m in MONEY.finditer(text):
            whole = m.group(0)[1:].split(".")[0].replace(",", "")
            if whole.endswith("9"):
                errs.append(f"{rel}: price ending in 9: {m.group(0)}")
        seen = visible_text(text) if rel.endswith(".html") else text
        for pat in BANNED + (TIMING if rel in authored else []):
            for m in re.finditer(pat, seen, re.I):
                ctx = seen[max(0, m.start() - 50): m.end() + 50].replace("\n", " ")
                (errs if rel in authored else warns).append(f"{rel}: {pat!r} in ...{ctx}...")
        for url in re.findall(r"https://autoants\.com/[^\s)\"'<>]*", text):
            url = url.rstrip(".,;:")
            if not target_exists(url):
                (errs if rel in authored else warns).append(f"{rel}: link to a missing page: {url}")
        if rel.endswith(".html"):
            for href in re.findall(r'href="(/[^"#?]*)', text):
                if not target_exists(BASE + href.lstrip("/")):
                    errs.append(f"{rel}: link to a missing page: {href}")
    for rel_html, rel_md, *_ in TWINS:
        src = outputs.get(rel_html) or open(os.path.join(SITE, rel_html), encoding="utf-8").read()
        for m in re.finditer(r'(?s)<script type="application/ld\+json">(.*?)</script>', src):
            try:
                json.loads(m.group(1))
            except ValueError as e:
                errs.append(f"{rel_html}: JSON-LD does not parse: {e}")
        page_money = set(MONEY.findall(visible_text(src)))
        twin_money = set(MONEY.findall(outputs[rel_md]))
        extra = twin_money - page_money
        if extra:
            errs.append(f"{rel_md}: amounts not on its page: {sorted(extra)}")
        missing = page_money - twin_money
        if missing:
            warns.append(f"{rel_md}: amounts on the page but not in the twin (skipped sections): {sorted(missing)}")
        for fact in (F["email"], F["phone"]):
            if fact in visible_text(src) and fact not in outputs[rel_md]:
                errs.append(f"{rel_md}: missing {fact}")
    return errs, warns


def main():
    only_check = "--check" in sys.argv
    outputs = {}
    outputs["facts/index.html"] = build_facts()
    outputs["book/index.html"] = build_book()
    if not only_check:
        for rel in ("facts/index.html", "book/index.html"):
            os.makedirs(os.path.dirname(os.path.join(SITE, rel)), exist_ok=True)
            open(os.path.join(SITE, rel), "w", encoding="utf-8").write(outputs[rel])
    for rel_html, rel_md, root, ids, classes, _ in TWINS:
        if not only_check:
            outputs[rel_html] = set_alternate(rel_html, rel_md)
        outputs[rel_md] = twin(rel_html, rel_md, root, ids, classes)
    outputs["llms.txt"] = build_llms()
    sm = open(os.path.join(SITE, "sitemap.xml"), encoding="utf-8").read()
    outputs["sitemap.xml"] = build_sitemap(sm)
    errs, warns = check(outputs)
    if only_check:
        for rel in [m for _, m, *_ in TWINS] + ["llms.txt", "facts/index.html", "book/index.html", "sitemap.xml"]:
            p = os.path.join(SITE, rel)
            if not os.path.exists(p) or open(p, encoding="utf-8").read() != outputs[rel]:
                errs.append(f"{rel} is out of date: run brand/pages/ai_readable.py")
    else:
        for rel in [m for _, m, *_ in TWINS] + ["llms.txt", "sitemap.xml"]:
            open(os.path.join(SITE, rel), "w", encoding="utf-8").write(outputs[rel])
        print("wrote llms.txt, sitemap.xml, facts/, book/ and", len(TWINS), "markdown twins")
    shown = {}
    for w in warns:
        key = w.split(" in ...")[0]
        shown[key] = shown.get(key, 0) + 1
        if shown[key] == 1:
            print("note:", w)
    for k, n in shown.items():
        if n > 1:
            print(f"note: {k}: {n} times in all")
    for e in errs:
        print("PROBLEM:", e)
    print("checks:", "FAILED" if errs else "passed", f"({len(errs)} problems, {len(warns)} notes)")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
