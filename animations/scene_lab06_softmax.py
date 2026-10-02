"""
Lab 06: The Probability Engine — Safe Softmax & FlashAttention
A deep, visual-first masterclass on Transformer Attention non-linear acceleration.
Builds bottom-up: The e^50 Exponential Rocket Overflow -> The Safe Softmax Invariant ->
3-Pass Silicon Datapath & Q0.8 LUT -> FlashAttention Online Softmax -> Interactive Challenge -> RTL.
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


class Lab06Softmax(SiliconCameraRig):
    def construct(self):
        layout = self.layout
        config = HardwareConfig(data_width=8)

        # =====================================================================
        # ACT 1: THE ATTENTION HOOK & ROCKET OVERFLOW (~50s)
        # =====================================================================
        kicker, _, _ = th.header(
            "THE PROBABILITY ENGINE",
            "Safe Softmax & FlashAttention in Silicon",
            title_size=th.FONT_TITLE,
            badge_color=th.CYAN
        )
        self.play(FadeIn(kicker, shift=DOWN * 0.3), run_time=1.0)

        banner = th.narration_banner(
            "In Transformers, Softmax converts raw attention scores into probabilities. But calculating raw exponentials causes an instant silicon crisis."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.8)
        self.wait(5.5)

        # PyTorch Code Window on Left
        py_code = [
            ("# PyTorch Transformer Self-Attention", th.MUTED),
            ("import torch", th.CYAN),
            ("scores = (Q @ K.T) / sqrt(d_k)", th.TEXT),
            ("logits = torch.tensor([2.0, 5.0, 1.0, 50.0])", th.AMBER),
            ("probs  = torch.softmax(logits, dim=-1)", th.GREEN),
            ("", th.MUTED),
            ("# The Silicon Reality:", th.RED),
            ("# e^50 ≈ 5.18 × 10²¹  ➔  OVERFLOWS ANY 64-BIT REGISTER!", th.RED_LIGHT),
        ]
        soft_win = th.code_window(
            py_code, title_text="PYTORCH: ATTENTION SOFTMAX",
            width=6.2, height=3.8, font_size=th.FONT_TINY
        ).move_to(LEFT * 3.1 + DOWN * 0.4)

        # Right Panel: Rocket Bar Chart with values [2.0, 5.0, 1.0, 50.0]
        chart = th.DynamicBarChartWidget(
            values=[2.0, 5.0, 1.0, 50.0],
            labels=["x0", "x1", "x2", "x3 (50.0)"],
            max_val=50.0,
            chart_width=5.0,
            chart_height=3.0,
            bar_color=th.CYAN
        ).move_to(RIGHT * 3.3 + DOWN * 0.4)

        chart.bars[3].set_fill(th.RED, opacity=0.85).set_stroke(th.RED_LIGHT, width=2.5)

        self.play(Create(soft_win), run_time=1.2)
        self.play(Create(chart), run_time=1.0)

        ceiling_line = Line(RIGHT * 0.8 + UP * 1.5, RIGHT * 5.8 + UP * 1.5, color=th.RED, stroke_width=2.5)
        ceiling_label = Text("MAX 64-BIT REGISTER CAPACITY", font=th.MONO, weight=BOLD, font_size=11, color=th.RED).next_to(ceiling_line, UP, buff=0.1)

        self.play(Create(ceiling_line), FadeIn(ceiling_label), run_time=0.6)
        self.play(
            chart.bars[3].animate.stretch_to_fit_height(4.2).shift(UP * 0.6),
            Flash(chart.bars[3].get_top(), color=th.RED, flash_radius=0.6),
            Transform(banner, th.narration_banner(
                "When a logit reaches 50, e^50 explodes to 5 sextillion! It blows through any register capacity, producing NaN!"
            )),
            run_time=0.9
        )
        self.screen_shake(intensity=0.08, cycles=3, run_time=0.25)
        self.wait(6.0)

        self.play(FadeOut(kicker), FadeOut(soft_win), FadeOut(chart),
                  FadeOut(ceiling_line), FadeOut(ceiling_label), run_time=0.6)

        # =====================================================================
        # ACT 2: THE SAFE SOFTMAX INVARIANT (~65s)
        # =====================================================================
        safe_title = Text("The Silicon Solution: Safe Softmax (Subtract the Max)",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.GREEN_LIGHT).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(safe_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "Because Softmax is scale-invariant, we can subtract the vector maximum from every element: Delta_i = x_i - max(X)."
            )),
            run_time=0.6
        )
        self.wait(5.0)

        chart_shifted = th.DynamicBarChartWidget(
            values=[0.5, 1.2, 0.2, 3.0],
            labels=["Δ0 (-48)", "Δ1 (-45)", "Δ2 (-49)", "Δ3 (0.0)"],
            max_val=3.0,
            chart_width=6.0,
            chart_height=2.4,
            bar_color=th.GREEN
        ).move_to(UP * 0.55)

        formula_card = th.card(10.5, 1.2, stroke=th.CYAN, radius=0.15).next_to(banner, UP, buff=0.22)
        form_txt = Text("Δ_i = x_i - max(X)  ≤  0  ===>  e^(Δ_i) is STRICTLY BOUNDED in (0.0, 1.0] !",
                        font=th.MONO, weight=BOLD, font_size=15, color=th.CYAN_LIGHT).move_to(formula_card)

        self.play(Create(chart_shifted), Create(formula_card), FadeIn(form_txt), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "Every shifted logit Delta_i is less than or equal to 0. Therefore e^(Delta_i) is bounded between 0 and 1. Zero overflow guarantee!"
            )),
            run_time=0.6
        )
        self.wait(6.5)

        self.play(FadeOut(safe_title), FadeOut(chart_shifted), FadeOut(formula_card), FadeOut(form_txt), run_time=0.6)

        # =====================================================================
        # ACT 3: THE 3-PASS SILICON DATAPATH (~70s)
        # =====================================================================
        act3_title = Text("The 3-Pass Silicon Datapath Architecture",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.CYAN).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act3_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "In silicon, Safe Softmax evaluates in 3 structured streaming passes through an on-chip pipeline."
            )),
            run_time=0.6
        )
        self.wait(5.0)

        dp_box = RoundedRectangle(corner_radius=0.18, width=10.5, height=3.6, stroke_color=th.CYAN, fill_color=th.CARD, fill_opacity=0.95).move_to(UP * 0.3)
        p1 = Text("Pass 1: Stream vector -> Comparator tree finds vector max: m = max(X)", font=th.MONO, font_size=13, color=th.AMBER_LIGHT)
        a1 = Arrow(UP * 0.18, DOWN * 0.18, buff=0.04, color=th.AMBER, stroke_width=2.5)
        p2 = Text("Pass 2: Subtract m -> Lookup e^(Δ_i) in 256-entry Q0.8 LUT -> Accumulator sums S = Σ e^(Δ_i)", font=th.MONO, font_size=13, color=th.CYAN_LIGHT)
        a2 = Arrow(UP * 0.18, DOWN * 0.18, buff=0.04, color=th.CYAN, stroke_width=2.5)
        p3 = Text("Pass 3: Multiply each e^(Δ_i) by reciprocal (1/S) -> Output normalized probability P_i ∈ [0, 1]", font=th.MONO, font_size=13, color=th.GREEN_LIGHT)
        dp_flow = VGroup(p1, a1, p2, a2, p3).arrange(DOWN, buff=0.18).move_to(dp_box)

        self.play(Create(dp_box), FadeIn(dp_flow), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "A 256-entry lookup ROM in Q0.8 fixed point replaces the complex exponential function with 1-cycle latency!"
            )),
            run_time=0.6
        )
        self.wait(6.5)

        self.play(FadeOut(act3_title), FadeOut(dp_box), FadeOut(dp_flow), run_time=0.6)

        # =====================================================================
        # ACT 4: FLASHATTENTION ONLINE SOFTMAX TILING (~70s)
        # =====================================================================
        act4_title = Text("The FlashAttention Breakthrough: Online Softmax",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.AMBER).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act4_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "Standard 3-pass Softmax requires reading from DRAM 3 times. FlashAttention solves this with Online Softmax."
            )),
            run_time=0.6
        )
        self.wait(5.0)

        fa_card1 = th.card(5.6, 3.6, stroke=th.RED, radius=0.16).move_to(LEFT * 3.1 + DOWN * 0.35)
        fa_h1 = Text("STANDARD SOFTMAX (DRAM WALL)", font=th.SANS, weight=BOLD, font_size=14, color=th.RED_LIGHT).next_to(fa_card1.get_top(), DOWN, buff=0.2)
        fa_l1 = th.bullets(
            ["Requires 3 separate passes",
             "Materializes N × N matrix in DRAM",
             "Memory bandwidth bottleneck",
             "High energy consumption"],
            color=th.TEXT, font_size=13, bullet_color=th.RED, buff=0.22
        ).next_to(fa_h1, DOWN, buff=0.2, aligned_edge=LEFT).move_to(fa_card1.get_center() + DOWN * 0.15)

        fa_card2 = th.card(5.6, 3.6, stroke=th.GREEN, radius=0.16).move_to(RIGHT * 3.1 + DOWN * 0.35)
        fa_h2 = Text("FLASHATTENTION (SRAM TILING)", font=th.SANS, weight=BOLD, font_size=14, color=th.GREEN_LIGHT).next_to(fa_card2.get_top(), DOWN, buff=0.2)
        fa_l2 = th.bullets(
            ["Online Max tracking: m_new = max(m, x)",
             "Rescales running sum: S_new = S·e^(m - m_new) + e^(x - m_new)",
             "Fits inside fast on-chip SRAM",
             "Zero N × N DRAM round trips!"],
            color=th.TEXT, font_size=13, bullet_color=th.GREEN, buff=0.22
        ).next_to(fa_h2, DOWN, buff=0.2, aligned_edge=LEFT).move_to(fa_card2.get_center() + DOWN * 0.15)

        self.play(Create(fa_card1), FadeIn(fa_h1), FadeIn(fa_l1),
                  Create(fa_card2), FadeIn(fa_h2), FadeIn(fa_l2), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "Online Safe Softmax rescales the running accumulator dynamically, enabling SRAM tiling without overflowing registers!"
            )),
            run_time=0.6
        )
        self.wait(6.5)

        self.play(FadeOut(act4_title), FadeOut(fa_card1), FadeOut(fa_h1), FadeOut(fa_l1),
                  FadeOut(fa_card2), FadeOut(fa_h2), FadeOut(fa_l2), run_time=0.6)

        # =====================================================================
        # ACT 5: INTERACTIVE CHECKPOINT & MATH CHALLENGE (~45s)
        # =====================================================================
        act5_title = Text("Architectural Checkpoint: The 3-Logit Challenge",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.AMBER).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act5_title), run_time=0.8)

        chal_card = th.card(10.5, 3.0, stroke=th.AMBER, radius=0.16).move_to(UP * 0.4)
        c_q = Text("PAUSE & CALCULATE: SAFE SOFTMAX SHIFT", font=th.MONO, weight=BOLD, font_size=15, color=th.AMBER_LIGHT)
        c_m1 = Text("Given input vector X = [-2.0, 0.0, 3.0]:", font=th.SANS, font_size=18, color=th.TEXT)
        c_m2 = Text("1) What is max(X)? 2) What are shifted deltas? 3) What is max e^(Δ_i)?", font=th.SANS, font_size=18, color=th.TEXT)
        chal_grp = VGroup(c_q, c_m1, c_m2).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(chal_card)

        self.play(Create(chal_card), FadeIn(chal_grp), run_time=1.0)
        self.play(
            Transform(banner, th.narration_banner(
                "Pause the video: find max(X), compute Delta = X - max(X), and verify that all exponential terms are <= 1.0."
            )),
            run_time=0.6
        )
        self.wait(7.0)

        ans_card = th.card(10.5, 1.4, stroke=th.GREEN, radius=0.14).next_to(chal_card, DOWN, buff=0.3)
        ans_t1 = Text("1) max(X) = 3.0   2) Deltas = [-5.0, -3.0, 0.0]", font=th.MONO, weight=BOLD, font_size=15, color=th.GREEN_LIGHT)
        ans_t2 = Text("3) e^(0.0) = 1.0 (Maximum possible value). Perfect stability in fixed point!", font=th.MONO, font_size=13, color=th.TEXT)
        ans_box = VGroup(ans_t1, ans_t2).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(ans_card)

        self.play(Create(ans_card), FadeIn(ans_box), run_time=0.8)
        self.wait(6.5)

        self.play(FadeOut(act5_title), FadeOut(chal_card), FadeOut(chal_grp), FadeOut(ans_card), FadeOut(ans_box), run_time=0.6)

        # =====================================================================
        # ACT 6: SYNTHESIZABLE SILICON ARCHITECTURE & VERIFICATION (~45s)
        # =====================================================================
        rtl_title = Text("Synthesizable Silicon: rtl/softmax.sv",
                         font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.CYAN).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(rtl_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "Here is the synthesizable Softmax engine: an on-chip max tracker, exponential LUT, and reciprocal multiplier."
            )),
            run_time=0.6
        )

        sv_lines = [
            ("module softmax #(parameter int VECTOR_SIZE = 4, DATA_WIDTH = 8)(", th.CYAN),
            ("    input  logic signed [DATA_WIDTH-1:0] in_vector [VECTOR_SIZE],", th.TEXT),
            ("    output logic        [DATA_WIDTH-1:0] out_prob  [VECTOR_SIZE]", th.GREEN_LIGHT),
            (");", th.CYAN),
            ("    // 1. Combinational Max Tree:", th.MUTED),
            ("    assign max_val = find_max(in_vector);", th.AMBER_LIGHT),
            ("    // 2. Exponential Lookup & Normalization in Q0.8:", th.MUTED),
            ("    always_comb begin", th.CYAN),
            ("        for (int i=0; i<VECTOR_SIZE; i++)", th.TEXT),
            ("            exp_lut_out[i] = exp_lut_table[in_vector[i] - max_val];", th.CYAN_LIGHT),
            ("    end", th.CYAN),
            ("endmodule", th.CYAN),
        ]
        sv_win = th.code_window(
            sv_lines, title_text="RTL/SOFTMAX.SV: ON-CHIP SAFE SOFTMAX",
            width=10.2, height=3.3, font_size=th.FONT_TINY, title_color=th.GREEN
        ).move_to(UP * 0.45)

        self.play(Create(sv_win), run_time=1.0)
        self.wait(5.0)

        # Pre-Silicon Checkpoint
        check_card = th.card(10.2, 1.2, stroke=th.GREEN, radius=0.15).move_to(DOWN * 1.5)
        check_txt = Text("✓ Cocotb Python Golden Model: Numerical Probability Sum Verified to 1.0 (0 Overflow Errors)",
                         font=th.MONO, weight=BOLD, font_size=13, color=th.GREEN_LIGHT).move_to(check_card)

        self.play(Create(check_card), FadeIn(check_txt), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "Next in our AI Hardware journey: Lab 07, where we build the Fast RSQRT Engine for LLaMA-3 RMSNorm!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(rtl_title), FadeOut(sv_win), FadeOut(check_card), FadeOut(check_txt), FadeOut(banner), run_time=1.0)
        self.wait(1.0)
