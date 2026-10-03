"""
Lab 06: The Probability Engine — Safe Softmax & FlashAttention
Architectural Implementation: Declarative Stage Lifecycle, Constraint Layout,
Dynamic Rocket Bar Chart, Voiceover Auto-Sync, and Vector LaTeX MathTex.
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
    HardwareConfig,
    TextRole,
    SemanticText,
    SemanticMath,
    HStack,
    VStack,
    ConstraintAnchor,
    PinProbe,
)


class Lab06Softmax(KineticSiliconScene):
    def construct(self):
        config = HardwareConfig(data_width=8)
        clock = KineticClock(initial_cycle=0)

        # Ambient Clock HUD at top right
        ticker = clock.create_ticker_badge(prefix="CLK: T = ", color=th.AMBER_LIGHT)
        ticker.to_corner(UR, buff=0.35)
        self.add(ticker)

        # =====================================================================
        # ACT 0: PRELORE — WHAT SOFTMAX IS FOR
        # =====================================================================
        prelore_narration = (
            "Softmax turns a row of scores into probabilities that add up to one. "
            "First it exponentiates each score, then it divides by the total. "
            "But exponentials grow fast—and in hardware, fast growth means overflow."
        )
        with self.stage("PRIMER", "What Softmax Is For", "Scores → Probabilities", narration=prelore_narration) as st:
            with self.voiceover(prelore_narration) as trk:
                pre_cards = HStack(
                    th.metric_card("Scores", "Any real numbers", "Logits from attention", color=th.CYAN, width=3.6, height=2.3),
                    th.metric_card("Exp", "e^score per row", "Grows very fast", color=th.RED, width=3.6, height=2.3),
                    th.metric_card("Normalize", "Divide by the sum", "Probabilities: Σ = 1", color=th.GREEN, width=3.6, height=2.3),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(pre_cards)
                self.play(FadeIn(pre_cards, shift=UP * 0.2), run_time=1.0)
                self.wait(max(0.3, trk.duration - 1.0))
                st.takeaway("Softmax = exponentiate, then divide by the total.", wait=1.2)

        # =====================================================================
        # ACT 1: THE e^50 ROCKET OVERFLOW & SHIFT-INVARIANCE THEOREM
        # =====================================================================
        act1_narration = (
            "Here is the danger. In raw softmax, a score of 50 becomes e to the 50—about five sextillion—"
            "instantly overflowing any fixed-point register. The trick is to subtract the largest score first, "
            "so every exponent lands at or below one, and the probabilities come out identical."
        )
        with self.stage("ACT 1", "The Rocket Overflow & Safe Softmax", "Mathematical Proof of Numerical Shift-Invariance", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                # Dynamic Bar Chart (scores; the largest is 50, the e^50 rocket)
                chart = th.DynamicBarChartWidget(
                    values=[2.0, 5.0, 1.0, 50.0],
                    labels=["x0", "x1", "x2", "x3 (50)"],
                    max_val=50.0,
                    chart_width=5.2,
                    chart_height=2.8,
                    bar_color=th.RED
                )

                # Shift Invariance Proof via SemanticMath
                proof_eq = SemanticMath(
                    r"S(x_i) = \frac{e^{x_i - m}}{\sum_j e^{x_j - m}}, \quad x_i - m \le 0 \implies e^{x_i - m} \in (0, 1]",
                    role=TextRole.MATH_DISPLAY,
                    color=th.CYAN_LIGHT
                )

                stage_layout = HStack(chart, proof_eq, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(stage_layout)

                self.play(Create(chart), Write(proof_eq), run_time=min(trk.duration * 0.7, 1.2))
                self.screen_shake(intensity=0.03, cycles=2, run_time=0.2)
                self.wait(max(0.2, trk.duration - 1.4))
                st.takeaway("Subtract the max, and every exponent stays at or below one.", wait=1.2)

        # =====================================================================
        # ACT 2: 3-PASS STREAMING HARDWARE PIPELINE (rtl/softmax.sv)
        # =====================================================================
        act2_narration = (
            "Our softmax unit computes this in three conceptual passes. "
            "Pass one finds the maximum. Pass two adds up the exponentials of the shifted scores. "
            "Pass three divides each exponential by that sum to get probabilities."
        )
        with self.stage("ACT 2", "3-Pass Hardware Pipeline", "Streaming Microarchitecture in rtl/softmax.sv", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                pass1 = th.metric_card("Pass 1: Find Max", "m = max(x_0..x_N)", "Comparator Tree Reduction", color=th.AMBER, width=3.8, height=2.4)
                pass2 = th.metric_card("Pass 2: Exp Sum", "d = Σ exp(x_i - m)", "SFU Exp2 + Accumulator", color=th.CYAN, width=3.8, height=2.4)
                pass3 = th.metric_card("Pass 3: Normalize", "P_i = exp(x_i - m) / d", "Reciprocal Multiplier", color=th.GREEN, width=3.8, height=2.4)

                pipeline_group = HStack(pass1, pass2, pass3, gap=th.SPACE_MD).move_to(self.layout.main_stage_center())
                st.add(pipeline_group)

                self.play(FadeIn(pass1, shift=RIGHT * 0.2), run_time=0.4)
                clock.advance(self, delta_cycles=1, run_time=0.3)
                self.play(FadeIn(pass2, shift=RIGHT * 0.2), run_time=0.4)
                clock.advance(self, delta_cycles=1, run_time=0.3)
                self.play(FadeIn(pass3, shift=RIGHT * 0.2), run_time=0.4)
                self.wait(max(0.2, trk.duration - 1.8))
                st.takeaway("Find the max, sum the exponentials, then normalize.", wait=1.2)

        # =====================================================================
        # ACT 3: FLASHATTENTION ONLINE RESCALING
        # =====================================================================
        act3_narration = (
            "But three passes means reading the data three times. FlashAttention avoids that by rescaling "
            "a running sum on the fly, inside on-chip SRAM, so the full attention matrix never has to leave the chip."
        )
        with self.stage("ACT 3", "FlashAttention Online Rescaling", "Tiled SRAM Streaming & Blackwell Warp Groups", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                online_eq = SemanticMath(
                    r"d_{\text{new}} = d_{\text{prev}} \cdot e^{m_{\text{prev}} - m_{\text{new}}} + e^{x_i - m_{\text{new}}}",
                    role=TextRole.MATH_DISPLAY,
                    color=th.GREEN_LIGHT
                )

                flash_cards = HStack(
                    th.metric_card("O(N) SRAM", "On-Chip Tiling", "Never writes N×N attention to DRAM", color=th.GREEN, width=4.2, height=2.2),
                    th.metric_card("3-5× Speedup", "FlashAttention-1/2/3", "IO-aware exact attention acceleration", color=th.CYAN, width=4.2, height=2.2),
                    gap=th.SPACE_MD
                )

                content_layout = VStack(online_eq, flash_cards, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(content_layout)

                self.play(Write(online_eq), FadeIn(flash_cards, shift=UP * 0.2), run_time=min(trk.duration, 1.2))
                self.wait(max(0.2, trk.duration - 1.2))
                st.takeaway("Rescale the running sum, and one pass is enough.", wait=1.2)
