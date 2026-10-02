"""
Lab 03: The Memory Wall — Weight-Stationary Processing Element (PE)
A kinetic, visual-first masterclass on spatial hardware computing in AI accelerators.

Narrative Flow:
  Act 1: The Von Neumann Memory Wall (DRAM 200 pJ vs Silicon 0.2 pJ)
  Act 2: The Living Weight-Stationary PE (Cycle-accurate clock pulse dataflow)
  Act 3: Register Budget & Physical Die Footprint (48 D-FFs per cell)
  Act 4: Synthesizable Silicon Architecture (rtl/pe.sv) & Verification
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
    StageLayout,
    HardwareConfig,
)


class Lab03ProcessingElement(SiliconCameraRig):
    def construct(self):
        layout = self.layout
        config = HardwareConfig(data_width=8)

        # =====================================================================
        # ACT 1: THE VON NEUMANN MEMORY WALL (~45s)
        # =====================================================================
        kicker, _, _ = th.header(
            "THE MEMORY WALL",
            "Why AI Chips Must Lock Weights in Silicon",
            title_size=30,
            badge_color=th.CYAN
        )
        self.play(FadeIn(kicker, shift=DOWN * 0.3), run_time=0.8)

        banner = th.narration_banner(
            "In modern AI workloads, standard CPUs and GPUs spend 90% of their energy not computing math, but moving numbers across memory buses."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.7)
        self.wait(1.5)

        # Software Code Window on Left
        py_code = [
            ("# Traditional CPU GEMM Execution", th.MUTED),
            ("for i in range(M):", th.TEXT),
            ("  for j in range(N):", th.TEXT),
            ("    for k in range(K):", th.TEXT),
            ("      # DRAM fetch every single step!", th.RED_LIGHT),
            ("      C[i][j] += A[i][k] * B[k][j];", th.CYAN_LIGHT),
            ("", th.MUTED),
            ("# The Physical Energy Disaster:", th.AMBER),
            ("# Moving 1 byte: 1,000x more energy than computing it!", th.RED),
        ]
        soft_win = th.code_window(py_code, title_text="CPU: VON NEUMANN BOTTLENECK",
                                  width=6.2, height=3.8, font_size=13)
        soft_win.move_to(LEFT * 3.1 + DOWN * 0.4)

        # Right Panel: Energy Shock Comparison
        m1 = th.metric_card("0.2 pJ", "Silicon 8-Bit MAC",
                            "Picojoules of energy to compute in gates", color=th.GREEN, width=4.8, height=1.7)
        m2 = th.metric_card("200 pJ", "Off-Chip DRAM Fetch",
                            "1,000x Energy Penalty just to move 1 byte!", color=th.RED, width=4.8, height=1.7)
        right_panel = VGroup(m1, m2).arrange(DOWN, buff=0.3).move_to(RIGHT * 3.3 + DOWN * 0.4)

        self.play(Create(soft_win), run_time=1.0)
        self.wait(1.0)
        self.play(FadeIn(m1, shift=UP * 0.2), FadeIn(m2, shift=UP * 0.2), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "Computing a multiply-accumulate takes 0.2 picojoules. But fetching that weight from DRAM burns 200 picojoules!"
            )),
            run_time=0.6
        )
        self.wait(2.5)

        self.play(FadeOut(kicker), FadeOut(soft_win), FadeOut(right_panel), run_time=0.5)

        # =====================================================================
        # ACT 2: THE LIVING WEIGHT-STATIONARY PE (~70s)
        # =====================================================================
        pe_title = Text("The Solution: Weight-Stationary Spatial Computing",
                        font=th.SANS, weight=BOLD, font_size=26, color=th.TEXT)
        pe_title.to_edge(UP, buff=0.6)
        self.play(Write(pe_title), run_time=0.6)

        self.play(
            Transform(banner, th.narration_banner(
                "Instead of re-reading weights from memory, we pre-load them ONCE into local flip-flops inside the Processing Element (PE)."
            )),
            run_time=0.5
        )

        # Outer PE Silicon Cell
        pe_box = RoundedRectangle(corner_radius=0.22, width=5.6, height=3.2,
                                  stroke_color=th.CYAN, stroke_width=3.0,
                                  fill_color=th.CARD, fill_opacity=0.95).move_to(UP * 0.35)

        # Internal stationary weight register (Glowing Gold)
        w_reg = RoundedRectangle(corner_radius=0.12, width=2.4, height=0.65,
                                 stroke_color=th.AMBER, stroke_width=2.5,
                                 fill_color=th.AMBER_DARK, fill_opacity=0.9).move_to(pe_box.get_top() + DOWN * 0.65)
        w_txt = Text("Weight Reg [W = 3]", font=th.MONO, weight=BOLD, font_size=14, color=th.AMBER_LIGHT).move_to(w_reg)

        # Multiplier block
        mult_circle = Circle(radius=0.42, color=th.AMBER, fill_color=th.BG, fill_opacity=1).move_to(pe_box.get_center() + LEFT * 0.45 + DOWN * 0.2)
        m_txt = Text("×", font=th.SANS, weight=BOLD, font_size=24, color=th.AMBER).move_to(mult_circle)

        # Adder block
        add_circle = Circle(radius=0.42, color=th.GREEN, fill_color=th.BG, fill_opacity=1).move_to(pe_box.get_center() + RIGHT * 0.45 + DOWN * 0.2)
        a_txt = Text("+", font=th.SANS, weight=BOLD, font_size=24, color=th.GREEN).move_to(add_circle)

        # External signal arrows
        in_a = Arrow(start=pe_box.get_left() + LEFT * 1.6 + UP * 0.1, end=pe_box.get_left() + UP * 0.1, buff=0, color=th.CYAN, stroke_width=4.0)
        lbl_in_a = Text("a_in (West)\n[4]", font=th.MONO, font_size=12, color=th.CYAN_LIGHT).next_to(in_a, UP, buff=0.1)

        out_a = Arrow(start=pe_box.get_right() + UP * 0.1, end=pe_box.get_right() + RIGHT * 1.6 + UP * 0.1, buff=0, color=th.CYAN, stroke_width=4.0)
        lbl_out_a = Text("a_out (East)\n[Hops East]", font=th.MONO, font_size=12, color=th.CYAN_LIGHT).next_to(out_a, UP, buff=0.1)

        in_s = Arrow(start=pe_box.get_top() + UP * 0.8 + RIGHT * 0.8, end=pe_box.get_top() + RIGHT * 0.8, buff=0, color=th.GREEN, stroke_width=4.0)
        lbl_in_s = Text("sum_in (North) [10]", font=th.MONO, font_size=12, color=th.GREEN_LIGHT).next_to(in_s, RIGHT, buff=0.1)

        out_s = Arrow(start=pe_box.get_bottom() + RIGHT * 0.8, end=pe_box.get_bottom() + DOWN * 0.8 + RIGHT * 0.8, buff=0, color=th.GREEN, stroke_width=4.0)
        lbl_out_s = Text("sum_out (South) [22]", font=th.MONO, weight=BOLD, font_size=12, color=th.GREEN_LIGHT).next_to(out_s, RIGHT, buff=0.1)

        pe_cell_grp = VGroup(pe_box, w_reg, w_txt, mult_circle, m_txt, add_circle, a_txt,
                             in_a, lbl_in_a, out_a, lbl_out_a, in_s, lbl_in_s, out_s, lbl_out_s)

        self.play(FadeIn(pe_cell_grp), run_time=1.2)
        self.focus_on(pe_box, buffer_factor=1.55, run_time=th.RATE_NORMAL)
        self.wait(0.8)

        # Shoot incoming data tokens using LaserPacketStream
        LaserPacketStream.shoot_token(self, in_a.get_start(), in_a.get_end(), color=th.CYAN, payload_val="4", run_time=0.5)
        LaserPacketStream.shoot_token(self, in_s.get_start(), in_s.get_end(), color=th.GREEN, payload_val="10", run_time=0.5)

        # Pulse clock signal: input 4 * 3 = 12; 10 + 12 = 22!
        step_badge = Text("ON CLOCK EDGE: 4 × 3 = 12  ➔  10 + 12 = 22 !", font=th.MONO,
                          weight=BOLD, font_size=15, color=th.AMBER_LIGHT)
        step_badge.next_to(banner, UP, buff=0.22)
        self.screen_shake(intensity=0.04, cycles=2, run_time=0.15)
        self.play(
            FadeIn(step_badge, shift=UP * 0.2),
            Flash(mult_circle, color=th.AMBER, flash_radius=0.5),
            Flash(add_circle, color=th.GREEN, flash_radius=0.5),
            Transform(banner, th.narration_banner(
                "Activations flow horizontally West to East. Partial sums accumulate vertically North to South. Zero DRAM memory traffic!"
            )),
            run_time=0.9
        )
        self.wait(2.2)
        self.reset_camera(run_time=th.RATE_FAST)

        self.play(FadeOut(pe_title), FadeOut(pe_cell_grp), FadeOut(step_badge), run_time=0.5)

        # =====================================================================
        # ACT 3: REGISTER BUDGET INSIDE 1 PE (~50s)
        # =====================================================================
        budget_title = Text("PE Physical Die Footprint: 48 D-Flip-Flop Registers",
                            font=th.SANS, weight=BOLD, font_size=26, color=th.CYAN)
        budget_title.to_edge(UP, buff=0.6)
        self.play(Write(budget_title), run_time=0.6)

        # 3 Register strips
        b_card = th.card(10.5, 3.2, stroke=th.BORDER, radius=0.18).move_to(UP * 0.25)
        r1 = Text("1. Stationary Weight Register (weight_reg):  8 bits (INT8)", font=th.MONO, font_size=15, color=th.AMBER_LIGHT)
        r2 = Text("2. Horizontal Activation Pipeline (a_reg):   8 bits (INT8)", font=th.MONO, font_size=15, color=th.CYAN_LIGHT)
        r3 = Text("3. Vertical Partial Sum Pipeline (sum_reg): 32 bits (INT32)", font=th.MONO, font_size=15, color=th.GREEN_LIGHT)
        tot = Text("Total State Registers per PE: 8 + 8 + 32 = 48 D-Flip-Flops", font=th.MONO, weight=BOLD, font_size=17, color=th.TEXT)

        r_stack = VGroup(r1, r2, r3, tot).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(b_card)

        self.play(Create(b_card), FadeIn(r_stack), run_time=0.9)
        self.play(
            Transform(banner, th.narration_banner(
                "With only 48 flip-flops per cell, thousands of PEs can fit on a single silicon die to form a massive 2D computing array!"
            )),
            run_time=0.6
        )
        self.wait(2.2)

        self.play(FadeOut(budget_title), FadeOut(b_card), FadeOut(r_stack), run_time=0.5)

        # =====================================================================
        # ACT 4: SYNTHESIZABLE SILICON ARCHITECTURE & VERIFICATION (~50s)
        # =====================================================================
        rtl_title = Text("Synthesizable PE: rtl/pe.sv",
                         font=th.SANS, weight=BOLD, font_size=26, color=th.CYAN)
        rtl_title.to_edge(UP, buff=0.6)
        self.play(Write(rtl_title), run_time=0.6)

        sv_lines = [
            ("// Weight-Stationary Processing Element Flip-Flops:", th.MUTED),
            ("always_ff @(posedge clk or negedge rst_n) begin", th.CYAN),
            ("    if (!rst_n) begin a_out <= 0; sum_out <= 0; end", th.MUTED),
            ("    else begin", th.CYAN),
            ("        a_out   <= a_in; // Pass activation East", th.CYAN_LIGHT),
            ("        sum_out <= sum_in + (a_in * weight_reg); // Accumulate South", th.GREEN_LIGHT),
            ("    end", th.CYAN),
            ("end", th.CYAN),
        ]
        sv_win = th.code_window(sv_lines, title_text="RTL/PE.SV",
                                width=10.5, height=3.0, font_size=13, title_color=th.GREEN)
        sv_win.move_to(UP * 0.55)

        self.play(Create(sv_win), run_time=1.0)

        # Pre-Silicon Checkpoint
        check_card = th.card(10.5, 1.1, stroke=th.GREEN, radius=0.15)
        check_card.next_to(banner, UP, buff=0.22)
        check_txt = Text("✓ Cocotb Testbench: Verified single-cell clock cycle timing & stationary weight reuse!",
                         font=th.MONO, weight=BOLD, font_size=14, color=th.GREEN_LIGHT).move_to(check_card)

        self.play(Create(check_card), FadeIn(check_txt), run_time=0.7)
        self.play(
            Transform(banner, th.narration_banner(
                "Next in our AI Hardware journey: Lab 04, where we connect 16 PEs into a 4x4 Systolic Wavefront Matrix Mesh!"
            )),
            run_time=0.6
        )
        self.wait(3.0)
