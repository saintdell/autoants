#!/usr/bin/env python3
"""Go-live gate for the autoants pay page.

Run from anywhere:  python3 pay/check_links.py
Exits 1 (and lists every problem) while the pay page could go live half-done:
  - any link in pay/links.json still contains REPLACE_
  - an offer link is not an https://buy.stripe.com/ Payment Link, or is a test-mode (test_) link
  - a Pay button on pay/index.html has no entry in links.json (or links.json has an offer no button uses)
  - the kickoff-call link is missing or not https
  - terms/index.html still carries the DRAFT banner (data-draft)
Exits 0 only when all of it is clean.
"""
import json
import re
import sys
from pathlib import Path

PAY = Path(__file__).resolve().parent
SITE = PAY.parent


def main() -> int:
    problems = []
    cfg = json.loads((PAY / "links.json").read_text())
    offers = cfg.get("offers", {})
    kickoff = cfg.get("kickoff_call", "")

    for key, url in offers.items():
        if "REPLACE_" in url:
            problems.append(f"offers.{key}: still a placeholder ({url})")
        elif not url.startswith("https://buy.stripe.com/"):
            problems.append(f"offers.{key}: not a Stripe Payment Link ({url})")
        elif url.startswith("https://buy.stripe.com/test_"):
            problems.append(f"offers.{key}: a TEST-mode link; make it in live mode ({url})")

    if not kickoff or "REPLACE_" in kickoff:
        problems.append(f"kickoff_call: still a placeholder ({kickoff or 'empty'})")
    elif not kickoff.startswith("https://"):
        problems.append(f"kickoff_call: not an https link ({kickoff})")

    page = (PAY / "index.html").read_text()
    used = set(re.findall(r'class="pay"[^>]*data-offer="([a-z_]+)"', page))
    for key in sorted(used - offers.keys()):
        problems.append(f"pay/index.html button '{key}' has no link in links.json")
    for key in sorted(offers.keys() - used):
        problems.append(f"links.json offer '{key}' has no Pay button on pay/index.html")

    if "data-draft" in (SITE / "terms" / "index.html").read_text():
        problems.append("terms/index.html still shows the DRAFT banner (agreement not approved)")

    if problems:
        print(f"NOT READY: {len(problems)} problem(s)")
        for p in problems:
            print("  -", p)
        return 1
    print(f"READY: {len(offers)} Payment Links set, kickoff link set, terms approved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
