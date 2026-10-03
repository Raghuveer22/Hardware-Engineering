#!/usr/bin/env python3
"""
==============================================================================
File: visualizer/serve.py
Description: Generates the latest simulation trace and launches a local
             browser visualizer to watch systolic hardware execution.
==============================================================================
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path
import subprocess

import argparse

DEFAULT_PORT = 8080

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def main():
    parser = argparse.ArgumentParser(description="Serve Systolic Hardware Visualizer")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to serve on")
    parser.add_argument("--no-browser", action="store_true", help="Do not auto-open browser")
    args = parser.parse_args()

    vis_dir = Path(__file__).resolve().parent
    
    # 1. Generate latest trace from RTL simulator / model
    print("🔄 Generating latest hardware execution trace...")
    subprocess.run([sys.executable, str(vis_dir / "generate_trace.py")], check=True)

    # 2. Start simple HTTP server in visualizer directory
    os.chdir(vis_dir)
    handler = http.server.SimpleHTTPRequestHandler

    port = args.port
    httpd = None
    for attempt_port in range(port, port + 20):
        try:
            httpd = ReusableTCPServer(("", attempt_port), handler)
            port = attempt_port
            break
        except OSError:
            continue

    if not httpd:
        print(f"❌ Error: Could not bind to port {port} or next 20 ports.")
        sys.exit(1)

    with httpd:
        url = f"http://localhost:{port}"
        print(f"\n=======================================================")
        print(f"🚀 Systolic Array Hardware Visualizer running at:")
        print(f"   👉 {url}")
        print(f"=======================================================\n")
        if not args.no_browser:
            print("Opening in your browser... (Press Ctrl+C to stop)")
            try:
                webbrowser.open(url)
            except Exception:
                pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down visualizer server.")

if __name__ == "__main__":
    main()
