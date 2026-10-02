"""
Lab 02: Accumulator Headroom — The MAC Unit & Sign Extension
A kinetic, visual-first masterclass on accumulator sizing and sign-bit replication.

Narrative Flow:
  Act 1: The Dot-Product Accumulation Crisis (K = 4096 terms in LLaMA)
  Act 2: The Bursting 16-Bit Liquid Tank (Overspill on the 3rd addition!)
  Act 3: Sizing the 32-Bit Tank & The Zero-Extension Disaster (-5 -> +65,531)
  Act 4: Synthesizable Silicon Architecture (rtl/mac_unit.sv) & Verification
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
    StageLayout,
    HardwareConfig,
)


class Lab02MACUnit(SiliconCameraRig):
    def construct(self):
        layout = self.layout
        config = HardwareConfig(data_width=8, vector_k=4096)

        # =====================================================================
        # ACT 1: THE DOT-PRODUCT ACCUMULATION CRISIS (~45s)
        # =====================================================================
        kicker, _, _ = th.header(
            "ACCUMULATOR HEADROOM",
            "The MAC Unit & The Zero-Extension Disaster",
            title_size=30,
            badge_color=th.CYAN
        )
        self.play(FadeIn(kicker, shift=DOWN * 0.3), run_time=0.8)

        banner = th.narration_banner(
            "In AI accelerators, multiplying numbers is only half the battle. Every neuron must accumulate thousands of products into a running sum."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.7)
        self.wait(1.5)

        # PyTorch Code Window on Left
        py_code = [
            ("# PyTorch Dot-Product Accumulation", th.MUTED),
            ("import torch", th.CYAN),
            ("# Hidden Dimension K = 4096 dot-product terms", th.TEXT),
            ("a = torch.randint(-128, 127, (4096,), dtype=torch.int8)", th.TEXT),
            ("b = torch.randint(-128, 127, (4096,), dtype=torch.int8)", th.TEXT),
            ("running_sum = torch.dot(a, b)", th.GREEN),
            ("", th.MUTED),
            ("# Architectural Question:", th.AMBER),
            ("# Can a 16-bit register hold the accumulated sum?", th.RED_LIGHT),
        ]
        soft_win = th.code_window(py_code, title_text="PYTORCH: DOT PRODUCT REDUCTION",
                                  width=6.4, height=3.8, font_size=13)
        soft_win.move_to(LEFT * 3.1 + DOWN * 0.4)

        # Right Panel: Scale Math
        m1 = th.metric_card("16,129", "Single INT8 Product",
                            "127 × 127 = 16,129 (Takes 15 bits)", color=th.AMBER, width=4.8, height=1.7)
        m2 = th.metric_card("4,096", "Dot-Product Length (K)",
                            "Accumulating 4096 products in one go!", color=th.CYAN, width=4.8, height=1.7)
        right_panel = VGroup(m1, m2).arrange(DOWN, buff=0.3).move_to(RIGHT * 3.3 + DOWN * 0.4)

        self.play(Create(soft_win), run_time=1.0)
        self.wait(1.0)
        self.play(FadeIn(m1, shift=UP * 0.2), FadeIn(m2, shift=UP * 0.2), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "A single INT8 product is 16,129. If we accumulate thousands of these terms, what happens to our register?"
            )),
            run_time=0.6
        )
        self.wait(2.5)

        self.play(FadeOut(kicker), FadeOut(soft_win), FadeOut(right_panel), run_time=0.5)

        # =====================================================================
        # ACT 2: THE BURSTING 16-BIT LIQUID TANK (~60s)
        # =====================================================================
        tank_title = Text("The 16-Bit Register Capacity Crisis",
                          font=th.SANS, weight=BOLD, font_size=26, color=th.RED_LIGHT)
        tank_title.to_edge(UP, buff=0.6)
        self.play(Write(tank_title), run_time=0.6)

        self.play(
            Transform(banner, th.narration_banner(
                "Let's visualize a 16-bit register as a graduated beaker with a maximum capacity of +32,767."
            )),
            run_time=0.5
        )

        # Left: 16-bit Tank
        tank16 = th.LiquidTankWidget(capacity=32767, width=3.0, height=3.4, title="16-BIT ACCUMULATOR",
                                    tank_color=th.BORDER, fluid_color=th.CYAN)
        tank16.move_to(LEFT * 2.8 + UP * 0.15)

        # Right: Pour Counter
        counter_card = th.card(5.6, 3.4, stroke=th.BORDER, radius=0.18)
        counter_card.move_to(RIGHT * 2.8 + UP * 0.15)
        c_title = Text("Product Accumulation Sequence", font=th.SANS, weight=BOLD, font_size=15, color=th.TEXT)
        c_title.next_to(counter_card.get_top(), DOWN, buff=0.2)

        t1 = Text("Drop 1: +16,129  (Fill: 49%)", font=th.MONO, font_size=14, color=th.CYAN_LIGHT)
        t2 = Text("Drop 2: +16,129  (Fill: 98% -> DANGER!)", font=th.MONO, font_size=14, color=th.AMBER_LIGHT)
        t3 = Text("Drop 3: +16,129  (OVERFLOW SPILL!)", font=th.MONO, weight=BOLD, font_size=14, color=th.RED)
        t_seq = VGroup(t1, t2, t3).arrange(DOWN, aligned_edge=LEFT, buff=0.28).next_to(c_title, DOWN, buff=0.35)

        self.play(Create(tank16), Create(counter_card), FadeIn(c_title), run_time=0.8)
        self.wait(0.5)

        # Drop 1 pours in -> 49%
        self.play(tank16.set_fluid_fraction(0.49), FadeIn(t1, shift=LEFT * 0.2), run_time=0.8)
        self.wait(0.6)

        # Drop 2 pours in -> 98%
        self.play(tank16.set_fluid_fraction(0.98), FadeIn(t2, shift=LEFT * 0.2), run_time=0.8)
        self.wait(0.6)

        # Drop 3 pours in -> 120% OVERFLOW!
        self.play(
            tank16.set_fluid_fraction(1.2),
            tank16.fluid.animate.set_color(th.RED),
            Flash(tank16.max_line, color=th.RED, flash_radius=0.7),
            FadeIn(t3, shift=LEFT * 0.2),
            Transform(banner, th.narration_banner(
                "On just the THIRD product, the 16-bit register overflows and corrupts! A 16-bit accumulator is completely useless!"
            )),
            run_time=0.9
        )
        self.screen_shake(intensity=0.08, cycles=3, run_time=0.25)
        self.wait(2.2)

        self.play(FadeOut(tank_title), FadeOut(tank16), FadeOut(counter_card), FadeOut(c_title), FadeOut(t_seq), run_time=0.5)

        # =====================================================================
        # ACT 3: SIZING THE 32-BIT TANK & ZERO-EXTENSION DISASTER (~70s)
        # =====================================================================
        ext_title = Text("Accumulator Sizing & The Zero-Extension Disaster",
                         font=th.SANS, weight=BOLD, font_size=26, color=th.TEXT)
        ext_title.to_edge(UP, buff=0.6)
        self.play(Write(ext_title), run_time=0.6)

        self.play(
            Transform(banner, th.narration_banner(
                "Sizing formula: Required Bits = 16 + log2(K). For K=4096, we need 28 bits. A 32-bit tank holds 65,536 terms with zero overflow!"
            )),
            run_time=0.5
        )

        # Compare Wrong Zero Extension vs Correct Sign Extension
        bad_box = RoundedRectangle(corner_radius=0.18, width=10.5, height=1.5,
                                   stroke_color=th.RED, stroke_width=2.0, fill_color=th.CARD, fill_opacity=0.95)
        bad_box.move_to(UP * 0.75)
        lbl_bad = Text("❌ WRONG: Zero-Extension of Negative Product (-5):",
                       font=th.SANS, weight=BOLD, font_size=14, color=th.RED_LIGHT)
        bits_bad = Text("32'b 0000 0000 0000 0000 | 1111 1111 1111 1011  ===>  +65,531 !",
                        font=th.MONO, weight=BOLD, font_size=15, color=th.RED)
        grp_bad = VGroup(lbl_bad, bits_bad).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(bad_box)

        good_box = RoundedRectangle(corner_radius=0.18, width=10.5, height=1.5,
                                    stroke_color=th.GREEN, stroke_width=2.0, fill_color=th.CARD, fill_opacity=0.95)
        good_box.next_to(bad_box, DOWN, buff=0.3)
        lbl_good = Text("✅ CORRECT: Hardware Sign-Extension (Replicate MSB bit 15):",
                        font=th.SANS, weight=BOLD, font_size=14, color=th.GREEN_LIGHT)
        bits_good = Text("32'b 1111 1111 1111 1111 | 1111 1111 1111 1011  ===>  -5  (PRESERVED!)",
                         font=th.MONO, weight=BOLD, font_size=15, color=th.GREEN_LIGHT)
        grp_good = VGroup(lbl_good, bits_good).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(good_box)

        self.play(Create(bad_box), FadeIn(grp_bad), run_time=0.8)
        self.wait(1.0)
        self.play(Create(good_box), FadeIn(grp_good), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "If you zero-extend -5, it becomes +65,531! We must replicate the MSB across all upper 16 bits to preserve the negative value."
            )),
            run_time=0.6
        )
        self.wait(2.5)

        self.play(FadeOut(ext_title), FadeOut(bad_box), FadeOut(grp_bad), FadeOut(good_box), FadeOut(grp_good), run_time=0.5)

        # =====================================================================
        # ACT 4: SYNTHESIZABLE SILICON ARCHITECTURE & VERIFICATION (~50s)
        # =====================================================================
        rtl_title = Text("Synthesizable MAC Unit: rtl/mac_unit.sv",
                         font=th.SANS, weight=BOLD, font_size=26, color=th.CYAN)
        rtl_title.to_edge(UP, buff=0.6)
        self.play(Write(rtl_title), run_time=0.6)

        sv_lines = [
            ("// Multiply-Accumulate Combinational Datapath:", th.MUTED),
            ("module mac_unit #(parameter DATA_WIDTH=8, ACC_WIDTH=32)(", th.CYAN),
            ("    input  logic signed [DATA_WIDTH-1:0] a, b,", th.TEXT),
            ("    input  logic signed [ACC_WIDTH-1:0]  sum_in,", th.TEXT),
            ("    output logic signed [ACC_WIDTH-1:0]  sum_out", th.GREEN_LIGHT),
            (");", th.CYAN),
            ("    // 1. Compute 16-bit Product & Automatically Sign-Extend:", th.AMBER),
            ("    logic signed [15:0] prod = a * b;", th.TEXT),
            ("    assign sum_out = sum_in + {{16{prod[15]}}, prod};", th.GREEN),
            ("endmodule", th.CYAN),
        ]
        sv_win = th.code_window(sv_lines, title_text="RTL/MAC_UNIT.SV",
                                width=10.5, height=3.0, font_size=13, title_color=th.GREEN)
        sv_win.move_to(UP * 0.55)

        self.play(Create(sv_win), run_time=1.0)

        # Pre-Silicon Checkpoint
        check_card = th.card(10.5, 1.1, stroke=th.GREEN, radius=0.15)
        check_card.next_to(banner, UP, buff=0.22)
        check_txt = Text("✓ Cocotb Testbench: Verified against 4096-step cumulative vectors! (0 Overflow Errors)",
                         font=th.MONO, weight=BOLD, font_size=14, color=th.GREEN_LIGHT).move_to(check_card)

        self.play(Create(check_card), FadeIn(check_txt), run_time=0.7)
        self.play(
            Transform(banner, th.narration_banner(
                "Next in our AI Hardware journey: Lab 03, where we lock weights inside local registers to escape the 1,000x Memory Wall!"
            )),
            run_time=0.6
        )
        self.wait(3.0)
