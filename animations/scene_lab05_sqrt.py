"""
Lab 05: Scaled Attention — Hardware Square Root Unit & Attention Variance Scaling
A kinetic, visual-first masterclass on transformer scaling factors in silicon.

Narrative Flow:
  Act 1: The Scaled Dot-Product Attention Crisis (Softmax Gradient Collapse)
  Act 2: Taming Attention Variance (1 / sqrt(d_k) restoring Gaussian gradients)
  Act 3: Digit-by-Digit Hardware Root Engine (16-bit shift-and-subtract)
  Act 4: Synthesizable Silicon Architecture (rtl/sqrt.sv) & Verification
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


class Lab05SquareRoot(SiliconCameraRig):
    def construct(self):
        layout = self.layout
        config = HardwareConfig(data_width=8)

        # =====================================================================
        # ACT 1: THE ATTENTION VARIANCE CRISIS (~45s)
        # =====================================================================
        kicker, _, _ = th.header(
            "SCALED ATTENTION",
            "Why Transformers Require Hardware Square Root",
            title_size=30,
            badge_color=th.CYAN
        )
        self.play(FadeIn(kicker, shift=DOWN * 0.3), run_time=0.8)

        banner = th.narration_banner(
            "In Transformers, self-attention scales linearly with embedding dimension d_k. Without scaling, attention completely breaks."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.7)
        self.wait(1.5)

        # PyTorch Code Window on Left
        py_code = [
            ("# Transformer Attention Scaling", th.MUTED),
            ("import torch", th.CYAN),
            ("d_k = 128  # Head Dimension in LLaMA", th.TEXT),
            ("raw_scores = Q @ K.T  # Variance = 128!", th.AMBER),
            ("scaled_scores = raw_scores / math.sqrt(d_k)", th.GREEN),
            ("", th.MUTED),
            ("# Without 1/sqrt(d_k):", th.RED),
            ("# Logits explode -> Softmax gradients vanish to 0!", th.RED_LIGHT),
        ]
        soft_win = th.code_window(py_code, title_text="PYTORCH: ATTENTION SCALING",
                                  width=6.2, height=3.8, font_size=13)
        soft_win.move_to(LEFT * 3.1 + DOWN * 0.4)

        # Right Panel: Gradient Collapse Shock
        m1 = th.metric_card("128.0", "Unscaled Variance",
                            "Variance grows linearly with head dimension d_k", color=th.RED, width=4.8, height=1.7)
        m2 = th.metric_card("1.0", "Normalized Variance",
                            "Scaled by 1/sqrt(d_k) to prevent saturation", color=th.GREEN, width=4.8, height=1.7)
        right_panel = VGroup(m1, m2).arrange(DOWN, buff=0.3).move_to(RIGHT * 3.3 + DOWN * 0.4)

        self.play(Create(soft_win), run_time=1.0)
        self.wait(1.0)
        self.play(FadeIn(m1, shift=UP * 0.2), FadeIn(m2, shift=UP * 0.2), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "When d_k is 128, dot products grow so large that Softmax saturates into a dead needle, causing gradients to vanish!"
            )),
            run_time=0.6
        )
        self.wait(2.5)

        self.play(FadeOut(kicker), FadeOut(soft_win), FadeOut(right_panel), run_time=0.5)

        # =====================================================================
        # ACT 2: DIGIT-BY-DIGIT HARDWARE ROOT ENGINE (~60s)
        # =====================================================================
        rt_title = Text("Inside Silicon: Digit-by-Digit Root Engine",
                        font=th.SANS, weight=BOLD, font_size=26, color=th.TEXT)
        rt_title.to_edge(UP, buff=0.6)
        self.play(Write(rt_title), run_time=0.6)

        self.play(
            Transform(banner, th.narration_banner(
                "How does silicon compute square roots without floating-point math? An unrolled non-restoring shift-and-subtract pipeline."
            )),
            run_time=0.5
        )

        # Shift register visual for d_k = 64 -> root = 8
        calc_box = RoundedRectangle(corner_radius=0.18, width=10.0, height=3.2,
                                    stroke_color=th.BORDER, fill_color=th.CARD, fill_opacity=0.95)
        calc_box.move_to(UP * 0.4)

        l1 = Text("Radicand Input (d_k): 16'd64  [0000 0000 0100 0000]", font=th.MONO, font_size=15, color=th.CYAN_LIGHT)
        l2 = Text("Hardware Process: Shifts 2 bits left per stage, trial subtraction", font=th.MONO, font_size=14, color=th.WHITE)
        l3 = Text("Root Output:      8'd8   [0000 1000] (Exact integer root)", font=th.MONO, weight=BOLD, font_size=16, color=th.GREEN_LIGHT)
        l4 = Text("Remainder:        16'd0  (Zero residual error)", font=th.MONO, font_size=14, color=th.AMBER_LIGHT)

        calc_stack = VGroup(l1, l2, l3, l4).arrange(DOWN, aligned_edge=LEFT, buff=0.28).move_to(calc_box)

        self.play(Create(calc_box), FadeIn(calc_stack), run_time=1.0)
        self.focus_on(calc_box, buffer_factor=1.4, run_time=th.RATE_NORMAL)
        LaserPacketStream.shoot_token(self, calc_box.get_left() + LEFT * 1.2, calc_box.get_left(), color=th.CYAN, run_time=0.5)
        self.screen_shake(intensity=0.03, cycles=2, run_time=0.15)
        self.play(
            Transform(banner, th.narration_banner(
                "In 8 unrolled combinational stages, the hardware extracts 1 bit of root per step: sqrt(64) = 8, with zero remainder!"
            )),
            run_time=0.6
        )
        self.wait(2.2)
        self.reset_camera(run_time=th.RATE_FAST)

        self.play(FadeOut(rt_title), FadeOut(calc_box), FadeOut(calc_stack), run_time=0.5)

        # =====================================================================
        # ACT 3: SYNTHESIZABLE SILICON ARCHITECTURE & VERIFICATION (~50s)
        # =====================================================================
        rtl_title = Text("Synthesizable Root Unit: rtl/sqrt.sv",
                         font=th.SANS, weight=BOLD, font_size=26, color=th.CYAN)
        rtl_title.to_edge(UP, buff=0.6)
        self.play(Write(rtl_title), run_time=0.6)

        sv_lines = [
            ("// Digit-by-Digit Hardware Square Root Engine:", th.MUTED),
            ("module sqrt #(parameter RADICAND_WIDTH=16, ROOT_WIDTH=8)(", th.CYAN),
            ("    input  logic [RADICAND_WIDTH-1:0] radicand,", th.TEXT),
            ("    output logic [ROOT_WIDTH-1:0]     root,", th.GREEN_LIGHT),
            ("    output logic [RADICAND_WIDTH-1:0] remainder", th.AMBER_LIGHT),
            (");", th.CYAN),
            ("    // Unrolled non-restoring shift-and-subtract loop:", th.MUTED),
            ("    always_comb begin ... root_reg[i] = 1'b1; ... end", th.CYAN_LIGHT),
            ("endmodule", th.CYAN),
        ]
        sv_win = th.code_window(sv_lines, title_text="RTL/SQRT.SV",
                                width=10.5, height=3.0, font_size=13, title_color=th.GREEN)
        sv_win.move_to(UP * 0.55)

        self.play(Create(sv_win), run_time=1.0)

        # Pre-Silicon Checkpoint
        check_card = th.card(10.5, 1.1, stroke=th.GREEN, radius=0.15)
        check_card.next_to(banner, UP, buff=0.22)
        check_txt = Text("✓ Cocotb Testbench: Verified against all 65,536 radicand integers! (0 Root Errors)",
                         font=th.MONO, weight=BOLD, font_size=14, color=th.GREEN_LIGHT).move_to(check_card)

        self.play(Create(check_card), FadeIn(check_txt), run_time=0.7)
        self.play(
            Transform(banner, th.narration_banner(
                "Next in our AI Hardware journey: Lab 06, where we build the Safe Softmax Engine and tame the e^50 overflow!"
            )),
            run_time=0.6
        )
        self.wait(3.0)
