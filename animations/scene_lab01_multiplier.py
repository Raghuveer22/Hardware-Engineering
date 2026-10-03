"""
Lab 01: The Area Monster — Signed INT8 Hardware Multiplier & O(N^2) Silicon Scaling
Wallace Trees, Radix-4 Modified Booth Encoding & Silicon Area Dynamics.

Tailored for Software Engineers:
- Act 1: The O(N^2) Silicon Area Explosion (42 Adder Gates vs 456 INT8 vs 7,000 FP32 Gates)
- Act 2: The 8x8 AND Matrix & The Asymmetric Corner Case ((-128) * (-128) = +16,384)
- Act 3: Radix-4 Booth Recoding & Wallace Tree 3:2 Compressor Reduction
- Act 4: Dynamic Power & NVIDIA Tensor Core mma.sync Architecture
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
    DieFootprint,
    PinProbe,
    fit_to_bounds,
)


class Lab01Multiplier(KineticSiliconScene):
    def construct(self):
        config = HardwareConfig(data_width=8)
        clock = KineticClock(initial_cycle=0)

        # Ambient Clock HUD at top right (compact)
        ticker = clock.create_ticker_badge(prefix="CLK: T = ", color=th.AMBER_LIGHT)
        ticker.to_corner(UR, buff=0.25)
        self.add(ticker)

        # =====================================================================
        # ACT 0: PRELORE — WHAT A MULTIPLIER IS MADE OF
        # =====================================================================
        prelore_narration = (
            "Every integer multiplier is built from one humble cell: the AND gate. "
            "Multiply two binary digits and you get a one only when both inputs are one. "
            "Multiply two 8-bit numbers and you need every pair of bits—that's where the cost comes from."
        )
        with self.stage("PRIMER", "What a Multiplier Is Made Of", "AND Gates: The Building Block", narration=prelore_narration) as st:
            with self.voiceover(prelore_narration) as trk:
                pre_cards = HStack(
                    th.metric_card("0 AND 0 = 0", "No match", "One zero is enough", color=th.MUTED, width=3.6, height=2.3),
                    th.metric_card("1 AND 0 = 0", "Still zero", "Both must agree", color=th.MUTED, width=3.6, height=2.3),
                    th.metric_card("1 AND 1 = 1", "The only 1", "That single 1 is a partial product", color=th.AMBER, width=3.6, height=2.3),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(pre_cards)
                self.play(FadeIn(pre_cards, shift=UP * 0.2), run_time=1.0)
                self.wait(max(0.3, trk.duration - 1.0))
                st.takeaway("Multiply two digits = one AND gate.", wait=1.2)

        # =====================================================================
        # ACT 1: THE SILICON AREA MONSTER & O(N²) DIE SCALING
        # =====================================================================
        act1_narration = (
            "Now the cost. An 8-bit adder needs only 42 gates, because addition is cheap. "
            "An 8-bit multiplier needs 456 gates, because it has to AND every pair of bits—an N-squared explosion. "
            "A 32-bit float multiplier needs 7,000. That is why shrinking to INT8 buys sixteen times more engines per chip."
        )
        with self.stage("ACT 1", "The O(N²) Silicon Area Monster", "Adder vs Multiplier Die Footprints", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                adder_die = DieFootprint("8-BIT ADDER", gates=42, width=2.8, height=3.2, color=th.GREEN)
                mult_die = DieFootprint("INT8 MULTIPLIER", gates=456, width=3.8, height=3.2, color=th.AMBER)
                fp_die = DieFootprint("FP32 MULTIPLIER", gates=7000, width=4.8, height=3.2, color=th.PURPLE)

                die_stage = HStack(adder_die, mult_die, fp_die, gap=th.SPACE_MD).move_to(self.layout.main_stage_center())
                st.add(die_stage)

                self.play(FadeIn(die_stage, shift=UP * 0.2), run_time=1.0)

                # Advance Clock & Trigger Thermal Glow on Multiplier
                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.play(mult_die.thermal_glow(color=th.RED, scale_factor=1.08), run_time=0.6)
                self.screen_shake(intensity=0.03, cycles=2, run_time=0.2)
                self.wait(max(0.3, trk.duration - 2.2))
                st.takeaway("Addition is cheap. Multiplication is N-squared.", wait=1.2)

        # =====================================================================
        # ACT 2: 8x8 AND MATRIX & ASYMMETRIC CORNER CASE
        # =====================================================================
        act2_narration = (
            "Multiplying two 8-bit numbers produces an 8-by-8 grid of partial products: 64 AND gates. "
            "And two's complement has a hidden trap. Negative 128 times negative 128 is positive 16,384, "
            "but a 15-bit register misreads that as negative 16,384. You need all 16 bits to hold the true answer."
        )
        with self.stage("ACT 2", "The 8×8 AND Matrix & 16-Bit Growth", "Partial Products & The Asymmetric Corner Case", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                # 8x8 Partial product dot array representing 64 AND gates
                and_grid = th.dot_grid(rows=8, cols=8, dx=0.40, dy=0.30, radius=0.065, color=th.AMBER)
                grid_title = SemanticText("64 PARTIAL PRODUCTS (8×8 AND GATES)", role=TextRole.PROBE_LABEL, color=th.AMBER)
                grid_title.next_to(and_grid, UP, buff=0.18)
                grid_group = VGroup(and_grid, grid_title)

                # Asymmetric proof card
                proof_card = RoundedRectangle(corner_radius=0.12, width=5.8, height=3.2, stroke_color=th.CYAN, stroke_width=1.5, fill_color="#09182a", fill_opacity=0.92)
                p_hdr = SemanticText("ASYMMETRIC TWO'S COMPLEMENT PROOF", role=TextRole.BLOCK_HEADER, color=th.CYAN)
                p_line1 = Text("(-128) × (-128) = +16,384", font=th.MONO, weight=BOLD, font_size=15, color=th.WHITE)
                p_line2 = Text("15-bit signed: bit 14 is sign ➔ -16,384 (ERROR!)", font=th.MONO, font_size=11, color=th.RED_LIGHT)
                p_line3 = Text("16-bit signed: 0b0100_0000_0000_0000 ➔ +16,384", font=th.MONO, font_size=11, color=th.GREEN_LIGHT)
                p_sub = VStack(p_hdr, p_line1, p_line2, p_line3, gap=th.SPACE_SM).move_to(proof_card)
                fit_to_bounds(p_sub, max_width=5.4)
                proof_group = VGroup(proof_card, p_sub)

                act2_layout = HStack(grid_group, proof_group, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(act2_layout)

                self.play(FadeIn(grid_group), FadeIn(proof_group, shift=RIGHT * 0.2), run_time=1.0)
                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.wait(max(0.3, trk.duration - 1.4))
                st.takeaway("64 AND gates, and 16 full bits to hold the result.", wait=1.2)

        # =====================================================================
        # ACT 3: RADIX-4 BOOTH RECODING & WALLACE COMPRESSION
        # =====================================================================
        act3_narration = (
            "Engineers shrink that cost with two tricks. Booth recoding scans the multiplier in overlapping 3-bit windows, "
            "halving eight partial-product rows down to four. A Wallace tree then squeezes those four rows into just two "
            "vectors in logarithmic time, instead of adding them one by one."
        )
        with self.stage("ACT 3", "Booth Recoding & Wallace CSA Tree", "Halving Rows to 4 & O(log N) Carry-Save Reduction", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                # Top: Bit row display with sliding window
                bits = ["0", "1", "1", "0", "1", "0", "1", "0", "0"] # 8 bits + implied 0
                bit_row = th.bit_row(bits, cell_w=0.55, cell_h=0.70, font_size=18)
                
                # Sliding 3-bit window
                window = RoundedRectangle(
                    corner_radius=0.08, width=1.85, height=0.85,
                    stroke_color=th.CYAN, stroke_width=2.5,
                    fill_color=th.CYAN_DARK, fill_opacity=0.3
                ).move_to(bit_row[0].get_center() + RIGHT * 0.55)

                rule_probe = PinProbe("BOOTH RULE", "Triplet: [y_2i+1, y_2i, y_2i-1] ➔ Op: +1×M", color=th.CYAN)
                rule_probe.next_to(bit_row, DOWN, buff=0.35)

                # Wallace Tree Reduction Diagram
                csa_panel = RoundedRectangle(corner_radius=0.1, width=10.2, height=1.4, stroke_color=th.GREEN_DARK, stroke_width=1.5, fill_color="#071b11", fill_opacity=0.92)
                t_csa1 = SemanticText("4 Booth Rows ➔ 3:2 CSA Compressor Level 1 ➔ 2 Carry-Save Vectors ➔ 16-Bit CPA", role=TextRole.PROBE_LABEL, color=th.GREEN_LIGHT)
                t_csa2 = Text("Gate Delay: O(log N) vs O(N) Ripple Carry  |  Area: 456 Synthesizable Gates", font=th.MONO, font_size=11, color=th.MUTED)
                csa_content = VStack(t_csa1, t_csa2, gap=th.SPACE_XS).move_to(csa_panel)
                csa_group = VGroup(csa_panel, csa_content).next_to(rule_probe, DOWN, buff=0.3)

                booth_layout = VGroup(bit_row, rule_probe, csa_group).move_to(self.layout.main_stage_center())
                st.add(booth_layout, window)

                self.play(Create(bit_row), Create(window), FadeIn(rule_probe), FadeIn(csa_group), run_time=1.0)

                # Slide window across bit triplets
                for shift_step, rule_txt in [(1, "+2×M (Left Shift 1)"), (2, "-1×M (Invert + 1)"), (3, "-2×M")]:
                    clock.advance(self, delta_cycles=1, run_time=0.35)
                    self.play(
                        window.animate.shift(RIGHT * 1.1),
                        rule_probe.set_value(rule_txt),
                        run_time=0.4
                    )
                self.wait(max(0.3, trk.duration - 2.8))
                st.takeaway("Booth halves the rows. Wallace compresses them in log time.", wait=1.2)

        # =====================================================================
        # ACT 4: DYNAMIC POWER & TENSOR CORE SCALING
        # =====================================================================
        act4_narration = (
            "Area matters because power follows it. Dynamic power grows with capacitance times voltage squared, "
            "and a smaller circuit wastes less of both. Since INT8 multipliers are sixteen times smaller than FP32, "
            "modern Tensor Cores pack thousands of them and fire 4,096 multiply-accumulates in a single instruction."
        )
        with self.stage("ACT 4", "Tensor Core Co-Design", "Silicon Power Formula & mma.sync Tensor Core Mapping", narration=act4_narration) as st:
            with self.voiceover(act4_narration) as trk:
                power_eq = SemanticMath(
                    r"\mathcal{P}_{\text{dyn}} = \alpha \cdot C_{\text{wire}} \cdot V_{\text{DD}}^2 \cdot f",
                    role=TextRole.MATH_DISPLAY,
                    color=th.AMBER_LIGHT
                )

                metric_cards = HStack(
                    th.metric_card("16×", "INT8 Multipliers per mm²", color=th.CYAN, width=3.6, height=2.2),
                    th.metric_card("4,096 MACs", "NVIDIA mma.sync Per Warp", color=th.GREEN, width=3.6, height=2.2),
                    th.metric_card("456 Gates", "INT8 vs 7,000 FP32 Gates", color=th.PURPLE, width=3.6, height=2.2),
                    gap=th.SPACE_MD
                )

                content_layout = VStack(power_eq, metric_cards, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(content_layout)

                self.play(Write(power_eq), FadeIn(metric_cards, shift=UP * 0.2), run_time=1.0)
                clock.advance(self, delta_cycles=1, run_time=0.3)
                self.wait(max(0.3, trk.duration - 1.3))
                st.takeaway("Smaller multipliers mean thousands more of them per chip.", wait=1.2)
