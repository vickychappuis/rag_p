#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from chonkie import SemanticChunker

load_dotenv()

CHUNK_OVERLAP = int(os.environ["CHUNK_OVERLAP"])


def clean_markdown(text):
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

chunker = SemanticChunker(
    embedding_model="minishlab/potion-base-32M",
    threshold=0.7,
    chunk_size=512,
)

SOURCE_DIRS = ["data/web", "data/pdfs"]
OUT_DIR = Path("data/chunks")
OUT_DIR.mkdir(parents=True, exist_ok=True)

all_chunks = []

for src_dir in SOURCE_DIRS:
    for md_file in sorted(Path(src_dir).rglob("*.md")):
        text = clean_markdown(md_file.read_text())
        if not text:
            continue

        chunks = chunker.chunk(text)
        for i, chunk in enumerate(chunks):
            overlap = chunks[i - 1].text[-CHUNK_OVERLAP:] if i > 0 else ""
            text_with_overlap = overlap + chunk.text if overlap else chunk.text
            all_chunks.append({
                "source": str(md_file),
                "chunk_index": i,
                "text": text_with_overlap,
                "token_count": chunk.token_count,
            })
        print(f"[chunk] {md_file} → {len(chunks)} chunks")

out_path = OUT_DIR / "chunks.json"
with open(out_path, "w") as f:
    json.dump(all_chunks, f, indent=2)

print(f"[chunk] total: {len(all_chunks)} chunks → {out_path}")
