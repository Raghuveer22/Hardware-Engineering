"""
Lab 00-Prep: Hardware Thinking Primer for Software & AI Engineers
Bridging the Gap from Python & PyTorch to Synthesizable Silicon Gates.

Visual-First 3Blue1Brown Standard:
Zero static bullet-point cards. Living dataflow, waveforms, physical wires,
capacitive energy dissipation, and in-circuit Python cosimulation.

Acts:
  Title: Temporal Execution vs. Spatial Silicon
  Act 0: Recipe vs. Machine (Instruction Tape vs. Concurrent Gates)
  Act 1: The Death of the Program Counter (Serial CPU vs. Streaming Wavefront)
  Act 2: The Physical Memory Energy Wall (Local Gate vs. Capacitive PCB Trace)
  Act 3: Wires vs. Registers (Dual Oscilloscope, Apertures & Analog Metastability)
  Act 4: The Golden Rule: = vs <= (Pipeline Preservation vs. Synthesizer Dissolve)
  Act 5: Host to Device (Command Ring Buffer, MMIO Doorbell & Ping-Pong SRAM)
  Act 6: Pytest for Silicon (Live Python Cocotb Driving Physical Pins)
"""

from manim import *
import numpy as np
import sys
from pathlib import Path

ANIM_DIR = Path(__file__).resolve().parent
if str(ANIM_DIR) not in sys.path:
    sys.path.insert(0, str(ANIM_DIR))

import theme as th
from components import (
    KineticSiliconScene,
    KineticClock,
    VoiceoverTracker,
    MemoryEnergyBar,
    DFlipFlopNode,
    SiliconWire,
    LaserPacketStream,
    HStack,
    VStack,
    code_line,
    map_point,
    snapshot,
)


class Lab00PrepPrimer(KineticSiliconScene):
    """Visual-first, kinetic hardware primer. Zero bullet slides."""

    def construct(self):
        self.clock = KineticClock(initial_cycle=0)
        self.ticker = self.clock.create_ticker_badge(prefix="CLK T=", color=th.CYAN_LIGHT)
        self.ticker.scale(0.82)
        self.ticker.to_corner(UR, buff=th.SPACE_SM)
        self.hud = self.ticker
        self.add(self.ticker)

        self.play_title()
        self.play_act0_recipe_vs_machine()
        self.play_act1_no_program_counter()
        self.play_act2_memory_energy_wall()
        self.play_act3_wires_vs_registers()
        self.play_act4_assign_vs_unpack()
        self.play_act5_host_to_device()
        self.play_act6_simulate_before_fab()

    # ------------------------------------------------------------------
    # Staging helpers
    # ------------------------------------------------------------------
    def _enter(self, st, *mobs, shift=UP * 0.12, run_time=0.6):
        st.register(*mobs)
        self.play(*[FadeIn(m, shift=shift) for m in mobs if m is not None], run_time=run_time)
        return run_time

    def _say(self, st, line, anim_time=0.0):
        if st.narration != line:
            st.update_narration(line, run_time=0.35)
            anim_time += 0.35
        dur = VoiceoverTracker(line).duration
        self.wait(max(0.2, dur - anim_time))

    def _op_node(self, symbol, title, color, radius=0.48):
        circle = Circle(
            radius=radius, color=color, stroke_width=2.5,
            fill_color="#072213", fill_opacity=0.92,
        )
        sym = Text(symbol, font=th.MONO, weight=BOLD, font_size=24, color=th.WHITE).move_to(circle)
        title_lbl = Text(title, font=th.MONO, font_size=10, color=color).next_to(circle, UP, buff=0.06)
        in1 = Line(circle.get_left() + UP * 0.22 + LEFT * 0.5, circle.get_left() + UP * 0.22, color=th.CYAN, stroke_width=2.0)
        in2 = Line(circle.get_left() + DOWN * 0.22 + LEFT * 0.5, circle.get_left() + DOWN * 0.22, color=th.CYAN, stroke_width=2.0)
        out = Line(circle.get_right(), circle.get_right() + RIGHT * 0.5, color=th.AMBER, stroke_width=2.0)
        node = VGroup(circle, sym, title_lbl, in1, in2, out)
        node.circle = circle
        node.sym = sym
        return node

    def _label(self, text, color=th.MUTED, size=11, weight=NORMAL, **kwargs):
        return Text(text, font=th.MONO, weight=weight, font_size=size, color=color, **kwargs)

    # =====================================================================
    # TITLE: Temporal Software vs. Spatial Silicon
    # =====================================================================
    def play_title(self):
        line = "You think in time: one line, then the next. A chip thinks in space: the circuit is always there."
        with self.stage(
            "LAB 00-PREP",
            "Hardware Thinking for Software Engineers",
            "Bridging Python to Synthesizable Silicon",
            narration=line,
        ) as st:
            # Left: Temporal Software Timeline
            t_title = self._label("SOFTWARE WORLD (TIME)", th.AMBER, 13, BOLD)
            tape_boxes = VGroup(*[
                RoundedRectangle(corner_radius=0.06, width=1.4, height=0.55, stroke_color=th.BORDER, stroke_width=1.5, fill_color="#0e1526", fill_opacity=0.92)
                for _ in range(3)
            ]).arrange(RIGHT, buff=0.18)
            tape_labels = VGroup(
                self._label("Line 1", th.TEXT, 11),
                self._label("Line 2", th.MUTED, 11),
                self._label("Line 3", th.MUTED, 11),
            )
            for b, l in zip(tape_boxes, tape_labels):
                l.move_to(b)
            step_arrow = Arrow(LEFT * 0.3, RIGHT * 0.3, color=th.AMBER_LIGHT, stroke_width=2.5).next_to(tape_boxes, DOWN, buff=0.15)
            seq_panel = VGroup(t_title, VGroup(tape_boxes, tape_labels), step_arrow).arrange(DOWN, buff=0.2)

            # Center divider
            vs_txt = Text("VS", font=th.MONO, weight=BOLD, font_size=18, color=th.FAINT)

            # Right: Spatial Silicon Grid
            s_title = self._label("SILICON WORLD (SPACE)", th.CYAN, 13, BOLD)
            spatial_grid = VGroup(*[
                RoundedRectangle(corner_radius=0.06, width=0.9, height=0.55, stroke_color=th.CYAN, stroke_width=1.5, fill_color="#081827", fill_opacity=0.92)
                for _ in range(4)
            ]).arrange_in_grid(rows=2, cols=2, buff=0.16)
            spatial_lbl = self._label("All Gates Live\nConcurrently", th.CYAN_LIGHT, 10, line_spacing=1.1).move_to(spatial_grid)
            wire_rays = VGroup(*[
                Line(spatial_grid.get_center(), pt, color=th.CYAN_DARK, stroke_width=1.5)
                for pt in [spatial_grid.get_left() + LEFT*0.4, spatial_grid.get_right() + RIGHT*0.4]
            ])
            hw_panel = VGroup(s_title, VGroup(spatial_grid, spatial_lbl, wire_rays)).arrange(DOWN, buff=0.2)

            stage_group = HStack(seq_panel, vs_txt, hw_panel, gap=th.SPACE_LG)
            st.place(stage_group)

            t = self._enter(st, stage_group, run_time=0.8)
            self._say(st, line, anim_time=t)
            st.takeaway("Software walks instructions in time. Hardware builds permanent physics in space.", wait=1.2)

    # =====================================================================
    # ACT 0: Recipe vs Machine (Instruction Tape vs Living Gates)
    # =====================================================================
    def play_act0_recipe_vs_machine(self):
        n0 = "In Python, a function is a recipe: the CPU fetches one instruction, does it, then fetches the next."
        n1 = "A chip is not a recipe. The adders and the multiplier are physical objects sitting on the die at the same time."
        n2 = "Same math. Two machines. One walks a list. The other is the list, wired in metal."
        with self.stage(
            "ACT 0",
            "Recipe vs Machine",
            "A function is a script. A chip is a factory.",
            narration=n0,
        ) as st:
            py = th.code_window(
                [
                    ("def y(a, b, c, d):", th.MUTED),
                    ("    t1 = a + b      # step 1", th.TEXT),
                    ("    t2 = c + d      # step 2", th.MUTED),
                    ("    return t1 * t2  # step 3", th.MUTED),
                ],
                title_text="PYTHON  —  RECIPE",
                width=5.1, height=2.8, font_size=13, title_color=th.AMBER,
            )
            pointer = Triangle(color=th.AMBER_LIGHT, fill_opacity=1.0).scale(0.09).rotate(-PI / 2)

            add1 = self._op_node("+", "ADDER 1", th.CYAN, radius=0.42)
            add2 = self._op_node("+", "ADDER 2", th.AMBER, radius=0.42)
            mul = self._op_node("×", "MULTIPLIER", th.GREEN, radius=0.46)
            add1.move_to(UP * 0.65 + LEFT * 0.9)
            add2.move_to(UP * 0.65 + RIGHT * 0.9)
            mul.move_to(DOWN * 0.75)
            w1 = Arrow(add1.circle.get_bottom(), mul.circle.get_top() + LEFT * 0.2, buff=0.06, color=th.CYAN, stroke_width=2.2)
            w2 = Arrow(add2.circle.get_bottom(), mul.circle.get_top() + RIGHT * 0.2, buff=0.06, color=th.AMBER, stroke_width=2.2)
            hw_title = self._label("SILICON  —  MACHINE (ALWAYS LIVE)", th.CYAN, 12, BOLD)
            hw = VGroup(hw_title, VGroup(add1, add2, mul, w1, w2)).arrange(DOWN, buff=0.18)
            hw_box = th.card(5.1, 3.2, stroke=th.CYAN)
            hw.move_to(hw_box)
            hw_panel = VGroup(hw_box, hw)

            pair = HStack(py, hw_panel, gap=th.SPACE_LG)
            st.place(pair)
            pointer.next_to(code_line(py, 1), LEFT, buff=th.SPACE_XS)

            t = self._enter(st, pair, run_time=0.8)
            st.register(pointer)
            self.play(FadeIn(pointer), run_time=0.3)
            self._say(st, n0, anim_time=t + 0.3)

            # Move instruction pointer in Python
            self.play(
                pointer.animate.next_to(code_line(py, 2), LEFT, buff=th.SPACE_XS),
                run_time=0.6,
            )
            self._say(st, n1, anim_time=0.6)

            # Silicon evaluates concurrently!
            self.play(
                add1.circle.animate.set_stroke(color=th.WHITE, width=3.8),
                add2.circle.animate.set_stroke(color=th.WHITE, width=3.8),
                run_time=0.45,
            )
            tok_a = Dot(radius=0.10, color=th.CYAN_LIGHT).move_to(add1.circle)
            tok_b = Dot(radius=0.10, color=th.AMBER_LIGHT).move_to(add2.circle)
            st.register(tok_a, tok_b)
            self.play(
                tok_a.animate.move_to(mul.circle.get_center() + LEFT * 0.16),
                tok_b.animate.move_to(mul.circle.get_center() + RIGHT * 0.16),
                mul.circle.animate.set_stroke(color=th.WHITE, width=4.0),
                run_time=0.75,
            )
            self.play(FadeOut(tok_a), FadeOut(tok_b), mul.circle.animate.set_stroke(color=th.GREEN, width=2.5), run_time=0.2)
            self._say(st, n2, anim_time=1.4)
            st.takeaway("Software describes steps. Hardware is the steps, sitting in space.", wait=1.2)

    # =====================================================================
    # ACT 1: No Program Counter (CPU Serial vs Continuous Wavefront)
    # =====================================================================
    def play_act1_no_program_counter(self):
        n0 = "To compute y equals (a plus b) times (c plus d), a CPU can point its program counter at only one line."
        n1 = "The chip has no program counter. With a=3, b=2, c=4, d=1, both adders show 5, and the multiplier already holds 25."
        n2 = "This is not threading. You placed two adder objects on the die. They exist together, so they finish while the CPU is still walking."
        with self.stage(
            "ACT 1",
            "There is No Program Counter",
            "A CPU walks a list. A chip is a live graph.",
            narration=n0,
        ) as st:
            eq = Text("y  =  (a + b)  ×  (c + d)", font=th.MONO, weight=BOLD, font_size=26, color=th.WHITE)
            eq_band, body = st.content.split_y(0.22, 0.78, gap=th.SPACE_SM)
            st.place(eq, eq_band)
            t0 = self._enter(st, eq, shift=DOWN * 0.1, run_time=0.5)

            # Left: CPU Pipeline
            cpu_title = self._label("CPU: SERIAL PIPELINE (3 CLOCKS)", th.AMBER, 12, BOLD)
            lines = [
                "0x00:  t1 = a + b    # Cycle 1",
                "0x04:  t2 = c + d    # Cycle 2",
                "0x08:  y  = t1 * t2  # Cycle 3",
            ]
            cpu_rows = VGroup()
            for src in lines:
                box = RoundedRectangle(
                    corner_radius=0.08, width=4.6, height=0.48,
                    stroke_color=th.BORDER, stroke_width=1.4,
                    fill_color="#0e1526", fill_opacity=0.94,
                )
                txt = Text(src, font=th.MONO, font_size=12, color=th.TEXT).move_to(box)
                cpu_rows.add(VGroup(box, txt))
            cpu_rows.arrange(DOWN, buff=0.1)
            pc = self._label("PC →", th.AMBER_LIGHT, 12, BOLD).next_to(cpu_rows[0], LEFT, buff=0.08)
            cpu_panel = VGroup(cpu_title, VGroup(cpu_rows, pc)).arrange(DOWN, buff=0.16)

            # Right: Silicon Spatial Graph
            hw_title = self._label("SILICON: CONCURRENT DATAFLOW", th.CYAN, 12, BOLD)
            add1 = self._op_node("+", "a+b", th.CYAN, radius=0.4)
            add2 = self._op_node("+", "c+d", th.AMBER, radius=0.4)
            mul = self._op_node("×", "y", th.GREEN, radius=0.44)
            add1.move_to(LEFT * 1.05 + UP * 0.45)
            add2.move_to(RIGHT * 1.05 + UP * 0.45)
            mul.move_to(DOWN * 0.95)
            w1 = Arrow(add1.circle.get_bottom(), mul.circle.get_top() + LEFT * 0.2, buff=0.05, color=th.CYAN, stroke_width=2.0)
            w2 = Arrow(add2.circle.get_bottom(), mul.circle.get_top() + RIGHT * 0.2, buff=0.05, color=th.AMBER, stroke_width=2.0)
            sum_l = self._label("5", th.CYAN_LIGHT, 16, BOLD).move_to(add1.circle)
            sum_r = self._label("5", th.AMBER_LIGHT, 16, BOLD).move_to(add2.circle)
            sum_y = self._label("25", th.GREEN_LIGHT, 16, BOLD).move_to(mul.circle)
            for lbl in (sum_l, sum_r, sum_y):
                lbl.set_opacity(0)
            nums = self._label("a=3, b=2    c=4, d=1", th.MUTED, 11)
            hw_panel = VGroup(hw_title, VGroup(add1, add2, mul, w1, w2, sum_l, sum_r, sum_y), nums).arrange(DOWN, buff=0.14)

            pair = HStack(cpu_panel, hw_panel, gap=th.SPACE_XL)
            st.place(pair, body)

            t1 = self._enter(st, pair, run_time=0.8)
            self._say(st, n0, anim_time=t0 + t1)

            # CPU highlights line 1. Silicon already holds both sums and the product.
            # No clock tick: these gates are combinational, so there is no program counter to advance.
            self.play(
                cpu_rows[0][0].animate.set_stroke(color=th.AMBER, width=2.6),
                add1.circle.animate.set_stroke(color=th.WHITE, width=3.8),
                add2.circle.animate.set_stroke(color=th.WHITE, width=3.8),
                mul.circle.animate.set_stroke(color=th.WHITE, width=3.8),
                add1.sym.animate.set_opacity(0),
                add2.sym.animate.set_opacity(0),
                mul.sym.animate.set_opacity(0),
                sum_l.animate.set_opacity(1),
                sum_r.animate.set_opacity(1),
                sum_y.animate.set_opacity(1),
                run_time=0.7,
            )
            self._say(st, n1, anim_time=0.7)

            # The program counter keeps walking after the chip is finished.
            self.play(
                pc.animate.next_to(cpu_rows[1], LEFT, buff=0.08),
                cpu_rows[0][0].animate.set_stroke(color=th.BORDER, width=1.4),
                cpu_rows[1][0].animate.set_stroke(color=th.AMBER, width=2.6),
                run_time=0.45,
            )
            self.play(
                pc.animate.next_to(cpu_rows[2], LEFT, buff=0.08),
                cpu_rows[1][0].animate.set_stroke(color=th.BORDER, width=1.4),
                cpu_rows[2][0].animate.set_stroke(color=th.GREEN, width=2.6),
                run_time=0.45,
            )
            self._say(st, n2, anim_time=0.9)
            st.takeaway("The CPU is still walking when the chip already holds 25.", wait=1.2)

    # =====================================================================
    # ACT 2: Memory Energy Wall (Local Gate vs. Capacitive PCB Trace)
    # =====================================================================
    def play_act2_memory_energy_wall(self):
        n0 = "In Python, a times b and arr of i look equally cheap. In silicon they are not even the same sport."
        n1 = "An eight-bit multiply-accumulate is about 0.2 picojoules. Fetching that byte from off-chip DRAM is about 200 picojoules — a thousand times more."
        n2 = "The ratio is one thousand. A linear bar would hide the multiply. Longer wires hold more charge, so the fetch costs more than the math."
        with self.stage(
            "ACT 2",
            "The Memory Energy Wall",
            "Compute is cheap. Moving data is what melts chips.",
            narration=n0,
        ) as st:
            # Physical Wire Comparison Visual
            # Top: On-Chip Microscopic Cell (10 um wire)
            on_chip_box = RoundedRectangle(corner_radius=0.1, width=5.6, height=1.65, stroke_color=th.GREEN, stroke_width=1.8, fill_color="#071b11", fill_opacity=0.92)
            on_title = self._label("ON-CHIP LOGIC (10 µm WIRE)", th.GREEN_LIGHT, 11, BOLD).next_to(on_chip_box.get_top(), DOWN, buff=0.10)
            cell_a = Circle(radius=0.22, color=th.CYAN, fill_color="#0a1d30", fill_opacity=0.9).move_to(on_chip_box.get_left() + RIGHT * 0.8)
            cell_b = Circle(radius=0.22, color=th.GREEN, fill_color="#072213", fill_opacity=0.9).move_to(on_chip_box.get_right() + LEFT * 0.8)
            wire_micro = Line(cell_a.get_right(), cell_b.get_left(), color=th.GREEN_LIGHT, stroke_width=2.5)
            cost_local = self._label("INT8 MAC: 0.2 pJ  (C ≈ 2 fF)", th.WHITE, 12, BOLD).next_to(wire_micro, DOWN, buff=0.12)
            local_vis = VGroup(on_chip_box, on_title, cell_a, cell_b, wire_micro, cost_local)

            # Bottom: Off-Chip Motherboard PCB Trace (10 cm wire with parasitic capacitors)
            pcb_box = RoundedRectangle(corner_radius=0.1, width=5.6, height=1.65, stroke_color=th.RED, stroke_width=1.8, fill_color="#200a0a", fill_opacity=0.92)
            pcb_title = self._label("OFF-CHIP DRAM BUS (10 cm PCB TRACE)", th.RED_LIGHT, 11, BOLD).next_to(pcb_box.get_top(), DOWN, buff=0.10)
            die_chip = RoundedRectangle(corner_radius=0.06, width=0.65, height=0.65, stroke_color=th.CYAN, fill_color="#0a1d30", fill_opacity=0.9).move_to(pcb_box.get_left() + RIGHT * 0.6)
            dram_chip = RoundedRectangle(corner_radius=0.06, width=0.65, height=0.65, stroke_color=th.RED, fill_color="#280909", fill_opacity=0.9).move_to(pcb_box.get_right() + LEFT * 0.6)
            trace_long = Line(die_chip.get_right(), dram_chip.get_left(), color=th.AMBER, stroke_width=3.5)
            
            # Distributed parasitic capacitors
            caps = VGroup()
            for frac in [0.25, 0.5, 0.75]:
                pt = trace_long.point_from_proportion(frac)
                c_lead = Line(pt, pt + DOWN * 0.18, color=th.AMBER_DARK, stroke_width=1.5)
                c_p1 = Line(pt + DOWN * 0.18 + LEFT * 0.12, pt + DOWN * 0.18 + RIGHT * 0.12, color=th.AMBER_LIGHT, stroke_width=2.0)
                c_p2 = Line(pt + DOWN * 0.24 + LEFT * 0.12, pt + DOWN * 0.24 + RIGHT * 0.12, color=th.AMBER_LIGHT, stroke_width=2.0)
                caps.add(c_lead, c_p1, c_p2)
            cost_dram = self._label("DRAM FETCH: 200.0 pJ  (1,000× COST!)", th.RED_LIGHT, 12, BOLD).next_to(trace_long, DOWN, buff=0.32)
            pcb_vis = VGroup(pcb_box, pcb_title, die_chip, dram_chip, trace_long, caps, cost_dram)

            wire_comparison = VStack(local_vis, pcb_vis, gap=th.SPACE_SM)

            # Log bars: log10(200/0.2) = 3 decades. Widths follow log10(pJ)+1,
            # and the axis says so. A linear bar of 1000× cannot fit honestly.
            bar_header = self._label("ENERGY, LOG SCALE", th.MUTED, 12, BOLD)
            mac_w = 0.7 * (np.log10(0.2) + 1.0)   # ~0.21
            dram_w = 0.7 * (np.log10(200.0) + 1.0)  # ~2.31, about 11× the MAC bar, not 32×
            bar_mac_lbl = self._label("MAC  0.2 pJ", th.GREEN_LIGHT, 12, BOLD)
            bar_mac = RoundedRectangle(corner_radius=0.04, width=mac_w, height=0.28, stroke_color=th.GREEN, fill_color=th.GREEN, fill_opacity=0.9)
            row_mac = HStack(bar_mac_lbl, bar_mac, gap=th.SPACE_SM, alignment="center")

            bar_dram_lbl = self._label("DRAM  200 pJ", th.RED_LIGHT, 12, BOLD)
            bar_dram = RoundedRectangle(corner_radius=0.04, width=dram_w, height=0.28, stroke_color=th.RED, fill_color=th.RED, fill_opacity=0.9)
            row_dram = HStack(bar_dram_lbl, bar_dram, gap=th.SPACE_SM, alignment="center")

            ratio = self._label("200 / 0.2  =  1,000×", th.WHITE, 16, BOLD)
            power_eq = Text("P = α · C · V² · f", font=th.MONO, font_size=15, color=th.AMBER_LIGHT)
            eq_sub = self._label("Same activity and voltage. A longer wire means a larger C.", th.MUTED, 10)
            energy_chart = VGroup(bar_header, row_mac, row_dram, ratio, power_eq, eq_sub).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
            chart_card = th.card(5.8, 3.6, stroke=th.BORDER)
            energy_chart.move_to(chart_card)
            chart_panel = VGroup(chart_card, energy_chart)

            st.columns(wire_comparison, chart_panel, gap=th.SPACE_LG)
            t = self._enter(st, wire_comparison, chart_panel, run_time=0.8)
            self._say(st, n0, anim_time=t)

            # Animate charge surging across PCB trace & screen shake
            flash_trace = ShowPassingFlash(trace_long.copy().set_color(th.WHITE).set_stroke(width=6.0), time_width=0.4, run_time=0.6)
            self.play(flash_trace, caps.animate.set_color(th.RED_LIGHT))
            self._say(st, n1, anim_time=0.6)

            # Highlight energy equation
            self.play(Indicate(power_eq, color=th.WHITE, scale_factor=1.15), run_time=0.5)
            self._say(st, n2, anim_time=0.5)
            st.takeaway("Compute is virtually free. Moving data across wires is what sets chips on fire.", wait=1.3)

    # =====================================================================
    # ACT 3: Wires vs Registers (Dual Oscilloscope & Metastability)
    # =====================================================================
    def play_act3_wires_vs_registers(self):
        n0 = "A combinational gate is an Excel formula: change an input, the output updates immediately. It has no memory."
        n1 = "A D flip-flop is a snapshot. On the rising clock edge it samples D and freezes it at Q until the next tick."
        n2 = "Data must be stable just before the edge, and stay stable just after. If it is still changing, you capture garbage — like reading a dict while another thread writes it."
        with self.stage(
            "ACT 3",
            "Wires Compute. Registers Remember.",
            "Live spreadsheet formulas vs. metronome snapshots",
            narration=n0,
        ) as st:
            # Left: D-Flip-Flop Standard Cell
            dff = DFlipFlopNode(name="D FLIP-FLOP", val="0", width=2.4, height=3.2, color=th.CYAN)
            analog = VGroup(
                self._label("SOFTWARE ANALOG", th.MUTED, 11, BOLD),
                self._label("wire  = live formula", th.TEXT, 12),
                self._label("flop  = photo on posedge", th.GREEN_LIGHT, 12),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            left_col = VGroup(dff, analog).arrange(DOWN, buff=0.22)

            # Right: Dual-Trace Digital Oscilloscope
            osc_bg = RoundedRectangle(
                corner_radius=0.12, width=6.6, height=3.7,
                stroke_color=th.BORDER, stroke_width=1.5,
                fill_color="#090e17", fill_opacity=0.95,
            )
            osc_title = self._label("DUAL-CHANNEL LOGIC ANALYZER", th.MUTED, 11, BOLD).next_to(osc_bg.get_top(), DOWN, buff=0.12)

            # Channel 1: Clock Square Wave
            cx = osc_bg.get_center()[0] + 0.3
            cy_clk = osc_bg.get_center()[1] + 0.75
            w_span = 4.8
            x_start = cx - w_span / 2
            
            clk_pts = [
                np.array([x_start, cy_clk - 0.25, 0]),
                np.array([x_start + 1.2, cy_clk - 0.25, 0]),
                np.array([x_start + 1.2, cy_clk + 0.25, 0]),  # RISING EDGE 1
                np.array([x_start + 2.4, cy_clk + 0.25, 0]),
                np.array([x_start + 2.4, cy_clk - 0.25, 0]),
                np.array([x_start + 3.6, cy_clk - 0.25, 0]),
                np.array([x_start + 3.6, cy_clk + 0.25, 0]),  # RISING EDGE 2
                np.array([x_start + 4.8, cy_clk + 0.25, 0]),
            ]
            clk_wave = VMobject(color=th.AMBER, stroke_width=2.5).set_points_as_corners(clk_pts)
            clk_tag = self._label("CLK", th.AMBER, 11, BOLD).move_to(np.array([x_start - 0.45, cy_clk, 0]))

            # Rising edge reference X
            edge1_x = x_start + 1.2

            # Setup & Hold Windows (Shaded Apertures)
            setup_aperture = Rectangle(
                width=0.7, height=2.4, stroke_color=th.GREEN, stroke_width=1.0,
                fill_color=th.GREEN, fill_opacity=0.20,
            ).move_to(np.array([edge1_x - 0.35, osc_bg.get_center()[1] - 0.15, 0]))
            setup_lbl = self._label("t_setup", th.GREEN_LIGHT, 10).next_to(setup_aperture, DOWN, buff=0.05)

            hold_aperture = Rectangle(
                width=0.5, height=2.4, stroke_color=th.CYAN, stroke_width=1.0,
                fill_color=th.CYAN, fill_opacity=0.20,
            ).move_to(np.array([edge1_x + 0.25, osc_bg.get_center()[1] - 0.15, 0]))
            hold_lbl = self._label("t_hold", th.CYAN_LIGHT, 10).next_to(hold_aperture, DOWN, buff=0.05)

            # Channel 2: Data Signal D (Transitions CLEANLY before setup aperture)
            cy_d = osc_bg.get_center()[1] - 0.65
            d_pts_clean = [
                np.array([x_start, cy_d - 0.25, 0]),
                np.array([edge1_x - 1.0, cy_d - 0.25, 0]),
                np.array([edge1_x - 0.8, cy_d + 0.25, 0]),  # Transitions well ahead of setup!
                np.array([x_start + 4.8, cy_d + 0.25, 0]),
            ]
            d_wave = VMobject(color=th.CYAN_LIGHT, stroke_width=2.8).set_points_as_corners(d_pts_clean)
            d_tag = self._label("DATA (D)", th.CYAN_LIGHT, 11, BOLD).move_to(np.array([x_start - 0.55, cy_d, 0]))

            osc_group = VGroup(
                osc_bg, osc_title, clk_wave, clk_tag,
                setup_aperture, setup_lbl, hold_aperture, hold_lbl,
                d_wave, d_tag,
            )
            scope_top = osc_bg.get_top()[1]
            scope_bottom = osc_bg.get_bottom()[1]
            scope_before = snapshot(osc_group)

            body, foot = st.content.split_y(1, 0.16, gap=th.SPACE_XS)
            st.columns(left_col, osc_group, weights=(0.85, 1.2), gap=th.SPACE_MD, region=body)

            t = self._enter(st, left_col, osc_group, run_time=0.9)
            self._say(st, n0, anim_time=t)

            # 1. Clean Sampling Animation
            self.clock.advance(self, delta_cycles=1, run_time=0.3)
            scan_beam = Line(
                map_point(scope_before, osc_group, np.array([edge1_x, scope_top - 0.3, 0])),
                map_point(scope_before, osc_group, np.array([edge1_x, scope_bottom + 0.3, 0])),
                color=th.WHITE, stroke_width=3.2,
            )
            self.play(ShowPassingFlash(scan_beam, time_width=0.35, run_time=0.6))
            self.play(dff.set_value("1", color=th.GREEN_LIGHT), run_time=0.35)
            self._say(st, n1, anim_time=1.25)

            # 2. Metastability Violation Animation (Data toggles directly INSIDE setup aperture!)
            d_pts_violation = [
                np.array([x_start, cy_d - 0.25, 0]),
                np.array([edge1_x - 0.3, cy_d - 0.25, 0]),
                np.array([edge1_x - 0.05, cy_d + 0.05, 0]), # Toggles directly inside setup window!
                # Analog Metastability Wobble near VDD/2 (0.0V mid-rail)
                np.array([edge1_x + 0.2, cy_d + 0.08, 0]),
                np.array([edge1_x + 0.4, cy_d - 0.06, 0]),
                np.array([edge1_x + 0.7, cy_d + 0.05, 0]),
                np.array([edge1_x + 1.0, cy_d - 0.25, 0]), # Collapses unpredictably
                np.array([x_start + 4.8, cy_d - 0.25, 0]),
            ]
            bad_d_wave = VMobject(color=th.RED, stroke_width=3.0).set_points_as_corners(
                [map_point(scope_before, osc_group, p) for p in d_pts_violation]
            )

            warn_box = self._label("METASTABILITY: DATA TOGGLES IN SETUP WINDOW!", th.RED, 12, BOLD)
            st.place(warn_box, foot)
            st.register(warn_box)

            self.play(
                Transform(d_wave, bad_d_wave),
                setup_aperture.animate.set_fill(color=th.RED, opacity=0.45).set_stroke(color=th.RED, width=2.5),
                Write(warn_box),
                run_time=0.8,
            )
            self.play(dff.set_value("X?", color=th.RED_LIGHT), run_time=0.4)
            self._say(st, n2, anim_time=1.45)
            st.takeaway("Setup and Hold are laws of physics. Violate them and your register flips a coin.", wait=1.2)

    # =====================================================================
    # ACT 4: = vs <= (Pipeline Preservation vs Synthesizer Dissolve)
    # =====================================================================
    def play_act4_assign_vs_unpack(self):
        n0 = "The number-one RTL bug for software people: blocking equals versus non-blocking less-than-equals."
        n1 = "Blocking assignment is ordinary Python: b equals a, then c equals b. C sees the new B. A two-stage pipeline collapses into a wire."
        n2 = "Non-blocking is tuple unpack: b, c equals a, b. Both right-hand sides are the old values. The pipeline survives the clock tick."
        with self.stage(
            "ACT 4",
            "Assignment vs Unpack",
            "b = a; c = b    vs    b, c = a, b",
            narration=n0,
        ) as st:
            left_code = th.code_window(
                [
                    ("# Python analog", th.MUTED),
                    ("b = a", th.TEXT),
                    ("c = b          # sees NEW b", th.RED_LIGHT),
                    ("# RTL: b = a; c = b;", th.MUTED),
                ],
                title_text="BLOCKING  =   (COLLAPSE)",
                width=5.2, height=2.3, font_size=12, title_color=th.RED,
            )
            right_code = th.code_window(
                [
                    ("# Python analog", th.MUTED),
                    ("b, c = a, b    # old values", th.GREEN_LIGHT),
                    ("# RTL:", th.MUTED),
                    ("b <= a;  c <= b;", th.TEXT),
                ],
                title_text="NON-BLOCKING  <=   (PIPELINE)",
                width=5.2, height=2.3, font_size=12, title_color=th.GREEN,
            )
            code_band, schem_band = st.content.split_y(1, 1, gap=th.SPACE_SM)
            code_pair = HStack(left_code, right_code, gap=th.SPACE_LG)
            st.place(code_pair, code_band)
            t = self._enter(st, code_pair, run_time=0.8)
            self._say(st, n0, anim_time=t)

            # Left: Broken Blocking Hardware
            b_reg_a = DFlipFlopNode(name="REG A", val="10", width=1.1, height=1.45, color=th.CYAN, has_leads=False)
            b_reg_b = DFlipFlopNode(name="REG B", val="20", width=1.1, height=1.45, color=th.RED, has_leads=False)
            b_reg_c = DFlipFlopNode(name="REG C", val="30", width=1.1, height=1.45, color=th.RED, has_leads=False)
            b_chain = HStack(b_reg_a, b_reg_b, b_reg_c, gap=0.35)
            b_w1 = Arrow(b_reg_a.chassis.get_right(), b_reg_b.chassis.get_left(), buff=0.04, color=th.RED, stroke_width=2.0)
            b_w2 = Arrow(b_reg_b.chassis.get_right(), b_reg_c.chassis.get_left(), buff=0.04, color=th.RED, stroke_width=2.0)
            b_tag = self._label("BLOCKING: B and C both take 10", th.RED_LIGHT, 11, BOLD)
            left_schem = VGroup(VGroup(b_chain, b_w1, b_w2), b_tag).arrange(DOWN, buff=0.12)

            # Right: Correct Non-Blocking Pipeline
            nb_reg_a = DFlipFlopNode(name="REG A", val="10", width=1.1, height=1.45, color=th.CYAN, has_leads=False)
            nb_reg_b = DFlipFlopNode(name="REG B", val="20", width=1.1, height=1.45, color=th.GREEN, has_leads=False)
            nb_reg_c = DFlipFlopNode(name="REG C", val="30", width=1.1, height=1.45, color=th.GREEN, has_leads=False)
            nb_chain = HStack(nb_reg_a, nb_reg_b, nb_reg_c, gap=0.35)
            nb_w1 = Arrow(nb_reg_a.chassis.get_right(), nb_reg_b.chassis.get_left(), buff=0.04, color=th.GREEN, stroke_width=2.0)
            nb_w2 = Arrow(nb_reg_b.chassis.get_right(), nb_reg_c.chassis.get_left(), buff=0.04, color=th.GREEN, stroke_width=2.0)
            nb_tag = self._label("PIPELINE PRESERVED: 10, 10, 20", th.GREEN_LIGHT, 11, BOLD)
            right_schem = VGroup(VGroup(nb_chain, nb_w1, nb_w2), nb_tag).arrange(DOWN, buff=0.12)

            schem_pair = HStack(left_schem, right_schem, gap=th.SPACE_XL)
            st.place(schem_pair, schem_band)

            t = self._enter(st, schem_pair, run_time=0.7)
            self._say(st, n1, anim_time=t)

            # One clock edge. Blocking copies the new B into C. Non-blocking keeps the old B.
            # B stays a register in both pictures; synthesis does not delete it in this example,
            # because B is still an observed pipeline stage.
            self.clock.advance(self, delta_cycles=1, run_time=0.3)
            self.play(
                b_reg_b.set_value("10", color=th.RED_LIGHT),
                b_reg_c.set_value("10", color=th.RED_LIGHT),
                nb_reg_b.set_value("10", color=th.GREEN_LIGHT),
                nb_reg_c.set_value("20", color=th.GREEN_LIGHT),
                run_time=0.9,
            )
            self._say(st, n2, anim_time=1.4)
            st.takeaway("always_comb gets '='. always_ff gets '<='. Think: sequential vs tuple unpack.", wait=1.3)

    # =====================================================================
    # ACT 5: Host to Device (Ring Buffer, MMIO Doorbell & Ping-Pong SRAM)
    # =====================================================================
    def play_act5_host_to_device(self):
        n0 = "When you call torch.matmul, the CPU is not doing the multiply. It writes a small descriptor, then rings one memory-mapped register: a doorbell."
        n1 = "That write wakes a DMA engine. Tensors stream over PCIe into on-chip SRAM while Python keeps running."
        n2 = "Double buffering is the hardware version of ping-pong queues: one SRAM bank feeds the array while the other fills from the bus."
        with self.stage(
            "ACT 5",
            "How a Tensor Reaches Silicon",
            "Python writes a doorbell. DMA owns the copy.",
            narration=n0,
        ) as st:
            # 1. Host Memory Circular Ring Buffer Visual
            host_card = th.card(3.6, 3.4, stroke=th.AMBER)
            host_title = self._label("HOST RING BUFFER", th.AMBER, 11, BOLD).next_to(host_card.get_top(), DOWN, buff=0.12)
            
            # Ring buffer circle with slots
            ring_center = host_card.get_center() + DOWN * 0.2
            ring_circle = Circle(radius=0.85, color=th.BORDER, stroke_width=2.0).move_to(ring_center)
            slots = VGroup()
            for angle in np.linspace(0, 2*np.pi, 6, endpoint=False):
                slot_dot = Dot(ring_center + np.array([np.cos(angle), np.sin(angle), 0]) * 0.85, radius=0.10, color=th.AMBER_DARK)
                slots.add(slot_dot)
            head_ptr = Arrow(ring_center, ring_center + UP * 0.65, buff=0, color=th.CYAN, stroke_width=2.2, max_tip_length_to_length_ratio=0.25)
            tail_ptr = Arrow(ring_center, ring_center + RIGHT * 0.65, buff=0, color=th.AMBER_LIGHT, stroke_width=2.2, max_tip_length_to_length_ratio=0.25)
            ring_lbl = self._label("Descriptor Queue", th.MUTED, 10).next_to(ring_circle, DOWN, buff=0.10)
            host_panel = VGroup(host_card, host_title, ring_circle, slots, head_ptr, tail_ptr, ring_lbl)

            # 2. PCIe Gen5 Bus & MMIO Doorbell Register
            pcie_card = th.card(3.2, 3.4, stroke=th.CYAN)
            pcie_title = self._label("PCIe GEN5 BUS", th.CYAN, 11, BOLD).next_to(pcie_card.get_top(), DOWN, buff=0.12)
            
            doorbell_box = RoundedRectangle(corner_radius=0.08, width=2.4, height=0.75, stroke_color=th.AMBER_LIGHT, stroke_width=2.0, fill_color="#2b1a05", fill_opacity=0.92)
            doorbell_box.move_to(pcie_card.get_center() + UP * 0.45)
            doorbell_addr = self._label("0x4000_0000", th.AMBER_LIGHT, 11, BOLD)
            doorbell_name = self._label("MMIO DOORBELL", th.WHITE, 10)
            doorbell_sub = VStack(doorbell_addr, doorbell_name, gap=0.04).move_to(doorbell_box)

            dma_engine = RoundedRectangle(corner_radius=0.08, width=2.4, height=0.75, stroke_color=th.CYAN, stroke_width=2.0, fill_color="#081827", fill_opacity=0.92)
            dma_engine.move_to(pcie_card.get_center() + DOWN * 0.55)
            dma_name = self._label("DMA CONTROLLER", th.CYAN_LIGHT, 11, BOLD)
            dma_stat = self._label("64 GB/s Stream", th.MUTED, 10)
            dma_sub = VStack(dma_name, dma_stat, gap=0.04).move_to(dma_engine)

            pcie_panel = VGroup(pcie_card, pcie_title, doorbell_box, doorbell_sub, dma_engine, dma_sub)

            # 3. Accelerator Double-Buffered SRAM (Ping-Pong Banks)
            acc_card = th.card(3.6, 3.4, stroke=th.GREEN)
            acc_title = self._label("ACCELERATOR ON-CHIP", th.GREEN, 11, BOLD).next_to(acc_card.get_top(), DOWN, buff=0.12)

            bank_a = RoundedRectangle(corner_radius=0.08, width=2.6, height=0.75, stroke_color=th.GREEN, stroke_width=2.0, fill_color="#072213", fill_opacity=0.92)
            bank_a.move_to(acc_card.get_center() + UP * 0.45)
            ba_txt = self._label("SRAM BANK A: COMPUTE", th.GREEN_LIGHT, 10, BOLD)
            ba_sub = self._label("Feeding Systolic PEs", th.WHITE, 9)
            bank_a_group = VGroup(bank_a, VStack(ba_txt, ba_sub, gap=0.04).move_to(bank_a))

            bank_b = RoundedRectangle(corner_radius=0.08, width=2.6, height=0.75, stroke_color=th.CYAN, stroke_width=2.0, fill_color="#091d2d", fill_opacity=0.92)
            bank_b.move_to(acc_card.get_center() + DOWN * 0.55)
            bb_txt = self._label("SRAM BANK B: DMA LOAD", th.CYAN_LIGHT, 10, BOLD)
            bb_sub = self._label("Filling from PCIe Bus", th.MUTED, 9)
            bank_b_group = VGroup(bank_b, VStack(bb_txt, bb_sub, gap=0.04).move_to(bank_b))

            acc_panel = VGroup(acc_card, acc_title, bank_a_group, bank_b_group)
            st.columns(host_panel, pcie_panel, acc_panel, gap=th.SPACE_SM)

            t = self._enter(st, host_panel, pcie_panel, acc_panel, run_time=0.9)
            self._say(st, n0, anim_time=t)

            # Four values leave the host ring, cross the doorbell, and land in bank B.
            values = ["1", "2", "3", "4"]
            packets = VGroup()
            for i, (val, slot) in enumerate(zip(values, slots)):
                token = VGroup(
                    Dot(slot.get_center(), radius=0.12, color=th.AMBER_LIGHT),
                    self._label(val, th.WHITE, 10, BOLD).move_to(slot),
                )
                packets.add(token)
            st.register(packets)
            self.play(FadeIn(packets), run_time=0.3)
            self.play(
                Indicate(doorbell_box, color=th.WHITE, scale_factor=1.08),
                packets[0].animate.move_to(doorbell_box.get_center()),
                run_time=0.45,
            )
            self.play(
                LaggedStart(*[
                    pkt.animate.move_to(bank_b.get_center() + RIGHT * ((i - 1.5) * 0.35))
                    for i, pkt in enumerate(packets)
                ], lag_ratio=0.18),
                bank_b.animate.set_stroke(color=th.WHITE, width=3.2),
                run_time=1.1,
            )
            self.play(bank_b.animate.set_stroke(color=th.CYAN, width=2.0), run_time=0.2)
            self._say(st, n1, anim_time=1.6)

            # Roles swap in place. The silicon does not move; the job of each bank does.
            ba_next = self._label("SRAM BANK A: DMA LOAD", th.CYAN_LIGHT, 10, BOLD).move_to(ba_txt)
            bb_next = self._label("SRAM BANK B: COMPUTE", th.GREEN_LIGHT, 10, BOLD).move_to(bb_txt)
            self.play(
                Transform(ba_txt, ba_next),
                Transform(bb_txt, bb_next),
                bank_a.animate.set_stroke(color=th.CYAN, width=2.0),
                bank_b.animate.set_stroke(color=th.GREEN, width=2.0),
                run_time=0.7,
            )
            self._say(st, n2, anim_time=1.2)
            st.takeaway("One register write launches gigabytes of DMA. The CPU never sits waiting on wires.", wait=1.2)

    # =====================================================================
    # ACT 6: Pytest for Silicon (Live Python Cocotb Driving Physical Pins)
    # =====================================================================
    def play_act6_simulate_before_fab(self):
        n0 = "You cannot git revert a chip. A tape-out is tens of millions of dollars. So we test the design as software first."
        n1 = "Cocotb drives the pins from Python. This adder is combinational, so the sum updates with no clock edge."
        n2 = "Carry three rules into every lab: the circuit is a live graph, clocked state uses less-than-equals, and moving data costs more than math."
        with self.stage(
            "ACT 6",
            "Pytest for Silicon",
            "Simulate the wires before you pay the foundry.",
            narration=n0,
        ) as st:
            # Left: Interactive Python Cocotb Test Terminal
            py_code = th.code_window(
                [
                    ("@cocotb.test()", th.MUTED),
                    ("async def test_adder(dut):", th.TEXT),
                    ("    dut.a.value = 10", th.TEXT),
                    ("    dut.b.value = 20", th.TEXT),
                    ("    await RisingEdge(dut.clk)", th.CYAN_LIGHT),
                    ("    assert dut.sum.value == 30", th.GREEN_LIGHT),
                ],
                title_text="PYTHON COCOTB  (test_adder.py)",
                width=5.4, height=3.3, font_size=12, title_color=th.CYAN,
            )

            # Right: Synthesizable Hardware Adder Standard Cell
            dut_box = RoundedRectangle(corner_radius=0.12, width=4.8, height=3.3, stroke_color=th.GREEN, stroke_width=2.0, fill_color="#071b11", fill_opacity=0.92)
            dut_title = self._label("SYSTEMVERILOG SILICON (adder.sv)", th.GREEN, 11, BOLD).next_to(dut_box.get_top(), DOWN, buff=0.12)
            
            # Adder internal core & pins
            add_core = self._op_node("+", "ADDER CORE", th.GREEN, radius=0.48).move_to(dut_box.get_center() + RIGHT * 0.4)
            pin_a = self._label("pin a  [8b]", th.CYAN_LIGHT, 10).move_to(dut_box.get_left() + RIGHT * 0.8 + UP * 0.6)
            pin_b = self._label("pin b  [8b]", th.AMBER_LIGHT, 10).move_to(dut_box.get_left() + RIGHT * 0.8 + DOWN * 0.1)
            pin_sum = self._label("pin sum [8b] = 30", th.GREEN_LIGHT, 11, BOLD).move_to(dut_box.get_bottom() + UP * 0.35)

            dut_panel = VGroup(dut_box, dut_title, add_core, pin_a, pin_b, pin_sum)
            body, foot = st.content.split_y(1, 0.16, gap=th.SPACE_XS)
            lab_pair = HStack(py_code, dut_panel, gap=th.SPACE_LG)
            st.place(lab_pair, body)
            # Wires after the layout pass, so they meet the pins where they landed.
            wire_a = Line(
                np.array([py_code.get_right()[0], pin_a.get_center()[1], 0]),
                pin_a.get_left(),
                color=th.CYAN, stroke_width=2.2,
            )
            wire_b = Line(
                np.array([py_code.get_right()[0], pin_b.get_center()[1], 0]),
                pin_b.get_left(),
                color=th.AMBER, stroke_width=2.2,
            )

            t = self._enter(st, lab_pair, wire_a, wire_b, run_time=0.9)
            self._say(st, n0, anim_time=t)

            # Step 1: Drive Pin A
            flash_a = ShowPassingFlash(wire_a.copy().set_color(th.WHITE).set_stroke(width=5.0), time_width=0.4, run_time=0.5)
            self.play(flash_a, pin_a.animate.set_color(th.WHITE))
            self.play(pin_a.animate.set_color(th.CYAN_LIGHT), run_time=0.2)

            # Step 2: Drive Pin B
            flash_b = ShowPassingFlash(wire_b.copy().set_color(th.WHITE).set_stroke(width=5.0), time_width=0.4, run_time=0.5)
            self.play(flash_b, pin_b.animate.set_color(th.WHITE))
            self.play(pin_b.animate.set_color(th.AMBER_LIGHT), run_time=0.2)

            # Combinational: the sum appears without a clock edge.
            self.play(
                add_core.circle.animate.set_stroke(color=th.WHITE, width=4.0),
                pin_sum.animate.set_color(th.WHITE).scale(1.1),
                run_time=0.55,
            )
            self.play(
                add_core.circle.animate.set_stroke(color=th.GREEN, width=2.5),
                pin_sum.animate.set_color(th.GREEN_LIGHT).scale(1/1.1),
                run_time=0.25,
            )
            self._say(st, n1, anim_time=2.1)

            # Step 4: Verification Passed Badge
            badge_bg = RoundedRectangle(corner_radius=0.08, width=3.6, height=0.45, stroke_color=th.GREEN, fill_color="#072213", fill_opacity=0.94)
            badge_txt = self._label("assert sum == 30   passed", th.GREEN_LIGHT, 12, BOLD).move_to(badge_bg)
            badge = VGroup(badge_bg, badge_txt)
            st.place(badge, foot)
            st.register(badge)
            self.play(FadeIn(badge, scale=1.1), run_time=0.5)
            self._say(st, n2, anim_time=0.5)
            st.takeaway("A bug caught in Python Cocotb takes seconds. A bug caught in silicon costs $50M.", wait=1.5)
