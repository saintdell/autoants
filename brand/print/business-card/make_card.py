"""autoants business card: 3.5 x 2 in, 0.125 in bleed, print-ready PDFs plus PNG proofs.

    uv run --with qrcode python3 brand/print/business-card/make_card.py

Logo side (card-front): forest green, the reverse wordmark and the tagline, nothing else.
Info side (card-back): white, writeable: name, title, the four service lines, contact, and the QR code
(autoants.com/card, which opens the request form with "Free company breakdown" picked). Lane chose this
design 2026-11-16 ("Card 2").
Edit CARD below; PHONE stays a red placeholder until there's a real business line."""
import os, subprocess, sys
import qrcode

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(BRAND, "mascot"))
from mascot import mascot, FOREST, MINT, STONE, INK, NIGHT  # noqa: E402

CARD = dict(name="Lane Davis II", title="Founder", email="lane@autoants.com", web="autoants.com",
            phone="(504) 499-1194",  # the autoants line, live and tested 2026-10-30
            qr="https://autoants.com/card")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@500;700;800'
         '&family=JetBrains+Mono:wght@500;700&display=swap">')
W, H, B = 3.75, 2.25, 0.125            # page = trim + bleed on every side
WORD = open(os.path.join(BRAND, "autoants-logo.svg")).read().strip()
WORD_REV = open(os.path.join(BRAND, "autoants-logo-reverse.svg")).read().strip()
WHITE = "#ffffff"
LINES = ("Get found on Google and ChatGPT", "Answer the calls you miss, day or night",
         "Ask every customer for a Google review", "Turn finished jobs into social media posts",
         "AI tools set up and managed for you")
# Simple line icons (24-unit viewBox, stroke = currentColor), one per LINES entry, then phone/mail/web.
_I = '<svg viewBox="0 0 24 24" style="width:{w}in;height:{w}in;display:block;flex:none" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">{p}</svg>'
ICONS = (
    '<path d="M12 21s-6-5.6-6-10.5A6 6 0 0 1 18 10.5C18 15.4 12 21 12 21z"/><circle cx="12" cy="10.5" r="2.2"/>',
    '<path d="M5 4h3l1.6 4-2 1.3a11 11 0 0 0 5.1 5.1l1.3-2 4 1.6v3a2 2 0 0 1-2.2 2A16 16 0 0 1 3 6.2 2 2 0 0 1 5 4z"/><path d="M15 3.5a5.5 5.5 0 0 1 5.5 5.5"/>',
    '<path d="M12 3.2l2.6 5.5 6 .8-4.4 4.2 1.1 6-5.3-2.9-5.3 2.9 1.1-6-4.4-4.2 6-.8z"/>',
    '<path d="M4 8h3l1.5-2.5h7L17 8h3a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/><circle cx="12" cy="13.2" r="3.4"/>',
    '<circle cx="12" cy="12" r="3.2"/><path d="M12 2.8l1.6 2.3 2.7-.8.6 2.8 2.7.9-.6 2.7 2 1.9-2 1.9.6 2.7-2.7.9-.6 2.8-2.7-.8L12 21.2l-1.6-2.3-2.7.8-.6-2.8-2.7-.9.6-2.7-2-1.9 2-1.9-.6-2.7 2.7-.9.6-2.8 2.7.8z"/>',
)
PHONE_I = '<path d="M5 4h3l1.6 4-2 1.3a11 11 0 0 0 5.1 5.1l1.3-2 4 1.6v3a2 2 0 0 1-2.2 2A16 16 0 0 1 3 6.2 2 2 0 0 1 5 4z"/>'
MAIL_I = '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 6 8.5 7 8.5-7"/>'
WEB_I = '<rect x="4" y="5" width="16" height="11" rx="1.5"/><path d="M2 19h20"/>'
def icon(p, w=.11): return _I.format(w=w, p=p)


def qr_svg(url, size_in, fg=INK, ant=False):
    """The QR code as crisp SVG squares. ant=True prints with high error correction (30% recoverable) and puts
    the mint ant face, on a light patch, in the middle: about 9% of the code's area, well inside what H corrects.
    Always re-check the printed proof with two phones (iPhone camera + an Android) before ordering."""
    q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_H if ant else qrcode.constants.ERROR_CORRECT_M)
    q.add_data(url)
    m = q.get_matrix()
    n = len(m)
    rects = "".join(f'<rect x="{x}" y="{y}" width="1.02" height="1.02"/>' for y, row in enumerate(m) for x, v in enumerate(row) if v)
    face = ""
    if ant:
        r = n * 0.15                      # patch radius in modules (diameter 30% of the side, ~7% of the area)
        c = n / 2
        face = (f'<circle cx="{c}" cy="{c}" r="{r}" fill="#e3f1ea"/>'
                f'<circle cx="{c}" cy="{c + r*0.12}" r="{r*0.72}" fill="{MINT}"/>'
                f'<circle cx="{c - r*0.26}" cy="{c + r*0.08}" r="{r*0.11}" fill="{FOREST}"/>'
                f'<circle cx="{c + r*0.26}" cy="{c + r*0.08}" r="{r*0.11}" fill="{FOREST}"/>')
    return (f'<svg viewBox="0 0 {n} {n}" style="width:{size_in}in;height:{size_in}in;display:block" shape-rendering="crispEdges">'
            f'<g fill="{fg}">{rects}</g><g shape-rendering="geometricPrecision">{face}</g></svg>')


def page(inner, ground, guides):
    g = ""
    if guides:  # proof only: trim line (solid) and safe area (dashed)
        g = (f'<div style="position:absolute;left:{B}in;top:{B}in;width:3.5in;height:2in;outline:1px solid #e0457b"></div>'
             f'<div style="position:absolute;left:{B*2}in;top:{B*2}in;width:{3.5-B*2}in;height:{2-B*2}in;outline:1px dashed #e0457b"></div>')
    return (f'<!doctype html><meta charset="utf-8">{FONTS}<style>@page{{size:{W}in {H}in;margin:0}}'
            f'html,body{{margin:0}}*{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}</style>'
            f'<body><div style="position:relative;width:{W}in;height:{H}in;overflow:hidden;background:{ground};font-family:Onest,sans-serif">{inner}{g}</div></body>')


def front():
    """The logo side: wordmark and tagline, centred on forest green, with one soft wave in the lower right
    (Lane, 2026-11-16: "Wave only"; no swoosh, no sparkles). The wave runs into the bleed so trimming can't clip it."""
    s = B * 2 + .06
    wave = (f'<svg style="position:absolute;left:0;top:0;width:{W}in;height:{H}in" viewBox="0 0 375 225" preserveAspectRatio="none">'
            f'<path d="M150 225 C 230 200, 300 170, 375 120 L375 225 Z" fill="#14603d"/></svg>')
    word = WORD_REV.replace("<svg ", "<svg style='height:.5in;width:auto;display:block' ", 1)
    return wave + (f'<div style="position:absolute;left:{s}in;top:{s}in;right:{s}in;bottom:{s}in;display:flex;flex-direction:column;'
            f'align-items:center;justify-content:center;gap:.12in">{word}'
            f'<div style="font:700 8pt Onest;color:{MINT};letter-spacing:.01em">automated assistants for local businesses</div></div>')


def back():
    """The info side: who, what, how to reach, and the QR code. Off-white so it takes a pen."""
    s = B * 2 + .06
    lines = "".join(f'<div style="display:flex;gap:.07in;align-items:center;margin-top:.075in">'
                    f'<span style="color:{FOREST}">{icon(ic)}</span><span>{t}</span></div>' for ic, t in zip(ICONS, LINES))
    sep = f'<span style="width:1px;height:.12in;background:#c9cec9;display:inline-block"></span>'
    item = lambda ic, t, bold=False: (f'<span style="display:inline-flex;align-items:center;gap:.035in;color:{FOREST if bold else INK};'
                                      f'font-weight:{700 if bold else 500}"><span style="color:{FOREST}">{icon(ic, .09)}</span>{t}</span>')
    return (f'<div style="position:absolute;left:{s}in;top:{s}in;right:{s}in;bottom:{s}in">'
            f'<div style="font:800 12.5pt/1.05 Onest;letter-spacing:-.01em;color:{INK}">{CARD["name"]}</div>'
            f'<div style="font:500 7.4pt/1.2 Onest;color:{FOREST};margin-top:2pt">{CARD["title"]} · New Orleans</div>'
            f'<div style="font:500 6.9pt/1.25 Onest;color:#1f2d25;margin-top:.1in;width:2.1in">{lines}</div>'
            f'<div style="position:absolute;right:0;top:.02in;width:.86in;text-align:center">'
            f'<div style="background:#e3f1ea;border-radius:.08in;padding:.06in .05in .05in">{qr_svg(CARD["qr"], .64)}'
            f'<div style="font:700 5.7pt/1.2 Onest;color:{FOREST};margin-top:.04in">Scan to request a free business breakdown</div></div></div>'
            f'<div style="position:absolute;left:0;right:0;bottom:0;border-top:1px solid #d5dad5;padding-top:.05in;'
            f'display:flex;justify-content:space-between;align-items:center;font:500 7pt/1 Onest,sans-serif;font-variant-numeric:tabular-nums">'
            f'{item(PHONE_I, CARD["phone"])}{sep}{item(MAIL_I, CARD["email"])}{sep}{item(WEB_I, CARD["web"], True)}</div></div>')


def shoot(name, html, guides):
    src = os.path.join(HERE, "_render.html")
    open(src, "w").write(html)
    args = [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=6000"]
    if guides:
        subprocess.run(args + ["--force-device-scale-factor=3.125", f"--window-size={int(W*96)},{int(H*96)}",
                               f"--screenshot={os.path.join(HERE, name + '-proof.png')}", "file://" + src], check=True, capture_output=True)
    else:
        subprocess.run(args + ["--no-pdf-header-footer", f"--print-to-pdf={os.path.join(HERE, name + '.pdf')}", "file://" + src],
                       check=True, capture_output=True)
    os.remove(src)


if __name__ == "__main__":
    for name, inner, ground in (("card-front", front(), FOREST), ("card-back", back(), "#fbfaf6")):
        shoot(name, page(inner, ground, guides=False), False)
        shoot(name, page(inner, ground, guides=True), True)
    print("\n".join(sorted(f for f in os.listdir(HERE) if f.startswith("card-"))))
