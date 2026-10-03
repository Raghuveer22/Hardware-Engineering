#!/usr/bin/env python3
"""
Local playground: edit SystemVerilog, click Generate, see the gate schematic.

    python synthesis/playground_server.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
SCHEMATICS = ROOT / "schematics"
RTL = ROOT / "rtl"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from synthesis.gate_schematic import synthesize_source

DEFAULT_PORT = 8090
MAX_BODY = 512_000

EXAMPLES = {
    "adder": RTL / "adder.sv",
    "multiplier_int8": RTL / "multiplier_int8.sv",
    "mac_unit": RTL / "mac_unit.sv",
}

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".svg": "image/svg+xml",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json",
    ".png": "image/png",
}


class PlaygroundHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path in ("/", "/playground.html"):
            self._send_file(SCHEMATICS / "playground.html")
            return
        if path.startswith("/api/example/"):
            self._send_example(path[len("/api/example/"):])
            return
        if path.startswith("/api/"):
            self._send_json({"ok": False, "error": "Unknown API route."}, status=404)
            return
        file_path = self._static_file(path)
        if file_path is None:
            self._send_json({"ok": False, "error": "Not found."}, status=404)
            return
        self._send_file(file_path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/synthesize":
            self._send_json({"ok": False, "error": "Unknown API route."}, status=404)
            return
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0 or length > MAX_BODY:
            self._send_json({"ok": False, "error": "Request body is empty or too large."}, status=400)
            return
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json({"ok": False, "error": "Body must be JSON."}, status=400)
            return
        if not isinstance(payload, dict):
            self._send_json({"ok": False, "error": "Body must be a JSON object."}, status=400)
            return
        source = payload.get("source", "")
        top = payload.get("top") or ""
        if not isinstance(source, str) or not isinstance(top, str):
            self._send_json({"ok": False, "error": "source and top must be strings."}, status=400)
            return
        result = synthesize_source(source, top)
        status = 200 if result.get("ok") else 422
        self._send_json(result, status=status)

    def _send_example(self, name: str):
        path = EXAMPLES.get(name)
        if path is None or not path.is_file():
            self._send_json({"ok": False, "error": f"Unknown example '{name}'."}, status=404)
            return
        source = path.read_text(encoding="utf-8")
        self._send_json({"ok": True, "name": name, "top": name, "source": source})

    def _static_file(self, url_path: str) -> Path | None:
        rel = url_path.lstrip("/")
        if not rel or ".." in Path(rel).parts:
            return None
        candidate = (SCHEMATICS / rel).resolve()
        root = SCHEMATICS.resolve()
        if not str(candidate).startswith(str(root) + os.sep) and candidate != root:
            return None
        if candidate.is_file():
            return candidate
        return None

    def _send_file(self, path: Path):
        if not path.is_file():
            self._send_json({"ok": False, "error": "Not found."}, status=404)
            return
        data = path.read_bytes()
        kind = CONTENT_TYPES.get(path.suffix.lower(), "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload: dict, status: int = 200):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main():
    parser = argparse.ArgumentParser(description="Serve the SystemVerilog gate schematic playground")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    if not (SCHEMATICS / "playground.html").is_file():
        print("Missing schematics/playground.html")
        sys.exit(1)

    httpd = None
    port = args.port
    for attempt in range(port, port + 20):
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", attempt), PlaygroundHandler)
            port = attempt
            break
        except OSError:
            continue
    if httpd is None:
        print(f"Could not bind to port {args.port} or the next 20 ports.")
        sys.exit(1)

    url = f"http://127.0.0.1:{port}/"
    print("\n=======================================================")
    print("SystemVerilog gate playground")
    print(f"   {url}")
    print("Edit Verilog, click Generate, then edit again.")
    print("=======================================================\n")
    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down playground.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
