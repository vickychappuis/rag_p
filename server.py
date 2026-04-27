#!/usr/bin/env python3
import os
from urllib.parse import urlparse, urlunparse

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from langserve import add_routes

import agent.config  # noqa: F401
from agent.chain import rag_chain

PUBLIC_URL = os.environ.get("ROOT_PATH", "")


class RewriteRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if PUBLIC_URL and "location" in response.headers:
            parsed = urlparse(response.headers["location"])
            public = urlparse(PUBLIC_URL)
            rewritten = parsed._replace(scheme=public.scheme, netloc=public.netloc)
            response.headers["location"] = urlunparse(rewritten)
        return response


app = FastAPI(
    title="Promtior RAG",
    description="RAG chatbot for answering questions about Promtior",
)

app.add_middleware(RewriteRedirectMiddleware)

add_routes(app, rag_chain, path="/chat")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, proxy_headers=True, forwarded_allow_ips="*")
