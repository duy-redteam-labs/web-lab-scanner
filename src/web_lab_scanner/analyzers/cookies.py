from __future__ import annotations

from requests import Response

from web_lab_scanner.models import Finding


def analyze_cookies(response: Response) -> list[Finding]:
    findings: list[Finding] = []

    set_cookie_headers = response.raw.headers.getlist("Set-Cookie") if hasattr(response.raw, "headers") else []
    if not set_cookie_headers:
        return findings

    for index, cookie_header in enumerate(set_cookie_headers, start=1):
        lowered = cookie_header.lower()

        if "httponly" not in lowered:
            findings.append(
                Finding(
                    id=f"cookie-missing-httponly-{index}",
                    category="cookies",
                    title="Cookie missing HttpOnly flag",
                    severity="Medium",
                    confidence="High",
                    url=response.url,
                    method="GET",
                    evidence=f"Set-Cookie did not include HttpOnly: {cookie_header}",
                    recommendation="Add the HttpOnly flag to session cookies where appropriate.",
                )
            )

        if response.url.startswith("https://") and "secure" not in lowered:
            findings.append(
                Finding(
                    id=f"cookie-missing-secure-{index}",
                    category="cookies",
                    title="Cookie missing Secure flag",
                    severity="Medium",
                    confidence="High",
                    url=response.url,
                    method="GET",
                    evidence=f"Set-Cookie did not include Secure: {cookie_header}",
                    recommendation="Add the Secure flag to cookies sent over HTTPS.",
                )
            )

        if "samesite" not in lowered:
            findings.append(
                Finding(
                    id=f"cookie-missing-samesite-{index}",
                    category="cookies",
                    title="Cookie missing SameSite attribute",
                    severity="Low",
                    confidence="High",
                    url=response.url,
                    method="GET",
                    evidence=f"Set-Cookie did not include SameSite: {cookie_header}",
                    recommendation="Set SameSite=Lax or SameSite=Strict unless cross-site behavior is required.",
                )
            )

    return findings
