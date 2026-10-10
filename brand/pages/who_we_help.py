"""Builds who-we-help.html: every kind of business we help, grouped, with one line on what we automate.
Kept short on purpose (Lane, 2026-10-01: the long version was too much). SECTORS/CREW below are unused for now.
It also prints as a brochure (Cmd+P, or make_pdf()) to brand/print/brochure/autoants-brochure.pdf.

    uv run --with playwright python3 brand/pages/who_we_help.py

Rules for the copy: no results or numbers we can't show, no popularity claims, AI always
named as AI, texts only to people who said yes, and no patient information until there's
a HIPAA program (dental/medical stays "coming later")."""
import html, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(SITE, "brand", "mascot"))
from mascot import mascot  # noqa: E402

ICON = lambda n: open(os.path.join(SITE, "brand", "icons", n + ".svg")).read().strip()

CREW = [("callback", "Text-Back Ant", "Miss a call and it texts them back in seconds."),
        ("responder", "Responder Ant", "Every new inquiry gets an answer right away, from your site or social."),
        ("scheduler", "Scheduler Ant", "Requests become booked appointments, confirmed and reminded."),
        ("reviewer", "Reviewer Ant", "Every customer gets the same review ask, one tap from your phone."),
        ("receptionist", "Receptionist Ant", "An AI that answers when you can't, says it's an AI, and texts you the details."),
        ("reminder", "Reminder Ant", "Brings past customers back, only the ones who said yes to hearing from you."),
        ("scout", "Scout Ant", "Shows up on Google, Apple, Bing and in AI answers."),
        ("promoter", "Promoter Ant", "Posts, short videos and local ads from your real work.")]

# (id, pose, eyebrow, title, the moment money walks out, [(assistant, what it does there)], note)
SECTORS = [
    ("trades", "hardhat", "Home services &amp; trades", "Tree, HVAC, roofing, plumbing, landscaping",
     "You're up a tree or under a house when the phone rings. The homeowner doesn't leave a voicemail; they call the next crew.",
     [("Text-Back Ant", "texts every missed call back in seconds"),
      ("Responder Ant", "answers quote requests while you're on the job"),
      ("Scheduler Ant", "turns requests into booked estimates"),
      ("Reviewer Ant", "asks every customer after every job"),
      ("Receptionist Ant", "picks up after hours, says it's an AI, and texts you the job")], None),
    ("auto", "point", "Auto repair &amp; tire shops", "Mechanics, tire and brake, oil change",
     "Your techs are under a car and the front desk is on the other line. A driver with a check-engine light calls three shops and books the first one that answers.",
     [("Text-Back Ant", "texts back the calls nobody could grab"),
      ("Responder Ant", "sends an estimate range from your own price list (the final price after inspection, always)"),
      ("Scheduler Ant", "books drop-off times and sends the confirmation"),
      ("Reminder Ant", "\"Your oil change is due\" to customers who opted in"),
      ("Reviewer Ant", "asks every customer when they pick up the car")], None),
    ("salons", "wave", "Salons, nail spas &amp; barbers", "Nails, hair, lashes, brows",
     "Your hands are busy with a client, the phone rings out, and a new client books somewhere else.",
     [("Text-Back Ant", "texts back every call you can't take mid-appointment"),
      ("Scheduler Ant", "books and confirms appointments, with a reminder the day before"),
      ("Reminder Ant", "\"Time for a fill?\" to clients who said yes"),
      ("Reviewer Ant", "asks every client after the visit"),
      ("Promoter Ant", "before-and-after posts, with your client's OK")],
     "Coming soon: comment-to-book. A follower comments BOOK on your post and gets your booking link in a message."),
    ("gyms", "thumbs", "Gyms &amp; fitness studios", "Gyms, CrossFit, yoga, pilates, martial arts",
     "Someone asks about a free trial at 9pm. By morning they've signed up down the street.",
     [("Responder Ant", "answers trial and class questions in seconds, from your site or social"),
      ("Scheduler Ant", "books the tour or first class"),
      ("Reminder Ant", "invites lapsed members back, only those who agreed to hear from you"),
      ("Reviewer Ant", "asks members after their first month"),
      ("Text-Back Ant", "texts back the calls the front desk missed")], None),
]
OTHER = ("carry", "Something else?", "Cleaners, pet groomers, photographers, tutors, repair shops",
         "If your business runs on phone calls and appointments, the crew probably fits. Tell us what eats your week and we'll tell you honestly whether automation would pay for itself.")
DENTAL = ("clipboard", "Dental &amp; medical offices", "Coming later, built HIPAA-ready first",
          "Patient information comes with HIPAA rules: anyone who handles it for you has to sign a business associate agreement and protect it. "
          "We're building that before we touch a single patient record. Want to be first in line when it's ready? Tell us.")


GROUPS = [
    ("Home services", "Missed calls texted back, quote requests booked, every customer asked for a review.",
     ["Tree service", "HVAC", "Roofing", "Plumbing", "Electrical", "Landscaping &amp; lawn care", "Pressure washing",
      "Pest control", "Pool service", "House cleaning", "Garage doors", "Handyman", "Movers"], False),
    ("Auto", "Calls answered while the techs are under a car, drop-offs booked, service-due reminders for customers who opted in.",
     ["Auto repair", "Tire &amp; brake", "Oil change &amp; lube", "Body &amp; collision", "Auto detailing", "Towing"], False),
    ("Beauty &amp; personal care", "Appointments booked and confirmed, a reminder the day before, rebooking for clients who said yes.",
     ["Nail spas", "Hair salons", "Barbershops", "Lash &amp; brow studios", "Day spas &amp; massage", "Tattoo studios"], False),
    ("Fitness", "Trial and class questions answered in seconds, tours booked, lapsed members invited back if they agreed to hear from you.",
     ["Gyms", "Yoga &amp; pilates", "CrossFit &amp; boxing", "Martial arts", "Personal trainers", "Dance studios"], False),
    ("Pets", "Grooming and boarding booked and confirmed, reminders, reviews.",
     ["Pet grooming", "Boarding &amp; daycare", "Dog training", "Veterinary clinics"], False),
    ("Food &amp; events", "Calls and messages answered, catering and event inquiries followed up, reviews.",
     ["Restaurants", "Catering", "Food trucks", "Event rentals", "Photographers", "DJs &amp; entertainment"], False),
    ("Professional &amp; local services", "New-client inquiries answered fast, consultations booked, reviews.",
     ["Accountants &amp; bookkeepers", "Insurance agencies", "Real estate agents", "Tutors &amp; learning centers",
      "Property managers", "Storage facilities"], False),
    ("Health &amp; medical", "Patient information needs a HIPAA program and signed agreements first, so we're building that before we touch a single patient record.",
     ["Dental offices", "Chiropractors", "Physical therapy", "Med spas", "Optometry", "Clinics"], True),
]

STEPS = [("Reach out", "Fill out the form, or call or text. Two minutes: your name, number and business."),
         ("See your free preview", "We build your new website with your real info and reviews, before you pay anything."),
         ("Pick your crew", "A 15-minute call to choose the assistants that fit. You approve every message before it goes out."),
         ("Go live", "Once you say go, your site is live within 7 days or the $500 setup fee comes back.")]
# Owners who buy a public-records list or mailing from us, not the assistants (Lane, 2026-10-07: these
# never go on the home or services page). One sentence and one contact button each; the interest
# text must match an <option> in the index.html contact form.
SELL_TO = [
    ("insurance", "For insurance agents",
     "Each month, the contractors in your parish whose liability coverage on file with the state board is coming up for renewal, from public records, so you can reach them first.",
     "Contractor coverage list", "Ask about the list"),
    ("restaurants", "For pest control and commercial cleaners serving restaurants",
     "Every week, the restaurants near you cited in state health inspections for the problems you fix, from the public inspection record.",
     "Restaurant inspection list", "Ask about the weekly list"),
    ("next-job", "For gutter, solar, fencing and pool companies",
     "Your postcard in the mailbox the week a city permit shows the job before yours (a new roof, a panel upgrade, a new pool), with one company per trade.",
     "Next-job postcards", "Ask about the postcards"),
]
NEVER = ["Fake reviews, or asking only the happy customers",
         "Texting anyone who didn't say yes",
         "An AI that pretends to be a person",
         "Sending anything to your customers without your OK"]


def pose(p, w):
    return mascot(p, w, dark=True).replace(f'width="{w}"', f'width="{w}" aria-hidden="true"', 1)


def page():
    crew = "".join(f'<div class="crew"><span class="ic">{ICON(i)}</span><div><b>{n}</b><p>{d}</p></div></div>' for i, n, d in CREW)
    sectors = ""
    for sid, p, title, sub, moment, jobs, note in SECTORS:
        lis = "".join(f'<li><b>{a}</b> {d}</li>' for a, d in jobs)
        sectors += (f'<article class="sector" id="{sid}"><div class="art">{pose(p, 120)}</div><div>'
                    f'<div class="eyebrow">{sub}</div><h3>{title}</h3><p class="moment">{moment}</p>'
                    f'<ul class="jobs">{lis}</ul>' + (f'<p class="soon">{note}</p>' if note else "") + '</div></article>')
    p, t, s, d = OTHER
    sectors += f'<article class="sector"><div class="art">{pose(p, 120)}</div><div><div class="eyebrow">{s}</div><h3>{t}</h3><p class="moment">{d}</p></div></article>'
    p, t, s, d = DENTAL
    sectors += (f'<article class="sector later" id="dental"><div class="art">{pose(p, 120)}</div><div><div class="eyebrow">{s}</div><h3>{t}</h3>'
                f'<p class="moment">{d}</p></div></article>')
    steps = "".join(f'<li><b>{t}</b><span>{d}</span></li>' for t, d in STEPS)
    allb = "".join(
        f'<div class="grp{" later-grp" if later else ""}"><h3>{name}</h3><p>{line}</p>'
        f'<div class="chips">{"".join(f"<span>{b}</span>" for b in biz)}</div></div>'
        for name, line, biz, later in GROUPS)
    never = "".join(f'<li>{x}</li>' for x in NEVER)
    sell = "".join(
        f'<div class="sell" id="{sid}"><h3>{t}</h3><p>{d}</p>'
        f'<a class="cta" href="index.html?interest={i.replace(" ", "%20")}#contact">{b}</a></div>'
        for sid, t, d, i, b in SELL_TO)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Who We Help · autoants</title>
<meta name="description" content="What autoants' automated assistants do for local businesses: trades, auto repair shops, salons and nail spas, gyms and studios. Missed-call text-back, fast replies, booking, reviews.">
<meta name="theme-color" content="#0b1712">
<link rel="icon" href="brand/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="brand/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
  :root{{--bg:#0b1712;--surface:#14261e;--ink:#f4f1e8;--muted:#a3b0a8;--faint:#6f7d75;--mint:#3ddcae;--mint-ink:#062a1d;--ok:#7bc96a;
        --line:rgba(244,241,232,.12);--disp:"Archivo",system-ui,sans-serif;--body:"Inter",system-ui,sans-serif;--mono:"JetBrains Mono",ui-monospace,monospace}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);line-height:1.6;-webkit-font-smoothing:antialiased}}
  a{{color:inherit}}
  .wrap{{max-width:1080px;margin:0 auto;padding:0 22px}}
  nav{{display:flex;align-items:center;gap:14px;padding:18px 0;border-bottom:1px solid var(--line)}}
  nav .sp{{margin-left:auto}}
  nav a.ghost{{color:var(--muted);text-decoration:none;font-weight:600;font-size:14px}}
  nav a.btn,.cta{{background:var(--mint);color:var(--mint-ink);font-weight:700;padding:10px 16px;border-radius:9px;text-decoration:none;font-family:var(--disp)}}
  a:focus-visible{{outline:3px solid var(--mint);outline-offset:3px}}
  .eyebrow{{font-family:var(--mono);font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--mint)}}
  header{{padding:56px 0 36px;border-bottom:1px solid var(--line)}}
  h1{{font-family:var(--disp);font-weight:800;font-size:clamp(32px,5vw,52px);line-height:1.05;margin:12px 0 14px;text-wrap:balance;max-width:20ch}}
  h1 em{{color:var(--mint);font-style:normal}}
  .sub{{font-size:19px;color:var(--muted);max-width:60ch;margin:0}}
  section{{padding:44px 0;border-bottom:1px solid var(--line)}}
  h2{{font-family:var(--disp);font-weight:800;font-size:clamp(24px,3.4vw,32px);margin:0 0 6px;text-wrap:balance}}
  .lede{{color:var(--muted);margin:0 0 24px;max-width:62ch}}
  .grps{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}}
  .grp{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:18px 18px 16px}}
  .grp h3{{font-family:var(--disp);font-weight:800;font-size:19px;margin:0 0 4px}}
  .grp p{{margin:0 0 12px;color:var(--muted);font-size:14px;line-height:1.45}}
  .chips{{display:flex;flex-wrap:wrap;gap:6px}}
  .chips span{{font-size:13px;padding:4px 10px;border-radius:999px;border:1px solid var(--line);background:rgba(61,220,174,.08)}}
  .sells{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}}
  .sell{{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--mint);border-radius:14px;padding:18px;display:flex;flex-direction:column;gap:10px}}
  .sell h3{{font-family:var(--disp);font-weight:800;font-size:19px;margin:0;text-wrap:balance}}
  .sell p{{margin:0;color:var(--muted);font-size:15px;line-height:1.5}}
  .sell .cta{{align-self:flex-start;margin-top:auto}}
  .nl{{margin-top:14px;display:grid;grid-template-columns:1.25fr 1fr;gap:14px 26px;align-items:center;background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--mint);border-radius:14px;padding:18px}}
  .nl h3{{font-family:var(--disp);font-weight:800;font-size:19px;margin:6px 0 4px;text-wrap:balance}}
  .nl-copy p{{margin:0;color:var(--muted);font-size:15px;line-height:1.5}}
  .nl-form{{display:flex;flex-wrap:wrap;gap:10px}}
  .nl-form input{{flex:1 1 200px;font:inherit;font-size:16px;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:9px;padding:10px 12px;min-width:0}}
  .nl-form select{{flex:1 1 200px;font:inherit;font-size:16px;color:var(--ink);background-color:var(--bg);background-image:linear-gradient(45deg,transparent 50%,var(--muted) 50%),linear-gradient(-45deg,transparent 50%,var(--muted) 50%);background-position:calc(100% - 18px) 52%,calc(100% - 12px) 52%;background-size:6px 6px;background-repeat:no-repeat;-webkit-appearance:none;appearance:none;border:1px solid var(--line);border-radius:9px;padding:10px 32px 10px 12px;min-width:0;cursor:pointer}}
  .nl-form select:invalid{{color:var(--faint)}} .nl-form option{{color:var(--ink);background:var(--bg)}}
  .nl-form input:focus,.nl-form select:focus{{outline:2px solid var(--mint);outline-offset:1px;border-color:transparent}}
  .nl-form button{{border:0;cursor:pointer;font-size:15px}}
  .nl-form .nl-consent{{flex-basis:100%;margin:0;font-size:13px;color:var(--faint)}}
  .sr{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}}
  @media (max-width:720px){{.nl{{grid-template-columns:1fr}}}}
  .assess-note{{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--mint);border-radius:12px;padding:16px 18px;color:var(--muted);max-width:760px}}
  .assess-note b{{color:var(--ink)}} .assess-note a{{color:var(--mint)}}
  .later-grp{{border-style:dashed;background:transparent}}
  .later-grp h3::after{{content:"coming later";margin-left:10px;font:500 11px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--faint);vertical-align:3px}}
  .later-grp .chips span{{background:transparent;color:var(--muted)}}
  .crews{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}}
  .crew{{display:flex;gap:12px;align-items:flex-start;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px}}
  .crew .ic{{flex:0 0 40px;width:40px;height:40px;border-radius:10px;background:#ebe8e2;display:grid;place-items:center}}
  .crew .ic svg{{width:28px;height:28px}}
  .crew b{{font-family:var(--disp);font-size:16px}}
  .crew p{{margin:2px 0 0;color:var(--muted);font-size:14px;line-height:1.45}}
  .sector{{display:grid;grid-template-columns:150px 1fr;gap:26px;padding:28px 0;border-top:1px solid var(--line)}}
  .sector:first-child{{border-top:0}}
  .sector .art{{display:flex;justify-content:center;align-items:flex-start}}
  .sector .art svg{{width:120px;height:auto}}
  .sector h3{{font-family:var(--disp);font-weight:800;font-size:26px;margin:4px 0 8px;text-wrap:balance}}
  .moment{{font-size:17px;margin:0 0 14px;max-width:62ch}}
  .jobs{{list-style:none;margin:0;padding:0;display:grid;gap:8px;max-width:66ch}}
  .jobs li{{padding-left:22px;position:relative;color:var(--muted)}}
  .jobs li::before{{content:"→";position:absolute;left:0;color:var(--mint)}}
  .jobs b{{color:var(--ink);font-weight:600}}
  .soon{{margin:14px 0 0;font-size:14px;color:var(--muted);border-left:3px solid var(--mint);padding-left:12px;max-width:62ch}}
  .later .moment{{color:var(--muted)}}
  .two{{display:grid;grid-template-columns:1.3fr 1fr;gap:28px}}
  ol.steps{{list-style:none;counter-reset:s;margin:0;padding:0;display:grid;gap:14px}}
  ol.steps.three{{grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px}}
  ol.steps li{{counter-increment:s;align-content:start;display:grid;grid-template-columns:34px 1fr;gap:0 12px}}
  ol.steps li::before{{content:counter(s);grid-row:span 2;width:30px;height:30px;border-radius:50%;background:var(--mint);color:var(--mint-ink);font:800 15px/30px var(--disp);text-align:center}}
  ol.steps b{{font-family:var(--disp);font-size:17px}}
  ol.steps span{{color:var(--muted);font-size:15px}}
  .never{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:20px 22px}}
  .never ul{{margin:8px 0 0;padding-left:18px;color:var(--muted)}}
  .never li{{margin:6px 0}}
  .price{{display:flex;flex-wrap:wrap;gap:10px 28px;color:var(--muted);margin:18px 0 22px}}
  .price b{{color:var(--ink)}}
  footer{{padding:28px 0 48px;color:var(--faint);font-size:14px}}
  .printonly{{display:none}}
  @media (max-width:520px){{nav a.ghost{{display:none}}nav a.btn{{padding:8px 12px;font-size:14px;white-space:nowrap}}}}
  @media (max-width:720px){{.sector{{grid-template-columns:1fr;gap:10px}}.sector .art{{justify-content:flex-start}}.sector .art svg{{width:84px}}.two{{grid-template-columns:1fr}}}}
  @media print{{
    :root{{--bg:#fff;--surface:#f6f4ef;--ink:#0f2a1d;--muted:#3d4a42;--faint:#6f7d75;--mint:#0f5132;--mint-ink:#fff;--line:#d6d1c6}}
    @page{{size:letter;margin:.55in}}
    nav,.noprint{{display:none}} .printonly{{display:block}} header{{padding:0 0 14px}} section{{padding:16px 0}}
    h1{{font-size:34px}} .sub{{font-size:14px}} h2{{font-size:22px}} .lede{{font-size:13px;margin-bottom:12px}}
    .crews{{grid-template-columns:repeat(2,1fr);gap:8px}} .crew{{padding:9px}} .crew p{{font-size:12px}}
    .sector{{break-inside:avoid;padding:10px 0;grid-template-columns:70px 1fr;gap:14px}} .sector .art svg{{width:62px}}
    .sector h3{{font-size:19px;margin:2px 0 4px}} .moment{{font-size:13px;margin-bottom:8px}} .jobs{{gap:3px}} .jobs li{{font-size:12px}} .soon{{font-size:11.5px}}
    ol.steps span,.never li{{font-size:12px}} .crew,.never{{break-inside:avoid}}
    .grp{{break-inside:avoid;padding:10px 12px}} .grp p{{font-size:11.5px;margin-bottom:6px}} .chips span{{font-size:10.5px;padding:2px 7px}} .grps{{grid-template-columns:repeat(2,1fr);gap:8px}}
 h2{{break-after:avoid}} .two,.price{{break-inside:avoid}}
    .sector{{padding:7px 0}} ol.steps{{gap:6px}} ol.steps b{{font-size:14px}} .never{{padding:12px 14px}} .price{{margin:10px 0 0;font-size:12.5px}} footer{{display:none}}
    a{{text-decoration:none}} *{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
  }}
</style>
</head>
<body>
<div class="wrap">
  <nav>
    <a href="index.html"><img src="brand/autoants-logo-reverse.svg" alt="autoants home" style="height:28px;width:auto;display:block"></a>
    <div class="sp"></div>
    <a class="ghost" href="index.html">Home</a>
    <a class="ghost" href="services.html">Services</a>
    <a class="btn" href="index.html#contact">Free preview</a>
  </nav>
  <header>
    <img class="printonly" src="brand/autoants-logo.svg" alt="autoants" style="height:34px;width:auto;margin-bottom:14px">
    <div class="eyebrow">Who we help</div>
    <h1>If your phone rings and your calendar matters, <em>the crew fits.</em></h1>
    <p class="sub">autoants builds automated assistants for local businesses that run on calls, messages and appointments. Here are the businesses we help.</p>
    <p class="printonly" style="font-size:14px;margin:12px 0 0"><b>Get your free preview:</b> autoants.com · lane@autoants.com</p>
  </header>
  <section id="all">
    <h2>The businesses we help</h2>
    <p class="lede">Find yours. Don't see it? If customers call or book with you, ask us.</p>
    <div class="grps">{allb}</div>
  </section>
  <section class="noprint" id="sell-to">
    <h2>Selling to local businesses?</h2>
    <p class="lede">Some owners don't need an assistant. They need to know who needs them this week.</p>
    <div class="sells">{sell}</div>
    <p class="lede" style="margin:14px 0 0">Want the counts behind these lists, for your own market? <a href="data/" style="color:var(--mint);font-weight:600">See the datasets →</a></p>
    <div class="nl" id="permit-report">
      <div class="nl-copy"><div class="eyebrow">Free · once a month</div><h3>Permits Pulled</h3>
        <p>A monthly read on what New Orleans' public records say about where the work is, from the same records these lists come from: re-roofs by ZIP, where houses are getting work, and what kinds of businesses just opened. Counts only, a two-minute read.</p></div>
      <form class="nl-form" data-newsletter action="#permit-report" method="post">
        <label class="sr" for="nl-email-who">Your email</label>
        <input id="nl-email-who" type="email" name="email" placeholder="you@yourbusiness.com" autocomplete="email" required>
        <label class="sr" for="nl-seg-who">I mostly…</label>
        <select id="nl-seg-who" name="segment" required>
          <option value="" disabled selected>I mostly…</option>
          <option value="trades">fix or build homes</option>
          <option value="sells-to-business">sell to local businesses</option>
          <option value="real-estate">work in real estate</option>
          <option value="other">something else</option>
        </select>
        <button class="cta" type="submit">Send me the report</button>
        <p class="nl-consent">Monthly. Unsubscribe anytime.</p>
      </form>
    </div>
  </section>
  <section>
    <div class="assess-note"><b>Not sure what you need?</b> Start with a free 15-minute call, or <a href="index.html#assessment">the assessment</a>
      ($500, credited toward setup, any remainder to the first month): a written report on what to automate first, and what each fix is worth.</div>
  </section>
  <section>
    <h2>How it works</h2>
    <ol class="steps three">
      <li><b>Reach out</b><span>Fill out the form, or call or text.</span></li>
      <li><b>See your free preview</b><span>Your new website, built before you pay anything.</span></li>
      <li><b>Pick your crew</b><span>A 15-minute call to choose the assistants that fit.</span></li>
    </ol>
    <a class="cta noprint" href="index.html#contact" style="display:inline-block;margin-top:24px">Get your free preview →</a>
  </section>
  <footer>autoants, short for automated assistants · Louisiana · autoants.com · Commercial services only.</footer>
</div>
<script src="assets/newsletter-signup.js" defer></script>
</body>
</html>
'''


def make_pdf():
    from playwright.sync_api import sync_playwright
    out = os.path.join(SITE, "brand", "print", "brochure")
    os.makedirs(out, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        pg = b.new_page()
        pg.goto("file://" + os.path.join(SITE, "who-we-help.html"), wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        pg.pdf(path=os.path.join(out, "autoants-brochure.pdf"), format="Letter", print_background=True)
        b.close()


if __name__ == "__main__":
    open(os.path.join(SITE, "who-we-help.html"), "w").write(page())
    make_pdf()
    print("who-we-help.html, brand/print/brochure/autoants-brochure.pdf")
