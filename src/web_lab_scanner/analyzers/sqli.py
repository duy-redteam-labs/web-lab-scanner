from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from requests import Session

from web_lab_scanner.http_client import FetchError, fetch
from web_lab_scanner.models import Finding


SQLI_PAYLOAD = "'"

SQL_ERROR_PATTERNS = [
    r"you have an error in your sql syntax",
    r"warning:\s*mysql",
    r"mysql.*error",
    r"unclosed quotation mark after the character string",
    r"quoted string not properly terminated",
    r"sqlite error",
    r"sqlite3\.operationalerror",
    r"psycopg2\.",
    r"postgresql.*error",
    r"sqlstate",
    r"odbc sql server driver",
]


def build_probe_url(url: str, parameter_name: str = "id") -> tuple[str, str]:
    parsed = urlparse(url)
    query_pairs = parse_qsl(parsed.query, keep_blank_values=True)

    if query_pairs:
        target_param = query_pairs[0][0]
        query_pairs[0] = (target_param, SQLI_PAYLOAD)
        mutated_query = urlencode(query_pairs)
        mutated_url = urlunparse(parsed._replace(query=mutated_query))
        return mutated_url, target_param

    mutated_query = urlencode([(parameter_name, SQLI_PAYLOAD)])
    mutated_url = urlunparse(parsed._replace(query=mutated_query))
    return mutated_url, parameter_name


def contains_sql_error(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in SQL_ERROR_PATTERNS)


def analyze_sqli(session: Session, urls: list[str], timeout: int) -> list[Finding]:
    findings: list[Finding] = []

    for index, url in enumerate(urls, start=1):
        probe_url, parameter_name = build_probe_url(url)

        try:
            response = fetch(session, probe_url, timeout=timeout)
        except FetchError:
            continue

        content_type = response.headers.get("Content-Type", "").lower()
        if "html" not in content_type and "text" not in content_type:
            continue

        if contains_sql_error(response.text):
            findings.append(
                Finding(
                    id=f"sqli-error-{index}",
                    category="sqli",
                    title="Possible SQL injection indicator",
                    severity="Medium",
                    confidence="Medium",
                    url=probe_url,
                    method="GET",
                    parameter=parameter_name,
                    evidence=(
                        f"Response contained SQL error-like content after modifying parameter "
                        f"{parameter_name!r} with payload {SQLI_PAYLOAD!r}."
                    ),
                    recommendation=(
                        "Review server-side query construction and use parameterized queries for "
                        "user-controlled input."
                    ),
                )
            )

    return findings
