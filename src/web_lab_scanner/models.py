from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Finding:
    id: str
    category: str
    title: str
    severity: str
    confidence: str
    url: str
    method: str | None = None
    parameter: str | None = None
    evidence: str = ""
    recommendation: str = ""


@dataclass(slots=True)
class InputField:
    name: str
    input_type: str = "text"
    value: str = ""


@dataclass(slots=True)
class FormInfo:
    page_url: str
    action: str
    method: str
    inputs: list[InputField] = field(default_factory=list)
    raw_html: str = ""


@dataclass(slots=True)
class ScanConfig:
    target: str
    max_depth: int = 2
    max_pages: int = 30
    timeout: int = 5
    auth_cookies: list[str] = field(default_factory=list)
    auth_headers: list[str] = field(default_factory=list)
    checks: dict[str, bool] = field(
        default_factory=lambda: {
            "headers": True,
            "cookies": True,
            "csrf": True,
            "xss": True,
            "sqli": True,
        }
    )
    output_json: str | None = None
    output_html: str | None = None


@dataclass(slots=True)
class ScanSummary:
    total_findings: int = 0
    by_severity: dict[str, int] = field(
        default_factory=lambda: {
            "High": 0,
            "Medium": 0,
            "Low": 0,
            "Info": 0,
        }
    )


@dataclass(slots=True)
class ScanResult:
    target: str
    findings: list[Finding] = field(default_factory=list)
    pages_scanned: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    summary: ScanSummary = field(default_factory=ScanSummary)
