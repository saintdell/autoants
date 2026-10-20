// autoants mail-tracking redirect: https://autoants.com/r/<code> (products/mail-tracking in tle-main).
//
// A QR on a mailed card points here. The Worker logs the scan and sends the visitor on to the campaign's landing page
// with ?ref=<code>, so the site's form records the code as the lead's source.
//
// What a scan log row holds, and nothing else: the code, the time, and a coarse device type
// (mobile | tablet | desktop | bot | other). No IP address, no user agent, no location, no cookie. The row is one
// KV key, scan:<code>:<ISO time>:<8 random hex>, with metadata {d: device}, kept 400 days. The Mac reads them with
// `wrangler kv key list --prefix scan:` (products/mail-tracking/track.py scans pull).
//
// Where a code goes: KV code:<code> = {"target": "https://..."} (written by Lane with `track.py kv <campaign>`).
// An unknown or malformed code still lands on the home page, so a card never dead-ends.
//
// Bindings (wrangler.toml): MAILTRACK (KV). Vars: FALLBACK (default https://autoants.com/).

export const CODE = /^mt-[23456789abcdefghjkmnpqrstuvwxyz]{6}$/;
const TTL = 400 * 24 * 3600;

export function device(ua) {
  const s = String(ua || "");
  if (!s) return "other";
  if (/bot|crawl|spider|preview|slurp|facebookexternalhit|whatsapp|slack|discord|telegram|curl|wget|python|headless/i.test(s)) return "bot";
  if (/ipad|tablet|kindle|silk|(android(?!.*mobile))/i.test(s)) return "tablet";
  if (/mobi|iphone|ipod|android|phone/i.test(s)) return "mobile";
  if (/windows|macintosh|x11|linux|cros/i.test(s)) return "desktop";
  return "other";
}

export function withRef(target, code) {
  const u = new URL(target);
  u.searchParams.set("ref", code);
  return u.toString();
}

function go(location) {
  return new Response(null, {
    status: 302,
    headers: { Location: location, "Cache-Control": "no-store", "Referrer-Policy": "no-referrer",
               "X-Robots-Tag": "noindex" },
  });
}

async function targetFor(env, code) {
  try {
    const raw = await env.MAILTRACK.get(`code:${code}`);
    const t = raw ? JSON.parse(raw).target : "";
    if (t && new URL(t).protocol === "https:") return t;
  } catch { /* fall through to the home page */ }
  return null;
}

export async function handle(req, env, ctx, now = new Date(), rand = () => crypto.randomUUID().replace(/-/g, "").slice(0, 8)) {
  const fallback = env.FALLBACK || "https://autoants.com/";
  const m = new URL(req.url).pathname.match(/^\/r\/([^/]+)\/?$/);
  const code = m ? decodeURIComponent(m[1]).toLowerCase() : "";
  if (!CODE.test(code)) return go(fallback);
  const target = (await targetFor(env, code)) || fallback;
  if (req.method === "GET") {
    // Only the code, the time and the device class are written. Nothing from req.headers but the UA's class,
    // and nothing from req.cf (no IP, no location).
    const write = env.MAILTRACK.put(`scan:${code}:${now.toISOString()}:${rand()}`, "1",
                                    { metadata: { d: device(req.headers.get("user-agent")) }, expirationTtl: TTL })
      .catch(() => {});
    if (ctx && ctx.waitUntil) ctx.waitUntil(write); else await write;
  }
  return go(withRef(target, code));
}

export default { fetch: (req, env, ctx) => handle(req, env, ctx) };
