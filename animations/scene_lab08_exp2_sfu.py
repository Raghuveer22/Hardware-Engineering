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
        # ACT 1: THE SWIGLU NON-LINEAR SILICON CHALLENGE
        # =====================================================================
        act1_narration = "In modern LLMs like LLaMA 3 and DeepSeek, over 60% of all FLOPs reside in SwiGLU non-linear Feed-Forward Networks requiring high-speed exponential SFUs."
        with self.stage("ACT 1", "The SwiGLU Silicon Challenge", "Why LLMs Require Hardware Exponential Special Function Units", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                swiglu_eq = SemanticMath(
                    r"\text{SwiGLU}(x) = \left(x \cdot \frac{1}{1 + e^{-x}}\right) \odot (x W_{\text{up}}) W_{\text{down}}",
                    role=TextRole.MATH_DISPLAY,
                    color=th.CYAN_LIGHT
                )

                metric_cards = HStack(
                    th.metric_card("60% FLOPs", "SwiGLU FFN Layer", "Dominates modern LLM runtime", color=th.AMBER, width=4.0, height=2.2),
                    th.metric_card("1 Cycle SFU", "Pipelined Silicon SFU", "Replaces 50-cycle software loop", color=th.GREEN, width=4.0, height=2.2),
                    gap=th.SPACE_MD
                )

                content_layout = VStack(swiglu_eq, metric_cards, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(content_layout)

                self.play(Write(swiglu_eq), FadeIn(metric_cards, shift=UP * 0.2), run_time=min(trk.duration, 1.2))
                self.wait(max(0.2, trk.duration - 1.2))

        # =====================================================================
        # ACT 2: THE BASE-2 LASER DECOMPOSITION THEOREM
        # =====================================================================
        act2_narration = "Computing natural e^x in gates is prohibitive. Silicon hardware converts to Base-2, decomposing into an integer bit-shift and a tiny fractional ROM lookup."
        with self.stage("ACT 2", "Base-2 Laser Decomposition", "Decomposing 2^x into 2^Integer × 2^Fractional", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                decomp_eq = SemanticMath(
                    r"e^x = 2^{x \cdot \log_2(e)} = 2^{I + F} = \underbrace{2^I}_{\text{Barrel Shift}} \times \underbrace{2^F}_{\text{Small 32-Entry ROM}}",
                    role=TextRole.MATH_DISPLAY,
                    color=th.AMBER_LIGHT
                )

                decomp_cards = HStack(
                    th.metric_card("2^I (Integer)", "Hardware Barrel Shifter", "Zero math: purely wire routing", color=th.CYAN, width=4.2, height=2.2),
                    th.metric_card("2^F (Fractional)", "32-Entry Seed ROM", "F ∈ [0, 1): exact seed table", color=th.GREEN, width=4.2, height=2.2),
                    gap=th.SPACE_MD
                )

                stage_layout = VStack(decomp_eq, decomp_cards, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(stage_layout)

                self.play(Write(decomp_eq), FadeIn(decomp_cards, shift=UP * 0.2), run_time=min(trk.duration, 1.2))
                self.wait(max(0.2, trk.duration - 1.2))

        # =====================================================================
        # ACT 3: COMPLETE HARDWARE SFU DATAPATH (rtl/exp2_sfu.sv)
        # =====================================================================
        act3_narration = "In synthesizable RTL, the input multiplies by log2(e), splits across fixed-point wires, evaluates 2^F in ROM, and shifts by 2^I in 4.2 ns."
        with self.stage("ACT 3", "Hardware SFU Datapath", "Streaming Microarchitecture in rtl/exp2_sfu.sv", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                # 4 Pipelined Blocks: Multiplier -> Slicer -> ROM -> Barrel Shifter
                b1 = th.metric_card("Scale log2(e)", "Fixed-Point Mult", "x × 1.442695", color=th.CYAN, width=2.8, height=2.4)
                b2 = th.metric_card("Bit Slicer", "Q8.8 Format", "Integer [I] + Frac [F]", color=th.AMBER, width=2.8, height=2.4)
                b3 = th.metric_card("Seed ROM", "32-Entry Table", "Evaluates 2^F", color=th.PURPLE, width=2.8, height=2.4)
                b4 = th.metric_card("Barrel Shifter", "Bit Crossbar", "Shifts by 2^I", color=th.GREEN, width=2.8, height=2.4)

                datapath = HStack(b1, b2, b3, b4, gap=th.SPACE_SM).move_to(self.layout.main_stage_center())
                st.add(datapath)

                for block in [b1, b2, b3, b4]:
                    clock.advance(self, delta_cycles=1, run_time=0.25)
                    self.play(FadeIn(block, shift=RIGHT * 0.2), run_time=0.3)

                self.wait(max(0.2, trk.duration - 1.5))

        # =====================================================================
        # ACT 4: ACCELERATOR TAPE-OUT SUMMARY
        # =====================================================================
        act4_narration = "From signed adders to systolic matrix arrays, custom silicon delivers thousand-fold throughput gains over CPUs, powering the frontier of AI."
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
