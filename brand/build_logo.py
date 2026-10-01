#!/usr/bin/env python3
"""Build the AutoAnts logo files from the approved design (R3, 2026-09-30).

The wordmark is Onest ExtraBold (800, SIL Open Font License) converted to outlines, so the
files never depend on the font being installed. Geometry matches the approved canvas board
exactly: 76 px type, letter-spacing -0.045em, a 58 px mint O sitting 2 px below the baseline
and 2 px above cap height, 3 px of space on each side.

Usage: uv run --with fonttools --with uharfbuzz python brand/build_logo.py <path-to-Onest[wght].ttf>
Writes brand/*.svg.
"""
import os
import sys

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

HERE = os.path.dirname(os.path.abspath(__file__))

FOREST, MINT, STONE, INK = "#0f5132", "#3ddcae", "#ebe8e2", "#0f2a1d"
SIZE = 76.0                      # px, the size the board was approved at
TRACK = -0.045 * SIZE            # CSS letter-spacing, added after every letter
BASE = 63.5                      # baseline from the top of the 76 px line box (measured)
ANT_W, ANT_H, ANT_BOTTOM = 62.0, 86.0, 10.5   # the O-ant box and its offset above the line bottom
ANT_MARGIN = 3.0


def ant(x, y, stroke, eyes, body=MINT, scale=1.0):
    """The O-ant, drawn in its own 62x86 box placed at (x, y)."""
    return (f'<g transform="translate({x:.2f} {y:.2f}) scale({scale})">'
            f'<g stroke="{stroke}" stroke-width="4" stroke-linecap="round"><path d="M24 31 15 9M38 31l9-22"/></g>'
            f'<circle cx="15" cy="7.5" r="3.6" fill="{stroke}"/><circle cx="47" cy="7.5" r="3.6" fill="{stroke}"/>'
            f'<circle cx="31" cy="57" r="29" fill="{body}"/>'
            f'<circle cx="21.5" cy="53" r="4.3" fill="{eyes}"/><circle cx="40.5" cy="53" r="4.3" fill="{eyes}"/></g>')


def run_paths(font, hbfont, text, x0, upm):
    """Shape `text` (kerning included), return (svg path data, x after the run)."""
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, {"kern": True, "liga": False})
    gs = font.getGlyphSet()
    order = font.getGlyphOrder()
    k = SIZE / upm
    x, d = x0, []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]
        pen = SVGPathPen(gs)
        gs[name].draw(TransformPen(pen, (k, 0, 0, -k, x + pos.x_offset * k, BASE)))
        d.append(pen.getCommands())
        x += pos.x_advance * k + TRACK
    return " ".join(d), x


def main(ttf):
    vf = TTFont(ttf)
    font = instantiateVariableFont(vf, {"wght": 800})
    tmp = os.path.join(HERE, ".onest-800.ttf")
    font.save(tmp)
    font = TTFont(tmp)
    upm = font["head"].unitsPerEm
    blob = hb.Blob.from_file_path(tmp)
    hbfont = hb.Font(hb.Face(blob))
    os.remove(tmp)

    left, x = run_paths(font, hbfont, "AUT", 0.0, upm)
    ant_x = x + ANT_MARGIN
    ant_y = SIZE - ANT_BOTTOM - ANT_H
    right, x_end = run_paths(font, hbfont, "ANTS", ant_x + ANT_W + ANT_MARGIN, upm)
    width = x_end - TRACK                     # drop the trailing letter-spacing
    top, bottom = ant_y - 1, SIZE - 8          # antenna tips to just under the baseline overshoot
    vb = f"-2 {top:.1f} {width + 4:.1f} {bottom - top:.1f}"

    def wordmark(letters, stroke, eyes):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="AutoAnts">'
                f'<title>AutoAnts</title><path fill="{letters}" d="{left} {right}"/>'
                f'{ant(ant_x, ant_y, stroke, eyes)}</svg>\n')

    files = {
        "autoants-logo.svg": wordmark(INK, FOREST, FOREST),            # on light grounds
        "autoants-logo-reverse.svg": wordmark(STONE, STONE, FOREST),   # on dark grounds
        "autoants-mark.svg": (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 -2 66 90" role="img" aria-label="AutoAnts">'
                              f'<title>AutoAnts</title>{ant(0, 0, FOREST, FOREST)}</svg>\n'),
        "autoants-icon.svg": (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-label="AutoAnts">'
                              f'<title>AutoAnts</title><rect width="128" height="128" rx="28" fill="{FOREST}"/>'
                              f'{ant(29, 12, STONE, FOREST, scale=1.13)}</svg>\n'),
        "favicon.svg": (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
                        f'<rect width="32" height="32" rx="7" fill="{FOREST}"/>'
                        f'<g stroke="{STONE}" stroke-width="2" stroke-linecap="round"><path d="M13 10 10 3M19 10l3-7"/></g>'
                        f'<circle cx="16" cy="19" r="10" fill="{MINT}"/>'
                        f'<circle cx="12.3" cy="17.6" r="1.9" fill="{FOREST}"/><circle cx="19.7" cy="17.6" r="1.9" fill="{FOREST}"/></svg>\n'),
    }
    for name, svg in files.items():
        with open(os.path.join(HERE, name), "w") as f:
            f.write(svg)
        print("wrote", name)


if __name__ == "__main__":
    main(sys.argv[1])
