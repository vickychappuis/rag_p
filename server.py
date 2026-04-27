#!/usr/bin/env python3
from fastapi import FastAPI
from langserve import add_routes

from agent.chain import rag_chain

app = FastAPI(
    title="Promtior RAG",
    description="RAG chatbot for answering questions about Promtior",
)

add_routes(app, rag_chain, path="/chat")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
