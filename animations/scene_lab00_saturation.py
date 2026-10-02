"""
Lab 00: The Number Crisis — Signed Integer Overflow & Saturation Clamping
A kinetic, visual-first masterclass on fixed-point arithmetic in AI silicon.
Refactored using the modular, parameter-driven Standard Cell Animation Library.
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
    HardwareConfig,
    StageLayout,
)


class Lab00SaturationIntro(SiliconCameraRig):
    def construct(self):
        layout = self.layout
        config = HardwareConfig(data_width=8)

        # =====================================================================
        # ACT 1: THE PYTORCH HOOK & THE SILICON BUG
        # =====================================================================
        kicker, _, _ = th.header(
            "THE NUMBER CRISIS",
            "Why AI Accelerators Need Saturation Arithmetic",
            title_size=th.FONT_TITLE,
            badge_color=th.CYAN
        )
        self.play(FadeIn(kicker, shift=DOWN * 0.3), run_time=th.RATE_NORMAL)

        banner = th.narration_banner(
            "In modern AI chips, INT8 quantization makes models 4x faster. But in silicon, standard addition hides a dangerous trap."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=th.RATE_FAST)
        self.wait(1.5)

        # PyTorch Code Window on Left
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
            width=5.8,
            height=3.8,
            font_size=th.FONT_TINY
        )

        # Right Panel: Metric Cards
        m1 = th.metric_card(
            "-106",
            "Corrupted Activation",
            "Sign bit flipped: positive became negative!",
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
        self.play(Create(soft_win), FadeIn(right_panel, shift=UP * 0.2), run_time=th.RATE_NORMAL)

        self.play(
            Transform(banner, th.narration_banner(
                "A large positive neural activation suddenly wraps around into a massive negative value, corrupting attention scores!"
            )),
            run_time=th.RATE_FAST
        )
        self.wait(2.2)

        self.play(
            FadeOut(kicker),
            FadeOut(stage_split),
            run_time=th.RATE_FAST
        )

        # =====================================================================
        # ACT 2 & 3: THE TWO'S COMPLEMENT SPEEDOMETER WHEEL & CLAMP
        # =====================================================================
        act2_title = Text(
            "Inside the Silicon: The Two's Complement Speedometer",
            font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.TEXT
        ).move_to(layout.hud_anchor(buff=0.6))
        self.play(Write(act2_title), run_time=th.RATE_FAST)

        # Create our parameter-driven modular TwosComplementWheel
        wheel = TwosComplementWheel(bits=8, radius=2.1).move_to(layout.center + DOWN * 0.1)
        self.play(Create(wheel), run_time=th.RATE_SLOW)

        # Smooth camera dive into the wheel for cinematic focus
        self.focus_on(wheel, buffer_factor=1.45, run_time=th.RATE_NORMAL)

        # Start at +100
        wheel.set_value_instant(100)
        self.play(
            Transform(banner, th.narration_banner(
                "Two's complement behaves like a circular speedometer. We start at +100 in the green positive zone."
            )),
            run_time=th.RATE_FAST
        )
        self.wait(1.5)

        # Scenario A: Standard Unclamped Addition (+100 + 50) -> Catastrophic Overflow!
        self.play(
            Transform(banner, th.narration_banner(
                "Add +50 without saturation: watch the needle cross the +127 boundary and violently snap into the red negative zone!"
            )),
            run_time=th.RATE_FAST
        )

        # Animate sweep across the boundary to -106
        wheel.animate_sweep(self, 150, run_time=1.4, clamp=False)
        
        # Tactile screen vibration indicating arithmetic corruption!
        self.screen_shake(intensity=0.09, cycles=4, run_time=0.3)

        overflow_badge = Text(
            "🚨 OVERFLOW CORRUPTION: +100 + 50 = -106!",
            font=th.MONO, weight=BOLD, font_size=th.FONT_CAPTION, color=th.RED
        ).next_to(wheel, UP, buff=th.SPACE_MD)
        self.play(FadeIn(overflow_badge, shift=UP * 0.2), run_time=th.RATE_FAST)
        self.wait(2.0)

        # Scenario B: Engaging Hardware Saturation Clamping
        self.play(
            FadeOut(overflow_badge),
            Transform(banner, th.narration_banner(
                "The Architectural Fix: Hardware Saturation. A mechanical clamp drops at +127 to prevent wraparound."
            )),
            run_time=th.RATE_FAST
        )

        # Reset needle to +100
        wheel.set_value_instant(100)
        self.wait(0.5)

        # Deploy the spring-loaded saturation clamp barrier!
        wheel.deploy_clamp_barrier(self)
        self.wait(0.8)

        # Sweep again from +100 toward +150: hits the clamp at +127!
        self.play(
            Transform(banner, th.narration_banner(
                "Now add +50 again: the needle advances toward +150, SLAMS into the clamp, and holds safely at +127!"
            )),
            run_time=th.RATE_FAST
        )
        wheel.animate_sweep(self, 150, run_time=1.2, clamp=True)
        
        # Clamp contact impact
        self.screen_shake(intensity=0.05, cycles=2, run_time=0.18)

        clamped_badge = Text(
            "✓ CLAMPED SAFELY AT +127 (MAX_POS)",
            font=th.MONO, weight=BOLD, font_size=th.FONT_CAPTION, color=th.GREEN_LIGHT
        ).next_to(wheel, UP, buff=th.SPACE_MD)
        self.play(FadeIn(clamped_badge, shift=UP * 0.2), run_time=th.RATE_FAST)
        self.wait(2.2)

        # Reset camera back to full wide-angle view
        self.play(
            FadeOut(act2_title),
            FadeOut(wheel),
            FadeOut(clamped_badge),
            run_time=th.RATE_FAST
        )
        self.reset_camera(run_time=th.RATE_FAST)

        # =====================================================================
        # ACT 4: SYNTHESIZABLE SILICON GATES & PRE-SILICON VERIFICATION
        # =====================================================================
        rtl_title = Text(
            "Synthesizable SystemVerilog: rtl/adder.sv",
            font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.CYAN
        ).move_to(layout.hud_anchor(buff=0.6))
        self.play(Write(rtl_title), run_time=th.RATE_FAST)

        self.play(
            Transform(banner, th.narration_banner(
                "Here is the synthesizable logic. An XOR gate detects sign mismatch, and a multiplexer clamps the output in 1 cycle!"
            )),
            run_time=th.RATE_FAST
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
            width=9.8,
            height=3.0,
            font_size=th.FONT_TINY,
            title_color=th.GREEN
        ).move_to(layout.center + UP * 0.4)

        self.play(Create(sv_win), run_time=th.RATE_NORMAL)
        self.wait(1.2)

        # Pre-Silicon Checkpoint
        check_card = th.card(9.8, 1.1, stroke=th.GREEN, radius=0.15)
        check_card.move_to(layout.center + DOWN * 1.8)
        pass_txt = Text(
            "✓ Cocotb Python Golden Model: 100,000 Random Vectors Passed (0 Errors, 42 Gates)",
            font=th.MONO, weight=BOLD, font_size=th.FONT_BADGE, color=th.GREEN_LIGHT
        ).move_to(check_card)

        self.play(Create(check_card), FadeIn(pass_txt), run_time=th.RATE_FAST)
        self.play(
            Transform(banner, th.narration_banner(
                "Next in our AI Silicon journey: Lab 01, where we multiply two INT8 numbers and face the O(N²) Area Monster!"
            )),
            run_time=th.RATE_FAST
        )
        self.wait(2.5)
