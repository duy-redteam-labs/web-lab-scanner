from web_lab_scanner.analyzers.sqli import SQLI_PAYLOAD, build_probe_url, contains_sql_error


def test_build_probe_url_adds_default_query_param() -> None:
    mutated_url, parameter = build_probe_url("http://example.com/item")
    assert parameter == "id"
    assert f"id=%27" in mutated_url


def test_build_probe_url_reuses_existing_query_param() -> None:
    mutated_url, parameter = build_probe_url("http://example.com/item?product=1")
    assert parameter == "product"
    assert f"product=%27" in mutated_url


def test_contains_sql_error_detects_common_patterns() -> None:
    body = "You have an error in your SQL syntax near '' at line 1"
    assert contains_sql_error(body) is True


def test_contains_sql_error_returns_false_for_normal_text() -> None:
    body = "Welcome to the homepage"
    assert contains_sql_error(body) is False
