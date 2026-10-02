"""
Lab 00-Prep: Hardware Thinking Primer for Software & AI Engineers

Deep-dive structure:
1.  Cold open: a Python program "running" sequentially, line by line.
2.  The fundamental shift: the same computation unrolled into silicon that
    fires everywhere at once (animated gates firing in parallel).
3.  The two pillars of digital silicon:
    a. Combinational logic (wires & gates): inputs ripple instantly to outputs.
    b. Sequential logic (D flip-flop + clock): state changes ONLY on the edge.
4.  A single D flip-flop animated: data enters, clock rises, value latches.
5.  Recap card: "You are drawing a physical blueprint."
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
        # ACT 1 — COLD OPEN: A PROGRAM RUNS LINE BY LINE
        # =================================================================
        kick, kick_b, kick_t = th.header(
            "LAB 00-PREP", "Your Brain Is About to Change"
        )
        self.play(FadeIn(kick, shift=DOWN * 0.3), run_time=0.7)

        code_lines = [
            ("a = b + c", th.GREEN),
            ("d = a * 2", th.AMBER),
            ("e = d + 10", th.CYAN),
        ]
        code_card = th.card(4.6, 2.6, stroke=th.GREEN, radius=0.15)
        code_card.move_to(DOWN * 0.9 + LEFT * 3.4)
        code_text = VGroup()
        for i, (ln, col) in enumerate(code_lines):
            t = Text(ln, font=th.MONO, font_size=26, color=col)
            code_text.add(t)
        code_text.arrange(DOWN, aligned_edge=LEFT, buff=0.28).move_to(code_card)

        pc = Text("PC", font=th.MONO, weight=BOLD, font_size=16, color=th.GREEN_LIGHT)
        pc_box = SurroundingRectangle(pc, buff=0.08, color=th.GREEN, stroke_width=2)

        self.play(Create(code_card), FadeIn(code_text), run_time=0.8)

        # A "Program Counter" arrow steps down the lines, one at a time.
        pc_grp = VGroup(pc_box, pc).next_to(code_text[0], LEFT, buff=0.7)
        self.play(FadeIn(pc_grp), run_time=0.4)
        for i in range(len(code_lines)):
            self.play(pc_grp.animate.next_to(code_text[i], LEFT, buff=0.7),
                      run_time=0.5)
            self.wait(0.35)
        self.wait(0.3)

        note = Text(
            "One instruction at a time.\nThe CPU has a single Program Counter.",
            font=th.SANS, font_size=20, color=th.MUTED, line_spacing=1.3,
        )
        note.next_to(code_card, RIGHT, buff=1.0).align_to(code_card, UP)
        self.play(FadeIn(note, shift=RIGHT * 0.2), run_time=0.6)
        self.wait(1.0)

        self.play(FadeOut(kick), FadeOut(code_card), FadeOut(code_text),
                  FadeOut(pc_grp), FadeOut(note), run_time=0.6)

        # =================================================================
        # ACT 2 — THE FUNDAMENTAL MENTAL SHIFT
        # =================================================================
        hdr, hb, ht = th.header(
            "LAB 00-PREP", "Software vs. Silicon"
        )
        self.play(FadeIn(hdr, shift=DOWN * 0.3), run_time=0.7)

        # Two panels.
        soft = th.card(5.4, 4.0, stroke=th.AMBER, radius=0.18)
        soft.move_to(LEFT * 3.0 + DOWN * 0.35)
        hard = th.card(5.4, 4.0, stroke=th.CYAN, radius=0.18)
        hard.move_to(RIGHT * 3.0 + DOWN * 0.35)

        s_t = Text("SOFTWARE", font=th.SANS, weight=BOLD, font_size=20,
                   color=th.AMBER_LIGHT).next_to(soft.get_top(), DOWN, buff=0.25)
        h_t = Text("SILICON", font=th.SANS, weight=BOLD, font_size=20,
                   color=th.CYAN_LIGHT).next_to(hard.get_top(), DOWN, buff=0.25)

        s_lines = th.bullets(
            ["Sequential execution",
             "Program Counter steps",
             "Variables live in RAM",
             "Line 1, THEN line 2"],
            color=th.TEXT, font_size=17, bullet_color=th.AMBER, buff=0.2,
        ).next_to(s_t, DOWN, buff=0.3, aligned_edge=LEFT)
        s_lines.move_to(soft.get_center() + UP * 0.1)

        h_lines = th.bullets(
            ["100% concurrent gates",
             "Electricity flows always",
             "Values live on wires",
             "Everything AT ONCE"],
            color=th.CYAN, font_size=17, bullet_color=th.CYAN, buff=0.2,
        ).next_to(h_t, DOWN, buff=0.3, aligned_edge=LEFT)
        h_lines.move_to(hard.get_center() + UP * 0.1)

        self.play(Create(soft), Create(hard), FadeIn(s_t), FadeIn(h_t),
                  run_time=0.7)
        self.play(FadeIn(s_lines, shift=UP * 0.1),
                  FadeIn(h_lines, shift=UP * 0.1), run_time=0.8)
        self.wait(0.8)

        # Animate the difference: a lone token loops in software; many tokens
        # fire simultaneously in silicon.
        loop = Circle(radius=0.16, color=th.AMBER, fill_opacity=1.0)
        loop.move_to(soft.get_bottom() + UP * 0.5)
        self.play(FadeIn(loop), run_time=0.3)
        self.play(MoveAlongPath(loop, Circle(radius=1.2).move_to(soft.get_bottom() + UP * 0.5)),
                  run_time=2.0, rate_func=linear)

        sparks = VGroup(*[
            Dot(point=hard.get_bottom() + UP * 0.5 + RIGHT * (i - 1.5) * 0.7,
                radius=0.1, color=th.CYAN)
            for i in range(4)
        ])
        self.play(LaggedStart(*[GrowFromCenter(s) for s in sparks],
                              lag_ratio=0.08), run_time=0.6)
        self.play(Flash(hard.get_bottom() + UP * 0.5, color=th.CYAN, line_length=0.4),
                  run_time=0.5)
        self.wait(0.6)

        self.play(FadeOut(hdr), FadeOut(soft), FadeOut(hard), FadeOut(s_t),
                  FadeOut(h_t), FadeOut(s_lines), FadeOut(h_lines),
                  FadeOut(loop), FadeOut(sparks), run_time=0.6)

        # =================================================================
        # ACT 3 — THE TWO PILLARS OF DIGITAL SILICON
        # =================================================================
        p_hdr, _, p_t = th.header(
            "LAB 00-PREP", "The Two Pillars of Digital Silicon"
        )
        self.play(FadeIn(p_hdr, shift=DOWN * 0.3), run_time=0.7)

        comb = th.card(10.4, 1.9, stroke=th.GREEN, radius=0.16)
        comb.move_to(UP * 0.35)
        seq = th.card(10.4, 1.9, stroke=th.AMBER, radius=0.16)
        seq.next_to(comb, DOWN, buff=0.45)

        c_t = Text("1.  Combinational Logic  —  wires & gates",
                   font=th.SANS, weight=BOLD, font_size=19, color=th.GREEN_LIGHT)
        c_sub = Text(
            "No memory, no clock.  Output updates the instant inputs change.",
            font=th.MONO, font_size=15, color=th.TEXT,
        )
        c_grp = VGroup(c_t, c_sub).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        c_grp.move_to(comb.get_center())

        s_t = Text("2.  Sequential Logic  —  registers & D flip-flops",
                   font=th.SANS, weight=BOLD, font_size=19, color=th.AMBER_LIGHT)
        s_sub = Text(
            "Memory & state.  Updates ONLY on the rising edge of the clock.",
            font=th.MONO, font_size=15, color=th.TEXT,
        )
        s_grp = VGroup(s_t, s_sub).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        s_grp.move_to(seq.get_center())

        self.play(Create(comb), FadeIn(c_grp), run_time=0.7)
        self.play(Create(seq), FadeIn(s_grp), run_time=0.7)

        # Animated mini-demo for combinational: flip an input bit, output reacts
        # immediately (same frame). Draw a small AND gate.
        and_grp = self._and_gate_demo(comb)
        self.play(FadeIn(and_grp), run_time=0.6)
        self._run_and_demo(and_grp)

        self.wait(0.5)
        self.play(FadeOut(p_hdr), FadeOut(comb), FadeOut(c_grp), FadeOut(seq),
                  FadeOut(s_grp), FadeOut(and_grp), run_time=0.6)

        # =================================================================
        # ACT 4 — THE D FLIP-FLOP, ANIMATED
        # =================================================================
        d_hdr, _, d_t = th.header(
            "LAB 00-PREP", "The D Flip-Flop: One Bit of Memory"
        )
        self.play(FadeIn(d_hdr, shift=DOWN * 0.3), run_time=0.7)
        self.wait(0.4)

        ff = th.card(2.6, 2.2, stroke=th.AMBER, radius=0.12)
        ff.move_to(UP * 0.15)
        ff_lbl = Text("D-FF", font=th.SANS, weight=BOLD, font_size=24,
                      color=th.AMBER_LIGHT).move_to(ff)

        d_in = Text("D", font=th.SANS, weight=BOLD, font_size=18, color=th.CYAN)
        d_in.next_to(ff, LEFT, buff=0.5)
        q_out = Text("Q", font=th.SANS, weight=BOLD, font_size=18, color=th.GREEN)
        q_out.next_to(ff, RIGHT, buff=0.5)
        clk_lbl = Text("clk", font=th.MONO, font_size=16, color=th.PURPLE_LIGHT)
        clk_lbl.next_to(ff, DOWN, buff=0.35)

        a1 = Arrow(d_in.get_right(), ff.get_left(), buff=0.06, color=th.CYAN)
        a2 = Arrow(ff.get_right(), q_out.get_left(), buff=0.06, color=th.GREEN)
        a3 = Arrow(clk_lbl.get_top(), ff.get_bottom(), buff=0.06, color=th.PURPLE)

        # The clock edge glyph
        edge = th.clock_symbol(color=th.PURPLE)
        edge.next_to(clk_lbl, LEFT, buff=0.25)

        self.play(Create(ff), FadeIn(ff_lbl), Create(a1), Create(a2), Create(a3),
                  FadeIn(d_in), FadeIn(q_out), FadeIn(clk_lbl), FadeIn(edge),
                  run_time=0.9)
        self.focus_on(ff, buffer_factor=2.2, run_time=th.RATE_NORMAL)

        # Show D=0, then pulse clock: Q follows D.
        d_val = Text("0", font=th.MONO, weight=BOLD, font_size=28, color=th.CYAN)
        d_val.move_to(d_in)
        q_val = Text("?", font=th.MONO, weight=BOLD, font_size=28, color=th.MUTED)
        q_val.move_to(q_out)
        self.play(FadeIn(d_val), FadeIn(q_val), run_time=0.4)

        self._pulse_clock(edge)
        self.screen_shake(intensity=0.03, cycles=2, run_time=0.15)
        self.play(Transform(q_val, Text("0", font=th.MONO, weight=BOLD,
                                        font_size=28, color=th.GREEN).move_to(q_out)),
                  run_time=0.4)
        self.wait(0.5)

        # Change D to 1 but DON'T clock: Q stays 0.
        self.play(Transform(d_val, Text("1", font=th.MONO, weight=BOLD,
                                        font_size=28, color=th.CYAN).move_to(d_in)),
                  run_time=0.4)
        stay = Text("Q holds 0 — no clock edge yet!",
                    font=th.SANS, font_size=19, color=th.MUTED)
        stay.next_to(ff, UP, buff=0.9)
        self.play(FadeIn(stay, shift=UP * 0.15), run_time=0.5)
        self.wait(1.0)
        self.play(FadeOut(stay), run_time=0.3)

        # Pulse clock again: Q latches the new D.
        self._pulse_clock(edge)
        self.screen_shake(intensity=0.03, cycles=2, run_time=0.15)
        self.play(Transform(q_val, Text("1", font=th.MONO, weight=BOLD,
                                        font_size=28, color=th.GREEN).move_to(q_out)),
                  run_time=0.4)
        self.wait(0.7)

        self.play(FadeOut(d_hdr), FadeOut(ff), FadeOut(ff_lbl), FadeOut(a1),
                  FadeOut(a2), FadeOut(a3), FadeOut(d_in), FadeOut(q_out),
                  FadeOut(clk_lbl), FadeOut(edge), FadeOut(d_val), FadeOut(q_val),
                  run_time=0.6)
        self.reset_camera(run_time=th.RATE_FAST)

        # =================================================================
        # CHECKPOINT
        # =================================================================
        th.checkpoint(
            self,
            "Which construct holds state, and which reacts instantly?",
            ["Combinational logic: no memory, output reacts instantly",
             "Sequential logic: D flip-flops store state on the clock edge"],
        )

        # =================================================================
        # CHALLENGE
        # =================================================================
        th.challenge(
            self,
            ["You have a module with three inputs A, B, C",
             "and one output Y = (A AND B) OR C.",
             "Does changing C change Y immediately — or only on a clock edge?"],
            "Immediately.  It is pure combinational logic: no register, no clock.",
        )

        # =================================================================
        # ACT 5 — RECAP
        # =================================================================
        th.recap(
            self,
            "Ready to Build Real AI Silicon",
            ["You are NOT writing code that runs on a CPU",
             "You are drawing a blueprint of copper wires & transistors",
             "Combinational gates react instantly; registers wait for the clock",
             "Next: Lab 00 — Signed Adder & Saturation Arithmetic"],
            stroke=th.CYAN, title_color=th.CYAN, font_size=19,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _and_gate_demo(self, anchor):
        """Build a small AND-gate demo drawing; returns VGroup positioned near anchor."""
        g = VGroup()
        body = VGroup(
            Line(np.array([0, 0.5, 0]), np.array([0.5, 0.5, 0]), color=th.GREEN, stroke_width=3),
            Line(np.array([0, -0.5, 0]), np.array([0.5, -0.5, 0]), color=th.GREEN, stroke_width=3),
            ArcBetweenPoints(np.array([0.5, 0.5, 0]), np.array([0.5, -0.5, 0]),
                             angle=-PI, color=th.GREEN, stroke_width=3),
        )
        g.add(body)

        in_a = Line(np.array([-0.7, 0.25, 0]), np.array([0, 0.25, 0]), color=th.CYAN, stroke_width=3)
        in_b = Line(np.array([-0.7, -0.25, 0]), np.array([0, -0.25, 0]), color=th.AMBER, stroke_width=3)
        out = Line(np.array([0.5, 0, 0]), np.array([1.3, 0, 0]), color=th.GREEN, stroke_width=3)
        g.add(in_a, in_b, out)

        a_lbl = Text("A", font=th.MONO, font_size=15, color=th.CYAN).next_to(in_a, LEFT, buff=0.05)
        b_lbl = Text("B", font=th.MONO, font_size=15, color=th.AMBER).next_to(in_b, LEFT, buff=0.05)
        y_lbl = Text("Y", font=th.MONO, font_size=15, color=th.GREEN).next_to(out, RIGHT, buff=0.05)
        g.add(a_lbl, b_lbl, y_lbl)

        # Output value badge (positioned near the output line)
        y_val = Text("0", font=th.MONO, weight=BOLD, font_size=22, color=th.GREEN)
        y_val.next_to(out, DOWN, buff=0.2)
        g.y_val = y_val

        g.scale(0.55)
        g.next_to(anchor, RIGHT, buff=0.3)
        return g

    def _run_and_demo(self, g):
        """Animate two input packets entering the AND gate, output lights instantly."""
        y_val = g.y_val
        self.add(y_val)
        start_a = g[1].get_start()  # in_a line
        start_b = g[2].get_start()  # in_b line
        pa = th.packet(color=th.CYAN, radius=0.07)
        pb = th.packet(color=th.AMBER, radius=0.07)
        pa.move_to(start_a + LEFT * 0.1)
        pb.move_to(start_b + LEFT * 0.1)
        self.play(FadeIn(pa), FadeIn(pb), run_time=0.3)
        self.play(pa.animate.move_to(start_a + RIGHT * 0.5),
                  pb.animate.move_to(start_b + RIGHT * 0.5), run_time=0.4)
        self.play(Transform(y_val, Text("1", font=th.MONO, weight=BOLD,
                                        font_size=22, color=th.GREEN).move_to(y_val)),
                  run_time=0.3)
        self.wait(0.4)
        self.remove(y_val, pa, pb)

    def _pulse_clock(self, edge_glyph):
        """Flash the clock glyph to represent one rising edge."""
        th.pulse_edge(self, edge_glyph)
