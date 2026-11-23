from pathlib import Path

FUNCTIONS = {
    "ask-iqdili": "supabase/functions/ask-iqdili/index.ts",
    "upload-pending-image": "supabase/functions/upload-pending-image/index.ts",
    "submit-public-post": "supabase/functions/submit-public-post/index.ts",
}

helper = Path("supabase/functions/_shared/client-ip.ts").read_text(encoding="utf-8")
assert 'headers.get("cf-connecting-ip")?.trim() || ""' in helper
assert 'headers.get("x-forwarded-for")' not in helper
assert 'headers.get("x-real-ip")' not in helper

for name, path in FUNCTIONS.items():
    source = Path(path).read_text(encoding="utf-8")
    assert 'import { getTrustedClientIp } from "../_shared/client-ip.ts";' in source, name
    assert "getTrustedClientIp(req.headers)" in source, name
    assert "if (!clientIp)" in source or "|| !clientIp" in source, name
    assert 'req.headers.get("x-forwarded-for")' not in source, name
    assert 'req.headers.get("x-real-ip")' not in source, name

ask_source = Path(FUNCTIONS["ask-iqdili"]).read_text(encoding="utf-8")
assert "consume_ask_rate_limit" in ask_source
assert "15 سؤال في الساعة" in ask_source

for name in ("upload-pending-image", "submit-public-post"):
    source = Path(FUNCTIONS[name]).read_text(encoding="utf-8")
    assert "consume_pending_image_rate_limit" in source

print("PASS: all three endpoints call the shared trusted-IP helper.")
print("PASS: the helper accepts only cf-connecting-ip and fails closed.")
print("PASS: each endpoint rejects requests when the trusted IP is unavailable.")
print("PASS: all database rate limiters remain enabled.")
print("NOTE: unit/source tests cannot prove hosted gateway header rewriting.")
