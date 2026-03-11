from requests import Response


class DummyHeaders:
    def __init__(self, values: list[str]) -> None:
        self._values = values

    def getlist(self, _name: str) -> list[str]:
        return self._values


class DummyRaw:
    def __init__(self, values: list[str]) -> None:
        self.headers = DummyHeaders(values)


from web_lab_scanner.analyzers.cookies import analyze_cookies


def test_analyze_cookies_flags_missing_cookie_attributes() -> None:
    response = Response()
    response.status_code = 200
    response.url = "http://example.com"
    response._content = b""
    response.raw = DummyRaw(["sessionid=abc123; Path=/"])

    findings = analyze_cookies(response)

    titles = {finding.title for finding in findings}
    assert "Cookie missing HttpOnly flag" in titles
    assert "Cookie missing SameSite attribute" in titles
