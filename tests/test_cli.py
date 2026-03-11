from web_lab_scanner.cli import build_parser


def test_scan_subcommand_exists() -> None:
    parser = build_parser()
    args = parser.parse_args(["scan", "http://localhost:3000"])
    assert args.command == "scan"
    assert args.target == "http://localhost:3000"
