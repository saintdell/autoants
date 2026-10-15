"""Smaller-ant profile photo (Lane, 2026-10-15). The twinkling footer GIF it also makes was rejected by Lane the same day
("I don't like the twinkle"): the footer uses the still workspace-logo-320x132.png; don't commit footer-twinkle.gif.

    uv run --with pillow python brand/email/build_footer_twinkle.py

footer-twinkle.gif   320x132 (Google's footer size), white ground. Frame 1 is the logo at rest, so mail apps that
                     show only the first frame (Outlook desktop) get the normal logo. Then the left tip twinkles,
                     the right tip twinkles, and it rests again; loops forever.
avatar-small-1024.png  the approved avatar with the ant shrunk inside the same forest square (more breathing room).
Renders through installed Chrome from ../autoants-logo.svg; nothing else changes.
"""
import io, os, re, subprocess, tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.dirname(HERE)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
MINT, FOREST, WHITE = "#3ddcae", "#0f5132", "#ffffff"
W, H = 320, 132
svg0 = open(os.path.join(BRAND, "autoants-logo.svg")).read()
KNOBS = [(15, 7.5), (47, 7.5)]   # antenna tips in the mark's coordinates (circles r=3.6)


def star(cx, cy, s):
    """A four-point sparkle centred on (cx, cy), half-width s."""
    if s <= 0:
        return ""
    t = s * 0.22
    d = (f"M{cx},{cy - s} L{cx + t},{cy - t} L{cx + s},{cy} L{cx + t},{cy + t} L{cx},{cy + s} "
         f"L{cx - t},{cy + t} L{cx - s},{cy} L{cx - t},{cy - t} Z")
    return f'<path d="{d}" fill="{MINT}"/>'


def frame_svg(left=(FOREST, 3.6, 0.0), right=(FOREST, 3.6, 0.0)):
    s = svg0
    for (cx, cy), (col, r, sp) in zip(KNOBS, (left, right)):
        s = s.replace(f'<circle cx="{cx}" cy="{cy}" r="3.6" fill="{FOREST}"/>',
                      f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}"/>' + star(cx, cy, sp), 1)
    return s


def render(svg, tmp, i):
    html = (f'<!doctype html><html><head><style>html,body{{margin:0;width:{W}px;height:{H}px;background:{WHITE}}}'
            f'div{{width:{W}px;height:{H}px;display:flex;align-items:center;justify-content:center}}'
            f'svg{{width:290px;height:auto;overflow:visible}}</style></head><body><div>{svg}</div></body></html>')
    p = os.path.join(tmp, f"f{i}.html"); open(p, "w").write(html)
    png = os.path.join(tmp, f"f{i}.png")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                    f"--window-size={W},{H}", f"--screenshot={png}", "file://" + p], check=True, capture_output=True)
    return Image.open(png).convert("RGB").resize((W, H), Image.LANCZOS)


def main():
    rest = (FOREST, 3.6, 0.0)
    tw = [(MINT, 4.4, 6.0), (MINT, 5.0, 12.0), (MINT, 4.6, 8.0), (MINT, 4.0, 3.5), rest]   # one twinkle
    seq = [(rest, rest, 1800)]
    seq += [(t, rest, 70) for t in tw]
    seq += [(rest, rest, 160)]
    seq += [(rest, t, 70) for t in tw]
    seq += [(rest, rest, 1600)]
    with tempfile.TemporaryDirectory() as tmp:
        frames = [render(frame_svg(l, r), tmp, i) for i, (l, r, _) in enumerate(seq)]
    pal = [f.quantize(colors=64, method=Image.MEDIANCUT, dither=Image.NONE) for f in frames]
    out = os.path.join(HERE, "footer-twinkle.gif")
    pal[0].save(out, save_all=True, append_images=pal[1:], duration=[d for *_, d in seq], loop=0, optimize=True, disposal=1)
    print(out, os.path.getsize(out), "bytes,", len(frames), "frames")

    a = Image.open(os.path.join(HERE, "avatar-1024.png")).convert("RGB")
    small = a.resize((int(1024 * 0.78), int(1024 * 0.78)), Image.LANCZOS)
    bg = Image.new("RGB", (1024, 1024), FOREST)
    off = (1024 - small.width) // 2
    bg.paste(small, (off, off))
    p = os.path.join(HERE, "avatar-small-1024.png"); bg.save(p); print(p)


if __name__ == "__main__":
    main()
