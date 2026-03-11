from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from web_lab_scanner.models import FormInfo, InputField


def parse_forms(page_url: str, html: str) -> list[FormInfo]:
    soup = BeautifulSoup(html, "html.parser")
    forms: list[FormInfo] = []

    for form in soup.find_all("form"):
        method = (form.get("method") or "GET").upper()
        action = urljoin(page_url, form.get("action") or page_url)

        inputs: list[InputField] = []
        for tag in form.find_all(["input", "textarea", "select"]):
            name = (tag.get("name") or "").strip()
            if not name:
                continue

            if tag.name == "input":
                input_type = (tag.get("type") or "text").lower()
                value = tag.get("value") or ""
            elif tag.name == "textarea":
                input_type = "textarea"
                value = tag.text or ""
            else:
                input_type = "select"
                value = ""

            inputs.append(
                InputField(
                    name=name,
                    input_type=input_type,
                    value=value,
                )
            )

        forms.append(
            FormInfo(
                page_url=page_url,
                action=action,
                method=method,
                inputs=inputs,
                raw_html=str(form),
            )
        )

    return forms
