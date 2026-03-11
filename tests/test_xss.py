from web_lab_scanner.analyzers.xss import XSS_MARKER, build_probe_url


def test_build_probe_url_adds_default_query_param() -> None:
    mutated_url, parameter = build_probe_url("http://example.com/search")
    assert parameter == "q"
    assert f"q={XSS_MARKER}" in mutated_url


def test_build_probe_url_reuses_existing_query_param() -> None:
    mutated_url, parameter = build_probe_url("http://example.com/search?term=abc")
    assert parameter == "term"
    assert f"term={XSS_MARKER}" in mutated_url
