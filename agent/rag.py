#!/usr/bin/env python3
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from agent.chain import rag_chain, retriever, reranker

from dotenv import load_dotenv
load_dotenv(BASE / ".env")

question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What does Promtior do?"

response = rag_chain.invoke(question)

print(f"Question: {question}\n")
print(response.content)

if os.environ.get("DEBUG"):
    docs = retriever.invoke(question)
    reranked = reranker.compress_documents(docs, question)
    print("\nSources:")
    for doc in reranked:
        print(f"  - {doc.metadata['source']}")
    print("\n--- Retrieved chunks ---")
    for i, doc in enumerate(reranked):
        print(f"\n[{i}] {doc.metadata['source']}")
        print(doc.page_content)
