from __future__ import annotations

from requests import Response

from web_lab_scanner.models import Finding


SECURITY_HEADERS = {
    "Content-Security-Policy": {
        "severity": "Medium",
        "title": "Missing Content-Security-Policy header",
        "recommendation": "Define a Content-Security-Policy header to reduce XSS impact.",
    },
    "X-Frame-Options": {
        "severity": "Medium",
        "title": "Missing X-Frame-Options header",
        "recommendation": "Set X-Frame-Options to DENY or SAMEORIGIN to reduce clickjacking risk.",
    },
    "X-Content-Type-Options": {
        "severity": "Low",
        "title": "Missing X-Content-Type-Options header",
        "recommendation": "Set X-Content-Type-Options to nosniff.",
    },
    "Referrer-Policy": {
        "severity": "Low",
        "title": "Missing Referrer-Policy header",
        "recommendation": "Set a Referrer-Policy header to reduce referrer leakage.",
    },
    "Permissions-Policy": {
        "severity": "Low",
        "title": "Missing Permissions-Policy header",
        "recommendation": "Set a Permissions-Policy header to restrict browser feature access.",
    },
}


def analyze_headers(response: Response) -> list[Finding]:
    findings: list[Finding] = []

    for header_name, metadata in SECURITY_HEADERS.items():
        if header_name not in response.headers:
            findings.append(
                Finding(
                    id=f"header-missing-{header_name.lower().replace('-', '_')}",
                    category="headers",
                    title=metadata["title"],
                    severity=metadata["severity"],
                    confidence="High",
                    url=response.url,
                    method="GET",
                    evidence=f"{header_name} header was not present in the response.",
                    recommendation=metadata["recommendation"],
                )
            )

    if response.url.startswith("https://") and "Strict-Transport-Security" not in response.headers:
        findings.append(
            Finding(
                id="header-missing-hsts",
                category="headers",
                title="Missing Strict-Transport-Security header",
                severity="Medium",
                confidence="High",
                url=response.url,
                method="GET",
                evidence="Strict-Transport-Security header was not present on an HTTPS response.",
                recommendation="Set the Strict-Transport-Security header for HTTPS responses.",
            )
        )

    return findings
