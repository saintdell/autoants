# Business card

3.5 × 2 in with 0.125 in bleed. `card-front.pdf` and `card-back.pdf` are the print files. The `-proof.png` files show the trim line (solid) and the safe area (dashed); never send the proofs to the printer.

Regenerate with `uv run --with qrcode python3 brand/print/business-card/make_card.py` after editing `CARD` in the script.

**Before printing:**
1. Put the real phone number in `CARD["phone"]`. The front shows a red PHONE TBD until then.
2. Make sure autoants.com resolves (the Cloudflare import). The QR code points to `https://autoants.com/?ref=card#contact`, and `ref=card` shows which visits came from cards.
3. Scan the back proof with a phone.
4. Order one printed proof first: the forest and night greens shift in print.

**Stock:** 16 pt or heavier, matte or uncoated, so it takes a pen. 250 to start.

The title is "Founder", not "Attorney". The law license stays off AutoAnts print to keep the legal firewall clean; the site's "Attorney-owned" line carries the trust.
