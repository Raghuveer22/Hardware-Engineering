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
            "Now the cost. An 8-bit adder is about 42 gates. An 8-bit multiplier is about 456, "
            "so its die is drawn about three times wider, the square root of that area ratio. "
            "A 32-bit float multiplier is about 7,000 gates. At this scale it would be roughly thirteen times wider than the adder, so it is not drawn."
        )
        with self.stage("ACT 1", "The O(N²) Silicon Area Monster", "Adder vs Multiplier Die Footprints", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                # Linear size tracks sqrt(gates), so area tracks the gate count.
                # sqrt(456/42) ≈ 3.3. sqrt(7000/42) ≈ 12.9, which does not fit.
                adder_die = DieFootprint("8-BIT ADDER", gates=42, width=1.15, height=1.35, color=th.GREEN)
                mult_die = DieFootprint("INT8 MULTIPLIER", gates=456, width=3.8, height=3.6, color=th.AMBER)
                fp_note = Text(
                    "FP32 multiplier\n~7,000 gates\nnot drawn:\n~13× the adder's width",
                    font=th.MONO, font_size=14, color=th.PURPLE_LIGHT, line_spacing=1.15,
                )
                die_stage = HStack(adder_die, mult_die, fp_note, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(die_stage)

                self.play(FadeIn(die_stage, shift=UP * 0.2), run_time=1.0)
                self.wait(max(0.3, trk.duration - 1.0))
                st.takeaway("456 gates is about 11× the area of 42. The picture uses that scale.", wait=1.2)

        # =====================================================================
        # ACT 2: 8x8 AND MATRIX & ASYMMETRIC CORNER CASE
        # =====================================================================
        act2_narration = (
            "Watch a real multiply: 6 times 5. Each 1 in the multiplier copies the multiplicand; each 0 copies nothing. "
            "The same rule at 8 bits is 64 AND gates. And negative 128 times negative 128 is positive 16,384, "
            "which a 15-bit register misreads as negative 16,384. You need all 16 bits."
        )
        with self.stage("ACT 2", "The 8×8 AND Matrix & 16-Bit Growth", "Partial Products & The Asymmetric Corner Case", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                # 6 × 5 = 30. Rows that correspond to a 1 in 0101 are copies of 0110.
                school = Text(
                    "      0 1 1 0     6\n"
                    "    × 0 1 0 1     5\n"
                    "    ---------\n"
                    "      0 1 1 0     ×1\n"
                    "    0 0 0 0       ×0\n"
                    "  0 1 1 0         ×1\n"
                    "0 0 0 0           ×0\n"
                    "= 0 1 1 1 1 0    30",
                    font=th.MONO, font_size=16, color=th.WHITE, line_spacing=1.05,
                )
                grid_title = Text("PARTIAL PRODUCTS ARE AND GATES", font=th.MONO, weight=BOLD, font_size=12, color=th.AMBER)
                grid_note = Text("INT8 is this picture with 64 ANDs, not 64 identical dots.", font=th.MONO, font_size=11, color=th.MUTED)
                grid_group = VGroup(grid_title, school, grid_note).arrange(DOWN, buff=0.14).move_to(LEFT * 3.3 + DOWN * 0.15)

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
                self.wait(max(0.3, trk.duration - 1.0))
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

                # y = 0b01011010, with the Booth y[-1] = 0 on the right.
                # Windows step from the LSB by two bits. The digit is the triplet, not a canned string.
                bits = ["0", "1", "0", "1", "1", "0", "1", "0", "0"]
                bit_row = th.bit_row(bits, cell_w=0.48, cell_h=0.62, font_size=16)
                bit_caption = Text("y7 … y0 | y-1     multiplier 0b01011010", font=th.MONO, font_size=12, color=th.MUTED)

                # 3 cells + 2 gaps of 0.08
                window = RoundedRectangle(
                    corner_radius=0.08, width=1.60, height=0.78,
                    stroke_color=th.CYAN, stroke_width=2.5,
                    fill_color=th.CYAN_DARK, fill_opacity=0.3,
                )

                # (y1,y0,y-1)=100 → -2; (y3,y2,y1)=111 → 0; (y5,y4,y3)=011 → +2; (y7,y6,y5)=010 → +1
                booth_digits = ["-2 × M", "0 × M", "+2 × M", "+1 × M"]
                rule_probe = PinProbe("BOOTH DIGIT", booth_digits[0], color=th.CYAN)

                row4 = VGroup(*[Dot(radius=0.07, color=th.AMBER) for _ in range(8)]).arrange(RIGHT, buff=0.12)
                row3 = VGroup(*[Dot(radius=0.07, color=th.AMBER) for _ in range(8)]).arrange(RIGHT, buff=0.12)
                row2 = VGroup(*[Dot(radius=0.07, color=th.GREEN_LIGHT) for _ in range(8)]).arrange(RIGHT, buff=0.12)
                row1 = VGroup(*[Dot(radius=0.07, color=th.GREEN_LIGHT) for _ in range(8)]).arrange(RIGHT, buff=0.12)
                four_rows = VGroup(row4, row3, row2, row1).arrange(DOWN, buff=0.08)
                two_rows = VGroup(row2.copy(), row1.copy()).arrange(DOWN, buff=0.1)
                four_lbl = Text("4 Booth rows", font=th.MONO, font_size=12, color=th.AMBER)
                two_lbl = Text("2 vectors", font=th.MONO, font_size=12, color=th.GREEN_LIGHT)
                wallace = VGroup(
                    VGroup(four_lbl, four_rows).arrange(DOWN, buff=0.08),
                    Text("→", font=th.MONO, font_size=28, color=th.WHITE),
                    VGroup(two_lbl, two_rows).arrange(DOWN, buff=0.08),
                ).arrange(RIGHT, buff=0.35)

                booth_layout = VGroup(concept_badge, bit_caption, bit_row, rule_probe, wallace).arrange(DOWN, buff=0.22)
                booth_layout.move_to(self.layout.main_stage_center())
                # Window covers the LSB triplet (cells 6, 7, 8) after the row has been placed.
                window.move_to(VGroup(bit_row[6], bit_row[7], bit_row[8]).get_center())
                booth_layout.add(window)
                st.add(booth_layout)

                self.play(FadeIn(concept_badge), FadeIn(bit_caption), Create(bit_row), Create(window), FadeIn(rule_probe), FadeIn(wallace), run_time=0.9)

                pitch = 0.48 + 0.08
                for step, digit in enumerate(booth_digits[1:], start=1):
                    self.play(
                        window.animate.shift(LEFT * (2 * pitch)),
                        rule_probe.set_value(digit),
                        run_time=0.45,
                    )
                self.wait(max(0.3, trk.duration - 2.6))
                st.takeaway("Each digit is the triplet under the window. Four rows then become two.", wait=1.2)

        # =====================================================================
        # ACT 4: DYNAMIC POWER & TENSOR CORE SCALING
        # =====================================================================
        act4_narration = (
            "Area matters because dynamic power grows with capacitance. "
            "The 4,096 number is not the gate-count ratio. One mma.sync instruction shaped m16 n8 k32 "
            "performs 16 times 8 times 32, which is 4,096 multiply-accumulates. That is an instruction shape."
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
                t1_val = Text("m16n8k32", font=th.SANS, weight=BOLD, font_size=28, color=th.CYAN_LIGHT)
                t1_lbl = Text("16 × 8 × 32 = 4,096", font=th.MONO, font_size=12, color=th.TEXT)
                t1_sub = Text("instruction shape, not die area", font=th.MONO, font_size=10, color=th.CYAN)
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
                t3_sub = Text("FP32 ~7,000, not drawn to scale", font=th.MONO, font_size=10, color=th.PURPLE)
                c3 = VStack(t3_val, t3_lbl, t3_sub, gap=0.1).move_to(tile3)
                grp3 = VGroup(tile3, c3)

                tiles = HStack(grp1, grp2, grp3, gap=th.SPACE_MD).move_to(DOWN * 0.8)
                st.add(tiles)

                self.play(FadeIn(tiles, shift=UP * 0.2), run_time=0.9)
                self.wait(max(0.3, trk.duration - 1.7))
                st.takeaway("4,096 MACs is 16×8×32. It is not the 7,000-over-456 gate ratio.", wait=1.2)
