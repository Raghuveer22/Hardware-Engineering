"""
Lab 02: Accumulator Headroom — The MAC Unit & Sign Extension
Architectural Implementation: Declarative Stage Lifecycle, Constraint Layout,
Dynamic Liquid Tank Gauge, Voiceover Auto-Sync, and Vector LaTeX MathTex.
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
    AccumulatorGauge,
    SiliconWire,
    HardwareConfig,
    TextRole,
    SemanticText,
    SemanticMath,
    HStack,
    VStack,
    ConstraintAnchor,
    PinProbe,
)


class Lab02MACUnit(KineticSiliconScene):
    def construct(self):
        config = HardwareConfig(data_width=8, vector_k=4096)
        clock = KineticClock(initial_cycle=0)

        # Ambient Clock HUD at top right
        ticker = clock.create_ticker_badge(prefix="CLK: T = ", color=th.AMBER_LIGHT)
        ticker.to_corner(UR, buff=0.35)
        self.add(ticker)

        # =====================================================================
        # ACT 1: THE BURSTING 16-BIT ACCUMULATOR TANK
        # =====================================================================
        act1_narration = "A single INT8 product is up to +16,129. After only two additions, a 16-bit accumulator catastrophically overflows into negative numbers!"
        with self.stage("ACT 1", "Accumulator Bit Growth", "Why 16-Bit Registers Burst in Dot Products", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                # 16-Bit Tank Widget
                tank_16 = th.LiquidTankWidget(capacity=32767, width=2.8, height=3.4, title="16-BIT REGISTER", fluid_color=th.RED)
                
                # Multiplier Input Block
                mult_block = RoundedRectangle(
                    corner_radius=0.12, width=3.4, height=3.4,
                    stroke_color=th.AMBER, stroke_width=2.0,
                    fill_color="#181106", fill_opacity=0.9
                )
                m_title = SemanticText("INT8 MULTIPLIER", role=TextRole.BLOCK_HEADER, color=th.AMBER_LIGHT)
                m_eq = SemanticText("(-128) × (-126) ➔ +16,128", role=TextRole.BUS_VALUE, color=th.WHITE)
                m_sub = VStack(m_title, m_eq, gap=th.SPACE_SM).move_to(mult_block)
                mult_group = VGroup(mult_block, m_sub)

                act1_layout = HStack(mult_group, tank_16, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(act1_layout)

                self.play(FadeIn(mult_group, shift=RIGHT * 0.2), Create(tank_16), run_time=1.0)

                # Fill Cycle 1: 50%
                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.play(tank_16.set_fluid_fraction(0.5, color=th.AMBER), run_time=0.5)

                # Fill Cycle 2: 105% OVERFLOW!
                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.play(tank_16.set_fluid_fraction(1.15, color=th.RED), run_time=0.5)
                self.screen_shake(intensity=0.06, cycles=3, run_time=0.25)
                self.wait(max(0.2, trk.duration - 2.8))

        # =====================================================================
        # ACT 2: 32-BIT HEADROOM INDUCTION PROOF
        # =====================================================================
        act2_narration = "In synthesizable RTL, the accumulator expands to 32 bits. This provides headroom for up to 131,072 consecutive dot products."
        with self.stage("ACT 2", "32-Bit Headroom Theorem", "Inductive Proof of Accumulator Capacity", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                headroom_eq = SemanticMath(
                    r"K_{\text{safe}} = \frac{2^{31} - 1}{(-128 \times -128)} = \frac{2,147,483,647}{16,384} \approx 131,072 \text{ MACs}",
                    role=TextRole.MATH_DISPLAY,
                    color=th.CYAN_LIGHT
                )

                stat_headroom = HStack(
                    th.metric_card("131,072", "Safe Vector Length (K)", color=th.GREEN, width=4.0, height=2.0),
                    th.metric_card("32 Bits", "Standard Accumulator Sizing", color=th.CYAN, width=4.0, height=2.0),
                    gap=th.SPACE_MD
                )

                proof_layout = VStack(headroom_eq, stat_headroom, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(proof_layout)

                self.play(Write(headroom_eq), FadeIn(stat_headroom, shift=UP * 0.2), run_time=min(trk.duration, 1.2))
                self.wait(max(0.2, trk.duration - 1.2))

        # =====================================================================
        # ACT 3: SIGN EXTENSION VS ZERO EXTENSION TRAP
        # =====================================================================
        act3_narration = "Signed INT8 products must duplicate the MSB sign bit across all 16 upper accumulator wires. Zero-extending negative numbers destroys neural accuracy."
        with self.stage("ACT 3", "The Sign-Extension Trap", "Preserving Two's Complement Polarity in RTL", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                # MSB Bit Register (8-bit product)
                prod_reg = th.BitRegister(width_bits=8, initial_val="11110000", highlight_msb=True, msb_color=th.RED)
                prod_lbl = SemanticText("16-Bit Signed Product: MSB = '1' (Negative)", role=TextRole.PROBE_LABEL, color=th.RED_LIGHT)
                prod_group = VStack(prod_lbl, prod_reg, gap=th.SPACE_XS)

                # Extended 16-Bit Register showing sign extension
                ext_reg = th.BitRegister(width_bits=16, initial_val="1111111111110000", highlight_msb=True, msb_color=th.GREEN)
                ext_lbl = SemanticText("Correctly Sign-Extended: 8 Upper Bits Duplicated from MSB", role=TextRole.PROBE_LABEL, color=th.GREEN_LIGHT)
                ext_group = VStack(ext_lbl, ext_reg, gap=th.SPACE_XS)

                registers_layout = VStack(prod_group, ext_group, gap=th.SPACE_MD).move_to(self.layout.main_stage_center())
                st.add(registers_layout)

                self.play(FadeIn(prod_group, shift=DOWN * 0.2), run_time=0.6)
                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.play(FadeIn(ext_group, shift=UP * 0.2), run_time=0.6)
                self.wait(max(0.2, trk.duration - 1.8))

        # =====================================================================
        # ACT 4: COMBINATIONAL VS PIPELINED F_MAX
        # =====================================================================
        act4_narration = "A single-cycle MAC chains multiplier and adder delays together, dropping F_max to 380 MHz. Pipelining doubles frequency to 1.1 GHz."
        with self.stage("ACT 4", "Combinational vs Pipelined MAC", "Critical Path Delay & Timing Closure", narration=act4_narration) as st:
            with self.voiceover(act4_narration) as trk:
                freq_cards = HStack(
                    th.metric_card("380 MHz", "Combinational Unpipelined MAC", "Critical Path: T_mult + T_add", color=th.RED, width=4.6, height=2.2),
                    th.metric_card("1.1 GHz", "Pipelined Silicon MAC", "Inter-stage Pipeline Flip-Flop", color=th.GREEN, width=4.6, height=2.2),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(freq_cards)

                self.play(FadeIn(freq_cards, shift=UP * 0.2), run_time=min(trk.duration, 1.0))
                self.wait(max(0.2, trk.duration - 1.0))
