#!/usr/bin/env python3
"""Build the ant artwork for autoants.com from the approved Ant boards (Logo Lab, 2026-10-01).

Writes brand/icons/<assistant>.svg (the logo ant holding each assistant's tool, on a light
tile so it reads on the site's dark cards), brand/ants/colony-wide.svg and
brand/ants/colony-tall.svg (the cutaway section, desktop and phone).

Rules from the boards: flat shapes in the brand colors, no legs or realism (to tree crews,
ants are a pest), plain assistant names. Usage: python3 brand/ants/build_ants.py
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.dirname(HERE)
import json, os
FOREST, MINT, STONE, INK, NIGHT = "#0f5132", "#3ddcae", "#ebe8e2", "#0f2a1d", "#0b1712"

def ant(x, y, s, stroke=FOREST, eyes=FOREST, look=0):
    """The logo ant (62x86 box) at (x, y), scale s. look shifts the eyes (-1 left, 1 right)."""
    dx = 2.5 * look
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<g stroke="{stroke}" stroke-width="4" stroke-linecap="round" fill="none"><path d="M24 31 15 9M38 31l9-22"/></g>'
            f'<circle cx="15" cy="7.5" r="3.6" fill="{stroke}"/><circle cx="47" cy="7.5" r="3.6" fill="{stroke}"/>'
            f'<circle cx="31" cy="57" r="29" fill="{MINT}"/>'
            f'<circle cx="{21.5+dx}" cy="53" r="4.3" fill="{eyes}"/><circle cx="{40.5+dx}" cy="53" r="4.3" fill="{eyes}"/></g>')

# Each tool is drawn in a 120x120 icon space, sitting lower-right of the ant.
TOOLS = {
 "Callback": ("phone", f'<g transform="translate(66 62)"><rect x="0" y="0" width="34" height="50" rx="8" fill="{INK}"/><rect x="5" y="7" width="24" height="30" rx="3" fill="{STONE}"/><circle cx="17" cy="43" r="3" fill="{MINT}"/><path d="M30 -10a14 14 0 0 1 14 14" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/><path d="M40 6l4 -2 2 4" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>'),
 "Responder": ("reply", f'<g transform="translate(62 60)"><path d="M0 8a8 8 0 0 1 8-8h34a8 8 0 0 1 8 8v22a8 8 0 0 1-8 8H18l-10 10v-10H8a8 8 0 0 1-8-8z" fill="{INK}"/><path d="M28 6 18 22h9l-4 12 12-17h-9z" fill="{MINT}"/></g>'),
 "Scheduler": ("calendar", f'<g transform="translate(64 62)"><rect x="0" y="6" width="46" height="42" rx="6" fill="{INK}"/><rect x="0" y="6" width="46" height="12" rx="6" fill="{FOREST}"/><rect x="10" y="0" width="5" height="12" rx="2.5" fill="{INK}"/><rect x="31" y="0" width="5" height="12" rx="2.5" fill="{INK}"/><path d="M13 32l6 6 13-13" stroke="{MINT}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>'),
 "Scout": ("magnifier", f'<g transform="translate(64 60)"><circle cx="18" cy="18" r="15" fill="{STONE}" stroke="{INK}" stroke-width="6"/><path d="M29 29l15 15" stroke="{INK}" stroke-width="8" stroke-linecap="round"/><circle cx="18" cy="18" r="6" fill="{MINT}"/></g>'),
 "Receptionist": ("headset", ""),
 "Reviewer": ("star", f'<g transform="translate(64 60)"><path d="M24 0l7 15 16 2-12 11 3 16-14-8-14 8 3-16L1 17l16-2z" fill="{INK}"/><path d="M24 12l3 7 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1z" fill="{MINT}"/></g>'),
 "Promoter": ("megaphone", f'<g transform="translate(62 62)"><path d="M4 16h10l26-14v44L14 32H4a4 4 0 0 1-4-4v-8a4 4 0 0 1 4-4z" fill="{INK}"/><rect x="8" y="32" width="8" height="14" rx="3" fill="{INK}"/><path d="M46 14q6 10 0 20" stroke="{MINT}" stroke-width="4" fill="none" stroke-linecap="round"/></g>'),
 "Reminder": ("bell", f'<g transform="translate(66 60)"><path d="M20 2a14 14 0 0 1 14 14v12l6 8H0l6-8V16A14 14 0 0 1 20 2z" fill="{INK}"/><circle cx="20" cy="42" r="5" fill="{INK}"/><circle cx="32" cy="8" r="6" fill="{MINT}" stroke="{STONE}" stroke-width="2"/></g>'),
}
JOBS = {
 "Callback": "Texts back every missed call in seconds",
 "Responder": "Answers web and form leads right away",
 "Scheduler": "Books the job and sends the reminders",
 "Scout": "Gets you found on Google and in AI answers",
 "Receptionist": "Answers the phone after hours, says it's AI",
 "Reviewer": "Asks every customer for a review",
 "Promoter": "Posts, short videos and local ads",
 "Reminder": "Brings past customers back each season",
}

def icon(name, size=120, ground=None, stroke=FOREST):
    bg = f'<rect width="120" height="120" rx="26" fill="{ground}"/>' if ground else ""
    if name == "Receptionist":
        body = (ant(20, 12, 1.05, stroke) +
                f'<path d="M30 70a24 24 0 0 1 48 0" stroke="{INK}" stroke-width="6" fill="none" stroke-linecap="round" transform="translate(-3 -5)"/>'
                f'<rect x="22" y="58" width="11" height="18" rx="5" fill="{INK}"/><rect x="72" y="58" width="11" height="18" rx="5" fill="{INK}"/>'
                f'<path d="M77 76q0 14-16 16" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/><circle cx="60" cy="92" r="5" fill="{INK}"/>')
    else:
        body = ant(8, 10, 0.95, stroke, look=1) + TOOLS[name][1]
    return f'<svg viewBox="0 0 120 120" width="{size}" height="{size}" aria-label="{name}">{bg}{body}</svg>'



SVG_OPEN, SVG_XY = "<svg ", '<svg x="0" y="0" '
NAMES = list(TOOLS)


def tile(name, size):
    return icon(name, size, ground=STONE).replace(SVG_OPEN, SVG_XY, 1)


def chamber(n, x, y):
    return (f'<g transform="translate({x} {y})"><ellipse cx="0" cy="0" rx="104" ry="64" fill="#173528"/>'
            f'<g transform="translate(-40 -52)">{tile(n, 80)}</g>'
            f'<text x="0" y="48" text-anchor="middle" font-family="Onest, sans-serif" font-weight="700" font-size="17" fill="{STONE}">The {n}</text></g>')


def colony_wide():
    chambers = [("Callback", 210, 470), ("Responder", 470, 400), ("Scheduler", 760, 520), ("Reviewer", 1040, 420),
                ("Receptionist", 1300, 540), ("Scout", 330, 700), ("Reminder", 900, 720), ("Promoter", 1420, 760)]
    tunnels = ('<path d="M780 220 C 760 300, 560 330, 480 400 M780 220 C 790 330, 760 420, 760 520 M480 400 C 380 420, 260 430, 210 470 '
               'M760 520 C 900 470, 980 430, 1040 420 M1040 420 C 1150 450, 1250 500, 1300 540 M210 470 C 230 580, 300 640, 330 700 '
               'M760 520 C 820 600, 870 670, 900 720 M1300 540 C 1360 620, 1400 700, 1420 760" stroke="#173528" stroke-width="40" fill="none" stroke-linecap="round"/>')
    surface = (f'<rect x="0" y="0" width="1672" height="210" fill="{STONE}"/>'
               f'<g fill="{FOREST}"><rect x="200" y="96" width="18" height="114"/><circle cx="209" cy="80" r="62"/><circle cx="160" cy="118" r="40"/><circle cx="262" cy="112" r="44"/></g>'
               f'<g transform="translate(1200 132)"><rect x="0" y="20" width="170" height="52" rx="8" fill="{INK}"/><rect x="118" y="0" width="68" height="72" rx="8" fill="{INK}"/>'
               f'<rect x="130" y="10" width="40" height="22" rx="3" fill="{STONE}"/><circle cx="40" cy="74" r="14" fill="{NIGHT}"/><circle cx="150" cy="74" r="14" fill="{NIGHT}"/>'
               f'<text x="20" y="54" font-family="Onest, sans-serif" font-weight="800" font-size="18" fill="{MINT}">ON THE JOB</text></g>'
               f'<path d="M740 210 q40 -34 80 0z" fill="#c8c1b3"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1672 860" role="img" aria-label="Cutaway of an ant colony under a work site: eight assistants each working in its own chamber while the owner is on the job">'
            f'<rect width="1672" height="860" fill="{NIGHT}"/>' + surface + tunnels + "".join(chamber(*c) for c in chambers) +
            f'<text x="836" y="836" text-anchor="middle" font-family="Onest, sans-serif" font-size="18" fill="#9db0a4">Nothing gets confirmed to a customer without your OK.</text></svg>\n')


def colony_tall():
    w, rows = 640, 4
    pos = [(170, 330 + r * 170) if i % 2 == 0 else (470, 400 + r * 170) for r in range(rows) for i in range(2)]
    tun = " ".join(f"M320 190 C 320 260, {x} {y-80}, {x} {y}" for x, y in pos[:2])
    tun += " " + " ".join(f"M{pos[i][0]} {pos[i][1]} C {pos[i][0]} {pos[i][1]+60}, {pos[i+2][0]} {pos[i+2][1]-60}, {pos[i+2][0]} {pos[i+2][1]}" for i in range(len(pos) - 2))
    surface = (f'<rect width="{w}" height="190" fill="{STONE}"/><g fill="{FOREST}"><rect x="90" y="96" width="14" height="94"/><circle cx="97" cy="82" r="48"/><circle cx="60" cy="112" r="30"/><circle cx="136" cy="108" r="32"/></g>'
               f'<g transform="translate(400 118)"><rect x="0" y="16" width="150" height="44" rx="7" fill="{INK}"/><rect x="104" y="0" width="58" height="60" rx="7" fill="{INK}"/>'
               f'<rect x="114" y="8" width="34" height="18" rx="3" fill="{STONE}"/><circle cx="34" cy="62" r="12" fill="{NIGHT}"/><circle cx="130" cy="62" r="12" fill="{NIGHT}"/></g>'
               f'<path d="M290 190 q30 -28 60 0z" fill="#c8c1b3"/>')
    h = pos[-1][1] + 110
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="Cutaway of an ant colony: eight assistants each working in its own chamber">'
            f'<rect width="{w}" height="{h}" fill="{NIGHT}"/>' + surface +
            f'<path d="{tun}" stroke="#173528" stroke-width="34" fill="none" stroke-linecap="round"/>' +
            "".join(chamber(n, x, y) for n, (x, y) in zip(NAMES[:8], pos)) + '</svg>\n')


if __name__ == "__main__":
    os.makedirs(os.path.join(BRAND, "icons"), exist_ok=True)
    for n in NAMES:
        svg = icon(n, 120, ground=STONE).replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" role="img" ', 1)
        open(os.path.join(BRAND, "icons", n.lower() + ".svg"), "w").write(svg + "\n")
    open(os.path.join(HERE, "colony-wide.svg"), "w").write(colony_wide())
    open(os.path.join(HERE, "colony-tall.svg"), "w").write(colony_tall())
    print("wrote", len(NAMES), "icons + colony-wide.svg + colony-tall.svg")
