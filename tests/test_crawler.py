from web_lab_scanner.crawler import extract_links, is_same_host


def test_extract_links_resolves_relative_and_absolute_links() -> None:
    html = """
    <html>
      <body>
        <a href="/login">Login</a>
        <a href="http://example.com/profile">Profile</a>
        <a href="#ignore-fragment">Fragment</a>
      </body>
    </html>
    """
    links = extract_links("http://example.com/", html)

    assert "http://example.com/login" in links
    assert "http://example.com/profile" in links


def test_is_same_host() -> None:
    assert is_same_host("http://example.com", "http://example.com/login") is True
    assert is_same_host("http://example.com", "http://other.com/login") is False
