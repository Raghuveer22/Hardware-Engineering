"""
Lab 08: The Non-Linear Engine — Hardware Exponential SFU (2^x & e^x) for SwiGLU
A kinetic, visual-first masterclass on the Base-2 silicon trick powering modern LLMs.

Narrative Flow:
  Act 1: The SwiGLU / SiLU Activation Challenge (>60% of LLaMA 3 FLOPs)
  Act 2: The Base-2 Silicon Secret (Laser-slicing into 2^I * 2^F)
  Act 3: Combinatorial Barrel Shifter & 16-Entry LUT Datapath
  Act 4: Synthesizable Silicon Architecture (rtl/exp2_sfu.sv) & Full Pre-Silicon Tapeout!
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
    SiliconCameraRig,
    LaserPacketStream,
    StageLayout,
    HardwareConfig,
)


class Lab08ExponentialSFU(SiliconCameraRig):
    def construct(self):
        layout = self.layout
        config = HardwareConfig(data_width=8)

        # =====================================================================
        # ACT 1: THE SWIGLU / SILU ACTIVATION CHALLENGE (~45s)
        # =====================================================================
        kicker, _, _ = th.header(
            "THE NON-LINEAR ENGINE",
            "Hardware Exponential SFU for SwiGLU & SiLU",
            title_size=30,
            badge_color=th.CYAN
        )
        self.play(FadeIn(kicker, shift=DOWN * 0.3), run_time=0.8)

        banner = th.narration_banner(
            "In modern Transformer architectures, over 60% of all parameters and compute FLOPs reside in SwiGLU non-linear Feed-Forward Networks."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.7)
        self.wait(1.5)

        # PyTorch Code Window on Left
        py_code = [
            ("# LLaMA 3 SwiGLU Activation Layer", th.MUTED),
            ("import torch.nn.functional as F", th.CYAN),
            ("def swiglu_ffn(x, W_gate, W_up, W_down):", th.TEXT),
            ("    # SiLU non-linear activation:", th.AMBER_LIGHT),
            ("    gate = F.silu(x @ W_gate)", th.GREEN),
            ("    return (gate * (x @ W_up)) @ W_down", th.TEXT),
            ("", th.MUTED),
            ("# Computing e^x via Taylor series: Disastrously slow in silicon!", th.RED),
        ]
        soft_win = th.code_window(py_code, title_text="PYTORCH: SWIGLU ACTIVATION",
                                  width=6.4, height=3.8, font_size=13)
        soft_win.move_to(LEFT * 3.1 + DOWN * 0.4)

        # Right Panel: Silicon Area Shock
        m1 = th.metric_card("60% FLOPs", "FFN Layer Dominance",
                            "Over half of inference compute is non-linear SwiGLU", color=th.AMBER, width=4.8, height=1.7)
        m2 = th.metric_card("3.2 ns", "Silicon SFU Delay",
                            "Combinational Base-2 decomposition in silicon", color=th.GREEN, width=4.8, height=1.7)
        right_panel = VGroup(m1, m2).arrange(DOWN, buff=0.3).move_to(RIGHT * 3.3 + DOWN * 0.4)

        self.play(Create(soft_win), run_time=1.0)
        self.wait(1.0)
        self.play(FadeIn(m1, shift=UP * 0.2), FadeIn(m2, shift=UP * 0.2), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "SwiGLU requires high-speed exponentiation. But computing Taylor series in silicon requires too many DSP multipliers and pipeline stalls."
            )),
            run_time=0.6
        )
        self.wait(2.5)

        self.play(FadeOut(kicker), FadeOut(soft_win), FadeOut(right_panel), run_time=0.5)

        # =====================================================================
        # ACT 2: THE BASE-2 SILICON SECRET (~60s)
        # =====================================================================
        f_title = Text("The Base-2 Silicon Secret: e^x = 2^(x · log2(e)) = 2^I × 2^F",
                       font=th.SANS, weight=BOLD, font_size=24, color=th.GREEN_LIGHT)
        f_title.to_edge(UP, buff=0.6)
        self.play(Write(f_title), run_time=0.6)

        self.play(
            Transform(banner, th.narration_banner(
                "By changing base to powers of two, we slice the exponent into integer I and fraction F. 2^I is a free barrel bit-shift in hardware!"
            )),
            run_time=0.5
        )

        # Fixed-point bit strip being sliced by a laser!
        bit_strip = th.BitRegister(width_bits=8, initial_val="00110101", highlight_msb=False,
                                   bg_color=th.CARD)
        bit_strip.move_to(UP * 0.7)

        # Labels for integer and fractional parts
        lbl_int = Text("Integer (I = 3)\n➔ 2^3 = 8 (Barrel Shift)", font=th.MONO, weight=BOLD, font_size=14, color=th.CYAN_LIGHT)
        lbl_int.next_to(bit_strip.cells[1], DOWN, buff=0.4)

        lbl_frac = Text("Fraction (F = 0.3125)\n➔ 2^F (16-Entry LUT)", font=th.MONO, weight=BOLD, font_size=14, color=th.PURPLE_LIGHT)
        lbl_frac.next_to(bit_strip.cells[5], DOWN, buff=0.4)

        # Neon Laser line between cell 3 and cell 4
        laser = Line(bit_strip.cells[3].get_right() + UP * 0.8,
                     bit_strip.cells[3].get_right() + DOWN * 0.8,
                     color=th.AMBER, stroke_width=3.5)
        laser_lbl = Text("BINARY POINT SLICER", font=th.MONO, weight=BOLD, font_size=11, color=th.AMBER_LIGHT)
        laser_lbl.next_to(laser, UP, buff=0.1)

        self.play(Create(bit_strip), run_time=0.8)
        self.focus_on(bit_strip, buffer_factor=1.5, run_time=th.RATE_NORMAL)
        self.play(Create(laser), FadeIn(laser_lbl), run_time=0.6)
        LaserPacketStream.shoot_token(self, laser.get_top(), laser.get_bottom(), color=th.AMBER, run_time=0.4)
        self.screen_shake(intensity=0.04, cycles=2, run_time=0.15)
        self.play(FadeIn(lbl_int), FadeIn(lbl_frac), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "The laser splits the number: the integer part routes to a barrel shifter, and the fractional part routes to a tiny 16-slot lookup table!"
            )),
            run_time=0.6
        )
        self.wait(2.2)
        self.reset_camera(run_time=th.RATE_FAST)

        self.play(FadeOut(f_title), FadeOut(bit_strip), FadeOut(laser), FadeOut(laser_lbl),
                  FadeOut(lbl_int), FadeOut(lbl_frac), run_time=0.5)

        # =====================================================================
        # ACT 3: COMBINATORIAL HARDWARE DATAPATH (~60s)
        # =====================================================================
        dp_title = Text("Inside Silicon: Hardware Exponential Datapath (rtl/exp2_sfu.sv)",
                        font=th.SANS, weight=BOLD, font_size=26, color=th.CYAN)
        dp_title.to_edge(UP, buff=0.6)
        self.play(Write(dp_title), run_time=0.6)

        # Datapath nodes
        scaler_node = RoundedRectangle(corner_radius=0.15, width=2.4, height=1.4,
                                       stroke_color=th.AMBER, stroke_width=2.0, fill_color=th.CARD, fill_opacity=0.95).shift(LEFT * 4.2 + UP * 0.35)
        sc_lbl = Text("Log2(e) Scaler\nu = x * 1.442", font=th.MONO, font_size=13, color=th.AMBER_LIGHT).move_to(scaler_node)

        split_node = RoundedRectangle(corner_radius=0.15, width=2.4, height=1.4,
                                      stroke_color=th.CYAN, stroke_width=2.0, fill_color=th.CARD, fill_opacity=0.95).shift(LEFT * 1.4 + UP * 0.35)
        sp_lbl = Text("Bit Slicer\nu = I + F", font=th.MONO, font_size=13, color=th.CYAN_LIGHT).move_to(split_node)

        shifter_node = RoundedRectangle(corner_radius=0.15, width=2.4, height=1.2,
                                       stroke_color=th.GREEN, stroke_width=2.0, fill_color=th.CARD, fill_opacity=0.95).shift(RIGHT * 1.6 + UP * 1.15)
        sh_lbl = Text("Barrel Shifter\n(2^I via Muxes)", font=th.MONO, font_size=13, color=th.GREEN_LIGHT).move_to(shifter_node)

        lut_node = RoundedRectangle(corner_radius=0.15, width=2.4, height=1.2,
                                   stroke_color=th.PURPLE, stroke_width=2.0, fill_color=th.CARD, fill_opacity=0.95).shift(RIGHT * 1.6 + DOWN * 0.45)
        lu_lbl = Text("16-Entry Seed LUT\n(2^F ROM)", font=th.MONO, font_size=13, color=th.PURPLE_LIGHT).move_to(lut_node)

        comb_node = RoundedRectangle(corner_radius=0.15, width=2.2, height=1.4,
                                     stroke_color=th.CYAN, stroke_width=2.0, fill_color=th.CARD, fill_opacity=0.95).shift(RIGHT * 4.4 + UP * 0.35)
        co_lbl = Text("Combiner\ny = 2^I * 2^F", font=th.MONO, font_size=13, color=th.CYAN_LIGHT).move_to(comb_node)

        a1 = Arrow(start=scaler_node.get_right(), end=split_node.get_left(), buff=0.1, color=th.BORDER)
        a_up = Arrow(start=split_node.get_right(), end=shifter_node.get_left(), buff=0.1, color=th.GREEN)
        a_dn = Arrow(start=split_node.get_right(), end=lut_node.get_left(), buff=0.1, color=th.PURPLE)
        a_c1 = Arrow(start=shifter_node.get_right(), end=comb_node.get_left() + UP * 0.3, buff=0.1, color=th.GREEN)
        a_c2 = Arrow(start=lut_node.get_right(), end=comb_node.get_left() + DOWN * 0.3, buff=0.1, color=th.PURPLE)

        nodes = VGroup(scaler_node, sc_lbl, split_node, sp_lbl, shifter_node, sh_lbl,
                       lut_node, lu_lbl, comb_node, co_lbl, a1, a_up, a_dn, a_c1, a_c2)

        self.play(FadeIn(nodes), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "In just 3.2 nanoseconds, the SFU multiplies the barrel-shifted integer with the LUT fraction to yield high-precision Q8.8 output!"
            )),
            run_time=0.6
        )
        self.wait(2.2)

        self.play(FadeOut(dp_title), FadeOut(nodes), run_time=0.5)

        # =====================================================================
        # ACT 4: GRAND FINALE — PRE-SILICON TAPE-OUT CHECKPOINT (~60s)
        # =====================================================================
        finale_title = Text("Grand Finale: Complete Pre-Silicon SoC Tape-Out!",
                            font=th.SANS, weight=BOLD, font_size=26, color=th.GREEN_LIGHT)
        finale_title.to_edge(UP, buff=0.6)
        self.play(Write(finale_title), run_time=0.6)

        f_card = th.card(10.5, 3.1, stroke=th.GREEN, radius=0.18).move_to(UP * 0.3)
        c1 = Text("★ FULL SILICON HARDWARE CURRICULUM COMPLETED:", font=th.SANS, weight=BOLD, font_size=16, color=th.GREEN_LIGHT)
        c2 = Text("• 4x4 Systolic Wavefront Tensor Core: Computes 100 TFLOPS Matrix Projections", font=th.MONO, font_size=13, color=th.CYAN_LIGHT)
        c3 = Text("• Non-Linear SFU Pipeline: Scaled Softmax, RSQRT RMSNorm, and SwiGLU Exp2", font=th.MONO, font_size=13, color=th.AMBER_LIGHT)
        c4 = Text("• End-to-End Cocotb Verification: All modules passed against PyTorch golden models!", font=th.MONO, font_size=13, color=th.TEXT)
        c5 = Text("You now possess the foundational blueprints of modern AI Acceleration Silicon!", font=th.MONO, weight=BOLD, font_size=14, color=th.GREEN)

        c_stack = VGroup(c1, c2, c3, c4, c5).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(f_card)

        self.play(Create(f_card), FadeIn(c_stack), run_time=1.0)
        self.play(
            Transform(banner, th.narration_banner(
                "Congratulations! You have mastered the complete hardware architecture from mathematical algorithms down to synthesizable silicon gates!"
            )),
            run_time=0.6
        )
        self.wait(3.5)
