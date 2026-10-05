"""autoants business card: 3.5 x 2 in, 0.125 in bleed, print-ready PDFs plus PNG proofs.

    uv run --with qrcode python3 brand/print/business-card/make_card.py

Front: stone ground (prints reliably, writeable), wordmark, name, contact.
Back: night ground (the site's dark green), the mascot, the promise, and a QR code to the free preview.
Edit CARD below; PHONE stays a red placeholder until there's a real business line."""
import os, subprocess, sys
import qrcode

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(BRAND, "mascot"))
from mascot import mascot, FOREST, MINT, STONE, INK, NIGHT  # noqa: E402

CARD = dict(name="Lane Davis II", title="Founder", email="lane@autoants.com", web="autoants.com",
            phone=None,  # e.g. "(504) 555-0100" once the business line exists
            qr="https://autoants.com/?ref=card#contact")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@500;700;800'
         '&family=JetBrains+Mono:wght@500;700&display=swap">')
W, H, B = 3.75, 2.25, 0.125            # page = trim + bleed on every side
WORD = open(os.path.join(BRAND, "autoants-logo.svg")).read().strip()


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
    s = B * 2 + .06   # inside the safe area
    phone = (f'<div>{CARD["phone"]}</div>' if CARD["phone"]
             else '<div style="color:#d1242f;font-weight:700">PHONE TBD</div>')
    return (f'<div style="position:absolute;left:{s}in;top:{s}in">{WORD.replace("<svg ", "<svg style=\'height:.36in;width:auto;display:block\' ", 1)}</div>'
            f'<div style="position:absolute;left:{s}in;bottom:{s}in;color:{INK}">'
            f'<div style="font:800 13pt/1.1 Onest;letter-spacing:-.01em">{CARD["name"]}</div>'
            f'<div style="font:500 7.5pt/1.2 Onest;color:#4d5a51;margin-top:2pt">{CARD["title"]}</div></div>'
            f'<div style="position:absolute;right:{s}in;bottom:{s}in;text-align:right;font:500 7.5pt/1.55 JetBrains Mono,monospace;color:{INK}">'
            f'{phone}<div>{CARD["email"]}</div><div style="color:{FOREST};font-weight:700">{CARD["web"]}</div></div>'
            f'<div style="position:absolute;right:{s}in;top:{s+.02}in;font:700 6pt JetBrains Mono,monospace;letter-spacing:.14em;text-transform:uppercase;color:{FOREST}">'
            f'automated assistants</div>')


def back():
    s = B * 2 + .06
    hat = mascot("wave", 100, dark=True).replace('width="100" height="130"', 'style="height:1.5in;width:auto;display:block"')
    return (f'<div style="position:absolute;left:{s+.02}in;bottom:{s-.02}in">{hat}</div>'
            f'<div style="position:absolute;left:1.42in;top:{s+.04}in;width:1.2in;font:800 11.5pt/1.08 Onest;letter-spacing:-.02em;color:{STONE};text-wrap:balance">Automated assistants for local businesses.</div>'
            f'<div style="position:absolute;right:{s}in;top:{s}in;background:{STONE};border-radius:.08in;padding:.1in">{qr_svg(CARD["qr"], .74)}</div>'
            f'<div style="position:absolute;right:{s}in;top:{s+1.0}in;width:.94in;text-align:center;font:700 6.5pt/1.3 Onest;color:{MINT}">'
            f'Scan for your free site preview</div>')


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
    for name, inner, ground in (("card-front", front(), STONE), ("card-back", back(), NIGHT)):
        shoot(name, page(inner, ground, guides=False), False)
        shoot(name, page(inner, ground, guides=True), True)
    print("\n".join(sorted(f for f in os.listdir(HERE) if f.startswith("card-"))))
