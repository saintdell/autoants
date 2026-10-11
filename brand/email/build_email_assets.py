"""autoants email assets: the inbox profile photo and the animated signature ant.

    uv run --with fonttools --with uharfbuzz --with skia-pathops --with playwright --with numpy --with pillow \
        python brand/email/build_email_assets.py

No font file is needed (the mark has no letters; the extra packages are build_logo.py imports). Renders through installed Chrome, like ../sting/build_sting.py.

The ant is the approved one, untouched: the static files draw it with ../build_logo.py ant(), the animated
frames with the same ANT_* numbers and the sting's own around() wrappers and BASE_CSS keyframes. The motion is
the sting's, not new: antennae lean in, spring out and settle with one bounce (0.38-0.88 s), then one blink
(0.88-1.06 s). The sting's pop-in is left out, so the loop starts and ends on the settled ant (frame 1 is what
Outlook desktop shows) and there is no flash of an empty square between plays.

Writes brand/email/:
  avatar-512.png, avatar-1024.png          the profile photo for every sending inbox (winner: AVATAR below)
  avatar-stone-512.png, avatar-stone-1024.png   the light-ground variant (AVATAR_ALT)
  ant-anim.gif        128 px (shown at 64 CSS px): rest LEAD s, the sting's antennae + blink, rest TAIL s, loop
  ant-anim@1x.gif     the same at 64 px
  ant-still.png       the settled frame, 128 px (for clients or places that want no motion)
  contact-sheet-email.png   avatar candidates at 40/64/128 px on white and Gmail dark, GIF frames on both
"""
import base64
import datetime
import io
import math
import os
import shutil
import sys
import tempfile

import numpy as np
from PIL import Image, ImageChops, ImageSequence

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.dirname(HERE)
sys.path[:0] = [BRAND, os.path.join(BRAND, "sting")]
import build_logo as B  # noqa: E402
import build_sting as S  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
GMAIL_DARK = "#202124"
GROUNDS = {"forest": B.FOREST, "night": S.NIGHT, "stone": B.STONE, "white": "#ffffff"}
DARK = {"forest", "night"}            # stone antennae on these, forest antennae on the light grounds (as in the logo files)
AVATAR, AVATAR_ALT = "forest", "stone"   # chosen on the contact sheet at 40 px (see README)
GIF_GROUND = "forest"                    # solid, so no 1-bit-transparency halo on dark-mode mail
FILL = 0.80          # the ant's smallest enclosing circle / the canvas' inscribed circle: room for the circle crop
GIF_PX, GIF_1X = 128, 64
FPS = 50             # GIF delays are whole centiseconds: 50 fps = 2 cs per frame, exact
T0, T1 = 0.38, 1.06  # from the sting's BASE_CSS: antennae start .38 s; blink ends .88 + .18 s
LEAD, TAIL = 0.6, 2.2   # still before and after each play: 2.8 s of calm between plays
MAX_KB = 60
BAKE = ("t => { for (const a of document.getAnimations()) "
        "{ a.pause(); a.currentTime = t; a.commitStyles(); a.cancel(); } }")   # the sting's frame bake


def circles(rot_l=0.0, rot_r=0.0):
    """The ant's outer circles (cx, cy, r) in its 62x86 box, antennae rotated about their bases (SVG degrees)."""
    (bx, by), br = B.ANT_BODY
    out = [(bx, by, br)]
    for (base, _), (kx, ky), a in zip(B.ANT_ANTENNAE, B.ANT_KNOBS[:2], (rot_l, rot_r)):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        dx, dy = kx - base[0], ky - base[1]
        out.append((base[0] + dx * c - dy * s, base[1] + dx * s + dy * c, B.ANT_KNOBS[2]))
    return out


def reach(cy, cs):
    return max(math.hypot(x - B.ANT_BODY[0][0], y - cy) + r for x, y, r in cs)


def enclosing():
    """Smallest circle around the resting ant; it is symmetric about x=31, so only the center's y is searched."""
    lo, hi = 0.0, 86.0
    for _ in range(100):
        a, b = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        lo, hi = (lo, b) if reach(a, circles()) < reach(b, circles()) else (a, hi)
    cy = (lo + hi) / 2
    return cy, reach(cy, circles())


CY, RAD = enclosing()


def place(n):
    s = FILL * (n / 2) / RAD
    return n / 2 - B.ANT_BODY[0][0] * s, n / 2 - CY * s, s


def colors(ground):
    return (B.STONE if ground in DARK else B.FOREST), B.FOREST   # antennae, eyes


def static_svg(n, ground):
    tx, ty, s = place(n)
    stroke, eyes = colors(ground)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" width="{n}" height="{n}">'
            f'<rect width="{n}" height="{n}" fill="{GROUNDS[ground]}"/>{B.ant(tx, ty, stroke, eyes, scale=s)}</svg>')


def anim_svg(n, ground):
    """The sting's ant (build_sting.animated_svg, ant part) without the pop wrapper, placed like static_svg."""
    tx, ty, s = place(n)
    stroke, eyes_c = colors(ground)
    (lb, lt), (rb, rt) = B.ANT_ANTENNAE
    kr = B.ANT_KNOBS[2]
    antL = (f'<path d="M{lb[0]} {lb[1]} {lt[0]} {lt[1]}" stroke="{stroke}" stroke-width="4" stroke-linecap="round"/>'
            f'<circle cx="{B.ANT_KNOBS[0][0]}" cy="{B.ANT_KNOBS[0][1]}" r="{kr}" fill="{stroke}"/>')
    antR = (f'<path d="M{rb[0]} {rb[1]} {rt[0]} {rt[1]}" stroke="{stroke}" stroke-width="4" stroke-linecap="round"/>'
            f'<circle cx="{B.ANT_KNOBS[1][0]}" cy="{B.ANT_KNOBS[1][1]}" r="{kr}" fill="{stroke}"/>')
    (bx, by), br = B.ANT_BODY
    (e1x, ey), (e2x, _), er = B.ANT_EYES
    eyes = f'<circle cx="{e1x}" cy="{ey}" r="{er}" fill="{eyes_c}"/><circle cx="{e2x}" cy="{ey}" r="{er}" fill="{eyes_c}"/>'
    inner = (S.around(*lb, "antL", antL) + S.around(*rb, "antR", antR)
             + f'<circle cx="{bx}" cy="{by}" r="{br}" fill="{B.MINT}"/>' + S.around(0, ey, "blink", eyes))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" width="{n}" height="{n}">'
            f'<rect width="{n}" height="{n}" fill="{GROUNDS[ground]}"/>'
            f'<g transform="translate({tx:.3f} {ty:.3f}) scale({s:.5f})">{inner}</g></svg>')


class Shooter:
    def __init__(self, browser, tmp):
        self.b, self.tmp, self.k = browser, tmp, 0

    def png(self, body, w, h, t=None, css="", full=False):
        self.k += 1
        html = os.path.join(self.tmp, f"p{self.k}.html")
        open(html, "w").write(f'<!doctype html><meta charset="utf-8"><style>html,body{{margin:0}}svg{{display:block}}{S.BASE_CSS}{css}'
                              f'</style><body>{body}</body>')
        pg = self.b.new_page(viewport={"width": w, "height": h})
        pg.goto("file://" + html, wait_until="load")
        if t is not None:
            pg.evaluate(BAKE, t * 1000)
        out = pg.screenshot(type="png", full_page=full)   # the viewport is the n x n canvas
        pg.close()
        return Image.open(io.BytesIO(out)).convert("RGB")


def gif(frames, durations, path, ground):
    """One shared palette for all frames, no dither; the brand colors snapped exact so the ground never drifts."""
    n = frames[0].width
    strip = Image.new("RGB", (n, n * len(frames)))
    for i, f in enumerate(frames):
        strip.paste(f, (0, i * n))
    q = strip.quantize(colors=48, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = q.getpalette()[:48 * 3]
    for hexc in (GROUNDS[ground], B.MINT, B.STONE, B.FOREST):
        rgb = tuple(int(hexc[i:i + 2], 16) for i in (1, 3, 5))
        j = min(range(48), key=lambda k: sum((pal[3 * k + c] - rgb[c]) ** 2 for c in range(3)))
        pal[3 * j:3 * j + 3] = rgb
    # map every pixel to its nearest entry ourselves: Pillow's palette lookup is approximate and put the ground
    # on a neighbour one step off the brand color
    lut = np.array(pal, dtype=np.int32).reshape(-1, 3)
    qf = []
    for f in frames:
        px = np.asarray(f, dtype=np.int32).reshape(-1, 1, 3)
        idx = ((px - lut[None]) ** 2).sum(2).argmin(1).astype(np.uint8).reshape(f.height, f.width)
        im = Image.fromarray(idx, "P")
        im.putpalette(pal)
        qf.append(im)
    qf[0].save(path, save_all=True, append_images=qf[1:], duration=durations, loop=0, optimize=False, disposal=1)
    return os.path.getsize(path)


def uri(img_or_path):
    if isinstance(img_or_path, str):
        data, mime = open(img_or_path, "rb").read(), "image/gif" if img_or_path.endswith(".gif") else "image/png"
    else:
        buf = io.BytesIO()
        img_or_path.save(buf, "PNG")
        data, mime = buf.getvalue(), "image/png"
    return f"data:{mime};base64," + base64.b64encode(data).decode()


def gif_frames(path):
    """Decoded frames of the written GIF (what a mail client shows), each with its start time in the cycle."""
    im, t, out = Image.open(path), 0, []
    for fr in ImageSequence.Iterator(im):
        out.append((t, fr.convert("RGB")))
        t += fr.info.get("duration", 0)
    return out


def main():
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp(prefix="autoants-email-")
    report = []
    times = [T0 + k / FPS for k in range(round((T1 - T0) * FPS) + 1)]
    durs = [round(LEAD * 1000)] + [round(1000 / FPS)] * (len(times) - 2) + [round(TAIL * 1000)]
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=CHROME, args=["--disable-gpu"])
        sh = Shooter(b, tmp)
        # avatars: three candidates, rendered at full size (no resampling of a smaller master)
        avatars = {}
        for g in ("forest", "night", "stone"):
            for n in (512, 1024):
                avatars[g, n] = sh.png(static_svg(n, g), n, n)
        avatars[AVATAR, 512].save(os.path.join(HERE, "avatar-512.png"), optimize=True)
        avatars[AVATAR, 1024].save(os.path.join(HERE, "avatar-1024.png"), optimize=True)
        avatars[AVATAR_ALT, 512].save(os.path.join(HERE, f"avatar-{AVATAR_ALT}-512.png"), optimize=True)
        avatars[AVATAR_ALT, 1024].save(os.path.join(HERE, f"avatar-{AVATAR_ALT}-1024.png"), optimize=True)

        # GIFs: the chosen ground ships; white is rendered too, for the comparison on the sheet
        gifs = {}
        for g in (GIF_GROUND, "white"):
            for n in (GIF_PX, GIF_1X):
                frames = [sh.png(anim_svg(n, g), n, n, t=t) for t in times]
                still = sh.png(static_svg(n, g), n, n)
                d0 = ImageChops.difference(frames[0], still).getextrema()
                d1 = ImageChops.difference(frames[-1], still).getextrema()
                frames[0] = frames[-1] = still   # the rest frames are the static ant() itself, like the sting's hold
                name = ("ant-anim" if n == GIF_PX else "ant-anim@1x") + ("" if g == GIF_GROUND else f"-{g}")
                path = os.path.join(HERE if g == GIF_GROUND else tmp, name + ".gif")
                size = gif(frames, durs, path, g)
                gifs[g, n] = path
                assert all(f.size == (n, n) for f in frames)
                report.append(f"{name}.gif: {n}px, {len(frames)} frames, {size / 1024:.1f} KB; rest frames are the static "
                              f"ant(); the animated rig at rest differs from it by at most {max(m for _, m in d0 + d1)}/255 "
                              f"(anti-aliasing only)")
                if g == GIF_GROUND and n == GIF_PX:
                    still.save(os.path.join(HERE, "ant-still.png"), optimize=True)
                    if size > MAX_KB * 1024:
                        raise SystemExit(f"{name}.gif is {size / 1024:.1f} KB, over {MAX_KB} KB")
        swing = reach(CY, circles(-12, 12)) / RAD * FILL
        report.append(f"ant fills {FILL:.0%} of the circle crop at rest, {swing:.0%} at the antennae's widest swing")
        report.append(f"cycle: {LEAD:.1f} s still, {T1 - T0:.2f} s motion, {TAIL:.1f} s still "
                      f"({LEAD + TAIL:.1f} s calm between plays)")

        # contact sheet
        today = datetime.date.today().isoformat()

        def avatar_panel(g, bg, fg, sub):
            src = uri(avatars[g, 1024])
            imgs = "".join(f'<div class="sz"><img src="{src}" width="{px}" height="{px}" style="border-radius:50%">'
                           f'<span>{px}px</span></div>' for px in (40, 64, 128))
            row = (f'<div class="row" style="border-color:{sub}"><img src="{src}" width="40" height="40" style="border-radius:50%">'
                   f'<div><b style="color:{fg}">Lane Davis II</b> <span style="color:{sub}">Re: your quote for Thursday - '
                   f'here is the schedule we talked about</span></div></div>')
            return f'<div class="panel" style="background:{bg};color:{fg}">{imgs}{row}</div>'

        def gif_panel(g, bg, fg):
            fr = gif_frames(gifs[g, GIF_PX])
            picks = {}
            for want, label in ((0, "frame 1: rest (Outlook)"), (LEAD * 1000 + 90, "antennae in"),
                                (LEAD * 1000 + 230, "antennae out"), (LEAD * 1000 + 330, "rebound"),
                                (LEAD * 1000 + 570, "blink closed"), (LEAD * 1000 + (T1 - T0) * 1000, "rest, hold")):
                t, im = min(fr, key=lambda x: abs(x[0] - want))
                picks[label] = (t, im)
            cells = "".join(f'<div class="sz"><img src="{uri(im)}" width="128" height="128" style="border-radius:50%">'
                            f'<span>{label}<br>{t / 1000:.2f} s</span></div>' for label, (t, im) in picks.items())
            live = (f'<div class="sz"><img src="{uri(gifs[g, GIF_PX])}" width="64" height="64" style="border-radius:50%">'
                    f'<span>64 CSS px</span></div><div class="sz"><img src="{uri(fr[0][1])}" width="64" height="64">'
                    f'<span>square (Outlook)</span></div>')
            return f'<div class="panel" style="background:{bg};color:{fg}">{cells}{live}</div>'

        sections = []
        for g in ("forest", "night", "stone"):
            tag = " (winner)" if g == AVATAR else (" (light variant)" if g == AVATAR_ALT else "")
            sections.append(f'<h2>Avatar: {g} {GROUNDS[g]}{tag}</h2><div class="pair">'
                            + avatar_panel(g, "#ffffff", "#1f1f1f", "#5f6368")
                            + avatar_panel(g, GMAIL_DARK, "#e8eaed", "#9aa0a6") + "</div>")
        for g in (GIF_GROUND, "white"):
            tag = " (ships as ant-anim.gif)" if g == GIF_GROUND else " (comparison only)"
            sections.append(f'<h2>Signature GIF on {g} ground{tag}: decoded frames, on white and Gmail dark {GMAIL_DARK}</h2>'
                            + gif_panel(g, "#ffffff", "#1f1f1f") + gif_panel(g, GMAIL_DARK, "#e8eaed"))
        css = ("body{background:#f1efe9;font:14px Menlo,monospace;color:#0f2a1d;padding:18px;width:1440px}"
               "h1{font-size:18px;margin:0 0 6px}h2{font-size:14px;margin:18px 0 6px}"
               ".pair{display:flex;gap:10px}.panel{flex:1;display:flex;flex-wrap:wrap;align-items:flex-end;gap:18px;padding:14px;"
               "border-radius:10px;margin-bottom:8px}.sz{display:flex;flex-direction:column;align-items:center;gap:6px;"
               "font-size:12px;text-align:center}.row{display:flex;align-items:center;gap:12px;font:14px Arial,sans-serif;"
               "border-top:1px solid;padding-top:10px;width:100%}")
        body = (f'<h1>autoants email assets - contact sheet, built {today}</h1>'
                f'<div>Avatars are the 1024 px PNG scaled by the browser and cropped to a circle, as Gmail does. '
                f'GIF frames are decoded from the written file.</div>' + "".join(sections))
        sheet = sh.png(body, 1476, 600, css=css, full=True)
        sheet.save(os.path.join(HERE, "contact-sheet-email.png"), optimize=True)
        b.close()
    shutil.rmtree(tmp)   # a system temp dir
    print("\n".join(report))


if __name__ == "__main__":
    main()
