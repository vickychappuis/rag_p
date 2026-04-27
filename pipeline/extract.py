#!/usr/bin/env python3
import os
from pathlib import Path
from docling.document_converter import DocumentConverter

BASE = Path(__file__).resolve().parent.parent

converter = DocumentConverter()
os.makedirs(BASE / "data/pdfs", exist_ok=True)

for pdf in (BASE / "pdfs").glob("*.pdf"):
    result = converter.convert(str(pdf))
    markdown = result.document.export_to_markdown()
    out_path = BASE / "data/pdfs" / (pdf.stem + ".md")
    out_path.write_text(markdown)
    print(f"[extract] {pdf.name} → {out_path}")
