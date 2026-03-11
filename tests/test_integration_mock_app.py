from __future__ import annotations

import html
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from web_lab_scanner.models import ScanConfig
from web_lab_scanner.scanner import Scanner


class MockAppHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/":
            body = """
            <html>
              <body>
                <a href="/search?term=hello">Search</a>
                <a href="/item?id=1">Item</a>
              </body>
            </html>
            """
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))
            return

        if parsed.path == "/search":
            params = parse_qs(parsed.query)
            term = params.get("term", [""])[0]
            body = f"<html><body>Search term: {html.escape(term)}</body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))
            return

        if parsed.path == "/item":
            params = parse_qs(parsed.query)
            item_id = params.get("id", [""])[0]

            if item_id == "'":
                body = "<html><body>You have an error in your SQL syntax near '' at line 1</body></html>"
            else:
                body = f"<html><body>Item id: {html.escape(item_id)}</body></html>"

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args) -> None:
        return


def test_scanner_detects_reflected_xss_indicator() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), MockAppHandler)
    host, port = server.server_address

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        config = ScanConfig(
            target=f"http://{host}:{port}/",
            max_depth=1,
            max_pages=5,
            timeout=3,
            checks={
                "headers": False,
                "cookies": False,
                "csrf": False,
                "xss": True,
                "sqli": False,
            },
        )

        result = Scanner(config).run()

        titles = {finding.title for finding in result.findings}
        assert "Potential reflected XSS indicator" in titles
        assert any("/search?" in page for page in result.pages_scanned)
    finally:
        server.shutdown()
        server.server_close()


def test_scanner_detects_sqli_indicator() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), MockAppHandler)
    host, port = server.server_address

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        config = ScanConfig(
            target=f"http://{host}:{port}/item?id=1",
            max_depth=0,
            max_pages=2,
            timeout=3,
            checks={
                "headers": False,
                "cookies": False,
                "csrf": False,
                "xss": False,
                "sqli": True,
            },
        )

        result = Scanner(config).run()

        titles = {finding.title for finding in result.findings}
        assert "Possible SQL injection indicator" in titles
    finally:
        server.shutdown()
        server.server_close()
