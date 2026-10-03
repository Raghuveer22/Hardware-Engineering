"""
Lab 02: Accumulator Headroom — The MAC Unit & Sign Extension
Accumulator Headroom Induction Proofs, Sign Extension & Pipelined Timing Dynamics.

Tailored for Software Engineers:
- Act 1: The Bursting 16-Bit Accumulator (Overloading on Term 2)
- Act 2: The 32-Bit Headroom Induction Proof (K <= 131,072 Zero-Overflow Guarantee)
- Act 3: Sign Extension vs Zero Extension Disaster (-5 becomes +65,531)
- Act 4: Combinational vs Pipelined MAC Critical Path (~250 MHz -> ~350 MHz)
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
    fit_to_bounds,
)


class Lab02MACUnit(KineticSiliconScene):
    def construct(self):
        config = HardwareConfig(data_width=8, vector_k=4096)
        clock = KineticClock(initial_cycle=0)

        # Ambient Clock HUD at top right (compact)
        ticker = clock.create_ticker_badge(prefix="CLK: T = ", color=th.AMBER_LIGHT)
        ticker.to_corner(UR, buff=0.25)
        self.add(ticker)

        # =====================================================================
        # ACT 0: PRELORE — THE MULTIPLY-ACCUMULATE HEARTBEAT
        # =====================================================================
        prelore_narration = (
            "Deep learning is one operation repeated trillions of times: multiply, then add. "
            "Take a value, multiply it by a weight, and add the result to a running total called the accumulator. "
            "That tiny loop is the heartbeat of every neural network on Earth."
        )
        with self.stage("PRIMER", "The Multiply-Accumulate Heartbeat", "Multiply, Then Add", narration=prelore_narration) as st:
            with self.voiceover(prelore_narration) as trk:
                pre_cards = HStack(
                    th.metric_card("Multiply", "value × weight", "One partial product", color=th.CYAN, width=3.6, height=2.3),
                    th.metric_card("Add", "…+ running total", "Into the accumulator", color=th.GREEN, width=3.6, height=2.3),
                    th.metric_card("Repeat", "billions of times", "The MAC loop", color=th.AMBER, width=3.6, height=2.3),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(pre_cards)
                self.play(FadeIn(pre_cards, shift=UP * 0.2), run_time=1.0)
                self.wait(max(0.3, trk.duration - 1.0))
                st.takeaway("MAC = multiply, then add to a running total.", wait=1.2)

        # =====================================================================
        # ACT 1: THE BURSTING 16-BIT ACCUMULATOR TANK
        # =====================================================================
        act1_narration = (
            "The accumulator is a register, and registers have a fixed size. "
            "One INT8 multiply can reach positive 16,384, while a 16-bit register only holds up to 32,767. "
            "Add just two of those products and the total bursts straight through the ceiling into negative numbers."
        )
        with self.stage("ACT 1", "Accumulator Bit Growth", "Why 16-Bit Registers Burst on Term 2", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                # 16-Bit Tank Widget
                tank_16 = th.LiquidTankWidget(capacity=32767, width=2.6, height=3.4, title="16-BIT REGISTER", fluid_color=th.RED)
                
                # Multiplier Input Block
                mult_block = RoundedRectangle(
                    corner_radius=0.12, width=4.6, height=3.4,
                    stroke_color=th.AMBER, stroke_width=2.0,
                    fill_color="#181106", fill_opacity=0.9
                )
                m_title = SemanticText("INT8 MULTIPLY-ACCUMULATE", role=TextRole.BLOCK_HEADER, color=th.AMBER_LIGHT)
                m_eq = Text(
                    "(-128) × (-128) = +16,384\n"
                    "Term 1: Sum = +16,384 (50% Full)\n"
                    "Term 2: Sum = +32,768 (OVERFLOW!)",
                    font=th.MONO, font_size=11, color=th.WHITE, line_spacing=1.3
                )
                m_sub = VStack(m_title, m_eq, gap=th.SPACE_SM).move_to(mult_block)
                mult_group = VGroup(mult_block, m_sub)

                act1_layout = HStack(mult_group, tank_16, gap=th.SPACE_XL).move_to(self.layout.main_stage_center())
                st.add(act1_layout)

                self.play(FadeIn(mult_group, shift=RIGHT * 0.2), Create(tank_16), run_time=1.0)

                # Fill Cycle 1: 50%
                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.play(tank_16.set_fluid_fraction(0.5, color=th.AMBER), run_time=0.5)

                # Fill Cycle 2: 115% OVERFLOW!
                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.play(tank_16.set_fluid_fraction(1.15, color=th.RED), run_time=0.5)
                self.screen_shake(intensity=0.06, cycles=3, run_time=0.25)
                self.wait(max(0.3, trk.duration - 2.8))
                st.takeaway("Two products are enough to burst a 16-bit register.", wait=1.2)

        # =====================================================================
        # ACT 2: 32-BIT HEADROOM INDUCTION PROOF
        # =====================================================================
        act2_narration = (
            "The fix is headroom: widen the accumulator to 32 bits. "
            "The worst case is every product hitting 16,384, which caps a 32-bit sum at 131,071 terms before overflow—"
            "far more than LLaMA's 8,192 hidden units, leaving 3 unused guard bits for safety."
        )
        with self.stage("ACT 2", "32-Bit Headroom Theorem", "Inductive Proof of Accumulator Capacity", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                headroom_eq = SemanticMath(
                    r"K_{\max} = \frac{2^{31} - 1}{(-128 \times -128)} = \frac{2,147,483,647}{16,384} = 131{,}071 \text{ MACs}",
                    role=TextRole.MATH_DISPLAY,
                    color=th.CYAN_LIGHT
                )

                stat_headroom = HStack(
                    th.metric_card("131,071", "Safe Vector Length (K)", "Zero overflow guarantee", color=th.GREEN, width=3.8, height=2.0),
                    th.metric_card("3 Guard Bits", "Spare in LLaMA (d=8192)", "Safety margin beyond worst case", color=th.AMBER, width=3.8, height=2.0),
                    th.metric_card("32 Bits", "Standard Accumulator Sizing", "ACC_WIDTH parameter", color=th.CYAN, width=3.8, height=2.0),
                    gap=th.SPACE_MD
                )

                proof_layout = VStack(headroom_eq, stat_headroom, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(proof_layout)

                self.play(Write(headroom_eq), FadeIn(stat_headroom, shift=UP * 0.2), run_time=1.0)
                clock.advance(self, delta_cycles=1, run_time=0.3)
                self.wait(max(0.3, trk.duration - 1.3))
                st.takeaway("32 bits of headroom absorbs the worst-case dot product.", wait=1.2)

        # =====================================================================
        # ACT 3: SIGN EXTENSION VS ZERO EXTENSION TRAP
        # =====================================================================
        act3_narration = (
            "But widening has a subtle rule. When you add a 16-bit product into a 32-bit accumulator, "
            "you must copy the product's sign bit across all the new upper bits—that is sign extension. "
            "Pad with zeros instead, and negative 5 silently becomes positive 65,531, corrupting the result."
        )
        with self.stage("ACT 3", "The Sign-Extension Trap", "Preserving Two's Complement Polarity in RTL", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                # 16-Bit Product Register (-5)
                prod_box = RoundedRectangle(corner_radius=0.1, width=10.2, height=1.0, stroke_color=th.RED, stroke_width=1.5, fill_color="#180b0b", fill_opacity=0.92)
                lbl_prod = SemanticText("16-BIT MULTIPLIER PRODUCT: -5  (MSB = 1)", role=TextRole.PROBE_LABEL, color=th.RED_LIGHT)
                val_prod = Text("1111 1111 1111 1011", font=th.MONO, weight=BOLD, font_size=15, color=th.RED_LIGHT)
                prod_content = VStack(lbl_prod, val_prod, gap=th.SPACE_XS).move_to(prod_box)
                grp_prod = VGroup(prod_box, prod_content)

                # Correct 32-bit Sign Extension: Upper 16 bits = 1111...
                good_box = RoundedRectangle(corner_radius=0.1, width=10.2, height=1.0, stroke_color=th.GREEN, stroke_width=1.5, fill_color="#071b11", fill_opacity=0.92)
                lbl_good = SemanticText("CORRECT SIGN EXTENSION: Replicate MSB to [31:16] ➔ Result: -5", role=TextRole.PROBE_LABEL, color=th.GREEN_LIGHT)
                val_good = Text("1111 1111 1111 1111 | 1111 1111 1111 1011", font=th.MONO, weight=BOLD, font_size=13, color=th.GREEN_LIGHT)
                good_content = VStack(lbl_good, val_good, gap=th.SPACE_XS).move_to(good_box)
                grp_good = VGroup(good_box, good_content)

                # Zero-Extension Disaster: Upper 16 bits = 0000...
                bad_box = RoundedRectangle(corner_radius=0.1, width=10.2, height=1.0, stroke_color=th.AMBER, stroke_width=1.5, fill_color="#1a1205", fill_opacity=0.92)
                lbl_bad = SemanticText("ZERO EXTENSION DISASTER: Upper 16 Bits Padded with 0s ➔ Result: +65,531!", role=TextRole.PROBE_LABEL, color=th.AMBER_LIGHT)
                val_bad = Text("0000 0000 0000 0000 | 1111 1111 1111 1011", font=th.MONO, weight=BOLD, font_size=13, color=th.AMBER_LIGHT)
                bad_content = VStack(lbl_bad, val_bad, gap=th.SPACE_XS).move_to(bad_box)
                grp_bad = VGroup(bad_box, bad_content)

                sign_stack = VStack(grp_prod, grp_good, grp_bad, gap=th.SPACE_MD).move_to(self.layout.main_stage_center())
                st.add(sign_stack)

                self.play(FadeIn(grp_prod, shift=DOWN * 0.2), run_time=0.6)
                clock.advance(self, delta_cycles=1, run_time=0.3)
                self.play(FadeIn(grp_good, shift=UP * 0.1), run_time=0.6)
                self.play(FadeIn(grp_bad, shift=UP * 0.1), run_time=0.6)
                self.wait(max(0.3, trk.duration - 2.1))
                st.takeaway("Widen with sign bits, never with zeros.", wait=1.2)

        # =====================================================================
        # ACT 4: COMBINATIONAL VS PIPELINED F_MAX
        # =====================================================================
        act4_narration = (
            "Speed is the last lesson. Chained back-to-back, the multiplier and adder form one 4-nanosecond critical path, "
            "so the chip can only clock around 250 megahertz. Insert a pipeline register between them and the slowest stage "
            "drops to 2.8 nanoseconds—pushing the clock toward 350 megahertz."
        )
        with self.stage("ACT 4", "Combinational vs Pipelined MAC", "Critical Path Delay & Timing Closure", narration=act4_narration) as st:
            with self.voiceover(act4_narration) as trk:
                # Visual datapath showing Multiplier -> Pipeline Register (16 DFFs) -> Adder
                m_stage = RoundedRectangle(corner_radius=0.1, width=3.2, height=2.2, stroke_color=th.AMBER, stroke_width=1.5, fill_color="#181106", fill_opacity=0.92)
                m_lbl = VStack(SemanticText("STAGE 1", role=TextRole.PROBE_LABEL, color=th.AMBER), Text("8×8 Multiplier\nt_mult ≈ 2.8 ns", font=th.MONO, font_size=11, color=th.TEXT, line_spacing=1.3)).move_to(m_stage)
                grp_m = VGroup(m_stage, m_lbl)

                pipe_reg = RoundedRectangle(corner_radius=0.08, width=1.6, height=2.2, stroke_color=th.CYAN, stroke_width=2.0, fill_color="#091f33", fill_opacity=0.95)
                pipe_lbl = VStack(SemanticText("DFF REG", role=TextRole.PROBE_LABEL, color=th.CYAN_LIGHT), Text("16 DFFs\n(t_cq ≈ 0.2ns)", font=th.MONO, font_size=10, color=th.CYAN, line_spacing=1.3)).move_to(pipe_reg)
                grp_pipe = VGroup(pipe_reg, pipe_lbl)

                a_stage = RoundedRectangle(corner_radius=0.1, width=3.2, height=2.2, stroke_color=th.GREEN, stroke_width=1.5, fill_color="#071b11", fill_opacity=0.92)
                a_lbl = VStack(SemanticText("STAGE 2", role=TextRole.PROBE_LABEL, color=th.GREEN), Text("32-bit Adder\nt_add ≈ 1.2 ns", font=th.MONO, font_size=11, color=th.TEXT, line_spacing=1.3)).move_to(a_stage)
                grp_a = VGroup(a_stage, a_lbl)

                w_m_p = Arrow(m_stage.get_right(), pipe_reg.get_left(), buff=0.08, color=th.CYAN_LIGHT, stroke_width=2.0)
                w_p_a = Arrow(pipe_reg.get_right(), a_stage.get_left(), buff=0.08, color=th.GREEN_LIGHT, stroke_width=2.0)

                pipe_chain = VGroup(HStack(grp_m, grp_pipe, grp_a, gap=th.SPACE_LG), w_m_p, w_p_a)

                stat_pipe = HStack(
                    th.metric_card("~250 MHz", "Unpipelined Combinational", "Critical path = 4.0 ns", color=th.RED, width=3.8, height=1.7),
                    th.metric_card("~350 MHz", "Pipelined Silicon MAC", "Stage path = 2.8 ns", color=th.GREEN, width=3.8, height=1.7),
                    gap=th.SPACE_LG
                )

                timing_layout = VStack(pipe_chain, stat_pipe, gap=th.SPACE_MD).move_to(self.layout.main_stage_center())
                st.add(timing_layout)

                self.play(FadeIn(pipe_chain, shift=DOWN * 0.2), run_time=0.9)
                clock.advance(self, delta_cycles=1, run_time=0.3)
                self.play(FadeIn(stat_pipe, shift=UP * 0.2), run_time=0.8)
                self.wait(max(0.3, trk.duration - 2.0))
                st.takeaway("One pipeline register nearly doubles the clock speed.", wait=1.2)
