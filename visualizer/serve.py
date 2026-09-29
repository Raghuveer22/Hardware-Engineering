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

PORT = 8080

def main():
    vis_dir = Path(__file__).resolve().parent
    
    # 1. Generate latest trace from RTL simulator / model
    print("🔄 Generating latest hardware execution trace...")
    subprocess.run([sys.executable, str(vis_dir / "generate_trace.py")], check=True)

    # 2. Start simple HTTP server in visualizer directory
    os.chdir(vis_dir)
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"\n=======================================================")
        print(f"🚀 Systolic Array Hardware Visualizer running at:")
        print(f"   👉 {url}")
        print(f"=======================================================\n")
        print("Opening in your browser... (Press Ctrl+C to stop)")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down visualizer server.")

if __name__ == "__main__":
    main()
