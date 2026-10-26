from core import db

SEED = {
    "guideline": [
        "Use a calm, clear, professional tone. Avoid hype and exclamation marks.",
        'Never describe ClearBrand as "the best", "perfect", "100% accurate" or "guaranteed", unless an approved fact supports the claim.',
        "Always state that people make the final decision. ClearBrand suggests fixes and never publishes or rewrites content automatically.",
        "When mentioning AI, disclose that an external AI service (Google Gemini) is used for part of the checks.",
        "Explain every finding by naming the guideline or approved fact it relies on.",
    ],
    "fact": [
        "ClearBrand is a brand-governance web application built by team ZeroDowntime for Codex 48, in response to a problem statement from Inkloom AI.",
        "ClearBrand checks drafts against the guidelines, approved facts and glossary that a manager adds.",
        "The checks are rule-based checks plus AI-assisted checks that use Google Gemini.",
        "AI findings are kept only if their cited source and quote can be verified against the approved material.",
        "ClearBrand has three roles (Creator, Reviewer and Manager) and supports comments, approvals and revision history.",
        "The current version reviews text content.",
    ],
    "glossary": [
        "users => teams",
        "rejected => flagged",
        "auto-fix => suggested-fix",
    ],
}


def seed_if_empty():
    if db.list_sources():
        return
    for kind, items in SEED.items():
        for text in items:
            db.add_source(kind, text)