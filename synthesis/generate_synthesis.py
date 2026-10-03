#!/usr/bin/env python3
"""
Write an HTML schematic page for one SystemVerilog file.

    python synthesis/generate_synthesis.py labs/lab0/adder.sv
    python synthesis/generate_synthesis.py labs/lab0/adder.sv --top adder
    python synthesis/generate_synthesis.py labs/lab0/adder.sv --gates
    python synthesis/generate_synthesis.py labs/lab0/adder.sv --box

Default draws gates (or full-adder blocks). Pass --box for the RTL hierarchy
view. Output is always an .html file next to the source (unless -o is set).
Open it with Simple Browser or Live Preview in Cursor.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from synthesis.gate_schematic import synthesize_source


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Synthesize a SystemVerilog file to a schematic HTML page."
    )
    parser.add_argument("filepath", help="SystemVerilog source, for example labs/lab0/adder.sv")
    parser.add_argument("--top", default=None, help="Top module name when the file has more than one")
    parser.add_argument(
        "--gates",
        action="store_true",
        help="Draw AND/OR/XOR gates instead of full-adder blocks.",
    )
    parser.add_argument(
        "--box",
        action="store_true",
        help="RTL hierarchy box: click + to open internals (no Yosys gates).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="HTML path. Default: same folder and stem as the source (.html).",
    )
    args = parser.parse_args()

    source_path = Path(args.filepath)
    if not source_path.is_file():
        print(f"File not found: {source_path}", file=sys.stderr)
        return 1

    out_path = Path(args.output) if args.output else source_path.with_suffix(".html")
    if out_path.suffix.lower() != ".html":
        out_path = out_path.with_suffix(".html")

    source = source_path.read_text(encoding="utf-8")
    result = synthesize_source(
        source,
        args.top,
        expand_adders=not args.gates,
        box_only=args.box,
    )
    if not result.get("ok"):
        print(result.get("error") or "Synthesis failed.", file=sys.stderr)
        return 1

    content = result.get("html") or result.get("svg") or ""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")

    top = result.get("top") or "(auto)"
    gates = result.get("gate_count", 0)
    cells = result.get("cells") or []
    view = result.get("view") or "gates"
    print(f"{source_path} -> {out_path}")
    print(f"top: {top}   view: {view}   gates: {gates}   {result.get('elapsed_ms', 0)} ms")
    for row in cells:
        detail = f"  ({row['detail']})" if row.get("detail") else ""
        print(f"  {row['count']:4d}  {row['name']}{detail}")
    for note in result.get("notes") or []:
        print(f"note: {note}")
    for warning in result.get("warnings") or []:
        print(f"warning: {warning}")
    print(f"open: {out_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
