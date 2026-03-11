from requests import Response

from web_lab_scanner.analyzers.headers import analyze_headers


def make_response(url: str, headers: dict[str, str]) -> Response:
    response = Response()
    response.status_code = 200
    response.url = url
    response.headers.update(headers)
    response._content = b""
    return response


def test_analyze_headers_flags_missing_headers() -> None:
    response = make_response("http://example.com", {})
    findings = analyze_headers(response)

    titles = {finding.title for finding in findings}
    assert "Missing Content-Security-Policy header" in titles
    assert "Missing X-Frame-Options header" in titles
    assert "Missing X-Content-Type-Options header" in titles
