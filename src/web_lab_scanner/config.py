from __future__ import annotations

from pathlib import Path

import yaml

from web_lab_scanner.models import ScanConfig


def load_config(path: str) -> ScanConfig:
    config_path = Path(path)
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}

    auth = data.get("auth", {})
    checks = data.get("checks", {})
    output = data.get("output", {})

    return ScanConfig(
        target=data["target"],
        max_depth=data.get("max_depth", 2),
        max_pages=data.get("max_pages", 30),
        timeout=data.get("timeout", 5),
        auth_cookies=auth.get("cookies", []),
        auth_headers=auth.get("headers", []),
        checks={
            "headers": checks.get("headers", True),
            "cookies": checks.get("cookies", True),
            "csrf": checks.get("csrf", True),
            "xss": checks.get("xss", True),
            "sqli": checks.get("sqli", True),
        },
        output_json=output.get("json"),
        output_html=output.get("html"),
    )
