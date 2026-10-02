"""
Lab 08: The Non-Linear Engine — Hardware Exponential SFU (2^x & e^x) for SwiGLU
A deep, visual-first masterclass on the Base-2 silicon trick powering modern LLMs.
Builds bottom-up: SwiGLU Activation Challenge -> The Base-2 Laser Slice (2^I * 2^F) ->
Combinational SFU Datapath -> Real Number Trace (x=1.0 -> 2.718) -> Interactive Challenge -> RTL & Tapeout.
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
        # ACT 1: THE SWIGLU / SILU ACTIVATION CHALLENGE (~50s)
        # =====================================================================
        kicker, _, _ = th.header(
            "THE NON-LINEAR ENGINE",
            "Hardware Exponential SFU for SwiGLU & SiLU",
            title_size=th.FONT_TITLE,
            badge_color=th.CYAN
        )
        self.play(FadeIn(kicker, shift=DOWN * 0.3), run_time=1.0)

        banner = th.narration_banner(
            "In modern Transformer architectures, over 60% of all parameters and compute FLOPs reside in SwiGLU non-linear Feed-Forward Networks."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.8)
        self.wait(5.5)

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
        soft_win = th.code_window(
            py_code, title_text="PYTORCH: SWIGLU ACTIVATION",
            width=6.4, height=3.8, font_size=th.FONT_TINY
        ).move_to(LEFT * 3.1 + DOWN * 0.4)

        # Right Panel: Silicon Area Shock
        m1 = th.metric_card("60% FLOPs", "FFN Layer Dominance", "Over half of inference compute is non-linear SwiGLU", color=th.AMBER, width=4.8, height=1.7)
        m2 = th.metric_card("3.2 ns", "Silicon SFU Delay", "Combinational Base-2 decomposition in silicon", color=th.GREEN, width=4.8, height=1.7)
        right_panel = VGroup(m1, m2).arrange(DOWN, buff=th.SPACE_MD).move_to(RIGHT * 3.3 + DOWN * 0.4)

        self.play(Create(soft_win), run_time=1.2)
        self.play(FadeIn(m1, shift=UP * 0.2), FadeIn(m2, shift=UP * 0.2), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "SwiGLU requires high-speed exponentiation. But computing Taylor series in silicon requires too many DSP multipliers and pipeline stalls."
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(kicker), FadeOut(soft_win), FadeOut(right_panel), run_time=0.6)

        # =====================================================================
        # ACT 2: THE BASE-2 SILICON SECRET (~65s)
        # =====================================================================
        f_title = Text("The Base-2 Silicon Secret: e^x = 2^(x · log2(e)) = 2^I × 2^F",
                       font=th.SANS, weight=BOLD, font_size=23, color=th.GREEN_LIGHT).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(f_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "By changing base to powers of two, we slice the exponent into integer I and fraction F. 2^I is a free barrel bit-shift in hardware!"
            )),
            run_time=0.6
        )
        self.wait(5.0)

        # Bit register being sliced by laser
        bit_strip = th.BitRegister(width_bits=8, initial_val="00110101", highlight_msb=False, bg_color=th.CARD).move_to(UP * 0.6)

        lbl_int = Text("Integer (I = 3)\n➔ 2³ = 8 (Barrel Shifter: 0 Gates!)", font=th.MONO, weight=BOLD, font_size=13, color=th.CYAN_LIGHT)
        lbl_int.next_to(bit_strip.cells[1], DOWN, buff=0.45)

        lbl_frac = Text("Fraction (F = 0.3125)\n➔ 2^F (16-Entry Lookup ROM)", font=th.MONO, weight=BOLD, font_size=13, color=th.PURPLE_LIGHT)
        lbl_frac.next_to(bit_strip.cells[5], DOWN, buff=0.45)

        laser = Line(bit_strip.cells[3].get_right() + UP * 0.85, bit_strip.cells[3].get_right() + DOWN * 0.85,
                     color=th.AMBER, stroke_width=3.5)
        laser_lbl = Text("BINARY POINT SLICER", font=th.MONO, weight=BOLD, font_size=11, color=th.AMBER_LIGHT).next_to(laser, UP, buff=0.1)

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
        self.wait(6.0)
        self.reset_camera(run_time=th.RATE_FAST)

        self.play(FadeOut(f_title), FadeOut(bit_strip), FadeOut(laser), FadeOut(laser_lbl),
                  FadeOut(lbl_int), FadeOut(lbl_frac), run_time=0.6)

        # =====================================================================
        # ACT 3: COMBINATIONAL SFU DATAPATH (~70s)
        # =====================================================================
        act3_title = Text("The Exponential SFU Datapath Architecture",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.CYAN).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act3_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "Here is the physical datapath: 1) Multiply by log2(e), 2) Split I and F, 3) Barrel Shift and ROM Lookup, 4) Final Multiply."
            )),
            run_time=0.6
        )
        self.wait(5.0)

        sfu_box = RoundedRectangle(corner_radius=0.18, width=10.5, height=3.6, stroke_color=th.CYAN, fill_color=th.CARD, fill_opacity=0.95).move_to(UP * 0.3)
        b1 = Text("Stage 1: Base-2 Scale: x_scaled = x · 1.442695 (Constant fixed-point scaling)", font=th.MONO, font_size=13, color=th.CYAN_LIGHT)
        a1 = Arrow(UP * 0.18, DOWN * 0.18, buff=0.04, color=th.AMBER, stroke_width=2.5)
        b2 = Text("Stage 2: Split Integer I = floor(x_scaled) and Fraction F = x_scaled - I", font=th.MONO, font_size=13, color=th.AMBER_LIGHT)
        a2 = Arrow(UP * 0.18, DOWN * 0.18, buff=0.04, color=th.AMBER, stroke_width=2.5)
        b3 = Text("Stage 3: Parallel Compute: 2^I (Barrel Shifter) || 2^F (16-Entry ROM Table)", font=th.MONO, font_size=13, color=th.GREEN_LIGHT)
        a3 = Arrow(UP * 0.18, DOWN * 0.18, buff=0.04, color=th.GREEN, stroke_width=2.5)
        b4 = Text("Stage 4: Output Product = 2^I · 2^F = e^x in just 3.2 nanoseconds!", font=th.MONO, weight=BOLD, font_size=14, color=th.WHITE)

        sfu_grp = VGroup(b1, a1, b2, a2, b3, a3, b4).arrange(DOWN, buff=0.14).move_to(sfu_box)

        self.play(Create(sfu_box), FadeIn(sfu_grp), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "Because 2^F is strictly in [1.0, 2.0), the 16-entry lookup table requires only 128 bits of silicon ROM area!"
            )),
            run_time=0.6
        )
        self.wait(6.5)

        self.play(FadeOut(act3_title), FadeOut(sfu_box), FadeOut(sfu_grp), run_time=0.6)

        # =====================================================================
        # ACT 4: REAL NUMBER WALKTHROUGH (x = 1.0 -> 2.718) (~70s)
        # =====================================================================
        act4_title = Text("Numerical Trace: Computing e^(1.0) = 2.718",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.TEXT).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act4_title), run_time=0.8)

        calc_box = RoundedRectangle(corner_radius=0.18, width=10.5, height=3.6, stroke_color=th.BORDER, fill_color=th.CARD, fill_opacity=0.95).move_to(UP * 0.3)

        l1 = Text("Input Activation:         x = 1.0000", font=th.MONO, font_size=14, color=th.CYAN_LIGHT)
        l2 = Text("Base-2 Scaling:           1.0 × 1.442695 = 1.4427", font=th.MONO, font_size=13, color=th.TEXT)
        l3 = Text("Integer / Fraction Split: I = 1,  F = 0.4427", font=th.MONO, font_size=13, color=th.AMBER_LIGHT)
        l4 = Text("Barrel Shifter Output:    2¹ = 2.0000 (Shift left 1 bit)", font=th.MONO, font_size=13, color=th.CYAN_LIGHT)
        l5 = Text("Fractional ROM Lookup:    2^(0.4427) ≈ 1.3591 (Entry #7 in ROM)", font=th.MONO, font_size=13, color=th.PURPLE_LIGHT)
        l6 = Text("Final SFU Output:         2.0 × 1.3591 = 2.7182 ≈ e¹ (Exact Euler's number!)", font=th.MONO, weight=BOLD, font_size=15, color=th.GREEN_LIGHT)

        calc_grp = VGroup(l1, l2, l3, l4, l5, l6).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(calc_box)

        self.play(Create(calc_box), FadeIn(calc_grp), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "2.0 times 1.3591 equals 2.7182: the exact mathematical value of e^1 computed purely with shifts and a tiny ROM!"
            )),
            run_time=0.6
        )
        self.wait(6.5)

        self.play(FadeOut(act4_title), FadeOut(calc_box), FadeOut(calc_grp), run_time=0.6)

        # =====================================================================
        # ACT 5: INTERACTIVE CHECKPOINT & MATH CHALLENGE (~45s)
        # =====================================================================
        act5_title = Text("Architectural Checkpoint: The Negative Exponent Challenge",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.AMBER).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act5_title), run_time=0.8)

        chal_card = th.card(10.5, 3.0, stroke=th.AMBER, radius=0.16).move_to(UP * 0.4)
        c_q = Text("PAUSE & CALCULATE: NEGATIVE EXPONENTS IN SILICON", font=th.MONO, weight=BOLD, font_size=15, color=th.AMBER_LIGHT)
        c_m1 = Text("For the Sigmoid function σ(-x), input x can be negative (e.g. x = -1.0).", font=th.SANS, font_size=18, color=th.TEXT)
        c_m2 = Text("How does the hardware Barrel Shifter evaluate 2^I when integer I is negative?", font=th.SANS, font_size=18, color=th.TEXT)
        chal_grp = VGroup(c_q, c_m1, c_m2).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(chal_card)

        self.play(Create(chal_card), FadeIn(chal_grp), run_time=1.0)
        self.play(
            Transform(banner, th.narration_banner(
                "Pause the video: what does 2^(-1) correspond to in digital hardware? How does the barrel shifter handle it?"
            )),
            run_time=0.6
        )
        self.wait(7.0)

        ans_card = th.card(10.5, 1.4, stroke=th.GREEN, radius=0.14).next_to(chal_card, DOWN, buff=0.3)
        ans_t1 = Text("Negative I means 2^(-k) = 1 / (2^k) ➔ An Arithmetic RIGHT Shift!", font=th.MONO, weight=BOLD, font_size=15, color=th.GREEN_LIGHT)
        ans_t2 = Text("A bidirectional barrel shifter simply shifts right for negative numbers with zero extra delay.", font=th.MONO, font_size=13, color=th.TEXT)
        ans_box = VGroup(ans_t1, ans_t2).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(ans_card)

        self.play(Create(ans_card), FadeIn(ans_box), run_time=0.8)
        self.wait(6.5)

        self.play(FadeOut(act5_title), FadeOut(chal_card), FadeOut(chal_grp), FadeOut(ans_card), FadeOut(ans_box), run_time=0.6)

        # =====================================================================
        # ACT 6: SYNTHESIZABLE SILICON & CURRICULUM GRADUATION (~45s)
        # =====================================================================
        rtl_title = Text("Synthesizable Silicon: rtl/exp2_sfu.sv & Full Tapeout!",
                         font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.CYAN).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(rtl_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "Here is the synthesizable SFU: barrel shifter and ROM table combined in a single combinational always_comb block."
            )),
            run_time=0.6
        )

        sv_lines = [
            ("module exp2_sfu #(parameter DATA_WIDTH = 16, Q_FRAC = 8)(", th.CYAN),
            ("    input  logic signed [DATA_WIDTH-1:0] x_in,", th.TEXT),
            ("    output logic        [DATA_WIDTH-1:0] exp_out", th.GREEN_LIGHT),
            (");", th.CYAN),
            ("    // 1. Barrel shift integer component:", th.MUTED),
            ("    assign shift_val = (int_part >= 0) ? (frac_rom_val << int_part) :", th.CYAN_LIGHT),
            ("                                         (frac_rom_val >> (-int_part));", th.CYAN_LIGHT),
            ("    // 2. 16-Entry Fractional Lookup Table:", th.MUTED),
            ("    assign frac_rom_val = EXP2_FRAC_LUT[frac_part[7:4]];", th.AMBER_LIGHT),
            ("    assign exp_out      = shift_val;", th.GREEN),
            ("endmodule", th.CYAN),
        ]
        sv_win = th.code_window(
            sv_lines, title_text="RTL/EXP2_SFU.SV: COMBINATIONAL BASE-2 ENGINE",
            width=10.2, height=3.3, font_size=th.FONT_TINY, title_color=th.GREEN
        ).move_to(UP * 0.45)

        self.play(Create(sv_win), run_time=1.0)
        self.wait(5.0)

        # Graduation Card
        grad_card = th.card(10.2, 1.3, stroke=th.GREEN, radius=0.15).move_to(DOWN * 1.5)
        grad_txt = Text(
            "🎉 CONGRATULATIONS! You have mastered the entire Silicon AI Acceleration Stack\n"
            "from 1-Bit Full Adders to 2D Systolic TPU Arrays, Safe Softmax, and Non-Linear SFUs!",
            font=th.MONO, weight=BOLD, font_size=12, color=th.GREEN_LIGHT, line_spacing=1.3
        ).move_to(grad_card)

        self.play(Create(grad_card), FadeIn(grad_txt), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "You now understand how AI models physically execute in silicon. Pre-silicon verification is complete: ready for tape-out!"
            )),
            run_time=0.6
        )
        self.wait(7.0)

        self.play(FadeOut(rtl_title), FadeOut(sv_win), FadeOut(grad_card), FadeOut(grad_txt), FadeOut(banner), run_time=1.0)
        self.wait(1.0)
