"""autoants walk-in postcard v2 (Lane's ChatGPT layout, 2026-11-16), Vistaprint size 6.12 x 4.12 in (0.06 in bleed).
Mass print: signed autoants + hello@autoants.com (no-name-on-mass-print rule). Not a mailer (no address panel)."""
import os, subprocess
import make_card as C

W, H = 6.12, 4.12
S = 0.36   # content inset from the page edge (0.3 in inside the trim)
QR = "https://autoants.com/?ref=postcard&interest=Free+Business+Breakdown#contact"
ROWS = ((C.ICONS[0], "Get found on Google and ChatGPT", "Improve your Google profile, listings, and online visibility."),
        (C.ICONS[1], "AI answers when you can't, day or night", "Answers overflow and after-hours calls. Texts back missed callers."),
        (C.ICONS[2], "Google reviews and social media posts", "Review requests and posts from finished jobs."))
PLAY = '<rect x="3" y="4" width="18" height="12" rx="1.5"/><path d="M1.5 19.5h21"/><path d="M10 7.5v5l4.2-2.5z" fill="currentColor"/>'


def page(inner, ground):
    return (f'<!doctype html><meta charset="utf-8">{C.FONTS}<style>@page{{size:{W}in {H}in;margin:0}}'
            f'html,body{{margin:0}}*{{-webkit-print-color-adjust:exact;print-color-adjust:exact;box-sizing:border-box}}</style>'
            f'<body><div style="position:relative;width:{W}in;height:{H}in;overflow:hidden;background:{ground};font-family:Onest,sans-serif">{inner}</div></body>')


def front():
    wave = (f'<svg style="position:absolute;left:0;top:0;width:{W}in;height:{H}in" viewBox="0 0 612 412" preserveAspectRatio="none">'
            f'<path d="M260 412 C 380 372, 500 320, 612 220 L612 412 Z" fill="#14603d"/></svg>')
    word = C.WORD_REV.replace("<svg ", "<svg style='height:.42in;width:auto;display:block' ", 1)
    under = (f'<svg viewBox="0 0 300 12" style="width:2.7in;height:.11in;display:block;margin-top:.04in" preserveAspectRatio="none">'
             f'<path d="M4 8 C 90 2, 210 2, 296 6" stroke="{C.MINT}" stroke-width="5" fill="none" stroke-linecap="round"/></svg>')
    return wave + (f'<div style="position:absolute;left:{S}in;top:{S}in;right:{S}in;bottom:{S}in">'
                   f'<div style="display:flex;align-items:flex-end;gap:.16in">{word}'
                   f'<span style="width:1px;height:.3in;background:rgba(235,232,226,.45);margin-bottom:.02in"></span>'
                   f'<span style="font:600 10.5pt/1 Onest;color:{C.MINT};white-space:nowrap;position:relative;top:-.66em">automated assistants for local businesses</span></div>'
                   f'<div style="font:800 30pt/1.06 Onest;letter-spacing:-.015em;color:#f4f2ec;margin-top:.32in">What happens when a customer calls and '
                   f'<span style="color:{C.MINT}">nobody answers?</span></div>{under}'
                   f'<div style="font:500 11.5pt/1.4 Onest;color:#e3ece6;margin-top:.18in;width:4.3in">autoants helps local businesses answer calls, follow up with customers, '
                   f'and automate everyday work. We set up and manage the AI tools for you.</div></div>')


def back():
    rows = "".join(f'<div style="display:flex;gap:.12in;align-items:flex-start;margin-top:.12in">'
                   f'<span style="flex:none;width:.36in;height:.36in;border-radius:.08in;background:#e3f1ea;color:{C.FOREST};display:flex;align-items:center;justify-content:center">{C.icon(ic, .2)}</span>'
                   f'<span><span style="display:block;font:700 9.6pt/1.18 Onest;color:{C.INK}">{t}</span>'
                   f'<span style="display:block;font:500 8pt/1.28 Onest;color:#3c4a42;margin-top:.02in">{d}</span></span></div>' for ic, t, d in ROWS)
    sep = '<span style="width:1px;height:.2in;background:rgba(235,232,226,.4)"></span>'
    it = lambda ic, t, b=False: (f'<span style="display:inline-flex;align-items:center;gap:.06in;color:#f4f2ec;font-weight:{700 if b else 500}">'
                                 f'<span style="color:{C.MINT}">{C.icon(ic, .14)}</span>{t}</span>')
    word = C.WORD_REV.replace("<svg ", "<svg style='height:.22in;width:auto;display:block' ", 1)
    bar_h = 0.62
    return (f'<div style="position:absolute;left:{S}in;top:{S}in;right:{S}in;bottom:{bar_h + .12}in;display:flex;gap:.22in">'
            f'<div style="flex:1.05">'
            f'<div style="font:800 15pt/1.08 Onest;letter-spacing:-.01em;color:{C.INK}">See where your business could improve.</div>{rows}</div>'
            f'<div style="width:1px;background:#d5dad5;margin:.05in 0"></div>'
            f'<div style="flex:1;background:#e3f1ea;border-radius:.14in;padding:.16in .16in .14in;display:flex;flex-direction:column">'
            f'<div style="display:flex;gap:.08in;align-items:flex-start"><span style="color:{C.FOREST}">{C.icon(PLAY, .36)}</span>'
            f'<span style="font:800 12pt/1.14 Onest;color:{C.INK}">Request a free video breakdown of your business.</span></div>'
            f'<div style="font:500 8.2pt/1.36 Onest;color:#2b3a31;margin-top:.1in">We\'ll look at your Google profile, your website, and the competitors near you. '
            f'Then we\'ll send you a short video and a written report with the first three things we\'d fix.</div>'
            f'<div style="margin-top:auto;padding-top:.12in;border-top:1px solid rgba(15,81,50,.15);display:flex;align-items:center;gap:.14in">'
            f'<div style="background:#fff;border-radius:.06in;padding:.05in;flex:none">{C.qr_svg(QR, .8)}</div>'
            f'<div><div style="font:700 10.5pt/1.18 Onest;color:{C.FOREST}">Scan to request your free video breakdown.</div>'
            f'<div style="font:500 8.3pt/1.35 Onest;color:#3c4a42;margin-top:.05in;white-space:nowrap">Free. No obligation.</div></div></div></div></div>'
            f'<div style="position:absolute;left:0;right:0;bottom:0;height:{bar_h}in;background:{C.FOREST};padding:0 {S}in .06in;'
            f'display:flex;align-items:center;justify-content:space-between;font:500 10pt/1 Onest;font-variant-numeric:tabular-nums">'
            f'{word}{sep}{it(C.PHONE_I, "(504) 499-1194")}{sep}{it(C.MAIL_I, "hello@autoants.com")}{sep}{it(C.WEB_I, "autoants.com", True)}</div>')


def shoot(name, html):
    src = os.path.join(C.HERE, "_render_pc2.html"); open(src, "w").write(html)
    subprocess.run([C.CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=6000", "--no-pdf-header-footer",
                    f"--print-to-pdf={os.path.join(C.HERE, name + '.pdf')}", "file://" + src], check=True, capture_output=True)
    os.remove(src)


if __name__ == "__main__":
    shoot("postcard2-front", page(front(), C.FOREST))
    shoot("postcard2-back", page(back(), "#fbfaf6"))
    print("ok")
