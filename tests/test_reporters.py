from pathlib import Path

from web_lab_scanner.models import Finding, ScanResult
from web_lab_scanner.reporters.html_reporter import write_html_report
from web_lab_scanner.reporters.json_reporter import write_json_report


def build_result() -> ScanResult:
    return ScanResult(
        target="http://example.com",
        findings=[
            Finding(
                id="test-1",
                category="headers",
                title="Missing CSP",
                severity="Medium",
                confidence="High",
                url="http://example.com",
                method="GET",
                evidence="CSP header was missing.",
                recommendation="Add CSP.",
            )
        ],
        pages_scanned=["http://example.com"],
        metadata={"status_code": 200, "content_type": "text/html"},
    )


def test_write_json_report(tmp_path: Path) -> None:
    output_file = tmp_path / "report.json"
    write_json_report(build_result(), str(output_file))

    content = output_file.read_text(encoding="utf-8")
    assert "Missing CSP" in content
    assert '"target": "http://example.com"' in content


def test_write_html_report(tmp_path: Path) -> None:
    output_file = tmp_path / "report.html"
    write_html_report(build_result(), str(output_file))

    content = output_file.read_text(encoding="utf-8")
    assert "<html" in content.lower()
    assert "Missing CSP" in content
    assert "Web Lab Scanner Report" in content
