"""
Lab 00: The Number Crisis — Signed Integer Overflow & Saturation Clamping
A deep, visual-first masterclass on fixed-point arithmetic in AI silicon.
Builds bottom-up: 1-Bit Full Adder -> 8-Bit Ripple Carry -> Signed 2's Complement -> Saturation Clamping.

Reuses all existing standard cell components while delivering full 5-minute pedagogical depth.
"""

from manim import *
import numpy as np
import sys
from pathlib import Path

# Ensure animations directory is in sys.path
ANIM_DIR = Path(__file__).resolve().parent
if str(ANIM_DIR) not in sys.path:
    sys.path.insert(0, str(ANIM_DIR))

import theme as th
from components import (
    SiliconCameraRig,
    TwosComplementWheel,
    FullAdderGateSchematic,
    RippleCarryChain,
    HardwareConfig,
    StageLayout,
)


class Lab00SaturationIntro(SiliconCameraRig):
    def construct(self):
        layout = self.layout
        config = HardwareConfig(data_width=8)

        # =====================================================================
        # ACT 1: THE PYTORCH HOOK & THE SILICON BUG (~50s)
        # =====================================================================
        kicker, _, _ = th.header(
            "THE NUMBER CRISIS",
            "Why AI Silicon Demands Saturation Arithmetic",
            title_size=th.FONT_TITLE,
            badge_color=th.CYAN
        )
        self.play(FadeIn(kicker, shift=DOWN * 0.3), run_time=1.0)

        banner = th.narration_banner(
            "In modern AI chips, INT8 quantization delivers 4x compute density. But in silicon, standard addition hides a catastrophic trap."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.8)
        self.wait(5.5)

        # Left Panel: PyTorch Code Window
        py_code = [
            ("# PyTorch INT8 Quantized Layer", th.MUTED),
            ("import torch", th.CYAN),
            ("a = torch.tensor([100], dtype=torch.int8)", th.TEXT),
            ("b = torch.tensor([50],  dtype=torch.int8)", th.TEXT),
            ("c = a + b  # Expected: +150", th.GREEN),
            ("", th.MUTED),
            ("print(c)   # Reality in Silicon:", th.AMBER),
            (">>> tensor([-106])  # 🚨 CATASTROPHIC WRAP!", th.RED),
        ]
        soft_win = th.code_window(
            py_code,
            title_text="PYTORCH: INT8 OVERFLOW BUG",
            width=6.0,
            height=3.8,
            font_size=th.FONT_TINY
        )

        # Right Panel: Metric Cards
        m1 = th.metric_card(
            "-106",
            "Corrupted Activation",
            "Sign bit flipped: strong positive became negative!",
            color=th.RED,
            width=4.8,
            height=1.7
        )
        m2 = th.metric_card(
            f"{config.min_val} to +{config.max_val}",
            "8-Bit Dynamic Range",
            "Signed two's complement closed boundary",
            color=th.AMBER,
            width=4.8,
            height=1.7
        )
        right_panel = VGroup(m1, m2).arrange(DOWN, buff=th.SPACE_MD)

        stage_split = layout.split_columns(soft_win, right_panel, buff=th.SPACE_LG)
        self.play(Create(soft_win), FadeIn(right_panel, shift=UP * 0.2), run_time=1.2)

        self.play(
            Transform(banner, th.narration_banner(
                "When positive attention weights sum past +127, the sign bit flips. +150 wraps to -106, poisoning the entire model!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(
            FadeOut(kicker),
            FadeOut(stage_split),
            run_time=0.6
        )

        # =====================================================================
        # ACT 2: FIRST PRINCIPLES — THE 1-BIT FULL ADDER (~60s)
        # =====================================================================
        act2_title = Text(
            "First Principles: The 1-Bit Full Adder",
            font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.TEXT
        ).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act2_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "Every silicon adder begins with 1 bit. A Full Adder takes 3 inputs (A, B, Cin) and produces 2 outputs (Sum, Cout)."
            )),
            run_time=0.6
        )
        self.wait(5.0)

        # Instantiate our reusable FullAdderGateSchematic
        fa_schematic = FullAdderGateSchematic(width=7.8, height=3.8).move_to(UP * 0.15)
        self.play(Create(fa_schematic), run_time=1.2)

        # Highlight parity XOR logic
        self.play(
            Transform(banner, th.narration_banner(
                "Sum uses XOR gates as an odd-parity detector: Sum = A ⊕ B ⊕ Cin. It is 1 only when an odd number of inputs are high."
            )),
            run_time=0.6
        )
        self.play(Indicate(fa_schematic.xor1_grp, color=th.GREEN), Indicate(fa_schematic.xor2_grp, color=th.GREEN), run_time=1.0)
        self.wait(5.5)

        # Highlight majority Cout logic
        self.play(
            Transform(banner, th.narration_banner(
                "Carry-Out (Cout) uses AND-OR logic as a majority voter: whenever 2 or more inputs are 1, a carry bit is born!"
            )),
            run_time=0.6
        )
        self.play(Indicate(fa_schematic.and1_grp, color=th.AMBER), Indicate(fa_schematic.and2_grp, color=th.AMBER), Indicate(fa_schematic.or1_grp, color=th.RED), run_time=1.0)
        self.wait(5.5)

        self.play(FadeOut(act2_title), FadeOut(fa_schematic), run_time=0.6)

        # =====================================================================
        # ACT 3: CASCADING BIT SLICES — THE 8-BIT RIPPLE CARRY ADDER (~55s)
        # =====================================================================
        act3_title = Text(
            "Cascading Slices: The 8-Bit Ripple Carry Chain",
            font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.CYAN
        ).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act3_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "To add 8-bit numbers, we chain 8 Full Adders. Each bit slice passes its Carry-Out to the next slice's Carry-In."
            )),
            run_time=0.6
        )
        self.wait(5.0)

        # Instantiate our reusable RippleCarryChain
        chain = RippleCarryChain(bits=8, width=11.6, height=1.6).move_to(UP * 0.5)
        self.play(Create(chain), run_time=1.2)

        self.play(
            Transform(banner, th.narration_banner(
                "Notice the physical propagation delay (t_pd): the most-significant bit (FA7) cannot compute until the carry ripples all the way from FA0!"
            )),
            run_time=0.6
        )
        # Animate the carry token rippling across all 8 stages
        chain.animate_ripple(self, run_time=2.2)
        self.wait(4.5)

        # Note on signed vs unsigned interpretation
        signed_note = th.card(11.6, 1.2, stroke=th.AMBER, radius=0.12).move_to(DOWN * 1.0)
        signed_txt = Text(
            "In Signed Two's Complement: Bit 7 is NOT just another power of two.\nBit 7 carries negative weight: -2^7 = -128! This creates the overflow trap.",
            font=th.MONO, font_size=13, color=th.TEXT, line_spacing=1.3
        ).move_to(signed_note)
        self.play(Create(signed_note), FadeIn(signed_txt), run_time=0.8)
        self.wait(6.0)

        self.play(FadeOut(act3_title), FadeOut(chain), FadeOut(signed_note), FadeOut(signed_txt), run_time=0.6)

        # =====================================================================
        # ACT 4: THE SPEEDOMETER WHEEL & HARDWARE SATURATION CLAMP (~80s)
        # =====================================================================
        act4_title = Text(
            "Inside the Silicon: The Two's Complement Speedometer",
            font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.TEXT
        ).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act4_title), run_time=0.8)

        # REUSE Existing Masterpiece: TwosComplementWheel
        wheel = TwosComplementWheel(bits=8, radius=2.1).move_to(layout.center + DOWN * 0.1)
        self.play(Create(wheel), run_time=1.2)

        self.focus_on(wheel, buffer_factor=1.45, run_time=th.RATE_NORMAL)

        # Start at +100
        wheel.set_value_instant(100)
        self.play(
            Transform(banner, th.narration_banner(
                "Two's complement behaves like a circular speedometer. We start at +100 in the green positive zone."
            )),
            run_time=0.6
        )
        self.wait(5.0)

        # Scenario A: Standard Unclamped Addition (+100 + 50) -> Catastrophic Overflow!
        self.play(
            Transform(banner, th.narration_banner(
                "Add +50 without saturation: watch the needle cross the +127 boundary and violently snap into the red negative zone!"
            )),
            run_time=0.6
        )
        wheel.animate_sweep(self, 150, run_time=2.0, clamp=False)
        self.screen_shake(intensity=0.09, cycles=4, run_time=0.35)

        overflow_badge = Text(
            "🚨 OVERFLOW CORRUPTION: +100 + 50 = -106!",
            font=th.MONO, weight=BOLD, font_size=th.FONT_CAPTION, color=th.RED
        ).next_to(wheel, UP, buff=th.SPACE_MD)
        self.play(FadeIn(overflow_badge, shift=UP * 0.2), run_time=0.6)
        self.wait(6.0)

        # Scenario B: Engaging Hardware Saturation Clamping
        self.play(
            FadeOut(overflow_badge),
            Transform(banner, th.narration_banner(
                "The Silicon Fix: Hardware Saturation. A mechanical clamp drops at +127 to physically prevent wraparound."
            )),
            run_time=0.6
        )
        wheel.set_value_instant(100)
        self.wait(1.0)

        # REUSE Existing Masterpiece: Deploy spring-loaded clamp barrier
        wheel.deploy_clamp_barrier(self)
        self.wait(2.0)

        # Sweep again from +100 toward +150: hits clamp at +127!
        self.play(
            Transform(banner, th.narration_banner(
                "Now add +50 again: the needle advances toward +150, SLAMS into the clamp, and holds safely at +127!"
            )),
            run_time=0.6
        )
        wheel.animate_sweep(self, 150, run_time=1.8, clamp=True)
        self.screen_shake(intensity=0.05, cycles=2, run_time=0.2)

        clamped_badge = Text(
            "✓ CLAMPED SAFELY AT +127 (MAX_POS)",
            font=th.MONO, weight=BOLD, font_size=th.FONT_CAPTION, color=th.GREEN_LIGHT
        ).next_to(wheel, UP, buff=th.SPACE_MD)
        self.play(FadeIn(clamped_badge, shift=UP * 0.2), run_time=0.6)
        self.wait(6.5)

        self.play(
            FadeOut(act4_title),
            FadeOut(wheel),
            FadeOut(clamped_badge),
            run_time=0.6
        )
        self.reset_camera(run_time=th.RATE_FAST)

        # =====================================================================
        # ACT 5: INTERACTIVE CHECKPOINT & MATH CHALLENGE (~45s)
        # =====================================================================
        act5_title = Text(
            "Architectural Checkpoint: The Negative Overflow Challenge",
            font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.AMBER
        ).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act5_title), run_time=0.8)

        chal_card = th.card(10.5, 3.2, stroke=th.AMBER, radius=0.16).move_to(UP * 0.3)
        chal_q = Text("PAUSE & PREDICT THE SILICON BEHAVIOR:", font=th.MONO, weight=BOLD, font_size=15, color=th.AMBER_LIGHT)
        chal_math = Text("What happens when adding: (-100) + (-50) in 8-bit Two's Complement?", font=th.SANS, font_size=18, color=th.TEXT)
        chal_hint = Text("Hint: Unclamped raw sum is -150. Representable range is [-128, +127].", font=th.MONO, font_size=14, color=th.MUTED)
        chal_box = VGroup(chal_q, chal_math, chal_hint).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(chal_card)

        self.play(Create(chal_card), FadeIn(chal_box), run_time=1.0)
        self.play(
            Transform(banner, th.narration_banner(
                "Pause the video and calculate: does two negative numbers adding past -128 wrap to positive, and what is the clamped result?"
            )),
            run_time=0.6
        )
        self.wait(7.0)

        # Reveal Solution
        ans_card = th.card(10.5, 1.4, stroke=th.GREEN, radius=0.14).next_to(chal_card, DOWN, buff=0.3)
        ans_t1 = Text("Raw Unclamped Result:  -150 wraps to +106 (Negative became Positive!)", font=th.MONO, font_size=13, color=th.RED_LIGHT)
        ans_t2 = Text("Hardware Clamped Result: Clamps cleanly to -128 (8'sd-128 MIN_NEG)", font=th.MONO, weight=BOLD, font_size=14, color=th.GREEN_LIGHT)
        ans_box = VGroup(ans_t1, ans_t2).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(ans_card)

        self.play(Create(ans_card), FadeIn(ans_box), run_time=0.8)
        self.wait(6.5)

        self.play(FadeOut(act5_title), FadeOut(chal_card), FadeOut(chal_box), FadeOut(ans_card), FadeOut(ans_box), run_time=0.6)

        # =====================================================================
        # ACT 6: SYNTHESIZABLE SILICON GATES & PRE-SILICON VERIFICATION (~45s)
        # =====================================================================
        rtl_title = Text(
            "Synthesizable SystemVerilog: rtl/adder.sv",
            font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.CYAN
        ).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(rtl_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "Here is the synthesizable logic. An XOR gate detects sign mismatch, and a multiplexer clamps the output in 1 cycle!"
            )),
            run_time=0.6
        )

        sv_lines = [
            ("// Overflow occurs when two same-sign inputs produce opposite sign:", th.MUTED),
            ("assign pos_overflow = (~a[7] & ~b[7]) &  sum_raw[7];", th.CYAN_LIGHT),
            ("assign neg_overflow = ( a[7] &  b[7]) & ~sum_raw[7];", th.RED_LIGHT),
            ("", th.MUTED),
            ("// 3-Way Hardware Saturation Multiplexer:", th.AMBER),
            ("assign sum_out = (pos_overflow) ? 8'sd127 :", th.GREEN),
            ("                 (neg_overflow) ? -8'sd128 : sum_raw[7:0];", th.GREEN),
        ]
        sv_win = th.code_window(
            sv_lines,
            title_text="RTL/ADDER.SV: COMBINATIONAL SATURATION",
            width=10.2,
            height=3.1,
            font_size=th.FONT_TINY,
            title_color=th.GREEN
        ).move_to(UP * 0.5)

        self.play(Create(sv_win), run_time=1.0)
        self.wait(5.0)

        # Pre-Silicon Checkpoint Card
        check_card = th.card(10.2, 1.2, stroke=th.GREEN, radius=0.15).move_to(DOWN * 1.5)
        pass_txt = Text(
            "✓ Cocotb Python Golden Model: 100,000 Random Vectors Passed (0 Errors, 42 Gates)",
            font=th.MONO, weight=BOLD, font_size=th.FONT_BADGE, color=th.GREEN_LIGHT
        ).move_to(check_card)

        self.play(Create(check_card), FadeIn(pass_txt), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "Next in our AI Hardware journey: Lab 01, where we multiply two INT8 numbers and face the O(N²) Area Monster!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(rtl_title), FadeOut(sv_win), FadeOut(check_card), FadeOut(pass_txt), FadeOut(banner), run_time=1.0)
        self.wait(1.0)
