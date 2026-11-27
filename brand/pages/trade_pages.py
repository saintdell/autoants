"""Builds the owner pages for plumbing, roofing and electrical: plumbing/index.html, roofing/index.html and
electrical/index.html, in the pattern of /hvac/ (brand/pages/hvac_pages.py; its CSS, fonts and organization node are
reused so the four pages look and read as one set).

    python3 brand/pages/trade_pages.py          # writes the three pages
    python3 brand/pages/trade_pages.py --check  # exits 1 if the built pages differ from what this file makes

Each FAQ answer is printed on the page and in the FAQPage JSON-LD from the same string, so the two can't drift.

Copy rules (Lane's, for every autoants page): plain words; "autoants" lowercase; no "#1", "best", "guarantee",
"never miss", no rank or result promises and no timing promises (the go-live promise was removed 2026-11-12); no
prices ending in 9; the receptionist is always "an AI" and says so; no attorney credential. The free mini assessment is "a
short video and a written report". Prices exactly as on /prices/ (checked TODAY). Every number carries its source and
date. Trade traps (from the trade-assessment-engine playbook): plumbing "callback" means a failed-fix return trip, so
the page never offers to "handle callbacks"; electrical "the service" means the utility connection, so the page says
"trouble call" for a repair visit; roofing stays clear of storm and insurance-claim work entirely (no claims,
deductibles, adjusters or storm deadlines) and says "a look at the roof", not "inspection".
URLs carry no place name (expansion rule, 2026-10-12): local wording lives in the copy.

Numbers: the first-screen checks are tle-main's booking-box scans (data/leads/booking-box-<trade>-2026-10-14.csv;
NONE + HIDDEN counted, sites that didn't load left out of both sides, the same way /hvac/ counts them); the
establishment counts are Census County Business Patterns 2023 (tle-main products/assessment/stats/stats.jsonl).
"""
import html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hvac_pages as hp  # noqa: E402  (CSS, fonts, the organization node, stat() and table())

SITE = hp.SITE
BASE = hp.BASE
TODAY = "2026-11-17"          # the day these pages were written and their facts checked (from `date`)
TODAY_WORDS = "November 17, 2026"
E = html.escape

# ---------------------------------------------------------------- prices (as on /prices, checked TODAY)
P_BOTH = "$1,250 a month + $1,250 setup"
P_TRY = "$500 once"
P_NMJ = "$750 a month + $750 setup"
P_GF = "$750 a month + $500 setup"
P_PPJ = "$250 a month + $25 for each job we save from a call you missed, never more than $750 a month"
BREAKDOWN = "a short video and a written report"

SRC_COMMON = {
    "cbp": ("U.S. Census Bureau, County Business Patterns 2023, establishments with paid employees in Orleans and "
            "Jefferson parishes under the trade's NAICS code. Owner-only shops are not counted",
            "https://www.census.gov/programs-surveys/cbp.html", "Read October 16, 2026"),
    "prices": ("autoants prices page. Prices are for our first 3 shops with up to 15 trucks; the page lists what they "
               "become after, and bigger or multi-location operations are quoted by size", BASE + "/prices/",
               "Checked November 17, 2026"),
}

TRADES = {
    "plumbing": {
        "who": "plumbers", "shop": "plumbing shop", "owners": "plumbing owners", "audience": "Plumbing contractors",
        "crumb": "autoants for plumbers",
        "answer": [
            "<b>autoants</b> helps plumbing shops in New Orleans and Jefferson Parish get found on Google and in AI "
            "answers like ChatGPT, answers the calls you can't get to (an AI that says it's an AI, day or night), "
            "follows up your quotes and asks every finished job for a review.",
        ],
        "cards": [
            ("The call you can't get to",
             "A backup or a no-hot-water call doesn't wait for you to call back. Every missed call gets a text back from "
             "your shop by name. If you want the phone answered too, an AI answers when nobody can, day or night: it "
             "says it's an AI, takes the address and what's going on, hands a real emergency to a person and texts "
             "you the job."),
            ("Big quotes followed up",
             "Repipes, slab leaks, sewer lines and water heater replacements are the quotes that go quiet. A quote "
             "with no answer gets a polite nudge. A reply stops it, and nothing goes out without your OK."),
            ("Found on Google and in AI answers",
             "Your Google profile and listings kept right, 2 new pages a month about the work you do and where you "
             "do it, and a monthly check of what ChatGPT and other AI assistants say when someone asks for a "
             "plumber."),
            ("Reviews and posts from finished jobs",
             "The same review ask after every finished job, with your link. It never picks who gets asked and never "
             "pays for reviews. A Google post every week, made from your real job photos and sent to you by text to "
             "approve."),
            ("Booking from a phone",
             "A Book button or a “next opening” box at the top of your site as it shows on a phone, tied to times "
             "your plumbers will keep."),
            ("Reminders when work comes due",
             "Past customers who agreed to hear from you get a reminder when something's due, like a yearly backflow "
             "test."),
        ],
        "firstscreen": ("28 of 45", "New Orleans-area plumbing websites that loaded had no way to book or request "
                        "service on the first phone screen"),
        "fs_src": ("autoants first-screen check: 53 New Orleans-area plumbing homepages, each loaded once at phone "
                   "size; the 45 that loaded are counted (8 didn't load). A first pass on one date. We count the "
                   "sites; we don't name them", None, "Checked October 14, 2026"),
        "cbp": ("281", "plumbing, heating and air-conditioning contractors with paid staff in Orleans and Jefferson "
                "(the Census counts plumbers and HVAC under one code, NAICS 238220)"),
        "never_ai": "Let an AI quote a price, diagnose a leak or a backup, or promise an arrival time. Those stay "
                    "with you.",
        "faq_ai": "No. It says it's an AI in its first sentence, takes the address and what's going on, hands a real "
                  "emergency to a person and texts you the job. It never quotes a price, diagnoses a leak or a "
                  "backup, or promises an arrival time; you approve a job before the customer hears yes.",
        "faq_extra": ("We give away a lot of quotes for repipes and water heaters. What happens to the ones that go "
                      "quiet?",
                      "Each one gets a polite nudge on the schedule you pick, written in your words. It stops as soon "
                      "as the customer replies, and nothing goes out without your OK."),
        "software": "No. You keep the software you run today, like Housecall Pro, Jobber or ServiceTitan; the "
                    "assistants work beside it.",
        "question": ("questions/ai-receptionist-plumbing-louisiana/",
                     "What should a plumbing company in Louisiana look for in an AI receptionist?"),
        "guide": None,
    },
    "roofing": {
        "who": "roofers", "shop": "roofing company", "owners": "roofing owners", "audience": "Roofing contractors",
        "crumb": "autoants for roofers",
        "answer": [
            "<b>autoants</b> helps roofing companies in New Orleans and Jefferson Parish get found on Google and in "
            "AI answers like ChatGPT, answers the leak calls you can't take from a roof (an AI that says it's an AI, "
            "day or night), follows up your estimates and turns finished roofs into reviews and posts.",
        ],
        "cards": [
            ("Leak calls while you're on a roof",
             "A leak call wants someone today, and your crew's hands are full on a tear-off. Every missed call gets a "
             "text back from your company by name. If you want the phone answered too, an AI answers when nobody "
             "can, day or night: it says it's an AI, takes the address and what's going on, and texts you the job."),
            ("Estimates followed up",
             "Repair or re-roof, the written estimate is where jobs go quiet. An estimate with no answer gets a "
             "polite nudge. A reply stops it, and nothing goes out without your OK."),
            ("Found on Google and in AI answers",
             "Your Google profile and listings kept right, 2 new pages a month about the roofs you do and where you "
             "do them, and a monthly check of what ChatGPT and other AI assistants say when someone asks for a "
             "local roofer."),
            ("Reviews and posts from finished roofs",
             "The same review ask after every finished job, with your link. It never picks who gets asked and never "
             "pays for reviews. A Google post every week, made from the job photos your crew already takes and sent "
             "to you by text to approve."),
            ("Booking from a phone",
             "A Book button or a “next opening” box at the top of your site as it shows on a phone, so a homeowner "
             "can ask for a look at the roof without calling."),
        ],
        "firstscreen": ("22 of 50", "New Orleans-area roofing websites that loaded had no way to book or request a "
                        "visit on the first phone screen"),
        "fs_src": ("autoants first-screen check: 60 New Orleans-area roofing homepages, each loaded once at phone "
                   "size; the 50 that loaded are counted (10 didn't load). A first pass on one date. We count the "
                   "sites; we don't name them", None, "Checked October 14, 2026"),
        "cbp": ("43", "roofing contractors with paid staff in Orleans and Jefferson (NAICS 238160)"),
        "never_ai": "Let an AI quote a price, say what a roof needs, or promise an arrival time. Those stay with you.",
        "faq_ai": "No. It says it's an AI in its first sentence, takes the address and what's going on, and texts "
                  "you the job. It never quotes a price, says what a roof needs, or promises an arrival time; you "
                  "approve a job before the customer hears yes.",
        "faq_extra": ("Repair or re-roof, our estimates take time to write. What happens to the ones nobody answers?",
                      "Each one gets a polite nudge on the schedule you pick, written in your words. It stops as soon "
                      "as the homeowner replies, and nothing goes out without your OK."),
        "software": "No. You keep the estimating and job tools you use today; the assistants work beside them.",
        "question": ("questions/marketing-small-roofing-company-new-orleans/",
                     "Who helps a small roofing company in New Orleans with marketing?"),
        "guide": ("nola/roofing/", "Roofers in Greater New Orleans: our free guide for homeowners (nobody pays for a "
                                   "spot)"),
    },
    "electrical": {
        "who": "electricians", "shop": "electrical company", "owners": "electrical contractors",
        "audience": "Electrical contractors", "crumb": "autoants for electricians",
        "answer": [
            "<b>autoants</b> helps electrical contractors in New Orleans and Jefferson Parish get found on Google "
            "and in AI answers like ChatGPT, answers the trouble calls you can't get to (an AI that says it's an AI, "
            "day or night), follows up your estimates and asks every finished job for a review.",
        ],
        "cards": [
            ("Trouble calls while you're on a job",
             "Dead outlets and tripping breakers come in while you're in someone's attic. Every missed call gets a "
             "text back from your company by name. If you want the phone answered too, an AI answers when nobody "
             "can, day or night: it says it's an AI, takes the address and what's going on, hands a real emergency "
             "to a person and texts you the job."),
            ("Estimates followed up",
             "Panel changes, service upgrades, rewires and EV chargers: the estimates you spend hours on are the ones "
             "that go quiet. An estimate with no answer gets a polite nudge. A reply stops it, and nothing goes out "
             "without your OK."),
            ("Found on Google and in AI answers",
             "Your Google profile and listings kept right, 2 new pages a month about the work you do and where you "
             "do it, and a monthly check of what ChatGPT and other AI assistants say when someone asks for an "
             "electrician."),
            ("Reviews and posts from finished jobs",
             "The same review ask after every finished job, with your link. It never picks who gets asked and never "
             "pays for reviews. A Google post every week, made from your real job photos and sent to you by text to "
             "approve."),
            ("Booking from a phone",
             "A Book button or a “next opening” box at the top of your site as it shows on a phone, tied to times "
             "your electricians will keep."),
            ("Generator maintenance reminders",
             "Standby generator customers who agreed to hear from you get a reminder when the yearly maintenance is "
             "due."),
        ],
        "firstscreen": ("30 of 47", "New Orleans-area electrical websites that loaded had no way to book or ask for a "
                        "visit on the first phone screen"),
        "fs_src": ("autoants first-screen check: 60 New Orleans-area electrical homepages, each loaded once at phone "
                   "size; the 47 that loaded are counted (13 didn't load). A first pass on one date. We count the "
                   "sites; we don't name them", None, "Checked October 14, 2026"),
        "cbp": ("178", "electrical contractors with paid staff in Orleans and Jefferson (NAICS 238210)"),
        "never_ai": "Let an AI quote a price, say whether wiring is safe, or promise an arrival time. Those stay with "
                    "you.",
        "faq_ai": "No. It says it's an AI in its first sentence, takes the address and what's going on, hands a real "
                  "emergency to a person and texts you the job. It never quotes a price, says whether wiring is "
                  "safe, or promises an arrival time; you approve a job before the customer hears yes.",
        "faq_extra": ("We price a lot of panel changes and service upgrades. What happens to the estimates nobody "
                      "answers?",
                      "Each one gets a polite nudge on the schedule you pick, written in your words. It stops as soon "
                      "as the customer replies, and nothing goes out without your OK."),
        "software": "No. You keep the software you run today, like Housecall Pro, Jobber or ServiceTitan; the "
                    "assistants work beside it.",
        "question": ("questions/after-hours-calls-electrical-company-new-orleans/",
                     "Who can answer and book after-hours calls for an electrical company in New Orleans?"),
        "guide": ("nola/electrical/", "Electricians in Greater New Orleans: our free guide for homeowners (nobody pays "
                                      "for a spot)"),
    },
}


def cta_href(p, slug):
    return f"{p}index.html?interest=Free%20mini%20assessment&amp;ref={slug}#contact"


def faq(t):
    return [
        ("What is the free mini assessment?",
         f"It's {BREAKDOWN} about your {t['shop']}, made only from public information: how you show up on Google and "
         "in AI answers like ChatGPT, your reviews and listings next to the shops around you, and what we'd fix "
         "first. It's yours to keep either way."),
        ("Does the AI pretend to be a person?", t["faq_ai"]),
        t["faq_extra"],
        ("Do I have to change my software?", t["software"]),
        ("Can you promise more calls or a spot on Google?",
         "No. Nobody honest can. Before we start we count one real week of your calls, nights and weekends "
         "included, and we show you the same numbers every month after."),
        ("What does it cost, and for how long?",
         f"Get Found + AI Front Desk is {P_BOTH}; to try one assistant first, it's {P_TRY}. Those are the "
         "prices for our first 3 shops with up to 15 trucks. Monthly plans are three months, then month to month, and "
         "you cancel by email. You own your accounts, pages and customer list."),
    ]


def page(slug):
    t = TRADES[slug]
    p = "../"
    url = f"{BASE}/{slug}/"
    h1 = f"Missed-call text-back and AI answering for {t['who']} in New Orleans"
    title = h1 + " · autoants"
    desc = (f"For {t['owners']} in New Orleans and Jefferson Parish: get found on Google and ChatGPT, an AI that "
            f"answers when you can't, and reviews from finished jobs. Starts with a free mini assessment.")
    answer = t["answer"] + [
        f"It starts with a free mini assessment of your business, {BREAKDOWN}. Then it's {P_BOTH} for both, or {P_TRY} "
        "to try one assistant."]
    qa = faq(t)
    cards = '<div class="cards">' + "".join(
        f'<div class="card"><h3>{E(h)}</h3><p>{E(b)}</p></div>' for h, b in t["cards"]) + "</div>"
    fs_n, fs_l = t["firstscreen"]
    cbp_n, cbp_l = t["cbp"]
    stats = ('<div class="stats">' +
             hp.stat(fs_n, fs_l, "autoants check, Oct 14, 2026") +
             hp.stat(cbp_n, cbp_l, "Census County Business Patterns 2023") + "</div>")
    prices = hp.table(["What", "Price"], [
        [f"<b>The free mini assessment</b>: {BREAKDOWN} on how you show up on Google, in AI answers and next to the shops "
         "around you, made from public information", "Free"],
        ["<b>Get Found + AI Front Desk</b>: missed calls answered, quotes followed up, appointments booked and "
         "reminded, reviews requested, your Google profile kept right and posted to every week, your listings kept "
         "right, 2 new pages a month, what AI answers say about you checked every month, and your website kept up",
         P_BOTH],
        ["<b>Not ready? Try one</b>: one assistant on your phone (most shops start with texting back every missed "
         "call)", P_TRY],
        ["<b>AI Front Desk</b> alone: just the calls", P_NMJ],
        ["<b>Get Found</b> alone: just Google and AI answers", P_GF],
        ["<b>Pay per job</b>: AI Front Desk, paid by the job", P_PPJ],
        ["<b>AI phone answering</b>: an AI that answers when nobody can, always says it's an AI, and texts you the "
         "job", "Priced with you once you're on Get Found + AI Front Desk; minutes written into the agreement"],
    ])
    more = [f'<li><a class="in" href="{p}{t["question"][0]}">{E(t["question"][1])}</a></li>',
            f'<li><a class="in" href="{p}questions/show-up-in-chatgpt-contractor-new-orleans/">How does a New Orleans '
            'contractor get named when people ask ChatGPT for a contractor?</a></li>',
            f'<li><a class="in" href="{p}compare/">How autoants compares with an answering service, a call center and '
            'doing it yourself</a></li>']
    if t["guide"]:
        more.append(f'<li><a class="in" href="{p}{t["guide"][0]}">{E(t["guide"][1])}</a></li>')
    srcs = [("fs", t["fs_src"]), ("cbp", SRC_COMMON["cbp"]), ("prices", SRC_COMMON["prices"])]
    sources = '<h2 id="sources">Sources</h2>\n<ol class="sources">' + "".join(
        f"<li>{E(w)}.{f' <a href={chr(34)}{E(u)}{chr(34)}>{E(u)}</a>.' if u else ''} {E(when)}.</li>"
        for _, (w, u, when) in srcs) + "</ol>"
    faq_html = '<h2 id="questions">Questions ' + E(t["owners"]) + ' ask</h2>\n<div class="faq">' + "".join(
        f"<h3>{E(q)}</h3><p>{E(a)}</p>" for q, a in qa) + "</div>"
    btn = f'<a class="btn" href="{cta_href(p, slug)}">Get my free mini assessment</a>'
    graph = [
        hp.ORG,
        {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": h1, "description": desc,
         "inLanguage": "en-US", "datePublished": TODAY, "dateModified": TODAY,
         "publisher": {"@id": BASE + "/#organization"}, "about": {"@id": url + "#service"},
         "breadcrumb": {"@id": url + "#breadcrumb"}},
        {"@type": "Service", "@id": url + "#service", "name": f"autoants for {t['who']}",
         "serviceType": "Missed-call text-back, AI phone answering, quote follow-up, review requests and local search",
         "provider": {"@id": BASE + "/#organization"},
         "areaServed": [{"@type": "City", "name": "New Orleans"},
                        {"@type": "AdministrativeArea", "name": "Jefferson Parish"}],
         "audience": {"@type": "BusinessAudience", "audienceType": t["audience"]},
         "offers": [
             {"@type": "Offer", "name": "Get Found + AI Front Desk", "price": "1250", "priceCurrency": "USD",
              "description": P_BOTH + ", for our first 3 shops", "url": BASE + "/prices/"},
             {"@type": "Offer", "name": "Try one", "price": "500", "priceCurrency": "USD",
              "description": "One assistant, $500 once, for our first 3 shops", "url": BASE + "/prices/"},
             {"@type": "Offer", "name": "The free mini assessment", "price": "0", "priceCurrency": "USD",
              "description": BREAKDOWN[0].upper() + BREAKDOWN[1:], "url": url}]},
        {"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "autoants", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": t["crumb"], "item": url}]},
        {"@type": "FAQPage", "@id": url + "#questions", "url": url, "dateModified": TODAY, "inLanguage": "en-US",
         "isPartOf": {"@id": url + "#webpage"}, "publisher": {"@id": BASE + "/#organization"},
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                        for q, a in qa]},
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    ans = "".join(f"<p>{a}</p>" for a in answer)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="autoants">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/brand/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f7f5f0">
<link rel="icon" href="/favicon-96.png" type="image/png" sizes="96x96">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="icon" href="{p}brand/favicon.svg" type="image/svg+xml">
{hp.FONTS}
<script type="application/ld+json">{ld}</script>
<style>{hp.CSS}</style>
</head>
<body>
<div class="wrap">
  <nav>
    <a href="{p}index.html"><img src="{p}brand/autoants-logo.svg" alt="autoants home" width="120" height="26" style="height:26px;width:auto;display:block"></a>
    <div class="sp"></div>
    <a class="ghost" href="{p}prices/">Prices</a>
    <a class="ghost" href="{p}index.html#contact">Contact</a>
  </nav>
  <main>
  <p class="crumbs">{E(t['crumb'])} · New Orleans and Jefferson Parish</p>
  <h1>{E(h1)}</h1>
  <div class="answer">{ans}</div>
  <p class="stamp">By autoants · checked {TODAY_WORDS} · prices for our first 3 shops</p>
  <p>{btn}</p>

  <h2>What we do for {E(t['who'])}</h2>
  {cards}

  <h2>The local numbers</h2>
  <p>Each number below has its source and the date we pulled it. Our own checks count sites; they never name them.</p>
  {stats}
  <p class="src">Source: autoants first-screen check (checked October 14, 2026); Census County Business Patterns 2023 (read October 16, 2026). <a href="#sources" style="color:inherit">Full list below</a>.</p>
  <p>What the records can't tell you is how many calls <i>your</i> shop misses, and when. So before we start, we count one real week of your own calls, nights and weekends included, and show you the same numbers every month after.</p>

  <h2>What it costs</h2>
  <p>Most shops need both, so that's where we start. Prices as on {hp.link(p, "prices/", "autoants.com/prices")}, checked {TODAY_WORDS}.</p>
  {prices}
  <ul>
    <li>You own everything: your accounts, pages and customer list.</li>
    <li>No 12-month contract: three months, then month to month. Cancel by email.</li><li>Try one counts toward setup if you upgrade within 30 days. Pay for a year up front and setup is free.</li>
    <li>We don't promise results. We count your calls and jobs before and after, and show you every month.</li>
    <li>Prices shown are for our first 3 shops with up to 15 trucks; bigger or multi-location operations are quoted by size. Texts and phone minutes run on your own account, billed to you directly.</li>
  </ul>

  <h2>What we never do</h2>
  <ul>
    <li>Let an AI pretend to be a person. It says it's an AI in its first sentence.</li>
    <li>Promise a number of calls, a spot on Google or a place in an AI answer.</li>
    <li>Pay for reviews, or pick which customers get asked.</li>
    <li>Text anyone who didn't contact you first or say yes to hearing from you.</li>
    <li>{E(t['never_ai'])}</li>
  </ul>
  <p>The full list: {hp.link(p, "never/", "what each assistant never does")}.</p>

{faq_html}

  <h2>More for {E(t['owners'])}</h2>
  <ul>{"".join(more)}</ul>

<div class="more"><p><b>Want to see it for your {E(t['shop'])} first?</b> Start with the free mini assessment: {BREAKDOWN} on how you show up on Google, in AI answers and next to the shops around you, made from public information. Every price is written down before anything starts.</p>{btn}</div>
{sources}
  </main>
  <footer>
    <p>autoants, short for automated assistants · a New Orleans company that answers missed calls, books jobs and gets local businesses found on Google and in AI answers · commercial services only. Call <a href="tel:+15044991194">(504) 499-1194</a>.</p>
    <p>Checked {TODAY_WORDS}. Corrections: hello@autoants.com · <a href="{p}hvac/">For HVAC companies</a> · <a href="{p}plumbing/">For plumbers</a> · <a href="{p}roofing/">For roofers</a> · <a href="{p}electrical/">For electricians</a> · <a href="{p}never/">What it never does</a> · <a href="{p}prices/">Prices</a> · <a href="{p}ai/">For AI assistants</a></p>
    <p>&mdash; autoants</p>
  </footer>
</div>
</body>
</html>
"""


def main():
    check = "--check" in sys.argv
    drift = []
    for slug in TRADES:
        path = os.path.join(SITE, slug, "index.html")
        doc = page(slug)
        if check:
            if not os.path.exists(path) or open(path).read() != doc:
                drift.append(path)
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(doc)
        print("wrote", os.path.relpath(path, SITE))
    if check and drift:
        print("differs from the generator:", *drift, sep="\n  ")
        sys.exit(1)


if __name__ == "__main__":
    main()
