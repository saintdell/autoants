#!/usr/bin/env python3
"""Build the AutoAnts logo files: the lowercase wordmark "aut·ants" with the ant as the o.

Approved by Lane 2026-10-01 (lowercase replaces the uppercase R3 of 2026-09-30; same ant,
same colors). The wordmark is Onest ExtraBold (800, SIL Open Font License) converted to
outlines, so the files never depend on the font being installed. Geometry comes from the
font's own metrics: the ant's body is 10% larger than the x-height (so it holds up small),
sits on the baseline with a round letter's overshoot, and its antennae rise toward the
height of the t's beside it.

Secondary files (added 2026-10-07, Lane approved the scope; the wordmark and ant above are
reused untouched, only placed):
  lockups/   autoants-stacked(-reverse)   the mark centered above the wordmark
             opsmath-lockup(-reverse)     "Operations Math" over "by aut·ants" (the endorsed line)
  one-color/ <logo|mark|stacked>-<black|white>   one solid color, the eyes cut out as holes,
             everything merged into one outline (vinyl, embroidery, stamps, print)
             <logo|stacked>-small-<black|white>  the same with the antenna weight floored at
             MIN_LINE_MM when printed 1 inch wide (the masters' antennae are thinner than that there)
  each with a PNG at 2x the SVG's nominal (viewBox) size, transparent.

Usage: uv run --with fonttools --with uharfbuzz --with skia-pathops --with playwright \
           python brand/build_logo.py <path-to-Onest[wght].ttf> [--no-png]
Writes brand/*.svg, brand/lockups/*, brand/one-color/*. The PNGs render through installed Chrome.
"""
import os
import sys

import pathops
import uharfbuzz as hb
from fontTools.misc.transform import Transform
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

HERE = os.path.dirname(os.path.abspath(__file__))

FOREST, MINT, STONE, INK = "#0f5132", "#3ddcae", "#ebe8e2", "#0f2a1d"
SIZE = 76.0                      # px, the size the board was approved at
TRACK = -0.045 * SIZE            # CSS letter-spacing, added after every letter
BASE = 63.5                      # baseline from the top of the 76 px line box (measured)
ANT_SCALE_OF_XH = 1.10           # ant body diameter / x-height
OVERSHOOT = 0.02                 # of x-height, below the baseline, like any round letter
ANT_MARGIN_L = 4.0               # px at 76 px type: clears the t's crossbar
ANT_MARGIN_R = 1.5               # px: the a's bowl sits close

# secondary lockups
STACK_MARK_OF_WIDTH = 0.30       # stacked: the mark's width / the wordmark's width
STACK_GAP_OF_XH = 0.55           # stacked: gap between the mark and the wordmark, in x-heights
OPS_TEXT = "Operations Math"
OPS_TRACK = -0.03                # em, the endorsed product line is longer than the wordmark, so a touch looser
OPS_SUB_OF_XH = 0.58             # "by aut·ants": its x-height / the main line's x-height
OPS_GAP_OF_XH = 0.62             # gap between the main line's baseline and the top of the sub-line, in main x-heights
BY_WGHT = 600                    # "by" is quieter than the wordmark beside it
MIN_LINE_MM = 0.5                # thinnest antenna that survives vinyl, a stamp or a running stitch
PRINT_WIDTH_IN = 1.0             # the size the one-color floor is checked at


def ant(x, y, stroke, eyes, body=MINT, scale=1.0):  # drawn in a 62x86 box, body r=29
    """The O-ant, drawn in its own 62x86 box placed at (x, y)."""
    return (f'<g transform="translate({x:.2f} {y:.2f}) scale({scale})">'
            f'<g stroke="{stroke}" stroke-width="4" stroke-linecap="round"><path d="M24 31 15 9M38 31l9-22"/></g>'
            f'<circle cx="15" cy="7.5" r="3.6" fill="{stroke}"/><circle cx="47" cy="7.5" r="3.6" fill="{stroke}"/>'
            f'<circle cx="31" cy="57" r="29" fill="{body}"/>'
            f'<circle cx="21.5" cy="53" r="4.3" fill="{eyes}"/><circle cx="40.5" cy="53" r="4.3" fill="{eyes}"/></g>')


# the same ant as numbers, for the one-color outlines and the sting
ANT_ANTENNAE = (((24, 31), (15, 9)), ((38, 31), (47, 9)))   # base -> tip
ANT_KNOBS = ((15, 7.5), (47, 7.5), 3.6)
ANT_STROKE = 4.0
ANT_BODY = ((31, 57), 29)
ANT_EYES = ((21.5, 53), (40.5, 53), 4.3)


def load_font(ttf, wght):
    """Instance the variable font at `wght`; return (TTFont, hb.Font, upm)."""
    font = instantiateVariableFont(TTFont(ttf), {"wght": wght})
    tmp = os.path.join(HERE, f".onest-{wght}.ttf")
    font.save(tmp)
    font = TTFont(tmp)
    hbfont = hb.Font(hb.Face(hb.Blob.from_file_path(tmp)))
    os.remove(tmp)
    return font, hbfont, font["head"].unitsPerEm


def run_glyphs(font, hbfont, text, x0, upm, size=SIZE, base=BASE, track=None):
    """Shape `text` (kerning included); return ([svg path data per glyph], x after the run)."""
    track = -0.045 * size if track is None else track
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, {"kern": True, "liga": False})
    gs = font.getGlyphSet()
    order = font.getGlyphOrder()
    k = size / upm
    x, d = x0, []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]
        pen = SVGPathPen(gs)
        gs[name].draw(TransformPen(pen, (k, 0, 0, -k, x + pos.x_offset * k, base)))
        d.append(pen.getCommands())
        x += pos.x_advance * k + track
    return d, x


def run_paths(font, hbfont, text, x0, upm):
    """Shape `text` (kerning included), return (svg path data, x after the run)."""
    d, x = run_glyphs(font, hbfont, text, x0, upm)
    return " ".join(d), x


def wordmark_geometry(font, hbfont, upm):
    """Everything about the approved wordmark, in its own (76 px) coordinates."""
    xh = font["OS/2"].sxHeight * SIZE / upm
    scale = ANT_SCALE_OF_XH * xh / 58.0           # the body circle is 58 units across
    ant_w, ant_h = 62.0 * scale, 86.0 * scale
    left_g, x = run_glyphs(font, hbfont, "aut", 0.0, upm)
    ant_x = x + ANT_MARGIN_L
    ant_y = BASE + OVERSHOOT * xh - ant_h          # body bottom on the baseline, plus overshoot
    right_g, x_end = run_glyphs(font, hbfont, "ants", ant_x + ant_w + ANT_MARGIN_R, upm)
    width = x_end - TRACK                          # drop the trailing letter-spacing
    t_top = BASE - 0.72 * SIZE                     # approx top of the t's, for the box
    top = min(ant_y, t_top) - 1
    bottom = BASE + OVERSHOOT * xh + 1             # no descenders in "autoants"
    return dict(xh=xh, scale=scale, ant_x=ant_x, ant_y=ant_y, ant_w=ant_w, ant_h=ant_h,
                left_g=left_g, right_g=right_g, left=" ".join(left_g), right=" ".join(right_g),
                width=width, top=top, bottom=bottom,
                vb=f"-2 {top:.1f} {width + 4:.1f} {bottom - top:.1f}")


# ---------------------------------------------------------------- composition
# A lockup is a list of parts, each ("path", d, role, Transform) or ("ant", (x, y, scale), roles, Transform),
# so one description renders both in color (svg_color) and as one merged outline (svg_mono).

def wm_parts(G, t=Transform(), letters="letters", ant_roles=("ant_stroke", "ant_eyes")):
    return [("path", f'{G["left"]} {G["right"]}', letters, t),
            ("ant", (G["ant_x"], G["ant_y"], G["scale"]), ant_roles, t)]


def mark_parts(x, y, s, t=Transform(), roles=("mark_stroke", "mark_eyes")):
    return [("ant", (x, y, s), roles, t)]


def _tf(t):
    return "" if t == Transform() else ' transform="matrix(%s)"' % " ".join(f"{v:.4f}".rstrip("0").rstrip(".") for v in t)


def svg_color(parts, vb, colors, label="AutoAnts"):
    out = []
    for kind, data, role, t in parts:
        if kind == "path":
            out.append(f'<path{_tf(t)} fill="{colors[role]}" d="{data}"/>')
        else:
            x, y, s = data
            a = ant(x, y, colors[role[0]], colors[role[1]], scale=s)
            out.append(f'<g{_tf(t)}>{a}</g>' if t != Transform() else a)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{label}">'
            f'<title>{label}</title>{"".join(out)}</svg>\n')


def _circle(pen, cx, cy, r):
    k = 0.5522847498 * r
    pen.moveTo((cx + r, cy))
    pen.curveTo((cx + r, cy + k), (cx + k, cy + r), (cx, cy + r))
    pen.curveTo((cx - k, cy + r), (cx - r, cy + k), (cx - r, cy))
    pen.curveTo((cx - r, cy - k), (cx - k, cy - r), (cx, cy - r))
    pen.curveTo((cx + k, cy - r), (cx + r, cy - k), (cx + r, cy))
    pen.closePath()


def _shape(draw, t):
    p = pathops.Path()
    draw(TransformPen(p.getPen(), t))
    return p


def _union(acc, p):
    return pathops.op(acc, p, pathops.PathOp.UNION)


def ant_mono(t, stroke=ANT_STROKE):
    """One-color ant: antennae + knobs + body as one outline, the eyes cut out. `t` places the 62x86 box."""
    knob_r = max(ANT_KNOBS[2], ANT_KNOBS[2] * stroke / ANT_STROKE)   # thicker antennae keep their knobs
    acc = _shape(lambda pen: _circle(pen, *ANT_BODY[0], ANT_BODY[1]), t)
    for (bx, by), (tx, ty) in ANT_ANTENNAE:
        dx, dy = tx - bx, ty - by
        n = (dx * dx + dy * dy) ** 0.5
        nx, ny = -dy / n * stroke / 2, dx / n * stroke / 2

        def bar(pen, bx=bx, by=by, tx=tx, ty=ty, nx=nx, ny=ny):
            pen.moveTo((bx + nx, by + ny)); pen.lineTo((tx + nx, ty + ny))
            pen.lineTo((tx - nx, ty - ny)); pen.lineTo((bx - nx, by - ny)); pen.closePath()
        acc = _union(acc, _shape(bar, t))
        acc = _union(acc, _shape(lambda pen, bx=bx, by=by: _circle(pen, bx, by, stroke / 2), t))   # round cap at the base
    for kx, ky in ANT_KNOBS[:2]:
        acc = _union(acc, _shape(lambda pen, kx=kx, ky=ky: _circle(pen, kx, ky, knob_r), t))
    for ex, ey in ANT_EYES[:2]:
        acc = pathops.op(acc, _shape(lambda pen, ex=ex, ey=ey: _circle(pen, ex, ey, ANT_EYES[2]), t),
                         pathops.PathOp.DIFFERENCE)
    return acc


def _num(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def merge(parts, min_stroke=0.0):
    """All parts as one pathops outline (eyes cut out). `min_stroke` floors the antenna weight, in viewBox units."""
    acc = pathops.Path()
    for kind, data, role, t in parts:
        if kind == "path":
            acc = _union(acc, _shape(lambda pen, d=data: parse_path(d, pen), t))
        else:
            x, y, s = data
            local = t.translate(x, y).scale(s)
            eff = abs(local[0])                                   # viewBox units per ant unit
            acc = _union(acc, ant_mono(local, max(ANT_STROKE, min_stroke / eff)))
    return acc


def fit_vb(parts, pad=2.0):
    """A viewBox around the parts' true ink bounds (descenders, antenna knobs) plus `pad`."""
    x0, y0, x1, y1 = merge(parts).bounds
    return f"{x0 - pad:.1f} {y0 - pad:.1f} {x1 - x0 + 2 * pad:.1f} {y1 - y0 + 2 * pad:.1f}"


def svg_mono(parts, vb, color, min_stroke=0.0, label="AutoAnts"):
    """Everything merged into one outline in one color. `min_stroke` floors the antenna weight, in viewBox units."""
    pen = SVGPathPen(None, ntos=_num)
    merge(parts, min_stroke).draw(pen)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{label}">'
            f'<title>{label}</title><path fill="{color}" d="{pen.getCommands()}"/></svg>\n')


def antenna_mm_at(parts, vb_w, width_in=PRINT_WIDTH_IN):
    """The thinnest antenna in a lockup, in mm, when the file is printed `width_in` wide."""
    thinnest = min(ANT_STROKE * abs(t.translate(*d[:2]).scale(d[2])[0]) for k, d, r, t in parts if k == "ant")
    return thinnest / vb_w * width_in * 25.4


# ---------------------------------------------------------------- lockups

def stacked(G):
    """The mark centered above the wordmark (square and tall spaces)."""
    w = G["width"]
    s = STACK_MARK_OF_WIDTH * w / 62.0
    mx = w / 2 - 31.0 * s
    my = G["top"] - STACK_GAP_OF_XH * G["xh"] - 86.0 * s
    parts = mark_parts(mx, my, s) + wm_parts(G)
    return parts, fit_vb(parts)


def opsmath(G, f800, f600, layout="stacked"):
    """'Operations Math' in Onest 800 with 'by aut·ants' as the endorsed line (stacked: beneath; horizontal: after)."""
    font, hbf, upm = f800
    xh = font["OS/2"].sxHeight * SIZE / upm
    main_g, x_end = run_glyphs(font, hbf, OPS_TEXT, 0.0, upm, track=OPS_TRACK * SIZE)
    main_w = x_end - OPS_TRACK * SIZE
    k = OPS_SUB_OF_XH * xh / G["xh"]                      # scale of the wordmark in the sub-line
    by_font, by_hbf, by_upm = f600
    by_size = SIZE * k
    if layout == "stacked":
        sub_top = BASE + OPS_GAP_OF_XH * xh               # top of the wordmark's box (the antenna tips)
        ty = sub_top - G["top"] * k
        by_x = 0.0
    else:                                                 # horizontal: same baseline, after a gap
        ty = BASE - BASE * k
        by_x = main_w + 0.55 * SIZE
    by_g, by_end = run_glyphs(by_font, by_hbf, "by", by_x, by_upm, size=by_size, base=ty + BASE * k, track=0.0)
    wm_x = by_end + 0.24 * by_size
    t = Transform().translate(wm_x, ty).scale(k)
    parts = ([("path", " ".join(main_g), "main", Transform()), ("path", " ".join(by_g), "by", Transform())]
             + wm_parts(G, t))
    return parts, fit_vb(parts)


LIGHT = dict(letters=INK, ant_stroke=FOREST, ant_eyes=FOREST, mark_stroke=FOREST, mark_eyes=FOREST,
             main=INK, by=FOREST)
REVERSE = dict(letters=STONE, ant_stroke=STONE, ant_eyes=FOREST, mark_stroke=STONE, mark_eyes=FOREST,
               main=STONE, by=MINT)


def render_pngs(svgs):
    """PNG at 2x each SVG's viewBox size, transparent, through the installed Chrome."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        pg = b.new_page(device_scale_factor=2)
        for path in svgs:
            svg = open(path).read()
            vb = [float(v) for v in svg.split('viewBox="')[1].split('"')[0].split()]
            w, h = vb[2], vb[3]
            sized = svg.replace("<svg ", '<svg width="%s" height="%s" ' % (w, h), 1)
            pg.set_content(f'<body style="margin:0;background:transparent">'
                           f'<div id="s" style="width:{w}px;height:{h}px">{sized}</div>')
            pg.locator("#s").screenshot(path=path[:-4] + ".png", omit_background=True)
        b.close()


def main(ttf, png=True):
    f800 = load_font(ttf, 800)
    font, hbfont, upm = f800
    G = wordmark_geometry(font, hbfont, upm)
    left, right, ant_x, ant_y, scale, vb = G["left"], G["right"], G["ant_x"], G["ant_y"], G["scale"], G["vb"]

    def wordmark(letters, stroke, eyes):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="AutoAnts">'
                f'<title>AutoAnts</title><path fill="{letters}" d="{left} {right}"/>'
                f'{ant(ant_x, ant_y, stroke, eyes, scale=scale)}</svg>\n')

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

    # secondary lockups
    st_parts, st_vb = stacked(G)
    f600 = load_font(ttf, BY_WGHT)
    op_parts, op_vb = opsmath(G, f800, f600, "stacked")
    files["lockups/autoants-stacked.svg"] = svg_color(st_parts, st_vb, LIGHT)
    files["lockups/autoants-stacked-reverse.svg"] = svg_color(st_parts, st_vb, REVERSE)
    files["lockups/opsmath-lockup.svg"] = svg_color(op_parts, op_vb, LIGHT, "Operations Math by autoants")
    files["lockups/opsmath-lockup-reverse.svg"] = svg_color(op_parts, op_vb, REVERSE, "Operations Math by autoants")

    # one color: the masters' geometry, plus a floored "-small" cut where 1 inch wide is too thin
    mono = {"logo": (wm_parts(G), vb), "mark": (mark_parts(0, 0, 1.0), "-2 -2 66 90"), "stacked": (st_parts, st_vb)}
    for name, (parts, v) in mono.items():
        vb_w = float(v.split()[2])
        mm = antenna_mm_at(parts, vb_w)
        print(f"one-color {name}: thinnest antenna at {PRINT_WIDTH_IN:g} in wide = {mm:.2f} mm"
              + ("" if mm >= MIN_LINE_MM else f"  (< {MIN_LINE_MM} mm: writing a -small cut)"))
        for cname, c in (("black", "#000000"), ("white", "#ffffff")):
            files[f"one-color/autoants-{name}-{cname}.svg"] = svg_mono(parts, v, c)
            if mm < MIN_LINE_MM:
                floor = MIN_LINE_MM / 25.4 / PRINT_WIDTH_IN * vb_w
                files[f"one-color/autoants-{name}-small-{cname}.svg"] = svg_mono(parts, v, c, min_stroke=floor)

    written = []
    for name, svg in files.items():
        path = os.path.join(HERE, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(svg)
        written.append(path)
        print("wrote", name)
    if png:
        render_pngs([p for p in written if os.sep + "lockups" + os.sep in p or os.sep + "one-color" + os.sep in p])
        print("wrote the 2x PNGs")


if __name__ == "__main__":
    main(sys.argv[1], png="--no-png" not in sys.argv)
