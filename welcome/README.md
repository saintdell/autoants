# /welcome/ — the last step of a new client's signup

Internal notes. Written 2026-11-13. The page is `noindex`, has no analytics or tracking pixel, and isn't in the sitemap.

The flow: the client signs the agreement (DocuSeal) → pays through a Stripe Payment Link → Stripe's
"after payment" setting redirects them here. The page says "You're in.", shows Signed ✓ · Paid ✓ · Next: your setup call,
lets them ask for a setup call, and lists what the first two weeks look like and what we need from them.

## Stripe redirect URLs

In Stripe: Payment Links → the link → **After payment** → "Don't show confirmation page" → **Redirect customers to your
website** → paste the URL for that link's plan:

| Payment link for | Redirect URL |
|---|---|
| Get found | `https://autoants.com/welcome/?plan=get-found` |
| Catch missed calls | `https://autoants.com/welcome/?plan=calls` |
| Get found and catch missed calls | `https://autoants.com/welcome/?plan=both` |
| New website | `https://autoants.com/welcome/?plan=website` |
| Anything else (Try one, the assessment, custom links) | `https://autoants.com/welcome/` |

No `?plan=` (or a value the page doesn't know) shows the general version: every step, each tagged with the plan it's for.

What each plan shows:
- **get-found:** Google profile manager, verification codes, facts, photos, work you want more of, where leads go.
- **calls:** facts, how calls should go, phone setup and call forwarding together, texting registration details, where leads go. No Google profile or photos.
- **both:** everything in get-found and calls.
- **website:** facts, photos, work you want more of, the domain, where leads go. No Google profile manager step or verification codes.
- Every plan: the setup call, the go-live date in writing, replies within two business days, "never send passwords".

To change what a plan shows, edit the `data-plans="..."` attribute on that list item in `index.html` (space-separated
plan values; no attribute = every plan). The plan names live in `PLANS` in the script.

## The setup-call booking (`BOOK_URL`)

`BOOK_URL` near the top of the script in `index.html` is empty, so the page shows a short form: name, business, best
phone, best email, time windows (weekday morning, weekday afternoon, Saturday morning) and an optional note.

Once there's a booking link (Cal.com, Calendly, a Google Calendar appointment page):
1. Set `var BOOK_URL = "https://...";` in `welcome/index.html`.
2. Push. The page then shows a "Pick a time" button that opens the link in a new tab, with "None of the times work?"
   underneath, which opens the same form.

Note: `pay/links.json` → `kickoff_call` (used by the older `pay/thanks.html`) already holds a Google Calendar appointment
link. If that is the setup-call calendar, use the same URL here.

## Where the form goes

It posts JSON to the home page's lead worker, `https://autoants-leads.saintdell.workers.dev/lead`
(`tle-main/workers/autoants-leads/index.js`). No worker change was needed:
- `source: "welcome"`, `page: "welcome"`, `interest: "Setup call (Get found)"` (or the plan's name), and `msg` carries
  the plan, the ticked time windows and the note. Lane's Telegram ping reads "Wants: Setup call (...)" and
  "Found us via: welcome".
- `sms: "no"` always: there are no consent boxes on this page, and nothing about marketing texts.
- The hidden `website` field is the honeypot. Name + business + a phone (7+ digits) or an email are required.
- The worker only accepts posts from `https://autoants.com` and `https://www.autoants.com`. A preview served anywhere
  else shows the failure message. On failure (refused, network, 15-second timeout) the page keeps what was typed and says
  "Text Lane at (504) 499-1194".
- Saved leads: `npx wrangler kv key list --binding LEADS --prefix lead: --remote`, then look for `"source":"welcome"`.

## `client_reference_id`

Adding `?client_reference_id=<deal-slug>` to a Stripe Payment Link URL tags the payment (it shows on the Checkout
Session and in the `checkout.session.completed` webhook), so Lane can match a payment to a deal. Stripe does **not** pass
it to the redirect URL, so this page never sees it and can't tell which client arrived. That's deliberate: the page is
public, so it must never show a client's name or details from the URL. The client types their business name in the form.

## `MANAGER_EMAIL`

The address clients add as a manager on their Google Business Profile. It is `lane@autoants.com` for now; Lane still
decides between `lane@` and `clients@`. Change the one constant in the script; the page fills it in everywhere.

## Testing

The end-to-end test (worker under `wrangler dev --local` with `--var ALLOWED_ORIGINS:http://127.0.0.1:<port>`, no
secrets, so no Telegram message can go out; KV simulated on disk; headless Chromium at 390 px) checked: an empty
submit sends nothing; a refused origin and a network failure both show the failure message and keep every typed value;
a real submit gets `{"ok":true}`, shows the thanks, and stores exactly one `lead:` record with source `welcome`; the
honeypot stores nothing; no horizontal scroll at 390 or 1440 px for every plan value.

## Copy rules

No timing promises ("we tell you the go-live date in writing" is the line), no guarantees, no "never miss", no prices,
no "#1"/"best"/"attorney", lowercase "autoants", and no client names anywhere in this folder (the repo is public).
