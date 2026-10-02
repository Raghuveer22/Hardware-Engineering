"""
Lab 05: Scaled Attention — Hardware Square Root Unit & Attention Variance Scaling
A deep, visual-first masterclass on transformer scaling factors in silicon.
Builds bottom-up: Attention Gradient Collapse -> The Non-Restoring Root Engine ->
Step-by-Step Cycle Walkthrough (Radicand 64 -> Root 8) -> Interactive Challenge -> Synthesizable RTL.
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


class Lab05SquareRoot(SiliconCameraRig):
    def construct(self):
        layout = self.layout
        config = HardwareConfig(data_width=8)

        # =====================================================================
        # ACT 1: THE ATTENTION VARIANCE CRISIS (~50s)
        # =====================================================================
        kicker, _, _ = th.header(
            "SCALED ATTENTION",
            "Why Transformers Require Hardware Square Root",
            title_size=th.FONT_TITLE,
            badge_color=th.CYAN
        )
        self.play(FadeIn(kicker, shift=DOWN * 0.3), run_time=1.0)

        banner = th.narration_banner(
            "In Transformers, self-attention scales linearly with embedding dimension d_k. Without scaling, attention completely breaks."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.8)
        self.wait(5.5)

        # PyTorch Code Window on Left
        py_code = [
            ("# Transformer Attention Scaling", th.MUTED),
            ("import torch", th.CYAN),
            ("d_k = 128  # Head Dimension in LLaMA", th.TEXT),
            ("raw_scores = Q @ K.T  # Variance = 128!", th.AMBER),
            ("scaled_scores = raw_scores / math.sqrt(d_k)", th.GREEN),
            ("", th.MUTED),
            ("# Without 1/sqrt(d_k):", th.RED),
            ("# Logits explode -> Softmax gradients vanish to 0!", th.RED_LIGHT),
        ]
        soft_win = th.code_window(
            py_code, title_text="PYTORCH: ATTENTION SCALING",
            width=6.2, height=3.8, font_size=th.FONT_TINY
        ).move_to(LEFT * 3.1 + DOWN * 0.4)

        # Right Panel: Gradient Collapse Shock
        m1 = th.metric_card("128.0", "Unscaled Variance", "Variance grows linearly with head dimension d_k", color=th.RED, width=4.8, height=1.7)
        m2 = th.metric_card("1.0", "Normalized Variance", "Scaled by 1/sqrt(d_k) to prevent saturation", color=th.GREEN, width=4.8, height=1.7)
        right_panel = VGroup(m1, m2).arrange(DOWN, buff=th.SPACE_MD).move_to(RIGHT * 3.3 + DOWN * 0.4)

        self.play(Create(soft_win), run_time=1.2)
        self.play(FadeIn(m1, shift=UP * 0.2), FadeIn(m2, shift=UP * 0.2), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "When d_k is 128, dot products grow so large that Softmax saturates into a dead one-hot needle, causing gradients to vanish!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(kicker), FadeOut(soft_win), FadeOut(right_panel), run_time=0.6)

        # =====================================================================
        # ACT 2: THE SILICON ARITHMETIC DILEMMA (~60s)
        # =====================================================================
        act2_title = Text("The Silicon Dilemma: Why FPUs are Too Slow",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.AMBER).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act2_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "In software, we simply call math.sqrt(). But in physical silicon, floating-point dividers take 50+ cycles and huge die area!"
            )),
            run_time=0.6
        )
        self.wait(5.0)

        fpu_card = th.card(5.6, 3.6, stroke=th.RED, radius=0.16).move_to(LEFT * 3.1 + DOWN * 0.35)
        h_fpu = Text("TRADITIONAL FPU SQRT", font=th.SANS, weight=BOLD, font_size=15, color=th.RED_LIGHT).next_to(fpu_card.get_top(), DOWN, buff=0.2)
        lines_fpu = th.bullets(
            ["50+ clock cycles latency",
             "Massive silicon area (~10,000 gates)",
             "Burns excessive thermal power",
             "Stalls the systolic pipeline"],
            color=th.TEXT, font_size=13, bullet_color=th.RED, buff=0.22
        ).next_to(h_fpu, DOWN, buff=0.2, aligned_edge=LEFT).move_to(fpu_card.get_center() + DOWN * 0.15)

        sfu_card = th.card(5.6, 3.6, stroke=th.GREEN, radius=0.16).move_to(RIGHT * 3.1 + DOWN * 0.35)
        h_sfu = Text("NON-RESTORING ROOT ENGINE", font=th.SANS, weight=BOLD, font_size=15, color=th.GREEN_LIGHT).next_to(sfu_card.get_top(), DOWN, buff=0.2)
        lines_sfu = th.bullets(
            ["Fixed-point integer arithmetic",
             "1 bit of root per stage",
             "Pure shift-and-subtract logic",
             "Combinational: 0-cycle throughput!"],
            color=th.TEXT, font_size=13, bullet_color=th.GREEN, buff=0.22
        ).next_to(h_sfu, DOWN, buff=0.2, aligned_edge=LEFT).move_to(sfu_card.get_center() + DOWN * 0.15)

        self.play(Create(fpu_card), FadeIn(h_fpu), FadeIn(lines_fpu),
                  Create(sfu_card), FadeIn(h_sfu), FadeIn(lines_sfu), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "Modern AI accelerators implement digit-by-digit non-restoring square root: fast, cheap, and strictly integer-driven."
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(act2_title), FadeOut(fpu_card), FadeOut(h_fpu), FadeOut(lines_fpu),
                  FadeOut(sfu_card), FadeOut(h_sfu), FadeOut(lines_sfu), run_time=0.6)

        # =====================================================================
        # ACT 3: DIGIT-BY-DIGIT NON-RESTORING ALGORITHM (~70s)
        # =====================================================================
        act3_title = Text("The Non-Restoring Digit Recurrence Algorithm",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.CYAN).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act3_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "Non-restoring square root mimics manual pencil-and-paper extraction: process 2 bits of the radicand per stage."
            )),
            run_time=0.6
        )
        self.wait(5.0)

        flow_box = RoundedRectangle(corner_radius=0.18, width=10.5, height=3.6, stroke_color=th.CYAN, fill_color=th.CARD, fill_opacity=0.95).move_to(UP * 0.3)
        stg1 = Text("1. Shift Remainder left by 2 bits and bring down next 2 radicand bits", font=th.MONO, font_size=13, color=th.CYAN_LIGHT)
        arr1 = Arrow(UP * 0.18, DOWN * 0.18, buff=0.04, color=th.AMBER, stroke_width=2.5)
        stg2 = Text("2. Trial Subtraction: Subtract trial divisor from current remainder", font=th.MONO, font_size=13, color=th.AMBER_LIGHT)
        arr2 = Arrow(UP * 0.18, DOWN * 0.18, buff=0.04, color=th.AMBER, stroke_width=2.5)
        stg3 = Text("3. If Remainder ≥ 0: Root bit = 1; else Root bit = 0 (No Restoring needed!)", font=th.MONO, font_size=13, color=th.GREEN_LIGHT)
        arr3 = Arrow(UP * 0.18, DOWN * 0.18, buff=0.04, color=th.GREEN, stroke_width=2.5)
        stg4 = Text("4. Repeat across 8 stages for a 16-bit Radicand -> Exact 8-bit Integer Root", font=th.MONO, weight=BOLD, font_size=14, color=th.WHITE)

        flow_grp = VGroup(stg1, arr1, stg2, arr2, stg3, arr3, stg4).arrange(DOWN, buff=0.14).move_to(flow_box)

        self.play(Create(flow_box), FadeIn(flow_grp), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "Because restoring failed subtractions wastes time, non-restoring arithmetic simply adds the divisor back in the next cycle!"
            )),
            run_time=0.6
        )
        self.wait(6.5)

        self.play(FadeOut(act3_title), FadeOut(flow_box), FadeOut(flow_grp), run_time=0.6)

        # =====================================================================
        # ACT 4: STEPPING THROUGH WITH REAL NUMBERS (d_k = 64 -> 8) (~70s)
        # =====================================================================
        act4_title = Text("Cycle Trace: Extracting sqrt(64) = 8",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.TEXT).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act4_title), run_time=0.8)

        calc_box = RoundedRectangle(corner_radius=0.18, width=10.5, height=3.6, stroke_color=th.BORDER, fill_color=th.CARD, fill_opacity=0.95).move_to(UP * 0.3)

        l1 = Text("Radicand Input (d_k): 16'd64  [0000 0000 0100 0000]", font=th.MONO, font_size=15, color=th.CYAN_LIGHT)
        l2 = Text("Stage 1..4 (Upper bits 0): Root[7:4] = 0000, Remainder = 0", font=th.MONO, font_size=13, color=th.MUTED)
        l3 = Text("Stage 5 (Pair '01'): Trial subtract 1 -> Remainder = 0 -> Root[3] = 1!", font=th.MONO, font_size=13, color=th.AMBER_LIGHT)
        l4 = Text("Stage 6..8 (Remaining '00' pairs): Trial subtract 0 -> Root[2:0] = 000", font=th.MONO, font_size=13, color=th.MUTED)
        l5 = Text("Final Root Output:  8'd8   [0000 1000] (Exact Integer Root)", font=th.MONO, weight=BOLD, font_size=16, color=th.GREEN_LIGHT)
        l6 = Text("Final Remainder:    16'd0  (Zero residual error)", font=th.MONO, font_size=14, color=th.WHITE)

        calc_stack = VGroup(l1, l2, l3, l4, l5, l6).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(calc_box)

        self.play(Create(calc_box), FadeIn(calc_stack), run_time=1.2)
        self.focus_on(calc_box, buffer_factor=1.4, run_time=th.RATE_NORMAL)

        # Packet pulse
        LaserPacketStream.shoot_token(self, calc_box.get_left() + LEFT * 1.2, calc_box.get_left(), color=th.CYAN, run_time=0.5)
        self.screen_shake(intensity=0.03, cycles=2, run_time=0.15)

        self.play(
            Transform(banner, th.narration_banner(
                "In 8 unrolled combinational stages, the hardware extracts 1 bit of root per step: sqrt(64) = 8, with zero remainder!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(act4_title), FadeOut(calc_box), FadeOut(calc_stack), run_time=0.6)
        self.reset_camera(run_time=th.RATE_FAST)

        # =====================================================================
        # ACT 5: INTERACTIVE CHECKPOINT & MATH CHALLENGE (~45s)
        # =====================================================================
        act5_title = Text("Architectural Checkpoint: Attention Dimension d_k = 128",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.AMBER).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act5_title), run_time=0.8)

        chal_card = th.card(10.5, 3.0, stroke=th.AMBER, radius=0.16).move_to(UP * 0.4)
        c_q = Text("PAUSE & CALCULATE: FIXED-POINT INTEGER ROOT", font=th.MONO, weight=BOLD, font_size=15, color=th.AMBER_LIGHT)
        c_m1 = Text("In LLaMA-3, the attention head dimension is d_k = 128.", font=th.SANS, font_size=18, color=th.TEXT)
        c_m2 = Text("What is the exact integer root and residual remainder produced by hardware?", font=th.SANS, font_size=18, color=th.TEXT)
        chal_grp = VGroup(c_q, c_m1, c_m2).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(chal_card)

        self.play(Create(chal_card), FadeIn(chal_grp), run_time=1.0)
        self.play(
            Transform(banner, th.narration_banner(
                "Pause the video: calculate the integer square root of 128. What is the nearest integer root, and what remainder is left over?"
            )),
            run_time=0.6
        )
        self.wait(7.0)

        ans_card = th.card(10.5, 1.4, stroke=th.GREEN, radius=0.14).next_to(chal_card, DOWN, buff=0.3)
        ans_t1 = Text("Integer Root: 8'd11  (since 11² = 121 ≤ 128)", font=th.MONO, weight=BOLD, font_size=15, color=th.GREEN_LIGHT)
        ans_t2 = Text("Remainder:    16'd7  (128 - 121 = 7). Exact hardware result!", font=th.MONO, font_size=13, color=th.TEXT)
        ans_box = VGroup(ans_t1, ans_t2).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(ans_card)

        self.play(Create(ans_card), FadeIn(ans_box), run_time=0.8)
        self.wait(6.5)

        self.play(FadeOut(act5_title), FadeOut(chal_card), FadeOut(chal_grp), FadeOut(ans_card), FadeOut(ans_box), run_time=0.6)

        # =====================================================================
        # ACT 6: SYNTHESIZABLE SILICON ARCHITECTURE & VERIFICATION (~45s)
        # =====================================================================
        rtl_title = Text("Synthesizable Silicon: rtl/sqrt.sv",
                         font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.CYAN).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(rtl_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "Here is the synthesizable Root Unit: an unrolled combinational loop in SystemVerilog that compiles directly to gates."
            )),
            run_time=0.6
        )

        sv_lines = [
            ("module sqrt #(parameter RADICAND_WIDTH=16, ROOT_WIDTH=8)(", th.CYAN),
            ("    input  logic [RADICAND_WIDTH-1:0] radicand,", th.TEXT),
            ("    output logic [ROOT_WIDTH-1:0]     root,", th.GREEN_LIGHT),
            ("    output logic [RADICAND_WIDTH-1:0] remainder", th.AMBER_LIGHT),
            (");", th.CYAN),
            ("    always_comb begin", th.CYAN),
            ("        // Unrolled 8-stage non-restoring shift-and-subtract:", th.MUTED),
            ("        for (int i = ROOT_WIDTH-1; i >= 0; i--) begin", th.TEXT),
            ("            trial = {rem[i+1], radicand[2*i +: 2]} - {root_acc, 2'b01};", th.CYAN_LIGHT),
            ("            root[i] = ~trial[WIDTH]; // 1 if positive subtraction", th.GREEN),
            ("        end", th.TEXT),
            ("    end", th.CYAN),
            ("endmodule", th.CYAN),
        ]
        sv_win = th.code_window(
            sv_lines, title_text="RTL/SQRT.SV: UNROLLED NON-RESTORING ROOT",
            width=10.2, height=3.3, font_size=th.FONT_TINY, title_color=th.GREEN
        ).move_to(UP * 0.45)

        self.play(Create(sv_win), run_time=1.0)
        self.wait(5.0)

        # Pre-Silicon Checkpoint
        check_card = th.card(10.2, 1.2, stroke=th.GREEN, radius=0.15).move_to(DOWN * 1.5)
        check_txt = Text("✓ Cocotb Python Golden Model: All 65,536 Radicand Integers Verified (0 Root Errors)",
                         font=th.MONO, weight=BOLD, font_size=13, color=th.GREEN_LIGHT).move_to(check_card)

        self.play(Create(check_card), FadeIn(check_txt), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "Next in our AI Hardware journey: Lab 06, where we build the Safe Softmax Engine and tame the e^80 overflow!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(rtl_title), FadeOut(sv_win), FadeOut(check_card), FadeOut(check_txt), FadeOut(banner), run_time=1.0)
        self.wait(1.0)
