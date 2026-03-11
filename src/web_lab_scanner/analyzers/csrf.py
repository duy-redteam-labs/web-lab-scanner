from __future__ import annotations

from web_lab_scanner.models import Finding, FormInfo


CSRF_FIELD_MARKERS = {
    "csrf",
    "csrf_token",
    "_csrf",
    "_token",
    "authenticity_token",
    "xsrf_token",
    "__requestverificationtoken",
}

STATE_CHANGING_HINTS = {
    "update",
    "delete",
    "change",
    "save",
    "profile",
    "password",
    "checkout",
    "cart",
    "transfer",
    "admin",
}


def _looks_state_changing(form: FormInfo) -> bool:
    haystack_parts = [form.action.lower(), form.raw_html.lower()]
    for field in form.inputs:
        haystack_parts.append(field.name.lower())

    haystack = " ".join(haystack_parts)
    return any(marker in haystack for marker in STATE_CHANGING_HINTS)


def _has_csrf_token(form: FormInfo) -> bool:
    for field in form.inputs:
        field_name = field.name.lower()
        if field_name in CSRF_FIELD_MARKERS:
            return True
        if "csrf" in field_name or "token" in field_name:
            return True
    return False


def analyze_csrf(forms: list[FormInfo]) -> list[Finding]:
    findings: list[Finding] = []

    for index, form in enumerate(forms, start=1):
        if form.method != "POST":
            continue

        if not _looks_state_changing(form):
            continue

        if _has_csrf_token(form):
            continue

        findings.append(
            Finding(
                id=f"csrf-missing-token-{index}",
                category="csrf",
                title="POST form may be missing CSRF protection",
                severity="Medium",
                confidence="Medium",
                url=form.page_url,
                method=form.method,
                evidence=(
                    f"Form posting to {form.action} looks state-changing but no CSRF-like token field "
                    "was detected."
                ),
                recommendation=(
                    "Add a per-request or per-session CSRF token to state-changing forms and validate it "
                    "server-side."
                ),
            )
        )

    return findings
