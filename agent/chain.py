import os

from langchain_cohere import CohereRerank
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

import agent.config  # noqa: F401 — loads .env and optionally SSM params
from agent.prompt import RAG_PROMPT

client = QdrantClient(url=os.environ["QDRANT_URL"])
embeddings = OpenAIEmbeddings(model=os.environ["EMBEDDING_MODEL"])

store = QdrantVectorStore(
    client=client,
    collection_name=os.environ["COLLECTION_NAME"],
    embedding=embeddings,
)

retriever = store.as_retriever(search_kwargs={"k": int(os.environ["TOP_K"])})
reranker = CohereRerank(
    model=os.environ["RERANK_MODEL"],
    top_n=int(os.environ["RERANK_TOP_N"]),
)
llm = ChatOpenAI(model=os.environ["LLM_MODEL"])


def retrieve_and_rerank(question: str) -> str:
    docs = retriever.invoke(question)
    reranked = reranker.compress_documents(docs, question)
    return "\n\n---\n\n".join(doc.page_content for doc in reranked)


rag_chain = (
    {"context": RunnableLambda(retrieve_and_rerank), "question": RunnablePassthrough()}
    | RAG_PROMPT
    | llm
)
