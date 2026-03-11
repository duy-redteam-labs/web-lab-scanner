from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from web_lab_scanner.config import load_config
from web_lab_scanner.http_client import FetchError
from web_lab_scanner.models import ScanConfig
from web_lab_scanner.reporters.html_reporter import write_html_report
from web_lab_scanner.reporters.json_reporter import write_json_report
from web_lab_scanner.scanner import Scanner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="web-lab-scanner",
        description="Session-aware web application lab scanner.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Run a scan against a target URL.")
    scan_parser.add_argument("target", nargs="?", help="Target base URL.")
    scan_parser.add_argument("--config", help="Path to YAML config file.")
    scan_parser.add_argument("--max-depth", type=int, default=2, help="Maximum crawl depth.")
    scan_parser.add_argument("--max-pages", type=int, default=30, help="Maximum pages to scan.")
    scan_parser.add_argument("--timeout", type=int, default=5, help="HTTP timeout in seconds.")
    scan_parser.add_argument(
        "--cookie",
        action="append",
        default=[],
        help='Cookie string, for example: --cookie "session=abc123"',
    )
    scan_parser.add_argument(
        "--header",
        action="append",
        default=[],
        help='Custom header, for example: --header "Authorization: Bearer token"',
    )
    scan_parser.add_argument("--json", dest="output_json", help="Path to JSON output report.")
    scan_parser.add_argument("--html", dest="output_html", help="Path to HTML output report.")

    return parser


def _build_scan_config(args: argparse.Namespace) -> ScanConfig:
    if args.config:
        return load_config(args.config)

    if not args.target:
        raise SystemExit("error: target URL is required when --config is not used")

    return ScanConfig(
        target=args.target,
        max_depth=args.max_depth,
        max_pages=args.max_pages,
        timeout=args.timeout,
        auth_cookies=args.cookie,
        auth_headers=args.header,
        output_json=args.output_json,
        output_html=args.output_html,
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "scan":
        config = _build_scan_config(args)
        scanner = Scanner(config)

        try:
            result = scanner.run()
        except FetchError as exc:
            print(f"[ERROR] {exc}")
            print("[HINT] Verify the target is running and the host/port is correct.")
            return 1

        if config.output_json:
            write_json_report(result, config.output_json)

        if config.output_html:
            write_html_report(result, config.output_html)

        print(json.dumps(asdict(result), indent=2))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
