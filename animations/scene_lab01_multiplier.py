"""
Lab 01: The Area Monster — Signed INT8 Hardware Multiplier & O(N^2) Silicon Scaling
Architectural Implementation: Declarative Stage Lifecycle, Constraint Layout,
DieFootprint Standard Cells, Voiceover Auto-Sync, and Semantic Typography.
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
)


class Lab01Multiplier(KineticSiliconScene):
    def construct(self):
        config = HardwareConfig(data_width=8)
        clock = KineticClock(initial_cycle=0)

        # Ambient Clock HUD at top right
        ticker = clock.create_ticker_badge(prefix="CLK: T = ", color=th.AMBER_LIGHT)
        ticker.to_corner(UR, buff=0.35)
        self.add(ticker)

        # =====================================================================
        # ACT 1: THE SILICON AREA MONSTER & O(N²) DIE SCALING
        # =====================================================================
        act1_narration = "While an adder takes 42 gates, a multiplier explodes to 456 gates (O(N²)). Switching from FP32 to INT8 saves 16× silicon area."
        with self.stage("ACT 1", "The O(N²) Silicon Area Monster", "Adder vs Multiplier Die Footprints", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                adder_die = DieFootprint("8-BIT ADDER", gates=42, width=3.4, height=3.4, color=th.GREEN)
                mult_die = DieFootprint("INT8 MULTIPLIER", gates=456, width=3.4, height=3.4, color=th.AMBER)
                fp_die = DieFootprint("FP32 MULTIPLIER", gates=7000, width=3.8, height=3.4, color=th.PURPLE)

                die_stage = HStack(adder_die, mult_die, fp_die, gap=th.SPACE_MD).move_to(self.layout.main_stage_center())
                st.add(die_stage)

                self.play(FadeIn(die_stage, shift=UP * 0.2), run_time=min(trk.duration * 0.6, 1.0))

                # Advance Clock & Trigger Thermal Glow on Multiplier
                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.play(mult_die.thermal_glow(color=th.RED, scale_factor=1.12), run_time=0.6)
                self.screen_shake(intensity=0.03, cycles=2, run_time=0.2)
                self.wait(max(0.2, trk.duration - 2.2))

        # =====================================================================
        # ACT 2: RADIX-4 MODIFIED BOOTH RECODING
        # =====================================================================
        act2_narration = "Standard multipliers generate 8 rows of partial products. Radix-4 Booth recodes bits in triplets, cutting rows in half to 4."
        with self.stage("ACT 2", "Radix-4 Modified Booth Recoding", "Halving Partial Product Rows from N to N/2", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                # Bit row display with sliding window
                bits = ["0", "1", "1", "0", "1", "0", "1", "0", "0"] # 8 bits + implied 0
                bit_row = th.bit_row(bits, cell_w=0.55, cell_h=0.75, font_size=20)
                
                # Sliding 3-bit window
                window = RoundedRectangle(
                    corner_radius=0.08, width=1.85, height=0.95,
                    stroke_color=th.CYAN, stroke_width=2.5,
                    fill_color=th.CYAN_DARK, fill_opacity=0.3
                ).move_to(bit_row[0].get_center() + RIGHT * 0.55)

                rule_probe = PinProbe("BOOTH RULE", "Triplet: [y_2i+1, y_2i, y_2i-1] ➔ Op: +1×M", color=th.CYAN)
                rule_probe.next_to(bit_row, DOWN, buff=th.SPACE_LG)

                booth_group = VStack(bit_row, rule_probe, gap=th.SPACE_MD).move_to(self.layout.main_stage_center())
                st.add(booth_group, window)

                self.play(Create(bit_row), Create(window), FadeIn(rule_probe), run_time=1.0)

                # Slide window across bit triplets
                for shift_step, rule_txt in [(1, "+2×M (Left Shift 1)"), (2, "-1×M (Invert + 1)"), (3, "-2×M")]:
                    clock.advance(self, delta_cycles=1, run_time=0.35)
                    self.play(
                        window.animate.shift(RIGHT * 1.1),
                        rule_probe.set_value(rule_txt),
                        run_time=0.4
                    )
                self.wait(max(0.2, trk.duration - 2.8))

        # =====================================================================
        # ACT 3: WALLACE TREE CARRY-SAVE REDUCTION
        # =====================================================================
        act3_narration = "In physical silicon, ripple adders are too slow. Wallace tree carry-save reduction compresses partial products in O(log N) latency."
        with self.stage("ACT 3", "Wallace Tree Carry-Save Compression", "O(log N) Critical Path Reduction", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                # 8x8 Dot Matrix compressing into 2 rows
                dot_matrix = th.dot_grid(rows=6, cols=8, dx=0.5, dy=0.4, radius=0.08, color=th.AMBER)
                dot_matrix.move_to(self.layout.main_stage_center())
                st.add(dot_matrix)

                self.play(FadeIn(dot_matrix, shift=DOWN * 0.2), run_time=0.8)

                # Compression pulse: 6 rows compress down to 2 rows (Sum & Carry vectors)
                compressed_dots = th.dot_grid(rows=2, cols=8, dx=0.5, dy=0.4, radius=0.09, color=th.GREEN)
                compressed_dots.move_to(self.layout.main_stage_center())

                latency_probe = PinProbe("CRITICAL PATH", "Latency: O(log_1.5 N) = 4 Compressor Stages", color=th.GREEN)
                latency_probe.next_to(compressed_dots, DOWN, buff=th.SPACE_MD)

                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.play(
                    Transform(dot_matrix, compressed_dots),
                    FadeIn(latency_probe),
                    run_time=0.8
                )
                self.wait(max(0.2, trk.duration - 2.0))

        # =====================================================================
        # ACT 4: DYNAMIC POWER & TENSOR CORE SCALING
        # =====================================================================
        act4_narration = "Dynamic switching power scales with capacitance and voltage squared. INT8 precision enables 16× more multipliers on chip."
        with self.stage("ACT 4", "Tensor Core Co-Design", "Silicon Power Formula & Architectural Density", narration=act4_narration) as st:
            with self.voiceover(act4_narration) as trk:
                # Dynamic Power Formula via SemanticMath
                power_eq = SemanticMath(
                    r"\mathcal{P}_{\text{dyn}} = \alpha \cdot C_{\text{wire}} \cdot V_{\text{DD}}^2 \cdot f",
                    role=TextRole.MATH_DISPLAY,
                    color=th.AMBER_LIGHT
                )

                metric_cards = HStack(
                    th.metric_card("16×", "INT8 Multipliers per mm²", color=th.CYAN, width=3.6, height=2.2),
                    th.metric_card("20×", "Dynamic Energy Reduction", color=th.GREEN, width=3.6, height=2.2),
                    th.metric_card("456 Gates", "INT8 vs 7,000 FP32 Gates", color=th.PURPLE, width=3.6, height=2.2),
                    gap=th.SPACE_MD
                )

                content_layout = VStack(power_eq, metric_cards, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(content_layout)

                self.play(Write(power_eq), FadeIn(metric_cards, shift=UP * 0.2), run_time=min(trk.duration, 1.2))
                self.wait(max(0.2, trk.duration - 1.2))
