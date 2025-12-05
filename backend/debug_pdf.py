import pdfplumber
from pathlib import Path

pdf_path = Path("pdfs/sample_pdf_1.pdf")

with pdfplumber.open(str(pdf_path)) as pdf:
    for i, page in enumerate(pdf.pages):
        print(f"\n===== PAGE {i+1} =====")
        text = page.extract_text()
        print(text)
        print("\n")
