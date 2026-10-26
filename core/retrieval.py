import re

STOP = {
    "the", "and", "for", "with", "that", "this", "from", "your", "our", "you",
    "are", "was", "will", "have", "has", "not", "but", "all", "can", "its",
}


def _tokens(text):
    words = re.findall(r"[a-z0-9']+", text.lower())
    return {w for w in words if len(w) > 2 and w not in STOP}


def retrieve(text, sources, k=8):
    """Pick the brand passages the AI is allowed to see."""
    draft_words = _tokens(text)
    guidelines = [s for s in sources if s["kind"] == "guideline"][:10]
    others = [s for s in sources if s["kind"] != "guideline"]
    scored = []
    for s in others:
        overlap = len(draft_words & _tokens(s["text"]))
        if overlap > 0:
            scored.append((overlap, s))
    scored.sort(key=lambda pair: -pair[0])
    return guidelines + [s for _, s in scored[:k]]