#!/usr/bin/env python3
"""
=============================================================================
File: slides/serve.py
Description: Simple HTTP server to serve the interactive Hardware AI Acceleration
             curriculum slide decks with live interactive animations.
=============================================================================
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).resolve().parent), **kwargs)

def main():
    os.chdir(Path(__file__).resolve().parent)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print("=" * 65)
        print(f"⚡ Hardware AI Acceleration Interactive Slides Server Running")
        print(f"👉 Open in your browser: {url}")
        print(f"📥 PPTX Decks available for download directly inside the app")
        print("=" * 65)
        try:
            webbrowser.open(url)
        except Exception:
            pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    main()
