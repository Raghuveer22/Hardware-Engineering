"""
Lab 07: Token Normalization — Fast Reciprocal Square Root (rsqrt) for RMSNorm
A deep, visual-first masterclass on accelerating LLaMA 3's RMSNorm in silicon.
Builds bottom-up: The RMSNorm Revolution -> Snapping to the Unit Sphere ->
Seed ROM & Newton-Raphson Recurrence -> Precision Convergence Trace -> Interactive Challenge -> RTL.
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


class Lab07RSQRT(SiliconCameraRig):
    def construct(self):
        layout = self.layout
        config = HardwareConfig(data_width=8)

        # =====================================================================
        # ACT 1: THE RMSNORM REVOLUTION (~50s)
        # =====================================================================
        kicker, _, _ = th.header(
            "TOKEN NORMALIZATION",
            "Fast Reciprocal Square Root (rsqrt) for RMSNorm",
            title_size=th.FONT_TITLE,
            badge_color=th.CYAN
        )
        self.play(FadeIn(kicker, shift=DOWN * 0.3), run_time=1.0)

        banner = th.narration_banner(
            "Frontier LLMs (LLaMA 3, Mistral, Gemma) replaced LayerNorm with RMSNorm. But computing 1 / sqrt(x) in software takes 40 clock cycles."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.8)
        self.wait(5.5)

        # PyTorch Code Window on Left
        py_code = [
            ("# LLaMA 3 Root Mean Square Normalization", th.MUTED),
            ("import torch", th.CYAN),
            ("def rms_norm(x, weight, eps=1e-5):", th.TEXT),
            ("    variance = x.pow(2).mean(-1, keepdim=True)", th.AMBER_LIGHT),
            ("    # Costly reciprocal square root:", th.RED_LIGHT),
            ("    return x * torch.rsqrt(variance + eps) * weight", th.GREEN),
            ("", th.MUTED),
            ("# Software Bottleneck: 40 cycles of division per token!", th.RED),
        ]
        soft_win = th.code_window(
            py_code, title_text="PYTORCH: LLAMA 3 RMSNORM",
            width=6.4, height=3.8, font_size=th.FONT_TINY
        ).move_to(LEFT * 3.1 + DOWN * 0.4)

        # Right Panel: Speedup Comparison
        m1 = th.metric_card("40 Cycles", "CPU Software Division", "Iterative floating-point loop stalls vector pipeline", color=th.RED, width=4.8, height=1.7)
        m2 = th.metric_card("4.6 ns", "Hardware RSQRT SFU", "Combinational single-cycle throughput in silicon", color=th.GREEN, width=4.8, height=1.7)
        right_panel = VGroup(m1, m2).arrange(DOWN, buff=th.SPACE_MD).move_to(RIGHT * 3.3 + DOWN * 0.4)

        self.play(Create(soft_win), run_time=1.2)
        self.play(FadeIn(m1, shift=UP * 0.2), FadeIn(m2, shift=UP * 0.2), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "In software, division stalls execution. In custom silicon, a dedicated SFU computes 1 / sqrt(x) in just 4.6 nanoseconds!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(kicker), FadeOut(soft_win), FadeOut(right_panel), run_time=0.6)

        # =====================================================================
        # ACT 2: VECTOR NORMALIZATION ONTO THE UNIT SPHERE (~65s)
        # =====================================================================
        sphere_title = Text("Visualizing RMSNorm: Snapping Tokens to the Unit Circle",
                            font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.TEXT).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(sphere_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "RMSNorm keeps activation magnitudes balanced. Wild, exploding vectors are scaled down to radius 1.0."
            )),
            run_time=0.6
        )
        self.wait(5.0)

        circle_center = UP * 0.15
        target_circle = Circle(radius=1.8, color=th.GREEN, stroke_width=3.0).move_to(circle_center)
        c_lbl = Text("Target Unit Norm (r = 1.0)", font=th.MONO, font_size=13, color=th.GREEN_LIGHT).next_to(target_circle, UP, buff=0.15)

        # 4 wild vectors exploding in length
        v1 = Arrow(start=circle_center, end=circle_center + UP * 2.4 + RIGHT * 1.5, buff=0, color=th.RED, stroke_width=4.0)
        v2 = Arrow(start=circle_center, end=circle_center + DOWN * 2.1 + LEFT * 1.6, buff=0, color=th.RED, stroke_width=4.0)
        v3 = Arrow(start=circle_center, end=circle_center + RIGHT * 2.7 + DOWN * 0.5, buff=0, color=th.AMBER, stroke_width=4.0)
        v4 = Arrow(start=circle_center, end=circle_center + LEFT * 2.5 + UP * 1.2, buff=0, color=th.AMBER, stroke_width=4.0)

        wild_vectors = VGroup(v1, v2, v3, v4)

        self.play(Create(target_circle), FadeIn(c_lbl), FadeIn(wild_vectors), run_time=1.0)
        self.focus_on(target_circle, buffer_factor=1.6, run_time=th.RATE_NORMAL)
        self.wait(2.0)

        # Animate all 4 vectors snapping onto the unit circle!
        tv1 = Arrow(start=circle_center, end=circle_center + normalize(UP * 2.4 + RIGHT * 1.5) * 1.8, buff=0, color=th.GREEN_LIGHT, stroke_width=4.0)
        tv2 = Arrow(start=circle_center, end=circle_center + normalize(DOWN * 2.1 + LEFT * 1.6) * 1.8, buff=0, color=th.GREEN_LIGHT, stroke_width=4.0)
        tv3 = Arrow(start=circle_center, end=circle_center + normalize(RIGHT * 2.7 + DOWN * 0.5) * 1.8, buff=0, color=th.GREEN_LIGHT, stroke_width=4.0)
        tv4 = Arrow(start=circle_center, end=circle_center + normalize(LEFT * 2.5 + UP * 1.2) * 1.8, buff=0, color=th.GREEN_LIGHT, stroke_width=4.0)

        self.screen_shake(intensity=0.04, cycles=2, run_time=0.15)
        self.play(
            Transform(v1, tv1), Transform(v2, tv2), Transform(v3, tv3), Transform(v4, tv4),
            Flash(target_circle, color=th.GREEN, flash_radius=2.0),
            Transform(banner, th.narration_banner(
                "Multiplying by the hardware rsqrt pulls all activations onto the unit sphere, stabilizing deep Transformer layers!"
            )),
            run_time=0.9
        )
        self.wait(6.0)
        self.reset_camera(run_time=th.RATE_FAST)

        self.play(FadeOut(sphere_title), FadeOut(target_circle), FadeOut(c_lbl), FadeOut(wild_vectors), run_time=0.6)

        # =====================================================================
        # ACT 3: SEED ROM + NEWTON-RAPHSON ARCHITECTURE (~70s)
        # =====================================================================
        act3_title = Text("Hybrid Silicon Architecture: Seed ROM + Newton-Raphson",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.CYAN).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act3_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "How do we compute 1 / sqrt(x) without division hardware? A 32-entry Seed ROM gives an initial guess, refined by Newton-Raphson."
            )),
            run_time=0.6
        )
        self.wait(5.0)

        arch_box = RoundedRectangle(corner_radius=0.18, width=10.5, height=3.6, stroke_color=th.CYAN, fill_color=th.CARD, fill_opacity=0.95).move_to(UP * 0.3)
        s1 = Text("1. Seed Lookup: Upper 5 bits of variance index a 32-entry Seed ROM -> Initial guess y₀", font=th.MONO, font_size=13, color=th.CYAN_LIGHT)
        a1 = Arrow(UP * 0.18, DOWN * 0.18, buff=0.04, color=th.AMBER, stroke_width=2.5)
        s2 = Text("2. Newton-Raphson Iteration: y₁ = y₀ · (1.5 - 0.5 · x · y₀²)", font=th.MONO, font_size=13, color=th.AMBER_LIGHT)
        a2 = Arrow(UP * 0.18, DOWN * 0.18, buff=0.04, color=th.AMBER, stroke_width=2.5)
        s3 = Text("3. Hardware Advantage: Computed using ONLY multipliers and subtractors — ZERO dividers!", font=th.MONO, font_size=13, color=th.GREEN_LIGHT)
        a3 = Arrow(UP * 0.18, DOWN * 0.18, buff=0.04, color=th.GREEN, stroke_width=2.5)
        s4 = Text("4. Fixed-Point Precision: Formatted as Q8.8 (8 integer bits, 8 fractional bits)", font=th.MONO, weight=BOLD, font_size=14, color=th.WHITE)

        arch_grp = VGroup(s1, a1, s2, a2, s3, a3, s4).arrange(DOWN, buff=0.14).move_to(arch_box)

        self.play(Create(arch_box), FadeIn(arch_grp), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "Because Newton-Raphson doubles precision bits every step, just 1 hardware iteration brings relative error under 1%!"
            )),
            run_time=0.6
        )
        self.wait(6.5)

        self.play(FadeOut(act3_title), FadeOut(arch_box), FadeOut(arch_grp), run_time=0.6)

        # =====================================================================
        # ACT 4: PRECISION CONVERGENCE TRACE (x = 4 -> 0.5) (~70s)
        # =====================================================================
        act4_title = Text("Convergence Trace: Computing 1 / sqrt(4.0) = 0.5",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.TEXT).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act4_title), run_time=0.8)

        calc_box = RoundedRectangle(corner_radius=0.18, width=10.5, height=3.6, stroke_color=th.BORDER, fill_color=th.CARD, fill_opacity=0.95).move_to(UP * 0.3)

        l1 = Text("Input Radicand (x):       16'd4  (Exact decimal: 4.0)", font=th.MONO, font_size=14, color=th.CYAN_LIGHT)
        l2 = Text("Seed ROM Lookup (y₀):     8'h7B  (Decimal: 0.4800, coarse approximation)", font=th.MONO, font_size=13, color=th.AMBER_LIGHT)
        l3 = Text("Step A: Compute 0.5 · x · y₀² = 0.5 · 4.0 · 0.2304 = 0.4608", font=th.MONO, font_size=13, color=th.TEXT)
        l4 = Text("Step B: Compute (1.5 - 0.4608) = 1.0392", font=th.MONO, font_size=13, color=th.TEXT)
        l5 = Text("Refined Output (y₁):      y₀ · 1.0392 = 0.4998 ≈ 0.5000 (Error: 0.04%!)", font=th.MONO, weight=BOLD, font_size=15, color=th.GREEN_LIGHT)
        l6 = Text("Q8.8 Representation:      16'h0080 (Exact binary representation of 0.5)", font=th.MONO, font_size=13, color=th.WHITE)

        calc_grp = VGroup(l1, l2, l3, l4, l5, l6).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(calc_box)

        self.play(Create(calc_box), FadeIn(calc_grp), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "In just 1 iteration, the result converges from 0.48 to 0.4998: indistinguishable from true 1/sqrt(4) in 8-bit precision!"
            )),
            run_time=0.6
        )
        self.wait(6.5)

        self.play(FadeOut(act4_title), FadeOut(calc_box), FadeOut(calc_grp), run_time=0.6)

        # =====================================================================
        # ACT 5: INTERACTIVE CHECKPOINT & MATH CHALLENGE (~45s)
        # =====================================================================
        act5_title = Text("Architectural Checkpoint: The Q8.8 Binary Fixed-Point",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.AMBER).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act5_title), run_time=0.8)

        chal_card = th.card(10.5, 3.0, stroke=th.AMBER, radius=0.16).move_to(UP * 0.4)
        c_q = Text("PAUSE & CALCULATE: FIXED-POINT RSQRT", font=th.MONO, weight=BOLD, font_size=15, color=th.AMBER_LIGHT)
        c_m1 = Text("If the input variance is x = 16, 1/sqrt(16) = 0.25.", font=th.SANS, font_size=18, color=th.TEXT)
        c_m2 = Text("What is 0.25 represented in Q8.8 fixed-point format (where 1.0 = 256)?", font=th.SANS, font_size=18, color=th.TEXT)
        chal_grp = VGroup(c_q, c_m1, c_m2).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(chal_card)

        self.play(Create(chal_card), FadeIn(chal_grp), run_time=1.0)
        self.play(
            Transform(banner, th.narration_banner(
                "Pause the video: multiply 0.25 by 256. What is the hex value latched into the output register?"
            )),
            run_time=0.6
        )
        self.wait(7.0)

        ans_card = th.card(10.5, 1.4, stroke=th.GREEN, radius=0.14).next_to(chal_card, DOWN, buff=0.3)
        ans_t1 = Text("0.25 × 256 = 64 = 16'h0040 = 'b0000_0000_0100_0000", font=th.MONO, weight=BOLD, font_size=15, color=th.GREEN_LIGHT)
        ans_t2 = Text("Bit 6 is 1 (representing 2⁻² = 0.25). Exact fixed-point representation!", font=th.MONO, font_size=13, color=th.TEXT)
        ans_box = VGroup(ans_t1, ans_t2).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(ans_card)

        self.play(Create(ans_card), FadeIn(ans_box), run_time=0.8)
        self.wait(6.5)

        self.play(FadeOut(act5_title), FadeOut(chal_card), FadeOut(chal_grp), FadeOut(ans_card), FadeOut(ans_box), run_time=0.6)

        # =====================================================================
        # ACT 6: SYNTHESIZABLE SILICON ARCHITECTURE & VERIFICATION (~45s)
        # =====================================================================
        rtl_title = Text("Synthesizable Silicon: rtl/rsqrt.sv",
                         font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.CYAN).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(rtl_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "Here is the synthesizable RSQRT unit: Seed ROM lookup followed by a pipelined Newton-Raphson datapath."
            )),
            run_time=0.6
        )

        sv_lines = [
            ("module rsqrt #(parameter DATA_WIDTH = 16, Q_FRAC = 8)(", th.CYAN),
            ("    input  logic [DATA_WIDTH-1:0] radicand_in,", th.TEXT),
            ("    output logic [DATA_WIDTH-1:0] rsqrt_out", th.GREEN_LIGHT),
            (");", th.CYAN),
            ("    // 1. Seed ROM Lookup from upper 5 bits:", th.MUTED),
            ("    assign seed_val = seed_rom[radicand_in[15:11]];", th.CYAN_LIGHT),
            ("    // 2. Newton-Raphson Refinement: y1 = y0 * (1.5 - 0.5 * x * y0^2)", th.MUTED),
            ("    always_comb begin", th.CYAN),
            ("        y_sq    = (seed_val * seed_val) >> Q_FRAC;", th.TEXT),
            ("        term    = (radicand_in * y_sq) >> (Q_FRAC + 1);", th.TEXT),
            ("        rsqrt_out = (seed_val * (FIXED_1_5 - term)) >> Q_FRAC;", th.GREEN_LIGHT),
            ("    end", th.CYAN),
            ("endmodule", th.CYAN),
        ]
        sv_win = th.code_window(
            sv_lines, title_text="RTL/RSQRT.SV: SEED ROM & NEWTON-RAPHSON",
            width=10.2, height=3.3, font_size=th.FONT_TINY, title_color=th.GREEN
        ).move_to(UP * 0.45)

        self.play(Create(sv_win), run_time=1.0)
        self.wait(5.0)

        # Pre-Silicon Checkpoint
        check_card = th.card(10.2, 1.2, stroke=th.GREEN, radius=0.15).move_to(DOWN * 1.5)
        check_txt = Text("✓ Cocotb Python Golden Model: Relative Error < 0.8% Across All Valid Variances (0 Division Gates)",
                         font=th.MONO, weight=BOLD, font_size=13, color=th.GREEN_LIGHT).move_to(check_card)

        self.play(Create(check_card), FadeIn(check_txt), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "Next in our AI Hardware journey: Lab 08, where we build the Base-2 Exponential SFU for SwiGLU activations!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(rtl_title), FadeOut(sv_win), FadeOut(check_card), FadeOut(check_txt), FadeOut(banner), run_time=1.0)
        self.wait(1.0)
