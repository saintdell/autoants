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
LINES = ("Get found on Google and ChatGPT", "Answer and text back missed calls",
         "Turn finished jobs into social posts", "AI advice for the rest of your business")


def qr_svg(url, size_in, fg=INK):
    q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(url)
    m = q.get_matrix()
    n = len(m)
    rects = "".join(f'<rect x="{x}" y="{y}" width="1.02" height="1.02"/>' for y, row in enumerate(m) for x, v in enumerate(row) if v)
    return f'<svg viewBox="0 0 {n} {n}" style="width:{size_in}in;height:{size_in}in;display:block" fill="{fg}" shape-rendering="crispEdges">{rects}</svg>'


def page(inner, ground, guides):
    g = ""
    if guides:  # proof only: trim line (solid) and safe area (dashed)
        g = (f'<div style="position:absolute;left:{B}in;top:{B}in;width:3.5in;height:2in;outline:1px solid #e0457b"></div>'
             f'<div style="position:absolute;left:{B*2}in;top:{B*2}in;width:{3.5-B*2}in;height:{2-B*2}in;outline:1px dashed #e0457b"></div>')
    return (f'<!doctype html><meta charset="utf-8">{FONTS}<style>@page{{size:{W}in {H}in;margin:0}}'
            f'html,body{{margin:0}}*{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}</style>'
            f'<body><div style="position:relative;width:{W}in;height:{H}in;overflow:hidden;background:{ground};font-family:Onest,sans-serif">{inner}{g}</div></body>')


def front():
    """The logo side: wordmark and tagline, centred on forest green."""
    s = B * 2 + .06
    word = WORD_REV.replace("<svg ", "<svg style='height:.5in;width:auto;display:block' ", 1)
    return (f'<div style="position:absolute;left:{s}in;top:{s}in;right:{s}in;bottom:{s}in;display:flex;flex-direction:column;'
            f'align-items:center;justify-content:center;gap:.12in">{word}'
            f'<div style="font:700 8pt Onest;color:{MINT};letter-spacing:.01em">Automated assistants for local businesses.</div></div>')


def back():
    """The info side: who, what, how to reach, and the QR code. White so it takes a pen."""
    s = B * 2 + .06
    lines = "".join(f'<div style="display:flex;gap:.05in;align-items:baseline"><span style="color:{FOREST};font-weight:800">&#8226;</span>'
                    f'<span>{t}</span></div>' for t in LINES)
    phone = (f'<div>{CARD["phone"]}</div>' if CARD["phone"]
             else '<div style="color:#d1242f;font-weight:700">PHONE TBD</div>')
    return (f'<div style="position:absolute;left:{s}in;top:{s}in;right:{s}in;bottom:{s}in">'
            f'<div style="font:800 12pt/1.1 Onest;letter-spacing:-.01em;color:{INK}">{CARD["name"]}</div>'
            f'<div style="font:500 7.5pt/1.2 Onest;color:#4d5a51;margin-top:2pt">{CARD["title"]} · New Orleans</div>'
            f'<div style="font:500 6.8pt/1.45 Onest;color:#2f3d35;margin-top:.07in">{lines}</div>'
            f'<div style="position:absolute;left:0;bottom:0;font:500 6.9pt/1.55 JetBrains Mono,monospace;color:{INK}">'
            f'{phone}<div>{CARD["email"]}</div><div style="color:{FOREST};font-weight:700">{CARD["web"]}</div></div>'
            f'<div style="position:absolute;right:0;bottom:0;width:.84in;text-align:center">'
            f'<div style="background:#f1efe9;border-radius:.07in;padding:.07in;display:inline-block">{qr_svg(CARD["qr"], .62)}</div>'
            f'<div style="font:700 5.6pt/1.2 Onest;color:{FOREST};margin-top:.03in">Scan to request a free breakdown</div></div></div>')


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
    for name, inner, ground in (("card-front", front(), FOREST), ("card-back", back(), WHITE)):
        shoot(name, page(inner, ground, guides=False), False)
        shoot(name, page(inner, ground, guides=True), True)
    print("\n".join(sorted(f for f in os.listdir(HERE) if f.startswith("card-"))))
