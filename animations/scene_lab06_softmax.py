"""
Lab 06: The Probability Engine — Safe Softmax & FlashAttention
A kinetic, visual-first masterclass on Transformer Attention non-linear acceleration.

Narrative Flow:
  Act 1: The PyTorch Attention Hook & The Rocket Logit Overflow (e^50 explosion)
  Act 2: The Safe Softmax Clamp (Pulling all logits down by max(X) <= 0)
  Act 3: 4-Stage Hardware Datapath & Liquid Probability Normalizer (Q0.8 domain)
  Act 4: Synthesizable Silicon Gates (rtl/softmax.sv) & FlashAttention Tiling
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
        # ACT 1: THE ATTENTION HOOK & ROCKET OVERFLOW (~45s)
        # =====================================================================
        kicker, _, _ = th.header(
            "THE PROBABILITY ENGINE",
            "Safe Softmax & FlashAttention in Silicon",
            title_size=30,
            badge_color=th.CYAN
        )
        self.play(FadeIn(kicker, shift=DOWN * 0.3), run_time=0.8)

        banner = th.narration_banner(
            "In Transformers, Softmax converts raw attention scores into probabilities. But calculating raw exponentials causes an instant silicon crisis."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.7)
        self.wait(1.5)

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
        soft_win = th.code_window(py_code, title_text="PYTORCH: ATTENTION SOFTMAX",
                                  width=6.2, height=3.8, font_size=13)
        soft_win.move_to(LEFT * 3.1 + DOWN * 0.4)

        # Right Panel: Rocket Bar Chart with values [2.0, 5.0, 1.0, 50.0]
        chart = th.DynamicBarChartWidget(
            values=[2.0, 5.0, 1.0, 50.0],
            labels=["x0", "x1", "x2", "x3 (50.0)"],
            max_val=50.0,
            chart_width=5.0,
            chart_height=3.0,
            bar_color=th.CYAN
        )
        chart.move_to(RIGHT * 3.3 + DOWN * 0.4)

        # Turn bar 3 (50.0) bright red
        chart.bars[3].set_fill(th.RED, opacity=0.85).set_stroke(th.RED_LIGHT, width=2.5)

        self.play(Create(soft_win), run_time=1.0)
        self.play(Create(chart), run_time=1.0)
        self.wait(1.0)

        # Animate bar 3 blasting off like a rocket through the ceiling!
        ceiling_line = Line(RIGHT * 0.8 + UP * 1.5, RIGHT * 5.8 + UP * 1.5,
                            color=th.RED, stroke_width=2.5)
        ceiling_label = Text("MAX 64-BIT REGISTER CAPACITY", font=th.MONO,
                             weight=BOLD, font_size=12, color=th.RED)
        ceiling_label.next_to(ceiling_line, UP, buff=0.1)

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
        self.wait(2.2)

        self.play(
            FadeOut(kicker), FadeOut(soft_win), FadeOut(chart),
            FadeOut(ceiling_line), FadeOut(ceiling_label),
            run_time=0.5
        )

        # =====================================================================
        # ACT 2: THE SAFE SOFTMAX MATHEMATICAL CLAMP (~60s)
        # =====================================================================
        safe_title = Text("The Silicon Solution: Safe Softmax (Subtract the Max)",
                          font=th.SANS, weight=BOLD, font_size=26, color=th.GREEN_LIGHT)
        safe_title.to_edge(UP, buff=0.6)
        self.play(Write(safe_title), run_time=0.6)

        self.play(
            Transform(banner, th.narration_banner(
                "Because Softmax is scale-invariant, we can subtract the vector maximum from every element: Delta = x - max(X)."
            )),
            run_time=0.5
        )

        # Shifted Bar Chart: Delta values [-48.0, -45.0, -49.0, 0.0]
        # Shows bars hanging down or grounded at zero!
        chart_shifted = th.DynamicBarChartWidget(
            values=[0.5, 1.2, 0.2, 3.0], # scaled visual representation
            labels=["Δ0 (-48)", "Δ1 (-45)", "Δ2 (-49)", "Δ3 (0.0)"],
            max_val=3.0,
            chart_width=6.0,
            chart_height=2.4,
            bar_color=th.GREEN
        )
        chart_shifted.move_to(UP * 0.55)

        formula_card = th.card(10.5, 1.1, stroke=th.CYAN, radius=0.15)
        formula_card.next_to(banner, UP, buff=0.22)
        form_txt = Text("Δ_i = x_i - max(X)  ≤  0  ===>  e^(Δ_i) is STRICTLY BOUNDED in (0.0, 1.0] !",
                        font=th.MONO, weight=BOLD, font_size=16, color=th.CYAN_LIGHT).move_to(formula_card)

        self.play(Create(chart_shifted), run_time=1.0)
        self.play(Create(formula_card), FadeIn(form_txt), run_time=0.7)
        self.play(
            Transform(banner, th.narration_banner(
                "Notice the magic: every single delta is now zero or negative! Exponentiating a negative number NEVER exceeds 1.0!"
            )),
            run_time=0.6
        )
        self.wait(2.5)

        self.play(
            FadeOut(safe_title), FadeOut(chart_shifted),
            FadeOut(formula_card), FadeOut(form_txt),
            run_time=0.5
        )

        # =====================================================================
        # ACT 3: 4-STAGE HARDWARE DATAPATH & Q0.8 PROBABILITIES (~70s)
        # =====================================================================
        pipe_title = Text("Inside the Silicon: 4-Stage Hardware Softmax Datapath",
                          font=th.SANS, weight=BOLD, font_size=26, color=th.TEXT)
        pipe_title.to_edge(UP, buff=0.6)
        self.play(Write(pipe_title), run_time=0.6)

        self.play(
            Transform(banner, th.narration_banner(
                "In silicon (rtl/softmax.sv), the engine evaluates all 4 stages in a continuous high-speed combinational wave."
            )),
            run_time=0.5
        )

        # 4 Physical Hardware Pipeline Slices
        s1 = RoundedRectangle(corner_radius=0.15, width=2.4, height=1.5,
                              stroke_color=th.AMBER, stroke_width=2.0, fill_color=th.CARD, fill_opacity=0.95).shift(LEFT * 4.2 + UP * 0.45)
        lbl1 = Text("STAGE 1\nComparator Tree\nmax(X) = 50", font=th.MONO, font_size=13, color=th.AMBER_LIGHT).move_to(s1)

        s2 = RoundedRectangle(corner_radius=0.15, width=2.4, height=1.5,
                              stroke_color=th.CYAN, stroke_width=2.0, fill_color=th.CARD, fill_opacity=0.95).shift(LEFT * 1.4 + UP * 0.45)
        lbl2 = Text("STAGE 2\nDelta Sub\nx_i - 50 <= 0", font=th.MONO, font_size=13, color=th.CYAN_LIGHT).move_to(s2)

        s3 = RoundedRectangle(corner_radius=0.15, width=2.4, height=1.5,
                              stroke_color=th.PURPLE, stroke_width=2.0, fill_color=th.CARD, fill_opacity=0.95).shift(RIGHT * 1.4 + UP * 0.45)
        lbl3 = Text("STAGE 3\nExp LUT\nQ0.8 (0..255)", font=th.MONO, font_size=13, color=th.PURPLE_LIGHT).move_to(s3)

        s4 = RoundedRectangle(corner_radius=0.15, width=2.4, height=1.5,
                              stroke_color=th.GREEN, stroke_width=2.0, fill_color=th.CARD, fill_opacity=0.95).shift(RIGHT * 4.2 + UP * 0.45)
        lbl4 = Text("STAGE 4\nAdder Tree & Div\nΣ P_i = 100%", font=th.MONO, font_size=13, color=th.GREEN_LIGHT).move_to(s4)

        a1 = Arrow(start=s1.get_right(), end=s2.get_left(), buff=0.1, color=th.BORDER)
        a2 = Arrow(start=s2.get_right(), end=s3.get_left(), buff=0.1, color=th.BORDER)
        a3 = Arrow(start=s3.get_right(), end=s4.get_left(), buff=0.1, color=th.BORDER)

        stages_grp = VGroup(s1, lbl1, s2, lbl2, s3, lbl3, s4, lbl4, a1, a2, a3)
        self.play(FadeIn(stages_grp), run_time=1.0)

        # Pulse a glowing vector through all 4 stages
        pulse = Dot(color=th.AMBER, radius=0.18).move_to(s1.get_left() + LEFT * 0.5)
        self.play(FadeIn(pulse), run_time=0.2)
        self.play(pulse.animate.move_to(s1), run_time=0.4)
        self.play(pulse.animate.move_to(s2).set_color(th.CYAN), run_time=0.4)
        self.play(pulse.animate.move_to(s3).set_color(th.PURPLE), run_time=0.4)
        self.play(pulse.animate.move_to(s4).set_color(th.GREEN), run_time=0.4)
        self.play(FadeOut(pulse), run_time=0.2)

        # Liquid Probability Output Visualizer: 4 cylinders filling up
        p_card = th.card(10.5, 1.2, stroke=th.GREEN, radius=0.15)
        p_card.next_to(banner, UP, buff=0.22)
        p_text = Text("Output Probabilities: [P0 = 0.0%, P1 = 0.0%, P2 = 0.0%, P3 = 100.0%]\nFixed-Point Invariant: Output strictly conserves probability mass!",
                      font=th.MONO, weight=BOLD, font_size=14, color=th.GREEN_LIGHT).move_to(p_card)

        self.play(Create(p_card), Write(p_text), run_time=0.8)
        self.wait(2.2)

        self.play(FadeOut(pipe_title), FadeOut(stages_grp), FadeOut(p_card), FadeOut(p_text), run_time=0.5)

        # =====================================================================
        # ACT 4: SYNTHESIZABLE RTL & FLASHATTENTION ROADMAP (~45s)
        # =====================================================================
        rtl_title = Text("Synthesizable Architecture: rtl/softmax.sv",
                         font=th.SANS, weight=BOLD, font_size=26, color=th.CYAN)
        rtl_title.to_edge(UP, buff=0.6)
        self.play(Write(rtl_title), run_time=0.6)

        sv_lines = [
            ("// 1. Parallel Comparator Tree to find vector maximum:", th.MUTED),
            ("always_comb begin max_val = in_vec[0]; ... end", th.CYAN_LIGHT),
            ("", th.MUTED),
            ("// 2. Safe Subtraction: delta_i <= 0 strictly bounded", th.AMBER),
            ("assign delta = in_vec[i] - max_val;", th.TEXT),
            ("", th.MUTED),
            ("// 3. High-Speed 16-Entry Exponential Seed ROM (Q0.8 domain):", th.PURPLE_LIGHT),
            ("assign exp_val = exp_lut[delta[3:0]];  // 0.0 to 1.0", th.GREEN_LIGHT),
        ]
        sv_win = th.code_window(sv_lines, title_text="RTL/SOFTMAX.SV: COMBINATIONAL FLASH SFU",
                                width=10.5, height=3.2, font_size=14, title_color=th.PURPLE)
        sv_win.move_to(UP * 0.55)

        self.play(Create(sv_win), run_time=1.0)

        # Summary
        flash_card = th.card(10.5, 1.1, stroke=th.GREEN, radius=0.15)
        flash_card.next_to(banner, UP, buff=0.22)
        flash_txt = Text("✓ FlashAttention Ready: Fuses Online Normalization directly into local SRAM buffers!",
                         font=th.MONO, weight=BOLD, font_size=15, color=th.GREEN_LIGHT).move_to(flash_card)

        self.play(Create(flash_card), FadeIn(flash_txt), run_time=0.7)
        self.play(
            Transform(banner, th.narration_banner(
                "Next in our AI Hardware journey: Lab 07, where we build the Fast Reciprocal Square Root (rsqrt) for LLaMA 3's RMSNorm!"
            )),
            run_time=0.6
        )
        self.wait(3.0)
