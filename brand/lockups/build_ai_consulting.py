#!/usr/bin/env python3
"""The "autoants / AI CONSULTING" lockup (Lane's pick D, 2026-11-27): the approved wordmark, untouched, with
"AI CONSULTING" in JetBrains Mono 500 caps, widely tracked, left-aligned under it. Text is outlined, so the files
never depend on a font being installed.

Outputs (brand/lockups/):
  ai-consulting.svg / .png                 forest descriptor, for cream and white grounds
  ai-consulting-reverse.svg / .png         mint descriptor, cream wordmark, for the forest ground
  ai-consulting-small.svg / -small-reverse larger, tighter descriptor for sizes under about 48 px tall
                                           (under about 28 px tall, use the wordmark alone)

Usage:
  uv run --with fonttools --with uharfbuzz --with cairosvg python brand/lockups/build_ai_consulting.py <JetBrainsMono-Variable.ttf>
"""
import os, re, sys
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.dirname(HERE)
FOREST, MINT = "#0f5132", "#3ddcae"
TEXT = "AI CONSULTING"


def logo_parts(name):
    s = open(os.path.join(BRAND, name), encoding="utf-8").read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
    body = re.sub(r"(?s)^.*?<svg[^>]*>", "", s)
    body = re.sub(r"(?s)</svg>\s*$", "", body)
    body = re.sub(r"(?s)<title>.*?</title>", "", body)
    return vb, body.strip()


def outline(ttf, text, size, track_em, x0, baseline):
    font = instantiateVariableFont(TTFont(ttf), {"wght": 500})
    tmp = os.path.join(HERE, ".jbm-500.ttf")
    font.save(tmp)
    font = TTFont(tmp)
    face = hb.Face(hb.Blob.from_file_path(tmp))
    hbf = hb.Font(face)
    upm = font["head"].unitsPerEm
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbf, buf, {"kern": True})
    gs, order = font.getGlyphSet(), font.getGlyphOrder()
    k = size / upm
    pen = SVGPathPen(gs)
    x = x0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        g = order[info.codepoint]
        gs[g].draw(TransformPen(pen, Transform(k, 0, 0, -k, x + pos.x_offset * k, baseline - pos.y_offset * k)))
        x += pos.x_advance * k + track_em * size
    cap = font["OS/2"].sCapHeight * k
    os.remove(tmp)
    return pen.getCommands(), x - track_em * size, cap


def build(ttf, logo, color, out, size, track_em, gap):
    (vx, vy, vw, vh), body = logo_parts(logo)
    left = 0.4                      # the wordmark's "a" starts at about x=0 in the logo file
    base = vy + vh + gap            # gap below the wordmark box, then the caps
    d, right, cap = outline(ttf, TEXT, size, track_em, left, 0)
    baseline = base + cap
    d, right, cap = outline(ttf, TEXT, size, track_em, left, baseline)
    w = max(vx + vw, right + 2) - vx
    h = baseline + 4 - vy
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx} {vy} {w:.1f} {h:.1f}" role="img" '
           f'aria-label="autoants, AI consulting"><title>autoants, AI consulting</title>\n{body}\n'
           f'<path fill="{color}" d="{d}"/>\n</svg>\n')
    p = os.path.join(HERE, out + ".svg")
    open(p, "w", encoding="utf-8").write(svg)
    try:
        import cairosvg
        cairosvg.svg2png(url=p, write_to=os.path.join(HERE, out + ".png"), output_width=1600)
    except Exception as e:  # PNG is a convenience; the SVG is the master
        print("png skipped:", e)
    print("wrote", out, f"{w:.0f}x{h:.0f}")


if __name__ == "__main__":
    ttf = sys.argv[1]
    # regular: descriptor about a third of the wordmark's height, tracked .24em (matches the approved concept)
    build(ttf, "autoants-logo.svg", FOREST, "ai-consulting", 22.1, 0.24, 12.0)
    build(ttf, "autoants-logo-reverse.svg", MINT, "ai-consulting-reverse", 22.1, 0.24, 12.0)
    # small cut: bigger, tighter caps so the line still reads on cards, signatures and profile images
    build(ttf, "autoants-logo.svg", FOREST, "ai-consulting-small", 30.0, 0.14, 10.0)
    build(ttf, "autoants-logo-reverse.svg", MINT, "ai-consulting-small-reverse", 30.0, 0.14, 10.0)
