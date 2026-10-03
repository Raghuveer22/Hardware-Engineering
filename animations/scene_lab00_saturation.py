"""
Lab 00: The Number Crisis — Signed Integer Overflow & Saturation Clamping
Architectural Implementation: Declarative Stage Lifecycle, Constraint Layout,
Two's Complement Wheel, Voiceover Auto-Sync, and Vector LaTeX MathTex.
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
    TwosComplementWheel,
    RippleCarryChain,
    HardwareConfig,
    TextRole,
    SemanticText,
    SemanticMath,
    HStack,
    VStack,
    ConstraintAnchor,
    PinProbe,
)


class Lab00SaturationIntro(KineticSiliconScene):
    def construct(self):
        config = HardwareConfig(data_width=8)
        clock = KineticClock(initial_cycle=0)

        # Ambient Clock HUD at top right
        ticker = clock.create_ticker_badge(prefix="CLK: T = ", color=th.AMBER_LIGHT)
        ticker.to_corner(UR, buff=0.35)
        self.add(ticker)

        # =====================================================================
        # ACT 1: THE SILICON BIT OVERFLOW BUG
        # =====================================================================
        act1_narration = "In standard two's complement, adding two large positive numbers causes the MSB to flip to 1, producing a catastrophic negative output."
        with self.stage("ACT 1", "Signed INT8 Overflow", "Why Adding Positive Numbers Yields Negative Results", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                # Two 8-bit registers: +100 (0x64) and +50 (0x32)
                reg_a = th.BitRegister(width_bits=8, initial_val="01100100", highlight_msb=True, msb_color=th.GREEN)
                lbl_a = SemanticText("Operand A: +100 (0x64)", role=TextRole.PROBE_LABEL, color=th.GREEN_LIGHT)
                group_a = VStack(lbl_a, reg_a, gap=th.SPACE_XS)

                reg_b = th.BitRegister(width_bits=8, initial_val="00110010", highlight_msb=True, msb_color=th.GREEN)
                lbl_b = SemanticText("Operand B:  +50 (0x32)", role=TextRole.PROBE_LABEL, color=th.GREEN_LIGHT)
                group_b = VStack(lbl_b, reg_b, gap=th.SPACE_XS)

                reg_sum = th.BitRegister(width_bits=8, initial_val="10010110", highlight_msb=True, msb_color=th.RED)
                lbl_sum = SemanticText("Hardware Sum: -106 (0x96) ➔ CORRUPTED!", role=TextRole.PROBE_LABEL, color=th.RED_LIGHT)
                group_sum = VStack(lbl_sum, reg_sum, gap=th.SPACE_XS)

                datapath_layout = VStack(group_a, group_b, group_sum, gap=th.SPACE_MD).move_to(self.layout.main_stage_center())
                st.add(datapath_layout)

                self.play(FadeIn(group_a), FadeIn(group_b), run_time=0.8)
                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.play(FadeIn(group_sum, shift=DOWN * 0.2), run_time=0.6)
                self.screen_shake(intensity=0.04, cycles=2, run_time=0.2)
                self.wait(max(0.2, trk.duration - 2.0))

        # =====================================================================
        # ACT 2: TWO'S COMPLEMENT OVERFLOW THEOREM
        # =====================================================================
        act2_narration = "In silicon logic gates, overflow occurs if and only if the carry into the sign bit differs from the carry out."
        with self.stage("ACT 2", "The Overflow Condition", "Hardware Theorem: Carry-In XOR Carry-Out", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                overflow_eq = SemanticMath(
                    r"V = C_{\text{in}}[7] \oplus C_{\text{out}}[7]",
                    role=TextRole.MATH_DISPLAY,
                    color=th.RED_LIGHT
                )

                metric_proof = HStack(
                    th.metric_card("C_in = 1", "Carry into Sign Bit", color=th.AMBER, width=4.0, height=2.0),
                    th.metric_card("C_out = 0", "Carry out of Sign Bit", color=th.CYAN, width=4.0, height=2.0),
                    th.metric_card("V = 1", "Overflow Flag Asserted", color=th.RED, width=4.0, height=2.0),
                    gap=th.SPACE_MD
                )

                proof_layout = VStack(overflow_eq, metric_proof, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(proof_layout)

                self.play(Write(overflow_eq), FadeIn(metric_proof, shift=UP * 0.2), run_time=min(trk.duration, 1.2))
                self.wait(max(0.2, trk.duration - 1.2))

        # =====================================================================
        # ACT 3: THE TWO'S COMPLEMENT SPEEDOMETER WHEEL
        # =====================================================================
        act3_narration = "Think of two's complement as a circular speedometer. Stepping past +127 wraps directly to -128, destroying gradient descent."
        with self.stage("ACT 3", "The Circle of Discontinuity", "Why Wrap-Around Destroys Deep Learning", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                wheel = TwosComplementWheel(radius=1.8).move_to(self.layout.main_stage_center())
                st.add(wheel)
                self.play(Create(wheel), run_time=1.0)

                # Animate dial sweep wrapping across overflow boundary
                clock.advance(self, delta_cycles=1, run_time=0.4)
                wheel.animate_sweep(self, target_val=150, run_time=1.0, clamp=False)
                self.screen_shake(intensity=0.05, cycles=2, run_time=0.2)

                # Deploy saturation clamp barrier and sweep again to clamp at +127
                clock.advance(self, delta_cycles=1, run_time=0.4)
                wheel.deploy_clamp_barrier(self)
                wheel.animate_sweep(self, target_val=150, run_time=0.8, clamp=True)
                self.wait(max(0.2, trk.duration - 2.8))

        # =====================================================================
        # ACT 4: THE 3:1 SATURATION CLAMPING DATAPATH
        # =====================================================================
        act4_narration = "AI accelerators fix this with a 3:1 Saturation Multiplexer. Overflow clamps positive results to +127 and negative results to -128."
        with self.stage("ACT 4", "The Saturation MUX", "Hardware Clamping Datapath in Synthesizable RTL", narration=act4_narration) as st:
            with self.voiceover(act4_narration) as trk:
                clamp_cards = HStack(
                    th.metric_card("+127 (0x7F)", "Positive Saturation Clamp", "Clamps +150 ➔ +127 Max Value", color=th.GREEN, width=4.6, height=2.2),
                    th.metric_card("-128 (0x80)", "Negative Saturation Clamp", "Clamps -200 ➔ -128 Min Value", color=th.CYAN, width=4.6, height=2.2),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(clamp_cards)

                self.play(FadeIn(clamp_cards, shift=UP * 0.2), run_time=min(trk.duration, 1.0))
                self.wait(max(0.2, trk.duration - 1.0))
