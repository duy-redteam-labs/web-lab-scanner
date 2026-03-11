from __future__ import annotations

from web_lab_scanner.analyzers.cookies import analyze_cookies
from web_lab_scanner.analyzers.csrf import analyze_csrf
from web_lab_scanner.analyzers.forms import parse_forms
from web_lab_scanner.analyzers.headers import analyze_headers
from web_lab_scanner.analyzers.sqli import analyze_sqli
from web_lab_scanner.analyzers.xss import analyze_xss
from web_lab_scanner.crawler import crawl
from web_lab_scanner.http_client import fetch
from web_lab_scanner.models import ScanConfig, ScanResult
from web_lab_scanner.session_manager import build_session


class Scanner:
    def __init__(self, config: ScanConfig) -> None:
        self.config = config

    def run(self) -> ScanResult:
        session = build_session(self.config)
        response = fetch(session, self.config.target, timeout=self.config.timeout)

        pages_scanned = crawl(
            session,
            response.url,
            max_depth=self.config.max_depth,
            max_pages=self.config.max_pages,
            timeout=self.config.timeout,
        )

        findings = []

        if self.config.checks.get("headers", True):
            findings.extend(analyze_headers(response))

        if self.config.checks.get("cookies", True):
            findings.extend(analyze_cookies(response))

        forms = parse_forms(response.url, response.text)

        if self.config.checks.get("csrf", True):
            findings.extend(analyze_csrf(forms))

        if self.config.checks.get("xss", True):
            findings.extend(analyze_xss(session, pages_scanned, timeout=self.config.timeout))

        if self.config.checks.get("sqli", True):
            findings.extend(analyze_sqli(session, pages_scanned, timeout=self.config.timeout))

        result = ScanResult(
            target=self.config.target,
            findings=findings,
            pages_scanned=pages_scanned,
            metadata={
                "max_depth": self.config.max_depth,
                "max_pages": self.config.max_pages,
                "timeout": self.config.timeout,
                "checks": self.config.checks,
                "status_code": response.status_code,
                "content_type": response.headers.get("Content-Type", ""),
                "forms_detected": len(forms),
            },
        )

        result.summary.total_findings = len(result.findings)
        for finding in result.findings:
            if finding.severity in result.summary.by_severity:
                result.summary.by_severity[finding.severity] += 1

        return result
