"""autoants door hanger: 4.25 x 11 in, 0.125 in bleed, standard 1.25 in hole. Print-ready PDF + proof.

    uv run --with qrcode python3 brand/print/door-hanger/make_hanger.py

Front (night): wordmark, the waving mascot, the promise, QR + autoants.com.
Back (stone): Meet the crew (the four assistants in The Office Manager, plus a line for the
rest) and How it works (what happens after someone reaches out). Copy matches the site's
own wording. Generic, so it prints in bulk; PHONE stays a red placeholder until the
business line exists.

Hang on business doors only. Never in mailboxes (federal law), on poles (New Orleans CZO
art. 24) or on vehicles, and skip any door marked No soliciting."""
import os, subprocess, sys
import qrcode

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(BRAND, "mascot"))
from mascot import mascot, FOREST, MINT, STONE, INK, NIGHT  # noqa: E402

INFO = dict(phone=None,  # e.g. "(504) 555-0100" once the business line exists
            email="lane@autoants.com", web="autoants.com",
            qr="https://autoants.com/?ref=hanger#contact")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@500;700;800'
         '&family=JetBrains+Mono:wght@500;700&display=swap">')
W, H, B = 4.5, 11.25, 0.125
HOLE_Y, HOLE_D = B + 1.25, 1.25
SOFT = "#c9d3cc"
WORD = open(os.path.join(BRAND, "autoants-logo-reverse.svg")).read().strip()


def qr_svg(url, size_in):
    q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(url)
    m = q.get_matrix()
    n = len(m)
    rects = "".join(f'<rect x="{x}" y="{y}" width="1.02" height="1.02"/>' for y, r in enumerate(m) for x, v in enumerate(r) if v)
    return f'<svg viewBox="0 0 {n} {n}" style="width:{size_in}in;height:{size_in}in;display:block" fill="{INK}" shape-rendering="crispEdges">{rects}</svg>'


def svg_h(svg, h_in):
    return svg.replace("<svg ", f'<svg style="height:{h_in}in;width:auto;display:block" ', 1)


def die(show):
    if not show:
        return ""
    c = "#e0457b"
    return (f'<div style="position:absolute;left:{B}in;top:{B}in;width:{W-2*B}in;height:{H-2*B}in;outline:1px solid {c}"></div>'
            f'<div style="position:absolute;left:{B*2}in;top:{B*2}in;width:{W-4*B}in;height:{H-4*B}in;outline:1px dashed {c}"></div>'
            f'<div style="position:absolute;left:{W/2-HOLE_D/2}in;top:{HOLE_Y-HOLE_D/2}in;width:{HOLE_D}in;height:{HOLE_D}in;border-radius:50%;outline:1px solid {c}"></div>'
            f'<div style="position:absolute;left:{W/2}in;top:{B}in;height:{HOLE_Y-HOLE_D/2-B}in;border-left:1px solid {c}"></div>')


def front(guides):
    m = mascot("wave", 100, dark=True).replace('width="100" height="130"', 'style="height:4.15in;width:auto;display:block"')
    return (f'<div class="pg" style="background:radial-gradient(90% 45% at 85% 30%,rgba(61,220,174,.17),transparent 62%),{NIGHT};color:{STONE}">'
            f'<div style="position:absolute;left:0;right:0;top:2.2in;display:flex;justify-content:center">{svg_h(WORD, .58)}</div>'
            f'<div style="position:absolute;left:.4in;right:.4in;top:3.05in;text-align:center">'
            f'<div style="font:800 23pt/1.02 Onest;letter-spacing:-.03em">Never miss another job.</div>'
            f'<div style="font:500 10.5pt/1.35 Onest;color:{SOFT};margin-top:.08in">Automated assistants for local businesses.</div></div>'
            f'<div style="position:absolute;left:50%;transform:translateX(-50%);top:4.15in">{m}</div>'
            f'<div style="position:absolute;left:.45in;right:.45in;top:8.75in;display:flex;align-items:center;gap:.2in">'
            f'<div style="background:{STONE};border-radius:.09in;padding:.1in">{qr_svg(INFO["qr"], .95)}</div>'
            f'<div><div style="font:800 13pt/1.1 Onest">See what we\'d build you</div>'
            f'<div style="font:700 12pt JetBrains Mono,monospace;color:{MINT};margin-top:.06in">{INFO["web"]}</div>'
            f'<div style="font:500 8.5pt/1.3 Onest;color:{SOFT};margin-top:.05in">Free website preview, built before you pay.</div></div></div>'
            f'{die(guides)}</div>')


CREW = [("phone", "The Callback", "Texts back every missed call."),
        ("carry", "The Responder", "Answers new leads in seconds."),
        ("clipboard", "The Scheduler", "Books the appointment."),
        ("thumbs", "The Reviewer", "Asks every customer for a review.")]
STEPS = ["Scan the code or visit autoants.com", "See your free website preview", "Pick your crew"]


def back(guides):
    crew = "".join(
        f'<div style="display:flex;gap:.16in;align-items:center;padding:.1in 0;border-top:1px solid #d6d1c6">'
        f'<div style="width:.62in;flex:0 0 .62in;display:flex;justify-content:center">'
        f'{mascot(pose, 100).replace(chr(119)+"idth=\"100\" height=\"130\"", "style=\"height:.78in;width:auto;display:block\"")}</div>'
        f'<div><div style="font:800 13pt Onest;color:{INK}">{name}</div><div style="font:500 10.5pt/1.3 Onest;color:#4d5a51">{line}</div></div></div>'
        for pose, name, line in CREW)
    steps = "".join(
        f'<div style="display:flex;gap:.12in;align-items:center;padding:.05in 0">'
        f'<div style="flex:0 0 .28in;height:.28in;border-radius:50%;background:{FOREST};color:{STONE};font:800 10pt/.28in Onest;text-align:center">{i}</div>'
        f'<div style="font:700 11pt Onest;color:{INK}">{t}</div></div>'
        for i, t in enumerate(STEPS, 1))
    phone = INFO["phone"] or '<span style="color:#d1242f;font-weight:700">PHONE TBD</span>'
    return (f'<div class="pg" style="background:{STONE};color:{INK}">'
            f'<div style="position:absolute;left:.42in;right:.42in;top:2.25in">'
            f'<div style="font:700 8pt JetBrains Mono,monospace;letter-spacing:.14em;text-transform:uppercase;color:{FOREST}">Meet the crew</div>'
            f'<div style="font:800 19pt/1.04 Onest;letter-spacing:-.02em;margin-top:.06in;text-wrap:balance">Assistants that work while you\'re busy.</div>'
            f'<div style="margin-top:.16in;border-bottom:1px solid #d6d1c6">{crew}</div></div>'
            f'<div style="position:absolute;left:.42in;right:.42in;top:7.45in">'
            f'<div style="font:700 8pt JetBrains Mono,monospace;letter-spacing:.14em;text-transform:uppercase;color:{FOREST}">How it works</div>'
            f'<div style="margin-top:.08in">{steps}</div></div>'
            f'<div style="position:absolute;left:.42in;right:.42in;bottom:.45in;border-top:2px solid {INK};padding-top:.1in;display:flex;justify-content:space-between;align-items:flex-end">'
            f'<div><div style="font:800 12pt Onest">Lane Davis</div><div style="font:500 8.5pt Onest;color:#4d5a51">founder, autoants</div></div>'
            f'<div style="text-align:right;font:500 8pt/1.55 JetBrains Mono,monospace">{phone}<br>{INFO["email"]}<br><b style="color:{FOREST}">{INFO["web"]}</b></div></div>'
            f'{die(guides)}</div>')


def doc(pages, flex=False):
    wrap = f'<div style="display:flex">{pages}</div>' if flex else pages
    return (f'<!doctype html><meta charset="utf-8">{FONTS}<style>@page{{size:{W}in {H}in;margin:0}}html,body{{margin:0}}'
            f'*{{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}}'
            f'.pg{{position:relative;width:{W}in;height:{H}in;overflow:hidden;font-family:Onest,sans-serif;{"" if flex else "page-break-after:always"}}}</style>'
            f'<body>{wrap}</body>')


def run(html, args):
    src = os.path.join(HERE, "_render.html")
    open(src, "w").write(html)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=6000", *args, "file://" + src],
                   check=True, capture_output=True)
    os.remove(src)


if __name__ == "__main__":
    run(doc(front(False) + back(False)), ["--no-pdf-header-footer", f"--print-to-pdf={os.path.join(HERE, 'door-hanger.pdf')}"])
    run(doc(front(True) + back(True), flex=True), ["--force-device-scale-factor=2", f"--window-size={int(W*96)*2},{int(H*96)}",
                                                  f"--screenshot={os.path.join(HERE, 'door-hanger-proof.png')}"])
    print("door-hanger.pdf, door-hanger-proof.png")
