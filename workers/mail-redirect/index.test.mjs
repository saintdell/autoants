// node --test workers/mail-redirect/index.test.mjs   (no network, no Cloudflare)
import { test } from "node:test";
import assert from "node:assert/strict";
import { handle, device } from "./index.js";

function kv(init = {}) {
  const m = new Map(Object.entries(init)); const puts = [];
  return { puts, get: async k => m.get(k) ?? null, put: async (k, v, o) => { puts.push({ k, v, o }); } };
}
const req = (path, headers = {}) => new Request(`https://autoants.com${path}`, { headers });
const NOW = new Date("2026-10-21T15:04:05.123Z");

test("a scan logs code, time and device only, then redirects with ?ref", async () => {
  const MAILTRACK = kv({ "code:mt-5pws5r": JSON.stringify({ target: "https://autoants.com/?interest=Free%20company%20breakdown#contact" }) });
  const r = await handle(req("/r/mt-5pws5r", { "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0)",
    "cf-connecting-ip": "203.0.113.9", "x-forwarded-for": "203.0.113.9", "cookie": "a=b" }),
    { MAILTRACK }, null, NOW, () => "1a2b3c4d");
  assert.equal(r.status, 302);
  assert.equal(r.headers.get("location"), "https://autoants.com/?interest=Free+company+breakdown&ref=mt-5pws5r#contact");
  assert.equal(r.headers.get("cache-control"), "no-store");
  assert.equal(MAILTRACK.puts.length, 1);
  const p = MAILTRACK.puts[0];
  assert.equal(p.k, "scan:mt-5pws5r:2026-10-21T15:04:05.123Z:1a2b3c4d");
  assert.deepEqual(p.o.metadata, { d: "mobile" });
  const all = JSON.stringify(MAILTRACK.puts);
  assert.doesNotMatch(all, /203\.0\.113|iPhone|Mozilla|cookie/);
});

test("unknown code: logged, lands on the home page with its ref", async () => {
  const MAILTRACK = kv();
  const r = await handle(req("/r/mt-zzzzzz"), { MAILTRACK }, null, NOW, () => "00000000");
  assert.equal(r.headers.get("location"), "https://autoants.com/?ref=mt-zzzzzz");
});

test("malformed code: home page, nothing logged", async () => {
  const MAILTRACK = kv();
  const r = await handle(req("/r/../../etc"), { MAILTRACK }, null, NOW);
  assert.equal(r.headers.get("location"), "https://autoants.com/");
  assert.equal(MAILTRACK.puts.length, 0);
});

test("a non-https target in KV is ignored", async () => {
  const MAILTRACK = kv({ "code:mt-5pws5r": JSON.stringify({ target: "javascript:alert(1)" }) });
  const r = await handle(req("/r/mt-5pws5r"), { MAILTRACK }, null, NOW, () => "1a2b3c4d");
  assert.equal(r.headers.get("location"), "https://autoants.com/?ref=mt-5pws5r");
});

test("device classes are coarse", () => {
  assert.equal(device("facebookexternalhit/1.1"), "bot");
  assert.equal(device("Mozilla/5.0 (iPad; CPU OS 17_0)"), "tablet");
  assert.equal(device("Mozilla/5.0 (Linux; Android 14; Pixel 8) Mobile"), "mobile");
  assert.equal(device("Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0)"), "desktop");
  assert.equal(device(""), "other");
});
