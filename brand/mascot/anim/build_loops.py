"""Animated mascot loops, drawn from the same geometry as ../mascot.py (rubber-hose body).

    uv run --with playwright python3 brand/mascot/anim/build_loops.py

Writes, per loop:
  svg/<loop>.svg               self-animating SVG (CSS keyframes), transparent, for the website
  video/<loop>-1080x1920.mp4   Reels / Shorts / Stories: night ground, headline, 12 s (the 4 s loop x3), silent

Every loop is exactly 4 s and ends where it starts, so platforms loop it seamlessly.
Motion stays small and calm: bob, sway, blink, one gesture. No new colors, no extra legs."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import mascot as M  # noqa: E402

LIGHT = dict(body=M.FOREST, boot=M.INK, ant=M.FOREST)
DARK = dict(body=M.FOREST_LIGHT, boot="#33453b", ant=M.STONE)
LOOP_S, FPS = 4, 30


def stroke(d, c, w=M.SW):
    return f'<path d="{d}" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'


def hand(x, y):
    return f'<circle cx="{x}" cy="{y}" r="10" fill="{M.MINT}"/>'


def legs(p):
    return (f'<g class="legL">{stroke("M93 208C90 226 82 232 84 244", p["body"])}<ellipse cx="77" cy="248" rx="19" ry="8.5" fill="{p["boot"]}"/></g>'
            f'<g class="legR">{stroke("M107 208C110 226 118 232 116 244", p["body"])}<ellipse cx="123" cy="248" rx="19" ry="8.5" fill="{p["boot"]}"/></g>')


def torso(p):
    return f'<ellipse cx="100" cy="184" rx="24" ry="30" fill="{p["body"]}"/><circle cx="100" cy="141" r="14" fill="{p["body"]}"/>'


def head(p, eyes, hat=False):
    """eyes: list of (class, kind, look). More than one = cross-fade between them."""
    a = p["ant"]
    out = (f'<g class="head"><g class="ants"><path d="M88 40 74 8M112 40l14-32" stroke="{a}" stroke-width="6" stroke-linecap="round"/>'
           f'<circle cx="74" cy="7" r="6.5" fill="{a}"/><circle cx="126" cy="7" r="6.5" fill="{a}"/></g>'
           f'<circle cx="100" cy="82" r="46" fill="{M.MINT}"/>')
    out += "".join(f'<g class="{cls}">{M.eyes(kind, look)}</g>' for cls, kind, look in eyes)
    if hat:
        out += M.HARDHAT
    return out + "</g>"


DOWN_L = lambda p: stroke("M90 142C70 150 64 176 58 194", p["body"]) + hand(56, 198)
HIP_L = lambda p: stroke("M90 146C58 150 56 178 76 176", p["body"]) + hand(78, 176)
HIP_R = lambda p: stroke("M110 146C142 150 144 178 124 176", p["body"]) + hand(122, 176)

# shared motion: transform-box view-box makes every origin a point in the drawing
BASE = """
.legL,.legR,.upper,.head,.ants,.blink,.armR,.phone,.spark,.speed{transform-box:view-box}
.upper{animation:bob 2s ease-in-out infinite}
.head{transform-origin:100px 128px;animation:tilt 4s ease-in-out infinite}
.ants{transform-origin:100px 40px;animation:sway 2s ease-in-out infinite;animation-delay:-.35s}
.blink{transform-origin:100px 78px;animation:blink 4s linear infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(3px)}}
@keyframes tilt{0%,100%{transform:rotate(-2deg)}50%{transform:rotate(2deg)}}
@keyframes sway{0%,100%{transform:rotate(-5deg)}50%{transform:rotate(5deg)}}
@keyframes blink{0%,64%,70%,100%{transform:scaleY(1)}67%{transform:scaleY(.1)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def hello(p):
    body = legs(p) + '<g class="upper">' + torso(p) + DOWN_L(p) + head(p, [("happy", "happy", 0)])
    body += f'<g class="armR">{stroke("M110 142C136 134 150 112 152 84", p["body"])}{hand(153, 78)}</g></g>'
    css = (".armR{transform-origin:110px 142px;animation:wave 4s ease-in-out infinite}"
           "@keyframes wave{0%,56%,100%{transform:rotate(0)}10%,34%{transform:rotate(16deg)}22%,46%{transform:rotate(-8deg)}}")
    return body, css


def ringing(p):
    rings = (f'<g class="rings" stroke="{M.MINT}" stroke-width="4.5" stroke-linecap="round" fill="none">'
             f'<path d="M166 74q8 13 0 26"/><path d="M175 67q13 20 0 40"/></g>')
    body = (legs(p) + '<g class="upper">' + torso(p) + HIP_L(p)
            + head(p, [("eyesA blink", "dot", -3), ("eyesB", "happy", -3)])
            + f'<g class="phone">{M.PHONE(138, 70)}</g>{rings}'
            + stroke("M110 142C140 140 152 122 146 106", p["body"]) + hand(146, 102) + "</g>")
    css = (".phone{transform-origin:148px 87px;animation:ring 4s linear infinite}"
           ".rings{animation:rings 4s linear infinite}.eyesA{animation:eyesA 4s linear infinite,blink 4s linear infinite}"
           ".eyesB{opacity:0;animation:eyesB 4s linear infinite}"
           "@keyframes ring{0%,15%,20%,35%,100%{transform:rotate(0)}3%,9%,23%,29%{transform:rotate(9deg)}6%,12%,26%,32%{transform:rotate(-9deg)}}"
           "@keyframes rings{0%,16%,20%,36%,100%{opacity:0}6%,26%{opacity:1}}"
           "@keyframes eyesA{0%,40%,94%,100%{opacity:1}43%,91%{opacity:0}}"
           "@keyframes eyesB{0%,40%,94%,100%{opacity:0}43%,91%{opacity:1}}")
    return body, css


def delivery(p):
    speed = "".join(f'<g class="speed s{i}"><path d="M{44 - 6*i} {150 + 24*i}h-22" stroke="{M.MINT}" stroke-width="5" stroke-linecap="round"/></g>'
                    for i in range(3))
    body = (speed + legs(p) + '<g class="upper walk">' + torso(p) + head(p, [("blink", "dot", 3)])
            + stroke("M90 144C92 168 104 172 115 168", p["body"]) + stroke("M110 144C142 140 166 150 178 159", p["body"])
            + M.ENVELOPE + hand(115, 168) + hand(178, 159) + "</g>")
    css = (".legL{transform-origin:93px 208px;animation:stepA 1s ease-in-out infinite}"
           ".legR{transform-origin:107px 208px;animation:stepB 1s ease-in-out infinite}"
           ".upper.walk{animation:bob2 1s ease-in-out infinite}"
           ".speed{animation:speed 1s linear infinite;opacity:0}.s1{animation-delay:-.33s}.s2{animation-delay:-.66s}"
           "@keyframes stepA{0%,100%{transform:rotate(12deg)}50%{transform:rotate(-12deg)}}"
           "@keyframes stepB{0%,100%{transform:rotate(-12deg)}50%{transform:rotate(12deg)}}"
           "@keyframes bob2{0%,50%,100%{transform:translateY(0)}25%,75%{transform:translateY(-4px)}}"
           "@keyframes speed{0%{transform:translateX(8px);opacity:0}30%{opacity:.9}100%{transform:translateX(-18px);opacity:0}}")
    return body, css


def thumbs(p):
    spark = f'<g class="spark"><path d="M190 98l4 10 10 4-10 4-4 10-4-10-10-4 10-4z" fill="{M.MINT}"/></g>'
    body = (legs(p) + '<g class="upper">' + torso(p) + DOWN_L(p) + head(p, [("happy", "happy", 0)])
            + f'<g class="armR">{stroke("M110 142C134 138 152 152 170 146", p["body"])}{hand(174, 146)}'
            + f'<rect x="169" y="121" width="10" height="23" rx="5" fill="{M.MINT}"/></g>{spark}</g>')
    css = (".armR{transform-origin:110px 142px;animation:pop 4s ease-in-out infinite}"
           ".spark{transform-origin:190px 112px;animation:spark 4s ease-out infinite}"
           "@keyframes pop{0%,8%,92%,100%{transform:rotate(70deg)}20%{transform:rotate(-10deg)}26%{transform:rotate(4deg)}30%,80%{transform:rotate(0)}}"
           "@keyframes spark{0%,26%,62%,100%{transform:scale(0) rotate(0);opacity:0}36%{transform:scale(1.15) rotate(20deg);opacity:1}50%{transform:scale(.9) rotate(40deg);opacity:1}}")
    return body, css


def onthejob(p):
    body = legs(p) + '<g class="upper">' + torso(p) + DOWN_L(p) + HIP_R(p) + head(p, [("blink", "dot", 0)], hat=True) + "</g>"
    return body, ""


LOOPS = {  # name: (draw, eyebrow, headline) — copy matches posts.json
    "hello": (hello, "autoants", "Meet the ants."),
    "ringing": (ringing, "The Callback", "Missed calls are jobs walking away."),
    "delivery": (delivery, "The Responder", "The crew that answers first wins."),
    "thumbs-up": (thumbs, "The Reviewer", "Every customer gets the ask."),
    "on-the-job": (onthejob, "Your office, handled", "They work while you're on the job."),
}


def svg(name, p, width=None):
    draw = LOOPS[name][0]
    body, css = draw(p)
    size = f' width="{width}" height="{round(width*260/210)}"' if width else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 260"{size} role="img" aria-label="autoants mascot">'
            f'<style>{BASE}{css}</style>{body}</svg>')


def reel_html(name):
    _, eyebrow, line = LOOPS[name]
    glow = f"radial-gradient(70% 50% at 85% 0%,rgba(61,220,174,.16),transparent 60%),{M.NIGHT}"
    return (f'<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@800'
            f'&family=JetBrains+Mono:wght@700&display=swap"><body style="margin:0">'
            f'<div style="position:relative;width:1080px;height:1920px;overflow:hidden;background:{glow}">'
            f'<div style="position:absolute;left:84px;right:84px;top:290px;display:flex;flex-direction:column;gap:28px">'
            f'<div style="font:700 30px JetBrains Mono,monospace;letter-spacing:.16em;text-transform:uppercase;color:{M.MINT}">{eyebrow}</div>'
            f'<div style="font:800 96px/1.03 Onest,sans-serif;letter-spacing:-.03em;color:{M.STONE};text-wrap:balance">{line}</div></div>'
            f'<div style="position:absolute;left:50%;transform:translateX(-50%);top:720px">{svg(name, DARK, 640)}</div>'
            f'</div></body>')


def render_reels(names):
    from playwright.sync_api import sync_playwright
    os.makedirs(os.path.join(HERE, "video"), exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for name in names:
            pg.set_content(reel_html(name), wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            one = os.path.join(HERE, "video", f"_{name}.mp4")
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-",
                                   "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow", one], stdin=subprocess.PIPE)
            for i in range(LOOP_S * FPS):
                pg.evaluate("t => document.getAnimations().forEach(a => { a.pause(); a.currentTime = t })", i * 1000 / FPS)
                ff.stdin.write(pg.screenshot(type="png"))
            ff.stdin.close(); ff.wait()
            out = os.path.join(HERE, "video", f"{name}-1080x1920.mp4")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "2", "-i", one, "-c", "copy", "-movflags", "+faststart", out], check=True)
            os.remove(one)
            print(os.path.relpath(out, HERE))
        b.close()


if __name__ == "__main__":
    names = sys.argv[1:] or list(LOOPS)
    os.makedirs(os.path.join(HERE, "svg"), exist_ok=True)
    for n in names:
        open(os.path.join(HERE, "svg", f"{n}.svg"), "w").write(svg(n, LIGHT))
    render_reels(names)
