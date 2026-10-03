"""
Lab 00-Prep: Hardware Thinking Primer for Software & AI Engineers

Goal: give a Python/PyTorch engineer a working mental model of silicon
*before* Lab 00 arithmetic. Each act maps one software habit onto one
hardware constraint, then proves it with a small visual experiment.

Act map:
  0  Recipe vs machine     — a function is a script; a chip is a factory
  1  No program counter    — CPU walks a list; silicon is a live dataflow graph
  2  Memory energy wall    — `a*b` looks as cheap as `arr[i]`. It is not.
  3  Wires vs registers    — spreadsheet formulas vs a snapshot on a metronome
  4  = vs <=               — sequential assign vs Python tuple-unpack
  5  Host to device        — torch.matmul is a doorbell + DMA, not CPU math
  6  Simulate before fab   — cocotb is pytest for wires
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
    HStack,
    VStack,
    fit_to_bounds,
)


class Lab00PrepPrimer(KineticSiliconScene):
    """Software-first hardware primer. Beat-paced, layout-driven, no LaTeX."""

    def construct(self):
        self.clock = KineticClock(initial_cycle=0)
        self.ticker = self.clock.create_ticker_badge(prefix="CLK T=", color=th.CYAN_LIGHT)
        self.ticker.scale(0.82)
        self.ticker.to_corner(UR, buff=0.22)
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
    # Scene helpers: register-then-reveal, banner beats, compact nodes
    # ------------------------------------------------------------------
    def _enter(self, st, *mobs, shift=UP * 0.12, run_time=0.7):
        """Register for stage cleanup, then FadeIn (never scene.add first)."""
        st.register(*mobs)
        self.play(*[FadeIn(m, shift=shift) for m in mobs if m is not None], run_time=run_time)
        return run_time

    def _say(self, st, line, anim_time=0.0):
        """Swap the bottom banner and wait out the spoken line."""
        if st.narration != line:
            st.update_narration(line, run_time=0.35)
            anim_time += 0.35
        dur = VoiceoverTracker(line).duration
        self.wait(max(0.25, dur - anim_time))

    def _op_node(self, symbol, title, color, radius=0.52):
        """Logic-op bubble that does not depend on LaTeX/MathTex."""
        circle = Circle(
            radius=radius, color=color, stroke_width=2.5,
            fill_color="#072213", fill_opacity=0.92,
        )
        sym = Text(symbol, font=th.MONO, weight=BOLD, font_size=26, color=th.WHITE)
        sym.move_to(circle)
        title_lbl = Text(title, font=th.MONO, font_size=11, color=color)
        title_lbl.next_to(circle, UP, buff=0.08)
        in1 = Line(
            circle.get_left() + UP * 0.26 + LEFT * 0.62,
            circle.get_left() + UP * 0.26,
            color=th.CYAN, stroke_width=2.2,
        )
        in2 = Line(
            circle.get_left() + DOWN * 0.26 + LEFT * 0.62,
            circle.get_left() + DOWN * 0.26,
            color=th.CYAN, stroke_width=2.2,
        )
        out = Line(
            circle.get_right(),
            circle.get_right() + RIGHT * 0.62,
            color=th.AMBER, stroke_width=2.2,
        )
        node = VGroup(circle, sym, title_lbl, in1, in2, out)
        node.circle = circle
        return node

    def _label(self, text, color=th.MUTED, size=12, weight=NORMAL):
        return Text(text, font=th.MONO, weight=weight, font_size=size, color=color)

    # =====================================================================
    # TITLE
    # =====================================================================
    def play_title(self):
        line = "You think in time: one line, then the next. A chip thinks in space: the circuit is always there."
        with self.stage(
            "LAB 00-PREP",
            "Hardware thinking for software engineers",
            "A Python dictionary for silicon",
            narration=line,
        ) as st:
            cards = HStack(
                th.metric_card("TIME", "Software", "PC walks a script", color=th.AMBER, width=3.5, height=1.7),
                th.metric_card("SPACE", "Hardware", "Gates wired in place", color=th.CYAN, width=3.5, height=1.7),
                th.metric_card("COST", "Why it matters", "Data movement >> math", color=th.GREEN, width=3.5, height=1.7),
                gap=th.SPACE_MD,
            )
            cards.move_to(self.layout.main_stage_center() + DOWN * 0.15)
            t = self._enter(st, cards, run_time=0.9)
            self._say(st, line, anim_time=t)
            st.takeaway("This primer is the map from Python habits to chip constraints.", wait=1.2)

    # =====================================================================
    # ACT 0: RECIPE VS MACHINE
    # =====================================================================
    def play_act0_recipe_vs_machine(self):
        n0 = "In Python, a function is a recipe: the CPU fetches one instruction, does it, then fetches the next."
        n1 = "A chip is not a recipe. The adders and the multiplier are physical objects sitting on the die at the same time."
        n2 = "Same math. Two machines. One walks a list. The other is the list, wired in metal."
        with self.stage(
            "ACT 0",
            "Recipe vs machine",
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
                width=5.2, height=2.8, font_size=14, title_color=th.AMBER,
            )
            pointer = Triangle(color=th.AMBER_LIGHT, fill_opacity=1.0).scale(0.1).rotate(-PI / 2)

            add1 = self._op_node("+", "ADDER", th.CYAN, radius=0.42)
            add2 = self._op_node("+", "ADDER", th.AMBER, radius=0.42)
            mul = self._op_node("×", "MUL", th.GREEN, radius=0.46)
            add1.move_to(UP * 0.55 + LEFT * 0.85)
            add2.move_to(UP * 0.55 + RIGHT * 0.85)
            mul.move_to(DOWN * 0.85)
            w1 = Arrow(add1.circle.get_bottom(), mul.circle.get_top() + LEFT * 0.22, buff=0.06, color=th.CYAN, stroke_width=2.2)
            w2 = Arrow(add2.circle.get_bottom(), mul.circle.get_top() + RIGHT * 0.22, buff=0.06, color=th.AMBER, stroke_width=2.2)
            hw_title = self._label("SILICON  —  MACHINE", th.CYAN, 13, BOLD)
            hw = VGroup(hw_title, VGroup(add1, add2, mul, w1, w2)).arrange(DOWN, buff=0.18)
            hw_box = th.card(5.2, 3.4, stroke=th.CYAN)
            hw.move_to(hw_box)
            hw_panel = VGroup(hw_box, hw)

            pair = HStack(py, hw_panel, gap=th.SPACE_LG)
            pair.move_to(self.layout.main_stage_center() + DOWN * 0.1)
            fit_to_bounds(pair, max_width=12.2, max_height=4.4)

            # Re-attach pointer after layout (py is now in place)
            pointer.next_to(py, LEFT, buff=0.12)
            pointer.align_to(py, UP).shift(DOWN * 1.05)

            t = self._enter(st, pair, run_time=0.8)
            st.register(pointer)
            self.play(FadeIn(pointer), run_time=0.3)
            self._say(st, n0, anim_time=t + 0.3)

            t = 0.7
            self.play(
                pointer.animate.shift(DOWN * 0.42),
                run_time=t,
            )
            self._say(st, n1, anim_time=t)

            self.play(
                add1.circle.animate.set_stroke(color=th.WHITE, width=4.0),
                add2.circle.animate.set_stroke(color=th.WHITE, width=4.0),
                run_time=0.5,
            )
            tok_a = Dot(radius=0.09, color=th.CYAN_LIGHT).move_to(add1.circle)
            tok_b = Dot(radius=0.09, color=th.AMBER_LIGHT).move_to(add2.circle)
            st.register(tok_a, tok_b)
            self.play(
                tok_a.animate.move_to(mul.circle.get_center() + LEFT * 0.15),
                tok_b.animate.move_to(mul.circle.get_center() + RIGHT * 0.15),
                mul.circle.animate.set_stroke(color=th.WHITE, width=4.0),
                run_time=0.7,
            )
            self.play(FadeOut(tok_a), FadeOut(tok_b), run_time=0.2)
            self._say(st, n2, anim_time=1.4)
            st.takeaway("Software describes steps. Hardware is the steps, sitting in space.", wait=1.2)

    # =====================================================================
    # ACT 1: NO PROGRAM COUNTER
    # =====================================================================
    def play_act1_no_program_counter(self):
        n0 = "To compute y = (a+b) times (c+d), a CPU spends three sequential cycles. A program counter points at one line."
        n1 = "Silicon has no program counter. Both adders exist, so both adds happen in the same moment of physics."
        n2 = "This is not threading. You did not spawn workers. You placed two adders on the die, the way you would instantiate two objects."
        with self.stage(
            "ACT 1",
            "There is no program counter",
            "A CPU walks a list. A chip is a live graph.",
            narration=n0,
        ) as st:
            eq = Text("y  =  (a + b)  ×  (c + d)", font=th.MONO, weight=BOLD, font_size=26, color=th.WHITE)
            eq.move_to(self.layout.main_stage_center() + UP * 1.55)
            fit_to_bounds(eq, max_width=10.5)
            t0 = self._enter(st, eq, shift=DOWN * 0.1, run_time=0.5)

            cpu_title = self._label("CPU  ·  3 CYCLES", th.AMBER, 12, BOLD)
            lines = [
                "t1 = a + b     # cycle 1",
                "t2 = c + d     # cycle 2",
                "y  = t1 * t2   # cycle 3",
            ]
            cpu_rows = VGroup()
            for src in lines:
                box = RoundedRectangle(
                    corner_radius=0.08, width=4.4, height=0.48,
                    stroke_color=th.BORDER, stroke_width=1.4,
                    fill_color="#0e1526", fill_opacity=0.94,
                )
                txt = Text(src, font=th.MONO, font_size=13, color=th.TEXT).move_to(box)
                cpu_rows.add(VGroup(box, txt))
            cpu_rows.arrange(DOWN, buff=0.1)
            pc = self._label("PC →", th.AMBER_LIGHT, 12, BOLD)
            pc.next_to(cpu_rows[0], LEFT, buff=0.08)
            cpu_body = VGroup(cpu_rows, pc)
            cpu_panel = VGroup(cpu_title, cpu_body).arrange(DOWN, buff=0.16)

            hw_title = self._label("SILICON  ·  ONE GRAPH", th.CYAN, 12, BOLD)
            add1 = self._op_node("+", "a+b", th.CYAN, radius=0.4)
            add2 = self._op_node("+", "c+d", th.AMBER, radius=0.4)
            mul = self._op_node("×", "y", th.GREEN, radius=0.44)
            add1.move_to(LEFT * 1.05 + UP * 0.45)
            add2.move_to(RIGHT * 1.05 + UP * 0.45)
            mul.move_to(DOWN * 0.95)
            w1 = Arrow(add1.circle.get_bottom(), mul.circle.get_top() + LEFT * 0.2, buff=0.05, color=th.CYAN, stroke_width=2.0)
            w2 = Arrow(add2.circle.get_bottom(), mul.circle.get_top() + RIGHT * 0.2, buff=0.05, color=th.AMBER, stroke_width=2.0)
            nums = self._label("a=3  b=2     c=4  d=1", th.MUTED, 11)
            hw_g = VGroup(add1, add2, mul, w1, w2)
            hw_panel = VGroup(hw_title, hw_g, nums).arrange(DOWN, buff=0.14)

            pair = HStack(cpu_panel, hw_panel, gap=th.SPACE_XL)
            pair.move_to(self.layout.main_stage_center() + DOWN * 0.25)
            fit_to_bounds(pair, max_width=12.4, max_height=4.2)

            t1 = self._enter(st, pair, run_time=0.8)
            self._say(st, n0, anim_time=t0 + t1)

            # Cycle 1: CPU line 0, BOTH adders live
            self.play(
                cpu_rows[0][0].animate.set_stroke(color=th.AMBER, width=2.6),
                add1.circle.animate.set_stroke(color=th.WHITE, width=4.0),
                add2.circle.animate.set_stroke(color=th.WHITE, width=4.0),
                run_time=0.55,
            )
            self.clock.advance(self, delta_cycles=1, run_time=0.25)
            self._say(st, n1, anim_time=0.8)

            tok_l = Dot(radius=0.1, color=th.CYAN_LIGHT).move_to(add1.circle)
            tok_r = Dot(radius=0.1, color=th.AMBER_LIGHT).move_to(add2.circle)
            st.register(tok_l, tok_r)
            self.play(
                pc.animate.next_to(cpu_rows[1], LEFT, buff=0.08),
                cpu_rows[0][0].animate.set_stroke(color=th.BORDER, width=1.4),
                cpu_rows[1][0].animate.set_stroke(color=th.AMBER, width=2.6),
                tok_l.animate.move_to(mul.circle.get_center() + LEFT * 0.16),
                tok_r.animate.move_to(mul.circle.get_center() + RIGHT * 0.16),
                add1.circle.animate.set_stroke(color=th.CYAN, width=2.5),
                add2.circle.animate.set_stroke(color=th.AMBER, width=2.5),
                mul.circle.animate.set_stroke(color=th.WHITE, width=4.0),
                run_time=0.85,
            )
            self.play(FadeOut(tok_l), FadeOut(tok_r), run_time=0.15)
            self.clock.advance(self, delta_cycles=1, run_time=0.25)

            y_txt = self._label("y = 25", th.GREEN_LIGHT, 16, BOLD)
            y_txt.next_to(mul, DOWN, buff=0.12)
            st.register(y_txt)
            self.play(
                pc.animate.next_to(cpu_rows[2], LEFT, buff=0.08),
                cpu_rows[1][0].animate.set_stroke(color=th.BORDER, width=1.4),
                cpu_rows[2][0].animate.set_stroke(color=th.GREEN, width=2.6),
                FadeIn(y_txt, shift=UP * 0.08),
                run_time=0.7,
            )
            self.clock.advance(self, delta_cycles=1, run_time=0.25)
            self._say(st, n2, anim_time=1.2)
            st.takeaway("The CPU is an interpreter. The chip is the program, already built.", wait=1.2)

    # =====================================================================
    # ACT 2: MEMORY ENERGY WALL
    # =====================================================================
    def play_act2_memory_energy_wall(self):
        n0 = "In Python, a times b and arr of i look equally cheap. In silicon they are not even the same sport."
        n1 = "An eight-bit multiply-accumulate is about 0.2 picojoules. Fetching that byte from off-chip DRAM is about 200 picojoules — a thousand times more."
        n2 = "Longer wires hold more charge. Moving data is a physics bill. That is why AI chips hoard weights next to the math units."
        with self.stage(
            "ACT 2",
            "The memory energy wall",
            "Compute is cheap. Fetching is the invoice.",
            narration=n0,
        ) as st:
            py = th.code_window(
                [
                    ("acc += w * x          # looks free", th.GREEN_LIGHT),
                    ("w = weights[i]        # looks free", th.AMBER_LIGHT),
                    ("# hardware: fetch >> multiply", th.MUTED),
                ],
                title_text="PYTHON  —  BOTH LOOK O(1)",
                width=5.4, height=2.4, font_size=14, title_color=th.AMBER,
            )
            cards = VStack(
                th.metric_card("0.2 pJ", "INT8 MAC", "local math", color=th.GREEN, width=3.6, height=1.55),
                th.metric_card("200 pJ", "DRAM byte", "off-chip fetch", color=th.RED, width=3.6, height=1.55),
                gap=th.SPACE_SM,
            )
            top = HStack(py, cards, gap=th.SPACE_LG)
            top.move_to(self.layout.main_stage_center() + UP * 0.55)
            fit_to_bounds(top, max_width=12.2, max_height=3.2)
            t = self._enter(st, top, run_time=0.8)
            self._say(st, n0, anim_time=t)

            bar = MemoryEnergyBar(total_width=11.0)
            bar.scale(0.82)
            bar.next_to(top, DOWN, buff=0.22)
            t = self._enter(st, bar, shift=UP * 0.08, run_time=0.8)
            self.screen_shake(intensity=0.025, cycles=2, run_time=0.2)
            self._say(st, n1, anim_time=t + 0.2)

            note = self._label(
                "analogy:  multiply = a local function call     fetch = a network round-trip",
                th.MUTED, 13,
            )
            note.next_to(bar, DOWN, buff=0.12)
            fit_to_bounds(note, max_width=11.5)
            t = self._enter(st, note, run_time=0.5)
            self._say(st, n2, anim_time=t)
            st.takeaway("Do not first optimize MACs. First stop moving the same bytes.", wait=1.3)

    # =====================================================================
    # ACT 3: WIRES VS REGISTERS
    # =====================================================================
    def play_act3_wires_vs_registers(self):
        n0 = "A combinational gate is an Excel formula: change an input, the output updates immediately. It has no memory."
        n1 = "A D flip-flop is a snapshot. On the rising clock edge it samples D and freezes it at Q until the next tick."
        n2 = "Data must be stable just before the edge, and stay stable just after. If it is still changing, you capture garbage — like reading a dict while another thread writes it."
        with self.stage(
            "ACT 3",
            "Wires compute. Registers remember.",
            "Spreadsheet formulas vs a metronome snapshot",
            narration=n0,
        ) as st:
            dff = DFlipFlopNode(name="D FLIP-FLOP", val="0", width=2.2, height=2.9, color=th.CYAN)
            analog = VGroup(
                self._label("SOFTWARE ANALOG", th.MUTED, 11, BOLD),
                self._label("wire  = live formula", th.TEXT, 12),
                self._label("flop  = photo on a tick", th.TEXT, 12),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            left = VGroup(dff, analog).arrange(DOWN, buff=0.22)

            chart_bg = RoundedRectangle(
                corner_radius=0.1, width=6.2, height=3.35,
                stroke_color=th.BORDER, stroke_width=1.5,
                fill_color="#090e17", fill_opacity=0.95,
            )
            chart_title = self._label("WHEN THE CLOCK IS ALLOWED TO SAMPLE", th.MUTED, 12, BOLD)
            chart_title.next_to(chart_bg.get_top(), DOWN, buff=0.12)

            # In-card square wave (no side label — ClockWaveform would overflow the panel)
            wave_w, wave_h = 4.4, 0.55
            cx, cy = chart_bg.get_center()[0] + 0.15, chart_bg.get_center()[1] + 0.7
            x0 = cx - wave_w / 2
            pts = [
                np.array([x0, cy - wave_h / 2, 0]),
                np.array([x0 + wave_w * 0.25, cy - wave_h / 2, 0]),
                np.array([x0 + wave_w * 0.25, cy + wave_h / 2, 0]),
                np.array([x0 + wave_w * 0.5, cy + wave_h / 2, 0]),
                np.array([x0 + wave_w * 0.5, cy - wave_h / 2, 0]),
                np.array([x0 + wave_w * 0.75, cy - wave_h / 2, 0]),
                np.array([x0 + wave_w * 0.75, cy + wave_h / 2, 0]),
                np.array([x0 + wave_w, cy + wave_h / 2, 0]),
            ]
            clk = VMobject(color=th.AMBER, stroke_width=2.6)
            clk.set_points_as_corners(pts)
            clk_tag = self._label("CLK", th.AMBER, 11, BOLD)
            clk_tag.move_to(np.array([x0 - 0.38, cy, 0]))
            edge_mark = Dot(np.array([x0 + wave_w * 0.25, cy, 0]), radius=0.001, fill_opacity=0)
            setup_box = Rectangle(
                width=0.85, height=1.55, stroke_color=th.GREEN, stroke_width=1.0,
                fill_color=th.GREEN, fill_opacity=0.18,
            ).move_to(np.array([x0 + wave_w * 0.25 - 0.42, cy - 1.05, 0]))
            hold_box = Rectangle(
                width=0.55, height=1.55, stroke_color=th.CYAN, stroke_width=1.0,
                fill_color=th.CYAN, fill_opacity=0.18,
            ).move_to(np.array([x0 + wave_w * 0.25 + 0.28, cy - 1.05, 0]))
            setup_lbl = self._label("stable BEFORE  (setup)", th.GREEN_LIGHT, 10)
            hold_lbl = self._label("stable AFTER  (hold)", th.CYAN_LIGHT, 10)
            setup_lbl.next_to(setup_box, DOWN, buff=0.04)
            hold_lbl.next_to(hold_box, DOWN, buff=0.04)
            timing = VGroup(
                chart_bg, chart_title, clk, clk_tag, edge_mark,
                setup_box, hold_box, setup_lbl, hold_lbl,
            )

            pair = HStack(left, timing, gap=th.SPACE_LG)
            pair.move_to(self.layout.main_stage_center() + DOWN * 0.15)
            fit_to_bounds(pair, max_width=12.4, max_height=4.5)

            t = self._enter(st, pair, run_time=0.9)
            self._say(st, n0, anim_time=t)

            self.clock.advance(self, delta_cycles=1, run_time=0.3)
            ex = edge_mark.get_x()
            scan = Line(
                np.array([ex, chart_bg.get_top()[1] - 0.25, 0]),
                np.array([ex, chart_bg.get_bottom()[1] + 0.25, 0]),
                color=th.WHITE, stroke_width=3.0,
            )
            self.play(ShowPassingFlash(scan, time_width=0.3, run_time=0.55))
            self.play(dff.set_value("1", color=th.GREEN_LIGHT), run_time=0.35)
            self._say(st, n1, anim_time=1.2)

            warn = self._label("BAD SAMPLE: value still changing at the edge", th.RED, 13, BOLD)
            warn.next_to(pair, DOWN, buff=0.12)
            fit_to_bounds(warn, max_width=11.0)
            st.register(warn)
            self.play(
                Write(warn),
                setup_box.animate.set_fill(color=th.RED, opacity=0.4).set_stroke(color=th.RED, width=2.4),
                run_time=0.7,
            )
            self.screen_shake(intensity=0.035, cycles=3, run_time=0.22)
            self.play(dff.set_value("X?", color=th.RED_LIGHT), run_time=0.35)
            self._say(st, n2, anim_time=1.3)
            st.takeaway("Respect the sample window, or the register stores a coin-flip.", wait=1.2)

    # =====================================================================
    # ACT 4: = VS <=  (Python unpack analog)
    # =====================================================================
    def play_act4_assign_vs_unpack(self):
        n0 = "The number-one RTL bug for software people: blocking equals versus non-blocking less-than-equals."
        n1 = "Blocking assignment is ordinary Python: b equals a, then c equals b. C sees the new B. A two-stage pipeline collapses into a wire."
        n2 = "Non-blocking is tuple unpack: b, c equals a, b. Both right-hand sides are the old values. The pipeline survives the clock tick."
        with self.stage(
            "ACT 4",
            "Assignment vs unpack",
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
                title_text="BLOCKING  =   COLLAPSE",
                width=5.3, height=2.35, font_size=13, title_color=th.RED,
            )
            right_code = th.code_window(
                [
                    ("# Python analog", th.MUTED),
                    ("b, c = a, b    # old values", th.GREEN_LIGHT),
                    ("# RTL:", th.MUTED),
                    ("b <= a;  c <= b;", th.TEXT),
                ],
                title_text="NON-BLOCKING  <=   PIPELINE",
                width=5.3, height=2.35, font_size=13, title_color=th.GREEN,
            )
            codes = HStack(left_code, right_code, gap=th.SPACE_LG)
            codes.move_to(self.layout.main_stage_center() + UP * 0.95)
            fit_to_bounds(codes, max_width=12.2, max_height=2.5)
            t = self._enter(st, codes, run_time=0.8)
            self._say(st, n0, anim_time=t)

            def _mini_chain(vals, color):
                nodes = []
                for name, val in vals:
                    n = DFlipFlopNode(name=name, val=val, width=1.15, height=1.45, color=color, has_leads=False)
                    nodes.append(n)
                row = HStack(*nodes, gap=0.35)
                arrows = VGroup()
                for i in range(len(nodes) - 1):
                    arrows.add(Arrow(
                        nodes[i].chassis.get_right(),
                        nodes[i + 1].chassis.get_left(),
                        buff=0.04, color=color, stroke_width=2.2,
                    ))
                return VGroup(row, arrows), nodes

            broken, b_nodes = _mini_chain([("A", "10"), ("B", "20"), ("C", "30")], th.RED)
            good, g_nodes = _mini_chain([("A", "10"), ("B", "20"), ("C", "30")], th.GREEN)
            b_tag = self._label("after 1 tick: 10, 10, 10", th.RED_LIGHT, 11, BOLD)
            g_tag = self._label("after 1 tick: 10, 10, 20", th.GREEN_LIGHT, 11, BOLD)
            left_s = VGroup(broken, b_tag).arrange(DOWN, buff=0.12)
            right_s = VGroup(good, g_tag).arrange(DOWN, buff=0.12)
            schem = HStack(left_s, right_s, gap=th.SPACE_XL)
            schem.next_to(codes, DOWN, buff=0.22)
            fit_to_bounds(schem, max_width=12.2, max_height=2.4)
            t = self._enter(st, schem, run_time=0.7)
            self._say(st, n1, anim_time=t)

            self.clock.advance(self, delta_cycles=1, run_time=0.3)
            tok_b = Dot(radius=0.09, color=th.RED_LIGHT).move_to(b_nodes[0].val_box)
            tok_g1 = Dot(radius=0.09, color=th.CYAN_LIGHT).move_to(g_nodes[0].val_box)
            tok_g2 = Dot(radius=0.09, color=th.GREEN_LIGHT).move_to(g_nodes[1].val_box)
            st.register(tok_b, tok_g1, tok_g2)
            self.play(
                tok_b.animate.move_to(b_nodes[2].val_box),
                b_nodes[1].set_value("10", color=th.RED_LIGHT),
                b_nodes[2].set_value("10", color=th.RED_LIGHT),
                tok_g1.animate.move_to(g_nodes[1].val_box),
                tok_g2.animate.move_to(g_nodes[2].val_box),
                g_nodes[1].set_value("10", color=th.GREEN_LIGHT),
                g_nodes[2].set_value("20", color=th.GREEN_LIGHT),
                run_time=1.1,
            )
            self.play(FadeOut(tok_b), FadeOut(tok_g1), FadeOut(tok_g2), run_time=0.2)
            self._say(st, n2, anim_time=1.6)
            st.takeaway("always_comb uses '='. always_ff uses '<='. Think: sequential vs unpack.", wait=1.3)

    # =====================================================================
    # ACT 5: HOST TO DEVICE
    # =====================================================================
    def play_act5_host_to_device(self):
        n0 = "When you call torch.matmul, the CPU is not doing the multiply. It writes a small descriptor, then rings one memory-mapped register: a doorbell."
        n1 = "That write wakes a DMA engine. Tensors stream over PCIe into on-chip SRAM while Python keeps running."
        n2 = "Double buffering is the hardware version of ping-pong queues: one SRAM bank feeds the array while the other fills from the bus."
        with self.stage(
            "ACT 5",
            "How a tensor actually reaches the chip",
            "Python writes a doorbell. DMA owns the copy.",
            narration=n0,
        ) as st:
            def _box(title, lines, color, fill):
                frame = RoundedRectangle(
                    corner_radius=0.12, width=3.35, height=3.15,
                    stroke_color=color, stroke_width=2.0,
                    fill_color=fill, fill_opacity=0.93,
                )
                head = self._label(title, color, 13, BOLD)
                body = VGroup(*[self._label(ln, th.TEXT, 11) for ln in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
                inner = VStack(head, body, gap=th.SPACE_SM, alignment="left")
                inner.move_to(frame)
                return VGroup(frame, inner), frame

            host, host_f = _box(
                "HOST  CPU",
                ["1. write descriptor", "2. ring doorbell MMIO", "3. return to Python"],
                th.AMBER, "#181106",
            )
            pcie, pcie_f = _box(
                "PCIe  LINK",
                ["bulk DMA copy", "CPU does not wait", "bandwidth >> doorbell"],
                th.CYAN, "#09182a",
            )
            acc, acc_f = _box(
                "ACCELERATOR",
                ["SRAM ping / pong", "math array eats SRAM", "weights stay local"],
                th.GREEN, "#071b11",
            )
            trio = HStack(host, pcie, acc, gap=th.SPACE_MD)
            trio.move_to(self.layout.main_stage_center() + UP * 0.05)
            fit_to_bounds(trio, max_width=12.2, max_height=3.5)

            a1 = Arrow(host_f.get_right(), pcie_f.get_left(), buff=0.06, color=th.AMBER_LIGHT, stroke_width=2.8)
            a2 = Arrow(pcie_f.get_right(), acc_f.get_left(), buff=0.06, color=th.CYAN_LIGHT, stroke_width=2.8)

            t = self._enter(st, trio, a1, a2, run_time=0.9)
            self._say(st, n0, anim_time=t)

            spark = Dot(host_f.get_right(), radius=0.11, color=th.AMBER)
            st.register(spark)
            self.play(Indicate(spark, color=th.WHITE, scale_factor=1.8), run_time=0.45)

            packets = VGroup(*[
                Dot(radius=0.09, color=c)
                for c in (th.AMBER_LIGHT, th.CYAN_LIGHT, th.GREEN_LIGHT, th.CYAN_LIGHT)
            ])
            for i, pkt in enumerate(packets):
                pkt.move_to(host_f.get_right() + LEFT * (0.15 + i * 0.22))
            st.register(packets)
            self.play(
                LaggedStart(*[pkt.animate.move_to(acc_f.get_left() + RIGHT * 0.25) for pkt in packets], lag_ratio=0.2),
                acc_f.animate.set_stroke(color=th.GREEN_LIGHT, width=3.4),
                run_time=1.25,
            )
            self.clock.advance(self, delta_cycles=1, run_time=0.25)
            self._say(st, n1, anim_time=2.0)

            note = self._label("software analog:  submit a job to a queue, do not join() the copy", th.MUTED, 13)
            note.next_to(trio, DOWN, buff=0.22)
            fit_to_bounds(note, max_width=11.5)
            t = self._enter(st, note, run_time=0.45)
            self._say(st, n2, anim_time=t)
            st.takeaway("One register write can launch a bulk copy. After that, the chip owns the data.", wait=1.2)

    # =====================================================================
    # ACT 6: SIMULATE BEFORE FAB
    # =====================================================================
    def play_act6_simulate_before_fab(self):
        n0 = "You cannot git revert a chip. A tape-out is tens of millions of dollars. So we test the design as software first."
        n1 = "Cocotb is pytest for wires: your Python testbench drives SystemVerilog, waits on a clock edge, and asserts the result."
        n2 = "Carry three rules into every lab: the circuit is a live graph, clocked state uses less-than-equals, and moving data costs more than math."
        with self.stage(
            "ACT 6",
            "Pytest for silicon",
            "Simulate the wires before you pay the foundry",
            narration=n0,
        ) as st:
            py = th.code_window(
                [
                    ("@cocotb.test()", th.MUTED),
                    ("async def test_add(dut):", th.TEXT),
                    ("    dut.a.value = 10", th.TEXT),
                    ("    dut.b.value = 20", th.TEXT),
                    ("    await RisingEdge(dut.clk)", th.CYAN_LIGHT),
                    ("    assert dut.sum.value == 30", th.GREEN_LIGHT),
                ],
                title_text="PYTHON  COCOTB  (pytest for RTL)",
                width=5.6, height=3.2, font_size=13, title_color=th.CYAN,
            )
            rules = VGroup(
                th.metric_card("1", "Live graph", "gates exist together", color=th.CYAN, width=4.6, height=1.05),
                th.metric_card("2", "Clocked unpack", "always_ff uses <=", color=th.AMBER, width=4.6, height=1.05),
                th.metric_card("3", "Move last", "fetch >> compute", color=th.GREEN, width=4.6, height=1.05),
            ).arrange(DOWN, buff=0.14)
            pair = HStack(py, rules, gap=th.SPACE_LG)
            pair.move_to(self.layout.main_stage_center() + DOWN * 0.05)
            fit_to_bounds(pair, max_width=12.2, max_height=4.4)

            t = self._enter(st, pair, run_time=0.9)
            self._say(st, n0, anim_time=t)
            self._say(st, n1, anim_time=0.2)

            badge_bg = RoundedRectangle(
                corner_radius=0.08, width=3.4, height=0.42,
                stroke_color=th.GREEN, fill_color="#072213", fill_opacity=0.92,
            )
            badge_t = self._label("tests passed  ·  safe to synthesize", th.GREEN_LIGHT, 12, BOLD)
            badge = VGroup(badge_bg, badge_t)
            badge_t.move_to(badge_bg)
            badge.next_to(pair, DOWN, buff=0.18)
            t = self._enter(st, badge, run_time=0.45)
            self._say(st, n2, anim_time=t)
            st.takeaway("Treat RTL like unreleased production code: test it before it becomes physics.", wait=1.5)
