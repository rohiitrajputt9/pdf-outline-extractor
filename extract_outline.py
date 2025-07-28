import os
import json
from utils.pdf_utils import extract_text_by_page, extract_pdf_title
from utils.heading_detection import extract_outline

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

def process_pdf(pdf_path, output_path):
    pages = extract_text_by_page(pdf_path)
    outline_title, outline = extract_outline(pages)
    # Try to get title from metadata
    meta_title = extract_pdf_title(pdf_path)
    title = meta_title if meta_title else outline_title
    result = {
        "title": title,
        "outline": outline
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

def main():
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(INPUT_DIR, filename)
            output_path = os.path.join(OUTPUT_DIR, filename[:-4] + ".json")
            process_pdf(pdf_path, output_path)

if __name__ == "__main__":
    main() 