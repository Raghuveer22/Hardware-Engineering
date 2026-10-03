"""
Lab 01: The Area Monster — Signed INT8 Hardware Multiplier & O(N^2) Silicon Scaling
Wallace Trees, Radix-4 Modified Booth Encoding & Silicon Area Dynamics.

Tailored for Software Engineers (3Blue1Brown Visual Standard):
- Act 0: The Elementary Atom: 1-Bit Multiplier as an AND Gate
- Act 1: The O(N^2) Silicon Area Explosion (Adder vs Multiplier Die Footprints)
- Act 2: The 8x8 AND Matrix & The Asymmetric Corner Case ((-128) * (-128) = +16,384)
- Act 3: Radix-4 Booth Recoding & Wallace Tree Compression (Logarithmic Reduction)
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
        # ACT 0: PRELORE — 1-BIT MULTIPLIER AS AN AND GATE
        # =====================================================================
        prelore_narration = (
            "Every integer multiplier is built from one humble cell: the AND gate. "
            "Multiply two binary digits and you get a one only when both inputs are one. "
            "Multiply two 8-bit numbers and you need every pair of bits—that's where the cost comes from."
        )
        with self.stage("PRIMER", "What a Multiplier Is Made Of", "AND Gates: The Elementary Multiplier Cell", narration=prelore_narration) as st:
            with self.voiceover(prelore_narration) as trk:
                # 3b1b style: Show the 1-bit multiplication definition and gate truth table
                mult_def = MathTex(
                    r"a \times b = a \land b",
                    font_size=42,
                    color=th.AMBER_LIGHT
                ).to_edge(UP, buff=1.3)
                st.add(mult_def)
                self.play(Write(mult_def), run_time=0.8)

                # Visual AND gate with live input toggles
                and_gate = VGroup(
                    Circle(radius=0.75, color=th.AMBER, stroke_width=2.5, fill_color="#1a1205", fill_opacity=0.9),
                    Text("&", font=th.MONO, weight=BOLD, font_size=36, color=th.AMBER_LIGHT)
                )
                and_gate[1].move_to(and_gate[0])

                in_wire1 = Line(LEFT * 1.6 + UP * 0.4, LEFT * 0.75 + UP * 0.4, color=th.CYAN_LIGHT, stroke_width=2.5)
                in_wire2 = Line(LEFT * 1.6 + DOWN * 0.4, LEFT * 0.75 + DOWN * 0.4, color=th.CYAN_LIGHT, stroke_width=2.5)
                out_wire = Line(RIGHT * 0.75, RIGHT * 1.6, color=th.GREEN_LIGHT, stroke_width=2.5)

                lbl_a = Text("A = 1", font=th.MONO, font_size=13, color=th.CYAN_LIGHT).next_to(in_wire1, LEFT, buff=0.1)
                lbl_b = Text("B = 1", font=th.MONO, font_size=13, color=th.CYAN_LIGHT).next_to(in_wire2, LEFT, buff=0.1)
                lbl_y = Text("Y = 1", font=th.MONO, weight=BOLD, font_size=13, color=th.GREEN_LIGHT).next_to(out_wire, RIGHT, buff=0.1)

                gate_schematic = VGroup(and_gate, in_wire1, in_wire2, out_wire, lbl_a, lbl_b, lbl_y).move_to(LEFT * 3.2 + DOWN * 0.3)

                # Truth table visual on right
                tt_rows = [
                    ("0 × 0 =", "0", th.MUTED),
                    ("0 × 1 =", "0", th.MUTED),
                    ("1 × 0 =", "0", th.MUTED),
                    ("1 × 1 =", "1", th.GREEN_LIGHT),
                ]
                tt_lines = VGroup(*[
                    HStack(
                        Text(eq, font=th.MONO, font_size=18, color=th.TEXT),
                        Text(ans, font=th.MONO, weight=BOLD, font_size=20, color=col),
                        gap=0.15
                    )
                    for eq, ans, col in tt_rows
                ]).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(RIGHT * 3.2 + DOWN * 0.3)

                st.add(gate_schematic, tt_lines)
                self.play(FadeIn(gate_schematic, shift=LEFT * 0.2), FadeIn(tt_lines, shift=RIGHT * 0.2), run_time=0.9)

                # Flash the 1 x 1 = 1 condition
                self.play(
                    and_gate[0].animate.set_stroke(color=th.WHITE, width=4.0),
                    tt_lines[3].animate.scale(1.2),
                    run_time=0.6
                )
                self.play(
                    and_gate[0].animate.set_stroke(color=th.AMBER, width=2.5),
                    tt_lines[3].animate.scale(1/1.2),
                    run_time=0.6
                )
                self.wait(max(0.3, trk.duration - 2.9))
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
                adder_die = DieFootprint("8-BIT ADDER", gates=42, width=3.0, height=3.4, color=th.GREEN)
                mult_die = DieFootprint("INT8 MULTIPLIER", gates=456, width=4.0, height=3.4, color=th.AMBER)
                fp_die = DieFootprint("FP32 MULTIPLIER", gates=7000, width=5.0, height=3.4, color=th.PURPLE)

                die_stage = HStack(adder_die, mult_die, fp_die, gap=th.SPACE_MD).move_to(self.layout.main_stage_center())
                st.add(die_stage)

                self.play(FadeIn(die_stage, shift=UP * 0.2), run_time=1.0)

                # Advance Clock & Trigger Thermal Glow on Multiplier
                clock.advance(self, delta_cycles=1, run_time=0.35)
                self.play(mult_die.thermal_glow(color=th.RED, scale_factor=1.08), run_time=0.6)
                self.screen_shake(intensity=0.03, cycles=2, run_time=0.2)
                self.wait(max(0.3, trk.duration - 2.15))
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
                grid_title = Text("64 PARTIAL PRODUCTS (8×8 AND GATES)", font=th.MONO, weight=BOLD, font_size=12, color=th.AMBER)
                grid_title.next_to(and_grid, UP, buff=0.18)
                grid_group = VGroup(and_grid, grid_title).move_to(LEFT * 3.4 + DOWN * 0.2)

                # Asymmetric proof card with LaTeX clarity
                proof_box = RoundedRectangle(corner_radius=0.12, width=5.6, height=3.4, stroke_color=th.CYAN, stroke_width=2.0, fill_color="#09182a", fill_opacity=0.92)
                p_hdr = Text("ASYMMETRIC TWO'S COMPLEMENT TRAP", font=th.MONO, weight=BOLD, font_size=13, color=th.CYAN)
                p_eq = MathTex(r"(-128) \times (-128) = +16{,}384 = +2^{14}", font_size=24, color=th.WHITE)
                p_15 = Text("15-bit signed: bit 14 is SIGN ➔ -16,384 (CORRUPT!)", font=th.MONO, font_size=11, color=th.RED_LIGHT)
                p_16 = Text("16-bit signed: bit 15 is 0    ➔ +16,384 (SAFE!)", font=th.MONO, font_size=11, color=th.GREEN_LIGHT)
                p_content = VStack(p_hdr, p_eq, p_15, p_16, gap=th.SPACE_SM).move_to(proof_box)
                proof_group = VGroup(proof_box, p_content).move_to(RIGHT * 3.4 + DOWN * 0.2)

                st.add(grid_group, proof_group)

                self.play(FadeIn(grid_group, shift=LEFT * 0.2), FadeIn(proof_group, shift=RIGHT * 0.2), run_time=1.0)
                clock.advance(self, delta_cycles=1, run_time=0.35)
                self.wait(max(0.3, trk.duration - 1.35))
                st.takeaway("64 AND gates, and 16 full bits to hold the result.", wait=1.2)

        # =====================================================================
        # ACT 3: RADIX-4 BOOTH RECODING & WALLACE COMPRESSION (CONCEPT)
        # =====================================================================
        act3_narration = (
            "Now, an important honest note. Our teaching RTL simply writes a times b and lets the synthesis tool "
            "infer the multiplier. But real silicon rarely does that. Industry multipliers use two tricks: Booth recoding "
            "scans the multiplier in overlapping 3-bit windows, halving eight rows down to four, and a Wallace tree "
            "squeezes those four rows into just two vectors in logarithmic time."
        )
        with self.stage("ACT 3", "Booth Recoding & Wallace Tree", "CONCEPT: How Industry Chips Optimize the Multiplier", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                # Concept badge
                concept_badge = VGroup(
                    RoundedRectangle(corner_radius=0.08, width=3.4, height=0.5, stroke_color=th.AMBER, stroke_width=1.5, fill_color="#1a1205", fill_opacity=0.9),
                    Text("CONCEPT (not rtl/)", font=th.MONO, weight=BOLD, font_size=12, color=th.AMBER_LIGHT)
                )
                concept_badge[1].move_to(concept_badge[0])

                # Bit row display with sliding window
                bits = ["0", "1", "1", "0", "1", "0", "1", "0", "0"]
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
                t_csa1 = Text("4 Booth Rows ➔ 3:2 CSA Compressor Level 1 ➔ 2 Carry-Save Vectors ➔ 16-Bit CPA", font=th.MONO, font_size=12, color=th.GREEN_LIGHT)
                t_csa2 = Text("Gate Delay: O(log N) vs O(N) Ripple Carry  |  rtl/multiplier_int8.sv = 1 inferred $mul", font=th.MONO, font_size=11, color=th.MUTED)
                csa_content = VStack(t_csa1, t_csa2, gap=th.SPACE_XS).move_to(csa_panel)
                csa_group = VGroup(csa_panel, csa_content).next_to(rule_probe, DOWN, buff=0.3)

                booth_layout = VGroup(concept_badge, bit_row, rule_probe, csa_group).arrange(DOWN, buff=th.SPACE_MD).move_to(self.layout.main_stage_center())
                st.add(booth_layout, window)

                self.play(FadeIn(concept_badge), Create(bit_row), Create(window), FadeIn(rule_probe), FadeIn(csa_group), run_time=1.0)

                # Slide window across bit triplets
                for shift_step, rule_txt in [(1, "+2×M (Left Shift 1)"), (2, "-1×M (Invert + 1)"), (3, "-2×M")]:
                    clock.advance(self, delta_cycles=1, run_time=0.35)
                    self.play(
                        window.animate.shift(RIGHT * 1.1),
                        rule_probe.set_value(rule_txt),
                        run_time=0.4
                    )
                self.wait(max(0.3, trk.duration - 2.8))
                st.takeaway("Booth halves the rows; Wallace compresses them in log time.", wait=1.2)

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
                power_eq = MathTex(
                    r"\mathcal{P}_{\text{dyn}} = \alpha \cdot C_{\text{wire}} \cdot V_{\text{DD}}^2 \cdot f",
                    font_size=38,
                    color=th.AMBER_LIGHT
                ).to_edge(UP, buff=1.4)
                st.add(power_eq)
                self.play(Write(power_eq), run_time=0.8)

                # Visual feature tiles
                tile1 = RoundedRectangle(corner_radius=0.1, width=3.4, height=2.4, stroke_color=th.CYAN, stroke_width=2.0, fill_color="#091b2e", fill_opacity=0.92)
                t1_val = Text("16×", font=th.SANS, weight=BOLD, font_size=36, color=th.CYAN_LIGHT)
                t1_lbl = Text("INT8 Density vs FP32", font=th.MONO, font_size=12, color=th.TEXT)
                t1_sub = Text("16× more multipliers/mm²", font=th.MONO, font_size=10, color=th.CYAN)
                c1 = VStack(t1_val, t1_lbl, t1_sub, gap=0.1).move_to(tile1)
                grp1 = VGroup(tile1, c1)

                tile2 = RoundedRectangle(corner_radius=0.1, width=3.4, height=2.4, stroke_color=th.GREEN, stroke_width=2.0, fill_color="#071b11", fill_opacity=0.92)
                t2_val = Text("4,096", font=th.SANS, weight=BOLD, font_size=36, color=th.GREEN_LIGHT)
                t2_lbl = Text("MACs per Instruction", font=th.MONO, font_size=12, color=th.TEXT)
                t2_sub = Text("NVIDIA mma.sync warp", font=th.MONO, font_size=10, color=th.GREEN)
                c2 = VStack(t2_val, t2_lbl, t2_sub, gap=0.1).move_to(tile2)
                grp2 = VGroup(tile2, c2)

                tile3 = RoundedRectangle(corner_radius=0.1, width=3.4, height=2.4, stroke_color=th.PURPLE, stroke_width=2.0, fill_color="#1e0a2e", fill_opacity=0.92)
                t3_val = Text("456 Gates", font=th.SANS, weight=BOLD, font_size=30, color=th.PURPLE_LIGHT)
                t3_lbl = Text("Silicon Gate Budget", font=th.MONO, font_size=12, color=th.TEXT)
                t3_sub = Text("vs 7,000 gates for FP32", font=th.MONO, font_size=10, color=th.PURPLE)
                c3 = VStack(t3_val, t3_lbl, t3_sub, gap=0.1).move_to(tile3)
                grp3 = VGroup(tile3, c3)

                tiles = HStack(grp1, grp2, grp3, gap=th.SPACE_MD).move_to(DOWN * 0.8)
                st.add(tiles)

                self.play(FadeIn(tiles, shift=UP * 0.2), run_time=0.9)
                clock.advance(self, delta_cycles=1, run_time=0.35)
                self.wait(max(0.3, trk.duration - 2.05))
                st.takeaway("Smaller multipliers mean thousands more of them per chip.", wait=1.2)
