# Mascot loops

Five 4-second loops, built from the mascot's own drawing code, so the character never drifts off-model. Each one ends where it starts.

| Loop | Gesture | Pairs with |
|---|---|---|
| hello | waves twice | Meet the ants |
| ringing | phone buzzes, the ant answers, eyes go happy | Callback Ant |
| delivery | walks in place carrying the envelope | Responder Ant |
| thumbs-up | thumb pops up with a sparkle | Reviewer Ant |
| on-the-job | hard hat, calm idle: sway and blink | Your office, handled |

- **`video/<loop>-1080x1920.mp4`**: for Reels, Shorts and Stories. Each file is 12 s (the loop three times) and silent; add music in the app if you want it. The headline sits clear of the Reels top bar and the caption area at the bottom.
- **`svg/<loop>.svg`**: a self-animating SVG on a transparent background, about 4 KB, for the website. It holds still for visitors who turn off motion.

Rebuild with `uv run --with playwright python3 brand/mascot/anim/build_loops.py [loop ...]`. The script renders through your installed Chrome and encodes with ffmpeg.
