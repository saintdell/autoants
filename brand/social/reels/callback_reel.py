"""'What happens when you miss a call': a 17-second Reel showing The Callback at work.

    uv run --with playwright python3 brand/social/reels/callback_reel.py

1080x1920, 30 fps, silent (add a sound in the app). Story: the phone rings while you're with a
customer -> missed call -> The Callback texts back in seconds -> they reply and book -> "The customer
stays yours." The business is "Your Business", so any owner pictures their own shop."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "out")
FPS, DUR = 30, 17.0
ANIM = os.path.join(BRAND, "mascot", "anim", "svg")
WORD = open(os.path.join(BRAND, "autoants-logo-reverse.svg")).read().strip()
ring = open(os.path.join(ANIM, "ringing-dark.svg")).read()
thumbs = open(os.path.join(ANIM, "thumbs-up-dark.svg")).read()

BIZ, NUM = "Your Business", "(985) 555-0142"
CAPS = [(0.2, 3.0, "You're with a customer. The phone rings."),
        (3.0, 5.6, "You can't pick up. Most callers won't leave a voicemail."),
        (5.6, 8.6, "The Callback texts them back in seconds."),
        (8.6, 12.7, "They answer. You get the job."),
        (12.7, 17.2, "The customer stays yours.")]
BUBBLES = [("out", 6.5, f"Hi, this is {BIZ}! Sorry we missed your call. What can we help with?"),
           ("in", 9.0, "Do you have anything open this week?"),
           ("out", 10.4, "We can fit you in Thursday. 9 or 2?"),
           ("in", 11.5, "9 works 👍")]
TYPING = [(5.9, 6.5), (9.8, 10.4)]

caps = "".join(f'<div class="cap" data-in="{a}" data-out="{b}">{t}</div>' for a, b, t in CAPS)
bubbles = "".join(f'<div class="b {k}" data-in="{t}">{x}</div>' for k, t, x in BUBBLES)
typing = "".join(f'<div class="b out typing" data-in="{a}" data-out="{b}"><i></i><i></i><i></i></div>' for a, b in TYPING)

HTML = f'''<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@500;700;800&family=JetBrains+Mono:wght@700&display=swap">
<style>
html,body{{margin:0;background:#0b1712}}
#stage{{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Onest,sans-serif;color:#ebe8e2;
  background:radial-gradient(70% 45% at 85% 5%,rgba(61,220,174,.16),transparent 60%),#0b1712}}
.cap{{position:absolute;left:84px;right:84px;top:300px;font:800 76px/1.04 Onest;letter-spacing:-.03em;text-wrap:balance;opacity:0}}
#phone{{position:absolute;left:150px;top:690px;width:520px;height:900px;border-radius:66px;background:#0f2a1d;
  box-shadow:0 0 0 10px #1a2f25,0 30px 80px rgba(0,0,0,.5);overflow:hidden;opacity:0}}
.scr{{position:absolute;inset:0;opacity:0;display:flex;flex-direction:column;align-items:center}}
#s-call .who,#s-missed .who{{margin-top:170px;font:700 26px Onest;color:#a3b0a8}}
#s-call .num,#s-missed .num{{margin-top:14px;font:800 46px Onest}}
#s-call .btns{{position:absolute;bottom:120px;left:0;right:0;display:flex;justify-content:space-around}}
.btn{{width:116px;height:116px;border-radius:50%;display:grid;place-items:center;font:800 22px Onest}}
.dec{{background:#c2453b}} .acc{{background:#3ddcae;color:#062a1d}}
#pulse{{position:absolute;left:50%;top:420px;width:150px;height:150px;margin-left:-75px;border-radius:50%;border:6px solid #3ddcae}}
#s-missed .badge{{margin-top:60px;font:800 30px Onest;color:#e8857c}}
#s-msgs{{align-items:stretch;padding:0 26px}}
#s-msgs .hd{{margin:70px 0 26px;text-align:center;font:700 26px Onest;color:#a3b0a8}}
.b{{max-width:78%;padding:18px 22px;border-radius:30px;font:500 27px/1.3 Onest;margin:9px 0;opacity:0}}
.b.out{{align-self:flex-end;background:#3ddcae;color:#062a1d;border-bottom-right-radius:8px}}
.b.in{{align-self:flex-start;background:#1f3a2e;color:#ebe8e2;border-bottom-left-radius:8px}}
.typing{{display:flex;gap:8px;padding:22px 24px;position:absolute;right:26px}}
.typing i{{width:12px;height:12px;border-radius:50%;background:#062a1d;opacity:.55}}
#tag{{position:absolute;left:150px;width:520px;top:1622px;text-align:center;font:700 20px JetBrains Mono;letter-spacing:.12em;
  text-transform:uppercase;color:#6f7d75;opacity:0}}
.ant{{position:absolute;opacity:0}} .ant svg{{width:100%;height:auto;display:block}}
#ant-ring{{left:680px;top:1040px;width:330px}}
#end{{position:absolute;inset:0;opacity:0}}
#end .a{{position:absolute;left:50%;top:640px;width:440px;margin-left:-220px}}
#end .w{{position:absolute;left:0;right:0;top:1250px;display:flex;justify-content:center}}
#end .w svg{{height:96px;width:auto}}
#end .l{{position:absolute;left:84px;right:84px;top:1385px;text-align:center;font:700 40px Onest;color:#c9d3cc}}
#end .u{{position:absolute;left:84px;right:84px;top:1452px;text-align:center;font:800 40px Onest;color:#3ddcae}}
</style>
<div id="stage">
  {caps}
  <div id="phone">
    <div class="scr" id="s-call"><div id="pulse"></div><div class="who">Incoming call</div><div class="num">{NUM}</div>
      <div class="btns"><div class="btn dec">✕</div><div class="btn acc">✓</div></div></div>
    <div class="scr" id="s-missed"><div class="who">Missed call</div><div class="num">{NUM}</div><div class="badge">No voicemail</div></div>
    <div class="scr" id="s-msgs"><div class="hd">{NUM}</div>{bubbles}{typing}</div>
  </div>
  <div class="ant" id="ant-ring">{ring}</div>
  <div id="end"><div class="a">{thumbs}</div><div class="w">{WORD}</div>
    <div class="l">Automated assistants for local businesses.</div><div class="u">autoants.com · free website preview</div></div>
</div>
<script>
const F = .28, clamp = x => Math.max(0, Math.min(1, x));
const win = (t, a, b) => clamp((t - a) / F) * clamp((b - t) / F);
function show(el, a, t, b = 99, rise = 24) {{ const k = win(t, a, b); el.style.opacity = k; el.style.transform = `translateY(${{(1 - k) * rise}}px)`; }}
window.seek = (t) => {{
  document.querySelectorAll('.cap').forEach(c => show(c, +c.dataset.in, t, +c.dataset.out));
  show(phone, 0.3, t, 12.9, 40);
  document.getElementById('s-call').style.opacity = win(t, 0.3, 3.0);
  document.getElementById('s-missed').style.opacity = win(t, 3.0, 5.7);
  document.getElementById('s-msgs').style.opacity = win(t, 5.6, 99);
  const ph = (t % 1.0); pulse.style.transform = `scale(${{1 + ph * 0.9}})`; pulse.style.opacity = t < 3 ? (1 - ph) : 0;
  document.querySelectorAll('.b:not(.typing)').forEach(b => {{ const k = clamp((t - b.dataset.in) / .22);
    b.style.opacity = k; b.style.transform = `scale(${{.9 + .1 * k}})`; b.style.transformOrigin = b.classList.contains('out') ? 'right bottom' : 'left bottom'; }});
  document.querySelectorAll('.typing').forEach(b => {{ const on = t >= b.dataset.in && t < b.dataset.out; b.style.opacity = on ? 1 : 0;
    b.style.top = (t < 8 ? 190 : 470) + 'px';
    b.querySelectorAll('i').forEach((d, i) => d.style.opacity = on ? .3 + .7 * Math.max(0, Math.sin((t * 6 - i) )) : 0); }});
  show(document.getElementById('ant-ring'), 0.5, t, 8.7, 30);
  show(document.getElementById('end'), 12.9, t, 99, 30);
  document.getAnimations().forEach(a => {{ a.pause(); a.currentTime = t * 1000; }});
}};
</script>'''


def render():
    from playwright.sync_api import sync_playwright
    os.makedirs(OUT, exist_ok=True)
    dest = os.path.join(OUT, "the-callback-reel-1080x1920.mp4")
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.set_content(HTML, wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-",
                               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow", "-movflags", "+faststart", dest],
                              stdin=subprocess.PIPE)
        for i in range(int(DUR * FPS)):
            pg.evaluate(f"seek({i / FPS})")
            ff.stdin.write(pg.locator("#stage").screenshot(type="png"))
        ff.stdin.close(); ff.wait()
        b.close()
    return dest


if __name__ == "__main__":
    print(render())
