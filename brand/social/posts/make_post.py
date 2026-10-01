"""Post templates for autoants social. Edit posts.json (one row per post), then run:

    python3 brand/social/posts/make_post.py            # every post, every format
    python3 brand/social/posts/make_post.py the-text-back

Each post comes out in three formats in out/:
  feed   1080x1350  Instagram, Facebook and LinkedIn feed (4:5)
  story  1080x1920  Instagram and Facebook stories (9:16); text stays clear of the top and bottom bars
  wide   1920x1080  X and LinkedIn link-style posts, and YouTube thumbnails (16:9)

Copy rules: one outcome per post, the assistant's job not the tech ("AI" never leads),
no numbers or results we can't show, no fake proof."""
import html, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(BRAND, "mascot"))
from mascot import mascot, NIGHT, STONE, MINT  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
WORD = open(os.path.join(BRAND, "autoants-logo-reverse.svg")).read().strip()
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@500;800'
         '&family=JetBrains+Mono:wght@700&display=swap">')
SOFT = "#c9d3cc"
FORMATS = {"feed": (1080, 1350), "story": (1080, 1920), "wide": (1920, 1080)}


def word(h):
    return WORD.replace("<svg ", f'<svg style="height:{h}px;width:auto;display:block" ', 1)


def layout(p, fmt):
    w, h = FORMATS[fmt]
    e, line, sub = (html.escape(p[k]) for k in ("eyebrow", "line", "sub"))
    eyebrow = (f'<div style="font:700 30px JetBrains Mono,monospace;letter-spacing:.16em;text-transform:uppercase;color:{MINT}">{e}</div>')
    if fmt == "wide":
        text = (f'<div style="position:absolute;left:110px;top:150px;width:1060px;display:flex;flex-direction:column;gap:34px">{eyebrow}'
                f'<div style="font:800 112px/1.02 Onest,sans-serif;letter-spacing:-.03em;color:{STONE};text-wrap:balance">{line}</div>'
                f'<div style="font:500 44px/1.3 Onest,sans-serif;color:{SOFT};max-width:900px">{sub}</div></div>'
                f'<div style="position:absolute;left:110px;bottom:90px">{word(64)}</div>')
        art = f'<div style="position:absolute;right:120px;bottom:40px">{mascot(p["pose"], 620, dark=True)}</div>'
    else:
        top = 300 if fmt == "story" else 110          # stories: clear of the progress bar and profile row
        foot = 380 if fmt == "story" else 90          # stories: clear of the reply bar
        m = 560 if fmt == "story" else 520
        text = (f'<div style="position:absolute;left:84px;right:84px;top:{top}px;display:flex;flex-direction:column;gap:30px">{eyebrow}'
                f'<div style="font:800 {116 if fmt == "story" else 104}px/1.02 Onest,sans-serif;letter-spacing:-.03em;color:{STONE};text-wrap:balance">{line}</div>'
                f'<div style="font:500 44px/1.3 Onest,sans-serif;color:{SOFT};max-width:820px">{sub}</div></div>'
                f'<div style="position:absolute;left:84px;bottom:{foot + 10}px">{word(60)}</div>')
        art = f'<div style="position:absolute;right:50px;bottom:{foot - 70}px">{mascot(p["pose"], m, dark=True)}</div>'
    glow = f'radial-gradient(70% 60% at 90% 0%,rgba(61,220,174,.16),transparent 60%),{NIGHT}'
    return (f'<!doctype html><meta charset="utf-8">{FONTS}<body style="margin:0">'
            f'<div style="position:relative;width:{w}px;height:{h}px;overflow:hidden;background:{glow}">{text}{art}</div></body>')


def render(p, fmt, out):
    w, h = FORMATS[fmt]
    src = os.path.join(out, "_render.html")
    open(src, "w").write(layout(p, fmt))
    dest = os.path.join(out, f'{p["slug"]}-{fmt}-{w}x{h}.png')
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--virtual-time-budget=6000", f"--window-size={w},{h}", f"--screenshot={dest}", "file://" + src],
                   check=True, capture_output=True)
    os.remove(src)
    return dest


if __name__ == "__main__":
    posts = json.load(open(os.path.join(HERE, "posts.json")))
    want = set(sys.argv[1:])
    out = os.path.join(HERE, "out")
    os.makedirs(out, exist_ok=True)
    for p in posts:
        if want and p["slug"] not in want:
            continue
        for fmt in FORMATS:
            print(os.path.relpath(render(p, fmt, out), HERE))
