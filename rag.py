#!/usr/bin/env python3
import os
import sys

from dotenv import load_dotenv
from langchain_cohere import CohereRerank
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from prompt import RAG_PROMPT

load_dotenv()

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

retriever = store.as_retriever(search_kwargs={"k": TOP_K})

llm = ChatOpenAI(model=os.environ["LLM_MODEL"])

RERANK_TOP_N = int(os.environ["RERANK_TOP_N"])

docs = retriever.invoke(question)
reranker = CohereRerank(model=os.environ["RERANK_MODEL"], top_n=RERANK_TOP_N)
docs = reranker.compress_documents(docs, question)
context = "\n\n---\n\n".join(doc.page_content for doc in docs)

response = llm.invoke(RAG_PROMPT.format_messages(context=context, question=question))

print(f"Question: {question}\n")
print(response.content)

print("\nSources:")
for doc in docs:
    print(f"  - {doc.metadata['source']}")

if os.environ.get("DEBUG"):
    print("\n--- Retrieved chunks ---")
    for i, doc in enumerate(docs):
        print(f"\n[{i}] {doc.metadata['source']}")
        print(doc.page_content)
