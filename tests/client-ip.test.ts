import { getTrustedClientIp } from "../supabase/functions/_shared/client-ip.ts";

Deno.test("prefers Cloudflare IP and ignores spoofed forwarding headers", () => {
  const headers = new Headers({
    "cf-connecting-ip": "203.0.113.25",
    "x-forwarded-for": "198.51.100.99",
    "x-real-ip": "192.0.2.88",
  });
  if (getTrustedClientIp(headers) !== "203.0.113.25") {
    throw new Error("did not select cf-connecting-ip");
  }
});

Deno.test("fails closed when Cloudflare IP is missing", () => {
  const headers = new Headers({
    "x-forwarded-for": "198.51.100.99",
    "x-real-ip": "192.0.2.88",
  });
  if (getTrustedClientIp(headers) !== "") {
    throw new Error("must not fall back to untrusted headers");
  }
});

Deno.test("trims whitespace around Cloudflare IP", () => {
  const headers = new Headers({ "cf-connecting-ip": " 203.0.113.25 " });
  if (getTrustedClientIp(headers) !== "203.0.113.25") {
    throw new Error("did not trim the trusted header");
  }
});
