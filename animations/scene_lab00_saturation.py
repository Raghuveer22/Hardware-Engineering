"""
Lab 00: The Number Crisis — Signed Integer Overflow & Saturation Clamping
Foundations of Fixed-Point Digital Arithmetic & Numerical Stability in AI Silicon.

Tailored for Software Engineers:
- Act 1: The Catastrophic Sign Flip (+100 + +50 = -106 destroys LLM Attention)
- Act 2: The Physical Ripple-Carry Adder & Overflow Proof (V = C_in[7] ^ C_out[7])
- Act 3: The Two's Complement Speedometer Wheel & Saturation Barrier
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
    fit_to_bounds,
)


class Lab00SaturationIntro(KineticSiliconScene):
    def construct(self):
        config = HardwareConfig(data_width=8)
        clock = KineticClock(initial_cycle=0)

        # Ambient Clock HUD at top right (compact to avoid title collisions)
        ticker = clock.create_ticker_badge(prefix="CLK: T = ", color=th.AMBER_LIGHT)
        ticker.to_corner(UR, buff=0.25)
        self.add(ticker)

        # =====================================================================
        # ACT 0: PRELORE — HOW NEGATIVE NUMBERS LIVE IN SILICON
        # =====================================================================
        prelore_narration = (
            "Before we break anything, let's recall how negative numbers live in hardware. "
            "In two's complement, the leftmost bit is the sign: zero means positive, one means negative. "
            "An 8-bit signed register holds positive 127 down to negative 128."
        )
        with self.stage("PRIMER", "How Negatives Live in Silicon", "Two's Complement in 20 Seconds", narration=prelore_narration) as st:
            with self.voiceover(prelore_narration) as trk:
                pre_cards = HStack(
                    th.metric_card("0b0…", "Sign bit = 0", "Means POSITIVE", color=th.GREEN, width=3.6, height=2.3),
                    th.metric_card("0b1…", "Sign bit = 1", "Means NEGATIVE", color=th.RED, width=3.6, height=2.3),
                    th.metric_card("-128 … +127", "8-bit signed range", "127 max, -128 min", color=th.AMBER, width=3.6, height=2.3),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(pre_cards)
                self.play(FadeIn(pre_cards, shift=UP * 0.2), run_time=1.0)
                self.wait(max(0.3, trk.duration - 1.0))
                st.takeaway("The leftmost bit is the sign. Keep that in mind.", wait=1.2)

        # =====================================================================
        # ACT 1: THE SILICON BIT OVERFLOW BUG
        # =====================================================================
        act1_narration = (
            "Now watch what happens when two positive numbers get too big. "
            "Plus 100 plus plus 50 should equal 150, but 8 bits only reach 127, so the carry flips the sign bit. "
            "The sum becomes negative 106. In an LLM attention head, that softmax value collapses to zero, wrecking the model."
        )
        with self.stage("ACT 1", "Signed INT8 Overflow", "Why Adding Positive Numbers Yields Negative Results", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                # Two 8-bit registers: +100 (0x64) and +50 (0x32)
                reg_a = th.BitRegister(width_bits=8, initial_val="01100100", highlight_msb=True, msb_color=th.GREEN)
                lbl_a = SemanticText("Operand A: +100 (0b0110_0100)", role=TextRole.PROBE_LABEL, color=th.GREEN_LIGHT)
                group_a = VStack(lbl_a, reg_a, gap=th.SPACE_XS)

                reg_b = th.BitRegister(width_bits=8, initial_val="00110010", highlight_msb=True, msb_color=th.GREEN)
                lbl_b = SemanticText("Operand B:  +50 (0b0011_0010)", role=TextRole.PROBE_LABEL, color=th.GREEN_LIGHT)
                group_b = VStack(lbl_b, reg_b, gap=th.SPACE_XS)

                reg_sum = th.BitRegister(width_bits=8, initial_val="10010110", highlight_msb=True, msb_color=th.RED)
                lbl_sum = SemanticText("Hardware Sum: -106 (0b1001_0110) ➔ CORRUPTED WRAP-AROUND!", role=TextRole.PROBE_LABEL, color=th.RED_LIGHT)
                group_sum = VStack(lbl_sum, reg_sum, gap=th.SPACE_XS)

                # LLM impact banner
                impact_card = RoundedRectangle(corner_radius=0.08, width=7.2, height=0.65, stroke_color=th.RED, fill_color="#2b0a0a", fill_opacity=0.9)
                impact_txt = SemanticText("LLM Impact: e^(-106) = 0.000 ➔ Attention Head Collapses!", role=TextRole.PROBE_LABEL, color=th.RED_LIGHT)
                impact_txt.move_to(impact_card)
                impact_grp = VGroup(impact_card, impact_txt)

                datapath_layout = VStack(group_a, group_b, group_sum, impact_grp, gap=th.SPACE_SM).move_to(self.layout.main_stage_center())
                st.add(datapath_layout)

                self.play(FadeIn(group_a), FadeIn(group_b), run_time=0.8)
                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.play(FadeIn(group_sum, shift=DOWN * 0.2), run_time=0.6)
                self.screen_shake(intensity=0.04, cycles=2, run_time=0.2)
                self.play(FadeIn(impact_grp, shift=UP * 0.1), run_time=0.4)
                self.wait(max(0.3, trk.duration - 2.4))
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
                rca = RippleCarryChain(bits=8, width=10.5, height=1.4).move_to(self.layout.main_stage_center() + UP * 0.8)
                st.add(rca)
                self.play(Create(rca), run_time=1.0)

                # Animate the carry token rippling across all 8 bit slices
                clock.advance(self, delta_cycles=1, run_time=0.3)
                rca.animate_ripple(self, run_time=1.4)

                # Bit 7 carry callout
                c_in_badge = PinProbe("C_in[7]", "1", color=th.AMBER)
                c_in_badge.next_to(rca.cells[7], UP, buff=0.15)
                c_out_badge = PinProbe("C_out[7]", "0", color=th.CYAN)
                c_out_badge.next_to(rca.cells[7], LEFT, buff=0.15)
                carry_badges = VGroup(c_in_badge, c_out_badge)
                st.add(carry_badges)

                self.play(FadeIn(carry_badges), run_time=0.4)

                # Mathematical proof card below
                overflow_eq = SemanticMath(
                    r"V = C_{\text{in}}[7] \oplus C_{\text{out}}[7] = 1 \oplus 0 = 1 \implies \text{OVERFLOW ASSERTED}",
                    role=TextRole.MATH_DISPLAY,
                    color=th.RED_LIGHT
                ).move_to(self.layout.main_stage_center() + DOWN * 1.5)
                fit_to_bounds(overflow_eq, max_width=10.5)
                st.add(overflow_eq)

                self.play(Write(overflow_eq), run_time=0.8)
                self.wait(max(0.3, trk.duration - 3.9))
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
                self.wait(max(0.3, trk.duration - 2.8))
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
                # Inputs on left: raw_sum, MAX_POS, MAX_NEG
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
                mux_title = SemanticText("3:1 MUX", role=TextRole.BLOCK_HEADER, color=th.AMBER)
                mux_sel = Text("sel = {overflow,\n       sign_bit}", font=th.MONO, font_size=10, color=th.AMBER_LIGHT, line_spacing=1.2)
                mux_group = VGroup(mux_box, VStack(mux_title, mux_sel, gap=th.SPACE_SM).move_to(mux_box))

                # Output on right: Clamped Sum
                out_box = RoundedRectangle(corner_radius=0.1, width=2.8, height=1.1, stroke_color=th.GREEN, stroke_width=2.0, fill_color="#072213", fill_opacity=0.95)
                out_title = SemanticText("CLAMPED SUM [7:0]", role=TextRole.PROBE_LABEL, color=th.GREEN)
                out_val = Text("+127 (0x7F)", font=th.MONO, weight=BOLD, font_size=15, color=th.WHITE)
                out_group = VGroup(out_box, VStack(out_title, out_val, gap=th.SPACE_XS).move_to(out_box))

                mux_layout = HStack(inputs_stack, mux_group, out_group, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())

                # Routing wires
                w_raw = Arrow(in_raw.get_right(), mux_box.get_left() + UP * 0.8, buff=0.08, color=th.MUTED, stroke_width=1.5)
                w_pos = Arrow(in_pos.get_right(), mux_box.get_left(), buff=0.08, color=th.GREEN, stroke_width=2.0)
                w_neg = Arrow(in_neg.get_right(), mux_box.get_left() + DOWN * 0.8, buff=0.08, color=th.CYAN, stroke_width=1.5)
                w_out = Arrow(mux_box.get_right(), out_box.get_left(), buff=0.08, color=th.GREEN_LIGHT, stroke_width=2.5)

                datapath_complete = VGroup(mux_layout, w_raw, w_pos, w_neg, w_out)
                st.add(datapath_complete)

                self.play(FadeIn(inputs_stack), FadeIn(mux_group), Create(w_raw), Create(w_pos), Create(w_neg), run_time=1.0)
                clock.advance(self, delta_cycles=1, run_time=0.3)

                # Active clamping route: highlight MAX_POS through MUX to output
                self.play(
                    grp_pos[0].animate.set_stroke(color=th.GREEN_LIGHT, width=3.0),
                    w_pos.animate.set_color(th.GREEN_LIGHT).set_stroke(width=3.5),
                    Create(w_out),
                    FadeIn(out_group, shift=RIGHT * 0.2),
                    run_time=0.8
                )
                self.wait(max(0.3, trk.duration - 2.1))
                st.takeaway("One multiplexer turns a wrap-around bug into a safe result.", wait=1.2)
