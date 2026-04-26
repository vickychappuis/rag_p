#!/usr/bin/env python3
"""
Minimal Firecrawl-based ingestion for RAG pipeline.

Usage:
    python scrape.py "site:promtior.ai" search --limit 20
    python scrape.py https://www.promtior.ai/ crawl --limit 50
    python scrape.py https://careers.promtior.ai/ crawl --limit 50
"""

import argparse
import json
import os
import re
from urllib.parse import urlparse

from dotenv import load_dotenv
from firecrawl import Firecrawl

load_dotenv()
app = Firecrawl()


def _to_dict(obj):
    from datetime import datetime
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, "__dict__"):
        return _to_dict(vars(obj))
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_dict(i) for i in obj]
    return obj


def _safe_filename(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/") or "index"
    path = re.sub(r"[^a-zA-Z0-9_\-]", "_", path)
    return path + ".md"


def cmd_search(query: str, limit: int):
    os.makedirs("discovery_output", exist_ok=True)

    print(f"[search] query={query!r}  limit={limit}")
    raw = app.search(query, limit=limit)
    payload = _to_dict(raw)

    out_path = "discovery_output/search_output.json"
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"[search] saved raw response → {out_path}")

    results = (
        payload.get("web")
        or payload.get("data")
        or (payload if isinstance(payload, list) else [])
    )

    hosts = set()
    for item in results:
        url = item.get("url") or item.get("link") or ""
        if url:
            host = urlparse(url).netloc
            if host:
                hosts.add(host)

    hosts_path = "discovery_output/hosts.txt"
    with open(hosts_path, "w") as f:
        for host in sorted(hosts):
            f.write(host + "\n")

    print(f"[search] discovered {len(hosts)} unique host(s) → {hosts_path}")
    for h in sorted(hosts):
        print(f"  {h}")


def cmd_crawl(url: str, limit: int):
    host = urlparse(url).netloc
    if not host:
        raise ValueError(f"Cannot parse host from URL: {url!r}")

    out_dir = os.path.join("crawl_output", host)
    os.makedirs(out_dir, exist_ok=True)

    print(f"[crawl] url={url!r}  host={host}  limit={limit}")
    result = app.crawl(
        url,
        limit=limit,
        scrape_options={"formats": ["markdown"]},
    )
    payload = _to_dict(result)

    index_path = os.path.join(out_dir, f"{host}.json")
    with open(index_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"[crawl] saved index → {index_path}")

    pages = payload.get("data") or []
    saved = 0
    for page in pages:
        page_url = (page.get("metadata") or {}).get("url") or page.get("url") or ""
        markdown = page.get("markdown") or ""
        if not markdown:
            continue
        filename = _safe_filename(page_url)
        md_path = os.path.join(out_dir, filename)
        with open(md_path, "w") as f:
            f.write(markdown)
        saved += 1

    print(f"[crawl] saved {saved} markdown file(s) under {out_dir}/")


def cmd_crawl_all(hosts_file: str, limit: int):
    with open(hosts_file) as f:
        hosts = [line.strip() for line in f if line.strip()]
    for host in hosts:
        cmd_crawl(f"https://{host}/", limit)


def main():
    parser = argparse.ArgumentParser(description="Firecrawl ingestion for RAG pipeline")
    parser.add_argument("input", help="Query string (search/crawl) or hosts file path (crawl-all)")
    parser.add_argument("mode", choices=["search", "crawl", "crawl-all"])
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    if args.mode == "search":
        cmd_search(args.input, args.limit)
    elif args.mode == "crawl":
        cmd_crawl(args.input, args.limit)
    else:
        cmd_crawl_all(args.input, args.limit)


if __name__ == "__main__":
    main()
