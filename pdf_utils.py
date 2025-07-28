import fitz  # PyMuPDF

def extract_text_by_page(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    for page in doc:
        lines = []
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" not in b:
                continue
            for l in b["lines"]:
                line_text = ""
                max_font_size = 0
                is_bold = False
                for s in l["spans"]:
                    line_text += s["text"]
                    if s["size"] > max_font_size:
                        max_font_size = s["size"]
                    if "bold" in s.get("font", "").lower():
                        is_bold = True
                if line_text.strip():
                    lines.append({
                        "text": line_text.strip(),
                        "font_size": max_font_size,
                        "is_bold": is_bold,
                    })
        pages.append(lines)
    return pages


def extract_pdf_title(pdf_path):
    doc = fitz.open(pdf_path)
    title = doc.metadata.get("title")
    if title and title.strip():
        return title.strip()
    return None