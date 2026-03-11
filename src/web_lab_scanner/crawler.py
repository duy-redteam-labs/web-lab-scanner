from __future__ import annotations

from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag

from bs4 import BeautifulSoup
from requests import Session

from web_lab_scanner.http_client import FetchError, fetch


def normalize_url(url: str) -> str:
    clean_url, _fragment = urldefrag(url)
    return clean_url.rstrip("/") if clean_url.endswith("/") and len(clean_url) > len(urlparse(clean_url).scheme) + 3 else clean_url


def is_same_host(base_url: str, candidate_url: str) -> bool:
    base = urlparse(base_url)
    candidate = urlparse(candidate_url)
    return (base.scheme, base.netloc) == (candidate.scheme, candidate.netloc)


def is_http_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"}


def extract_links(base_url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        absolute = urljoin(base_url, href)
        absolute = normalize_url(absolute)

        if not is_http_url(absolute):
            continue

        links.append(absolute)

    return links


def crawl(
    session: Session,
    start_url: str,
    *,
    max_depth: int,
    max_pages: int,
    timeout: int,
) -> list[str]:
    visited: set[str] = set()
    discovered: list[str] = []
    queue: deque[tuple[str, int]] = deque([(normalize_url(start_url), 0)])

    while queue and len(discovered) < max_pages:
        current_url, depth = queue.popleft()

        if current_url in visited:
            continue

        visited.add(current_url)

        try:
            response = fetch(session, current_url, timeout=timeout)
        except FetchError:
            continue

        discovered.append(response.url)

        if depth >= max_depth:
            continue

        content_type = response.headers.get("Content-Type", "")
        if "html" not in content_type.lower():
            continue

        for link in extract_links(response.url, response.text):
            if not is_same_host(start_url, link):
                continue
            if link in visited:
                continue
            queue.append((link, depth + 1))

    return discovered
