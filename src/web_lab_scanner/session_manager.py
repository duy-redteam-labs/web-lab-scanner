from __future__ import annotations

from requests import Session

from web_lab_scanner.models import ScanConfig


def _split_header(header_line: str) -> tuple[str, str]:
    if ":" not in header_line:
        raise ValueError(f"Invalid header format: {header_line!r}")
    name, value = header_line.split(":", 1)
    return name.strip(), value.strip()


def _split_cookie(cookie_line: str) -> tuple[str, str]:
    if "=" not in cookie_line:
        raise ValueError(f"Invalid cookie format: {cookie_line!r}")
    name, value = cookie_line.split("=", 1)
    return name.strip(), value.strip()


def build_session(config: ScanConfig) -> Session:
    session = Session()

    for header_line in config.auth_headers:
        name, value = _split_header(header_line)
        session.headers[name] = value

    for cookie_line in config.auth_cookies:
        name, value = _split_cookie(cookie_line)
        session.cookies.set(name, value)

    return session
