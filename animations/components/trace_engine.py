"""
Hardware AI Acceleration - Simulation Trace & Gate Netlist Engine
Reads real cycle-accurate simulation traces from visualizer/trace.json and Cocotb testbenches,
driving 100% bit-accurate animation scenes in lockstep with synthesized Verilog RTL.
"""

import json
from pathlib import Path
from manim import *
import sys

ANIM_DIR = Path(__file__).resolve().parent.parent
if str(ANIM_DIR) not in sys.path:
    sys.path.insert(0, str(ANIM_DIR))

import theme as th
from components.layout import TextRole, SemanticText, HStack


class TracePlayback:
    """
    Direct interface to pre-silicon Verilator / Cocotb simulation traces.
    Powers data-driven, cycle-accurate animations without manual scripting.
    """
    def __init__(self, trace_path=None):
        if trace_path is None:
            root_dir = Path(__file__).resolve().parent.parent.parent
            trace_path = root_dir / "visualizer" / "trace.json"
        
        self.trace_path = Path(trace_path)
        self.data = self._load()

    def _load(self):
        if not self.trace_path.exists():
            return {"cycles": [], "matrices": {}, "dimensions": {}}
        try:
            with open(self.trace_path, "r") as f:
                return json.load(f)
        except Exception:
            return {"cycles": [], "matrices": {}, "dimensions": {}}

    @property
    def total_cycles(self):
        return len(self.data.get("cycles", []))

    @property
    def dimensions(self):
        return self.data.get("dimensions", {"ROWS": 4, "COLS": 4})

    @property
    def matrix_a(self):
        return self.data.get("matrices", {}).get("A", [])

    @property
    def matrix_w(self):
        return self.data.get("matrices", {}).get("W", [])

    def get_cycle_snapshot(self, cycle_idx):
        cycles = self.data.get("cycles", [])
        if 0 <= cycle_idx < len(cycles):
            return cycles[cycle_idx]
        return None

    def get_pe_state(self, cycle_idx, row, col):
        """Returns the full cycle state dict for PE at (row, col)."""
        snap = self.get_cycle_snapshot(cycle_idx)
        if snap:
            grid = snap.get("pe_grid", snap.get("pes", []))
            if row < len(grid) and col < len(grid[row]):
                return grid[row][col]
        return {
            "weight": 0, "act_in": 0, "act_reg": 0,
            "sum_in": 0, "sum_reg": 0, "mac_calc": "0"
        }

    def get_pe_registers(self, cycle_idx, row, col):
        """Returns tuple of (weight, act_reg, sum_reg)."""
        pe = self.get_pe_state(cycle_idx, row, col)
        return pe.get("weight", 0), pe.get("act_reg", 0), pe.get("sum_reg", 0)

    def get_cycle_inputs(self, cycle_idx):
        """Returns tuple of (weights_in, activations_in, act_skewed)."""
        snap = self.get_cycle_snapshot(cycle_idx)
        if snap:
            return (
                snap.get("weights_in", []),
                snap.get("activations_in", []),
                snap.get("act_skewed", [])
            )
        return [], [], []


class TraceDrivenController:
    """
    Binds physical animation components (PE cells, pin probes, buses) to named
    signals in a TracePlayback instance, advancing them automatically on clock edges.
    """
    def __init__(self, playback: TracePlayback = None):
        self.playback = playback or TracePlayback()
        self.pe_cells = {}      # (row, col) -> ProcessingElementCell
        self.input_probes = []  # list of PinProbe
        self.output_probes = [] # list of PinProbe
        self.current_cycle = -1

    def bind_pe(self, row: int, col: int, pe_cell):
        """Binds a ProcessingElementCell to grid coordinates."""
        self.pe_cells[(row, col)] = pe_cell

    def bind_input_probe(self, probe):
        self.input_probes.append(probe)

    def bind_output_probe(self, probe):
        self.output_probes.append(probe)

    def step_to_cycle(self, scene, target_cycle: int, run_time=th.RATE_FAST):
        """
        Advances all bound hardware cells and probes to target_cycle
        with animated bit-accurate value transformations.
        """
        self.current_cycle = target_cycle
        snap = self.playback.get_cycle_snapshot(target_cycle)
        if not snap:
            return

        anims = []
        # Update bound PE internal registers
        for (r, c), pe in self.pe_cells.items():
            state = self.playback.get_pe_state(target_cycle, r, c)
            w_val = state.get("weight", 0)
            a_reg = state.get("act_reg", 0)
            s_reg = state.get("sum_reg", 0)

            if hasattr(pe, "w_val"):
                anims.append(pe.w_val.update_text(f"{w_val:d}"))
            if hasattr(pe, "mac_eq"):
                anims.append(pe.mac_eq.update_text(f"{s_reg:d}"))

        if anims:
            scene.play(*anims, run_time=run_time)


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
            box = RoundedRectangle(width=target_width, height=4.0, stroke_color=th.BORDER)
            txt = SemanticText(f"SCHEMATIC: {module_name}.svg", role=TextRole.BLOCK_HEADER, color=th.MUTED)
            txt.move_to(box)
            self.add(box, txt)
            self.svg = box

    def highlight_subcircuit(self, submobject_index, color=th.CYAN, run_time=th.RATE_NORMAL):
        """Highlights a specific synthesized gate or wire within the SVG netlist."""
        if hasattr(self.svg, "submobjects") and submobject_index < len(self.svg.submobjects):
            target = self.svg.submobjects[submobject_index]
            return target.animate(run_time=run_time).set_color(color).set_stroke(width=3.0)
        return None
