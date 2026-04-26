#!/usr/bin/env python3
import os
from pathlib import Path
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
os.makedirs("pdf_output", exist_ok=True)

for pdf in Path("pdfs").glob("*.pdf"):
    result = converter.convert(str(pdf))
    markdown = result.document.export_to_markdown()
    out_path = Path("pdf_output") / (pdf.stem + ".md")
    out_path.write_text(markdown)
    print(f"[extract] {pdf.name} → {out_path}")
