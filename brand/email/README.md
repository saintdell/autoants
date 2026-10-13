# AutoAnts email

**The mailbox:** lane@autoants.com on Google Workspace Business Starter. Setup sheet: `autoants-mailbox-setup.md` (DNS: SPF, DKIM, DMARC). Until it exists, the site footer and JSON-LD keep lane@blundellcore.com, so nothing bounces.

**Sending inboxes for outreach** (approved 2026-10-11): lane@getautoants.com, a second named getautoants.com inbox [FILL: address], and lane@tryautoants.com (autoantshq.com was dropped 2026-10-12). All of them, plus lane@autoants.com, get the same profile photo.

## Which file goes where

| Where | File | Notes |
|---|---|---|
| Google profile photo of every inbox above | `avatar-512.png` (or `avatar-1024.png`) | Forest ground, stone antennae: the ant that reads best at 40 px. `avatar-stone-*.png` is the light variant, kept as a spare. |
| Signature on replies, clients, partners | `signature-anim.html` (uses `ant-anim.gif`) | The ant springs its antennae and blinks, then holds still for 2.8 s. |
| The same, without the animation | `signature.html` (uses `sig-logo.png`) or `signature.txt` | The October 1 wordmark signature, unchanged. |
| Branded emails after first contact (booking, onboarding, proposal, billing, monthly report, newsletter) | `~/tle-main/brand/email-templates/` (header uses `newsletter-logo.png`) | Rendered with `render.py`; setup steps for Kit, Stripe, Gmail and Cal.com are in its README. |
| Cold first touch and its one follow-up | **No signature file, no images.** The playbook's plain-text CAN-SPAM footer (`channel.email.footer`), added by the send queue | Plain text with no images and no links is what lands in the inbox from a new domain. A GIF in a cold email is a spam signal. The profile photo is fine there: it is not in the message. |

**Files:**
- `avatar-512.png`, `avatar-1024.png`: the ant on a forest #0f5132 square. It fills 80% of the circle Gmail crops to, so nothing touches the edge.
- `avatar-stone-512.png`, `avatar-stone-1024.png`: the same on stone #ebe8e2, with forest antennae.
- `ant-anim.gif`: 128 px, shown at 64 CSS px, about 18 KB, loops forever. Cycle: still 0.6 s, the sting's antenna spring (0.5 s) and blink (0.18 s), then still 2.2 s. The first and last frames are the approved static ant, so Outlook, which shows only frame 1, gets the ant at rest.
- `ant-anim@1x.gif`: the same at 64 px, about 12 KB, for places that do not scale images down.
- `ant-still.png`: the resting ant at 128 px on forest, for anywhere motion is unwanted.
- `sig-logo.png`: the wordmark at 2x (522×112, transparent), used by `signature.html`.
- `signature-anim.html` / `signature.html`: open the page, copy what is inside the white box, and paste it into Gmail → Settings → See all settings → Signature. Fill in the phone first. The images load from `https://autoants.com/brand/email/`, so they show once the site is live.
- `contact-sheet-email.png`: shows each avatar candidate at 40, 64 and 128 px on Gmail's light and dark lists, and the GIF frames on white and on Gmail dark #202124.
- `build_email_assets.py`: rebuilds all of the above (usage at the top of the file).

**Why the GIF has a forest ground and not a transparent one:** GIF transparency is on or off per pixel, so a transparent ant carries a light halo onto dark-mode mail. Its forest antennae also disappear on #202124. A solid forest square avoids both problems and matches the inbox photo. The signature rounds it to a circle (`border-radius`) in Gmail and Apple Mail. Outlook ignores the rounding and shows a forest square, which is fine.

**Why the inbox icon itself can't animate:**
- **Gmail** shows the sender's Google account profile photo, and it is always a still. If you upload an animated GIF, Gmail keeps one frame.
- **Outlook and Apple Mail** show still images or initials.
- **BIMI** (the brand logo in the inbox) only accepts a static SVG Tiny PS file.

So the motion lives in the message body, which is the signature. The round icon is the still `avatar-512.png`.

## Set the profile photo for each inbox

Do this once per inbox: lane@getautoants.com, the second getautoants.com inbox, lane@tryautoants.com and lane@autoants.com.

1. Sign in to the inbox's Google account. Go to myaccount.google.com, then **Personal info**, then **Profile picture**. Upload `avatar-512.png`. If Google offers a crop, keep the whole square: the circle already has the margin built in.
2. If the photo can't be changed, the Workspace admin has locked profile editing. Use one of these:
   - **Fix the setting.** In the Admin console (admin.google.com), go to **Directory → Users**. Click **More options** at the top right and choose **Allow users to edit profile**. Tick **Photo** and save.
   - **Set it as admin.** In the Admin console, go to **Directory → Users**, click the user's name, click the avatar, then **Change photo**, and upload the file.
3. Each domain (getautoants.com, tryautoants.com, autoants.com) is its own Workspace or secondary domain, so repeat the steps in whichever Admin console owns that inbox.
4. Check it by sending from the inbox to an outside Gmail address. Google caches photos, so a new one can take up to a day to show to other people.

Source for the Admin console steps: Google Workspace Admin Help, ["Add or change a user's profile photo"](https://knowledge.workspace.google.com/admin/users/add-or-change-a-users-profile-photo) and ["Allow Directory users to change their profile and photo"](https://knowledge.workspace.google.com/admin/users/allow-directory-users-to-change-their-profile-and-photo). Checked 2026-10-11.

## BIMI: possible later, not now

BIMI puts the brand logo in the inbox avatar slot, in Gmail, Yahoo and Apple Mail. It needs three things:
- **DMARC at enforcement.** `p=quarantine` or `p=reject` on the sending domain. Monitoring mode (`p=none`) doesn't count.
- **A logo in SVG Tiny PS.** It must be static, so the forest-square ant would be redrawn in that format.
- **A paid mark certificate:**
  - **VMC (Verified Mark Certificate).** Needs a *registered* trademark, and the USPTO filing for autoants is still open. It is the only certificate that gets Gmail's blue checkmark. Price: about $750 to $1,750 a year. List price is about $1,752 a year. Real one-year quotes in May and June 2026 ran from $780 to $1,305.
  - **CMC (Common Mark Certificate).** No trademark needed, but the logo must have been in public use for 12 months. The autoants ant has been in use since 2026-10-01, so the earliest is about October 2027. Price: about $650 to $1,400 a year (list about $1,416). DigiCert's CMC sells from $949 a year through resellers.

Plan for roughly $1,000+ a year per certificate. Check whether one certificate can cover several sending domains before you buy.

The trigger to revisit: DMARC has been at quarantine or reject, with clean reports, on the domain that sends client mail, **and** either the trademark is registered (VMC) or it is past 2027-10 (CMC).

Sources (prices checked 2026-10-11):
- [DMARCTrust, "VMC vs CMC for BIMI: 2026 prices and requirements"](https://www.dmarctrust.com/blog/cmc-vmc-bimi-new-offering)
- [Tallyfy, "What a verified mark certificate actually costs in 2026"](https://tallyfy.com/engineering-vmc-certificate-pricing/) (vendor quotes from May and June 2026)
- [SSL Dragon, DigiCert mark certificates](https://www.ssldragon.com/security/digicert-mark-certificates/)

## Notes

**What's deliberately missing:** "attorney". AutoAnts stays separate from the law license.

**When the mailbox is live:**
- fill the phone in the signature files;
- set `channel.email.sender` in `tree-lead-engine/playbook.yaml`;
- switch the site's footer and JSON-LD email to lane@autoants.com.
