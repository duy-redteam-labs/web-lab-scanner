from web_lab_scanner.models import ScanConfig
from web_lab_scanner.session_manager import build_session


def test_build_session_applies_headers_and_cookies() -> None:
    config = ScanConfig(
        target="http://example.com",
        auth_headers=["Authorization: Bearer test-token"],
        auth_cookies=["sessionid=abc123"],
    )

    session = build_session(config)

    assert session.headers["Authorization"] == "Bearer test-token"
    assert session.cookies.get("sessionid") == "abc123"
