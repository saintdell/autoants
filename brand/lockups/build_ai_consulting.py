#!/usr/bin/env python3
"""The "autoants / AI CONSULTING" lockup (Lane's pick D, 2026-11-27): the approved wordmark, untouched, with
"AI CONSULTING" in JetBrains Mono 500 caps under it, spaced to run exactly from the wordmark's left edge to its right edge. Text is outlined, so the files
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


def ink_bounds(name):
    """Left and right ink edges of the wordmark, from its own paths."""
    from fontTools.svgLib.path import parse_path
    from fontTools.pens.boundsPen import BoundsPen
    s = open(os.path.join(BRAND, name), encoding="utf-8").read()
    pen = BoundsPen(None)
    for d in re.findall(r'\bd="([^"]+)"', s):
        parse_path(d, pen)
    x0, y0, x1, y1 = pen.bounds
    return x0, x1


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


def build(ttf, logo, color, out, size, gap):
    (vx, vy, vw, vh), body = logo_parts(logo)
    left, right_target = ink_bounds(logo)
    n = len(TEXT)
    _, natural_right, cap = outline(ttf, TEXT, size, 0.0, left, 0)
    natural = natural_right - left
    track_em = (right_target - left - natural) / ((n - 1) * size)   # spread so the caps end where the wordmark ends
    baseline = vy + vh + gap + cap
    d, right, cap = outline(ttf, TEXT, size, track_em, left, baseline)
    w = vw
    h = baseline + 4 - vy
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx} {vy} {w:.1f} {h:.1f}" role="img" '
           f'aria-label="autoants, AI consulting"><title>autoants, AI consulting</title>\n{body}\n'
           f'<path fill="{color}" d="{d}"/>\n</svg>\n')
    open(os.path.join(HERE, out + ".svg"), "w", encoding="utf-8").write(svg)
    print("wrote", out, f"caps {left:.1f}..{right:.1f} vs wordmark {left:.1f}..{right_target:.1f}, tracking {track_em:.3f} em")


if __name__ == "__main__":
    ttf = sys.argv[1]
    # regular: descriptor about a third of the wordmark's height, tracked .24em (matches the approved concept)
    build(ttf, "autoants-logo.svg", FOREST, "ai-consulting", 24.0, 12.0)
    build(ttf, "autoants-logo-reverse.svg", MINT, "ai-consulting-reverse", 24.0, 12.0)
    # small cut: bigger, tighter caps so the line still reads on cards, signatures and profile images
    build(ttf, "autoants-logo.svg", FOREST, "ai-consulting-small", 32.0, 10.0)
    build(ttf, "autoants-logo-reverse.svg", MINT, "ai-consulting-small-reverse", 32.0, 10.0)
