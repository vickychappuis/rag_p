#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

BASE = Path(__file__).resolve().parent.parent

load_dotenv(BASE / ".env")

COLLECTION = os.environ["COLLECTION_NAME"]
QDRANT_URL = os.environ["QDRANT_URL"]
TOP_K = int(os.environ["TOP_K"])

question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What does Promtior do?"

client = QdrantClient(url=QDRANT_URL)
embeddings = OpenAIEmbeddings(model=os.environ["EMBEDDING_MODEL"])

store = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION,
    embedding=embeddings,
)

results = store.similarity_search_with_score(question, k=TOP_K)

print(f"Query: {question}\n")
for doc, score in results:
    print(f"[{score:.4f}] ({doc.metadata['source']})")
    print(f"  {doc.page_content[:200]}")
    print()
