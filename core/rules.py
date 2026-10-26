import re
from core import db

# Words that usually need proof when used in promotional content.
RISKY_CLAIMS = [
    "best", "no. 1", "number one", "#1", "guaranteed", "guarantee", "100%",
    "cheapest", "fastest", "leading", "unbeatable", "risk-free", "proven", "world-class",
]


def _find_all(term, text):
    pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
    return list(re.finditer(pattern, text, flags=re.IGNORECASE))


def check_glossary(text, sources):
    findings = []
    for s in sources:
        if s["kind"] != "glossary" or "=>" not in s["text"]:
            continue
        avoid, preferred = [p.strip() for p in s["text"].split("=>", 1)]
        if not avoid:
            continue
        for m in _find_all(avoid, text):
            findings.append({
                "flagged_text": m.group(0),
                "category": "Terminology",
                "severity": "low",
                "reason": f'The brand uses "{preferred}" instead of "{avoid}".',
                "source_code": s["code"],
                "suggestion": preferred,
                "origin": "rule",
                "start": m.start(),
            })
    return findings


def check_claims(text, sources):
    findings = []
    guidelines = [s for s in sources if s["kind"] == "guideline"]
    facts = [s for s in sources if s["kind"] == "fact"]
    for term in RISKY_CLAIMS:
        for m in _find_all(term, text):
            # If an approved fact mentions this word, treat the claim as backed by a source.
            if any(_find_all(term, f["text"]) for f in facts):
                continue
            rule = next((g for g in guidelines if _find_all(term, g["text"])), None)
            if rule:
                reason = (f'"{m.group(0)}" is a claim that needs an approved source, '
                          "and none is listed. Marked unverified.")
                code = rule["code"]
            else:
                reason = (f'"{m.group(0)}" is a claim, and no guideline or approved fact '
                          "covers it. Marked unverified.")
                code = None
            findings.append({
                "flagged_text": m.group(0),
                "category": "Unverified claim",
                "severity": "high",
                "reason": reason,
                "source_code": code,
                "suggestion": "Remove the claim, or add an approved fact that supports it and cite it.",
                "origin": "rule",
                "start": m.start(),
            })
    return findings


def run_rule_checks(text):
    sources = db.list_sources()
    findings = check_glossary(text, sources) + check_claims(text, sources)
    findings.sort(key=lambda f: f["start"])
    return findings