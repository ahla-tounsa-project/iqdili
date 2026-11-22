/**
 * Read the client IP supplied by the trusted Cloudflare proxy.
 * Never fall back to caller-controlled forwarding headers.
 */
export function getTrustedClientIp(headers: Headers): string {
  return headers.get("cf-connecting-ip")?.trim() || "";
}
