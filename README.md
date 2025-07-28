# PDF Outline Extractor – Adobe Hackathon 2025 (Problem 1A)

This project is a solution to **Problem Statement 1A** from the Adobe Hackathon 2025. 
It extracts the **document title** and a structured **hierarchical outline Headings** (H1, H2, H3) from unstructured PDF files using font metadata and layout analysis.

---

## Features

- Extracts:
  - **Title** (based on font size or metadata)
  - **Headings** (H1, H2, H3) using visual font hierarchy
- Works offline with **PyMuPDF (fitz)**
- Outputs results in the required **JSON format**
- Dockerized for consistent execution

---
## How to Run (Locally)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
