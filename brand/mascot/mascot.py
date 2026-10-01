"""The autoants mascot: the logo's ant head on a simple body. Flat, brand colors only.

Drawn in a 200x260 box. Head = the logo ant's head (mint circle, two straight antennae
with round tips, two eyes). Body = forest torso, two arms with mint hands, two legs
in ink boots. Never six legs, never insect detail."""
FOREST, MINT, STONE, INK, NIGHT = "#0f5132", "#3ddcae", "#ebe8e2", "#0f2a1d", "#0b1712"
SW = 11  # limb stroke
BODY, BOOT, ANT = FOREST, INK, FOREST   # swapped for dark grounds by mascot(dark=True)
FOREST_LIGHT = "#1e7a50"


def eyes(kind="dot", look=0, c=FOREST):
    lx, rx, y = 84 + look, 116 + look, 78
    if kind == "dot":
        return f'<circle cx="{lx}" cy="{y}" r="7" fill="{c}"/><circle cx="{rx}" cy="{y}" r="7" fill="{c}"/>'
    if kind == "happy":
        return (f'<path d="M{lx-8} {y+3}q8 -11 16 0M{rx-8} {y+3}q8 -11 16 0" stroke="{c}" stroke-width="5" '
                f'fill="none" stroke-linecap="round"/>')
    if kind == "wink":
        return (f'<circle cx="{lx}" cy="{y}" r="7" fill="{c}"/>'
                f'<path d="M{rx-8} {y+2}q8 -9 16 0" stroke="{c}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    if kind == "focused":
        return (f'<path d="M{lx-8} {y}h16M{rx-8} {y}h16" stroke="{c}" stroke-width="6" stroke-linecap="round"/>')
    if kind == "surprised":
        return f'<circle cx="{lx}" cy="{y}" r="9" fill="{c}"/><circle cx="{rx}" cy="{y}" r="9" fill="{c}"/>'
    raise ValueError(kind)


def head(eye="dot", look=0, ant_stroke=None, hat=False):
    ant_stroke = ant_stroke or ANT
    ants = (f'<g stroke="{ant_stroke}" stroke-width="6" stroke-linecap="round"><path d="M88 40 74 8M112 40l14-32"/></g>'
            f'<circle cx="74" cy="7" r="6.5" fill="{ant_stroke}"/><circle cx="126" cy="7" r="6.5" fill="{ant_stroke}"/>')
    h = f'<circle cx="100" cy="82" r="46" fill="{MINT}"/>' + eyes(eye, look)
    if hat:  # hard hat: stone shell, forest brim and ridge; antennae come through the top
        h += (f'<path d="M56 64a44 40 0 0 1 88 0z" fill="{STONE}"/><rect x="48" y="60" width="104" height="9" rx="4.5" fill="{FOREST}"/>'
              f'<path d="M100 26v34" stroke="{FOREST}" stroke-width="5"/>')
    return ants + h


def body():
    """An ant's three-part silhouette: the head (drawn by head()), a small thorax and a
    larger gaster, standing upright on two legs in work boots."""
    return (f'<g stroke="{BODY}" stroke-width="{SW+2}" stroke-linecap="round"><path d="M90 222 86 244M110 222l4 22"/></g>'
            f'<ellipse cx="82" cy="248" rx="15" ry="7.5" fill="{BOOT}"/><ellipse cx="118" cy="248" rx="15" ry="7.5" fill="{BOOT}"/>'
            f'<ellipse cx="100" cy="192" rx="37" ry="38" fill="{BODY}"/>'
            f'<circle cx="100" cy="137" r="20" fill="{BODY}"/>')


def arm(path, hand_xy, hand=True):
    out = f'<path d="{path}" stroke="{BODY}" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
    if hand:
        out += f'<circle cx="{hand_xy[0]}" cy="{hand_xy[1]}" r="9" fill="{MINT}"/>'
    return out


PHONE = lambda x, y: (f'<rect x="{x}" y="{y}" width="20" height="34" rx="5" fill="{INK}"/>'
                      f'<rect x="{x+3}" y="{y+5}" width="14" height="20" rx="2" fill="{STONE}"/>')
CLIP = (f'<rect x="72" y="136" width="56" height="70" rx="6" fill="{INK}"/><rect x="78" y="146" width="44" height="54" rx="3" fill="{STONE}"/>'
        f'<rect x="90" y="131" width="20" height="10" rx="3" fill="{INK}"/>'
        f'<path d="M85 160h28M85 172h28M85 184h18" stroke="{FOREST}" stroke-width="4" stroke-linecap="round"/>'
        f'<path d="M104 184l5 5 10-11" stroke="{MINT}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
ENVELOPE = (f'<g transform="translate(112 146) rotate(-8)"><rect x="0" y="0" width="64" height="44" rx="6" fill="{STONE}" stroke="{INK}" stroke-width="3"/>'
            f'<path d="M5 6l27 20 27-20" stroke="{FOREST}" stroke-width="4.5" fill="none" stroke-linejoin="round"/></g>')

L0, R0 = "M85 136", "M115 136"
POSES = {
    "wave": ("Hello", lambda: body() + arm(L0 + " 66 170 58 196", (57, 200)) + head("happy") + arm(R0 + " 148 112 160 78", (161, 72))),
    "phone": ("On the phone", lambda: body() + arm(L0 + " 66 168 80 188", (82, 190)) + head("dot", look=-3)
              + PHONE(138, 70) + arm(R0 + " 150 128 148 106", (146, 102))),
    "thumbs": ("Done", lambda: body() + arm(L0 + " 66 170 58 196", (57, 200)) + head("happy")
               + arm(R0 + " 150 146 172 146", (176, 146)) + f'<rect x="171" y="122" width="10" height="22" rx="5" fill="{MINT}"/>'),
    "clipboard": ("On it", lambda: body() + head("focused") + CLIP + arm(L0 + " 70 162 78 180", (80, 180))
                  + arm(R0 + " 130 162 122 180", (120, 180))),
    "point": ("This way", lambda: body() + arm(L0 + " 66 170 58 196", (57, 200)) + head("dot", look=4)
              + arm(R0 + " 186 124", (188, 123)) + f'<path d="M192 122h14" stroke="{MINT}" stroke-width="7" stroke-linecap="round"/>'),
    "carry": ("Got your lead", lambda: body() + head("dot", look=3) + ENVELOPE
              + arm(L0 + " 96 166 118 168", (118, 168)) + arm(R0 + " 148 156 168 170", (170, 172))),
    "hardhat": ("On the job", lambda: body() + arm(L0 + " 66 170 58 196", (57, 200)) + arm(R0 + " 140 170 126 186", (124, 188))
                + head("dot", hat=True)),
}


def mascot(pose="wave", size=200, extra_attrs="", dark=False):
    global BODY, BOOT, ANT
    BODY, BOOT, ANT = (FOREST_LIGHT, "#33453b", STONE) if dark else (FOREST, INK, FOREST)
    label, draw = POSES[pose]
    h = round(size * 1.3)
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 260" width="{size}" height="{h}" role="img" '
            f'aria-label="autoants mascot: {label}" {extra_attrs}>{draw()}</svg>')
    BODY, BOOT, ANT = FOREST, INK, FOREST
    return out


def face(kind, size=90, ground=None):
    bg = f'<rect width="200" height="150" rx="28" fill="{ground}"/>' if ground else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 150" width="{size}" height="{round(size*.75)}" '
            f'aria-label="{kind}">{bg}<g transform="translate(0 6)">{head(kind)}</g></svg>')
