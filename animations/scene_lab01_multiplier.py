"""
Lab 01: The Area Monster — Signed INT8 Hardware Multiplier & O(N^2) Silicon Scaling
A deep, visual-first masterclass on silicon multiplication in AI accelerators.
Builds bottom-up: 1-Bit AND multiply -> Shift-and-Add -> 64 Partial Product Grid ->
Baugh-Wooley Signed Trap -> Wallace Tree CSA Reduction -> Synthesizable RTL.
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


class Lab01Multiplier(SiliconCameraRig):
    def construct(self):
        layout = self.layout
        config = HardwareConfig(data_width=8)

        # =====================================================================
        # ACT 1: THE GEMM SCALING CRISIS (~50s)
        # =====================================================================
        kicker, _, _ = th.header(
            "THE AREA MONSTER",
            "Why Multipliers Consume 90% of AI Silicon",
            title_size=th.FONT_TITLE,
            badge_color=th.CYAN
        )
        self.play(FadeIn(kicker, shift=DOWN * 0.3), run_time=1.0)

        banner = th.narration_banner(
            "In modern Large Language Models, generating a single token requires tens of millions of matrix multiplications."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.8)
        self.wait(5.5)

        # PyTorch Code Window on Left
        py_code = [
            ("# PyTorch LLaMA-3 Feed-Forward Layer", th.MUTED),
            ("import torch", th.CYAN),
            ("x = torch.randint(-128, 127, (4096,), dtype=torch.int8)", th.TEXT),
            ("W = torch.randint(-128, 127, (4096, 14336), dtype=torch.int8)", th.TEXT),
            ("y = x @ W  # GEMM Projection", th.GREEN),
            ("", th.MUTED),
            ("# Single Token Compute Budget:", th.AMBER),
            ("# ~60 Million Multiplications in <5ms!", th.RED_LIGHT),
        ]
        soft_win = th.code_window(
            py_code, title_text="PYTORCH: INT8 GEMM PROJECTION",
            width=6.2, height=3.8, font_size=th.FONT_TINY
        ).move_to(LEFT * 3.1 + DOWN * 0.4)

        # Right Panel: Silicon Area Shock
        m1 = th.metric_card("42 Gates", "Adder Silicon Area", "O(N) Linear: Cheap & tiny in silicon", color=th.GREEN, width=4.8, height=1.7)
        m2 = th.metric_card("456 Gates", "Multiplier Silicon Area", "O(N²) Quadratic: 10x larger and hotter!", color=th.RED, width=4.8, height=1.7)
        right_panel = VGroup(m1, m2).arrange(DOWN, buff=th.SPACE_MD).move_to(RIGHT * 3.3 + DOWN * 0.4)

        self.play(Create(soft_win), run_time=1.2)
        self.play(FadeIn(m1, shift=UP * 0.2), FadeIn(m2, shift=UP * 0.2), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "An adder needs just 42 logic gates. But an 8-bit multiplier demands over 450 gates and consumes 90% of Tensor Core die area!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(kicker), FadeOut(soft_win), FadeOut(right_panel), run_time=0.6)

        # =====================================================================
        # ACT 2: BINARY LONG-MULTIPLICATION & BIT GROWTH (~65s)
        # =====================================================================
        mult_title = Text("Binary Shift-and-Add & Bit Growth",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.TEXT).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(mult_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "How does silicon multiply numbers? It uses binary shift-and-add: multiplying bit-by-bit and shifting left."
            )),
            run_time=0.6
        )
        self.wait(5.0)

        # 4-bit demonstration: 1011 (11) * 1101 (13) = 143 (10001111)
        calc_box = RoundedRectangle(corner_radius=0.18, width=7.4, height=3.8,
                                    stroke_color=th.BORDER, fill_color=th.CARD, fill_opacity=0.95).move_to(UP * 0.45)

        t_op1 = Text("      1 0 1 1   (A = 11)", font=th.MONO, font_size=18, color=th.CYAN_LIGHT)
        t_op2 = Text("   ×  1 1 0 1   (B = 13)", font=th.MONO, font_size=18, color=th.AMBER_LIGHT)
        div_l1 = Line(LEFT * 2.8, RIGHT * 2.8, color=th.BORDER, stroke_width=2.0)

        r0 = Text("      1 0 1 1   (Shift 0: A × B[0])", font=th.MONO, font_size=15, color=th.TEXT)
        r1 = Text("    0 0 0 0     (Shift 1: A × B[1])", font=th.MONO, font_size=15, color=th.FAINT)
        r2 = Text("  1 0 1 1       (Shift 2: A × B[2])", font=th.MONO, font_size=15, color=th.TEXT)
        r3 = Text("1 0 1 1         (Shift 3: A × B[3])", font=th.MONO, font_size=15, color=th.TEXT)
        div_l2 = Line(LEFT * 2.8, RIGHT * 2.8, color=th.BORDER, stroke_width=2.0)

        prod_txt = Text("1 0 0 0 1 1 1 1   (= 143, Exactly 8 bits!)", font=th.MONO, weight=BOLD, font_size=17, color=th.GREEN_LIGHT)

        math_stack = VGroup(t_op1, t_op2, div_l1, r0, r1, r2, r3, div_l2, prod_txt).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(calc_box)

        self.play(Create(calc_box), run_time=0.8)
        self.play(Write(t_op1), Write(t_op2), Create(div_l1), run_time=0.8)
        self.play(FadeIn(r0, shift=LEFT * 0.2), FadeIn(r1, shift=LEFT * 0.2), run_time=0.6)
        self.play(FadeIn(r2, shift=LEFT * 0.2), FadeIn(r3, shift=LEFT * 0.2), run_time=0.6)
        self.play(Create(div_l2), FadeIn(prod_txt), run_time=0.8)

        # Bit growth card below
        bg_card = th.card(11.2, 1.15, stroke=th.AMBER, radius=0.15).next_to(banner, UP, buff=0.22)
        bg_txt = Text("Mathematical Law: Multiplying two N-bit numbers produces a 2N-bit result! (INT8 × INT8 = INT16)",
                      font=th.MONO, weight=BOLD, font_size=13, color=th.AMBER_LIGHT).move_to(bg_card)

        self.play(Create(bg_card), FadeIn(bg_txt), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "Because 4 bits times 4 bits requires 8 bits, an 8-bit multiplier MUST output a 16-bit signed integer to prevent truncation!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(mult_title), FadeOut(calc_box), FadeOut(math_stack), FadeOut(bg_card), FadeOut(bg_txt), run_time=0.6)

        # =====================================================================
        # ACT 3: THE 64 AND GATES & BAUGH-WOOLEY SIGNED TRAP (~70s)
        # =====================================================================
        act3_title = Text("Inside Silicon: 64 AND Gates & The Signed Trap",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.CYAN).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act3_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "In silicon, every partial product bit is an AND gate: 8 x 8 = 64 simultaneous logic gates etched onto the chip."
            )),
            run_time=0.6
        )
        self.wait(5.0)

        # 8x8 Grid of glowing AND gate dots on the left
        dots = VGroup()
        grid_origin = LEFT * 3.4 + UP * 0.7
        for r in range(8):
            for c in range(8):
                col = th.RED if (r == 7 or c == 7) else th.CYAN
                d = Dot(point=grid_origin + RIGHT * (c * 0.45) + DOWN * (r * 0.32), radius=0.07, color=col)
                dots.add(d)

        grid_label = Text("8 × 8 = 64 Bit-Level AND Gates\n(Red: Sign Bit MSB Multipliers)",
                          font=th.MONO, weight=BOLD, font_size=13, color=th.CYAN_LIGHT).next_to(dots, UP, buff=0.25)

        # Right side: The Baugh-Wooley Signed Trap explanation
        trap_card = th.card(5.6, 3.6, stroke=th.RED, radius=0.16).move_to(RIGHT * 3.1 + DOWN * 0.4)
        trap_h = Text("THE SIGNED INT8 TRAP", font=th.SANS, weight=BOLD, font_size=16, color=th.RED_LIGHT).next_to(trap_card.get_top(), DOWN, buff=0.2)
        trap_lines = th.bullets(
            ["Naive multipliers treat MSB as +128",
             "Suppose A = -2 ('b1110) & B = +3",
             "Unsigned treats A as +14:",
             "  14 × 3 = 42 (WRONG! Expected -6)",
             "Fix: Baugh-Wooley Algorithm:",
             "  Invert sign partial products & add 1"],
            color=th.TEXT, font_size=13, bullet_color=th.AMBER, buff=0.18
        ).next_to(trap_h, DOWN, buff=0.2, aligned_edge=LEFT).move_to(trap_card.get_center() + DOWN * 0.15)

        self.play(Create(grid_label), FadeIn(dots), Create(trap_card), FadeIn(trap_h), FadeIn(trap_lines), run_time=1.2)
        self.wait(6.0)

        self.play(
            Transform(banner, th.narration_banner(
                "Because negative numbers have MSB with negative weight (-128), hardware synthesizers use Baugh-Wooley inversion gates!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(act3_title), FadeOut(grid_label), FadeOut(dots), FadeOut(trap_card), FadeOut(trap_h), FadeOut(trap_lines), run_time=0.6)

        # =====================================================================
        # ACT 4: WALLACE TREE REDUCTION & PACHINKO COMPRESSION (~65s)
        # =====================================================================
        tree_title = Text("Wallace-Tree Reduction: Compressing 8 Rows in O(log N)",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.GREEN).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(tree_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "How do we add 8 rows of partial products? Sequential adders are too slow. Wallace Trees compress rows using Carry-Save Adders (CSAs)!"
            )),
            run_time=0.6
        )
        self.wait(5.5)

        # Diagram of Wallace Tree Stages
        tree_box = RoundedRectangle(corner_radius=0.18, width=10.5, height=3.6, stroke_color=th.GREEN, fill_color=th.CARD, fill_opacity=0.95).move_to(UP * 0.3)
        stg1 = Text("Stage 1: 8 Partial Product Rows (64 AND Gates)", font=th.MONO, font_size=14, color=th.CYAN_LIGHT)
        arr1 = Arrow(UP * 0.2, DOWN * 0.2, buff=0.05, color=th.AMBER, stroke_width=2.5)
        stg2 = Text("Stage 2: CSA Compressors (3:2 Reduction) -> 4 Rows", font=th.MONO, font_size=14, color=th.AMBER_LIGHT)
        arr2 = Arrow(UP * 0.2, DOWN * 0.2, buff=0.05, color=th.AMBER, stroke_width=2.5)
        stg3 = Text("Stage 3: CSA Compressors (3:2 Reduction) -> 2 Rows (Sum & Carry)", font=th.MONO, font_size=14, color=th.GREEN_LIGHT)
        arr3 = Arrow(UP * 0.2, DOWN * 0.2, buff=0.05, color=th.GREEN, stroke_width=2.5)
        stg4 = Text("Final Stage: 16-Bit Carry-Propagate Adder (CPA) -> Product [15:0]", font=th.MONO, weight=BOLD, font_size=15, color=th.WHITE)

        tree_flow = VGroup(stg1, arr1, stg2, arr2, stg3, arr3, stg4).arrange(DOWN, buff=0.14).move_to(tree_box)

        self.play(Create(tree_box), FadeIn(tree_flow), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "Wallace Trees reduce 8 rows to 2 rows in logarithmic depth O(log N). The critical path drops from 8 ripple stages to just 4 gate delays!"
            )),
            run_time=0.6
        )
        self.wait(6.5)

        self.play(FadeOut(tree_title), FadeOut(tree_box), FadeOut(tree_flow), run_time=0.6)

        # =====================================================================
        # ACT 5: INTERACTIVE CHECKPOINT & MATH CHALLENGE (~45s)
        # =====================================================================
        act5_title = Text("Architectural Checkpoint: The Asymmetric Corner Case",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.AMBER).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act5_title), run_time=0.8)

        chal_card = th.card(10.5, 3.0, stroke=th.AMBER, radius=0.16).move_to(UP * 0.4)
        c_q = Text("PAUSE & THINK: TWO'S COMPLEMENT ASYMMETRY", font=th.MONO, weight=BOLD, font_size=15, color=th.AMBER_LIGHT)
        c_m1 = Text("What is (-128) × (-128)? Does it fit in 15 bits or 16 bits?", font=th.SANS, font_size=18, color=th.TEXT)
        c_h1 = Text("Hint: (+127) × (+127) = +16,129 (fits in 15 bits: 'b011111100000001).", font=th.MONO, font_size=13, color=th.MUTED)
        chal_grp = VGroup(c_q, c_m1, c_h1).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(chal_card)

        self.play(Create(chal_card), FadeIn(chal_grp), run_time=1.0)
        self.play(
            Transform(banner, th.narration_banner(
                "Pause the video: calculate (-128) * (-128). Why does this exact corner case dictate why the output MUST be 16 bits?"
            )),
            run_time=0.6
        )
        self.wait(7.0)

        ans_card = th.card(10.5, 1.4, stroke=th.GREEN, radius=0.14).next_to(chal_card, DOWN, buff=0.3)
        ans_t1 = Text("(-128) × (-128) = +16,384 = 'b0100000000000000 (Strictly 16 bits!)", font=th.MONO, weight=BOLD, font_size=14, color=th.GREEN_LIGHT)
        ans_t2 = Text("If truncated to 15 bits, 'b100000000000000 flips into -16,384! Output must be 16-bit.", font=th.MONO, font_size=13, color=th.TEXT)
        ans_grp = VGroup(ans_t1, ans_t2).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(ans_card)

        self.play(Create(ans_card), FadeIn(ans_grp), run_time=0.8)
        self.wait(6.5)

        self.play(FadeOut(act5_title), FadeOut(chal_card), FadeOut(chal_grp), FadeOut(ans_card), FadeOut(ans_grp), run_time=0.6)

        # =====================================================================
        # ACT 6: SYNTHESIZABLE SILICON ARCHITECTURE & VERIFICATION (~45s)
        # =====================================================================
        rtl_title = Text("Synthesizable Silicon: rtl/multiplier_int8.sv",
                         font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.CYAN).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(rtl_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "In SystemVerilog, declaring inputs as 'logic signed' instructs the synthesis compiler to build the Baugh-Wooley Wallace Tree."
            )),
            run_time=0.6
        )

        sv_lines = [
            ("module multiplier_int8 #(", th.CYAN),
            ("    parameter int A_WIDTH = 8, B_WIDTH = 8,", th.TEXT),
            ("    localparam int PROD_WIDTH = A_WIDTH + B_WIDTH  // 16 bits", th.AMBER),
            (")(", th.CYAN),
            ("    input  logic signed [A_WIDTH-1:0]    a,", th.TEXT),
            ("    input  logic signed [B_WIDTH-1:0]    b,", th.TEXT),
            ("    output logic signed [PROD_WIDTH-1:0] product", th.GREEN_LIGHT),
            (");", th.CYAN),
            ("    assign product = a * b; // Synthesizes to 64 AND gates + Wallace CSA", th.GREEN),
            ("endmodule", th.CYAN),
        ]
        sv_win = th.code_window(
            sv_lines, title_text="RTL/MULTIPLIER_INT8.SV",
            width=10.2, height=3.2, font_size=th.FONT_TINY, title_color=th.GREEN
        ).move_to(UP * 0.4)

        self.play(Create(sv_win), run_time=1.0)
        self.wait(5.0)

        # Pre-Silicon Checkpoint
        check_card = th.card(10.2, 1.2, stroke=th.GREEN, radius=0.15).move_to(DOWN * 1.5)
        check_txt = Text("✓ Cocotb Python Golden Model: 65,536 Exhaustive Input Pairs Verified (0 Errors, 456 Gates)",
                         font=th.MONO, weight=BOLD, font_size=13, color=th.GREEN_LIGHT).move_to(check_card)

        self.play(Create(check_card), FadeIn(check_txt), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "Next in our AI Hardware journey: Lab 02, where we connect this multiplier to an accumulator and build the MAC unit!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(rtl_title), FadeOut(sv_win), FadeOut(check_card), FadeOut(check_txt), FadeOut(banner), run_time=1.0)
        self.wait(1.0)
