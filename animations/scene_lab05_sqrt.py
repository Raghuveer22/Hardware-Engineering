"""
Lab 05: Scaled Attention — Hardware Square Root Unit & Attention Variance Scaling
Architectural Implementation: Declarative Stage Lifecycle, Constraint Layout,
Unrolled Digit-Recurrence Pipeline, Voiceover Auto-Sync, and Vector LaTeX MathTex.
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


class Lab05SquareRoot(KineticSiliconScene):
    def construct(self):
        config = HardwareConfig(data_width=8)
        clock = KineticClock(initial_cycle=0)

        # Ambient Clock HUD at top right
        ticker = clock.create_ticker_badge(prefix="CLK: T = ", color=th.AMBER_LIGHT)
        ticker.to_corner(UR, buff=0.35)
        self.add(ticker)

        # =====================================================================
        # ACT 0: PRELORE — WHY ATTENTION NEEDS A SQUARE ROOT
        # =====================================================================
        prelore_narration = (
            "Attention starts with a dot product: one vector times another, summed over many dimensions. "
            "The longer the vectors, the bigger that sum gets—so big it breaks training. "
            "The fix is to divide by the square root of the length, which needs square-root hardware."
        )
        with self.stage("PRIMER", "Why Attention Needs a Square Root", "Dot Products Grow With Dimension", narration=prelore_narration) as st:
            with self.voiceover(prelore_narration) as trk:
                pre_cards = HStack(
                    th.metric_card("Dot Product", "q · k = Σ qᵢkᵢ", "Sums over d_k terms", color=th.CYAN, width=3.6, height=2.3),
                    th.metric_card("Variance", "grows with d_k", "Scores blow up", color=th.RED, width=3.6, height=2.3),
                    th.metric_card("1/√d_k", "The fix", "Needs a root unit", color=th.GREEN, width=3.6, height=2.3),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(pre_cards)
                self.play(FadeIn(pre_cards, shift=UP * 0.2), run_time=1.0)
                self.wait(max(0.3, trk.duration - 1.0))
                st.takeaway("Longer vectors mean bigger dot products—so we divide by √d_k.", wait=1.2)

        # =====================================================================
        # ACT 1: ATTENTION VARIANCE COLLAPSE & THE 1/√d_k SCALING PROOF
        # =====================================================================
        act1_narration = (
            "Here is the exact math. With independent inputs, the dot product's variance grows to d_k—128 in this example. "
            "Dividing by the square root of d_k pulls the variance back down to exactly one, "
            "so the softmax sees well-behaved numbers instead of exploding scores."
        )
        with self.stage("ACT 1", "Attention Variance Proof", "Why Attention Explodes Without Square Root Scaling", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                variance_eq = SemanticMath(
                    r"\text{Var}(\mathbf{q}^T \mathbf{k}) = \sum_{i=1}^{d_k} \text{Var}(q_i k_i) = d_k \cdot 1 = d_k \implies \text{Var}\left(\frac{\mathbf{q}^T \mathbf{k}}{\sqrt{d_k}}\right) = 1.0",
                    role=TextRole.MATH_DISPLAY,
                    color=th.CYAN_LIGHT
                )

                metric_cards = HStack(
                    th.metric_card("Var = 128", "Unscaled Dot-Product", "Causes dead vanishing gradients", color=th.RED, width=4.2, height=2.2),
                    th.metric_card("1 / √128", "Hardware Scaling Factor", "Normalizes variance back to 1.0", color=th.GREEN, width=4.2, height=2.2),
                    gap=th.SPACE_MD
                )

                stage_layout = VStack(variance_eq, metric_cards, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(stage_layout)

                self.play(Write(variance_eq), FadeIn(metric_cards, shift=UP * 0.2), run_time=min(trk.duration, 1.2))
                self.wait(max(0.2, trk.duration - 1.2))
                st.takeaway("Divide by √d_k, and the variance lands on one.", wait=1.2)

        # =====================================================================
        # ACT 2: UNROLLED 8-STAGE RESTORING SQRT PIPELINE
        # =====================================================================
        act2_narration = (
            "Our synthesizable root unit peels the answer off bit by bit, most significant bit first, "
            "using a digit-by-digit shift-and-subtract loop. Each of the eight stages here produces one bit of the root, "
            "and it needs no multiplier at all—just compares and subtracts."
        )
        with self.stage("ACT 2", "Digit-by-Digit Root Unit", "Bit-by-Bit Shift-and-Subtract in rtl/sqrt.sv", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                # 8 Pipeline Slices
                slices = VGroup(*[
                    VGroup(
                        RoundedRectangle(corner_radius=0.08, width=1.1, height=2.8, stroke_color=th.CYAN, stroke_width=1.5, fill_color="#0b1728", fill_opacity=0.9),
                        VStack(
                            SemanticText(f"S{i}", role=TextRole.BLOCK_HEADER, color=th.CYAN),
                            SemanticText(f"Q[{7-i}]", role=TextRole.PROBE_LABEL, color=th.AMBER_LIGHT),
                            gap=th.SPACE_XS
                        )
                    )
                    for i in range(8)
                ]).arrange(RIGHT, buff=0.18).move_to(self.layout.main_stage_center())

                probe_in = PinProbe("RADICAND [16b]", "0x0040 (64)", color=th.AMBER)
                probe_in.next_to(slices, LEFT, buff=th.SPACE_SM)

                probe_out = PinProbe("EXACT ROOT [8b]", "0x08 (8)", color=th.GREEN)
                probe_out.next_to(slices, RIGHT, buff=th.SPACE_SM)

                st.add(slices, probe_in, probe_out)
                self.play(Create(slices), FadeIn(probe_in), run_time=1.0)

                # Step clock and light up each bit-slice stage
                for i in range(8):
                    clock.advance(self, delta_cycles=1, run_time=0.25)
                    self.play(
                        slices[i][0].animate.set_stroke(color=th.GREEN, width=2.5).set_fill(color="#062414", opacity=0.95),
                        run_time=0.2
                    )

                self.play(FadeIn(probe_out), run_time=0.5)
                self.wait(max(0.2, trk.duration - 3.2))
                st.takeaway("Each slice peels off one bit of the square root.", wait=1.2)

        # =====================================================================
        # ACT 3: HARDWARE TRADE-OFFS & SYNTHESIS
        # =====================================================================
        act3_narration = (
            "Why this algorithm? It avoids multipliers entirely, which keeps the circuit small. "
            "The trade-off is latency—one step per bit—but the answer is exact to the last bit, "
            "which matters when every attention score must be deterministic."
        )
        with self.stage("ACT 3", "Hardware Trade-Off Matrix", "Digit Recurrence vs CORDIC vs Newton-Raphson", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                tradeoff_cards = HStack(
                    th.metric_card("No Multipliers", "Digit-by-Digit (rtl/sqrt.sv)", "Compares and subtracts only; exact root", color=th.GREEN, width=3.8, height=2.2),
                    th.metric_card("CORDIC", "Rotation-based method", "Also multiplier-free, needs trig tables", color=th.AMBER, width=3.8, height=2.2),
                    th.metric_card("Newton-Raphson", "Iterative refinement", "Fast but demands a multiplier", color=th.RED, width=3.8, height=2.2),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(tradeoff_cards)

                self.play(FadeIn(tradeoff_cards, shift=UP * 0.2), run_time=min(trk.duration, 1.0))
                self.wait(max(0.2, trk.duration - 1.0))
                st.takeaway("No multiplier, exact answer—just one bit at a time.", wait=1.2)
