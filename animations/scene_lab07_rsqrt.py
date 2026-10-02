"""
Lab 07: Token Normalization — Fast Reciprocal Square Root (rsqrt) for RMSNorm
A kinetic, visual-first masterclass on accelerating LLaMA 3's RMSNorm in silicon.

Narrative Flow:
  Act 1: The LLaMA 3 RMSNorm Revolution (Replacing 40-cycle division loops)
  Act 2: Vector Normalization onto the Glowing Unit Sphere (r = 1.0)
  Act 3: Hybrid Hardware Architecture (Seed ROM + Digit Root + Q8.8 Scaler)
  Act 4: Synthesizable Silicon Architecture (rtl/rsqrt.sv) & Verification
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
        # ACT 1: THE RMSNORM REVOLUTION (~45s)
        # =====================================================================
        kicker, _, _ = th.header(
            "TOKEN NORMALIZATION",
            "Fast Reciprocal Square Root (rsqrt) for RMSNorm",
            title_size=30,
            badge_color=th.CYAN
        )
        self.play(FadeIn(kicker, shift=DOWN * 0.3), run_time=0.8)

        banner = th.narration_banner(
            "State-of-the-art LLMs (LLaMA 3, Mistral, Gemma) abandoned LayerNorm for RMSNorm. But computing 1 / sqrt(x) in software stalls pipelines for 40 cycles."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.7)
        self.wait(1.5)

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
        soft_win = th.code_window(py_code, title_text="PYTORCH: LLAMA 3 RMSNORM",
                                  width=6.4, height=3.8, font_size=13)
        soft_win.move_to(LEFT * 3.1 + DOWN * 0.4)

        # Right Panel: Speedup Comparison
        m1 = th.metric_card("40 Cycles", "CPU Software Division",
                            "Iterative floating-point loop stalls vector pipeline", color=th.RED, width=4.8, height=1.7)
        m2 = th.metric_card("4.6 ns", "Hardware RSQRT SFU",
                            "Combinational single-cycle throughput in silicon", color=th.GREEN, width=4.8, height=1.7)
        right_panel = VGroup(m1, m2).arrange(DOWN, buff=0.3).move_to(RIGHT * 3.3 + DOWN * 0.4)

        self.play(Create(soft_win), run_time=1.0)
        self.wait(1.0)
        self.play(FadeIn(m1, shift=UP * 0.2), FadeIn(m2, shift=UP * 0.2), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "In software, division stalls execution. In custom silicon, a dedicated SFU computes 1 / sqrt(x) in just 4.6 nanoseconds!"
            )),
            run_time=0.6
        )
        self.wait(2.5)

        self.play(FadeOut(kicker), FadeOut(soft_win), FadeOut(right_panel), run_time=0.5)

        # =====================================================================
        # ACT 2: VECTOR NORMALIZATION ONTO THE UNIT SPHERE (~60s)
        # =====================================================================
        sphere_title = Text("Visualizing RMSNorm: Snapping Tokens to the Unit Circle",
                            font=th.SANS, weight=BOLD, font_size=26, color=th.TEXT)
        sphere_title.to_edge(UP, buff=0.6)
        self.play(Write(sphere_title), run_time=0.6)

        self.play(
            Transform(banner, th.narration_banner(
                "RMSNorm keeps activation magnitudes balanced. Wild, exploding vectors are scaled down to radius 1.0."
            )),
            run_time=0.5
        )

        circle_center = UP * 0.15
        target_circle = Circle(radius=1.8, color=th.GREEN, stroke_width=3.0).move_to(circle_center)
        c_lbl = Text("Target Unit Norm (r = 1.0)", font=th.MONO, font_size=13, color=th.GREEN_LIGHT)
        c_lbl.next_to(target_circle, UP, buff=0.15)

        # 4 wild vectors exploding in length
        v1 = Arrow(start=circle_center, end=circle_center + UP * 2.4 + RIGHT * 1.5, buff=0, color=th.RED, stroke_width=4.0)
        v2 = Arrow(start=circle_center, end=circle_center + DOWN * 2.1 + LEFT * 1.6, buff=0, color=th.RED, stroke_width=4.0)
        v3 = Arrow(start=circle_center, end=circle_center + RIGHT * 2.7 + DOWN * 0.5, buff=0, color=th.AMBER, stroke_width=4.0)
        v4 = Arrow(start=circle_center, end=circle_center + LEFT * 2.5 + UP * 1.2, buff=0, color=th.AMBER, stroke_width=4.0)

        wild_vectors = VGroup(v1, v2, v3, v4)

        self.play(Create(target_circle), FadeIn(c_lbl), FadeIn(wild_vectors), run_time=1.0)
        self.focus_on(target_circle, buffer_factor=1.6, run_time=th.RATE_NORMAL)
        self.wait(0.8)

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
        self.wait(2.2)
        self.reset_camera(run_time=th.RATE_FAST)

        self.play(FadeOut(sphere_title), FadeOut(target_circle), FadeOut(c_lbl), FadeOut(wild_vectors), run_time=0.5)

        # =====================================================================
        # ACT 3: HYBRID HARDWARE ARCHITECTURE (~60s)
        # =====================================================================
        hw_title = Text("Inside Silicon: Hybrid Seed ROM + Digit Recurrence Engine",
                        font=th.SANS, weight=BOLD, font_size=26, color=th.CYAN)
        hw_title.to_edge(UP, buff=0.6)
        self.play(Write(hw_title), run_time=0.6)

        # Hybrid routing diagram
        box1 = RoundedRectangle(corner_radius=0.15, width=4.5, height=1.5,
                                stroke_color=th.AMBER, stroke_width=2.0, fill_color=th.CARD, fill_opacity=0.95).shift(LEFT * 2.8 + UP * 0.55)
        t_b1 = Text("Small Variance: x in [1, 15]\n16-Entry Seed ROM (High Precision)", font=th.MONO, font_size=13, color=th.AMBER_LIGHT).move_to(box1)

        box2 = RoundedRectangle(corner_radius=0.15, width=4.5, height=1.5,
                                stroke_color=th.GREEN, stroke_width=2.0, fill_color=th.CARD, fill_opacity=0.95).shift(RIGHT * 2.8 + UP * 0.55)
        t_b2 = Text("Large Variance: x >= 16\nDigit Engine + Q8.8 Scaler: 256 / r", font=th.MONO, font_size=13, color=th.GREEN_LIGHT).move_to(box2)

        out_box = RoundedRectangle(corner_radius=0.15, width=6.5, height=1.2,
                                   stroke_color=th.CYAN, stroke_width=2.0, fill_color=th.CARD, fill_opacity=0.95).shift(DOWN * 0.85)
        t_out = Text("Output: y_out in Q8.8 Fixed-Point Format\n(8 Integer bits + 8 Fractional bits)", font=th.MONO, font_size=14, color=th.CYAN_LIGHT).move_to(out_box)

        a_down1 = Arrow(start=box1.get_bottom(), end=out_box.get_top() + LEFT * 1.5, buff=0.1, color=th.BORDER)
        a_down2 = Arrow(start=box2.get_bottom(), end=out_box.get_top() + RIGHT * 1.5, buff=0.1, color=th.BORDER)

        arch_grp = VGroup(box1, t_b1, box2, t_b2, out_box, t_out, a_down1, a_down2)

        self.play(FadeIn(arch_grp), run_time=1.0)
        self.play(
            Transform(banner, th.narration_banner(
                "A hybrid multiplexer selects between a fast seed ROM for small numbers and a digit-recurrence engine for large numbers!"
            )),
            run_time=0.6
        )
        self.wait(2.2)

        self.play(FadeOut(hw_title), FadeOut(arch_grp), run_time=0.5)

        # =====================================================================
        # ACT 4: SYNTHESIZABLE SILICON ARCHITECTURE & VERIFICATION (~50s)
        # =====================================================================
        rtl_title = Text("Synthesizable RSQRT: rtl/rsqrt.sv",
                         font=th.SANS, weight=BOLD, font_size=26, color=th.CYAN)
        rtl_title.to_edge(UP, buff=0.6)
        self.play(Write(rtl_title), run_time=0.6)

        sv_lines = [
            ("// Parameterized Reciprocal Square Root Special Function Unit:", th.MUTED),
            ("module rsqrt #(parameter INPUT_WIDTH=16, OUTPUT_WIDTH=16)(", th.CYAN),
            ("    input  logic [INPUT_WIDTH-1:0]  x_in,", th.TEXT),
            ("    output logic [OUTPUT_WIDTH-1:0] y_out, // Q8.8 fixed-point", th.GREEN_LIGHT),
            ("    output logic                    valid_out // Zero detection", th.AMBER_LIGHT),
            (");", th.CYAN),
            ("    assign valid_out = (x_in != '0); // Prevent divide-by-zero", th.CYAN_LIGHT),
            ("    // 16-entry seed lookup + Q8.8 normalizer scaling:", th.MUTED),
            ("endmodule", th.CYAN),
        ]
        sv_win = th.code_window(sv_lines, title_text="RTL/RSQRT.SV",
                                width=10.5, height=3.3, font_size=13, title_color=th.GREEN)
        sv_win.move_to(UP * 0.55)

        self.play(Create(sv_win), run_time=1.0)

        # Pre-Silicon Checkpoint
        check_card = th.card(10.5, 1.1, stroke=th.GREEN, radius=0.15)
        check_card.next_to(banner, UP, buff=0.22)
        check_txt = Text("✓ Cocotb Testbench: Verified against PyTorch golden models across 16,384 test vectors!",
                         font=th.MONO, weight=BOLD, font_size=14, color=th.GREEN_LIGHT).move_to(check_card)

        self.play(Create(check_card), FadeIn(check_txt), run_time=0.7)
        self.play(
            Transform(banner, th.narration_banner(
                "Next in our AI Hardware journey: Lab 08, where we master the Base-2 Silicon Trick to compute SwiGLU activations!"
            )),
            run_time=0.6
        )
        self.wait(3.0)
