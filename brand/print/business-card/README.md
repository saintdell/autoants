# Business card

3.5 × 2 in with 0.125 in bleed. `card-front.pdf` and `card-back.pdf` are the print files. The `-proof.png` files show the trim line (solid) and the safe area (dashed); never send the proofs to the printer.

Regenerate with `uv run --with qrcode python3 brand/print/business-card/make_card.py` after editing `CARD` in the script.

**Cleared to print** (2026-10-30). The card carries the autoants line, (504) 499-1194. Twilio approved the texting campaign on 2026-10-29 and Lane's missed-call test passed on 2026-10-30 (the call rang his cell, the auto-text arrived).

**Before printing:**
1. The phone is the Twilio line (set 2026-10-21). Re-check it still forwards to Lane's cell.
2. Make sure autoants.com resolves (the Cloudflare import). The QR code points to `https://autoants.com/?ref=card#contact`, and `ref=card` shows which visits came from cards.
3. Scan the back proof with a phone.
4. Order one printed proof first: the forest and night greens shift in print.

**Stock:** 16 pt or heavier, matte or uncoated, so it takes a pen. 250 to start.

The title is "Founder". Lane's law license never appears in AutoAnts copy unless it's material to the client (for example, a law firm).
