import re

CATEGORIES = {"Tone", "Terminology", "Fact mismatch", "Unverified claim", "Messaging"}
SEVERITIES = {"high", "medium", "low"}


def _norm(t):
    return re.sub(r"\s+", " ", str(t)).strip().lower()


def verify_findings(raw_findings, draft_text, sources_by_code):
    """Keep only findings whose evidence can be checked. Returns (kept, dropped_count)."""
    kept = []
    dropped = 0
    for f in raw_findings:
        if not isinstance(f, dict):
            dropped += 1
            continue
        flagged = (f.get("flagged_text") or "").strip()
        if not flagged or _norm(flagged) not in _norm(draft_text):
            dropped += 1
            continue

        category = f.get("category") if f.get("category") in CATEGORIES else "Messaging"
        severity = f.get("severity") if f.get("severity") in SEVERITIES else "medium"
        code = f.get("source_code") or None

        if code:
            source = sources_by_code.get(code)
            quote = f.get("source_quote") or ""
            if not source or not quote or _norm(quote) not in _norm(source["text"]):
                dropped += 1
                continue
        else:
            if category != "Unverified claim":
                dropped += 1
                continue

        kept.append({
            "flagged_text": flagged,
            "category": category,
            "severity": severity,
            "reason": f.get("reason") or "Flagged by the AI check.",
            "source_code": code,
            "suggestion": f.get("suggestion") or "",
            "origin": "ai",
        })
    return kept, dropped