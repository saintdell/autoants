# AutoAnts email

**The mailbox:** lane@autoants.com on Google Workspace Business Starter. Setup sheet: `autoants-mailbox-setup.md` (DNS: SPF, DKIM, DMARC). Until it exists, the site footer and JSON-LD keep lane@blundellcore.com, so nothing bounces.

**Two kinds of mail, two signatures:**

| Mail | Signature | Why |
|---|---|---|
| Cold first touch and its one follow-up | The playbook's plain-text CAN-SPAM footer (`channel.email.footer`), added by the send queue | Plain text with no images and no links is what lands in the inbox from a new domain |
| Replies, clients, partners | `signature.html` (logo) or `signature.txt` | Branded, once a real conversation exists |

**Files:**
- `sig-logo.png`: the logo at 2x (522×112, transparent), referenced by URL from `signature.html`. It shows once autoants.com resolves.
- `signature.html`: open it, copy the white box, and paste it into Gmail's signature setting.
- `signature.txt`: the plain version.

**What's deliberately missing:** "attorney". AutoAnts stays separate from the law license.

**When the mailbox is live:**
- fill the phone in both signature files;
- set `channel.email.sender` in `tree-lead-engine/playbook.yaml`;
- switch the site's footer and JSON-LD email to lane@autoants.com.
