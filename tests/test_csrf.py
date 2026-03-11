from web_lab_scanner.analyzers.csrf import analyze_csrf
from web_lab_scanner.models import FormInfo, InputField


def test_analyze_csrf_flags_post_form_without_token() -> None:
    forms = [
        FormInfo(
            page_url="http://example.com/account",
            action="http://example.com/profile/update",
            method="POST",
            inputs=[InputField(name="username", input_type="text")],
            raw_html='<form method="post" action="/profile/update"><input name="username"></form>',
        )
    ]

    findings = analyze_csrf(forms)

    assert len(findings) == 1
    assert findings[0].title == "POST form may be missing CSRF protection"


def test_analyze_csrf_skips_form_with_token() -> None:
    forms = [
        FormInfo(
            page_url="http://example.com/account",
            action="http://example.com/profile/update",
            method="POST",
            inputs=[
                InputField(name="username", input_type="text"),
                InputField(name="csrf_token", input_type="hidden"),
            ],
            raw_html='<form method="post" action="/profile/update"><input name="csrf_token"></form>',
        )
    ]

    findings = analyze_csrf(forms)

    assert findings == []
