import docx
import pdfplumber

MAX_FILE_MB = 5
MAX_CHARS = 20000
MAX_PDF_PAGES = 40


def _clip(text, notes):
    text = text.strip()
    if len(text) > MAX_CHARS:
        notes.append(f"The text was shortened to the first {MAX_CHARS:,} characters.")
        text = text[:MAX_CHARS]
    return text


def _docx_content(file):
    document = docx.Document(file)
    parts = [p.text.strip() for p in document.paragraphs if p.text.strip()]
    for table in document.tables:
        for row in table.rows:
            cells = []
            for cell in row.cells:
                value = cell.text.strip()
                if value and value not in cells:
                    cells.append(value)
            if cells:
                parts.append(" | ".join(cells))
    alts = []
    for shape in document.inline_shapes:
        try:
            alts.append((shape._inline.docPr.get("descr") or "").strip())
        except Exception:
            alts.append("")
    return "\n\n".join(parts), alts


def _pdf_content(file):
    with pdfplumber.open(file) as pdf:
        total_pages = len(pdf.pages)
        pages = pdf.pages[:MAX_PDF_PAGES]
        texts = [(page.extract_text() or "").strip() for page in pages]
        image_count = sum(len(page.images) for page in pages)
    return "\n\n".join(t for t in texts if t), image_count, total_pages


def extract_text(uploaded):
    """Returns (text, notes) for a .docx, .pdf, .txt or .md upload."""
    name = uploaded.name.lower()
    notes = []
    uploaded.seek(0)

    if name.endswith(".docx"):
        body, alts = _docx_content(uploaded)
        text = _clip(body, notes)
        if alts:
            lines = [f"Image alt text (image {i}): {alt or 'MISSING'}" for i, alt in enumerate(alts, 1)]
            text = (text + "\n\n" if text else "") + "Images in this document:\n" + "\n".join(lines)
            missing = sum(1 for a in alts if not a)
            notes.append(f"Found {len(alts)} image(s) in the document; {missing} without alt text.")
    elif name.endswith(".pdf"):
        body, image_count, total_pages = _pdf_content(uploaded)
        text = _clip(body, notes)
        if total_pages > MAX_PDF_PAGES:
            notes.append(f"Only the first {MAX_PDF_PAGES} of {total_pages} pages were read.")
        if image_count:
            notes.append(f"The PDF contains {image_count} image(s). Alt text cannot be read from PDFs, so check it in the source document.")
    elif name.endswith((".txt", ".md")):
        text = _clip(uploaded.getvalue().decode("utf-8", errors="ignore"), notes)
    else:
        raise ValueError("Unsupported file type")

    return text, notes