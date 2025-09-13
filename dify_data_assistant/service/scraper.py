from __future__ import annotations

import hashlib
from typing import Optional

import requests
from bs4 import BeautifulSoup
from diskcache import Cache
from markdownify import markdownify as to_md
from readability import Document


cache = Cache(directory="/workspace/dify_data_assistant/.cache", size_limit=10 * 1024 * 1024 * 1024)


def _make_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def fetch_to_markdown(url: str, ttl_seconds: int = 24 * 3600) -> str:
    key = _make_key(url)
    cached = cache.get(key)
    if cached is not None:
        return cached

    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    html = resp.text
    # readability to extract main content
    doc = Document(html)
    content_html = doc.summary(html_partial=True)
    soup = BeautifulSoup(content_html, "lxml")
    # remove script/style
    for tag in soup(["script", "style"]):
        tag.decompose()
    md = to_md(str(soup))
    cache.set(key, md, expire=ttl_seconds)
    return md

