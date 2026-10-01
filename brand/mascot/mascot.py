"""The autoants mascot: the logo's ant head on a simple body. Flat, brand colors only.

Drawn in a 200x260 box. Head = the logo ant's head (mint circle, two straight antennae
with round tips, two eyes). Body = rubber-hose style (Lane picked option E on 2026-10-01):
small thorax, slim gaster, curvy noodle arms with mint hands, noodle legs in big ink boots.
Never six legs, never insect detail."""
FOREST, MINT, STONE, INK, NIGHT = "#0f5132", "#3ddcae", "#ebe8e2", "#0f2a1d", "#0b1712"
SW = 8   # limb stroke (rubber hose: thin noodle limbs)
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
    """Rubber-hose (chosen 2026-10-01): a small thorax and a slim gaster, noodle legs
    in big work boots. Limbs are thin curves, never straight sticks."""
    return (f'<path d="M93 208C90 226 82 232 84 244M107 208C110 226 118 232 116 244" stroke="{BODY}" stroke-width="{SW}" '
            f'stroke-linecap="round" fill="none"/>'
            f'<ellipse cx="77" cy="248" rx="19" ry="8.5" fill="{BOOT}"/><ellipse cx="123" cy="248" rx="19" ry="8.5" fill="{BOOT}"/>'
            f'<ellipse cx="100" cy="184" rx="24" ry="30" fill="{BODY}"/>'
            f'<circle cx="100" cy="141" r="14" fill="{BODY}"/>')


def arm(path, hand_xy, hand=True):
    out = f'<path d="{path}" stroke="{BODY}" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
    if hand:
        out += f'<circle cx="{hand_xy[0]}" cy="{hand_xy[1]}" r="10" fill="{MINT}"/>'
    return out


PHONE = lambda x, y: (f'<rect x="{x}" y="{y}" width="20" height="34" rx="5" fill="{INK}"/>'
                      f'<rect x="{x+3}" y="{y+5}" width="14" height="20" rx="2" fill="{STONE}"/>')
CLIP = (f'<rect x="72" y="140" width="56" height="70" rx="6" fill="{INK}"/><rect x="78" y="150" width="44" height="54" rx="3" fill="{STONE}"/>'
        f'<rect x="90" y="135" width="20" height="10" rx="3" fill="{INK}"/>'
        f'<path d="M85 164h28M85 176h28M85 188h18" stroke="{FOREST}" stroke-width="4" stroke-linecap="round"/>'
        f'<path d="M104 188l5 5 10-11" stroke="{MINT}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
ENVELOPE = (f'<g transform="translate(112 146) rotate(-8)"><rect x="0" y="0" width="64" height="44" rx="6" fill="{STONE}" stroke="{INK}" stroke-width="3"/>'
            f'<path d="M5 6l27 20 27-20" stroke="{FOREST}" stroke-width="4.5" fill="none" stroke-linejoin="round"/></g>')

DOWN_L = ("M90 142C70 150 64 176 58 194", (56, 198))           # relaxed left arm
HIP_R = ("M110 146C142 150 144 178 124 176", (122, 176))       # right hand on hip
POSES = {
    "wave": ("Hello", lambda: body() + arm(*DOWN_L) + head("happy") + arm("M110 142C136 134 150 112 152 84", (153, 78))),
    "phone": ("On the phone", lambda: body() + arm("M90 146C58 150 56 178 76 176", (78, 176)) + head("dot", look=-3)
              + PHONE(138, 70) + arm("M110 142C140 140 152 122 146 106", (146, 102))),
    "thumbs": ("Done", lambda: body() + arm(*DOWN_L) + head("happy")
               + arm("M110 142C134 138 152 152 170 146", (174, 146)) + f'<rect x="169" y="121" width="10" height="23" rx="5" fill="{MINT}"/>'),
    "clipboard": ("On it", lambda: body() + head("focused") + CLIP + arm("M90 144C68 156 70 178 80 184", (81, 184))
                  + arm("M110 144C132 156 130 178 120 184", (119, 184))),
    "point": ("This way", lambda: body() + arm(*DOWN_L) + head("dot", look=4)
              + arm("M110 142C140 138 164 126 186 124", (188, 123)) + f'<path d="M193 122h14" stroke="{MINT}" stroke-width="7" stroke-linecap="round"/>'),
    # arms behind the envelope, hands gripping its two side edges
    "carry": ("Got your lead", lambda: body() + head("dot", look=3)
              + arm("M90 144C92 168 104 172 115 168", None, hand=False) + arm("M110 144C142 140 166 150 178 159", None, hand=False)
              + ENVELOPE + f'<circle cx="115" cy="168" r="10" fill="{MINT}"/><circle cx="178" cy="159" r="10" fill="{MINT}"/>'),
    "hardhat": ("On the job", lambda: body() + arm(*DOWN_L) + arm(*HIP_R) + head("dot", hat=True)),
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
