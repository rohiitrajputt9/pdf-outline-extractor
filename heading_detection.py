import re

# Expanded list of known section names to always include as headings
KNOWN_H1 = [
    "TABLE OF CONTENTS", "ACKNOWLEDGEMENTS", "REVISION HISTORY", "REFERENCES", "PATHWAY OPTIONS",
    "SUMMARY", "BACKGROUND", "MILESTONES", "APPENDIX", "APPENDIX A", "APPENDIX B", "APPENDIX C",
    "EVALUATION AND AWARDING OF CONTRACT", "APPROACH AND SPECIFIC PROPOSAL REQUIREMENTS",
    "THE BUSINESS PLAN TO BE DEVELOPED", "TIMELINE", "PREAMBLE", "MEMBERSHIP", "CHAIR", "MEETINGS",
    "LINES OF ACCOUNTABILITY AND COMMUNICATION", "FINANCIAL AND ADMINISTRATIVE POLICIES",
    "ONTARIO’S DIGITAL LIBRARY", "A CRITICAL COMPONENT FOR IMPLEMENTING ONTARIO’S ROAD MAP TO PROSPERITY STRATEGY"
]

STOPWORDS = {"and", "the", "of", "to", "for", "in", "on", "at", "by", "with", "a", "an"}

def looks_like_date(text):
    text = text.strip()
    # Matches lines with only dots and numbers (e.g., '1.2.3.....')
    if re.match(r"^[.\-\/\\]+$", text):
        return True
    # Numeric date formats
    if re.match(r"^\d{1,2}[.\/-]\d{1,2}[.\/-]\d{2,4}$", text):
        return True
    if re.match(r"^\d{1,2}[.\/-]\d{2,4}$", text):
        return True
    if re.match(r"^\d{4}(-\d{4})?$", text):
        return True
    # Month name date formats (e.g., '18 JUNE 2013', '6 NOV 2013', '23 JULY 2013')
    if re.match(r"^\d{1,2}\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+\d{2,4}$", text, re.I):
        return True
    if re.match(r"^(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+\d{1,2},?\s+\d{2,4}$", text, re.I):
        return True
    return False

def looks_like_page_number(text):
    return bool(re.match(r"^page\s*\d+$", text, re.I)) or \
           bool(re.match(r"^\d{1,3}$", text.strip()))

def is_mostly_punctuation(text):
    text = text.strip()
    if not text:
        return True
    punct_count = sum(1 for c in text if not c.isalnum() and not c.isspace())
    return (punct_count / len(text)) > 0.6

def looks_like_address(text):
    # Exclude lines like '3735 PARKWAY' (number + single word, possibly all caps)
    return bool(re.match(r"^\d+\s+[A-Z][A-Z\s]+$", text.strip()))

def is_section_numbered(text):
    # Matches '1. ...', '2.1 ...', '3.2.1 ...', etc. (optionally with space after number)
    return bool(re.match(r"^\d+(\.\d+)*\s+.+", text))

def is_prominent_heading(line, avg_font_size, max_font_size):
    text = line["text"].strip()
    # Short, prominent, celebratory headings (e.g., invitations, flyers)
    celebratory_words = [
        "WELCOME", "INVITATION", "JOIN US", "RSVP", "PARTY", "CONGRATULATIONS", "SEE YOU", "CELEBRATE", "THANK YOU", "YOU'RE INVITED", "HOPE TO SEE YOU"
    ]
    if len(text.split()) <= 7 and len(text) <= 40:
        if (text.isupper() or text.istitle()) and (line["font_size"] >= max_font_size * 0.9):
            if any(word in text.upper() for word in celebratory_words):
                return True
        if ('!' in text or '?' in text) and line["font_size"] >= avg_font_size * 1.1:
            return True
    return False

def heading_level(text):
    # If in known H1, always H1
    if any(text.upper().startswith(kw) for kw in KNOWN_H1):
        return "H1"
    # Section-numbered: count dots for depth
    match = re.match(r"^(\d+)((\.\d+)+)\s+", text)
    if match:
        depth = text.count('.')
        if depth == 0:
            return "H1"
        elif depth == 1:
            return "H2"
        elif depth == 2:
            return "H3"
        elif depth == 3:
            return "H4"
        elif depth == 4:
            return "H5"
        else:
            return f"H{depth+1}"
    return "H2"  # Default for unnumbered headings not in known list

def normalize_heading_text(text):
    # Remove extra spaces and normalize
    return re.sub(r'\s+', ' ', text.strip())

def is_heading(line, avg_font_size, max_font_size):
    text = normalize_heading_text(line["text"])
    font_size = line.get("font_size", 0)
    is_bold = line.get("is_bold", False)
    y0 = line.get("y0", None)
    words = text.split()
    if len(text) < 3 or len(text) > 120:
        return False
    if looks_like_page_number(text):
        return False
    if looks_like_date(text):
        return False
    if is_mostly_punctuation(text):
        return False
    if looks_like_address(text):
        return False
    # Only allow section-numbered if there is text after the number
    if is_section_numbered(text):
        # Must have at least one word after the number
        if re.match(r"^\d+(\.\d+)*\s+\S+", text):
            return True
        else:
            return False
    # Allow unnumbered if in known list or matches known section name
    if any(text.upper().startswith(kw) for kw in KNOWN_H1):
        return True
    # Allow all-caps lines with exclamation mark as heading (for invitations, etc.)
    if text.isupper() and '!' in text and not looks_like_date(text) and not looks_like_address(text):
        return True
    # Allow prominent celebratory headings (flyers, invitations, etc.)
    if is_prominent_heading(line, avg_font_size, max_font_size):
        return True
    # Allow unnumbered, prominent headings (large, bold, or at top, and in known list)
    if (font_size > avg_font_size * 1.1 or is_bold or (y0 is not None and y0 < 150)):
        for kw in KNOWN_H1:
            if kw in text.upper():
                return True
    # Exclude headings that are just numbers, punctuation, or a single word (unless in known list)
    if len(text.split()) == 1 and not any(text.upper().startswith(kw) for kw in KNOWN_H1):
        return False
    if re.match(r"^[\d.\-\/\\]+$", text):
        return False
    return False

def extract_outline(pages):
    outline = []
    h_titles = []
    seen = set()  # To track (level, normalized text) pairs
    first_page = pages[0] if pages else []
    font_sizes = [line["font_size"] for line in first_page if "font_size" in line]
    avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 12
    max_font_size = max(font_sizes) if font_sizes else 12
    # Collect outline
    for i, lines in enumerate(pages):
        for line in lines:
            text = normalize_heading_text(line["text"])
            if is_heading(line, avg_font_size, max_font_size):
                level = heading_level(text)
                norm_key = (level, text.lower())
                if norm_key in seen:
                    continue  # Skip repeated headings (case-insensitive, normalized)
                seen.add(norm_key)
                outline.append({
                    "level": level,
                    "text": text,
                    "page": i  # Start from 0
                })
                if level in ("H1", "H2") and len(h_titles) < 3:
                    h_titles.append(text)
    # Title: concatenate first 2-3 H1/H2s if present, else first heading, else fallback
    if h_titles:
        title = " ".join(h_titles)
    elif outline:
        title = outline[0]["text"]
    else:
        title = ""
    return title, outline 