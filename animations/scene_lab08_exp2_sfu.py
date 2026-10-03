"""
Lab 08: The Non-Linear Engine — Hardware Exponential SFU (2^x & e^x) for SwiGLU
Architectural Implementation: Declarative Stage Lifecycle, Constraint Layout,
Base-2 Laser Decomposition, Voiceover Auto-Sync, and Vector LaTeX MathTex.
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


class Lab08ExponentialSFU(KineticSiliconScene):
    def construct(self):
        config = HardwareConfig(data_width=8)
        clock = KineticClock(initial_cycle=0)

        # Ambient Clock HUD at top right
        ticker = clock.create_ticker_badge(prefix="CLK: T = ", color=th.AMBER_LIGHT)
        ticker.to_corner(UR, buff=0.35)
        self.add(ticker)

        # =====================================================================
        # ACT 0: PRELORE — THE SIGMOID, THE GATE
        # =====================================================================
        prelore_narration = (
            "SwiGLU is a gated activation: a sigmoid decides how much of a value passes through. "
            "The sigmoid itself is one over one plus e to the minus x. "
            "So at the heart of the most-used layer in an LLM sits a single exponential function."
        )
        with self.stage("PRIMER", "The Sigmoid, The Gate", "σ(x) = 1 / (1 + e^-x)", narration=prelore_narration) as st:
            with self.voiceover(prelore_narration) as trk:
                pre_cards = HStack(
                    th.metric_card("σ(x)", "1 / (1 + e^-x)", "The gate value in [0,1]", color=th.CYAN, width=3.6, height=2.3),
                    th.metric_card("Gate", "σ(·) ⊙ value", "How much passes", color=th.AMBER, width=3.6, height=2.3),
                    th.metric_card("e^-x", "The exponential", "The one expensive step", color=th.GREEN, width=3.6, height=2.3),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(pre_cards)
                self.play(FadeIn(pre_cards, shift=UP * 0.2), run_time=1.0)
                self.wait(max(0.3, trk.duration - 1.0))
                st.takeaway("SwiGLU = sigmoid gate times a value. The cost is the exponential.", wait=1.2)

        # =====================================================================
        # ACT 1: THE SWIGLU NON-LINEAR SILICON CHALLENGE
        # =====================================================================
        act1_narration = (
            "In LLaMA 3 and DeepSeek, most of the compute lives in the feed-forward network, "
            "where SwiGLU applies a sigmoid gate to one projection and multiplies it with another. "
            "That means the humble exponential sits on the critical path of the whole model."
        )
        with self.stage("ACT 1", "The SwiGLU Silicon Challenge", "Why LLMs Require Hardware Exponential Special Function Units", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                swiglu_eq = SemanticMath(
                    r"\text{SwiGLU}(x) = \text{sigmoid}(x W_{\text{up}}) \odot (x W_{\text{down}})",
                    role=TextRole.MATH_DISPLAY,
                    color=th.CYAN_LIGHT
                )

                metric_cards = HStack(
                    th.metric_card("FFN", "The gated layer", "Sigmoid gate × projection", color=th.AMBER, width=4.0, height=2.2),
                    th.metric_card("1 Cycle SFU", "Pipelined Silicon SFU", "Replaces a long software loop", color=th.GREEN, width=4.0, height=2.2),
                    gap=th.SPACE_MD
                )

                content_layout = VStack(swiglu_eq, metric_cards, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(content_layout)

                self.play(Write(swiglu_eq), FadeIn(metric_cards, shift=UP * 0.2), run_time=min(trk.duration, 1.2))
                self.wait(max(0.2, trk.duration - 1.2))
                st.takeaway("One exponential sits at the heart of every gated layer.", wait=1.2)

        # =====================================================================
        # ACT 2: THE BASE-2 LASER DECOMPOSITION THEOREM
        # =====================================================================
        act2_narration = (
            "Computing e to the x directly in gates would be huge. So hardware first rewrites it in base two: "
            "split the exponent into an integer part and a fraction. The integer part becomes a bit shift—free wiring—"
            "and the fraction becomes a tiny lookup table."
        )
        with self.stage("ACT 2", "Base-2 Laser Decomposition", "Decomposing 2^x into 2^Integer × 2^Fractional", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                decomp_eq = SemanticMath(
                    r"e^x = 2^{x \cdot \log_2(e)} = 2^{I + F} = \underbrace{2^I}_{\text{Barrel Shift}} \times \underbrace{2^F}_{\text{16-Entry LUT}}",
                    role=TextRole.MATH_DISPLAY,
                    color=th.AMBER_LIGHT
                )

                decomp_cards = HStack(
                    th.metric_card("2^I (Integer)", "Hardware Barrel Shifter", "Zero math: purely wire routing", color=th.CYAN, width=4.2, height=2.2),
                    th.metric_card("2^F (Fractional)", "16-Entry Lookup Table", "F ∈ [0, 1): 4-bit index", color=th.GREEN, width=4.2, height=2.2),
                    gap=th.SPACE_MD
                )

                stage_layout = VStack(decomp_eq, decomp_cards, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(stage_layout)

                self.play(Write(decomp_eq), FadeIn(decomp_cards, shift=UP * 0.2), run_time=min(trk.duration, 1.2))
                self.wait(max(0.2, trk.duration - 1.2))
                st.takeaway("Integer part = a shift. Fraction = a tiny lookup.", wait=1.2)

        # =====================================================================
        # ACT 3: COMPLETE HARDWARE SFU DATAPATH (rtl/exp2_sfu.sv)
        # =====================================================================
        act3_narration = (
            "The full datapath is four blocks. Multiply the input by log base two of e, "
            "split the result into integer and fraction, look the fraction up in the table, "
            "then barrel-shift by the integer—all in a single clock cycle."
        )
        with self.stage("ACT 3", "Hardware SFU Datapath", "Streaming Microarchitecture in rtl/exp2_sfu.sv", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                # 4 Pipelined Blocks: Multiplier -> Slicer -> ROM -> Barrel Shifter
                b1 = th.metric_card("Scale log2(e)", "Fixed-Point Mult", "x × 1.442695", color=th.CYAN, width=2.8, height=2.4)
                b2 = th.metric_card("Bit Slicer", "Q8.8 Format", "Integer [I] + Frac [F]", color=th.AMBER, width=2.8, height=2.4)
                b3 = th.metric_card("Seed LUT", "16-Entry Table", "Evaluates 2^F", color=th.PURPLE, width=2.8, height=2.4)
                b4 = th.metric_card("Barrel Shifter", "Bit Crossbar", "Shifts by 2^I", color=th.GREEN, width=2.8, height=2.4)

                datapath = HStack(b1, b2, b3, b4, gap=th.SPACE_SM).move_to(self.layout.main_stage_center())
                st.add(datapath)

                for block in [b1, b2, b3, b4]:
                    clock.advance(self, delta_cycles=1, run_time=0.25)
                    self.play(FadeIn(block, shift=RIGHT * 0.2), run_time=0.3)

                self.wait(max(0.2, trk.duration - 1.5))
                st.takeaway("Multiply, split, look up, shift—one cycle.", wait=1.2)

        # =====================================================================
        # ACT 4: ACCELERATOR TAPE-OUT SUMMARY
        # =====================================================================
        act4_narration = (
            "Put it all together and you get a full picture: signed adders with saturation, cheap INT8 multipliers, "
            "wide accumulators, a systolic array—and now special-function units for the non-linear parts. "
            "That is the hardware stack behind the AI frontier."
        )
        with self.stage("ACT 4", "Hardware AI Accelerator Co-Design", "From Mathematical Proof to Synthesized Silicon Tapeout", narration=act4_narration) as st:
            with self.voiceover(act4_narration) as trk:
                summary_grid = HStack(
                    th.metric_card("100% Concurrent", "Zero Program Counter", "Concurrent silicon logic arrays", color=th.CYAN, width=3.8, height=2.2),
                    th.metric_card("1,000× Energy", "Memory Wall Overcome", "Spatial dataflows keep data on-chip", color=th.GREEN, width=3.8, height=2.2),
                    th.metric_card("Tapeout Ready", "SystemVerilog Core", "Verified via Cocotb pre-silicon tests", color=th.AMBER, width=3.8, height=2.2),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(summary_grid)

                self.play(FadeIn(summary_grid, shift=UP * 0.2), run_time=min(trk.duration, 1.0))
                self.wait(max(0.2, trk.duration - 1.0))
                st.takeaway("Arithmetic to arrays to SFUs—one silicon stack.", wait=1.2)
