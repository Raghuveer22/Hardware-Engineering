"""
Lab 01: The Area Monster — Signed INT8 Hardware Multiplier & O(N^2) Silicon Scaling
A kinetic, visual-first masterclass on silicon multiplication in AI accelerators.

Narrative Flow:
  Act 1: The GEMM Scaling Crisis (PyTorch linear layer with 60M multiplies)
  Act 2: Binary Long-Multiplication in Motion (Row-by-row partial product shifts)
  Act 3: The O(N^2) Gate Explosion & Wallace-Tree Pachinko Reduction
  Act 4: Synthesizable Silicon Architecture (rtl/multiplier_int8.sv) & Verification
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


class Lab01Multiplier(SiliconCameraRig):
    def construct(self):
        layout = self.layout
        config = HardwareConfig(data_width=8)

        # =====================================================================
        # ACT 1: THE GEMM SCALING CRISIS (~45s)
        # =====================================================================
        kicker, _, _ = th.header(
            "THE AREA MONSTER",
            "Why Multipliers Consume 90% of AI Silicon",
            title_size=30,
            badge_color=th.CYAN
        )
        self.play(FadeIn(kicker, shift=DOWN * 0.3), run_time=0.8)

        banner = th.narration_banner(
            "In modern LLMs, generating a single token requires tens of millions of multiplications. But in silicon, multiplying bits is a physical nightmare."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.7)
        self.wait(1.5)

        # PyTorch Code Window on Left
        py_code = [
            ("# PyTorch LLaMA 3 Feed-Forward Layer", th.MUTED),
            ("import torch", th.CYAN),
            ("x = torch.randint(-128, 127, (4096,), dtype=torch.int8)", th.TEXT),
            ("W = torch.randint(-128, 127, (4096, 14336), dtype=torch.int8)", th.TEXT),
            ("y = x @ W  # GEMM Projection", th.GREEN),
            ("", th.MUTED),
            ("# Single Token Compute Budget:", th.AMBER),
            ("# ~60 Million Multiplications in <5 milliseconds!", th.RED_LIGHT),
        ]
        soft_win = th.code_window(py_code, title_text="PYTORCH: INT8 GEMM PROJECTION",
                                  width=6.2, height=3.8, font_size=13)
        soft_win.move_to(LEFT * 3.1 + DOWN * 0.4)

        # Right Panel: Silicon Area Shock
        m1 = th.metric_card("42 Gates", "Adder Silicon Area",
                            "O(N) Linear: Cheap & tiny in silicon", color=th.GREEN, width=4.8, height=1.7)
        m2 = th.metric_card("456 Gates", "Multiplier Silicon Area",
                            "O(N²) Quadratic: 10x larger and hotter!", color=th.RED, width=4.8, height=1.7)
        right_panel = VGroup(m1, m2).arrange(DOWN, buff=0.3).move_to(RIGHT * 3.3 + DOWN * 0.4)

        self.play(Create(soft_win), run_time=1.0)
        self.wait(1.0)
        self.play(FadeIn(m1, shift=UP * 0.2), FadeIn(m2, shift=UP * 0.2), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "An adder needs just 42 logic gates. But an 8-bit multiplier demands over 450 gates and consumes 90% of Tensor Core die area!"
            )),
            run_time=0.6
        )
        self.wait(2.5)

        self.play(
            FadeOut(kicker), FadeOut(soft_win), FadeOut(right_panel),
            run_time=0.5
        )

        # =====================================================================
        # ACT 2: BINARY LONG-MULTIPLICATION IN MOTION (~60s)
        # =====================================================================
        mult_title = Text("Binary Long-Multiplication & Bit Growth",
                          font=th.SANS, weight=BOLD, font_size=26, color=th.TEXT)
        mult_title.to_edge(UP, buff=0.6)
        self.play(Write(mult_title), run_time=0.6)

        self.play(
            Transform(banner, th.narration_banner(
                "How does silicon multiply numbers? It uses binary shift-and-add: multiplying bit-by-bit and shifting left."
            )),
            run_time=0.5
        )

        # 4-bit demonstration: 1011 (11) * 1101 (13) = 143 (10001111)
        calc_box = RoundedRectangle(corner_radius=0.18, width=7.2, height=3.6,
                                    stroke_color=th.BORDER, fill_color=th.CARD, fill_opacity=0.95)
        calc_box.move_to(UP * 0.45)

        t_op1 = Text("      1 0 1 1   (A = 11)", font=th.MONO, font_size=18, color=th.CYAN_LIGHT)
        t_op2 = Text("   ×  1 1 0 1   (B = 13)", font=th.MONO, font_size=18, color=th.AMBER_LIGHT)
        div_l1 = Line(LEFT * 2.8, RIGHT * 2.8, color=th.BORDER, stroke_width=2.0)

        r0 = Text("      1 0 1 1   (Shift 0)", font=th.MONO, font_size=16, color=th.TEXT)
        r1 = Text("    0 0 0 0     (Shift 1)", font=th.MONO, font_size=16, color=th.FAINT)
        r2 = Text("  1 0 1 1       (Shift 2)", font=th.MONO, font_size=16, color=th.TEXT)
        r3 = Text("1 0 1 1         (Shift 3)", font=th.MONO, font_size=16, color=th.TEXT)
        div_l2 = Line(LEFT * 2.8, RIGHT * 2.8, color=th.BORDER, stroke_width=2.0)

        prod_txt = Text("1 0 0 0 1 1 1 1   (= 143, Exactly 8 bits!)", font=th.MONO, weight=BOLD,
                        font_size=18, color=th.GREEN_LIGHT)

        math_stack = VGroup(t_op1, t_op2, div_l1, r0, r1, r2, r3, div_l2, prod_txt).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(calc_box)

        self.play(Create(calc_box), run_time=0.6)
        self.play(Write(t_op1), Write(t_op2), Create(div_l1), run_time=0.8)
        self.wait(0.5)

        # Staggered entry of partial product rows
        self.play(FadeIn(r0, shift=LEFT * 0.2), run_time=0.4)
        self.play(FadeIn(r1, shift=LEFT * 0.2), run_time=0.4)
        self.play(FadeIn(r2, shift=LEFT * 0.2), run_time=0.4)
        self.play(FadeIn(r3, shift=LEFT * 0.2), run_time=0.4)
        self.play(Create(div_l2), FadeIn(prod_txt), run_time=0.8)
        self.wait(1.5)

        # Bit growth card below
        bg_card = th.card(10.5, 1.05, stroke=th.AMBER, radius=0.15)
        bg_card.next_to(banner, UP, buff=0.22)
        bg_txt = Text("Mathematical Law: Multiplying two N-bit numbers produces a 2N-bit result! (INT8 × INT8 = INT16)",
                      font=th.MONO, weight=BOLD, font_size=13, color=th.AMBER_LIGHT).move_to(bg_card)

        self.play(Create(bg_card), FadeIn(bg_txt), run_time=0.6)
        self.play(
            Transform(banner, th.narration_banner(
                "Because 4 bits times 4 bits requires 8 bits, an 8-bit multiplier MUST output a 16-bit signed integer to prevent truncation!"
            )),
            run_time=0.6
        )
        self.wait(2.2)

        self.play(FadeOut(mult_title), FadeOut(calc_box), FadeOut(math_stack), FadeOut(bg_card), FadeOut(bg_txt), run_time=0.5)

        # =====================================================================
        # ACT 3: THE O(N^2) GATE EXPLOSION & WALLACE TREE (~70s)
        # =====================================================================
        mesh_title = Text("Inside Silicon: 64 AND Gates & Wallace-Tree Reduction",
                          font=th.SANS, weight=BOLD, font_size=26, color=th.CYAN)
        mesh_title.to_edge(UP, buff=0.6)
        self.play(Write(mesh_title), run_time=0.6)

        self.play(
            Transform(banner, th.narration_banner(
                "In silicon, every partial product bit is an AND gate: 8 x 8 = 64 simultaneous logic gates etched onto the chip."
            )),
            run_time=0.5
        )

        # 8x8 Grid of glowing AND gate dots
        dots = VGroup()
        grid_origin = LEFT * 3.2 + UP * 0.75
        for r in range(8):
            for c in range(8):
                d = Dot(point=grid_origin + RIGHT * (c * 0.42) + DOWN * (r * 0.32),
                        radius=0.07, color=th.CYAN)
                dots.add(d)

        grid_label = Text("8 × 8 = 64 Bit-Level AND Gates\n(Quadratic O(N²) Silicon Area)",
                          font=th.MONO, weight=BOLD, font_size=14, color=th.CYAN_LIGHT)
        grid_label.next_to(dots, UP, buff=0.2)

        # Right side: Wallace Tree Funnel
        funnel_box = RoundedRectangle(corner_radius=0.18, width=5.2, height=3.4,
                                      stroke_color=th.GREEN, fill_color=th.CARD, fill_opacity=0.95)
        funnel_box.move_to(RIGHT * 3.3 + DOWN * 0.3)

        f_t = Text("Wallace-Tree Reduction Funnel", font=th.SANS, weight=BOLD, font_size=15, color=th.GREEN_LIGHT)
        f_t.next_to(funnel_box.get_top(), DOWN, buff=0.2)

        st1 = Text("Stage 1: 64 bits ➔ 42 Carry-Save Adders", font=th.MONO, font_size=13, color=th.TEXT)
        st2 = Text("Stage 2: 42 bits ➔ 28 Carry-Save Adders", font=th.MONO, font_size=13, color=th.TEXT)
        st3 = Text("Stage 3: 28 bits ➔ 16 Final Sum Register", font=th.MONO, font_size=13, color=th.GREEN_LIGHT)
        st_grp = VGroup(st1, st2, st3).arrange(DOWN, aligned_edge=LEFT, buff=0.25).next_to(f_t, DOWN, buff=0.3)

        funnel_grp = VGroup(funnel_box, f_t, st_grp)

        self.play(Create(dots, lag_ratio=0.01), FadeIn(grid_label), run_time=1.0)
        self.play(Create(funnel_grp), run_time=0.8)
        self.focus_on(dots, buffer_factor=1.6, run_time=th.RATE_NORMAL)
        self.wait(0.8)

        # Animate Pachinko dots falling from 64 grid into the funnel!
        arrow_reduction = Arrow(start=dots.get_right() + RIGHT * 0.2, end=funnel_box.get_left() + LEFT * 0.2,
                                buff=0, color=th.AMBER, stroke_width=4.0)
        self.play(GrowArrow(arrow_reduction), run_time=0.6)
        LaserPacketStream.shoot_token(self, dots.get_right(), funnel_box.get_left(), color=th.AMBER, run_time=0.5)
        self.screen_shake(intensity=0.04, cycles=2, run_time=0.15)
        self.play(
            dots.animate.set_color(th.GREEN_LIGHT),
            Flash(funnel_box, color=th.GREEN, flash_radius=0.6),
            Transform(banner, th.narration_banner(
                "A Wallace Tree collapses all 64 partial products in parallel across 3 adder stages, avoiding slow ripple carries!"
            )),
            run_time=0.9
        )
        self.wait(2.2)
        self.reset_camera(run_time=th.RATE_FAST)

        self.play(
            FadeOut(mesh_title), FadeOut(dots), FadeOut(grid_label),
            FadeOut(funnel_grp), FadeOut(arrow_reduction),
            run_time=0.5
        )

        # =====================================================================
        # ACT 4: SYNTHESIZABLE SILICON ARCHITECTURE & VERIFICATION (~50s)
        # =====================================================================
        rtl_title = Text("Synthesizable Multiplier: rtl/multiplier_int8.sv",
                         font=th.SANS, weight=BOLD, font_size=26, color=th.CYAN)
        rtl_title.to_edge(UP, buff=0.6)
        self.play(Write(rtl_title), run_time=0.6)

        sv_lines = [
            ("// Parameterized Signed Hardware Multiplier:", th.MUTED),
            ("module multiplier_int8 #(", th.CYAN),
            ("    parameter int DATA_WIDTH = 8,", th.TEXT),
            ("    parameter int PROD_WIDTH = 2 * DATA_WIDTH // 16 bits", th.AMBER_LIGHT),
            (")(", th.CYAN),
            ("    input  logic signed [DATA_WIDTH-1:0] a, b,", th.TEXT),
            ("    output logic signed [PROD_WIDTH-1:0] product", th.GREEN_LIGHT),
            (");", th.CYAN),
            ("    assign product = a * b; // Synthesizes into Wallace Tree", th.GREEN),
            ("endmodule", th.CYAN),
        ]
        sv_win = th.code_window(sv_lines, title_text="RTL/MULTIPLIER_INT8.SV",
                                width=10.5, height=3.1, font_size=13, title_color=th.GREEN)
        sv_win.move_to(UP * 0.55)

        self.play(Create(sv_win), run_time=1.0)

        # Pre-Silicon Checkpoint
        check_card = th.card(10.5, 1.1, stroke=th.GREEN, radius=0.15)
        check_card.next_to(banner, UP, buff=0.22)
        check_txt = Text("✓ Cocotb Testbench: Verified against all 65,536 exhaustive input pairs! (0 Errors)",
                         font=th.MONO, weight=BOLD, font_size=14, color=th.GREEN_LIGHT).move_to(check_card)

        self.play(Create(check_card), FadeIn(check_txt), run_time=0.7)
        self.play(
            Transform(banner, th.narration_banner(
                "Next in our AI Hardware journey: Lab 02, where we fuse multiplication and addition into the MAC Unit!"
            )),
            run_time=0.6
        )
        self.wait(3.0)
