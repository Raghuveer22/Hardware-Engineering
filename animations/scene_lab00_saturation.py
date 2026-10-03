"""
Lab 00: The Number Crisis — Signed Integer Overflow & Saturation Clamping
Foundations of Fixed-Point Digital Arithmetic & Numerical Stability in AI Silicon.

Tailored for Software Engineers (3Blue1Brown Visual Standard):
- Act 0: The Two's Complement Place-Value Tower
- Act 1: The Catastrophic Sign Flip (+100 + +50 = -106 destroys LLM Attention)
- Act 2: The Physical Ripple-Carry Adder & Overflow Proof (V = C_in[7] ^ C_out[7])
- Act 3: The Modular Speedometer Wheel & Saturation Barrier
- Act 4: The 3:1 Saturation MUX Datapath (Synthesizable RTL Implementation)
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
    edge_at,
)


class Lab00SaturationIntro(KineticSiliconScene):
    def construct(self):
        config = HardwareConfig(data_width=8)
        clock = KineticClock(initial_cycle=0)

        # Ambient Clock HUD at top right (compact)
        ticker = clock.create_ticker_badge(prefix="CLK: T = ", color=th.AMBER_LIGHT)
        ticker.to_corner(UR, buff=th.SPACE_SM)
        self.hud = ticker
        self.add(ticker)

        # =====================================================================
        # ACT 0: PRELORE — TWO'S COMPLEMENT PLACE VALUE TOWER
        # =====================================================================
        prelore_narration = (
            "Before we break anything, let's recall how negative numbers live in hardware. "
            "In two's complement, the leftmost bit is the sign: zero means positive, one means negative. "
            "An 8-bit signed register holds positive 127 down to negative 128."
        )
        with self.stage("PRIMER", "How Negatives Live in Silicon", "Two's Complement in 20 Seconds", narration=prelore_narration) as st:
            with self.voiceover(prelore_narration) as trk:
                # 3b1b mathematical definition of two's complement place values
                formula = MathTex(
                    r"X =",
                    r"-b_7 \cdot 2^7",
                    r"+",
                    r"\sum_{i=0}^{6} b_i \cdot 2^i",
                    font_size=36,
                )
                formula_band, bit_band = st.content.split_y(0.32, 0.68, gap=th.SPACE_SM)
                st.place(formula, formula_band)
                formula[1].set_color(th.RED_LIGHT)
                formula[3].set_color(th.GREEN_LIGHT)
                st.add(formula)
                self.play(Write(formula), run_time=0.8)

                # Visual bit-weight boxes from bit 7 down to bit 0
                weights = ["-128", "+64", "+32", "+16", "+8", "+4", "+2", "+1"]
                indices = ["[7]", "[6]", "[5]", "[4]", "[3]", "[2]", "[1]", "[0]"]
                bit_cells = VGroup()
                for i, (w, idx) in enumerate(zip(weights, indices)):
                    is_msb = (i == 0)
                    col = th.RED if is_msb else th.GREEN
                    box = RoundedRectangle(corner_radius=0.08, width=1.1, height=1.3, stroke_color=col, stroke_width=2.0 if is_msb else 1.2, fill_color="#0e1526", fill_opacity=0.9)
                    w_txt = Text(w, font=th.MONO, weight=BOLD, font_size=15, color=col)
                    i_txt = Text(idx, font=th.MONO, font_size=11, color=th.FAINT)
                    cell_sub = VStack(w_txt, i_txt, gap=0.08).move_to(box)
                    bit_cells.add(VGroup(box, cell_sub))
                bit_cells.arrange(RIGHT, buff=th.SPACE_XS)
                st.place(bit_cells, bit_band)
                st.add(bit_cells)

                self.play(FadeIn(bit_cells, shift=UP * 0.2), run_time=0.8)

                # Flash the MSB weight to emphasize negative polarity
                self.play(
                    bit_cells[0][0].animate.set_stroke(color=th.WHITE, width=4.0),
                    bit_cells[0][1][0].animate.set_color(th.WHITE),
                    run_time=0.6
                )
                self.play(
                    bit_cells[0][0].animate.set_stroke(color=th.RED, width=2.0),
                    bit_cells[0][1][0].animate.set_color(th.RED_LIGHT),
                    run_time=0.6
                )
                self.wait(max(0.3, trk.duration - 2.8))
                st.takeaway("The leftmost bit is the sign. Keep that in mind.", wait=1.2)

        # =====================================================================
        # ACT 1: THE SILICON BIT OVERFLOW BUG
        # =====================================================================
        act1_narration = (
            "Run this in Python: numpy int8 of 100 plus numpy int8 of 50. "
            "The mathematical sum is 150, but 8 bits only reach 127, so the stored result is negative 106. "
            "A later exponential of a large negative underflows toward zero. We do not pretend e to the 150 fits in float32."
        )
        with self.stage("ACT 1", "Signed INT8 Overflow", "Why Adding Positive Numbers Yields Negative Results", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                # Vertical schoolbook addition of binary bits
                a_bits = "0 1 1 0 0 1 0 0"  # +100
                b_bits = "0 0 1 1 0 0 1 0"  # +50
                s_bits = "1 0 0 1 0 1 1 0"  # -106

                add_title = Text("COLUMN-BY-COLUMN SILICON ADDITION", font=th.MONO, weight=BOLD, font_size=15, color=th.AMBER)
                row_a = Text(f"  {a_bits}    (+100)", font=th.MONO, font_size=20, color=th.GREEN_LIGHT)
                row_b = Text(f"+ {b_bits}    ( +50)", font=th.MONO, font_size=20, color=th.GREEN_LIGHT)
                row_s = Text(f"= {s_bits}    (-106!)", font=th.MONO, weight=BOLD, font_size=20, color=th.RED_LIGHT)
                span = max(row_a.width, row_b.width, row_s.width)
                div_line = Line(ORIGIN, RIGHT * span, color=th.BORDER, stroke_width=2.0)

                py_line = Text("np.int8(100) + np.int8(50)", font=th.MONO, font_size=18, color=th.AMBER_LIGHT)
                add_block = VGroup(py_line, add_title, row_a, row_b, div_line, row_s).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
                sum_slot, note_slot = st.content.split_x(1.35, 0.85, gap=th.SPACE_LG)
                st.place(add_block, sum_slot)

                st.add(add_block)
                self.play(FadeIn(add_block[:5]), run_time=0.7)
                self.play(Write(row_s), run_time=0.6)

                # Reveal the consequence only after the bits have flipped.
                note = Text(
                    "Stored value is -106.\nA later exp of a large\nnegative underflows.\nfloat32 cannot hold e^150.",
                    font=th.MONO, font_size=14, color=th.RED_LIGHT, line_spacing=1.15,
                )
                note_box = RoundedRectangle(
                    corner_radius=0.1, width=4.2, height=2.4,
                    stroke_color=th.RED, stroke_width=1.6, fill_color="#200a0a", fill_opacity=0.92,
                )
                note.move_to(note_box)
                note_group = VGroup(note_box, note)
                st.place(note_group, note_slot)
                st.add(note_group)
                self.play(FadeIn(note_group, shift=RIGHT * 0.15), run_time=0.5)

                self.wait(max(0.3, trk.duration - 2.8))
                st.takeaway("100 + 50 wrapped to -106. The sign bit flipped.", wait=1.2)

        # =====================================================================
        # ACT 2: THE PHYSICAL RIPPLE-CARRY ADDER & OVERFLOW PROOF
        # =====================================================================
        act2_narration = (
            "Let's open the adder and watch the bug happen. Addition ripples a carry bit through eight full adders. "
            "Overflow occurs exactly when the carry entering the sign bit differs from the carry leaving it. "
            "Here, one enters bit seven but zero leaves—so the overflow flag is set."
        )
        with self.stage("ACT 2", "Ripple Carry & Overflow Theorem", "Gate-Level Identity: V = C_in[7] XOR C_out[7]", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                # 8-bit Ripple Carry Adder chain
                chain_band, eq_band = st.content.split_y(1.05, 0.95, gap=th.SPACE_SM)
                rca = RippleCarryChain(bits=8, width=10.5, height=1.2)
                bit_labels, carries = rca.operand_labels(100, 50)
                chain = VGroup(rca, bit_labels)
                st.place(chain, chain_band)
                st.add(chain)
                self.play(Create(rca), FadeIn(bit_labels), run_time=0.8)

                # Carry is 1 only into bit 7. That is the overflow, not a generic sweep.
                self.play(rca.cells[7][0].animate.set_stroke(color=th.WHITE, width=3.5), run_time=0.4)
                assert carries[7] == 1 and carries[8] == 0

                # Bit 7 carry callout
                c_in_badge = PinProbe("C_in[7]", "1", color=th.AMBER)
                c_in_badge.next_to(rca.cells[7], UP, buff=0.15)
                c_out_badge = PinProbe("C_out[7]", "0", color=th.CYAN)
                c_out_badge.next_to(rca.cells[7], LEFT, buff=0.15)
                carry_badges = VGroup(c_in_badge, c_out_badge)
                st.add(carry_badges)

                self.play(FadeIn(carry_badges), run_time=0.4)

                # Mathematical theorem equation with colored XOR terms
                overflow_eq = MathTex(
                    r"V", r"=", r"C_{\text{in}}[7]", r"\oplus", r"C_{\text{out}}[7]",
                    r"=", r"1", r"\oplus", r"0", r"=", r"1", r"\implies", r"\text{OVERFLOW ASSERTED}",
                    font_size=32
                )
                st.place(overflow_eq, eq_band)
                overflow_eq[0].set_color(th.RED)
                overflow_eq[2].set_color(th.AMBER)
                overflow_eq[4].set_color(th.CYAN)
                overflow_eq[6].set_color(th.AMBER)
                overflow_eq[8].set_color(th.CYAN)
                overflow_eq[10].set_color(th.RED)
                overflow_eq[12].set_color(th.RED_LIGHT)

                st.add(overflow_eq)
                self.play(Write(overflow_eq), run_time=0.9)
                self.wait(max(0.3, trk.duration - 3.7))
                st.takeaway("Overflow = the two carry bits disagree.", wait=1.2)

        # =====================================================================
        # ACT 3: THE TWO'S COMPLEMENT SPEEDOMETER WHEEL
        # =====================================================================
        act3_narration = (
            "Picture two's complement as a circular dial, like a speedometer. "
            "Push past positive 127 and the needle wraps around to negative 128. "
            "A hardware saturation barrier adds a physical stop, locking the needle at 127 instead."
        )
        with self.stage("ACT 3", "The Circle of Discontinuity", "Why Wrap-Around Destroys Deep Learning", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                wheel = TwosComplementWheel(radius=1.8)
                st.place(wheel)
                st.add(wheel)
                self.play(Create(wheel), run_time=0.9)

                # Animate dial sweep wrapping across overflow boundary
                wheel.animate_sweep(self, target_val=150, run_time=1.0, clamp=False)

                # Deploy saturation clamp barrier and sweep again to clamp at +127
                wheel.deploy_clamp_barrier(self)
                wheel.animate_sweep(self, target_val=150, run_time=0.8, clamp=True)
                self.wait(max(0.3, trk.duration - 2.7))
                st.takeaway("Wrap-around is a bug. Saturation turns it into a guardrail.", wait=1.2)

        # =====================================================================
        # ACT 4: THE 3:1 SATURATION CLAMPING DATAPATH
        # =====================================================================
        act4_narration = (
            "Here is the actual circuit that enforces the guardrail: a three-to-one multiplexer. "
            "When overflow fires, the selector overrides the raw sum and clamps instantly—"
            "positive 127 on upward overflow, negative 128 on downward overflow."
        )
        with self.stage("ACT 4", "The 3:1 Saturation MUX", "Hardware Clamping Datapath in Synthesizable RTL", narration=act4_narration) as st:
            with self.voiceover(act4_narration) as trk:
                # 3:1 Multiplexer visual datapath
                in_raw = RoundedRectangle(corner_radius=0.08, width=2.6, height=0.55, stroke_color=th.MUTED, fill_color=th.CARD, fill_opacity=0.9)
                t_raw = Text("raw_sum (-106)", font=th.MONO, font_size=11, color=th.MUTED).move_to(in_raw)
                grp_raw = VGroup(in_raw, t_raw)

                in_pos = RoundedRectangle(corner_radius=0.08, width=2.6, height=0.55, stroke_color=th.GREEN, fill_color="#071b11", fill_opacity=0.9)
                t_pos = Text("MAX_POS (+127)", font=th.MONO, font_size=11, color=th.GREEN_LIGHT).move_to(in_pos)
                grp_pos = VGroup(in_pos, t_pos)

                in_neg = RoundedRectangle(corner_radius=0.08, width=2.6, height=0.55, stroke_color=th.CYAN, fill_color="#09182a", fill_opacity=0.9)
                t_neg = Text("MAX_NEG (-128)", font=th.MONO, font_size=11, color=th.CYAN_LIGHT).move_to(in_neg)
                grp_neg = VGroup(in_neg, t_neg)

                inputs_stack = VStack(grp_raw, grp_pos, grp_neg, gap=th.SPACE_SM)

                # Center: 3:1 MUX trapezoid
                mux_box = RoundedRectangle(corner_radius=0.1, width=2.6, height=3.0, stroke_color=th.AMBER, stroke_width=2.0, fill_color="#181106", fill_opacity=0.95)
                mux_title = Text("3:1 MUX", font=th.MONO, weight=BOLD, font_size=15, color=th.AMBER)
                mux_sel = Text(
                    "if overflow:\n  a[7]==0 ? +127\n        : -128",
                    font=th.MONO, font_size=11, color=th.AMBER_LIGHT, line_spacing=1.05,
                )
                mux_group = VGroup(mux_box, VStack(mux_title, mux_sel, gap=th.SPACE_SM).move_to(mux_box))

                # Output on right: Clamped Sum
                out_box = RoundedRectangle(corner_radius=0.1, width=2.8, height=1.1, stroke_color=th.GREEN, stroke_width=2.0, fill_color="#072213", fill_opacity=0.95)
                out_title = Text("CLAMPED SUM [7:0]", font=th.MONO, font_size=11, color=th.GREEN)
                out_val = Text("+127 (0x7F)", font=th.MONO, weight=BOLD, font_size=15, color=th.WHITE)
                out_group = VGroup(out_box, VStack(out_title, out_val, gap=th.SPACE_XS).move_to(out_box))

                mux_layout = HStack(inputs_stack, mux_group, out_group, gap=th.SPACE_LG)

                # Ports are fractions of the mux edge, so a taller mux keeps the same taps.
                w_raw = Arrow(in_raw.get_right(), edge_at(mux_box, LEFT, 0.82), buff=th.SPACE_XS, color=th.MUTED, stroke_width=1.5)
                w_pos = Arrow(in_pos.get_right(), edge_at(mux_box, LEFT, 0.50), buff=th.SPACE_XS, color=th.GREEN, stroke_width=2.0)
                w_neg = Arrow(in_neg.get_right(), edge_at(mux_box, LEFT, 0.18), buff=th.SPACE_XS, color=th.CYAN, stroke_width=1.5)
                w_out = Arrow(edge_at(mux_box, RIGHT, 0.50), out_box.get_left(), buff=th.SPACE_XS, color=th.GREEN_LIGHT, stroke_width=2.5)

                datapath_complete = VGroup(mux_layout, w_raw, w_pos, w_neg, w_out)
                st.add(datapath_complete)

                wrong = Text(
                    "sum[7] is 1, and would pick -128",
                    font=th.MONO, font_size=13, color=th.RED_LIGHT,
                )
                right = Text(
                    "rtl uses a[7], which is 0, so the clamp is +127",
                    font=th.MONO, font_size=13, color=th.GREEN_LIGHT,
                )
                choice = VGroup(wrong, right).arrange(DOWN, aligned_edge=LEFT, buff=th.SPACE_XS)
                body, foot = st.content.split_y(1, 0.28, gap=th.SPACE_XS)
                st.place(datapath_complete, body)
                st.place(choice, foot)

                self.play(FadeIn(inputs_stack), FadeIn(mux_group), Create(w_raw), Create(w_pos), Create(w_neg), run_time=0.8)
                st.add(choice)
                self.play(FadeIn(wrong), run_time=0.35)
                self.play(
                    FadeIn(right),
                    grp_pos[0].animate.set_stroke(color=th.GREEN_LIGHT, width=3.0),
                    w_pos.animate.set_color(th.GREEN_LIGHT).set_stroke(width=3.5),
                    Create(w_out),
                    FadeIn(out_group, shift=RIGHT * 0.2),
                    run_time=0.8,
                )
                self.wait(max(0.3, trk.duration - 2.4))
                st.takeaway("Clamp with the operand sign. The sum's sign is already wrong.", wait=1.2)
