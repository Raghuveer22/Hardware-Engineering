"""
Lab 02: Accumulator Headroom — The MAC Unit & Sign Extension
Accumulator Headroom Induction Proofs, Sign Extension & Pipelined Timing Dynamics.

Tailored for Software Engineers (3Blue1Brown Visual Standard):
- Act 0: The Multiply-Accumulate Heartbeat of Deep Learning
- Act 1: The Bursting 16-Bit Accumulator (Overloading on Term 2)
- Act 2: The 32-Bit Headroom Induction Proof (K <= 131,071 Zero-Overflow Guarantee)
- Act 3: Sign Extension vs Zero Extension Disaster (-5 becomes +65,531)
- Act 4: Combinational vs Pipelined MAC Critical Path (Frequency Scaling)
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
        with self.stage("PRIMER", "The Multiply-Accumulate Heartbeat", "Multiply, Then Add to Running Total", narration=prelore_narration) as st:
            with self.voiceover(prelore_narration) as trk:
                # 3b1b mathematical vector dot product representation
                dot_eq = MathTex(
                    r"\mathbf{y} = \sum_{k=0}^{K-1} w_k \cdot x_k = w_0 x_0 + w_1 x_1 + \dots + w_{K-1} x_{K-1}",
                    font_size=34,
                    color=th.GREEN_LIGHT
                ).to_edge(UP, buff=1.3)
                dot_eq[0][4:11].set_color(th.CYAN_LIGHT)
                st.add(dot_eq)
                self.play(Write(dot_eq), run_time=0.9)

                # Visual MAC pipeline units
                # Input multipliers w_k and x_k
                in_w = RoundedRectangle(corner_radius=0.08, width=1.4, height=0.7, stroke_color=th.AMBER, stroke_width=2.0, fill_color="#181106", fill_opacity=0.9)
                t_w = Text("w[k]", font=th.MONO, font_size=13, color=th.AMBER_LIGHT).move_to(in_w)
                grp_w = VGroup(in_w, t_w)

                in_x = RoundedRectangle(corner_radius=0.08, width=1.4, height=0.7, stroke_color=th.CYAN, stroke_width=2.0, fill_color="#09182a", fill_opacity=0.9)
                t_x = Text("x[k]", font=th.MONO, font_size=13, color=th.CYAN_LIGHT).move_to(in_x)
                grp_x = VGroup(in_x, t_x)

                in_stack = VStack(grp_w, grp_x, gap=0.3)

                # Multiplier block
                mult_cell = Circle(radius=0.6, color=th.AMBER, stroke_width=2.5, fill_color="#1a1205", fill_opacity=0.9)
                mult_sym = MathTex(r"\times", color=th.AMBER_LIGHT, font_size=32).move_to(mult_cell)
                mult_unit = VGroup(mult_cell, mult_sym)

                # Adder block
                add_cell = Circle(radius=0.6, color=th.GREEN, stroke_width=2.5, fill_color="#072213", fill_opacity=0.9)
                add_sym = MathTex(r"+", color=th.GREEN_LIGHT, font_size=32).move_to(add_cell)
                add_unit = VGroup(add_cell, add_sym)

                # Accumulator register
                acc_box = RoundedRectangle(corner_radius=0.1, width=2.4, height=1.3, stroke_color=th.CYAN, stroke_width=2.0, fill_color="#091f33", fill_opacity=0.95)
                acc_lbl = Text("ACCUMULATOR", font=th.MONO, font_size=10, color=th.CYAN)
                acc_val = Text("sum += p", font=th.MONO, weight=BOLD, font_size=14, color=th.WHITE)
                acc_unit = VGroup(acc_box, VStack(acc_lbl, acc_val, gap=0.08).move_to(acc_box))

                # Accumulator feedback loop wire
                wire_w_m = Arrow(in_w.get_right(), mult_cell.get_left() + UP * 0.2, buff=0.06, color=th.AMBER, stroke_width=2.0)
                wire_x_m = Arrow(in_x.get_right(), mult_cell.get_left() + DOWN * 0.2, buff=0.06, color=th.CYAN, stroke_width=2.0)
                wire_m_a = Arrow(mult_cell.get_right(), add_cell.get_left(), buff=0.06, color=th.AMBER_LIGHT, stroke_width=2.5)
                wire_a_r = Arrow(add_cell.get_right(), acc_box.get_left(), buff=0.06, color=th.GREEN_LIGHT, stroke_width=2.5)

                mac_chain = VGroup(
                    HStack(in_stack, mult_unit, add_unit, acc_unit, gap=0.8),
                    wire_w_m, wire_x_m, wire_m_a, wire_a_r
                ).move_to(DOWN * 0.5)

                st.add(mac_chain)
                self.play(FadeIn(mac_chain), run_time=1.0)

                # Animate token multiplying and accumulating
                dot_m = Dot(mult_cell.get_center(), radius=0.1, color=th.AMBER_LIGHT)
                dot_a = Dot(add_cell.get_center(), radius=0.1, color=th.GREEN_LIGHT)
                self.play(
                    mult_cell.animate.set_stroke(color=th.WHITE, width=4.0),
                    run_time=0.4
                )
                self.play(
                    mult_cell.animate.set_stroke(color=th.AMBER, width=2.5),
                    add_cell.animate.set_stroke(color=th.WHITE, width=4.0),
                    acc_val.animate.set_color(th.GREEN_LIGHT),
                    run_time=0.4
                )
                self.play(add_cell.animate.set_stroke(color=th.GREEN, width=2.5), run_time=0.3)
                self.wait(max(0.3, trk.duration - 3.0))
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
                tank_16 = th.LiquidTankWidget(capacity=32767, width=2.8, height=3.6, title="16-BIT REGISTER", fluid_color=th.RED)
                
                # Multiplier Input Block
                mult_block = RoundedRectangle(
                    corner_radius=0.12, width=4.8, height=3.6,
                    stroke_color=th.AMBER, stroke_width=2.0,
                    fill_color="#181106", fill_opacity=0.9
                )
                m_title = Text("INT8 MULTIPLY-ACCUMULATE", font=th.MONO, weight=BOLD, font_size=13, color=th.AMBER_LIGHT)
                m_eq = Text(
                    "(-128) × (-128) = +16,384\n\n"
                    "Term 1: Sum = +16,384 (50% Full)\n"
                    "Term 2: Sum = +32,768 (OVERFLOW!)",
                    font=th.MONO, font_size=11, color=th.WHITE, line_spacing=1.2
                )
                m_sub = VStack(m_title, m_eq, gap=th.SPACE_SM).move_to(mult_block)
                mult_group = VGroup(mult_block, m_sub)

                act1_layout = HStack(mult_group, tank_16, gap=th.SPACE_XL).move_to(self.layout.main_stage_center())
                st.add(act1_layout)

                self.play(FadeIn(mult_group, shift=RIGHT * 0.2), Create(tank_16), run_time=1.0)

                # Fill Cycle 1: 50%
                clock.advance(self, delta_cycles=1, run_time=0.35)
                self.play(tank_16.set_fluid_fraction(0.5, color=th.AMBER), run_time=0.5)

                # Fill Cycle 2: 115% OVERFLOW!
                clock.advance(self, delta_cycles=1, run_time=0.35)
                self.play(tank_16.set_fluid_fraction(1.15, color=th.RED), run_time=0.5)
                self.screen_shake(intensity=0.06, cycles=3, run_time=0.25)
                self.wait(max(0.3, trk.duration - 2.6))
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
                headroom_eq = MathTex(
                    r"K_{\max} = \frac{2^{31} - 1}{(-128 \times -128)} = \frac{2{,}147{,}483{,}647}{16{,}384} = 131{,}071 \text{ MACs}",
                    font_size=32,
                    color=th.CYAN_LIGHT
                ).to_edge(UP, buff=1.3)
                st.add(headroom_eq)
                self.play(Write(headroom_eq), run_time=0.9)

                # Headroom comparative tiles
                c_k = RoundedRectangle(corner_radius=0.1, width=3.4, height=2.4, stroke_color=th.GREEN, stroke_width=2.0, fill_color="#071b11", fill_opacity=0.92)
                t_k_val = Text("131,071", font=th.SANS, weight=BOLD, font_size=32, color=th.GREEN_LIGHT)
                t_k_lbl = Text("Max Safe Vector (K)", font=th.MONO, font_size=12, color=th.TEXT)
                t_k_sub = Text("Zero overflow guarantee", font=th.MONO, font_size=10, color=th.GREEN)
                c_k_grp = VGroup(c_k, VStack(t_k_val, t_k_lbl, t_k_sub, gap=0.1).move_to(c_k))

                c_g = RoundedRectangle(corner_radius=0.1, width=3.4, height=2.4, stroke_color=th.AMBER, stroke_width=2.0, fill_color="#181106", fill_opacity=0.92)
                t_g_val = Text("3 Guard Bits", font=th.SANS, weight=BOLD, font_size=30, color=th.AMBER_LIGHT)
                t_g_lbl = Text("Spare in LLaMA-3", font=th.MONO, font_size=12, color=th.TEXT)
                t_g_sub = Text("d_model = 8,192 < 131,071", font=th.MONO, font_size=10, color=th.AMBER)
                c_g_grp = VGroup(c_g, VStack(t_g_val, t_g_lbl, t_g_sub, gap=0.1).move_to(c_g))

                c_w = RoundedRectangle(corner_radius=0.1, width=3.4, height=2.4, stroke_color=th.CYAN, stroke_width=2.0, fill_color="#091b2e", fill_opacity=0.92)
                t_w_val = Text("32 Bits", font=th.SANS, weight=BOLD, font_size=34, color=th.CYAN_LIGHT)
                t_w_lbl = Text("Standard ACC_WIDTH", font=th.MONO, font_size=12, color=th.TEXT)
                t_w_sub = Text("16 product + 16 headroom", font=th.MONO, font_size=10, color=th.CYAN)
                c_w_grp = VGroup(c_w, VStack(t_w_val, t_w_lbl, t_w_sub, gap=0.1).move_to(c_w))

                stat_headroom = HStack(c_k_grp, c_g_grp, c_w_grp, gap=th.SPACE_MD).move_to(DOWN * 0.8)
                st.add(stat_headroom)

                self.play(FadeIn(stat_headroom, shift=UP * 0.2), run_time=0.9)
                clock.advance(self, delta_cycles=1, run_time=0.3)
                self.wait(max(0.3, trk.duration - 2.1))
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
                lbl_prod = Text("16-BIT MULTIPLIER PRODUCT: -5  (MSB = 1)", font=th.MONO, font_size=11, color=th.RED_LIGHT)
                val_prod = Text("1111 1111 1111 1011", font=th.MONO, weight=BOLD, font_size=15, color=th.RED_LIGHT)
                prod_content = VStack(lbl_prod, val_prod, gap=th.SPACE_XS).move_to(prod_box)
                grp_prod = VGroup(prod_box, prod_content)

                # Correct 32-bit Sign Extension: Upper 16 bits = 1111...
                good_box = RoundedRectangle(corner_radius=0.1, width=10.2, height=1.0, stroke_color=th.GREEN, stroke_width=1.5, fill_color="#071b11", fill_opacity=0.92)
                lbl_good = Text("CORRECT SIGN EXTENSION: Replicate MSB to [31:16] ➔ Result: -5", font=th.MONO, font_size=11, color=th.GREEN_LIGHT)
                val_good = Text("1111 1111 1111 1111 | 1111 1111 1111 1011", font=th.MONO, weight=BOLD, font_size=13, color=th.GREEN_LIGHT)
                good_content = VStack(lbl_good, val_good, gap=th.SPACE_XS).move_to(good_box)
                grp_good = VGroup(good_box, good_content)

                # Zero-Extension Disaster: Upper 16 bits = 0000...
                bad_box = RoundedRectangle(corner_radius=0.1, width=10.2, height=1.0, stroke_color=th.AMBER, stroke_width=1.5, fill_color="#1a1205", fill_opacity=0.92)
                lbl_bad = Text("ZERO EXTENSION DISASTER: Upper 16 Bits Padded with 0s ➔ Result: +65,531!", font=th.MONO, font_size=11, color=th.AMBER_LIGHT)
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
        # ACT 4: COMBINATIONAL VS PIPELINED F_MAX (CONCEPT)
        # =====================================================================
        act4_narration = (
            "Speed is the last lesson. Our teaching MAC is combinational, so its multiplier and adder chain into one "
            "4-nanosecond critical path, capping the clock around 250 megahertz. Real chips fix this by inserting a "
            "pipeline register between the two stages, cutting the path to 2.8 nanoseconds and pushing toward 350 megahertz."
        )
        with self.stage("ACT 4", "Combinational vs Pipelined MAC", "CONCEPT: Critical Path & Timing Closure", narration=act4_narration) as st:
            with self.voiceover(act4_narration) as trk:
                concept_badge = VGroup(
                    RoundedRectangle(corner_radius=0.08, width=3.4, height=0.5, stroke_color=th.AMBER, stroke_width=1.5, fill_color="#1a1205", fill_opacity=0.9),
                    Text("CONCEPT (not rtl/)", font=th.MONO, weight=BOLD, font_size=12, color=th.AMBER_LIGHT)
                )
                concept_badge[1].move_to(concept_badge[0])

                # Visual datapath showing Multiplier -> Pipeline Register (16 DFFs) -> Adder
                m_stage = RoundedRectangle(corner_radius=0.1, width=3.2, height=2.2, stroke_color=th.AMBER, stroke_width=1.5, fill_color="#181106", fill_opacity=0.92)
                m_lbl = VStack(Text("STAGE 1", font=th.MONO, font_size=11, color=th.AMBER), Text("8×8 Multiplier\nt_mult ≈ 2.8 ns", font=th.MONO, font_size=11, color=th.TEXT, line_spacing=1.3)).move_to(m_stage)
                grp_m = VGroup(m_stage, m_lbl)

                pipe_reg = RoundedRectangle(corner_radius=0.08, width=1.6, height=2.2, stroke_color=th.CYAN, stroke_width=2.0, fill_color="#091f33", fill_opacity=0.95)
                pipe_lbl = VStack(Text("DFF REG", font=th.MONO, font_size=11, color=th.CYAN_LIGHT), Text("16 DFFs\n(t_cq ≈ 0.2ns)", font=th.MONO, font_size=10, color=th.CYAN, line_spacing=1.3)).move_to(pipe_reg)
                grp_pipe = VGroup(pipe_reg, pipe_lbl)

                a_stage = RoundedRectangle(corner_radius=0.1, width=3.2, height=2.2, stroke_color=th.GREEN, stroke_width=1.5, fill_color="#071b11", fill_opacity=0.92)
                a_lbl = VStack(Text("STAGE 2", font=th.MONO, font_size=11, color=th.GREEN), Text("32-bit Adder\nt_add ≈ 1.2 ns", font=th.MONO, font_size=11, color=th.TEXT, line_spacing=1.3)).move_to(a_stage)
                grp_a = VGroup(a_stage, a_lbl)

                w_m_p = Arrow(m_stage.get_right(), pipe_reg.get_left(), buff=0.08, color=th.CYAN_LIGHT, stroke_width=2.0)
                w_p_a = Arrow(pipe_reg.get_right(), a_stage.get_left(), buff=0.08, color=th.GREEN_LIGHT, stroke_width=2.0)

                pipe_chain = VGroup(HStack(grp_m, grp_pipe, grp_a, gap=th.SPACE_LG), w_m_p, w_p_a)

                # Frequency comparison tiles
                tile_comb = RoundedRectangle(corner_radius=0.1, width=4.5, height=1.8, stroke_color=th.RED, stroke_width=2.0, fill_color="#200a0a", fill_opacity=0.92)
                comb_val = Text("~250 MHz", font=th.SANS, weight=BOLD, font_size=28, color=th.RED_LIGHT)
                comb_lbl = Text("Combinational (rtl/mac_unit.sv)", font=th.MONO, font_size=11, color=th.TEXT)
                comb_sub = Text("t_crit = 2.8 + 1.2 = 4.0 ns", font=th.MONO, font_size=10, color=th.RED)
                grp_comb = VGroup(tile_comb, VStack(comb_val, comb_lbl, comb_sub, gap=0.08).move_to(tile_comb))

                tile_pipe = RoundedRectangle(corner_radius=0.1, width=4.5, height=1.8, stroke_color=th.GREEN, stroke_width=2.0, fill_color="#071b11", fill_opacity=0.92)
                pipe_val = Text("~350 MHz", font=th.SANS, weight=BOLD, font_size=28, color=th.GREEN_LIGHT)
                pipe_lbl = Text("Pipelined MAC (Concept)", font=th.MONO, font_size=11, color=th.TEXT)
                pipe_sub = Text("t_crit = max(2.8, 1.2) = 2.8 ns", font=th.MONO, font_size=10, color=th.GREEN)
                grp_pipe_tile = VGroup(tile_pipe, VStack(pipe_val, pipe_lbl, pipe_sub, gap=0.08).move_to(tile_pipe))

                stat_pipe = HStack(grp_comb, grp_pipe_tile, gap=th.SPACE_LG)

                timing_layout = VStack(concept_badge, pipe_chain, stat_pipe, gap=th.SPACE_MD).move_to(self.layout.main_stage_center())
                st.add(timing_layout)

                self.play(FadeIn(concept_badge), FadeIn(pipe_chain, shift=DOWN * 0.2), run_time=0.9)
                clock.advance(self, delta_cycles=1, run_time=0.3)
                self.play(FadeIn(stat_pipe, shift=UP * 0.2), run_time=0.8)
                self.wait(max(0.3, trk.duration - 2.0))
                st.takeaway("One pipeline register nearly doubles the clock speed.", wait=1.2)
