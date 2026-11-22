# Staging verification: trusted client IP headers

This runbook is for the isolated Supabase project `ahla-tounsa-staging`
(project ref `iaksqnyglraoybavydmb`) only. Do not deploy this probe to
production, and do not use the public production endpoints for header tests.

## Why this test is required

The unit tests prove that application code reads only `cf-connecting-ip`.
They cannot prove that the hosted Supabase/Cloudflare gateway overwrites or
rejects a caller-supplied `cf-connecting-ip`. That gateway behavior must be
observed at the deployed function boundary before merging PR #75.

## 1. Deploy a temporary, read-only probe to staging

Create a temporary Edge Function named `trusted-ip-probe` in the staging
project. Keep JWT verification enabled. Its entire handler should be:

```ts
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

Deno.serve((req: Request) => {
  if (req.method !== "GET") {
    return new Response("Method not allowed", { status: 405 });
  }
  return Response.json({
    cf_connecting_ip: req.headers.get("cf-connecting-ip"),
    x_forwarded_for: req.headers.get("x-forwarded-for"),
    x_real_ip: req.headers.get("x-real-ip"),
  }, {
    headers: { "Cache-Control": "no-store" },
  });
});
```

Do not add database access, email, AI, storage, or rate-limit calls. Do not
disable JWT verification. Use only the staging project's publishable/anon key
as the probe's `apikey` and bearer token.

## 2. Send baseline and forged-header requests

From a client outside Supabase, send the same GET request twice to:

`https://iaksqnyglraoybavydmb.supabase.co/functions/v1/trusted-ip-probe`

Include `apikey: <STAGING_PUBLISHABLE_KEY>` and
`Authorization: Bearer <STAGING_PUBLISHABLE_KEY>`.

- Baseline: send no forwarding headers. Record the returned fields.
- Forged test: send `X-Forwarded-For: 198.51.100.77`,
  `X-Real-IP: 198.51.100.78`, and
  `CF-Connecting-IP: 198.51.100.79`.
- Repeat the forged test from a second network if available.

The two RFC 5737 addresses above are documentation-only test values, not
real client addresses. Do not publish actual client IPs in issue comments.

## 3. Pass/fail interpretation

- **Pass for the Cloudflare header:** the forged value
  `198.51.100.79` is not returned as `cf_connecting_ip`; the returned
  value corresponds to the real connecting client or the trusted proxy's
  documented client-IP value.
- **Fail:** the function returns `198.51.100.79` as
  `cf_connecting_ip`. Do not merge PR #75; investigate the gateway trust
  boundary and use a gateway-authenticated source instead.
- **Inconclusive:** the header is absent, the request is blocked, or the
  observed value cannot be correlated with the actual client. Do not treat
  this as a pass.

The XFF and X-Real-IP fields are diagnostic only. PR #75 must continue to
ignore them regardless of what the gateway returns.

## 4. Cleanup and evidence

After recording the outcome, delete the temporary `trusted-ip-probe`
function from staging. Keep a redacted record containing the test time,
network used, status code, whether the forged value appeared, and the
pass/fail/inconclusive result. Never include API keys, bearer tokens, or
actual personal IP addresses.

This procedure has not yet been executed. Passing unit/contract tests or
deploying the probe alone is not evidence of gateway header rewriting.
