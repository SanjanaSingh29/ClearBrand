import re

A11Y = "A11Y"
ALT_LINE = re.compile(r"^Image alt text \(image (\d+)\): (.*)$", re.MULTILINE)
VAGUE_ALT = {"image", "photo", "picture", "img", "graphic", "logo", "screenshot", "banner", "icon"}
VAGUE_LINK = re.compile(r"\b(click here|read more|learn more|tap here)\b", re.IGNORECASE)
CAPS_RUN = re.compile(r"\b(?:[A-Z]{2,}[ \t]+){2,}[A-Z]{2,}\b")
LOWER_HASHTAG = re.compile(r"#[a-z][a-z0-9]{11,}\b")
SENTENCE = re.compile(r"[^.!?\n]+[.!?]*")
MAX_WORDS_PER_SENTENCE = 35


def _finding(flagged, severity, reason, suggestion, start):
    return {
        "flagged_text": flagged,
        "category": "Accessibility",
        "severity": severity,
        "reason": reason,
        "source_code": A11Y,
        "suggestion": suggestion,
        "origin": "rule",
        "start": start,
    }


def _syllables(word):
    groups = re.findall(r"[aeiouy]+", word.lower())
    count = len(groups)
    if word.lower().endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def _reading_ease(text):
    words = re.findall(r"[A-Za-z']+", text)
    sentences = [s for s in SENTENCE.findall(text) if s.strip()]
    if len(words) < 40 or not sentences:
        return None
    syllables = sum(_syllables(w) for w in words)
    return 206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words))


def check_accessibility(text):
    findings = []

    for m in ALT_LINE.finditer(text):
        line, alt = m.group(0), m.group(2).strip()
        if not alt or alt.upper() == "MISSING":
            findings.append(_finding(
                line, "high",
                "This image has no alt text, so people using screen readers cannot tell what it shows.",
                "Replace MISSING with a short description of what the image shows and why it is there.",
                m.start()))
        elif (alt.lower().strip(".") in VAGUE_ALT or len(alt) < 8
              or re.search(r"\.(png|jpe?g|gif|webp)$", alt, re.IGNORECASE)
              or re.match(r"^(img|dsc|image|screenshot)[-_ ]?\d+", alt, re.IGNORECASE)):
            findings.append(_finding(
                line, "medium",
                "This alt text is too vague to be useful (for example just 'photo' or a file name).",
                "Describe what the image actually shows in one short sentence.",
                m.start()))

    # Hide the image lines so the checks below only look at the real text.
    masked = ALT_LINE.sub(lambda m: " " * len(m.group(0)), text)

    for m in VAGUE_LINK.finditer(masked):
        findings.append(_finding(
            m.group(0), "medium",
            "Vague link text is hard to understand when read out of context by a screen reader.",
            "Use descriptive link text, such as the name of the page it opens.",
            m.start()))

    for m in CAPS_RUN.finditer(masked):
        findings.append(_finding(
            m.group(0), "low",
            "Long runs of capital letters are harder to read, and some screen readers spell them out.",
            "Use normal sentence case.",
            m.start()))

    for m in LOWER_HASHTAG.finditer(masked):
        findings.append(_finding(
            m.group(0), "low",
            "A hashtag in all lowercase is read as one long word by screen readers.",
            "Capitalise each word, for example #BrandSafetyFirst.",
            m.start()))

    for m in SENTENCE.finditer(masked):
        sentence = m.group(0).strip()
        if len(sentence.split()) > MAX_WORDS_PER_SENTENCE:
            findings.append(_finding(
                sentence, "low",
                f"This sentence has {len(sentence.split())} words, which is hard to follow.",
                "Split it into two or three shorter sentences.",
                m.start()))

    ease = _reading_ease(masked)
    if ease is not None and ease < 30:
        findings.append(_finding(
            "Overall readability", "low",
            f"The text is very hard to read (reading ease {ease:.0f} out of 100; higher is easier).",
            "Use shorter sentences and simpler words.",
            0))

    return findings