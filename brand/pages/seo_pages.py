#!/usr/bin/env python3
"""Service pages and town pages for autoants.com (SEO sprint, 2026-11-19).

    python3 brand/pages/seo_pages.py          # write the pages and add them to sitemap.xml
    python3 brand/pages/ai_readable.py        # then rebuild the markdown twins and llms.txt

Pages written (edit the content here, never the outputs):
  /missed-call-answering/   Catch missed calls, explained as a service page
  /get-found/               Get Found, titled with the Google profile's secondary category (Internet marketing service)
  /new-business-launch/     the $750 launch pack (wording from /start-a-business/)
  /areas/                   the service-area hub
  /areas/new-orleans/, /areas/metairie/, /areas/kenner/
                            town pages titled with the profile's primary category (Marketing agency) + town; each
                            carries facts only that town has (its licence path, our own dated AI checks, public data)

Copy rules (house): no "#1", no guarantees, no timing promises, never say Google's AI calls run in Louisiana, the
tagline stays "Automated assistants for local businesses.", no price ending in 9, the client owns everything.
The FAQ JSON-LD is built from the same strings as the visible FAQ, so the two can't drift.
Standard library only.
"""
import datetime, html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, "..", ".."))
BASE = "https://autoants.com/"
TODAY = "2026-11-19"
PHONE, TEL = "(504) 499-1194", "+15044991194"
TAGLINE = "Automated assistants for local businesses."
E = html.escape

PLACES = {
    "New Orleans": {"@type": "City", "name": "New Orleans", "sameAs": [
        "https://www.wikidata.org/wiki/Q34404", "https://en.wikipedia.org/wiki/New_Orleans",
        "https://www.google.com/search?kgmid=/m/0f2tj"]},
    "Metairie": {"@type": "City", "name": "Metairie, LA", "sameAs": [
        "https://www.wikidata.org/wiki/Q126661", "https://en.wikipedia.org/wiki/Metairie,_Louisiana",
        "https://www.google.com/search?kgmid=/m/01_gvm3"]},
    "Kenner": {"@type": "City", "name": "Kenner, LA", "sameAs": [
        "https://www.wikidata.org/wiki/Q991464", "https://en.wikipedia.org/wiki/Kenner,_Louisiana",
        "https://www.google.com/search?kgmid=/m/01_gv32"]},
}

ORG = {"@type": "ProfessionalService", "@id": BASE + "#business", "name": "autoants", "url": BASE,
       "telephone": "+1-504-499-1194", "email": "hello@autoants.com", "slogan": TAGLINE,
       "founder": {"@type": "Person", "name": "Lane Davis II", "url": BASE + "about-lane/"},
       "sameAs": ["https://www.instagram.com/autoants/"]}

FINE_PRINT = ("Prices shown are for our first 3 shops. You own everything: your accounts, pages, listings and customer "
              "list. Monthly plans run 90 days, then month to month. No promised results: we count your calls and jobs "
              "before we start and show you the same numbers every month.")

FREE_FIRST = ("<p><b>Free first:</b> a breakdown of your business: how you show up on Google, in AI answers and next to "
              "your competitors. It shows which fix your numbers need.</p>")

SERVICES_NAV = [("/missed-call-answering/", "Missed-call answering"), ("/get-found/", "Get found on Google and AI answers"),
                ("/new-business-launch/", "New Business Launch"), ("/areas/", "Where we work"),
                ("/areas/new-orleans/", "New Orleans"), ("/areas/metairie/", "Metairie"), ("/areas/kenner/", "Kenner")]

SRC = {
    "google-ai-calls": ("Google Business Profile Help, \"Manage how Google calls your business\" (lists the states where "
                        "the feature isn't available)", "https://support.google.com/business/answer/7690269",
                        "November 18, 2026"),
    "works-with": ("autoants, What it connects to", "https://autoants.com/works-with/", "November 19, 2026"),
    "never": ("autoants, What it never does", "https://autoants.com/never/", "November 19, 2026"),
    "rules": ("autoants, Texts and calls", "https://autoants.com/rules/", "November 19, 2026"),
    "prices": ("autoants, Prices", "https://autoants.com/prices/", "November 19, 2026"),
    "checklist": ("autoants, Starting a business in Louisiana: a free checklist (every official link)",
                  "https://autoants.com/start-a-business/", "November 10, 2026"),
    "permits": ("City of New Orleans permits, data.nola.gov dataset 72f9-bi28 (pulled October 8, 2026)",
                "https://data.nola.gov/d/72f9-bi28", "October 8, 2026"),
    "onestop": ("City of New Orleans One Stop (occupational licenses)", "https://onestopapp.nola.gov/", "November 10, 2026"),
    "jpso": ("Jefferson Parish Sheriff's Office, Bureau of Revenue and Taxation", "https://www.jpso.com/",
             "November 10, 2026"),
    "acs": ("U.S. Census Bureau, American Community Survey 2020-2024, as cited on our Spanish line page",
            "https://autoants.com/hvac/spanish-line/", "October 20, 2026"),
    "aiscan-hvac": ("autoants AI-visibility scans of New Orleans, Metairie and Kenner HVAC questions (one AI assistant, "
                    "Claude, web search on; our own logs, November 10 and 11, 2026)", "", "November 11, 2026"),
    "aiscan-oct": ("autoants, How does an HVAC company show up when people ask ChatGPT, Claude or Google's AI? (scan of "
                   "October 19, 2026)", "https://autoants.com/hvac/show-up-in-ai-answers/", "October 19, 2026"),
    "guide-kenner": ("autoants New Orleans guide: landscaping and tree service in Kenner, from state and parish license "
                     "lists", "https://autoants.com/nola/landscaping/kenner/", "November 19, 2026"),
}


def head(path, title, desc):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{BASE}{path}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{BASE}{path}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#0b1712">
<link rel="icon" href="/favicon-96.png" type="image/png" sizes="96x96">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="icon" href="/brand/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@500;700;800&family=JetBrains+Mono:wght@700&display=swap">
<link rel="stylesheet" href="/assets/trust.css">
<link rel="stylesheet" href="/assets/compare.css">
<style>.callrow{{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}}.tagline{{color:var(--muted);margin:-4px 0 14px}}</style>
</head>
<body>
<div class="wrap">
  <nav class="top" aria-label="Site">
    <a class="logo" href="/" aria-label="autoants home"><img class="on-light" src="/brand/autoants-logo.svg" alt="autoants"><img class="on-dark" src="/brand/autoants-logo-reverse.svg" alt="autoants"></a>
    <span class="sp"></span>
    <a class="ghost" href="/prices/">Prices</a>
    <a class="ghost" href="tel:{TEL}">Call {PHONE}</a>
  </nav>
  <main id="main">
"""


def call_card():
    return (f'    <div class="card free">\n      {FREE_FIRST}\n      <div class="callrow"><a class="btn" href="tel:{TEL}">'
            f'Call or text {PHONE}</a> <a class="btn" href="/book/">Book a free breakdown</a></div>\n    </div>\n')


def faq_html(faq):
    return '    <h2>Questions</h2>\n    <div class="faq">' + "".join(
        f"<h3>{E(q)}</h3><p>{E(a)}</p>" for q, a in faq) + "</div>\n"


def sources_html(keys):
    items = "".join(f'<li>{E(SRC[k][0])}. '
                    + (f'<a href="{E(SRC[k][1])}">{E(SRC[k][1].split("://", 1)[1])}</a>. ' if SRC[k][1] else "")
                    + f'Checked {E(SRC[k][2])}.</li>' for k in keys)
    return f'    <h2>Sources</h2>\n    <ol class="sources">{items}</ol>\n'


def tail(path, faq, extra_ld):
    nav = "".join(f'<li><a href="{h}"' + (' aria-current="page"' if h == "/" + path else "") + f">{E(t)}</a></li>"
                  for h, t in SERVICES_NAV)
    lds = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]
    lds += extra_ld
    crumbs = [("autoants", BASE)]
    if path.startswith("areas/") and path != "areas/":
        crumbs.append(("Where we work", BASE + "areas/"))
    crumbs.append((None, BASE + path))
    lds.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n or "this page", "item": u} for i, (n, u) in enumerate(crumbs)]})
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in lds)
    return f"""  </main>
  <nav class="more" aria-label="Services and service areas">
    <p class="small">Services and service areas</p>
    <ul>{nav}</ul>
  </nav>
  <footer class="foot">autoants, short for automated assistants · New Orleans · <a href="/privacy.html">Privacy</a> · <a href="/facts/">Facts</a> · <a href="mailto:hello@autoants.com">hello@autoants.com</a> · <a href="tel:{TEL}">{PHONE}</a></footer>
</div>
{ld}</body>
</html>
"""


def ul(items):
    return "    <ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>\n"


def ol(items):
    return "    <ol>" + "".join(f"<li>{x}</li>" for x in items) + "</ol>\n"


def fix_breadcrumb_name(lds_page, name):
    return lds_page.replace('"name": "this page"', '"name": ' + json.dumps(name, ensure_ascii=False))


def page(path, title, desc, eyebrow, h1, body, faq, sources, extra_ld, crumb):
    out = head(path, title, desc)
    out += f'    <p class="eyebrow">{E(eyebrow)}</p>\n    <h1>{E(h1)}</h1>\n    <p class="tagline">{E(TAGLINE)}</p>\n'
    out += f'    <p class="meta">Updated {datetime.date.fromisoformat(TODAY).strftime("%B %-d, %Y")}</p>\n'
    out += body + call_card() + f'    <p class="small">{E(FINE_PRINT)}</p>\n' + faq_html(faq) + sources_html(sources)
    out += tail(path, faq, extra_ld)
    return fix_breadcrumb_name(out, crumb)


def service_ld(path, name, desc, offers, area=("New Orleans", "Metairie", "Kenner")):
    return {"@context": "https://schema.org", "@type": "Service", "name": name, "url": BASE + path,
            "description": desc, "provider": ORG, "areaServed": [PLACES[a] for a in area],
            "offers": [{"@type": "Offer", "name": n, "price": p, "priceCurrency": "USD", "description": d}
                       for n, p, d in offers]}


def town_ld(path, town, desc):
    o = dict(ORG)
    o.update({"description": desc, "areaServed": PLACES[town], "url": BASE + path,
              "contactPoint": {"@type": "ContactPoint", "telephone": "+1-504-499-1194", "contactType": "sales",
                               "areaServed": "US-LA", "availableLanguage": "English"}})
    o["@context"] = "https://schema.org"
    o["@id"] = BASE + path + "#business"
    return o


PRICE_LINES = [
    "Get Found and catch missed calls: $1,250 a month + $1,250 setup.",
    "Catch missed calls alone: $750 a month + $750 setup. Get Found alone: $750 a month + $500 setup.",
    "Not ready? Try one assistant: $500 once. If you upgrade within 30 days, the $500 counts toward setup.",
    "New Business Launch, for a business that's just starting: $750 one time.",
]

PAGES = {}

# ---------------------------------------------------------------- /missed-call-answering/
p = "missed-call-answering/"
faq = [
    ("Is this an answering service?",
     "No. An answering service puts a person on your calls. autoants texts back the calls you miss, follows up your "
     "quotes and books appointments. A voice answer is the AI receptionist, and it always says it's an AI."),
    ("Do I have to change my phone number?",
     "No. You keep your number and customers keep calling it. Calls you don't answer forward to the assistant, your "
     "number is never moved, and you can turn forwarding off yourself."),
    ("When can the texts start?",
     "Business texts have to be registered with the phone carriers first, under your business's name. We file the "
     "registration the day you say yes and tell you the go-live date in writing."),
    ("Will Google's AI call my business for customers?",
     "Not in Louisiana. Google's help page lists Louisiana as one of five states where its automated calls to "
     "businesses aren't available (checked November 18, 2026). The calls that count here come from people."),
    ("Do you promise more jobs?",
     "No. We count your missed calls and booked jobs for one real week before we start, then show you the same "
     "numbers every month."),
    ("Who owns the number and the customer list?",
     "You do. Texting runs on an account in your business's name, and your customer list, pages and listings stay "
     "yours if you leave."),
]
body = (
    '    <p class="answer">When a call to your business rings out, autoants texts the caller back once, naming your '
    "business, and every reply comes to your phone. Quotes get followed up, appointments get booked and reminded, and "
    "every customer is asked for a review. It's our Catch missed calls plan: $750 a month + $750 setup for our first 3 "
    "shops. Not ready? Try one assistant for $500 once.</p>\n"
    "    <h2>What happens when a call rings out</h2>\n"
    + ol(["You keep your number. Calls you don't answer forward to the assistant, and you can turn forwarding off "
          "yourself.",
          "The caller gets one text back that names your business and lets them reply STOP. A landline can't receive "
          "it.",
          "Their reply comes to you, tagged, so you decide what happens next.",
          "Add the AI receptionist and a voice answers instead. It says it's an AI in its first sentence and texts you "
          "the job."])
    + "    <h2>What it won't do</h2>\n"
    + ul(["Quote a price, promise a time or give out an address.",
          "Text anyone who didn't contact you first.",
          "Send a new kind of message before you've approved the wording.",
          "Stand in for you when someone wants a person: they get passed to you."])
    + "    <h2>Why this matters in Louisiana</h2>\n"
    "    <p>Google's automated calls to businesses aren't available in Louisiana; its help page lists Louisiana as one "
    "of five states left out (checked November 18, 2026). So the calls that count here come from people, and the fix "
    "is plain: answer them, keep your Google hours honest, and follow up the ones you miss.</p>\n"
    "    <h2>What it costs</h2>\n"
    + ul(["Catch missed calls: $750 a month + $750 setup.",
          "Pay per job instead: $250 a month + $25 a job, never more than $750. Jobs that cancel are never billed.",
          "Need Google too? Get Found and catch missed calls: $1,250 a month + $1,250 setup.",
          "Try one: $500 once. If you upgrade within 30 days, the $500 counts toward setup."])
    + '    <p>Every price is on <a href="/prices/">one page</a>. Built for trades first: <a href="/hvac/">HVAC</a>, '
    '<a href="/plumbing/">plumbing</a>, <a href="/roofing/">roofing</a> and <a href="/electrical/">electrical</a>.</p>\n'
)
desc = ("When a call rings out, autoants texts the caller back, naming your business, and sends you the reply. "
        "Catch missed calls: $750 a month + $750 setup.")
PAGES[p] = page(p, "Missed-Call Answering for New Orleans Businesses · autoants", desc, "Catch missed calls",
                "Missed-call answering for New Orleans businesses", body, faq,
                ["google-ai-calls", "works-with", "never", "rules", "prices"],
                [service_ld(p, "Missed-call answering (Catch missed calls)", desc,
                            [("Catch missed calls", "750", "$750 a month + $750 setup, first 3 shops"),
                             ("Try one", "500", "$500 once, one assistant")])],
                "Missed-call answering")

# ---------------------------------------------------------------- /get-found/
p = "get-found/"
faq = [
    ("Will you get me to the top of Google?",
     "Nobody can promise that. We fix what Google and AI answers read, then count calls, booked jobs and how often "
     "you're named, before and after."),
    ("Do I keep my Google profile?",
     "Yes. You stay the Primary Owner. We're added as a Manager, which can't remove you or delete the profile, and we "
     "never ask for your password."),
    ("How is this different from SEO I've paid for before?",
     "You see the work as counts you can check: listings fixed, pages added, how many AI answers named you, and the "
     "calls that came in. No 50-keyword ranking report."),
    ("Do you buy links or directory packages?",
     "No. Real local links only: chambers, associations, partners and local news. No link packages."),
    ("Do you ask only happy customers for reviews?",
     "No. We ask every customer, the same way every time. Asking only happy customers is review gating, and Google "
     "bans it."),
]
body = (
    '    <p class="answer">Get Found keeps your Google Business Profile right and posted to every week, keeps your '
    "listings matching, adds 2 new pages a month, drafts your review replies, keeps your website up, and checks every "
    "month what AI assistants like ChatGPT say about you. It's $750 a month + $500 setup for our first 3 shops, or "
    "$1,250 a month + $1,250 setup with Catch missed calls.</p>\n"
    "    <h2>What we do, in order</h2>\n"
    + ol(["<b>Your Google profile.</b> The truest primary category, your real services with plain descriptions, every "
          "true attribute, honest hours and real job photos. You stay the owner; we're added as a Manager.",
          "<b>Your listings.</b> Google, Apple, Bing, Yelp, Facebook, BBB, Nextdoor and your trade's directories, with "
          "the same name, phone and website on every one. You do only the verification steps, like a video check.",
          "<b>Your pages.</b> One page per service, and real pages for the towns you work, each with something only "
          "you can say. Two new pages a month.",
          "<b>Your reviews.</b> Every customer asked, the same way every time, and a drafted reply to every review, "
          "good or bad.",
          "<b>AI answers.</b> Every month we ask ChatGPT, Claude and the others the questions your customers ask, and "
          "report how many answers named you. Then we fix what those answers read.",
          "<b>Your email.</b> Business email on your own domain set up so quotes don't land in spam."])
    + "    <h2>How we report it</h2>\n"
    "    <p>Counts, not ranks: \"named in 4 of 9 answers, up from 1 of 9\", calls from your Google profile, and booked "
    "jobs. AI answers change from one ask to the next: in October, one AI assistant named 28 different companies "
    "across 24 answers about New Orleans HVAC, so we count over many asks, never one.</p>\n"
    "    <h2>What it costs</h2>\n"
    + ul(["Get Found: $750 a month + $500 setup. Setup includes your listings and business email.",
          "Get Found and catch missed calls: $1,250 a month + $1,250 setup.",
          "New website, if you need one: $1,000 once, free with Get Found and catch missed calls."])
    + '    <p>Just starting a business? See the <a href="/new-business-launch/">New Business Launch</a>. Every price is '
    'on <a href="/prices/">one page</a>.</p>\n'
)
desc = ("Your Google profile and listings kept right, 2 new pages a month, and what AI answers say about you checked "
        "monthly. Get Found: $750 a month + $500 setup.")
PAGES[p] = page(p, "Internet Marketing Service in New Orleans: Get Found · autoants", desc, "Get Found",
                "Internet marketing service in New Orleans: get found on Google and in AI answers", body, faq,
                ["aiscan-oct", "prices"],
                [service_ld(p, "Get Found (Google profile, listings, pages, AI answers)", desc,
                            [("Get Found", "750", "$750 a month + $500 setup, first 3 shops"),
                             ("Get Found and catch missed calls", "1250", "$1,250 a month + $1,250 setup, first 3 shops")])],
                "Get Found")

# ---------------------------------------------------------------- /new-business-launch/
p = "new-business-launch/"
faq = [
    ("How much is the New Business Launch?",
     "$750 one time. There's no monthly fee unless you choose a plan later."),
    ("Who owns the website and the Google profile?",
     "You do. The domain, the site files, the email admin login and the Google profile are in your name."),
    ("Can you verify my Google profile for me?",
     "No. Google asks the owner to verify, often with a short video of the business. We prepare everything and walk "
     "you through it."),
    ("Do you set up my LLC?",
     "No. Forming an entity is a legal step. File it yourself, or use an attorney or a formation service. Our free "
     "checklist links every official step."),
]
body = (
    '    <p class="answer">The autoants New Business Launch, $750 one time: your website live, your Google Business '
    "Profile set up and verified, business email on your own domain set up so quotes don't land in spam, and your "
    "first 30 days of posts. When you're ready for more, the next step is Catch missed calls: $750 a month + $750 "
    "setup.</p>\n"
    "    <h2>Who it's for</h2>\n"
    "    <p>A business that just got its license or opened its doors around New Orleans and isn't on Google yet, or is "
    "there with a half-finished profile.</p>\n"
    "    <h2>What you get</h2>\n"
    + ul(["Your website live on your own domain. The domain and the files are yours.",
          "Your Google Business Profile set up: the right category, your services, honest hours and real photos. You "
          "stay the Primary Owner.",
          "Business email on your own domain, with the records that keep quotes out of spam. You pay the email "
          "provider directly and keep the admin login.",
          "Your first 30 days of posts on the profile, from real photos you approve.",
          "The same name, phone and website on every listing from the start."])
    + "    <h2>What we don't do</h2>\n"
    "    <p>We don't form your LLC or file legal documents. That's a legal step: file it yourself, or use an attorney or "
    'a formation service. Our <a href="/start-a-business/">free start-a-business checklist</a> links each official '
    "step.</p>\n"
    "    <h2>The local license, by town</h2>\n"
    + ul(['<a href="/areas/new-orleans/">New Orleans</a>: the City\'s One Stop site, then the Amended Return to the '
          "Bureau of Revenue.",
          '<a href="/areas/metairie/">Metairie</a>: a zoning clearance, then the Jefferson Parish Sheriff\'s Office '
          "Bureau of Revenue and Taxation.",
          '<a href="/areas/kenner/">Kenner</a>: the license is paid to the City of Kenner, and you still register with '
          "the Bureau."])
)
desc = ("For new businesses around New Orleans: your website live, your Google Business Profile set up and verified, "
        "business email and 30 days of posts. $750 one time.")
PAGES[p] = page(p, "New Business Launch: Website and Google Profile · autoants", desc, "New Business Launch",
                "New Business Launch: your website, Google profile and email, set up", body, faq,
                ["checklist", "prices"],
                [service_ld(p, "New Business Launch", desc,
                            [("New Business Launch", "750", "$750 one time")])],
                "New Business Launch")

# ---------------------------------------------------------------- town pages


def town(slug, name, title, h1, answer, seen, start, faq, sources, desc):
    p = f"areas/{slug}/"
    body = (f'    <p class="answer">{answer}</p>\n    <h2>What we\'ve seen in {E(name)}</h2>\n' + ul(seen)
            + f"    <h2>Starting a business in {E(name)}?</h2>\n    <p>{start}</p>\n"
            + f"    <h2>What we do for {E(name)} businesses</h2>\n"
            + ul(['<a href="/missed-call-answering/">Missed-call answering</a>: the calls you miss texted back, quotes '
                  "followed up, jobs booked.",
                  '<a href="/get-found/">Get found</a>: your Google profile, listings, pages and what AI answers say '
                  "about you.",
                  '<a href="/new-business-launch/">New Business Launch</a>: a new business on Google, with a website '
                  "and email, from the start.",
                  'Trades first: <a href="/hvac/">HVAC</a>, <a href="/plumbing/">plumbing</a>, '
                  '<a href="/roofing/">roofing</a>, <a href="/electrical/">electrical</a>.'])
            + "    <h2>Prices</h2>\n" + ul(PRICE_LINES))
    PAGES[p] = page(p, title, desc, name, h1, body, faq, sources, [town_ld(p, name, desc)], name)


COMMON_FAQ_PROMISE = ("Do you promise more calls?",
                      "No. We count your calls and booked jobs for one real week before we start, then show you the "
                      "same numbers every month.")

town("new-orleans", "New Orleans", "Marketing Agency in New Orleans, LA · autoants",
     "Marketing agency in New Orleans, LA",
     "autoants is based in New Orleans. We set up automated assistants that answer the calls local businesses miss, "
     "follow up their quotes, and get them found on Google and in AI answers. Call or text "
     f'<a href="tel:{TEL}">{PHONE}</a>.',
     ["HVAC permits in New Orleans peak in April and May and again in October, not in summer, and re-roof permits "
      "peak in April, about 49% above an average month (City permit data, pulled October 8, 2026). Those are the "
      "months a missed call costs the most.",
      "We asked one AI assistant twice who to call for AC repair in New Orleans (November 10, 2026). The answers "
      "named 7 companies, and only one came up both times. Being named once isn't the same as being named every "
      "time, so we count over many asks."],
     "Every business in Orleans Parish needs an occupational license. Confirm the zoning allows the use and the site "
     "has a Certificate of Occupancy, apply on the City's One Stop site, and send the Amended Return to the City's "
     "Bureau of Revenue within your first 40 days of operating. Our "
     '<a href="/start-a-business/">free checklist</a> has every official link. The '
     '<a href="/new-business-launch/">New Business Launch</a> then gets you on Google.',
     [("Do you meet in person in New Orleans?",
       "Yes. autoants comes to you or meets by phone and video. There's no storefront, so no street address is "
       "listed."),
      ("Which New Orleans businesses do you work with?",
       "Trades first: HVAC, plumbing, roofing and electrical. Also auto shops, salons, gyms and other local "
       "businesses that live on phone calls."),
      COMMON_FAQ_PROMISE],
     ["permits", "aiscan-hvac", "onestop", "checklist", "prices"],
     "autoants answers the calls New Orleans businesses miss and gets them found on Google and in AI answers. "
     "Call or text (504) 499-1194.")

town("metairie", "Metairie", "Marketing Agency in Metairie, LA · autoants",
     "Marketing agency in Metairie, LA",
     "autoants works with businesses in Metairie and across Jefferson Parish. We answer the calls you miss, follow up "
     "your quotes, and get you found on Google and in AI answers. Call or text "
     f'<a href="tel:{TEL}">{PHONE}</a>.',
     ["We asked one AI assistant the same two Metairie HVAC questions six times on November 11, 2026. It named 15 "
      "different companies, and only 2 came up every time. That's why we count over many asks, never one.",
      "14.3% of Jefferson Parish residents age 5 and up speak Spanish at home (Census ACS 2020-2024). Read "
      '<a href="/hvac/spanish-line/">whether a shop around here needs a Spanish line</a>.'],
     "Metairie is unincorporated Jefferson Parish, so there's no city license. Get a zoning clearance first, then file "
     "the General Registration Application with the Jefferson Parish Sheriff's Office Bureau of Revenue and Taxation. "
     "It also covers parish sales tax, and the minimum is $50 per location. Our "
     '<a href="/start-a-business/">free checklist</a> has every official link.',
     [("Do you come to Metairie?",
       "Yes. autoants comes to you or meets by phone and video. There's no storefront, so no street address is "
       "listed."),
      ("Should my Google profile say Metairie or New Orleans?",
       "Use the address and city your business really uses, and list the towns you serve as service areas. Never add "
       "a town or a keyword to your business name; Google treats that as a violation."),
      COMMON_FAQ_PROMISE],
     ["aiscan-hvac", "acs", "jpso", "checklist", "prices"],
     "autoants answers the calls Metairie businesses miss and gets them found on Google and in AI answers. "
     "Call or text (504) 499-1194.")

town("kenner", "Kenner", "Marketing Agency in Kenner, LA · autoants",
     "Marketing agency in Kenner, LA",
     "autoants works with businesses in Kenner. We answer the calls you miss, follow up your quotes, and get you found "
     f'on Google and in AI answers. Call or text <a href="tel:{TEL}">{PHONE}</a>.',
     ["We asked one AI assistant twice who to call for AC repair in Kenner (November 10, 2026). The answers named 8 "
      "companies, 2 of them both times, and one carried another town's name. A page that plainly says you work in "
      "Kenner gives those answers something to read.",
      'Our New Orleans guide lists <a href="/nola/landscaping/kenner/">27 licensed landscapers</a> and '
      '<a href="/nola/tree-service/kenner/">9 tree services</a> in Kenner, taken only from public license lists.'],
     "Kenner is its own city: the occupational license is paid to the City of Kenner, and you still register with the "
     "Jefferson Parish Sheriff's Office Bureau of Revenue and Taxation. Our "
     '<a href="/start-a-business/">free checklist</a> has every official link.',
     [("Do you come to Kenner?",
       "Yes. autoants comes to you or meets by phone and video. There's no storefront, so no street address is "
       "listed."),
      ("Can my Kenner business show up for New Orleans searches?",
       "Google mostly shows businesses near the person searching. List the towns you really serve as service areas "
       "and build a real page for each one you work often; don't add a town to your business name."),
      COMMON_FAQ_PROMISE],
     ["aiscan-hvac", "guide-kenner", "jpso", "checklist", "prices"],
     "autoants answers the calls Kenner businesses miss and gets them found on Google and in AI answers. "
     "Call or text (504) 499-1194.")

# ---------------------------------------------------------------- /areas/
p = "areas/"
faq = [("Do you have an office?",
        "No storefront. autoants comes to you or meets by phone and video, so no street address is listed."),
       ("Do you work outside Greater New Orleans?",
        "Yes. Louisiana first: Greater New Orleans, Baton Rouge and the Northshore. We meet by phone and video "
        "anywhere."),
       COMMON_FAQ_PROMISE]
others = ["Harahan", "River Ridge", "Gretna", "Harvey", "Marrero", "Chalmette", "LaPlace", "Covington", "Mandeville",
          "Slidell", "Hammond", "Baton Rouge"]
body = (
    '    <p class="answer">autoants is based in New Orleans and works with local businesses across Louisiana: Greater '
    "New Orleans, Baton Rouge and the Northshore first. Each town page below says something only that town has: its "
    "license path and what we've measured there.</p>\n"
    "    <h2>Town pages</h2>\n"
    + ul(['<a href="/areas/new-orleans/">New Orleans</a>: Orleans Parish licensing and the City\'s permit seasons.',
          '<a href="/areas/metairie/">Metairie</a>: Jefferson Parish licensing and our repeated AI checks.',
          '<a href="/areas/kenner/">Kenner</a>: the City of Kenner license and what AI answers said about Kenner.'])
    + "    <h2>We also work in</h2>\n    <p>" + ", ".join(others) + ".</p>\n"
)
desc = "Where autoants works: New Orleans, Metairie, Kenner and the rest of Louisiana. Call or text (504) 499-1194."
PAGES[p] = page(p, "Where autoants Works: Greater New Orleans · autoants", desc, "Service areas",
                "Where we work", body, faq, ["checklist", "prices"],
                [dict(ORG, **{"@context": "https://schema.org",
                              "areaServed": [PLACES[t] for t in ("New Orleans", "Metairie", "Kenner")]})],
                "Where we work")


def add_sitemap(paths):
    sm_path = os.path.join(SITE, "sitemap.xml")
    s = open(sm_path, encoding="utf-8").read()
    for path in paths:
        loc = f"<loc>{BASE}{path}</loc>"
        if loc not in s:
            pri = "0.8" if not path.startswith("areas/") or path == "areas/" else "0.7"
            s = s.replace("</urlset>", f"  <url>{loc}<lastmod>{TODAY}</lastmod><priority>{pri}</priority></url>\n</urlset>")
    open(sm_path, "w", encoding="utf-8").write(s)


def lint(rel, text):
    vis = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", text)
    vis = html.unescape(re.sub(r"<[^>]+>", " ", vis))
    bad = [r"#1\b", r"\bguarantee", r"\bnever miss", r"\brisk[- ]free", r"\bsame[- ]day\b", r"\bin seconds\b",
           r"\bwithin (a|one) (minute|hour)\b", r"\b\d+-day\b"]
    errs = [f"{rel}: {b!r}" for b in bad if re.search(b, vis, re.I)]
    for m in re.finditer(r"\$(\d[\d,]*)", vis):
        if m.group(1).replace(",", "").endswith("9"):
            errs.append(f"{rel}: price ending in 9: {m.group(0)}")
    if "Google's AI calls" in vis and "not" not in vis:
        errs.append(f"{rel}: Google AI calls line")
    if TAGLINE not in vis:
        errs.append(f"{rel}: tagline missing")
    if f"tel:{TEL}" not in text:
        errs.append(f"{rel}: no tel link")
    for m in re.finditer(r'(?s)<script type="application/ld\+json">(.*?)</script>', text):
        json.loads(m.group(1))
    t = re.search(r"<title>(.*?)</title>", text).group(1)
    if len(html.unescape(t)) > 65:
        errs.append(f"{rel}: title {len(t)} chars")
    # FAQ JSON-LD text must equal the visible FAQ text
    faq_ld = [json.loads(m.group(1)) for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', text)]
    faq_ld = [x for x in faq_ld if x.get("@type") == "FAQPage"][0]
    shown = re.search(r'<div class="faq">(.*?)</div>', text, re.S).group(1)
    for qa in faq_ld["mainEntity"]:
        if E(qa["name"]) not in shown or E(qa["acceptedAnswer"]["text"]) not in shown:
            errs.append(f"{rel}: FAQ schema differs from the page: {qa['name']}")
    return errs


def main():
    errs = []
    titles = {}
    for rel, text in PAGES.items():
        errs += lint(rel, text)
        t = re.search(r"<title>(.*?)</title>", text).group(1)
        if t in titles:
            errs.append(f"{rel}: duplicate title with {titles[t]}")
        titles[t] = rel
    if errs:
        raise SystemExit("\n".join(errs))
    for rel, text in PAGES.items():
        out = os.path.join(SITE, rel, "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(text)
    add_sitemap(list(PAGES))
    print("wrote", len(PAGES), "pages:", ", ".join("/" + r for r in PAGES))


if __name__ == "__main__":
    main()
