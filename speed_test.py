import time
from core.ai_check import _make_client, get_api_key

client = _make_client(get_api_key())
models = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
]
for m in models:
    t = time.time()
    try:
        r = client.models.generate_content(model=m, contents="Reply with OK")
        print(m, round(time.time() - t, 1), "s ->", (r.text or "").strip()[:20])
    except Exception as e:
        print(m, round(time.time() - t, 1), "s FAILED", str(e)[:80])