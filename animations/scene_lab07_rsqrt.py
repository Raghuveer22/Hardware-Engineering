"""
Lab 07: Token Normalization — Fast Reciprocal Square Root (rsqrt) for RMSNorm
Architectural Implementation: Declarative Stage Lifecycle, Constraint Layout,
Division-Free Newton-Raphson Derivation, Voiceover Auto-Sync, and Vector LaTeX MathTex.
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


class Lab07RSQRT(KineticSiliconScene):
    def construct(self):
        config = HardwareConfig(data_width=8)
        clock = KineticClock(initial_cycle=0)

        # Ambient Clock HUD at top right
        ticker = clock.create_ticker_badge(prefix="CLK: T = ", color=th.AMBER_LIGHT)
        ticker.to_corner(UR, buff=0.35)
        self.add(ticker)

        # =====================================================================
        # ACT 1: UNIT SPHERE NORMALIZATION IN LLAMA 3
        # =====================================================================
        act1_narration = "Modern LLMs like LLaMA 3 normalize hidden states using RMSNorm. Computing 1 over square root variance snaps exploded vectors back to the unit sphere."
        with self.stage("ACT 1", "Token Normalization & RMSNorm", "Snapping Exploded Activation Vectors to Unit Radius", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                target_circle = Circle(radius=1.8, color=th.GREEN, stroke_width=3.0)
                c_lbl = SemanticText("Unit Sphere Target (r = 1.0)", role=TextRole.PROBE_LABEL, color=th.GREEN_LIGHT)
                c_lbl.next_to(target_circle, UP, buff=0.15)
                circle_group = VGroup(target_circle, c_lbl)

                # Wild vectors snapping to circle
                vectors = VGroup(*[
                    Arrow(ORIGIN, np.array([np.cos(ang), np.sin(ang), 0]) * r, color=th.RED, buff=0, stroke_width=3.0)
                    for ang, r in [(0.4, 3.2), (1.8, 2.9), (3.6, 3.4), (5.1, 2.7)]
                ])

                circle_layout = VGroup(circle_group, vectors).move_to(self.layout.main_stage_center())
                st.add(circle_layout)

                self.play(Create(circle_group), FadeIn(vectors), run_time=1.0)

                # Snap vectors to unit circle
                snapped_vectors = VGroup(*[
                    Arrow(ORIGIN, np.array([np.cos(ang), np.sin(ang), 0]) * 1.8, color=th.GREEN, buff=0, stroke_width=3.0)
                    for ang, _ in [(0.4, 3.2), (1.8, 2.9), (3.6, 3.4), (5.1, 2.7)]
                ]).move_to(circle_group[0].get_center())

                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.play(Transform(vectors, snapped_vectors), run_time=0.8)
                self.wait(max(0.2, trk.duration - 2.2))

        # =====================================================================
        # ACT 2: DIVISION-FREE NEWTON-RAPHSON DERIVATION
        # =====================================================================
        act2_narration = "Hardware division is notoriously slow. Newton-Raphson reformulates inverse square root into multiplications and bit-shifts with zero dividers!"
        with self.stage("ACT 2", "Division-Free Newton-Raphson", "Multiplication-Only Convergence Theorem", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                nr_eq = SemanticMath(
                    r"y_{n+1} = y_n \cdot \left(\frac{3 - x \cdot y_n^2}{2}\right)",
                    role=TextRole.MATH_DISPLAY,
                    color=th.CYAN_LIGHT
                )

                stat_cards = HStack(
                    th.metric_card("0 Dividers", "Multiplication-Only Math", "Replaces 40-cycle divider unit", color=th.GREEN, width=4.0, height=2.2),
                    th.metric_card("4.6 ns", "Single-Cycle Latency", "Pipelined SFU critical path", color=th.CYAN, width=4.0, height=2.2),
                    gap=th.SPACE_MD
                )

                nr_layout = VStack(nr_eq, stat_cards, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(nr_layout)

                self.play(Write(nr_eq), FadeIn(stat_cards, shift=UP * 0.2), run_time=min(trk.duration, 1.2))
                self.wait(max(0.2, trk.duration - 1.2))

        # =====================================================================
        # ACT 3: RMSNORM VS LAYERNORM 55% GATE REDUCTION
        # =====================================================================
        act3_narration = "By eliminating mean-centering subtraction, RMSNorm saves 55% silicon area and 30% latency over traditional LayerNorm."
        with self.stage("ACT 3", "RMSNorm vs LayerNorm", "55% Silicon Gate Savings in Modern LLMs", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                comparison_cards = HStack(
                    th.metric_card("55% Less Area", "RMSNorm vs LayerNorm", "Eliminates mean subtraction tree", color=th.GREEN, width=3.8, height=2.2),
                    th.metric_card("32-Entry ROM", "Seed Approximation Table", "Initial guess y_0 with 1.5% error", color=th.AMBER, width=3.8, height=2.2),
                    th.metric_card("LLaMA 3", "Industry Standard SFU", "Deployed across all modern weights", color=th.CYAN, width=3.8, height=2.2),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(comparison_cards)

                self.play(FadeIn(comparison_cards, shift=UP * 0.2), run_time=min(trk.duration, 1.0))
                self.wait(max(0.2, trk.duration - 1.0))
