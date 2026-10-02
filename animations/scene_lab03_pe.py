"""
Lab 03: The Memory Wall — Weight-Stationary Processing Element (PE)
A deep, visual-first masterclass on spatial hardware computing in AI accelerators.
Builds bottom-up: The 1,000x Memory Energy Wall -> Internal PE Anatomy ->
Weight-Preload vs Streaming Modes -> Energy Savings Challenge -> Synthesizable RTL.
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


class Lab03ProcessingElement(SiliconCameraRig):
    def construct(self):
        layout = self.layout
        config = HardwareConfig(data_width=8)

        # =====================================================================
        # ACT 1: THE VON NEUMANN MEMORY WALL (~50s)
        # =====================================================================
        kicker, _, _ = th.header(
            "THE MEMORY WALL",
            "Why AI Chips Must Lock Weights in Silicon",
            title_size=th.FONT_TITLE,
            badge_color=th.CYAN
        )
        self.play(FadeIn(kicker, shift=DOWN * 0.3), run_time=1.0)

        banner = th.narration_banner(
            "In modern AI workloads, standard CPUs spend 90% of their energy not computing math, but moving bytes across memory buses."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.8)
        self.wait(5.5)

        # Software Code Window on Left
        py_code = [
            ("# Traditional CPU GEMM Execution", th.MUTED),
            ("for i in range(M):", th.TEXT),
            ("  for j in range(N):", th.TEXT),
            ("    for k in range(K):", th.TEXT),
            ("      # DRAM fetch every single step!", th.RED_LIGHT),
            ("      C[i][j] += A[i][k] * B[k][j];", th.CYAN_LIGHT),
            ("", th.MUTED),
            ("# The Physical Energy Disaster:", th.AMBER),
            ("# Moving 1 byte: 1,000x more energy than computing it!", th.RED),
        ]
        soft_win = th.code_window(
            py_code, title_text="CPU: VON NEUMANN BOTTLENECK",
            width=6.2, height=3.8, font_size=th.FONT_TINY
        ).move_to(LEFT * 3.1 + DOWN * 0.4)

        # Right Panel: Energy Shock Comparison
        m1 = th.metric_card("0.2 pJ", "Silicon 8-Bit MAC", "Energy to compute arithmetic in gates", color=th.GREEN, width=4.8, height=1.7)
        m2 = th.metric_card("200 pJ", "Off-Chip DRAM Fetch", "1,000x Energy Penalty to move 1 byte across PCB!", color=th.RED, width=4.8, height=1.7)
        right_panel = VGroup(m1, m2).arrange(DOWN, buff=th.SPACE_MD).move_to(RIGHT * 3.3 + DOWN * 0.4)

        self.play(Create(soft_win), run_time=1.2)
        self.play(FadeIn(m1, shift=UP * 0.2), FadeIn(m2, shift=UP * 0.2), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "Performing an INT8 MAC takes 0.2 picojoules. But fetching that weight from DRAM burns 200 picojoules: a 1,000x energy penalty!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(kicker), FadeOut(soft_win), FadeOut(right_panel), run_time=0.6)

        # =====================================================================
        # ACT 2: PHYSICAL ENERGY BREAKDOWN BAR CHART (~60s)
        # =====================================================================
        act2_title = Text("The Physics of Silicon: Energy Dissipation Scale",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.RED_LIGHT).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act2_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "Wire length dictates energy consumption. The closer data stays to the transistors, the faster and cooler the chip runs."
            )),
            run_time=0.6
        )
        self.wait(5.0)

        # Animated Horizontal Bar Chart
        bar_box = RoundedRectangle(corner_radius=0.18, width=10.5, height=3.8, stroke_color=th.BORDER, fill_color=th.CARD, fill_opacity=0.95).move_to(UP * 0.3)
        bars_data = [
            ("Off-Chip DRAM Read", 200.0, 7.5, th.RED, "200.0 pJ (1,000x Waste)"),
            ("On-Chip SRAM Buffer", 5.0, 2.8, th.AMBER, "5.0 pJ (25x Cheaper)"),
            ("Local Register (Flip-Flop)", 1.0, 1.4, th.CYAN, "1.0 pJ (In-Place)"),
            ("INT8 MAC Arithmetic", 0.2, 0.7, th.GREEN, "0.2 pJ (Virtually Free)"),
        ]
        bar_group = VGroup()
        for i, (name, val, w, col, desc) in enumerate(bars_data):
            lbl = Text(name, font=th.MONO, font_size=12, color=th.TEXT)
            rect = Rectangle(width=w, height=0.38, fill_color=col, fill_opacity=0.85, stroke_width=0)
            val_txt = Text(desc, font=th.MONO, font_size=11, color=col)
            row = VGroup(lbl, rect, val_txt).arrange(RIGHT, buff=0.25)
            bar_group.add(row)
        bar_group.arrange(DOWN, aligned_edge=LEFT, buff=0.28).move_to(bar_box.get_center())

        self.play(Create(bar_box), FadeIn(bar_group), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "The lesson of silicon physics: never read weights from DRAM twice! Lock them stationary in local registers inside the core."
            )),
            run_time=0.6
        )
        self.wait(6.5)

        self.play(FadeOut(act2_title), FadeOut(bar_box), FadeOut(bar_group), run_time=0.6)

        # =====================================================================
        # ACT 3: INSIDE THE WEIGHT-STATIONARY PE (~70s)
        # =====================================================================
        act3_title = Text("Inside the Weight-Stationary Processing Element (PE)",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.TEXT).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act3_title), run_time=0.8)

        # Outer PE Cell Box
        pe_box = RoundedRectangle(corner_radius=0.22, width=6.2, height=3.6, stroke_color=th.CYAN, stroke_width=3.0, fill_color=th.CARD, fill_opacity=0.95).move_to(UP * 0.35)

        # Internal stationary weight register (Glowing Gold)
        w_reg = RoundedRectangle(corner_radius=0.12, width=2.6, height=0.7, stroke_color=th.AMBER, stroke_width=2.5, fill_color=th.AMBER_DARK, fill_opacity=0.9).move_to(pe_box.get_top() + DOWN * 0.7)
        w_txt = Text("Weight Reg [W = 3]", font=th.MONO, weight=BOLD, font_size=13, color=th.AMBER_LIGHT).move_to(w_reg)

        mult_circle = Circle(radius=0.45, color=th.AMBER, fill_color=th.BG, fill_opacity=1).move_to(pe_box.get_center() + LEFT * 0.5 + DOWN * 0.3)
        m_txt = Text("×", font=th.SANS, weight=BOLD, font_size=26, color=th.AMBER).move_to(mult_circle)

        add_circle = Circle(radius=0.45, color=th.GREEN, fill_color=th.BG, fill_opacity=1).move_to(pe_box.get_center() + RIGHT * 0.6 + DOWN * 0.3)
        a_txt = Text("+", font=th.SANS, weight=BOLD, font_size=26, color=th.GREEN).move_to(add_circle)

        in_a = Arrow(start=pe_box.get_left() + LEFT * 1.6 + UP * 0.1, end=pe_box.get_left() + UP * 0.1, buff=0, color=th.CYAN, stroke_width=4.0)
        lbl_in_a = Text("a_in (West)\n[4]", font=th.MONO, font_size=12, color=th.CYAN_LIGHT).next_to(in_a, UP, buff=0.1)

        out_a = Arrow(start=pe_box.get_right() + UP * 0.1, end=pe_box.get_right() + RIGHT * 1.6 + UP * 0.1, buff=0, color=th.CYAN, stroke_width=4.0)
        lbl_out_a = Text("a_out (East)\n[Hops East]", font=th.MONO, font_size=12, color=th.CYAN_LIGHT).next_to(out_a, UP, buff=0.1)

        in_s = Arrow(start=pe_box.get_top() + UP * 0.8 + RIGHT * 0.8, end=pe_box.get_top() + RIGHT * 0.8, buff=0, color=th.GREEN, stroke_width=4.0)
        lbl_in_s = Text("sum_in (North) [10]", font=th.MONO, font_size=12, color=th.GREEN_LIGHT).next_to(in_s, RIGHT, buff=0.1)

        out_s = Arrow(start=pe_box.get_bottom() + RIGHT * 0.8, end=pe_box.get_bottom() + DOWN * 0.8 + RIGHT * 0.8, buff=0, color=th.GREEN, stroke_width=4.0)
        lbl_out_s = Text("sum_out (South) [22]", font=th.MONO, weight=BOLD, font_size=12, color=th.GREEN_LIGHT).next_to(out_s, RIGHT, buff=0.1)

        pe_cell_grp = VGroup(pe_box, w_reg, w_txt, mult_circle, m_txt, add_circle, a_txt,
                             in_a, lbl_in_a, out_a, lbl_out_a, in_s, lbl_in_s, out_s, lbl_out_s)

        self.play(FadeIn(pe_cell_grp), run_time=1.2)
        self.focus_on(pe_box, buffer_factor=1.55, run_time=th.RATE_NORMAL)

        self.play(
            Transform(banner, th.narration_banner(
                "Every Processing Element contains: 1) Local Weight Register, 2) MAC Engine, 3) Eastward Activation Register, 4) Southward Sum Register."
            )),
            run_time=0.6
        )
        self.wait(6.0)

        # Pulse MAC execution
        p_act = th.packet(color=th.CYAN, radius=0.12).move_to(in_a.get_start())
        p_sum = th.packet(color=th.GREEN, radius=0.12).move_to(in_s.get_start())
        self.play(FadeIn(p_act), FadeIn(p_sum), run_time=0.3)
        self.play(p_act.animate.move_to(mult_circle.get_center()),
                  p_sum.animate.move_to(add_circle.get_center()), run_time=0.8)

        # MAC Flash
        self.play(Flash(mult_circle, color=th.WHITE, line_length=0.3),
                  Flash(add_circle, color=th.WHITE, line_length=0.3), run_time=0.4)

        # Forwarding out
        self.play(p_act.animate.move_to(out_a.get_end()),
                  p_sum.animate.move_to(out_s.get_end()), run_time=0.8)
        self.play(FadeOut(p_act), FadeOut(p_sum), run_time=0.3)

        self.play(
            Transform(banner, th.narration_banner(
                "Activations flow horizontally West to East. Partial sums accumulate vertically North to South. Communication is strictly neighbor-to-neighbor!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(act3_title), FadeOut(pe_cell_grp), run_time=0.6)
        self.reset_camera(run_time=th.RATE_FAST)

        # =====================================================================
        # ACT 4: REGISTER BUDGET & AREA FOOTPRINT (~60s)
        # =====================================================================
        act4_title = Text("PE Silicon Register Budget: 48 Flip-Flops",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.AMBER).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act4_title), run_time=0.8)

        bud_card = th.card(10.5, 3.6, stroke=th.AMBER, radius=0.16).move_to(UP * 0.3)
        b_t = Text("FLIP-FLOP (D-FF) ALLOCATION PER PE:", font=th.MONO, weight=BOLD, font_size=15, color=th.AMBER_LIGHT)
        b1 = Text("• Stationary Weight Register:    8 Flip-Flops (Holds W locked for entire matrix)", font=th.MONO, font_size=13, color=th.TEXT)
        b2 = Text("• Horizontal Activation Latch:   8 Flip-Flops (Buffers West-to-East data hop)", font=th.MONO, font_size=13, color=th.CYAN_LIGHT)
        b3 = Text("• Vertical Partial Sum Latch:   32 Flip-Flops (Buffers North-to-South accumulation)", font=th.MONO, font_size=13, color=th.GREEN_LIGHT)
        b4 = Text("────────────────────────────────────────────────────────────────────────────────", font=th.MONO, font_size=11, color=th.BORDER)
        b5 = Text("TOTAL PER CELL:                48 Flip-Flops + 1 Multiplier + 1 Adder", font=th.MONO, weight=BOLD, font_size=14, color=th.WHITE)
        bud_grp = VGroup(b_t, b1, b2, b3, b4, b5).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(bud_card)

        self.play(Create(bud_card), FadeIn(bud_grp), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "Because wires travel only to adjacent physical neighbors (<100 micrometers), parasitic capacitance is near zero, enabling 1+ GHz clock rates!"
            )),
            run_time=0.6
        )
        self.wait(6.5)

        self.play(FadeOut(act4_title), FadeOut(bud_card), FadeOut(bud_grp), run_time=0.6)

        # =====================================================================
        # ACT 5: INTERACTIVE CHECKPOINT & ENERGY CHALLENGE (~45s)
        # =====================================================================
        act5_title = Text("Architectural Checkpoint: DRAM Energy Savings",
                          font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.AMBER).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(act5_title), run_time=0.8)

        chal_card = th.card(10.5, 3.0, stroke=th.AMBER, radius=0.16).move_to(UP * 0.4)
        c_q = Text("PAUSE & CALCULATE: ENERGY CONSERVATION", font=th.MONO, weight=BOLD, font_size=15, color=th.AMBER_LIGHT)
        c_m1 = Text("For an N = 1024 matrix multiplication with 1024 reuse per weight,", font=th.SANS, font_size=18, color=th.TEXT)
        c_m2 = Text("how much DRAM energy is eliminated by keeping weights stationary?", font=th.SANS, font_size=18, color=th.TEXT)
        chal_grp = VGroup(c_q, c_m1, c_m2).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(chal_card)

        self.play(Create(chal_card), FadeIn(chal_grp), run_time=1.0)
        self.play(
            Transform(banner, th.narration_banner(
                "Pause the video and calculate: 1024 DRAM fetches at 200 pJ each, replaced by 1 preload. What is the total energy reduction?"
            )),
            run_time=0.6
        )
        self.wait(7.0)

        ans_card = th.card(10.5, 1.4, stroke=th.GREEN, radius=0.14).next_to(chal_card, DOWN, buff=0.3)
        ans_t1 = Text("Savings: 1,024 × 200 pJ = ~204,800 pJ saved per weight element!", font=th.MONO, weight=BOLD, font_size=14, color=th.GREEN_LIGHT)
        ans_t2 = Text("Across a 1M-element matrix, this eliminates over 200 Joules per forward pass!", font=th.MONO, font_size=13, color=th.TEXT)
        ans_grp = VGroup(ans_t1, ans_t2).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(ans_card)

        self.play(Create(ans_card), FadeIn(ans_grp), run_time=0.8)
        self.wait(6.5)

        self.play(FadeOut(act5_title), FadeOut(chal_card), FadeOut(chal_grp), FadeOut(ans_card), FadeOut(ans_grp), run_time=0.6)

        # =====================================================================
        # ACT 6: SYNTHESIZABLE SILICON ARCHITECTURE & VERIFICATION (~45s)
        # =====================================================================
        rtl_title = Text("Synthesizable Silicon: rtl/pe.sv",
                         font=th.SANS, weight=BOLD, font_size=th.FONT_SUBHEAD, color=th.CYAN).move_to(layout.hud_anchor(buff=0.5))
        self.play(Write(rtl_title), run_time=0.8)

        self.play(
            Transform(banner, th.narration_banner(
                "Here is the synthesizable Processing Element: weight loading is controlled by 'load_weight', and registers forward data every cycle."
            )),
            run_time=0.6
        )

        sv_lines = [
            ("always_ff @(posedge clk or negedge rst_n) begin", th.CYAN),
            ("    if (!rst_n) begin", th.TEXT),
            ("        weight_reg <= '0; a_out <= '0; sum_out <= '0;", th.AMBER),
            ("    end else begin", th.CYAN),
            ("        if (load_weight) weight_reg <= weight_in; // Preload phase", th.AMBER_LIGHT),
            ("        // Streaming phase: forward activation and accumulate sum", th.MUTED),
            ("        a_out   <= a_in;                                 // Hop East", th.CYAN_LIGHT),
            ("        sum_out <= sum_in + (a_in * weight_reg);         // Stream South", th.GREEN_LIGHT),
            ("    end", th.CYAN),
            ("end", th.CYAN),
        ]
        sv_win = th.code_window(
            sv_lines, title_text="RTL/PE.SV: WEIGHT-STATIONARY CELL",
            width=10.2, height=3.3, font_size=th.FONT_TINY, title_color=th.GREEN
        ).move_to(UP * 0.45)

        self.play(Create(sv_win), run_time=1.0)
        self.wait(5.0)

        # Pre-Silicon Checkpoint
        check_card = th.card(10.2, 1.2, stroke=th.GREEN, radius=0.15).move_to(DOWN * 1.5)
        check_txt = Text("✓ Cocotb Python Golden Model: Multi-cycle Preload & Streaming Pipeline Verified (0 Errors)",
                         font=th.MONO, weight=BOLD, font_size=13, color=th.GREEN_LIGHT).move_to(check_card)

        self.play(Create(check_card), FadeIn(check_txt), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "Next in our AI Hardware journey: Lab 04, where we connect these PEs into a 2D Systolic Wavefront Array!"
            )),
            run_time=0.6
        )
        self.wait(6.0)

        self.play(FadeOut(rtl_title), FadeOut(sv_win), FadeOut(check_card), FadeOut(check_txt), FadeOut(banner), run_time=1.0)
        self.wait(1.0)
