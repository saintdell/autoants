"""autoants walk-in postcard: 6 x 4 in, 0.125 in bleed. Leave-behind that explains the free breakdown.
Mass print: signed autoants + hello@autoants.com, never Lane's name (no-name-on-mass-print rule).
Not set up for mailing (no address or postage panel)."""
import os, subprocess
import make_card as C

W, H, B = 6.25, 4.25, 0.125
QR = "https://autoants.com/?ref=postcard&interest=Free+Business+Breakdown#contact"
POINTS = ("How you show up on Google and in AI answers like ChatGPT",
          "How you compare with businesses near you",
          "The first three things we'd fix")


def page(inner, ground):
    return (f'<!doctype html><meta charset="utf-8">{C.FONTS}<style>@page{{size:{W}in {H}in;margin:0}}'
            f'html,body{{margin:0}}*{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}</style>'
            f'<body><div style="position:relative;width:{W}in;height:{H}in;overflow:hidden;background:{ground};font-family:Onest,sans-serif">{inner}</div></body>')


def front():
    wave = (f'<svg style="position:absolute;left:0;top:0;width:{W}in;height:{H}in" viewBox="0 0 625 425" preserveAspectRatio="none">'
            f'<path d="M250 425 C 380 380, 500 330, 625 230 L625 425 Z" fill="#14603d"/></svg>')
    word = C.WORD_REV.replace("<svg ", "<svg style='height:.95in;width:auto;display:block' ", 1)
    return wave + (f'<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.2in">'
                   f'{word}<div style="font:700 14pt Onest;color:{C.MINT};letter-spacing:.01em">automated assistants for local businesses</div></div>')


def back():
    s = B + .4
    pts = "".join(f'<div style="display:flex;gap:.1in;align-items:flex-start;margin-top:.06in">'
                  f'<span style="color:{C.MINT};font-weight:800;font-size:13pt;line-height:1">✓</span><span>{t}</span></div>' for t in POINTS)
    sep = '<span style="width:1px;height:.16in;background:#c9cec9;display:inline-block"></span>'
    item = lambda ic, t, bold=False: (f'<span style="display:inline-flex;align-items:center;gap:.05in;color:{C.FOREST if bold else C.INK};'
                                      f'font-weight:{700 if bold else 500}"><span style="color:{C.FOREST}">{C.icon(ic, .13)}</span>{t}</span>')
    word = C.WORD.replace("<svg ", "<svg style='height:.26in;width:auto;display:block' ", 1)
    return (f'<div style="position:absolute;left:{s}in;top:{s}in;right:{s}in;bottom:{s}in">'
            f'{word}'
            f'<div style="font:800 17pt/1.1 Onest;letter-spacing:-.01em;color:{C.INK};margin-top:.14in;width:3.6in">Want a free video breakdown of your business?</div>'
            f'<div style="font:500 9.5pt/1.3 Onest;color:{C.FOREST};margin-top:.08in;width:3.6in">A short video and a written report, made from public information:</div>'
            f'<div style="font:500 9.5pt/1.25 Onest;color:#1f2d25;width:3.6in">{pts}</div>'
            f'<div style="position:absolute;right:0;top:.05in;width:1.55in;text-align:center">'
            f'<div style="background:#e3f1ea;border-radius:.12in;padding:.12in .1in .1in">{C.qr_svg(QR, 1.2)}'
            f'<div style="font:700 9.5pt/1.2 Onest;color:{C.FOREST};margin-top:.08in">Scan to request yours</div></div>'
            f'<div style="font:500 8pt/1.3 Onest;color:#4a5a50;margin-top:.08in">Free. No obligation.</div></div>'
            f'<div style="position:absolute;left:0;right:0;bottom:0;border-top:1px solid #d5dad5;padding-top:.09in;'
            f'display:flex;justify-content:space-between;align-items:center;font:500 10pt/1 Onest,sans-serif;font-variant-numeric:tabular-nums">'
            f'{item(C.PHONE_I, "(504) 499-1194")}{sep}{item(C.MAIL_I, "hello@autoants.com")}{sep}{item(C.WEB_I, "autoants.com", True)}</div></div>')


def shoot(name, html):
    src = os.path.join(C.HERE, "_render_pc.html"); open(src, "w").write(html)
    subprocess.run([C.CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=6000", "--no-pdf-header-footer",
                    f"--print-to-pdf={os.path.join(C.HERE, name + '.pdf')}", "file://" + src], check=True, capture_output=True)
    os.remove(src)


if __name__ == "__main__":
    shoot("postcard-front", page(front(), C.FOREST))
    shoot("postcard-back", page(back(), "#fbfaf6"))
    print("ok")
