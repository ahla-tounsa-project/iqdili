from pathlib import Path
import re

source = Path("supabase/functions/ask-iqdili/index.ts").read_text(encoding="utf-8")

# The platform overview must be grounded in the actual public navigation.
required_sections = [
    "الخدمات",
    "فرص العمل",
    "العقارات",
    "السوق",
    "باب الخير",
    "الدليل التونسي",
    "اسأل أحلى توانسة",
    "المنشورات الحية",
    "CV من أجل الخير",
    "حسابي",
    "الإدارة",
]
for section in required_sections:
    assert section in source, f"Missing platform section: {section}"

# Platform-specific questions must receive the curated answer before any web-backed model call.
overview_call = source.index("const platformOverview = getPlatformOverviewAnswer(question);")
groq_call = source.index('const groqApiKey = Deno.env.get("GROQ_API_KEY");')
assert overview_call < groq_call, "Platform overview must not depend on external web search."

# Reject the previously hallucinated external site and hotel-booking claim in the curated response.
overview = source[source.index("function getPlatformOverviewAnswer"):overview_call]
assert "a7latwensa.com" not in overview
assert "حجز الفنادق" not in overview

# The question normalizer must collapse whitespace correctly.
assert re.search(r'replace\(/\\s\+/g, " "\)', overview), "Whitespace normalization is missing."

print("Platform overview contract checks passed.")
