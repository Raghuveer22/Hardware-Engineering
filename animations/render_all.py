#!/usr/bin/env python3
"""
Master Animation Render Script for Hardware AI Acceleration Curriculum.
Renders all Manim animation scenes into high-quality MP4 videos.

Usage:
    python animations/render_all.py          # Render all 10 scenes
    python animations/render_all.py 04       # Render specific lab (e.g. Lab 04)
    python animations/render_all.py --high   # Render in 1080p60 high quality
"""

import sys
import subprocess
from pathlib import Path

ANIMATIONS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ANIMATIONS_DIR.parent

SCENES = [
    ("scene_lab00_prep.py", "Lab00PrepPrimer", "Lab 00-Prep: Hardware Primer"),
    ("scene_lab00_saturation.py", "Lab00SaturationIntro", "Lab 00: Signed Adder & Saturation"),
    ("scene_lab01_multiplier.py", "Lab01Multiplier", "Lab 01: INT8 Multiplier & Area"),
    ("scene_lab02_mac_unit.py", "Lab02MACUnit", "Lab 02: MAC Unit & Accumulator"),
    ("scene_lab03_pe.py", "Lab03ProcessingElement", "Lab 03: Weight-Stationary PE"),
    ("scene_lab04_systolic_array.py", "Lab04SystolicArray", "Lab 04: 4x4 Systolic Wavefront"),
    ("scene_lab05_sqrt.py", "Lab05SquareRoot", "Lab 05: Hardware Square Root"),
    ("scene_lab06_softmax.py", "Lab06Softmax", "Lab 06: Safe Softmax & FlashAttention"),
    ("scene_lab07_rsqrt.py", "Lab07RSQRT", "Lab 07: Fast RSQRT for RMSNorm"),
    ("scene_lab08_exp2_sfu.py", "Lab08ExponentialSFU", "Lab 08: Exponential SFU for SwiGLU"),
]

def main():
    args = sys.argv[1:]
    quality_flag = "-qh" if "--high" in args else "-qm"

    # Filter target if specified (e.g. '04' or 'systolic')
    target = None
    for a in args:
        if not a.startswith("--"):
            target = a.lower()
            break

    to_render = SCENES
    if target:
        to_render = [s for s in SCENES if target in s[0].lower() or target in s[1].lower() or target in s[2].lower()]
        if not to_render:
            print(f"❌ No scenes found matching '{target}'. Available: {[s[0] for s in SCENES]}")
            sys.exit(1)

    print(f"\n==================================================================")
    print(f"🎬 Hardware AI Acceleration — Manim Video Generator")
    print(f"   Quality: {'1080p 60fps' if quality_flag == '-qh' else '720p 30fps'}")
    print(f"   Total scenes to render: {len(to_render)}")
    print(f"==================================================================\n")

    for file_name, scene_name, title in to_render:
        script_path = ANIMATIONS_DIR / file_name
        print(f"▶ Rendering: {title} ({file_name} -> {scene_name})...")
        cmd = [
            sys.executable, "-m", "manim",
            quality_flag,
            str(script_path),
            scene_name
        ]
        res = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
        if res.returncode != 0:
            print(f"❌ Failed rendering {title}!")
            sys.exit(res.returncode)
        print(f"✅ Finished: {title}\n")

    print("🎉 All requested animations rendered successfully!")
    print(f"📁 Video files stored under: {PROJECT_ROOT / 'media' / 'videos'}\n")

if __name__ == "__main__":
    main()
