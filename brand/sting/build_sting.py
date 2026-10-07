"""The autoants logo sting: 2.5 s, drawn from the same geometry as ../build_logo.py.

    uv run --with fonttools --with uharfbuzz --with skia-pathops --with playwright --with numpy --with pillow \
        python brand/sting/build_sting.py <path-to-Onest[wght].ttf>

Timeline (seconds):
  0.00-0.08  empty ground
  0.08-0.50  the ant face pops in at the center of the frame, 8% overshoot, settles
  0.38-0.88  the antennae lean in, spring out, settle (one bounce)
  0.88-1.06  one blink
  1.06-1.63  the letters fade in and step outward from the ant to their places (nearest first) while the
             whole wordmark glides from ant-centered to centered; letters only move and fade, never scale
  1.70-2.50  hold. From 1.70 the frame shows the static logo file itself (autoants-logo(-reverse).svg),
             so the end frame is the logo, pixel for pixel; the check below proves it per variant.

Writes video/:
  autoants-sting-1920x1080-night.mp4, -1920x1080-stone.mp4, -1080x1920.mp4, -1080x1080.mp4   silent, H.264
  the same four with -tick: one soft synthesized pop at 0.30 s (the overshoot peak), no music
  autoants-sting-alpha-reverse.mov / -alpha-light.mov   ProRes 4444 with alpha, 1920x1080, for overlays
                                                       (reverse = stone letters for dark footage)
  autoants-sting-alpha-reverse.webm / -alpha-light.webm  VP9 with alpha, same, for the web
and tick.wav (the pop, generated here: a pitch-dropping sine burst with a little filtered noise, no samples
used), contact-sheet.png (12 frames of the night 16:9), check.txt (the swap and clipping checks), and a
poster PNG per opaque video (its end frame = the logo). Renders through installed Chrome, encodes with ffmpeg.
Motion style matches ../mascot/anim/build_loops.py: CSS keyframes, seeked frame by frame, small and calm.
"""
import io
import os
import shutil
import tempfile
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.dirname(HERE)
sys.path.insert(0, BRAND)
import build_logo as B  # noqa: E402

NIGHT = "#0b1712"
DUR, FPS = 2.5, 30
N = int(DUR * FPS)
SWAP = 1.70                    # the static logo takes over here
TICK_AT = 0.08 + 0.55 * 0.42   # the pop's overshoot peak
EASE_OUT = "cubic-bezier(.16,1,.3,1)"
LETTER_IN = 16.0               # wordmark units (76 px type): how far each letter travels; the same for all, so none overlap
SHEET = (0, 4, 9, 13, 15, 19, 29, 34, 37, 41, 51, 74)   # contact-sheet frames: empty, pop, overshoot, settle, antennae in,
                                                        # antennae out, blink closed, letters x3, the swap, the end

VARIANTS = {  # name: (w, h, ground or None for alpha, palette, logo width px)
    "1920x1080-night": (1920, 1080, NIGHT, "reverse", 960),
    "1920x1080-stone": (1920, 1080, B.STONE, "light", 960),
    "1080x1920": (1080, 1920, NIGHT, "reverse", 760),
    "1080x1080": (1080, 1080, NIGHT, "reverse", 760),
    "alpha-reverse": (1920, 1080, None, "reverse", 960),
    "alpha-light": (1920, 1080, None, "light", 960),
}
PAL = {"light": dict(letters=B.INK, stroke=B.FOREST, eyes=B.FOREST, file="autoants-logo.svg"),
       "reverse": dict(letters=B.STONE, stroke=B.STONE, eyes=B.FOREST, file="autoants-logo-reverse.svg")}


def around(cx, cy, cls, inner):
    """Animate `inner` about (cx, cy) without relying on CSS transform-origin in nested SVG groups."""
    return f'<g transform="translate({cx} {cy})"><g class="{cls}"><g transform="translate({-cx} {-cy})">{inner}</g></g></g>'


def animated_svg(G, p):
    (lb, lt), (rb, rt) = B.ANT_ANTENNAE
    kr = B.ANT_KNOBS[2]
    antL = (f'<path d="M{lb[0]} {lb[1]} {lt[0]} {lt[1]}" stroke="{p["stroke"]}" stroke-width="4" stroke-linecap="round"/>'
            f'<circle cx="{B.ANT_KNOBS[0][0]}" cy="{B.ANT_KNOBS[0][1]}" r="{kr}" fill="{p["stroke"]}"/>')
    antR = (f'<path d="M{rb[0]} {rb[1]} {rt[0]} {rt[1]}" stroke="{p["stroke"]}" stroke-width="4" stroke-linecap="round"/>'
            f'<circle cx="{B.ANT_KNOBS[1][0]}" cy="{B.ANT_KNOBS[1][1]}" r="{kr}" fill="{p["stroke"]}"/>')
    (bx, by), br = B.ANT_BODY
    (e1x, ey), (e2x, _), er = B.ANT_EYES
    eyes = f'<circle cx="{e1x}" cy="{ey}" r="{er}" fill="{p["eyes"]}"/><circle cx="{e2x}" cy="{ey}" r="{er}" fill="{p["eyes"]}"/>'
    ant_inner = (around(*lb, "antL", antL) + around(*rb, "antR", antR)
                 + f'<circle cx="{bx}" cy="{by}" r="{br}" fill="{B.MINT}"/>' + around(0, ey, "blink", eyes))
    ant = (f'<g transform="translate({G["ant_x"]:.2f} {G["ant_y"]:.2f}) scale({G["scale"]})">'
           + around(bx, by, "pop", ant_inner) + "</g>")

    css, letters = [], []
    for side, glyphs in (("L", G["left_g"]), ("R", G["right_g"])):
        for i, d in enumerate(glyphs):
            rank = len(glyphs) - 1 - i if side == "L" else i            # nearest the ant arrives first
            off = LETTER_IN * (1 if side == "L" else -1)                # start a short step toward the ant
            delay = 1.06 + 0.04 * rank
            cls = f"g{side}{i}"
            css.append(f".{cls}{{animation:{cls} .45s {EASE_OUT} {delay:.2f}s both,fade .25s linear {delay:.2f}s both}}"
                       f"@keyframes {cls}{{from{{transform:translateX({off:.2f}px)}}to{{transform:none}}}}")
            letters.append(f'<path class="{cls}" fill="{p["letters"]}" d="{d}"/>')
    vbx, vby, vbw, vbh = (float(v) for v in G["vb"].split())
    dx0 = (vbx + vbw / 2) - (G["ant_x"] + 31 * G["scale"])                                      # ant at the center while it is alone
    css.append(f".all{{animation:glide .57s {EASE_OUT} 1.06s both}}@keyframes glide{{from{{transform:translateX({dx0:.2f}px)}}to{{transform:none}}}}")
    return (f'<svg class="anim" xmlns="http://www.w3.org/2000/svg" viewBox="{G["vb"]}"><g class="all">'
            + "".join(letters) + ant + "</g></svg>"), "".join(css)


BASE_CSS = """
.pop{animation:pop .42s .08s both}
@keyframes pop{0%{transform:scale(0);animation-timing-function:cubic-bezier(.3,0,.2,1)}
 55%{transform:scale(1.08);animation-timing-function:cubic-bezier(.4,0,.4,1)}
 80%{transform:scale(.97);animation-timing-function:ease-in-out}100%{transform:scale(1)}}
.antL{animation:antL .5s .38s both ease-in-out}.antR{animation:antR .5s .38s both ease-in-out}
@keyframes antL{0%,100%{transform:rotate(0)}18%{transform:rotate(6deg)}45%{transform:rotate(-12deg)}68%{transform:rotate(4deg)}86%{transform:rotate(-1.5deg)}}
@keyframes antR{0%,100%{transform:rotate(0)}18%{transform:rotate(-6deg)}45%{transform:rotate(12deg)}68%{transform:rotate(-4deg)}86%{transform:rotate(1.5deg)}}
.blink{animation:blink .18s .88s both linear}
@keyframes blink{0%,100%{transform:scaleY(1)}40%{transform:scaleY(.1)}}
@keyframes fade{from{opacity:0}to{opacity:1}}
"""


def page(G, w, h, ground, pal, logo_w, static_only=False):
    p = PAL[pal]
    vbx, vby, vbw, vbh = (float(v) for v in G["vb"].split())
    lh = logo_w * vbh / vbw
    left, top = round((w - logo_w) / 2), round((h - lh) / 2)
    box = f"position:absolute;left:{left}px;top:{top}px;width:{logo_w}px;height:{lh:.3f}px"
    if static_only:   # the hold: the logo file itself, inline, same box, nothing else on the page
        static = open(os.path.join(BRAND, p["file"])).read().replace("<svg ", '<svg width="100%" height="100%" ', 1)
        layers = f'<div style="{box}">{static}</div>'
    else:
        anim, css = animated_svg(G, p)
        anim = anim.replace("<svg ", '<svg width="100%" height="100%" ', 1)
        layers = f'<style>{BASE_CSS}{css}</style><div style="{box}">{anim}</div>'
    bg = f"background:{ground}" if ground else "background:transparent"
    return (f'<!doctype html><meta charset="utf-8"><style>html,body{{margin:0;{bg}}}'
            f'.anim{{position:absolute;inset:0}}</style><body><div style="position:relative;width:{w}px;height:{h}px;overflow:hidden">'
            f'{layers}</div></body>')


def tick(path, sr=48000):
    """A soft pop: 1100->380 Hz sine with a fast exponential decay, a pinch of low-passed noise, peak -14 dBFS."""
    t = np.arange(int(0.14 * sr)) / sr
    f = 380 + 720 * np.exp(-t / 0.018)
    tone = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t / 0.028)
    rng = np.random.default_rng(7)
    noise = np.convolve(rng.standard_normal(t.size), np.ones(24) / 24, "same") * np.exp(-t / 0.004) * 0.35
    env = np.minimum(1, t / 0.0015)
    x = (tone + noise) * env
    x = x / np.abs(x).max() * 10 ** (-14 / 20)
    out = np.zeros(int(DUR * sr))
    i0 = int(TICK_AT * sr)
    out[i0:i0 + x.size] = x
    pcm = (np.stack([out, out], 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as wv:
        wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(sr); wv.writeframes(pcm.tobytes())


def ff(args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def main(ttf):
    from playwright.sync_api import sync_playwright
    f800 = B.load_font(ttf, 800)
    G = B.wordmark_geometry(*f800)
    vdir = os.path.join(HERE, "video")
    tmp = tempfile.mkdtemp(prefix="autoants-sting-")   # frames live outside the repo
    os.makedirs(vdir, exist_ok=True)
    tick(os.path.join(HERE, "tick.wav"))
    color = ["-vf", "scale=out_color_matrix=bt709:out_range=tv", "-colorspace", "bt709",
             "-color_primaries", "bt709", "-color_trc", "bt709"]
    report = []
    with sync_playwright() as pw:
        # software raster: deterministic, and the same raster path for the moving frames and the hold
        b = pw.chromium.launch(executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                               args=["--disable-gpu"])
        for name, (w, h, ground, pal, logo_w) in VARIANTS.items():
            pg = b.new_page(viewport={"width": w, "height": h})
            alpha = ground is None
            fdir = os.path.join(tmp, name)
            os.makedirs(fdir, exist_ok=True)
            html = os.path.join(tmp, f"{name}.html")
            # the hold (SWAP to the end) is the static logo file alone on the page, same box: the end frame IS the logo
            open(html, "w").write(page(G, w, h, ground, pal, logo_w, static_only=True))
            pg.goto("file://" + html, wait_until="load")
            hold = pg.screenshot(type="png", omit_background=alpha)
            open(html, "w").write(page(G, w, h, ground, pal, logo_w))
            for i in range(N):
                out_png = os.path.join(fdir, f"{i:03d}.png")
                if i >= round(SWAP * FPS):
                    open(out_png, "wb").write(hold)
                    continue
                # bake the frame: seek every animation, write its value as a plain style, drop the animation, so
                # Chrome draws a still page (paused animations get compositor layers that anti-alias differently)
                pg.goto("file://" + html, wait_until="load")
                pg.evaluate("t => { for (const a of document.getAnimations()) "
                            "{ a.pause(); a.currentTime = t; a.commitStyles(); a.cancel(); } }", i * 1000 / FPS)
                pg.screenshot(path=out_png, type="png", omit_background=alpha)
            # checks: the swap is invisible (the frame before it is already at rest), nothing clips at any frame
            pre = Image.open(os.path.join(fdir, f"{round(SWAP * FPS) - 1:03d}.png")).convert("RGBA")
            post = Image.open(io.BytesIO(hold)).convert("RGBA")
            under = Image.new("RGBA", post.size, ground or (NIGHT if pal == "reverse" else B.STONE))   # alpha: as seen on its ground
            dl = ImageChops.difference(Image.alpha_composite(under, pre), Image.alpha_composite(under, post)).convert("L")
            moved = sum(dl.point(lambda v: 255 if v > 8 else 0).histogram()[255:])
            margin = min(w, h)
            for i in range(N):
                im = Image.open(os.path.join(fdir, f"{i:03d}.png")).convert("RGBA")
                if alpha:
                    bb = im.getchannel("A").getbbox()
                else:
                    bb = ImageChops.difference(im.convert("RGB"), Image.new("RGB", im.size, ground)).getbbox()
                if bb:
                    margin = min(margin, bb[0], bb[1], w - bb[2], h - bb[3])
            report.append(f"{name}: frames {round(SWAP * FPS)}-{N - 1} are the static logo file; at the swap "
                          f"{moved} px change by more than 8/255 (max {dl.getextrema()[1]}, anti-aliasing only); "
                          f"closest ink to a frame edge across all frames: {margin} px")
            if not alpha:
                post.convert("RGB").save(os.path.join(vdir, f"autoants-sting-{name}-poster.png"))
            pg.close()
            src = ["-framerate", str(FPS), "-i", os.path.join(fdir, "%03d.png")]
            if alpha:
                ff(src + ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-vendor", "apl0",
                          os.path.join(vdir, f"autoants-sting-{name}.mov")])
                ff(src + ["-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "20", "-auto-alt-ref", "0",
                          os.path.join(vdir, f"autoants-sting-{name}.webm")])
            else:
                out = os.path.join(vdir, f"autoants-sting-{name}.mp4")
                ff(src + color + ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "14", "-preset", "slow",
                                  "-movflags", "+faststart", out])
                ff(["-i", out, "-i", os.path.join(HERE, "tick.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out[:-4] + "-tick.mp4"])
            print("wrote", name)
        b.close()
    contact_sheet(os.path.join(tmp, "1920x1080-night"), os.path.join(HERE, "contact-sheet.png"))
    open(os.path.join(HERE, "check.txt"), "w").write("\n".join(report) + "\n")
    shutil.rmtree(tmp)   # a system temp dir
    print("\n".join(report))


def contact_sheet(fdir, out, cols=4, tw=480):
    idx, picks = SHEET, len(SHEET)
    th = round(tw * 1080 / 1920)
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 8, (picks // cols) * (th + 30) + 8), "#1b2a22")
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 15)
    except OSError:
        font = ImageFont.load_default()
    for k, i in enumerate(idx):
        im = Image.open(os.path.join(fdir, f"{i:03d}.png")).convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = 8 + (k % cols) * (tw + 8), 8 + (k // cols) * (th + 30)
        sheet.paste(im, (x, y))
        d.text((x + 2, y + th + 6), f"frame {i:02d}  t={i / FPS:.2f}s", fill="#ebe8e2", font=font)
    sheet.save(out)


if __name__ == "__main__":
    main(sys.argv[1])
