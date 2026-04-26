#!/usr/bin/env python3
import json
import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

load_dotenv()

COLLECTION = os.environ["COLLECTION_NAME"]
QDRANT_URL = os.environ["QDRANT_URL"]
CHUNKS_PATH = "data/chunks/chunks.json"

EMBEDDING_MODEL = os.environ["EMBEDDING_MODEL"]
EMBEDDING_DIMS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}
EMBEDDING_DIM = EMBEDDING_DIMS[EMBEDDING_MODEL]

embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

with open(CHUNKS_PATH) as f:
    chunks = json.load(f)

docs = [
    Document(
        page_content=c["text"],
        metadata={"source": c["source"], "chunk_index": c["chunk_index"]},
    )
    for c in chunks
]

client = QdrantClient(url=QDRANT_URL)

if client.collection_exists(COLLECTION):
    client.delete_collection(COLLECTION)

client.create_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
)

store = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION,
    embedding=embeddings,
)

BATCH = 100
for i in range(0, len(docs), BATCH):
    batch = docs[i : i + BATCH]
    store.add_documents(batch)
    print(f"[store] indexed {min(i + BATCH, len(docs))}/{len(docs)}")

info = client.get_collection(COLLECTION)
print(f"[store] done — {info.points_count} vectors in '{COLLECTION}'")
