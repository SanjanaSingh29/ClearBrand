from core import db, rules, retrieval, ai_check, verify


def run_checks(text):
    """Returns (findings, notice). Rule checks always run; the AI check is added when possible."""
    rule_findings = rules.run_rule_checks(text)
    notice = None
    ai_findings = []

    sources = db.list_sources()
    if not sources:
        notice = "No brand material has been added yet, so the AI check was skipped."
    else:
        passages = retrieval.retrieve(text, sources)
        raw, error = ai_check.run_ai_checks(text, passages)
        if error:
            notice = error
        else:
            by_code = {p["code"]: p for p in passages}
            ai_findings, dropped = verify.verify_findings(raw, text, by_code)
            if dropped:
                notice = f"{dropped} AI finding(s) were discarded because their source or quote could not be verified."

    def duplicates_rule(f):
        a = f["flagged_text"].lower()
        for r in rule_findings:
            t = r["flagged_text"].lower()
            if r["source_code"] == f["source_code"] and (t in a or a in t):
                return True
        return False

    ai_findings = [f for f in ai_findings if not duplicates_rule(f)]

    combined = rule_findings + ai_findings
    low_text = text.lower()
    combined.sort(key=lambda f: low_text.find(f["flagged_text"].lower()))
    return combined, notice