from web_lab_scanner.analyzers.forms import parse_forms


def test_parse_forms_extracts_method_action_and_inputs() -> None:
    html = """
    <html>
      <body>
        <form method="post" action="/profile/update">
          <input type="text" name="username" value="alice">
          <input type="hidden" name="csrf_token" value="abc123">
          <textarea name="bio">hello</textarea>
        </form>
      </body>
    </html>
    """

    forms = parse_forms("http://example.com/account", html)

    assert len(forms) == 1
    form = forms[0]
    assert form.method == "POST"
    assert form.action == "http://example.com/profile/update"

    field_names = {field.name for field in form.inputs}
    assert "username" in field_names
    assert "csrf_token" in field_names
    assert "bio" in field_names
