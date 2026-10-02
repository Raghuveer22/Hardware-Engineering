#!/usr/bin/env python3
"""
==============================================================================
File: synthesis/synthesize.py
Description: Centralized Yosys logic synthesis and schematic image generator.
             Synthesizes RTL modules, computes gate/register metrics, and
             exports schematic diagrams (.svg / .png) into schematics/ folder.
==============================================================================
"""

import subprocess
import os
import sys
import argparse
from pathlib import Path
import re

MODULE_SOURCES = {
    "multiplier_int8": ["rtl/multiplier_int8.sv"],
    "mac_unit": ["rtl/mac_unit.sv"],
    "pe": ["rtl/mac_unit.sv", "rtl/pe.sv"],
    "systolic_array": ["rtl/mac_unit.sv", "rtl/pe.sv", "rtl/systolic_array.sv"]
}

def synthesize_module(module_name, out_dir="schematics"):
    if module_name not in MODULE_SOURCES:
        raise ValueError(f"Unknown module '{module_name}'. Available: {list(MODULE_SOURCES.keys())}")

    proj_dir = Path(__file__).resolve().parent.parent
    if str(proj_dir) not in sys.path:
        sys.path.insert(0, str(proj_dir))
    schematics_dir = proj_dir / out_dir
    schematics_dir.mkdir(parents=True, exist_ok=True)

    sources = [s for s in MODULE_SOURCES[module_name]]
    read_cmd = " ".join([f'read_verilog -sv {s};' for s in sources])

    dot_file = schematics_dir / f"{module_name}.dot"
    svg_file = schematics_dir / f"{module_name}.svg"
    png_file = schematics_dir / f"{module_name}.png"

    print(f"\n========================================================")
    print(f"🔬 SYNTHESIZING: {module_name.upper()}")
    print(f"========================================================")

    os.chdir(proj_dir)

    # Generate high-level DOT and gate-level statistics
    yosys_script = (
        f"{read_cmd} "
        f"hierarchy -top {module_name}; "
        f"proc; opt; memory; opt; fsm; opt; "
        f"stat; "
        f"show -format dot -prefix {out_dir}/{module_name} {module_name}"
    )

    res = subprocess.run(["yosys", "-p", yosys_script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # Parse statistics from Yosys output
    stat_match = re.search(r"=== " + re.escape(module_name) + r" ===.*?(?=\n\d+\.|\Z)", res.stdout, re.DOTALL)
    if stat_match:
        print("\n📊 Gate-Level Cell & Register Statistics:")
        print(stat_match.group(0).strip())

    # Generate PNG from DOT if available
    if dot_file.exists():
        try:
            subprocess.run(["dot", "-Tpng", "-Gdpi=150", str(dot_file), "-o", str(png_file)], check=True)
            print(f"🖼️ PNG Schematic: {png_file}")
        except Exception as e:
            print(f"Warning converting PNG: {e}")

    # Generate Interactive Collapsible SVG
    try:
        from synthesis.generate_schematics import (
            generate_multiplier_svg,
            generate_mac_unit_svg,
            generate_pe_svg,
            generate_systolic_array_svg
        )
        if module_name == "multiplier_int8":
            generate_multiplier_svg(svg_file)
        elif module_name == "mac_unit":
            generate_mac_unit_svg(svg_file)
        elif module_name == "pe":
            generate_pe_svg(svg_file)
        elif module_name == "systolic_array":
            generate_systolic_array_svg(svg_file)
        print(f"🎨 Interactive Collapsible SVG: {svg_file}")
    except Exception as e:
        print(f"Warning generating interactive SVG: {e}")

    print(f"✅ Synthesis complete for {module_name}!\n")

def main():
    parser = argparse.ArgumentParser(description="Centralized Yosys Synthesis & Interactive Schematic Generator")
    parser.add_argument("--top", default="all", choices=list(MODULE_SOURCES.keys()) + ["all"],
                        help="Which module to synthesize (default: all)")
    parser.add_argument("--out", default="schematics", help="Output directory for schematics")
    args = parser.parse_args()

    if args.top == "all":
        for mod in MODULE_SOURCES:
            synthesize_module(mod, args.out)
    else:
        synthesize_module(args.top, args.out)

    print("🚀 View interactive schematics by opening: schematics/index.html")

if __name__ == "__main__":
    main()
