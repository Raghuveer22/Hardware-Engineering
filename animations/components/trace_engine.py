"""
Hardware AI Acceleration - Simulation Trace & Gate Netlist Engine
Reads real cycle-accurate simulation traces from visualizer/trace.json and
ingests Yosys-synthesized SVG netlists directly into Manim.
"""

import json
from pathlib import Path
from manim import *
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import theme as th


class TracePlayback:
    """
    Direct interface to pre-silicon Verilator / Cocotb simulation traces.
    Powers data-driven, cycle-accurate animations without manual scripting.
    """
    def __init__(self, trace_path=None):
        if trace_path is None:
            # Default to visualizer/trace.json in repository root
            root_dir = Path(__file__).resolve().parent.parent.parent
            trace_path = root_dir / "visualizer" / "trace.json"
        
        self.trace_path = Path(trace_path)
        self.data = self._load()

    def _load(self):
        if not self.trace_path.exists():
            return {"cycles": []}
        try:
            with open(self.trace_path, "r") as f:
                return json.load(f)
        except Exception:
            return {"cycles": []}

    @property
    def total_cycles(self):
        return len(self.data.get("cycles", []))

    def get_cycle_snapshot(self, cycle_idx):
        cycles = self.data.get("cycles", [])
        if 0 <= cycle_idx < len(cycles):
            return cycles[cycle_idx]
        return None

    def get_pe_registers(self, cycle_idx, row, col):
        snap = self.get_cycle_snapshot(cycle_idx)
        if snap and "pes" in snap and row < len(snap["pes"]) and col < len(snap["pes"][row]):
            pe = snap["pes"][row][col]
            return pe.get("w", 0), pe.get("a", 0), pe.get("sum", 0)
        return 0, 0, 0


class SchematicNetlist(VGroup):
    """
    Parses and renders Yosys-synthesized Netlistsvg gate-level schematics
    directly from schematics/*.svg into Manim scenes.
    """
    def __init__(self, module_name="mac_unit", target_width=8.0, **kwargs):
        super().__init__(**kwargs)
        root_dir = Path(__file__).resolve().parent.parent.parent
        svg_file = root_dir / "schematics" / f"{module_name}.svg"

        if svg_file.exists():
            self.svg = SVGMobject(str(svg_file), stroke_width=1.2)
            self.svg.set_width(target_width)
            self.add(self.svg)
        else:
            # Fallback placeholder if SVG not found
            box = RoundedRectangle(width=target_width, height=4.0, stroke_color=th.BORDER)
            txt = Text(f"SCHEMATIC: {module_name}.svg", font=th.MONO, font_size=th.FONT_BODY, color=th.MUTED)
            txt.move_to(box)
            self.add(box, txt)
            self.svg = box

    def highlight_subcircuit(self, submobject_index, color=th.CYAN, run_time=th.RATE_NORMAL):
        """Highlights a specific synthesized gate or wire within the SVG netlist."""
        if hasattr(self.svg, "submobjects") and submobject_index < len(self.svg.submobjects):
            target = self.svg.submobjects[submobject_index]
            return target.animate(run_time=run_time).set_color(color).set_stroke(width=3.0)
        return None
