from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from requests import Session

from web_lab_scanner.http_client import FetchError, fetch
from web_lab_scanner.models import Finding


XSS_MARKER = "XSSMARK12345"


def build_probe_url(url: str, parameter_name: str = "q") -> tuple[str, str]:
    parsed = urlparse(url)
    query_pairs = parse_qsl(parsed.query, keep_blank_values=True)

    if query_pairs:
        target_param = query_pairs[0][0]
        query_pairs[0] = (target_param, XSS_MARKER)
        mutated_query = urlencode(query_pairs)
        mutated_url = urlunparse(parsed._replace(query=mutated_query))
        return mutated_url, target_param

    mutated_query = urlencode([(parameter_name, XSS_MARKER)])
    mutated_url = urlunparse(parsed._replace(query=mutated_query))
    return mutated_url, parameter_name


def analyze_xss(session: Session, urls: list[str], timeout: int) -> list[Finding]:
    findings: list[Finding] = []

    for index, url in enumerate(urls, start=1):
        probe_url, parameter_name = build_probe_url(url)

        try:
            response = fetch(session, probe_url, timeout=timeout)
        except FetchError:
            continue

        content_type = response.headers.get("Content-Type", "").lower()
        if "html" not in content_type:
            continue

        if XSS_MARKER in response.text:
            findings.append(
                Finding(
                    id=f"xss-reflection-{index}",
                    category="xss",
                    title="Potential reflected XSS indicator",
                    severity="Medium",
                    confidence="Medium",
                    url=probe_url,
                    method="GET",
                    parameter=parameter_name,
                    evidence=(
                        f"Injected marker {XSS_MARKER!r} was reflected in the HTML response after "
                        f"modifying parameter {parameter_name!r}."
                    ),
                    recommendation=(
                        "Review output encoding and input handling for reflected user-controlled data."
                    ),
                )
            )

    return findings
