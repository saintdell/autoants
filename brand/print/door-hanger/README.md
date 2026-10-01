# Door hanger

The branded door hanger: 4.25 × 11 in, 0.125 in bleed, standard 1.25 in hole. `door-hanger.pdf` is the print file (front and back). `door-hanger-proof.png` shows the trim (solid), the safe area (dashed) and the hole; never send the proof to the printer.

- **Front:** the wordmark, "Never miss another job.", the waving mascot, and a QR code plus autoants.com.
- **Back (kept light on purpose):** "Meet the crew" gives four assistants (Callback, Responder, Scheduler, Reviewer) one short line each; "How it works" is three one-line steps; then the contact details. The full story lives on autoants.com/who-we-help.html.

Regenerate with `uv run --with qrcode python3 brand/print/door-hanger/make_hanger.py` after editing `INFO` or the copy in the script.

**Before printing:**
1. Put the real phone number in `INFO["phone"]`; the back shows a red PHONE TBD until then.
2. Make sure autoants.com resolves and the lane@autoants.com mailbox exists.
3. Scan the proof's QR code with a phone. It goes to `autoants.com/?ref=hanger#contact`, and `ref=hanger` tells us which visits came from hangers.
4. Order one printed proof first: the night green shifts in print.

**Where they go:** business doors only. Never in mailboxes (federal law), never on poles (New Orleans CZO art. 24, $100–300 a day) or vehicles. Skip any door marked No soliciting.

The copy avoids "most popular" (no popularity claims until there are reference customers) and never mentions the law license.
