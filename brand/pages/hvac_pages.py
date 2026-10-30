"""Builds the HVAC section: hvac/index.html (the hub) and one page per owner question under hvac/<slug>/.

    python3 brand/pages/hvac_pages.py          # writes hvac/**/index.html
    python3 brand/pages/hvac_pages.py --check  # exits 1 if the built pages differ from what this file makes

Why a generator: every FAQ answer is printed on the page and in the FAQPage JSON-LD from the same string, so the
two can't drift (the seo skill's character-for-character rule), and a price change is one edit here.

Copy rules (Lane's, for every autoants page): plain words; no "#1", no rank or result promises; no prices ending
in 9; the receptionist is always "an AI" and says so; no Google ratings or reviews of named businesses and no
competitor named in a negative way (these pages name none); no attorney credential; signed autoants. Every number
carries its source and the date it was pulled. The numbers come from tle-main's stats ledger
(products/assessment/stats/stats.jsonl), the language-targeting run (data/language-targeting/stats-2026-10-20.json),
the AI-visibility scans (data/aivis/*/hvac*) and NOAA's 1991-2020 normals, each read on the date in SRC.
URLs carry no place name (expansion rule, 2026-10-12): local wording lives in the copy.
"""
import html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, "..", ".."))
BASE = "https://autoants.com"
TODAY = "2026-10-20"          # the day these pages were written and their facts checked (from `date`)
TODAY_WORDS = "October 20, 2026"
E = html.escape

# ---------------------------------------------------------------- sources (shown at the foot of each page)
# key: (what it is, url or None, when we read it)
SRC = {
    "noaa": ("NOAA National Centers for Environmental Information, U.S. Climate Normals 1991-2020, New Orleans "
             "International Airport (station USW00012916), monthly and seasonal normals",
             "https://www.ncei.noaa.gov/data/normals-monthly/1991-2020/access/USW00012916.csv", "Read October 20, 2026"),
    "permits": ("City of New Orleans open data, “Permits - BLDS” (dataset 72f9-bi28), HVAC permits issued "
                "October 1, 2025 to September 30, 2026. Orleans Parish only (Jefferson Parish publishes no open permit "
                "data). The city records the license holder, not the company, and permits track installs and "
                "replacements, not repair calls",
                "https://data.nola.gov/resource/72f9-bi28.json", "Pulled October 14, 2026"),
    "firstscreen": ("autoants first-screen check: 51 New Orleans-area HVAC homepages, each loaded once at phone size; "
                    "the 45 that loaded as a working site are counted (6 didn't load, showed an error page or stayed "
                    "blank). A first pass on one date. We count the sites; we don't name them",
                    None, "Checked October 12, 2026"),
    "spanishsites": ("autoants language check: the homepages of 135 HVAC businesses in Orleans, Jefferson and St. "
                     "Bernard parishes, each read once for a Spanish page, link or language switch. A first pass on "
                     "the homepage only. We count the sites; we don't name them",
                     None, "Checked October 20, 2026"),
    "acs": ("U.S. Census Bureau, American Community Survey 2020-2024 5-year estimates, table C16001 (language spoken "
            "at home by ability to speak English), residents 5 and over. Survey estimates with a margin of error, "
            "averaged over 2020-2024",
            "https://www.census.gov/programs-surveys/acs", "Read October 20, 2026"),
    "aien": ("autoants AI-answer scan: the same 8 homeowner questions about air conditioning companies, each asked 3 "
             "times of one AI assistant (Claude, with web search on), for New Orleans, Kenner and Slidell. One AI, one "
             "date. Answers change from run to run, so a count is a snapshot, not a ranking",
             None, "Asked October 19, 2026"),
    "aies": ("autoants AI-answer scan in Spanish: 8 questions a Spanish-speaking customer in Kenner might ask about "
             "air conditioning, each asked once of one AI assistant (Claude, with web search on). One AI, one date, "
             "one run",
             None, "Asked October 20, 2026"),
    "bls": ("U.S. Bureau of Labor Statistics, Occupational Employment and Wage Statistics, May 2025: median yearly pay "
            "for receptionists and information clerks (SOC 43-4171), New Orleans-Metairie metro. Wage-and-salary jobs "
            "only; benefits not included",
            "https://www.bls.gov/oes/current/oes_35380.htm", "Read October 15, 2026"),
    "gmaps": ("Google, Maps User Generated Content Policy, the “Rating manipulation” section",
              "https://support.google.com/contributionpolicy/answer/7400114", "Checked October 20, 2026"),
    "gbp": ("Google Business Profile Help, “Tips to get more reviews”",
            "https://support.google.com/business/answer/3474122", "Checked October 20, 2026"),
    "ftc": ("Federal Trade Commission, Trade Regulation Rule on the Use of Consumer Reviews and Testimonials (16 CFR "
            "Part 465, in effect since October 21, 2024), and the FTC's questions-and-answers page on it",
            "https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers",
            "Checked October 20, 2026"),
    "brightlocal": ("BrightLocal, “Where to get local citations for AI search” (Local AI Visibility Tracker "
                    "study, US-wide, published August 26, 2026, updated September 16, 2026). Their study and their "
                    "sample, not New Orleans",
                    "https://www.brightlocal.com/resources/ai-directory-sources/", "Checked October 20, 2026"),
    "gsc": ("Google Search Central, “Introducing Search Generative AI performance reports in Search Console” "
            "(June 3, 2026; rolled out to all websites worldwide as of August 31, 2026)",
            "https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports", "Checked October 20, 2026"),
    "prices": ("autoants prices page. Prices are for our first 3 shops on each plan; the page lists what they become "
               "after", BASE + "/prices/", "Checked October 20, 2026"),
    "rules": ("autoants, Texts and calls: carrier registration, STOP and the AI disclosure",
              BASE + "/rules/", "Checked October 20, 2026"),
    "compare": ("autoants vs a traditional answering service: the other side's prices from their own pages, each "
                "dated", BASE + "/compare/answering-service/", "Checked October 20, 2026"),
}

# ---------------------------------------------------------------- prices (as on /prices, checked TODAY)
P_BOTH = "$1,250 a month + $1,000 setup"
P_TRY = "$500 once"
P_NMJ = "$750 a month + $750 setup"
P_GF = "$750 a month + $250 setup"
P_PPJ = "$250 a month + $25 for each job we save from a call you missed, never more than $750 a month"

PAGES = [
    ("missed-calls-summer", "How does an HVAC company stop missing calls in the July rush?"),
    ("ai-receptionist-vs-answering-service", "AI receptionist, answering service or a dispatcher: which fits an HVAC company?"),
    ("book-from-the-first-screen", "Can customers book your HVAC company from the first phone screen?"),
    ("more-google-reviews", "How does an HVAC company get more Google reviews without breaking Google's rules?"),
    ("show-up-in-ai-answers", "How does an HVAC company show up when people ask ChatGPT, Claude or Google's AI for an AC company?"),
    ("spanish-line", "Does an HVAC company around New Orleans need a Spanish line?"),
]
H1 = dict(PAGES)

CSS = """
  :root{--bg:#0b1712;--surface:#14261e;--surface-2:#1b3328;--ink:#f4f1e8;--muted:#a3b0a8;--faint:#87948d;
        --mint:#3ddcae;--mint-ink:#062a1d;--line:rgba(244,241,232,.12);
        --disp:"Archivo",system-ui,sans-serif;--body:"Inter",system-ui,sans-serif;--mono:"JetBrains Mono",ui-monospace,monospace;
        color-scheme:dark}
  *{box-sizing:border-box}
  html{-webkit-text-size-adjust:100%}
  body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);line-height:1.6;-webkit-font-smoothing:antialiased;overflow-x:hidden}
  a{color:inherit}
  a:focus-visible{outline:3px solid var(--mint);outline-offset:3px}
  .wrap{max-width:820px;margin:0 auto;padding:0 16px;overflow-wrap:break-word}
  nav{display:flex;align-items:center;gap:14px;padding:18px 0;border-bottom:1px solid var(--line)}
  nav .sp{margin-left:auto}
  nav a.ghost{color:var(--muted);text-decoration:none;font-weight:600;font-size:14px;white-space:nowrap;padding:10px 0}
  .crumbs{font-family:var(--mono);font-size:12px;letter-spacing:.08em;color:var(--faint);margin:32px 0 0}
  .crumbs a{color:var(--mint);text-decoration:none}
  h1{font-family:var(--disp);font-weight:800;font-size:clamp(28px,5.4vw,44px);line-height:1.08;letter-spacing:-.01em;margin:10px 0 16px;text-wrap:balance}
  .answer{font-size:18px;background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--mint);border-radius:12px;padding:14px 18px;margin:0 0 8px}
  .answer p{color:var(--ink);margin:.45em 0;max-width:none}
  .stamp{font-family:var(--mono);font-size:12px;color:var(--faint);margin:10px 0 24px}
  h2{font-family:var(--disp);font-weight:800;font-size:clamp(22px,4vw,26px);line-height:1.2;margin:42px 0 10px;text-wrap:balance}
  h3{font-family:var(--disp);font-weight:700;font-size:18px;line-height:1.3;margin:22px 0 4px}
  p,li{color:var(--muted);max-width:68ch}
  b,strong{color:var(--ink)}
  ul,ol{padding-left:1.2rem} li{margin:.45em 0}
  .wrap a.in{color:var(--mint)}
  .stats{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:14px 0 6px}
  .stat{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:14px}
  .stat .n{font-family:var(--disp);font-weight:800;font-size:30px;line-height:1;color:var(--mint);font-variant-numeric:tabular-nums}
  .stat .l{font-size:14px;color:var(--muted);margin-top:6px;line-height:1.4}
  .stat .s{font-family:var(--mono);font-size:11px;color:var(--faint);margin-top:8px;line-height:1.4}
  .src{font-family:var(--mono);font-size:12px;color:var(--faint);margin:6px 0 0;max-width:none}
  .tw{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:10px 0 0;border-radius:12px}
  table{width:100%;border-collapse:collapse;background:var(--surface);border:1px solid var(--line);border-radius:12px;font-size:15px}
  th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
  tr:last-child td{border-bottom:0}
  th{color:var(--ink);font-family:var(--mono);font-size:12px;letter-spacing:.06em;text-transform:uppercase;font-weight:500}
  td{color:var(--muted)} td b{color:var(--ink)} td.num{font-variant-numeric:tabular-nums;white-space:nowrap}
  .cards{display:grid;gap:10px;margin:12px 0}
  .card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:14px 16px}
  .card h3{margin:0 0 4px}
  .card p{margin:.3em 0}
  .card a.go{display:inline-block;color:var(--mint);font-weight:600;text-decoration:none;padding:8px 0 2px}
  .faq h3{margin-top:20px}
  .btn{display:inline-block;background:var(--mint);color:var(--mint-ink);font-weight:700;text-decoration:none;border-radius:10px;padding:12px 18px;min-height:44px}
  .more{background:var(--surface-2);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:36px 0}
  .more p{color:var(--ink)}
  .more a:not(.btn){color:var(--mint)}
  ol.sources{padding-left:1.4rem} ol.sources li{font-size:14px;margin:.6em 0}
  ol.sources a{color:var(--mint);word-break:break-all}
  footer{color:var(--faint);font-size:13px;padding:30px 0 48px;border-top:1px solid var(--line);margin-top:44px}
  footer p{color:var(--faint);margin:.3em 0;max-width:none}
  footer a{color:var(--muted);display:inline-block;padding:6px 0}
  @media (max-width:560px){
    .stats{grid-template-columns:1fr}
    table{font-size:14px} th,td{padding:8px 8px}
    th{letter-spacing:0;text-transform:none;font-size:12px} td.num{white-space:normal}
    table.stack thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
    table.stack,table.stack tbody,table.stack tr,table.stack td{display:block;width:100%}
    table.stack tr{border-bottom:1px solid var(--line);padding:6px 0}
    table.stack tr:last-child{border-bottom:0}
    table.stack td{border:0;padding:4px 12px}
    table.stack td:first-child{padding-top:8px}
    table.stack td:not(:first-child)::before{content:attr(data-label) ": ";font-family:var(--mono);font-size:11px;color:var(--faint);letter-spacing:.04em}
    .answer{font-size:17px}
  }
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800&family=Inter:wght@400;600'
         '&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">')

ORG = {"@type": "ProfessionalService", "@id": BASE + "/#organization", "name": "autoants",
       "alternateName": "automated assistants", "legalName": "AutoAnts, LLC", "url": BASE + "/",
       "logo": BASE + "/brand/autoants-icon.svg", "email": "hello@autoants.com",
       "telephone": "+1-504-499-1194",
       "areaServed": [{"@type": "City", "name": "New Orleans"}, {"@type": "City", "name": "Metairie"},
                      {"@type": "City", "name": "Kenner"},
                      {"@type": "AdministrativeArea", "name": "St. Tammany Parish (the Northshore)"}]}


def link(p, href, text):
    return f'<a class="in" href="{p}{href}">{text}</a>'


def stat(n, label, src):
    return f'<div class="stat"><div class="n">{n}</div><div class="l">{label}</div><div class="s">{src}</div></div>'


def table(head, rows):
    """A real HTML table. With 4+ columns it stacks into labeled cards on a phone (CSS .stack)."""
    stack = len(head) >= 4
    h = "".join(f"<th>{c}</th>" for c in head)
    body = ""
    for r in rows:
        cells = ""
        for i, c in enumerate(r):
            cls = ' class="num"' if i and len(head) > 2 and c[:1].isdigit() else ""
            lab = f' data-label="{E(html.unescape(head[i]))}"' if stack else ""
            cells += f"<td{cls}{lab}>{c}</td>"
        body += f"<tr>{cells}</tr>"
    tcls = ' class="stack"' if stack else ""
    return f'<div class="tw"><table{tcls}><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table></div>'


SHORT = {"noaa": "NOAA climate normals 1991-2020", "permits": "City of New Orleans permit data",
         "firstscreen": "autoants first-screen check", "spanishsites": "autoants language check",
         "acs": "Census ACS 2020-2024, table C16001", "aien": "autoants AI-answer scan",
         "aies": "autoants AI-answer scan in Spanish", "bls": "BLS wage survey, May 2025",
         "gmaps": "Google Maps content policy", "gbp": "Google Business Profile Help", "ftc": "FTC review rule",
         "brightlocal": "BrightLocal", "gsc": "Google Search Central", "prices": "autoants prices page",
         "rules": "autoants texts and calls rules", "compare": "autoants comparison page"}


def src_line(*keys):
    return '<p class="src">Source: ' + "; ".join(f"{E(SHORT[k])} ({SRC[k][2][:1].lower() + SRC[k][2][1:]})" for k in keys) + \
        '. <a href="#sources" style="color:inherit">Full list below</a>.</p>'


def sources_block(keys):
    items = []
    for k in keys:
        what, url, when = SRC[k]
        u = f' <a href="{E(url)}">{E(url)}</a>.' if url else ""
        items.append(f"<li>{E(what)}.{u} {E(when)}.</li>")
    return '<h2 id="sources">Sources</h2>\n<ol class="sources">' + "".join(items) + "</ol>"


def faq_block(faq):
    return '<h2 id="questions">Questions</h2>\n<div class="faq">' + "".join(
        f"<h3>{E(q)}</h3><p>{E(a)}</p>" for q, a in faq) + "</div>"


def cta(p):
    return (f'<div class="more"><p><b>Want to see it for your shop first?</b> Start with the free breakdown: how you '
            f'show up on Google, in AI answers and next to the shops around you, made from public information. Every '
            f'price is written down before anything starts.</p>'
            f'<a class="btn" href="{p}index.html?interest=Free%20company%20breakdown&amp;ref=hvac#contact">Get my free '
            f'breakdown</a></div>')


def page(path, title, desc, h1, crumbs_html, answer_paras, body, faq, srcs, graph, p, top_cta=False):
    canon = f"{BASE}/{path}"
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    ans = "".join(f"<p>{a}</p>" for a in answer_paras)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE}/brand/og.png">
<meta name="theme-color" content="#0b1712">
<link rel="icon" href="/favicon-96.png" type="image/png" sizes="96x96">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="icon" href="{p}brand/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{p}brand/apple-touch-icon.png">
{FONTS}
<script type="application/ld+json">{ld}</script>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <nav>
    <a href="{p}index.html"><img src="{p}brand/autoants-logo-reverse.svg" alt="autoants home" width="120" height="26" style="height:26px;width:auto;display:block"></a>
    <div class="sp"></div>
    <a class="ghost" href="{p}prices/">Prices</a>
    <a class="ghost" href="{p}index.html#contact">Contact</a>
  </nav>
  <main>
  <p class="crumbs">{crumbs_html}</p>
  <h1>{E(h1)}</h1>
  <div class="answer">{ans}</div>
  <p class="stamp">By autoants · checked {TODAY_WORDS} · prices for our first 3 shops</p>
{f'  <p><a class="btn" href="{p}index.html?interest=Free%20company%20breakdown&amp;ref=hvac#contact">Get my free breakdown</a></p>' if top_cta else ""}
{body}
{faq_block(faq) if faq else ""}
{cta(p)}
{sources_block(srcs)}
  </main>
  <footer>
    <p>autoants, short for automated assistants · a New Orleans company that answers missed calls, books jobs and gets local businesses found on Google and in AI answers · commercial services only. Call <a href="tel:+15044991194">(504) 499-1194</a>.</p>
    <p>Checked {TODAY_WORDS}. Corrections: hello@autoants.com · <a href="{p}hvac/">For HVAC companies</a> · <a href="{p}never/">What it never does</a> · <a href="{p}prices/">Prices</a> · <a href="{p}compare/">Comparisons</a> · <a href="{p}ai/">For AI assistants</a></p>
    <p>&mdash; autoants</p>
  </footer>
</div>
</body>
</html>
"""


def crumbs(p, here=None):
    if here is None:
        return "autoants for HVAC · New Orleans, Metairie, Kenner, the Northshore"
    return f'<a href="{p}hvac/">autoants for HVAC</a> · {E(here)}'


def breadcrumb(slug, name):
    items = [{"@type": "ListItem", "position": 1, "name": "autoants", "item": BASE + "/"},
             {"@type": "ListItem", "position": 2, "name": "autoants for HVAC companies", "item": BASE + "/hvac/"}]
    if slug:
        items.append({"@type": "ListItem", "position": 3, "name": name, "item": f"{BASE}/hvac/{slug}/"})
    return {"@type": "BreadcrumbList", "itemListElement": items}


def faq_ld(url, faq):
    return {"@type": "FAQPage", "@id": url + "#questions", "url": url, "dateModified": TODAY, "inLanguage": "en-US",
            "isPartOf": {"@id": BASE + "/hvac/#webpage"}, "publisher": {"@id": BASE + "/#organization"},
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                           for q, a in faq]}


def related(p, skip):
    out = []
    for slug, q in PAGES:
        if slug != skip:
            out.append(f'<li><a class="in" href="{p}hvac/{slug}/">{E(q)}</a></li>')
    return ('<h2>More for HVAC owners</h2><ul>' + "".join(out) +
            f'<li><a class="in" href="{p}hvac/">autoants for HVAC companies: everything on one page</a></li></ul>')


# ---------------------------------------------------------------- the hub
def hub():
    p = "../"
    url = BASE + "/hvac/"
    title = "Never miss an AC call: autoants for HVAC companies"
    desc = ("For HVAC owners in New Orleans, Metairie, Kenner and the Northshore: missed calls answered, phone "
            "booking, reviews, and getting found on Google and in AI answers.")
    answer = [
        "<b>autoants</b> answers the calls your HVAC shop misses, follows up your quotes, lets customers book from "
        "the first phone screen and asks every customer for a review. We also keep your Google profile right and "
        "check what AI assistants say about you.",
        "We work with HVAC owners in New Orleans, Metairie, Kenner and the Northshore. It starts with a free "
        f"breakdown of your business; then it's {P_BOTH} for both, or {P_TRY} to try one "
        "assistant.",
    ]
    cards = [
        ("Missed calls answered",
         "Every missed call gets a text from your business within seconds, naming your shop. If you want the phone "
         "answered too, an AI can answer it, and it always says it's an AI.",
         "missed-calls-summer", "Missed calls in the July rush"),
        ("Booking on the first phone screen",
         "A Book button or a “next opening” box at the top of your site as it shows on a phone, tied to times "
         "your crew will keep.", "book-from-the-first-screen", "Can customers book you from a phone?"),
        ("Quotes followed up",
         "A quote that goes quiet gets a nudge. A reply stops it, and nothing goes out without your OK.", None, None),
        ("Pre-season tune-up reminders",
         "Past customers who agreed to hear from you get a reminder before the season, at no extra price inside "
         "Never miss a job.", None, None),
        ("Every customer asked for a review",
         "The same ask after every job, with your link. It never picks who gets asked and never pays for reviews.",
         "more-google-reviews", "More reviews, inside Google's rules"),
        ("Found on Google and in AI answers",
         "Your Google profile, listings and pages kept right, and a monthly check of what AI assistants say when "
         "someone asks for an AC company.", "show-up-in-ai-answers", "Showing up in AI answers"),
        ("A Spanish option",
         "Spanish pages for your site and the missed-call text and review ask in Spanish, each wording reviewed by a "
         "person who reads Spanish.", "spanish-line", "Do you need a Spanish line?"),
    ]
    card_html = '<div class="cards">' + "".join(
        f'<div class="card"><h3>{E(t)}</h3><p>{E(b)}</p>' +
        (f'<a class="go" href="{p}hvac/{s}/">{E(lt)} &rarr;</a>' if s else "") + "</div>"
        for t, b, s, lt in cards) + "</div>"
    stats = ('<div class="stats">' +
             stat("91&deg;F", "the normal July high in New Orleans, with about 23 days at 90&deg;F or hotter in July "
                  "alone", "NOAA normals 1991-2020, read Oct 20, 2026") +
             stat("16 of 45", "New Orleans-area HVAC websites had no way to book or request service on the first "
                  "phone screen", "autoants check, Oct 12, 2026") +
             stat("132 of 135", "HVAC websites in Orleans, Jefferson and St. Bernard showed no Spanish page on the "
                  "homepage", "autoants first-pass check, Oct 20, 2026") +
             stat("28", "different HVAC companies one AI assistant named across 24 answers about New Orleans; only 4 "
                  "came up in half or more", "autoants AI scan, Oct 19, 2026") +
             "</div>")
    numbers = table(["What", "The number", "Where it's from"], [
        ["Normal July high, New Orleans airport", "91.4&deg;F", "NOAA normals 1991-2020"],
        ["Days at 90&deg;F or hotter, June to August (normal)", "64", "NOAA normals 1991-2020"],
        ["Share of a normal year's cooling need that falls in June to August", "53%", "NOAA normals: 1,695 of 3,206 cooling degree days"],
        ["HVAC permits in Orleans Parish, Oct 2025 to Sep 2026", "2,022", "City of New Orleans open data, pulled Oct 14, 2026"],
        ["Share of those permits pulled by ten license holders", "50%", "City of New Orleans open data, pulled Oct 14, 2026"],
        ["Jefferson Parish residents (5 and over) who speak Spanish at home", "14.3%", "Census ACS 2020-2024, table C16001"],
        ["Kenner residents (5 and over) who speak Spanish at home", "23%", "Census ACS 2020-2024, table C16001"],
    ])
    prices = table(["What", "Price"], [
        ["<b>The free breakdown</b>: a 10-14 page look at how you show up on Google, in AI answers and next to the "
         "shops around you, made from public information", "Free"],
        ["<b>Get found and never miss a job</b>: missed calls answered, quotes followed up, appointments booked and "
         "reminded (pre-season tune-ups included), reviews requested, your Google profile kept right and posted to "
         "every week, your listings kept right, 2 new pages a month, what AI answers say about you checked every "
         "month, and your website kept up", P_BOTH],
        ["<b>Not ready? Try one</b>: one assistant on your phone (most shops start with texting back every missed "
         "call). Live within 7 days of your go (for texting, within 7 days of the carriers' approval), or the $500 "
         "back", P_TRY],
        ["<b>Never miss a job</b> alone: just the calls", P_NMJ],
        ["<b>Get found</b> alone: just Google and AI answers", P_GF],
        ["<b>Pay per job</b>: Never miss a job, paid by the job", P_PPJ],
        ["<b>AI phone answering</b>: an AI that answers when nobody can, always says it's an AI, and texts you the "
         "job", "Priced with you once you're on Get found and never miss a job; minutes written into the agreement"],
    ])
    body = f"""
  <h2>What we do for HVAC shops</h2>
  {card_html}

  <h2>The local numbers</h2>
  <p>Each number below has its source and the date we pulled it. Our own checks count sites; they never name them.</p>
  {stats}
  {numbers}
  {src_line("noaa", "permits", "acs")}
  <p>Two things the records can't tell you: how many calls <i>your</i> shop misses, and when. Permits track installs and replacements, not repair calls. So before we start, we count one real week of your own calls, nights and weekends included, and show you the same numbers every month after.</p>

  <h2>What it costs</h2>
  <p>Most shops need both, so that's where we start. Prices as on {link(p, "prices/", "autoants.com/prices")}, checked {TODAY_WORDS}.</p>
  {prices}
  <ul>
    <li>You own everything: your accounts, pages and customer list.</li>
    <li>90 days, then month to month. Cancel by email.</li>
    <li>We don't promise results. We count your calls and jobs before and after, and show you every month.</li>
    <li>Prices shown are for our first 3 shops. Texts and phone minutes run on your own account, billed to you directly.</li>
  </ul>

  <h2>What we never do</h2>
  <ul>
    <li>Let an AI pretend to be a person. It says it's an AI in its first sentence.</li>
    <li>Promise a number of calls, a spot on Google or a place in an AI answer.</li>
    <li>Pay for reviews, or pick which customers get asked.</li>
    <li>Text anyone who didn't contact you first or say yes to hearing from you.</li>
    <li>Let an AI quote a price, diagnose a system or promise an arrival time. Those stay with you.</li>
  </ul>
  <p>The full list: {link(p, "never/", "what each assistant never does")}.</p>

  <h2>Questions HVAC owners ask</h2>
  <ul>{"".join(f'<li><a class="in" href="{p}hvac/{s}/">{E(q)}</a></li>' for s, q in PAGES)}
    <li><a class="in" href="{p}questions/missed-call-text-back-hvac-new-orleans/">Who can set up a missed-call text-back for an HVAC business in New Orleans?</a></li>
    <li><a class="in" href="{p}compare/">How autoants compares with an answering service, a call center and doing it yourself</a></li>
  </ul>
"""
    graph = [
        ORG,
        {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": title, "description": desc,
         "inLanguage": "en-US", "datePublished": TODAY, "dateModified": TODAY,
         "publisher": {"@id": BASE + "/#organization"}, "about": {"@id": url + "#service"}},
        {"@type": "Service", "@id": url + "#service",
         "name": "autoants for HVAC companies",
         "serviceType": "Missed-call answering, booking, quote follow-up, review requests and local search for HVAC companies",
         "provider": {"@id": BASE + "/#organization"}, "areaServed": ORG["areaServed"],
         "audience": {"@type": "BusinessAudience", "audienceType": "HVAC and air conditioning companies"},
         "offers": [
             {"@type": "Offer", "name": "Get found and never miss a job", "price": "1250", "priceCurrency": "USD",
              "description": P_BOTH + ", for our first 3 shops", "url": BASE + "/prices/"},
             {"@type": "Offer", "name": "Try one", "price": "500", "priceCurrency": "USD",
              "description": "One assistant, $500 once, for our first 3 shops", "url": BASE + "/prices/"},
             {"@type": "Offer", "name": "The free breakdown", "price": "0", "priceCurrency": "USD",
              "url": BASE + "/prices/"}]},
        breadcrumb(None, None),
    ]
    srcs = ["noaa", "firstscreen", "spanishsites", "aien", "permits", "acs", "prices"]
    return page("hvac/", title + " · autoants", desc, title, crumbs(p), answer, body, None, srcs, graph, p,
                top_cta=True)


# ---------------------------------------------------------------- problem pages
def p_missed():
    slug, p = "missed-calls-summer", "../../"
    url = f"{BASE}/hvac/{slug}/"
    h1 = H1[slug]
    answer = [
        "Make sure every call gets an answer even when nobody can pick up: a text back from your business within "
        "seconds, an AI that answers and texts you the job, or both. In New Orleans the normal July high is "
        "91&deg;F with about 23 days at 90&deg;F or hotter, so a caller with no cool air has every reason to try the "
        "next shop.",
    ]
    heat = table(["Month", "Normal high", "Days at 90&deg;F+"], [
        ["May", "85.3&deg;F", "5.9"], ["June", "90.0&deg;F", "18.4"], ["July", "91.4&deg;F", "22.9"],
        ["August", "91.3&deg;F", "23.0"], ["September", "88.1&deg;F", "12.8"]])
    faq = [
        ("Does a missed-call text replace answering the phone?",
         "No. It holds the caller while you finish the job, and their reply comes straight to you. If you want calls "
         "answered too, that's AI phone answering: an AI that always says it's an AI and texts you the job."),
        ("When should an HVAC shop set this up?",
         "Before May. Business texting has to be registered with the carriers first, and that review usually takes "
         "two to three weeks."),
        ("What does it cost at autoants?",
         "The text-back on its own is Try one, $500 once. Never miss a job, with quote follow-up, booking, "
         "reminders and the review ask, is $750 a month + $750 setup. Both are prices for our first 3 shops."),
        ("Can you tell me how many calls my shop misses?",
         "Yes, for your own phone. Before we start we count one real week of your calls, nights and weekends "
         "included. We don't guess it from other shops."),
    ]
    body = f"""
  <h2>How hot it gets, month by month</h2>
  {heat}
  <p>About 53% of a normal year's cooling need lands in June, July and August (1,695 of 3,206 cooling degree days, a measure of how much cooling a year takes). New Orleans needs almost three times as much cooling as heating in a normal year.</p>
  {src_line("noaa")}

  <h2>What the city's records show, and what they don't</h2>
  <p>Orleans Parish issued 2,022 HVAC permits from October 2025 to September 2026. The busiest month was May (249) and the slowest was January (121); July had 196. But permits track installs and replacements, not repair calls, so no public record counts the summer repair rush. Your own phone does.</p>
  {src_line("permits")}

  <h2>Three ways to cover the calls you miss</h2>
  <ol>
    <li><b>Text back every missed call.</b> The caller gets a text from your business within seconds, naming your shop, with STOP to opt out. It never texts a call you answered, and never texts the same caller twice inside 12 hours. A landline can't receive it.</li>
    <li><b>Let an AI answer.</b> It says it's an AI in its first sentence, takes the details, texts you the job and passes a real emergency to a person by rules you write. It never quotes a price, diagnoses a system or promises an arrival time.</li>
    <li><b>Have a person answer.</b> An answering service or someone on staff. That's the better choice when callers need a person every time. See {link(p, "hvac/ai-receptionist-vs-answering-service/", "AI receptionist, answering service or a dispatcher")}.</li>
  </ol>
  <p>Most shops start with the first. The second covers nights and weekends.</p>

  <h2>Set it up in spring, not in July</h2>
  <ol>
    <li><b>Register for business texting.</b> Carriers block texts from unregistered business numbers, and the review usually takes two to three weeks. Your shop gets its own registration under your legal name. ({link(p, "rules/", "How we handle texts and calls")})</li>
    <li><b>Send tune-up reminders</b> to past customers who agreed to hear from you, so tune-ups get booked in spring, before the heat, while your crew has room.</li>
    <li><b>Put a way to book on the first phone screen</b>, so a customer who can't get through can still ask for a time. {link(p, "hvac/book-from-the-first-screen/", "16 of 45 local HVAC sites didn't have one")}.</li>
    <li><b>Make your Google hours honest.</b> Only list late hours if someone, or an AI on a line you approved, really answers then. A text-back alone doesn't make the shop open.</li>
  </ol>

  <h2>Count first, then decide</h2>
  <p>We count one real week of your calls before we recommend anything: how many rang out, and when (on a job, at lunch, after 5, on weekends). Then you see the same numbers every month. We don't promise a number; we show you yours.</p>
{related(p, slug)}
"""
    graph = [faq_ld(url, faq), breadcrumb(slug, h1), ORG]
    return page(f"hvac/{slug}/", "How HVAC companies stop missing calls in the July rush · autoants",
                "In New Orleans the normal July high is 91°F. How an HVAC shop covers the calls it can't pick up: "
                "a text back in seconds, an AI that answers, or both.",
                h1, crumbs(p, "Missed calls"), answer, body, faq, ["noaa", "permits", "rules", "prices"], graph, p)


def p_receptionist():
    slug, p = "ai-receptionist-vs-answering-service", "../../"
    url = f"{BASE}/hvac/{slug}/"
    h1 = H1[slug]
    answer = [
        "If you mostly lose calls while you're on a job or after hours, a missed-call text or an AI receptionist "
        "covers those calls without adding a person. If your callers need a person who can make judgment calls, an "
        "answering service or a dispatcher on staff is the better choice.",
    ]
    t = table(["Option", "Who answers", "What it costs", "Fits when"], [
        ["<b>Missed-call text-back</b> (autoants)", "Nobody by voice: a text from your business goes back within "
         "seconds", f"Try one, {P_TRY}; or inside Never miss a job, {P_NMJ}", "Calls ring out while techs are on "
         "jobs"],
        ["<b>AI receptionist</b> (autoants)", "An AI that says it's an AI in its first sentence, then texts you the "
         "job", "Priced with you once you're on Get found and never miss a job; minutes written into the agreement",
         "Nights, weekends, lunch, and techs on a roof"],
        ["<b>Answering service</b>", "Live people, often 24/7", "Published plans are priced by the minute; see our "
         f'{link(p, "compare/answering-service/", "dated comparison")}', "Callers expect a person every time"],
        ["<b>Dispatcher on staff</b>", "Your own person, during their hours", "Median pay for receptionists in the "
         "New Orleans metro: $35,750 a year, before benefits", "Steady calls all day, and techs to schedule"],
    ])
    faq = [
        ("Will callers know it's an AI?",
         "Yes. It says it's an AI in its first sentence, and again if anyone asks."),
        ("Can the AI book a tech?",
         "It takes the job details and texts them to you. You text back to approve before the customer hears yes."),
        ("What does the AI never do?",
         "It never quotes a price, diagnoses a system, promises an arrival time or takes a card number. Those calls "
         "go to you."),
        ("Can I keep my answering service?",
         "Yes. Some shops keep a live service for calls and use autoants for the text-back, quote follow-ups and "
         "booking."),
    ]
    body = f"""
  <h2>The four options side by side</h2>
  {t}
  {src_line("prices", "compare", "bls")}
  <p>We use the receptionist figure because it's the closest published local number. A dispatcher who also schedules techs and orders parts is a different job, and the pay depends on it.</p>

  <h2>How to decide, step by step</h2>
  <ol>
    <li><b>Count a week of missed calls, and when they happen.</b> On a job, at lunch, after 5, on weekends. We do this with you before we start.</li>
    <li><b>Mostly during the workday, while techs are busy?</b> Start with the missed-call text. It's the smallest step.</li>
    <li><b>Many after hours, and some are real emergencies?</b> AI answering with an emergency hand-off to a person, or a live answering service.</li>
    <li><b>You also need someone scheduling techs all day?</b> That's a dispatcher. The text-back or the AI can still cover nights and weekends.</li>
    <li><b>Callers who won't talk to an AI?</b> Some won't, and that's their call. A person is the better fit for them.</li>
  </ol>
  <p>You can mix them. The comparisons go deeper: {link(p, "compare/answering-service/", "autoants vs an answering service")} and {link(p, "compare/ai-receptionist-vs-call-center/", "an AI receptionist vs a call center")}.</p>
{related(p, slug)}
"""
    graph = [faq_ld(url, faq), breadcrumb(slug, h1), ORG]
    return page(f"hvac/{slug}/", "AI receptionist or answering service for HVAC? · autoants",
                "Missed-call text, an AI receptionist that says it's an AI, an answering service or a dispatcher: "
                "what each costs an HVAC shop, and how to decide.",
                h1, crumbs(p, "Answering the phone"), answer, body, faq, ["prices", "compare", "bls"], graph, p)


def p_booking():
    slug, p = "book-from-the-first-screen", "../../"
    url = f"{BASE}/hvac/{slug}/"
    h1 = H1[slug]
    answer = [
        "Many can't. When we opened New Orleans-area HVAC websites on a phone on October 12, 2026, 16 of the 45 that "
        "loaded had no way to book or request service on the first screen, and 10 of those had none anywhere on the "
        "homepage.",
        "The fix is a Book button or a “next opening” box at the top of the phone screen, tied to times your "
        "crew will actually keep.",
    ]
    t = table(["What the first phone screen showed", "Sites"], [
        ["A Book, Schedule or Request Service button, with no time promised (often it opens a contact form)", "22"],
        ["A button plus a time promise in words, such as “same-day”", "4"],
        ["A booking control, but below the first screen", "6"],
        ["No way to book or request service anywhere on the homepage", "10"],
        ["Unclear: says “book online” but we found no control", "3"],
        ["<b>Working sites counted</b>", "<b>45</b>"],
        ["Left out: didn't load, showed an error page or stayed blank", "6"],
    ])
    faq = [
        ("Isn't a phone number enough?",
         "Keep the phone number first. But a customer who can't get through, or who wants to book at 10 PM, needs a "
         "way to ask for a time without a call."),
        ("Do I need scheduling software for this?",
         "No. The box can show a time from your calendar or from a simple rule you set, and it says “same-day "
         "when available” when it can't check. It never shows a time your crew won't keep."),
        ("What does it cost at autoants?",
         "It can be your one assistant in Try one, $500 once, and it's included in Never miss a job, $750 a month + "
         "$750 setup. Both are prices for our first 3 shops."),
        ("Which sites didn't have a way to book?",
         "We count them; we don't name them."),
    ]
    body = f"""
  <h2>What we found on 45 local HVAC sites</h2>
  {t}
  {src_line("firstscreen")}
  <p>The 16 are the 6 with booking below the first screen plus the 10 with none at all. Even among the 26 with a button up top, only 4 said anything about when.</p>

  <h2>What a first phone screen that books has</h2>
  <ol>
    <li><b>A call button you can hit with a thumb</b>, top right, that dials the number it shows.</li>
    <li><b>A headline that says the service and the place</b>: “AC repair and installation in Metairie”, not a slogan.</li>
    <li><b>Two reassurances, not six</b>: the two your customers care about most, and only ones that are true.</li>
    <li><b>A Book or Request button</b>, or a box with the next opening, before any scrolling.</li>
    <li><b>A time only if the crew keeps it.</b> If the rule can't be checked, say “same-day when available”. A time that isn't real is the first promise a customer sees broken.</li>
  </ol>

  <h2>Check your own site in two minutes</h2>
  <ol>
    <li>Open your homepage on your phone. Don't scroll.</li>
    <li>Can you tap to book or request a visit from what you see?</li>
    <li>Tap the call button. Does it dial the number printed on it?</li>
    <li>Send yourself a request through the form. Does it reach your phone, and how fast?</li>
  </ol>
  <p>Or let us look: the free {link(p, "tools/first-screen/", "first-screen check")} sends you a picture of your first screen and the one change that would get more people to book. A person looks at every result.</p>
{related(p, slug)}
"""
    graph = [faq_ld(url, faq), breadcrumb(slug, h1), ORG]
    return page(f"hvac/{slug}/", "Can customers book your HVAC company from a phone? · autoants",
                "We opened New Orleans-area HVAC websites on a phone: 16 of the 45 that loaded had no way to book on the first screen. "
                "What a first screen that books has, and a 2-minute self-check.",
                h1, crumbs(p, "Booking from a phone"), answer, body, faq, ["firstscreen", "prices"], graph, p)


def p_reviews():
    slug, p = "more-google-reviews", "../../"
    url = f"{BASE}/hvac/{slug}/"
    h1 = H1[slug]
    answer = [
        "Ask every customer after every job, the same way, with a direct link, and never offer anything for the "
        "review. Google's rules ban rewarding customers for reviews and asking only the customers you expect to be "
        "happy.",
    ]
    t = table(["The rule", "Whose rule"], [
        ["No payment, discounts, or free goods or services in exchange for a review, or for changing or removing a "
         "negative one", "Google (Maps content policy and Business Profile help)"],
        ["Don't discourage negative reviews, and don't ask only for positive ones", "Google (Maps content policy)"],
        ["Don't require staff to get a set number of reviews, or reviews that say certain things",
         "Google (Maps content policy)"],
        ["No fake reviews, no buying reviews that must say something good (or bad), no undisclosed reviews by "
         "insiders, and no threats to keep reviews down", "FTC rule, 16 CFR Part 465, in effect since October 21, "
         "2024"],
        ["Asking only happy customers “could violate the FTC Act”, even though the rule doesn't name it",
         "FTC questions-and-answers page"],
    ])
    faq = [
        ("Can I give a discount for a review?",
         "Not for a Google review. Google's policy bans offering payment, discounts or free service in exchange for a "
         "review."),
        ("Can I ask only my happy customers?",
         "No. Google's policy says not to ask selectively for positive reviews, and the FTC says that could violate "
         "the FTC Act. Ask everyone."),
        ("Can my techs ask for reviews?",
         "Yes, the same way for every customer. Don't give techs a review quota or tell customers what to write; "
         "Google's policy bans both."),
        ("What does the review ask cost at autoants?",
         "It can be your one assistant in Try one, $500 once, and it's part of Never miss a job, $750 a month + $750 "
         "setup. Both are prices for our first 3 shops."),
    ]
    body = f"""
  <h2>What Google and the FTC say</h2>
  {t}
  {src_line("gmaps", "gbp", "ftc")}
  <p>This is a plain summary of public rules, not legal advice. The two differ in one place: the FTC rule allows some rewards for honest reviews, but Google doesn't allow any. On Google, follow Google.</p>

  <h2>A review ask that works for an HVAC shop</h2>
  <ol>
    <li><b>Send it the day the job is done</b>, while the house is cooling down and the visit is fresh.</li>
    <li><b>One message with your link</b>, your business name and STOP to opt out, only to customers who gave you their number for the job.</li>
    <li><b>Ask every customer</b>, including the callback and the one who complained. Skipping them is the gating Google bans.</li>
    <li><b>It's fine to say</b> “if you can, mention what we did and your neighborhood.” Never write the review for them.</li>
    <li><b>Reply to every review within a day or two</b>, bad ones too, in plain words. Never confirm private details about a customer in a reply.</li>
  </ol>

  <h2>Why it matters past Google</h2>
  <p>AI assistants read reviews too, and not only Google's. In BrightLocal's US study, 80% of ChatGPT's answers to local searches cited Yelp as a source. Keep your other listings complete and correct, with the same name and phone everywhere.</p>
  {src_line("brightlocal")}

  <h2>What autoants does</h2>
  <p>The review assistant sends the same ask to every customer after every job, one tap from your phone, and you approve the wording before anything goes out. It never picks who gets asked and never pays for reviews. With Get found, replies to your new reviews are drafted for you every week. More: {link(p, "questions/more-google-reviews-home-service-new-orleans/", "getting more Google reviews for a home service business")}.</p>
{related(p, slug)}
"""
    graph = [faq_ld(url, faq), breadcrumb(slug, h1), ORG]
    return page(f"hvac/{slug}/", "More Google reviews for HVAC, inside Google's rules · autoants",
                "Ask every customer the same way and never reward a review. Google's and the FTC's rules in plain "
                "words, and a review ask that works for an HVAC shop.",
                h1, crumbs(p, "Reviews"), answer, body, faq, ["gmaps", "gbp", "ftc", "brightlocal", "prices"], graph, p)


def p_ai():
    slug, p = "show-up-in-ai-answers", "../../"
    url = f"{BASE}/hvac/{slug}/"
    h1 = H1[slug]
    answer = [
        "AI assistants name the companies they can find and trust in what they read: your website, your Google "
        "profile, directory listings and reviews. Nobody can promise you a spot in the answer, and the names change "
        "from one answer to the next, so the work is fixing what the answers read and checking again every month.",
    ]
    t = table(["Asked about", "Answers", "Companies named", "Named in half or more", "Named once"], [
        ["New Orleans", "24", "28", "4", "8"],
        ["Kenner", "24", "27", "5", "9"],
        ["Slidell", "24", "33", "4", "13"],
    ])
    faq = [
        ("Can you get my company to the top of ChatGPT?",
         "No one can honestly promise that. The answers change from one run to the next. We measure who gets named "
         "for your customers' questions every month and fix what the answers read."),
        ("Which AI assistant do you check?",
         "Our scans run today on Claude with web search on, asking each question more than once. For your own site "
         "we also read Google's AI report in Search Console, with your access."),
        ("Do I pay to be listed in an AI answer?",
         "There's no honest way to buy a place in an AI answer, and we don't sell one. No paid placements, no fake "
         "reviews and no planted mentions."),
        ("What does it cost at autoants?",
         "The monthly AI-answer check is part of Get found, $750 a month + $250 setup, and of Get found and never "
         "miss a job, $1,250 a month + $1,000 setup. Both are prices for our first 3 shops."),
    ]
    body = f"""
  <h2>What one AI said when we asked</h2>
  <p>We asked one AI assistant the same 8 homeowner questions about air conditioning companies, 3 times each, for three places. This is a snapshot from one AI on one date, not a ranking.</p>
  {t}
  {src_line("aien")}
  <p>What it shows: the answers spread across many companies, and most come and go. Across 24 answers about New Orleans, only 4 companies came up in half or more, and 8 came up once. A shop that's in today's answer can be missing from the next one. Being named for one town doesn't mean being named for the next: in our checks, a shop named often for its home town was missing from answers about the city next door. Each town you serve needs its own pages and listings. Our monthly public record of these answers is the {link(p, "ai-index/", "New Orleans AI Recommendation Index")}.</p>

  <h2>What the answers read</h2>
  <ul>
    <li><b>Your own site:</b> a page for each service and each town you serve, with plain answers to the questions callers ask.</li>
    <li><b>Your Google profile:</b> the right category, hours, services and photos, matching the site.</li>
    <li><b>Listings:</b> the directories the answers cite, with your name and phone the same everywhere. That includes Apple Maps, which Siri uses for places, and Bing Places.</li>
    <li><b>Reviews:</b> real ones, asked of every customer. In BrightLocal's US study, 80% of ChatGPT's answers to local searches cited Yelp. ({link(p, "hvac/more-google-reviews/", "How to ask inside Google's rules")})</li>
  </ul>
  {src_line("brightlocal")}

  <h2>Measure it yourself</h2>
  <ol>
    <li>Ask an AI assistant what your customers would ask: “My AC stopped blowing cold in Metairie. Who can come today?” Ask it three times and write down every company it names.</li>
    <li>Open the sources the answer cites. Those are the pages it trusted. Is your shop on them?</li>
    <li>Open Google Search Console for your site. Since August 31, 2026 it shows how often your pages appear in Google's AI Overviews and AI Mode.</li>
  </ol>
  {src_line("gsc")}

  <h2>What autoants does, and won't do</h2>
  <p>With Get found, we ask the questions your customers ask every month, record who gets named and which sites the answers cite, and fix your profile, listings and pages. We fix real signals only. We never promise a rank. More: {link(p, "questions/show-up-in-chatgpt-contractor-new-orleans/", "how a New Orleans contractor gets named by ChatGPT")}.</p>
{related(p, slug)}
"""
    graph = [faq_ld(url, faq), breadcrumb(slug, h1), ORG]
    return page(f"hvac/{slug}/", "HVAC companies in ChatGPT and Google AI answers · autoants",
                "What AI assistants read before they name an AC company, what one AI said about New Orleans, Kenner "
                "and Slidell, and how to check it yourself. No rank promises.",
                h1, crumbs(p, "AI answers"), answer, body, faq, ["aien", "brightlocal", "gsc", "prices"], graph, p)


def p_spanish():
    slug, p = "spanish-line", "../../"
    url = f"{BASE}/hvac/{slug}/"
    h1 = H1[slug]
    answer = [
        "If you work in Jefferson Parish, it's worth a look: about 1 in 7 residents there (age 5 and over) speaks Spanish at home, and "
        "of 135 HVAC websites we checked across Orleans, Jefferson and St. Bernard, 132 showed no Spanish page.",
        "When we asked an AI assistant, in Spanish, for a Kenner AC company that serves customers in Spanish, it said "
        "both times that it couldn't find one that advertises it.",
    ]
    people = table(["Area", "Speak Spanish at home", "Speak Spanish, and English less than very well"], [
        ["Kenner", "23%", "12%"],
        ["Jefferson Parish", "14.3% (57,674 people)", "7.3%"],
        ["St. Bernard Parish", "6.5% (2,685 people)", "3.0%"],
        ["Orleans Parish", "5.3% (18,584 people)", "1.9%"],
    ])
    sites = table(["Where", "HVAC sites checked", "No Spanish page"], [
        ["Orleans, Jefferson and St. Bernard", "135", "132"],
        ["Metairie", "36", "35"],
        ["New Orleans", "32", "32"],
        ["Kenner", "26", "25"],
    ])
    faq = [
        ("Is a translate button on my site enough?",
         "It helps someone who is already on your site. A page written in Spanish, for the way people search in "
         "Spanish, is what a search engine or an AI assistant can find and quote."),
        ("Do I need someone on staff who speaks Spanish?",
         "Not for Spanish pages or Spanish texts. Only say “se habla español” if a person who answers "
         "your phone does."),
        ("What does a Spanish option cost at autoants?",
         "It isn't on our price list yet. We scope it with you in writing before any work starts."),
        ("Who sees the Spanish pages?",
         "Anyone who searches. We never pick people by language or background. We use public area counts from the "
         "Census, and your own website, Google profile and customers."),
    ]
    body = f"""
  <h2>Who speaks Spanish at home, by area</h2>
  {people}
  {src_line("acs")}
  <p>Residents 5 and over. These are survey estimates averaged over 2020-2024, with a margin of error.</p>

  <h2>How many local HVAC sites have a Spanish page</h2>
  {sites}
  {src_line("spanishsites")}

  <h2>What an AI said when asked in Spanish</h2>
  <p>We asked one AI assistant 8 questions in Spanish that a customer in Kenner might ask about air conditioning. It named 27 different companies across the 8 answers. Twice we asked it for a company that serves customers in Spanish (“Necesito una compañía de aire acondicionado en Kenner que hable español”). Both times it said it couldn't find an air conditioning company in Kenner that advertises service in Spanish, and told the caller to ask each company directly.</p>
  {src_line("aies")}
  <p>One AI, one date, one run of each question. It does show the gap: a shop that says it in Spanish, on its own site, has something for the answer to find.</p>

  <h2>What a Spanish option means</h2>
  <ol>
    <li><b>Spanish pages written for Spanish searches</b>, such as “reparación de aire acondicionado en Kenner”, not a word-for-word copy of the English.</li>
    <li><b>Your Google profile services in Spanish</b>, and the same facts in both languages: phone, hours, area served.</li>
    <li><b>The missed-call text and the review ask in Spanish</b>, or in both languages.</li>
    <li><b>A person who reads Spanish reviews every wording</b> before it goes out. Prices and promises stay the same in both languages.</li>
  </ol>

  <h2>What we won't do</h2>
  <ul>
    <li>Pick people by language, name or background. Area counts and your own channels only.</li>
    <li>Call a page a “certified translation”.</li>
    <li>Say “se habla español” for you unless someone at your shop does.</li>
  </ul>
{related(p, slug)}
"""
    graph = [faq_ld(url, faq), breadcrumb(slug, h1), ORG]
    return page(f"hvac/{slug}/", "A Spanish line for HVAC companies around New Orleans · autoants",
                "About 1 in 7 Jefferson Parish residents speak Spanish at home, and 132 of 135 local HVAC sites we "
                "checked had no Spanish page. What a Spanish option means.",
                h1, crumbs(p, "Spanish"), answer, body, faq, ["acs", "spanishsites", "aies"], graph, p)


BUILDERS = [("hvac/index.html", hub), ("hvac/missed-calls-summer/index.html", p_missed),
            ("hvac/ai-receptionist-vs-answering-service/index.html", p_receptionist),
            ("hvac/book-from-the-first-screen/index.html", p_booking),
            ("hvac/more-google-reviews/index.html", p_reviews),
            ("hvac/show-up-in-ai-answers/index.html", p_ai),
            ("hvac/spanish-line/index.html", p_spanish)]


def main():
    check = "--check" in sys.argv
    bad = 0
    for rel, fn in BUILDERS:
        out = fn()
        path = os.path.join(SITE, rel)
        if check:
            cur = open(path).read() if os.path.exists(path) else ""
            if cur != out:
                print("differs:", rel)
                bad = 1
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(out)
        print("wrote", rel)
    sys.exit(bad)


if __name__ == "__main__":
    main()
