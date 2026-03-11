from __future__ import annotations

import requests
from requests import Response, Session


class FetchError(RuntimeError):
    pass


def fetch(session: Session, url: str, timeout: int) -> Response:
    try:
        response = session.get(url, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        return response
    except requests.RequestException as exc:
        raise FetchError(f"Failed to fetch {url}: {exc}") from exc
