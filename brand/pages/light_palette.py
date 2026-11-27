#!/usr/bin/env python3
"""Move a page (or a generator's CSS string) from the old dark palette to the site's light one.

Lane, 2026-09-29: "I don't like the dark sections"; 2026-11-27: "The services page is still black."
The homepage's tokens are the target (cream #f7f5f0, white cards, forest #0f5132 accent, dark-green ink).
Only the default :root block and a few known dark-on-dark literals change; a prefers-color-scheme dark block
is left alone. Same token NAMES, light VALUES, so every rule that reads a token follows.

    python3 brand/pages/light_palette.py <file> [<file> ...]      # rewrite in place
    python3 brand/pages/light_palette.py --check <file> ...        # exit 1 if any file is still dark
"""
import re, sys

TOKENS = {  # token -> light value (dark values vary slightly page to page, so match by name)
    "bg": "#f7f5f0", "bg2": "#ebe8e2", "surface": "#ffffff", "surface2": "#efece6", "surface-2": "#efece6",
    "ink": "#0f2a1d", "muted": "#4b5a52", "faint": "#56655d",
    "mint": "#0f5132", "mint-ink": "#ffffff", "amber": "#0f5132", "amber-deep": "#0b3d26", "amber-ink": "#ffffff",
    "ok": "#2f7a3a", "line": "rgba(15,42,29,.12)",
}
LITERALS = [  # dark-theme literals outside the token block
    (r"rgba\(\s*11\s*,\s*23\s*,\s*18\s*,", "rgba(247,245,240,"),      # translucent dark nav/backdrops
    (r"rgba\(\s*244\s*,\s*241\s*,\s*232\s*,", "rgba(15,42,29,"),      # light-on-dark hairlines and overlays
    (r'(<meta name="theme-color" content=")#0b1712', r"\1#f7f5f0"),
    (r"color-scheme:\s*dark", "color-scheme:light"),
    (r"autoants-logo-reverse\.svg", "autoants-logo.svg"),           # the white logo vanishes on cream
]
ROOT = re.compile(r"(:root\s*\{\{?)(.*?)(\}\}?)", re.S)

def is_dark(s: str) -> bool:
    m = re.search(r"--bg:\s*(#[0-9a-fA-F]{6})", s)
    return bool(m and m.group(1).lower() == "#0b1712")

def convert(s: str) -> str:
    if not is_dark(s):
        return s
    m = ROOT.search(s)  # the first :root block is the default theme
    body = m.group(2)
    for name, val in TOKENS.items():
        body = re.sub(rf"(--{re.escape(name)}:\s*)[^;}}]+", lambda x: x.group(1) + val, body)
    body = body.replace("color-scheme:dark", "color-scheme:light")
    s = s[: m.start(2)] + body + s[m.end(2):]
    for pat, rep in LITERALS:
        s = re.sub(pat, rep, s)
    return logo_ink(s)

LOGO_SVG = re.compile(r'<svg[^>]*aria-label="autoants"[^>]*>.*?</svg>', re.S | re.I)

def logo_ink(s: str) -> str:
    """An inline logo drawn for a dark ground has cream letters; the light ground needs the forest ones."""
    return LOGO_SVG.sub(lambda m: m.group(0).replace('fill="#ebe8e2"', 'fill="#0f5132"'), s)

if __name__ == "__main__":
    args = sys.argv[1:]
    check = args and args[0] == "--check"
    files = args[1:] if check else args
    bad = 0
    for f in files:
        s = open(f, encoding="utf-8").read()
        if check:
            if is_dark(s): print("still dark:", f); bad += 1
            continue
        t = convert(s)
        if t != s:
            open(f, "w", encoding="utf-8").write(t)
    sys.exit(1 if bad else 0)
