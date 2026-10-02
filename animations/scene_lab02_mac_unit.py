"""
Lab 02: Accumulator Headroom — The MAC Unit & Sign Extension
A deep, visual-first masterclass on accumulator sizing, bit-growth dynamics,
and the zero-extension trap in AI accelerators.
Builds bottom-up: Dot-Product Scaling -> 16-Bit Overflow Tank -> Sign-Extension vs Zero-Extension ->
MAC Datapath & 32-Bit Gauge -> Interactive Challenge -> Synthesizable RTL.
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
    AccumulatorGauge,
    StageLayout,
    HardwareConfig,
)


class Lab02MACUnit(SiliconCameraRig):
    def construct(self):
        layout = self.layout
        config = HardwareConfig(data_width=8, vector_k=4096)

        # =====================================================================
        # ACT 1: THE DOT-PRODUCT ACCUMULATION CRISIS (~50s)
        # =====================================================================
        kicker, _, _ = th.header(
            "ACCUMULATOR HEADROOM",
            "The MAC Unit & Accumulator Bit Growth",
            title_size=th.FONT_TITLE,
            badge_color=th.CYAN
        )
        self.play(FadeIn(kicker, shift=DOWN * 0.3), run_time=1.0)

        banner = th.narration_banner(
            "In AI accelerators, multiplying numbers is only half the battle. Every neuron must accumulate thousands of products into a running sum."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.8)
        self.wait(5.5)

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
        soft_win = th.code_window(
            py_code, title_text="PYTORCH: DOT PRODUCT REDUCTION",
            width=6.4, height=3.8, font_size=th.FONT_TINY
        ).move_to(LEFT * 3.1 + DOWN * 0.4)

        # Right Panel: Scale Math
        m1 = th.metric_card("16,129", "Single INT8 Product", "127 × 127 = 16,129 (Takes 15 bits)", color=th.AMBER, width=4.8, height=1.7)
        m2 = th.metric_card("4,096", "Dot-Product Length (K)", "Accumulating 4096 products in one go!", color=th.CYAN, width=4.8, height=1.7)
        right_panel = VGroup(m1, m2).arrange(DOWN, buff=th.SPACE_MD).move_to(RIGHT * 3.3 + DOWN * 0.4)

        self.play(Create(soft_win), run_time=1.2)
        self.play(FadeIn(m1, shift=UP * 0.2), FadeIn(m2, shift=UP * 0.2), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "A single INT8 product is 16,129. If we accumulate thousands of these terms, what happens to our register?"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(kicker), FadeOut(soft_win), FadeOut(right_panel), run_time=0.6)

        # =====================================================================
        # ACT 2: THE BURSTING 16-BIT REGISTER TANK (~65s)
        # =====================================================================
        tank_title = Text("The 16-Bit Register Capacity Crisis",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.RED_LIGHT).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(tank_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "Let's visualize a 16-bit register as a container with a maximum signed capacity of +32,767."
            )),
            run_time=0.6
        )
        self.wait(5.0)

        # 16-bit Tank on Left
        tank16 = th.LiquidTankWidget(capacity=32767, width=3.2, height=3.6, title="16-BIT ACCUMULATOR",
                                     tank_color=th.BORDER, fluid_color=th.CYAN).move_to(LEFT * 2.8 + UP * 0.15)

        # Counter Card on Right
        counter_card = th.card(5.8, 3.6, stroke=th.BORDER, radius=0.18).move_to(RIGHT * 2.8 + UP * 0.15)
        c_title = Text("Product Accumulation Sequence", font=th.SANS, weight=BOLD, font_size=15, color=th.TEXT).next_to(counter_card.get_top(), DOWN, buff=0.2)

        t1 = Text("Cycle 1: +16,129  (Tank Fill: 49%)", font=th.MONO, font_size=13, color=th.CYAN_LIGHT)
        t2 = Text("Cycle 2: +16,129  (Tank Fill: 98% -> DANGER!)", font=th.MONO, font_size=13, color=th.AMBER_LIGHT)
        t3 = Text("Cycle 3: +16,129  (CATASTROPHIC OVERFLOW!)", font=th.MONO, weight=BOLD, font_size=13, color=th.RED)
        t_seq = VGroup(t1, t2, t3).arrange(DOWN, aligned_edge=LEFT, buff=0.25).next_to(c_title, DOWN, buff=0.35)

        self.play(Create(tank16), Create(counter_card), FadeIn(c_title), run_time=0.8)
        self.play(tank16.set_fluid_fraction(0.49), FadeIn(t1, shift=LEFT * 0.2), run_time=0.8)
        self.wait(2.0)

        self.play(tank16.set_fluid_fraction(0.98), FadeIn(t2, shift=LEFT * 0.2), run_time=0.8)
        self.wait(2.0)

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
        self.wait(6.0)

        self.play(FadeOut(tank_title), FadeOut(tank16), FadeOut(counter_card), FadeOut(c_title), FadeOut(t_seq), run_time=0.6)

        # =====================================================================
        # ACT 3: SIGN-EXTENSION VS ZERO-EXTENSION DISASTER (~70s)
        # =====================================================================
        act3_title = Text("The Hardware Trap: Sign-Extension vs. Zero-Extension",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.AMBER).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act3_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "To prevent overflow, we widen the accumulator to 32 bits. But how do we expand a 16-bit product to 32 bits?"
            )),
            run_time=0.6
        )
        self.wait(5.0)

        ext_card1 = th.card(5.6, 3.6, stroke=th.RED, radius=0.16).move_to(LEFT * 3.1 + DOWN * 0.35)
        h_bad = Text("ZERO-EXTENSION (FATAL BUG)", font=th.SANS, weight=BOLD, font_size=15, color=th.RED_LIGHT).next_to(ext_card1.get_top(), DOWN, buff=0.2)
        lines_bad = th.bullets(
            ["Pads upper 16 bits with 0s",
             "Suppose Product = -5 (16'hFFFB)",
             "Extends to: 32'h0000_FFFB",
             "Interpreted as: +65,531!",
             "A negative number became positive!"],
            color=th.TEXT, font_size=13, bullet_color=th.RED, buff=0.18
        ).next_to(h_bad, DOWN, buff=0.2, aligned_edge=LEFT).move_to(ext_card1.get_center() + DOWN * 0.15)

        ext_card2 = th.card(5.6, 3.6, stroke=th.GREEN, radius=0.16).move_to(RIGHT * 3.1 + DOWN * 0.35)
        h_good = Text("SIGN-EXTENSION (CORRECT)", font=th.SANS, weight=BOLD, font_size=15, color=th.GREEN_LIGHT).next_to(ext_card2.get_top(), DOWN, buff=0.2)
        lines_good = th.bullets(
            ["Replicates MSB sign bit 16 times",
             "Product = -5 (16'hFFFB, MSB=1)",
             "Extends to: 32'hFFFF_FFFB",
             "Interpreted as: -5!",
             "Preserves true negative value!"],
            color=th.TEXT, font_size=13, bullet_color=th.GREEN, buff=0.18
        ).next_to(h_good, DOWN, buff=0.2, aligned_edge=LEFT).move_to(ext_card2.get_center() + DOWN * 0.15)

        self.play(Create(ext_card1), FadeIn(h_bad), FadeIn(lines_bad),
                  Create(ext_card2), FadeIn(h_good), FadeIn(lines_good), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "Zero-extension turns -5 into +65,531! In hardware, we must replicate the MSB: {{16{product[15]}}, product}."
            )),
            run_time=0.6
        )
        self.wait(6.5)

        self.play(FadeOut(act3_title), FadeOut(ext_card1), FadeOut(h_bad), FadeOut(lines_bad),
                  FadeOut(ext_card2), FadeOut(h_good), FadeOut(lines_good), run_time=0.6)

        # =====================================================================
        # ACT 4: THE MAC DATAPATH & 32-BIT GAUGE (~70s)
        # =====================================================================
        act4_title = Text("Inside the MAC Unit Datapath",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.CYAN).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act4_title), run_time=0.8)

        # Left: MAC Datapath Block Diagram
        dp_box = RoundedRectangle(corner_radius=0.18, width=7.2, height=3.8, stroke_color=th.CYAN, fill_color=th.CARD, fill_opacity=0.95).move_to(LEFT * 2.3 + UP * 0.2)
        dp_t = Text("MAC UNIT (Multiply-Accumulate)", font=th.MONO, weight=BOLD, font_size=13, color=th.CYAN_LIGHT).next_to(dp_box.get_top(), DOWN, buff=0.15)

        mult_blk = RoundedRectangle(width=2.0, height=0.7, corner_radius=0.1, color=th.AMBER, fill_color=th.BG).move_to(dp_box.get_center() + LEFT * 2.0 + UP * 0.7)
        mult_lbl = Text("8×8 MULT", font=th.MONO, font_size=11, color=th.AMBER).move_to(mult_blk)

        ext_blk = RoundedRectangle(width=2.0, height=0.7, corner_radius=0.1, color=th.PURPLE, fill_color=th.BG).move_to(dp_box.get_center() + LEFT * 2.0 + DOWN * 0.7)
        ext_lbl = Text("SIGN EXT 32b", font=th.MONO, font_size=10, color=th.PURPLE_LIGHT).move_to(ext_blk)

        add_blk = RoundedRectangle(width=2.0, height=0.7, corner_radius=0.1, color=th.GREEN, fill_color=th.BG).move_to(dp_box.get_center() + RIGHT * 1.5 + UP * 0.7)
        add_lbl = Text("32-BIT ADD", font=th.MONO, font_size=11, color=th.GREEN).move_to(add_blk)

        acc_reg = RoundedRectangle(width=2.0, height=0.7, corner_radius=0.1, color=th.CYAN, fill_color=th.BG).move_to(dp_box.get_center() + RIGHT * 1.5 + DOWN * 0.7)
        acc_lbl = Text("ACCUM REG (FF)", font=th.MONO, font_size=10, color=th.CYAN_LIGHT).move_to(acc_reg)

        dp_grp = VGroup(dp_box, dp_t, mult_blk, mult_lbl, ext_blk, ext_lbl, add_blk, add_lbl, acc_reg, acc_lbl)

        # Right: Reusable AccumulatorGauge
        gauge = AccumulatorGauge(width=2.6, height=3.8).move_to(RIGHT * 4.0 + UP * 0.2)

        self.play(Create(dp_grp), Create(gauge), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "Inputs multiply into 16 bits, sign-extend to 32 bits, and accumulate in the 32-bit register on every rising clock edge."
            )),
            run_time=0.6
        )
        self.wait(5.0)

        # Step through accumulation levels
        gauge.set_fluid_level(self, 0.20, color=th.GREEN_LIGHT, run_time=0.8)
        self.wait(1.5)
        gauge.set_fluid_level(self, 0.45, color=th.CYAN, run_time=0.8)
        self.wait(1.5)
        gauge.set_fluid_level(self, 0.70, color=th.AMBER, run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "Even for K=4096 dot products, the running sum fills only 28 bits of the 32-bit register, leaving 4 bits of safe headroom!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(act4_title), FadeOut(dp_grp), FadeOut(gauge), run_time=0.6)

        # =====================================================================
        # ACT 5: INTERACTIVE CHECKPOINT & HEADROOM CHALLENGE (~45s)
        # =====================================================================
        act5_title = Text("Architectural Checkpoint: Accumulator Capacity",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.AMBER).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act5_title), run_time=0.8)

        chal_card = th.card(10.5, 3.0, stroke=th.AMBER, radius=0.16).move_to(UP * 0.4)
        ch_q = Text("PAUSE & CALCULATE: MAXIMUM ACCUMULATION LENGTH", font=th.MONO, weight=BOLD, font_size=15, color=th.AMBER_LIGHT)
        ch_m1 = Text("With an INT8 multiplier (max product 16,129) and a 32-bit accumulator (+2,147,483,647),", font=th.SANS, font_size=17, color=th.TEXT)
        ch_m2 = Text("how many products (K) can you accumulate before overflowing 32 bits?", font=th.SANS, font_size=17, color=th.TEXT)
        ch_grp = VGroup(ch_q, ch_m1, ch_m2).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(chal_card)

        self.play(Create(chal_card), FadeIn(ch_grp), run_time=1.0)
        self.play(
            Transform(banner, th.narration_banner(
                "Pause the video and calculate: 2^31 divided by 16,129. How many terms can this MAC unit sum safely?"
            )),
            run_time=0.6
        )
        self.wait(7.0)

        ans_card = th.card(10.5, 1.4, stroke=th.GREEN, radius=0.14).next_to(chal_card, DOWN, buff=0.3)
        ans_t1 = Text("K = 2,147,483,647 / 16,129 ≈ 133,144 terms!", font=th.MONO, weight=BOLD, font_size=15, color=th.GREEN_LIGHT)
        ans_t2 = Text("Since LLM hidden dimensions are typically 4096 or 8192, 32 bits provides total numerical safety.", font=th.MONO, font_size=13, color=th.TEXT)
        ans_box = VGroup(ans_t1, ans_t2).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(ans_card)

        self.play(Create(ans_card), FadeIn(ans_box), run_time=0.8)
        self.wait(6.5)

        self.play(FadeOut(act5_title), FadeOut(chal_card), FadeOut(ch_grp), FadeOut(ans_card), FadeOut(ans_box), run_time=0.6)

        # =====================================================================
        # ACT 6: SYNTHESIZABLE SILICON ARCHITECTURE & VERIFICATION (~45s)
        # =====================================================================
        rtl_title = Text("Synthesizable Silicon: rtl/mac_unit.sv",
                         font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.CYAN).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(rtl_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "Here is the synthesizable MAC unit: on every clock cycle, it adds the sign-extended product into the accumulator register."
            )),
            run_time=0.6
        )

        sv_lines = [
            ("always_ff @(posedge clk or negedge rst_n) begin", th.CYAN),
            ("    if (!rst_n) begin", th.TEXT),
            ("        accumulator <= 32'sd0;  // Synchronous reset", th.AMBER),
            ("    end else if (clear) begin", th.TEXT),
            ("        accumulator <= 32'sd0;  // Clear between matrix rows", th.AMBER),
            ("    end else if (valid_in) begin", th.GREEN),
            ("        // Sign-extend 16-bit product to 32 bits and accumulate:", th.MUTED),
            ("        accumulator <= accumulator + {{16{product[15]}}, product};", th.GREEN_LIGHT),
            ("    end", th.GREEN),
            ("end", th.CYAN),
        ]
        sv_win = th.code_window(
            sv_lines, title_text="RTL/MAC_UNIT.SV: PIPELINED ACCUMULATION",
            width=10.2, height=3.3, font_size=th.FONT_TINY, title_color=th.GREEN
        ).move_to(UP * 0.45)

        self.play(Create(sv_win), run_time=1.0)
        self.wait(5.0)

        # Pre-Silicon Checkpoint
        check_card = th.card(10.2, 1.2, stroke=th.GREEN, radius=0.15).move_to(DOWN * 1.5)
        check_txt = Text("✓ Cocotb Python Golden Model: 10,000 Pipelined Vector Accumulations Verified (0 Errors)",
                         font=th.MONO, weight=BOLD, font_size=13, color=th.GREEN_LIGHT).move_to(check_card)

        self.play(Create(check_card), FadeIn(check_txt), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "Next in our AI Hardware journey: Lab 03, where we assemble MAC units into Weight-Stationary Processing Elements!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(rtl_title), FadeOut(sv_win), FadeOut(check_card), FadeOut(check_txt), FadeOut(banner), run_time=1.0)
        self.wait(1.0)
