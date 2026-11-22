from pathlib import Path

FUNCTIONS = {
    "ask-iqdili": {
        "path": "supabase/functions/ask-iqdili/index.ts",
        "limiter": "consume_ask_rate_limit",
        "fail_closed": 'if (!supabaseUrl || !serviceRoleKey || !clientIp)',
    },
    "upload-pending-image": {
        "path": "supabase/functions/upload-pending-image/index.ts",
        "limiter": "consume_pending_image_rate_limit",
        "fail_closed": "if (!clientIp)",
    },
    "submit-public-post": {
        "path": "supabase/functions/submit-public-post/index.ts",
        "limiter": "consume_pending_image_rate_limit",
        "fail_closed": "if (!clientIp)",
    },
}

for name, contract in FUNCTIONS.items():
    source = Path(contract["path"]).read_text(encoding="utf-8")
    assert 'req.headers.get("cf-connecting-ip")?.trim() || ""' in source, (
        f"{name} must use only the Cloudflare client-IP header"
    )
    assert 'req.headers.get("x-forwarded-for")' not in source, (
        f"{name} must not trust caller-controlled X-Forwarded-For"
    )
    assert 'req.headers.get("x-real-ip")' not in source, (
        f"{name} must not fall back to an unverified IP header"
    )
    assert contract["fail_closed"] in source, (
        f"{name} must fail closed when the trusted IP is unavailable"
    )
    assert contract["limiter"] in source, (
        f"{name} must retain its server-side database rate limiter"
    )

ask_source = Path(FUNCTIONS["ask-iqdili"]["path"]).read_text(encoding="utf-8")
assert "15 سؤال في الساعة" in ask_source, "Ask rate-limit message must remain intact"

print("PASS: all three public endpoints use cf-connecting-ip only.")
print("PASS: caller-controlled IP headers are not used as fallbacks.")
print("PASS: missing trusted IP fails closed and database rate limits remain enabled.")
print("NOTE: static source checks do not prove that the hosted gateway overwrites spoofed headers.")
