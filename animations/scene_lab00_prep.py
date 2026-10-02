"""
Lab 00-Prep: Hardware Thinking Primer for Software & AI Engineers
A visual-first masterclass on the death of the Program Counter and transitioning
from sequential software execution to 100% concurrent silicon hardware.
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
    SiliconCameraRig,
    LaserPacketStream,
    SiliconWire,
    StageLayout,
)


class Lab00PrepPrimer(SiliconCameraRig):
    def construct(self):
        layout = self.layout

        # =================================================================
        # ACT 1: THE PROGRAM COUNTER ILLUSION (~50s)
        # =================================================================
        kick, _, _ = th.header(
            "LAB 00-PREP: HARDWARE PRIMER", "The Death of the Program Counter",
            title_size=th.FONT_TITLE, badge_color=th.CYAN
        )
        self.play(FadeIn(kick, shift=DOWN * 0.3), run_time=1.0)

        banner = th.narration_banner(
            "In software, your brain is wired for sequential execution: Line 1 runs, THEN Line 2, driven by a single Program Counter."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.8)
        self.wait(5.5)

        code_lines = [
            ("# Sequential Software Thread", th.MUTED),
            ("a = b + c    # Clock cycle 1", th.GREEN),
            ("d = a * 2    # Clock cycle 2", th.AMBER),
            ("e = d + 10   # Clock cycle 3", th.CYAN),
            ("", th.MUTED),
            ("# While Line 1 runs:", th.RED),
            ("# Multiplier and SFU sit idle!", th.RED_LIGHT),
        ]
        code_win = th.code_window(
            code_lines, title_text="CPU: SEQUENTIAL PROGRAM COUNTER",
            width=6.0, height=3.8, font_size=th.FONT_TINY
        ).move_to(LEFT * 3.2 + DOWN * 0.4)

        stat1 = th.metric_card("1 at a Time", "Sequential Fetch", "A CPU only executes what the PC points to", color=th.AMBER, width=4.8, height=1.7)
        stat2 = th.metric_card("90% ALU Idle", "Silicon Inefficiency", "Standard CPUs leave most execution units waiting", color=th.RED, width=4.8, height=1.7)
        right_panel = VGroup(stat1, stat2).arrange(DOWN, buff=th.SPACE_MD).move_to(RIGHT * 3.2 + DOWN * 0.4)

        self.play(Create(code_win), FadeIn(right_panel, shift=UP * 0.2), run_time=1.2)

        self.play(
            Transform(banner, th.narration_banner(
                "When you write code for a CPU, instructions execute one at a time. The processor fetches, decodes, and steps forward."
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(kick), FadeOut(code_win), FadeOut(right_panel), run_time=0.6)

        # =================================================================
        # ACT 2: THE SILICON REALITY — 100% CONCURRENCY (~55s)
        # =================================================================
        hdr, _, _ = th.header(
            "LAB 00-PREP", "Software Threads vs. Physical Silicon",
            title_size=th.FONT_TITLE, badge_color=th.GREEN
        )
        self.play(FadeIn(hdr, shift=DOWN * 0.3), run_time=0.8)

        soft = th.card(5.6, 4.0, stroke=th.AMBER, radius=0.18).move_to(LEFT * 3.1 + DOWN * 0.35)
        hard = th.card(5.6, 4.0, stroke=th.CYAN, radius=0.18).move_to(RIGHT * 3.1 + DOWN * 0.35)

        s_t = Text("SOFTWARE WORLD", font=th.SANS, weight=BOLD, font_size=18, color=th.AMBER_LIGHT).next_to(soft.get_top(), DOWN, buff=0.25)
        h_t = Text("SILICON HARDWARE", font=th.SANS, weight=BOLD, font_size=18, color=th.CYAN_LIGHT).next_to(hard.get_top(), DOWN, buff=0.25)

        s_lines = th.bullets(
            ["Sequential instruction stream",
             "Program Counter steps down",
             "Variables stored in RAM / Cache",
             "Line 1, THEN Line 2, THEN Line 3"],
            color=th.TEXT, font_size=15, bullet_color=th.AMBER, buff=0.22,
        ).next_to(s_t, DOWN, buff=0.3, aligned_edge=LEFT).move_to(soft.get_center() + UP * 0.1)

        h_lines = th.bullets(
            ["100% concurrent gates & wires",
             "Electricity flows continuously",
             "Values exist as voltages on traces",
             "Everything executes AT THE SAME TIME"],
            color=th.CYAN, font_size=15, bullet_color=th.CYAN, buff=0.22,
        ).next_to(h_t, DOWN, buff=0.3, aligned_edge=LEFT).move_to(hard.get_center() + UP * 0.1)

        self.play(Create(soft), Create(hard), FadeIn(s_t), FadeIn(h_t), run_time=0.9)
        self.play(FadeIn(s_lines, shift=UP * 0.1), FadeIn(h_lines, shift=UP * 0.1), run_time=0.9)

        self.play(
            Transform(banner, th.narration_banner(
                "In silicon, there is no Program Counter. When power is applied, voltage ripples through copper wires: everything fires at once!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        # Animate parallel sparks on the hardware card
        sparks = VGroup(*[
            Dot(point=hard.get_bottom() + UP * 0.55 + RIGHT * (i - 1.5) * 0.9, radius=0.12, color=th.CYAN)
            for i in range(4)
        ])
        self.play(LaggedStart(*[GrowFromCenter(s) for s in sparks], lag_ratio=0.1), run_time=0.8)
        self.play(Flash(hard.get_bottom() + UP * 0.55, color=th.CYAN, line_length=0.45), run_time=0.6)
        self.wait(5.0)

        self.play(FadeOut(hdr), FadeOut(soft), FadeOut(hard), FadeOut(s_t), FadeOut(h_t),
                  FadeOut(s_lines), FadeOut(h_lines), FadeOut(sparks), run_time=0.6)

        # =================================================================
        # ACT 3: COMBINATIONAL VS SEQUENTIAL LOGIC (~60s)
        # =================================================================
        p_hdr, _, _ = th.header(
            "LAB 00-PREP", "The Two Pillars of Digital Silicon",
            title_size=th.FONT_TITLE, badge_color=th.AMBER
        )
        self.play(FadeIn(p_hdr, shift=DOWN * 0.3), run_time=0.8)

        comb = th.card(10.8, 1.8, stroke=th.GREEN, radius=0.16).move_to(UP * 0.45)
        seq = th.card(10.8, 1.8, stroke=th.AMBER, radius=0.16).next_to(comb, DOWN, buff=0.4)

        c_t = Text("1. Combinational Logic — Wires & Boolean Gates", font=th.SANS, weight=BOLD, font_size=18, color=th.GREEN_LIGHT)
        c_sub = Text("Zero memory, zero clock. Outputs react immediately after propagation delay t_pd.", font=th.MONO, font_size=14, color=th.TEXT)
        c_grp = VGroup(c_t, c_sub).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(comb.get_center())

        s_t = Text("2. Sequential Logic — Registers & Flip-Flops", font=th.SANS, weight=BOLD, font_size=18, color=th.AMBER_LIGHT)
        s_sub = Text("State & Memory. Values latch and update ONLY on the rising edge of the clock (posedge clk).", font=th.MONO, font_size=14, color=th.TEXT)
        s_grp = VGroup(s_t, s_sub).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(seq.get_center())

        self.play(Create(comb), FadeIn(c_grp), run_time=0.8)
        self.play(Create(seq), FadeIn(s_grp), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "Combinational logic computes instantly. Sequential logic acts like a camera shutter, freezing time at each clock tick."
            )),
            run_time=0.6
        )
        self.wait(6.0)

        # Interactive live AND gate demo
        and_demo = self._and_gate_demo(comb)
        self.play(FadeIn(and_demo), run_time=0.6)
        self._run_and_demo(and_demo)
        self.wait(5.0)

        self.play(FadeOut(p_hdr), FadeOut(comb), FadeOut(c_grp), FadeOut(seq), FadeOut(s_grp), FadeOut(and_demo), run_time=0.6)

        # =================================================================
        # ACT 4: ANATOMY OF A D FLIP-FLOP (~70s)
        # =================================================================
        d_hdr, _, _ = th.header(
            "LAB 00-PREP", "The D Flip-Flop: The Master of Time",
            title_size=th.FONT_TITLE, badge_color=th.CYAN
        )
        self.play(FadeIn(d_hdr, shift=DOWN * 0.3), run_time=0.8)

        ff = th.card(3.0, 2.4, stroke=th.AMBER, radius=0.15).move_to(UP * 0.2)
        ff_lbl = Text("D-FF", font=th.SANS, weight=BOLD, font_size=26, color=th.AMBER_LIGHT).move_to(ff)

        d_in = Text("D (Data)", font=th.MONO, weight=BOLD, font_size=16, color=th.CYAN).next_to(ff, LEFT, buff=0.6)
        q_out = Text("Q (Output)", font=th.MONO, weight=BOLD, font_size=16, color=th.GREEN).next_to(ff, RIGHT, buff=0.6)
        clk_lbl = Text("clk (Clock Edge)", font=th.MONO, font_size=15, color=th.PURPLE_LIGHT).next_to(ff, DOWN, buff=0.45)

        a1 = Arrow(d_in.get_right(), ff.get_left(), buff=0.08, color=th.CYAN)
        a2 = Arrow(ff.get_right(), q_out.get_left(), buff=0.08, color=th.GREEN)
        a3 = Arrow(clk_lbl.get_top(), ff.get_bottom(), buff=0.08, color=th.PURPLE)

        edge = th.clock_symbol(color=th.PURPLE).next_to(clk_lbl, LEFT, buff=0.25)

        self.play(Create(ff), FadeIn(ff_lbl), Create(a1), Create(a2), Create(a3),
                  FadeIn(d_in), FadeIn(q_out), FadeIn(clk_lbl), FadeIn(edge), run_time=1.0)
        self.focus_on(ff, buffer_factor=2.0, run_time=th.RATE_NORMAL)

        d_val = Text("0", font=th.MONO, weight=BOLD, font_size=28, color=th.CYAN).next_to(d_in, DOWN, buff=0.15)
        q_val = Text("?", font=th.MONO, weight=BOLD, font_size=28, color=th.MUTED).next_to(q_out, DOWN, buff=0.15)
        self.play(FadeIn(d_val), FadeIn(q_val), run_time=0.4)

        self.play(
            Transform(banner, th.narration_banner(
                "A D Flip-Flop ignores input D during steady clock states. It captures D ONLY at the rising clock edge (0 -> 1)."
            )),
            run_time=0.6
        )
        self.wait(5.0)

        # Pulse clock: Q captures 0
        self._pulse_clock(edge)
        self.screen_shake(intensity=0.03, cycles=2, run_time=0.2)
        self.play(Transform(q_val, Text("0", font=th.MONO, weight=BOLD, font_size=28, color=th.GREEN).next_to(q_out, DOWN, buff=0.15)), run_time=0.4)
        self.wait(3.0)

        # Change D to 1 without clock edge: Q stays 0!
        self.play(Transform(d_val, Text("1", font=th.MONO, weight=BOLD, font_size=28, color=th.CYAN).next_to(d_in, DOWN, buff=0.15)), run_time=0.4)
        hold_note = Text("D changed to 1, but Q holds 0 stable until the next clock!", font=th.MONO, font_size=13, color=th.AMBER_LIGHT).next_to(ff, UP, buff=0.6)
        self.play(FadeIn(hold_note), run_time=0.5)
        self.wait(5.0)

        # Pulse clock again: Q latches 1!
        self._pulse_clock(edge)
        self.screen_shake(intensity=0.03, cycles=2, run_time=0.2)
        self.play(Transform(q_val, Text("1", font=th.MONO, weight=BOLD, font_size=28, color=th.GREEN).next_to(q_out, DOWN, buff=0.15)), run_time=0.4)
        self.wait(4.0)

        self.play(FadeOut(d_hdr), FadeOut(ff), FadeOut(ff_lbl), FadeOut(a1), FadeOut(a2), FadeOut(a3),
                  FadeOut(d_in), FadeOut(q_out), FadeOut(clk_lbl), FadeOut(edge),
                  FadeOut(d_val), FadeOut(q_val), FadeOut(hold_note), run_time=0.6)
        self.reset_camera(run_time=th.RATE_FAST)

        # =================================================================
        # ACT 5: INTERACTIVE CHECKPOINT & CHALLENGE (~45s)
        # =================================================================
        act5_title = Text(
            "Architectural Checkpoint: Combinational vs. Sequential",
            font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.AMBER
        ).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act5_title), run_time=0.8)

        chal_card = th.card(10.5, 3.0, stroke=th.AMBER, radius=0.16).move_to(UP * 0.4)
        q1 = Text("PAUSE & THINK: PREDICT CIRCUIT BEHAVIOR", font=th.MONO, weight=BOLD, font_size=15, color=th.AMBER_LIGHT)
        q2 = Text("You have a circuit: Y = (A & B) | C. If input C changes voltage,", font=th.SANS, font_size=18, color=th.TEXT)
        q3 = Text("does output Y change immediately, or does it wait for a clock edge?", font=th.SANS, font_size=18, color=th.TEXT)
        chal_grp = VGroup(q1, q2, q3).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(chal_card)

        self.play(Create(chal_card), FadeIn(chal_grp), run_time=1.0)
        self.play(
            Transform(banner, th.narration_banner(
                "Pause the video and answer: does this boolean expression react instantly, or does it require a clock pulse?"
            )),
            run_time=0.6
        )
        self.wait(7.0)

        ans_card = th.card(10.5, 1.3, stroke=th.GREEN, radius=0.14).next_to(chal_card, DOWN, buff=0.3)
        ans_txt = Text(
            "Answer: IMMEDIATELY. This is pure combinational logic (no registers, no flip-flops).",
            font=th.MONO, weight=BOLD, font_size=14, color=th.GREEN_LIGHT
        ).move_to(ans_card)
        self.play(Create(ans_card), FadeIn(ans_txt), run_time=0.8)
        self.wait(6.0)

        self.play(FadeOut(act5_title), FadeOut(chal_card), FadeOut(chal_grp), FadeOut(ans_card), FadeOut(ans_txt), run_time=0.6)

        # =================================================================
        # ACT 6: SYNTHESIZABLE VERILOG & COCOTB BRIDGE (~45s)
        # =================================================================
        act6_title = Text(
            "Synthesizable SystemVerilog & Python Cocotb",
            font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.CYAN
        ).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act6_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "In SystemVerilog, we use 'always_comb' for instant gates, and 'always_ff @(posedge clk)' for clocked flip-flops."
            )),
            run_time=0.6
        )

        sv_lines = [
            ("// 1. Combinational Logic: Instant evaluation", th.MUTED),
            ("always_comb begin", th.CYAN),
            ("    sum = a + b;   // Pure wires and gates", th.TEXT),
            ("end", th.CYAN),
            ("", th.MUTED),
            ("// 2. Sequential Logic: Clock-edge register latch", th.MUTED),
            ("always_ff @(posedge clk or negedge rst_n) begin", th.AMBER),
            ("    if (!rst_n) q <= 8'd0;", th.TEXT),
            ("    else        q <= d;     // Latches only on rising edge", th.GREEN_LIGHT),
            ("end", th.AMBER),
        ]
        sv_win = th.code_window(
            sv_lines, title_text="SYSTEMVERILOG: COMBINATIONAL VS SEQUENTIAL",
            width=10.2, height=3.2, font_size=th.FONT_TINY, title_color=th.GREEN
        ).move_to(UP * 0.4)

        self.play(Create(sv_win), run_time=1.0)
        self.wait(5.0)

        recap_card = th.card(10.2, 1.2, stroke=th.GREEN, radius=0.15).move_to(DOWN * 1.5)
        recap_txt = Text(
            "✓ Ready for Silicon: In Lab 00, we build the 8-Bit Signed Adder with Saturation Clamping!",
            font=th.MONO, weight=BOLD, font_size=th.FONT_BADGE, color=th.GREEN_LIGHT
        ).move_to(recap_card)

        self.play(Create(recap_card), FadeIn(recap_txt), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "Now you have the hardware mindset: gates fire concurrently, and flip-flops anchor time. On to Lab 00!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(act6_title), FadeOut(sv_win), FadeOut(recap_card), FadeOut(recap_txt), FadeOut(banner), run_time=1.0)
        self.wait(1.0)

    # ------------------------------------------------------------------
    # Helper Gates
    # ------------------------------------------------------------------
    def _and_gate_demo(self, anchor):
        g = VGroup()
        body = VGroup(
            Line(np.array([0, 0.45, 0]), np.array([0.45, 0.45, 0]), color=th.GREEN, stroke_width=3),
            Line(np.array([0, -0.45, 0]), np.array([0.45, -0.45, 0]), color=th.GREEN, stroke_width=3),
            ArcBetweenPoints(np.array([0.45, 0.45, 0]), np.array([0.45, -0.45, 0]), angle=-PI, color=th.GREEN, stroke_width=3),
        )
        g.add(body)
        in_a = Line(np.array([-0.6, 0.22, 0]), np.array([0, 0.22, 0]), color=th.CYAN, stroke_width=3)
        in_b = Line(np.array([-0.6, -0.22, 0]), np.array([0, -0.22, 0]), color=th.AMBER, stroke_width=3)
        out = Line(np.array([0.45, 0, 0]), np.array([1.1, 0, 0]), color=th.GREEN, stroke_width=3)
        g.add(in_a, in_b, out)
        a_lbl = Text("A=1", font=th.MONO, font_size=12, color=th.CYAN).next_to(in_a, LEFT, buff=0.05)
        b_lbl = Text("B=1", font=th.MONO, font_size=12, color=th.AMBER).next_to(in_b, LEFT, buff=0.05)
        y_lbl = Text("Y=1", font=th.MONO, weight=BOLD, font_size=13, color=th.GREEN_LIGHT).next_to(out, RIGHT, buff=0.05)
        g.add(a_lbl, b_lbl, y_lbl)
        g.scale(0.85).next_to(anchor, DOWN, buff=0.25)
        return g

    def _run_and_demo(self, g):
        dot_a = Dot(g[1].get_start(), radius=0.08, color=th.CYAN_LIGHT)
        dot_b = Dot(g[2].get_start(), radius=0.08, color=th.AMBER_LIGHT)
        self.play(FadeIn(dot_a), FadeIn(dot_b), run_time=0.3)
        self.play(dot_a.animate.move_to(g[1].get_end()), dot_b.animate.move_to(g[2].get_end()), run_time=0.5)
        dot_out = Dot(g[3].get_start(), radius=0.08, color=th.GREEN_LIGHT)
        self.play(FadeIn(dot_out), run_time=0.2)
        self.play(dot_out.animate.move_to(g[3].get_end()), run_time=0.5)
        self.play(FadeOut(dot_a), FadeOut(dot_b), FadeOut(dot_out), run_time=0.3)

    def _pulse_clock(self, edge_glyph):
        th.pulse_edge(self, edge_glyph)
