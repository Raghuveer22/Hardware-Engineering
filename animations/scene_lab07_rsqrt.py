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
        # ACT 0: PRELORE — NORMALIZING A VECTOR
        # =====================================================================
        prelore_narration = (
            "A hidden-state vector grows as training goes on—its magnitude drifts upward. "
            "RMSNorm pulls it back to a fixed length by dividing by the root-mean-square of its entries. "
            "That division needs one over the square root, and that is what this lab builds in silicon."
        )
        with self.stage("PRIMER", "Normalizing a Vector", "Pull the Magnitude Back to One", narration=prelore_narration) as st:
            with self.voiceover(prelore_narration) as trk:
                pre_cards = HStack(
                    th.metric_card("Magnitude", "grows during training", "Vectors drift outward", color=th.RED, width=3.6, height=2.3),
                    th.metric_card("RMS", "√(mean of xᵢ²)", "One number per row", color=th.CYAN, width=3.6, height=2.3),
                    th.metric_card("1/√var", "the reciprocal root", "The hardware target", color=th.GREEN, width=3.6, height=2.3),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(pre_cards)
                self.play(FadeIn(pre_cards, shift=UP * 0.2), run_time=1.0)
                self.wait(max(0.3, trk.duration - 1.0))
                st.takeaway("RMSNorm = divide each row by its own root-mean-square.", wait=1.2)

        # =====================================================================
        # ACT 1: UNIT SPHERE NORMALIZATION IN LLAMA 3
        # =====================================================================
        act1_narration = (
            "Modern LLMs like LLaMA 3 normalize hidden states with RMSNorm. "
            "Each activation vector is divided by one over the square root of its variance, "
            "snapping it back to a fixed length instead of letting it drift."
        )
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
                st.takeaway("Divide by the reciprocal root, and the vectors snap to length one.", wait=1.2)

        # =====================================================================
        # ACT 2: DIVISION-FREE NEWTON-RAPHSON DERIVATION
        # =====================================================================
        act2_narration = (
            "But hardware division is slow and area-hungry, so our unit avoids it. "
            "It computes the integer square root digit by digit, then scales it into a reciprocal with a single "
            "fixed-point multiply—never a divider in the datapath."
        )
        with self.stage("ACT 2", "Digit Root + Reciprocal Scaler", "Integer Root Then a Single Multiply", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                nr_eq = SemanticMath(
                    r"\text{rsqrt}(x) \approx \frac{2^8}{\lfloor \sqrt{x} \rfloor}, \quad y = \frac{65536}{\text{root} \cdot 256}",
                    role=TextRole.MATH_DISPLAY,
                    color=th.CYAN_LIGHT
                )

                stat_cards = HStack(
                    th.metric_card("0 Dividers", "Digit Root + Multiply", "No divider in the datapath", color=th.GREEN, width=4.0, height=2.2),
                    th.metric_card("Q8.8", "Fixed-Point Output", "256 means 1.0", color=th.CYAN, width=4.0, height=2.2),
                    gap=th.SPACE_MD
                )

                nr_layout = VStack(nr_eq, stat_cards, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(nr_layout)

                self.play(Write(nr_eq), FadeIn(stat_cards, shift=UP * 0.2), run_time=min(trk.duration, 1.2))
                self.wait(max(0.2, trk.duration - 1.2))
                st.takeaway("Digit root, then scale—no divider needed.", wait=1.2)

        # =====================================================================
        # ACT 3: RMSNORM VS LAYERNORM — WHAT YOU SAVE
        # =====================================================================
        act3_narration = (
            "The reason modern LLMs prefer RMSNorm is what it leaves out. "
            "LayerNorm first subtracts the mean of every row—an entire extra reduction tree. "
            "RMSNorm skips that step and keeps only the scale, so the circuit is smaller and faster."
        )
        with self.stage("ACT 3", "RMSNorm vs LayerNorm", "What You Save by Dropping the Mean", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                comparison_cards = HStack(
                    th.metric_card("No Mean Tree", "RMSNorm vs LayerNorm", "Skips the mean subtraction stage", color=th.GREEN, width=3.8, height=2.2),
                    th.metric_card("Digit Root", "Integer isqrt engine", "Bit-by-bit, exact result", color=th.AMBER, width=3.8, height=2.2),
                    th.metric_card("LLaMA 3", "Industry Standard SFU", "Deployed across modern LLM weights", color=th.CYAN, width=3.8, height=2.2),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(comparison_cards)

                self.play(FadeIn(comparison_cards, shift=UP * 0.2), run_time=min(trk.duration, 1.0))
                self.wait(max(0.2, trk.duration - 1.0))
                st.takeaway("Drop the mean, keep the scale—smaller and faster.", wait=1.2)
