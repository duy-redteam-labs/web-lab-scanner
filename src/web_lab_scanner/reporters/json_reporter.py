from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from web_lab_scanner.models import ScanResult


def write_json_report(result: ScanResult, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
