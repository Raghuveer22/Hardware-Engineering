"""
Lab 04: The Systolic Array Matrix Multiplier — Complete 5-to-7 Minute Masterclass
Designed specifically for Computer Science Engineers & Software Developers.

Duration: ~5.5 minutes (335 seconds)
Target Audience: CSE students and software engineers transitioning to AI hardware co-design.

Six-Act Architectural Arc:
  Act 1: The Software Paradox & The Trillion-Operation LLM Scaling Crisis (~50s)
  Act 2: CPU vs GPU vs TPU & The 1,000x Physical Memory Energy Wall (~55s)
  Act 3: Inside the Weight-Stationary Processing Element (PE) Datapath (~55s)
  Act 4: The 2D Systolic Wavefront & The Activation Skewing Paradox (Cycle T0..T4) (~80s)
  Act 5: Architectural Checkpoints & Interactive Mathematical Challenge (~45s)
  Act 6: Pre-Silicon Verification (Cocotb Python + RTL), TPU Scale & Career Roadmap (~50s)
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
    KineticClock,
    LiveOscilloscope,
    LaserPacketStream,
    StageLayout,
    HardwareConfig,
)


class Lab04SystolicArray(SiliconCameraRig):
    def construct(self):
        layout = self.layout
        config = HardwareConfig(array_size=2)

        # =====================================================================
        # ACT 1: THE SOFTWARE PARADOX & THE LLM SCALING CRISIS (~50s)
        # =====================================================================
        kicker, _, _ = th.header(
            "FROM PYTORCH TO SILICON",
            "Why Modern LLMs Demand Custom Hardware",
            title_size=30,
            badge_color=th.CYAN
        )
        self.play(FadeIn(kicker, shift=DOWN * 0.3), run_time=1.0)

        banner = th.narration_banner(
            "Welcome to Hardware AI Acceleration. Today, we bridge the fundamental gap between PyTorch code and physical silicon."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.8)
        self.wait(8.0)

        # Left Panel: Software Code (Python / C++)
        code_lines = [
            ("# PyTorch LLM Self-Attention", th.MUTED),
            ("import torch", th.CYAN),
            ("scores = Q @ K.T / sqrt(d_k)", th.GREEN),
            ("probs  = softmax(scores)", th.AMBER),
            ("output = probs @ V", th.GREEN),
            ("", th.MUTED),
            ("// In C++ / CPU: 3 Nested Loops", th.MUTED),
            ("for (int i=0; i<N; i++)", th.TEXT),
            ("  for (int j=0; j<N; j++)", th.TEXT),
            ("    for (int k=0; k<N; k++)", th.TEXT),
            ("      C[i][j] += A[i][k]*B[k][j];", th.CYAN_LIGHT),
        ]
        soft_win = th.code_window(code_lines, title_text="SOFTWARE: O(N³) NESTED LOOPS",
                                  width=5.8, height=4.3, font_size=13)
        soft_win.move_to(LEFT * 3.3 + DOWN * 0.4)

        # Right Panel: The Scale Disaster
        stat_card1 = th.metric_card("1 Trillion", "Operations per Token",
                                    "For 1M Context Window (LLaMA / Gemini)", color=th.AMBER, width=4.8, height=1.7)
        stat_card2 = th.metric_card("90% Stalled", "Von Neumann Bottleneck",
                                    "CPUs spend 90% time waiting on DRAM transfers", color=th.RED, width=4.8, height=1.7)
        right_panel = VGroup(stat_card1, stat_card2).arrange(DOWN, buff=0.35)
        right_panel.move_to(RIGHT * 3.3 + DOWN * 0.4)

        self.play(Create(soft_win), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "As software engineers, we write matrix multiplications as clean single-line abstractions, like Q times K transpose."
            )),
            run_time=0.6
        )
        self.wait(9.0)

        self.play(FadeIn(stat_card1, shift=UP * 0.2), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "In large language models with one-million-token context windows, a single attention head requires over one trillion operations."
            )),
            run_time=0.6
        )
        self.wait(9.5)

        self.play(FadeIn(stat_card2, shift=UP * 0.2), run_time=0.8)
        self.play(
            Transform(banner, th.narration_banner(
                "On standard CPUs, this causes catastrophic cache thrashing. The processor spends 90% of its power stalling for DRAM memory."
            )),
            run_time=0.6
        )
        self.wait(10.0)

        self.play(
            Transform(banner, th.narration_banner(
                "How do Google TPUs and NVIDIA Tensor Cores solve this? The answer lies in Spatial Hardware Computing."
            )),
            run_time=0.6
        )
        self.wait(9.5)

        self.play(
            FadeOut(kicker), FadeOut(soft_win), FadeOut(right_panel),
            FadeOut(banner), run_time=0.8
        )

        # =====================================================================
        # ACT 2: CPU vs GPU vs TPU & THE 1,000x MEMORY WALL (~55s)
        # =====================================================================
        mem_hdr, _, _ = th.header(
            "THE PHYSICS OF SILICON",
            "The 1,000x Memory Energy Wall",
            title_size=30,
            badge_color=th.RED
        )
        self.play(FadeIn(mem_hdr, shift=DOWN * 0.3), run_time=0.8)

        banner = th.narration_banner(
            "In computer science, we analyze algorithmic Big-O complexity. But in silicon physics, wire distance and energy dictate everything."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.6)
        self.wait(9.5)

        # Energy comparison card
        chart_card = th.card(11.2, 4.0, stroke=th.BORDER, radius=0.2)
        chart_card.move_to(DOWN * 0.45)
        self.play(Create(chart_card), run_time=0.8)

        categories = [
            ("DRAM Read (Off-Chip DRAM / HBM)", "200.0 pJ", 7.2, th.RED, "1,000x Energy Penalty!"),
            ("On-Chip SRAM Buffer (Cache)",     "  5.0 pJ", 2.2, th.AMBER, "25x cheaper than DRAM"),
            ("PE Local Register (Flip-Flop)",   "  1.0 pJ", 0.9, th.CYAN, "Local in-place storage"),
            ("INT8 MAC Arithmetic Operation",   "  0.2 pJ", 0.4, th.GREEN, "The math itself is virtually FREE!"),
        ]

        bar_group = VGroup()
        for i, (name, val_txt, bar_len, col, note) in enumerate(categories):
            lbl = Text(name, font=th.SANS, font_size=14, color=th.TEXT)
            bar = RoundedRectangle(
                corner_radius=0.08, width=bar_len, height=0.35,
                stroke_color=col, fill_color=col, fill_opacity=0.85
            )
            v_t = Text(val_txt, font=th.MONO, font_size=14, weight=BOLD, color=col)
            n_t = Text(note, font=th.SANS, font_size=12, color=th.MUTED)
            row = VGroup(lbl, bar, v_t, n_t).arrange(RIGHT, buff=0.25)
            bar_group.add(row)

        bar_group.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        bar_group.move_to(chart_card.get_center())

        for row in bar_group:
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.7)
            self.wait(5.2)

        self.play(
            Transform(banner, th.narration_banner(
                "Notice the staggering reality: reading one number from DRAM burns 1,000 times more energy than computing it!"
            )),
            run_time=0.6
        )
        self.wait(10.0)

        self.play(
            Transform(banner, th.narration_banner(
                "A CPU moves numbers back and forth over a shared bus on every iteration. To achieve massive AI throughput, we must never re-read weights."
            )),
            run_time=0.6
        )
        self.wait(10.5)

        self.play(
            Transform(banner, th.narration_banner(
                "This fundamental insight gave birth to the Weight-Stationary Systolic Array."
            )),
            run_time=0.6
        )
        self.wait(9.5)

        self.play(
            FadeOut(mem_hdr), FadeOut(chart_card), FadeOut(bar_group),
            FadeOut(banner), run_time=0.8
        )

        # =====================================================================
        # ACT 3: INSIDE THE WEIGHT-STATIONARY PE DATAPATH (~55s)
        # =====================================================================
        pe_hdr, _, _ = th.header(
            "LAB 03 & 04 ARCHITECTURE",
            "Inside the Weight-Stationary Processing Element",
            title_size=30,
            badge_color=th.AMBER
        )
        self.play(FadeIn(pe_hdr, shift=DOWN * 0.3), run_time=0.8)

        banner = th.narration_banner(
            "Let us zoom into the silicon floorplan and inspect a single Processing Element, or P-E."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.6)
        self.wait(8.5)

        # Draw a detailed PE block diagram
        pe_box = th.card(6.2, 4.0, stroke=th.AMBER, radius=0.2, stroke_w=2.5)
        pe_box.move_to(LEFT * 2.5 + DOWN * 0.45)
        pe_tag = Text("PROCESSING ELEMENT [r, c]", font=th.SANS, weight=BOLD, font_size=15, color=th.AMBER_LIGHT)
        pe_tag.next_to(pe_box.get_top(), DOWN, buff=0.25)

        # Sub-blocks inside PE
        w_reg = th.card(1.9, 0.8, stroke=th.AMBER, fill="#291e0a")
        w_reg.move_to(pe_box.get_center() + UP * 0.6 + LEFT * 1.5)
        w_lbl = Text("Weight Reg\n(Locked Stationary)", font=th.MONO, font_size=10, color=th.AMBER_LIGHT, line_spacing=1.1).move_to(w_reg)

        mac_unit = th.card(2.2, 1.2, stroke=th.GREEN, fill="#0c2d1b")
        mac_unit.move_to(pe_box.get_center() + DOWN * 0.45)
        mac_lbl = Text("MAC ENGINE\nsum_out = sum_in + a*w", font=th.MONO, weight=BOLD, font_size=11, color=th.GREEN_LIGHT, line_spacing=1.1).move_to(mac_unit)

        a_ff = th.card(1.6, 0.65, stroke=th.CYAN, fill="#0c2538")
        a_ff.move_to(pe_box.get_right() + LEFT * 1.1 + UP * 0.6)
        a_lbl = Text("East Reg (Act)", font=th.MONO, font_size=11, color=th.CYAN_LIGHT).move_to(a_ff)

        s_ff = th.card(1.6, 0.65, stroke=th.GREEN, fill="#0c2d1b")
        s_ff.move_to(pe_box.get_bottom() + UP * 0.65)
        s_lbl = Text("South Reg (Sum)", font=th.MONO, font_size=11, color=th.GREEN_LIGHT).move_to(s_ff)

        pe_internals = VGroup(pe_box, pe_tag, w_reg, w_lbl, mac_unit, mac_lbl, a_ff, a_lbl, s_ff, s_lbl)

        # Right side: Architecture explanation bullet points
        pe_points = th.bullets([
            "1. Weight Register: Loaded once during weights setup; stays stationary.",
            "2. Activation Input (West): Streams from the left; latches into East register.",
            "3. Partial Sum (North): Enters from top; accumulates with (A × W).",
            "4. Zero Shared Buses: PEs communicate only with immediate physical neighbors.",
            "5. INT8 Arithmetic: 16x less silicon area and 20x less power than FP32.",
        ], color=th.TEXT, font_size=15, bullet_color=th.CYAN, buff=0.22)
        pe_points.move_to(RIGHT * 3.4 + DOWN * 0.45)

        self.play(Create(pe_internals), run_time=1.4)
        self.play(FadeIn(pe_points, shift=LEFT * 0.2), run_time=1.0)

        # Smooth camera dive into the PE internals
        self.focus_on(pe_internals, buffer_factor=1.4, run_time=th.RATE_NORMAL)

        self.play(
            Transform(banner, th.narration_banner(
                "Weights are pre-loaded once and remain locked in local flip-flops. Activations stream East; partial sums stream South."
            )),
            run_time=0.6
        )
        self.wait(9.0)

        # Animate data token arriving and MAC firing using LaserPacketStream
        LaserPacketStream.shoot_token(self, pe_box.get_left() + LEFT * 0.5, mac_unit.get_left(), color=th.CYAN, run_time=0.6)
        LaserPacketStream.shoot_token(self, pe_box.get_top() + UP * 0.4, mac_unit.get_top(), color=th.GREEN, run_time=0.6)

        self.play(mac_unit.animate.set_stroke(th.WHITE, width=3).set_fill(th.GREEN_DARK, opacity=1.0), run_time=0.35)
        self.play(mac_unit.animate.set_stroke(th.GREEN, width=2).set_fill("#0c2d1b", opacity=0.9), run_time=0.35)
        self.wait(6.0)

        self.play(
            Transform(banner, th.narration_banner(
                "Because wires only connect direct neighbors, wire lengths are tiny, allowing chips to clock at gigahertz speeds."
            )),
            run_time=0.6
        )
        self.wait(8.0)

        # Pull camera back to full wide-angle view
        self.play(
            FadeOut(pe_hdr), FadeOut(pe_internals), FadeOut(pe_points),
            FadeOut(banner), run_time=0.8
        )
        self.reset_camera(run_time=th.RATE_FAST)

        # =====================================================================
        # ACT 4: THE 2D SYSTOLIC WAVEFRONT & SKEWING PARADOX (~105s)
        # =====================================================================
        wave_hdr, _, _ = th.header(
            "THE HEARTBEAT OF SILICON",
            "Activation Skewing & The 2D Wavefront",
            title_size=30,
            badge_color=th.GREEN
        )
        self.play(FadeIn(wave_hdr, shift=DOWN * 0.3), run_time=0.8)

        banner = th.narration_banner(
            "Now connect PEs into a 2D mesh. Here we encounter the central architectural puzzle: Activation Skewing."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.6)
        self.wait(9.0)

        # First: Show the NAIVE (Unskewed) Failure to give students the "Aha!" moment!
        fail_card = th.card(10.8, 3.8, stroke=th.RED, radius=0.2)
        fail_card.move_to(DOWN * 0.45)
        fail_title = Text("THE NAIVE ATTEMPT: NO SKEWING (DATA COLLISION)", font=th.SANS, weight=BOLD, font_size=18, color=th.RED_LIGHT)
        fail_title.next_to(fail_card.get_top(), DOWN, buff=0.35)

        fail_bullets = th.bullets([
            "• If Row 0 and Row 1 activations enter at the EXACT same clock cycle (T=1):",
            "• PE(0,0) computes: 1 × 5 = 5 (Partial sum must travel South to PE 1,0).",
            "• But PE(1,0) fires at T=1 simultaneously! Its partial sum from North is 0 (NOT 5)!",
            "• PE(1,0) calculates: 0 + (2 × 7) = 14  ❌ WRONG! (Golden answer is 19).",
            "• Result: The entire neural network outputs garbage. Software synchronization fails in silicon!",
        ], color=th.TEXT, font_size=15, bullet_color=th.RED, buff=0.25)
        fail_bullets.move_to(fail_card.get_center() + DOWN * 0.15)
        fail_group = VGroup(fail_card, fail_title, fail_bullets)

        self.play(Create(fail_group), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "Watch what happens if we feed inputs naively without skewing: PE(1,0) calculates before PE(0,0)'s sum arrives!"
            )),
            run_time=0.6
        )
        self.wait(10.5)

        self.play(
            Transform(banner, th.narration_banner(
                "Because registers have physical propagation latency, software-style instant execution produces total mathematical corruption."
            )),
            run_time=0.6
        )
        self.wait(10.5)

        self.play(FadeOut(fail_group), run_time=0.8)

        # 2x2 Grid Visualization with real numbers
        # Matrix A = [[1, 2]] (1x2 vector), Weight W = [[5, 6], [7, 8]]
        # 2x2 Grid Visualization with real numbers
        # Matrix A = [[1, 2]] (1x2 vector), Weight W = [[5, 6], [7, 8]]
        # Output C = A * W = [1*5 + 2*7, 1*6 + 2*8] = [19, 22]
        # 2x2 Grid Visualization with real numbers
        pe_grid = self._create_2x2_annotated_grid()
        pe_grid.move_to(UP * 0.75 + LEFT * 1.5)

        # Kinetic Clock generator & Live Oscilloscope
        clock = KineticClock(initial_cycle=0)
        ticker_badge = clock.create_ticker_badge()
        ticker_badge.move_to(UP * 3.1 + RIGHT * 3.5)

        scope = LiveOscilloscope(
            signals=[
                ("CLK", [1, 0, 1, 0, 1, 0, 1, 0], th.GREEN),
                ("A_IN", [0, 1, 1, 0, 0, 0, 0, 0], th.CYAN),
                ("PE_00", [0, 0, 1, 0, 0, 0, 0, 0], th.CYAN_LIGHT),
                ("PE_10", [0, 0, 0, 1, 0, 0, 0, 0], th.AMBER),
            ],
            total_cycles=4,
            width=5.2,
            height=2.3
        )
        scope.move_to(DOWN * 0.65 + RIGHT * 3.5)

        self.play(Create(pe_grid, lag_ratio=0.08), FadeIn(ticker_badge), Create(scope), run_time=1.2)

        self.play(
            Transform(banner, th.narration_banner(
                "The Architectural Solution: Input Skew Registers. Row k is delayed by exactly k clock cycles using hardware D flip-flops."
            )),
            run_time=0.6
        )
        self.wait(8.0)

        # ---- CYCLE 1 ----
        clock.advance(self, 1, run_time=0.5)
        self.play(
            scope.set_cursor_cycle(1),
            Transform(banner, th.narration_banner(
                "At Clock 1, activation 1 enters PE(0,0). 1 times 5 equals 5. The partial sum 5 latches into the South register."
            )),
            run_time=0.6
        )
        p00 = self.pe_cells[0][0]
        LaserPacketStream.shoot_token(self, pe_grid.get_left() + UP * 1.0, p00.get_center(), color=th.CYAN, payload_val="1", run_time=0.5)
        self.screen_shake(intensity=0.03, cycles=2, run_time=0.15)
        self.play(
            p00.animate.set_fill(th.CYAN_DARK, opacity=0.9).set_stroke(th.CYAN, width=3.5),
            FadeOut(self.pe_flow_hints[0][0]),
            run_time=0.5
        )
        sum_00 = Text("Sum = 5", font=th.MONO, weight=BOLD, font_size=13, color=th.GREEN_LIGHT).move_to(p00.get_bottom() + UP * 0.25)
        self.play(FadeIn(sum_00), run_time=0.4)
        self.wait(8.0)

        # ---- CYCLE 2 ----
        clock.advance(self, 1, run_time=0.5)
        self.play(
            scope.set_cursor_cycle(2),
            Transform(banner, th.narration_banner(
                "At Clock 2, activation 1 hops East to PE(0,1). Skewed activation 2 enters PE(1,0): 5 + 2*7 = 19! Column 0 is complete!"
            )),
            run_time=0.6
        )
        p01 = self.pe_cells[0][1]
        p10 = self.pe_cells[1][0]
        LaserPacketStream.shoot_token(self, p00.get_center(), p01.get_center(), color=th.CYAN, payload_val="1", run_time=0.5)
        LaserPacketStream.shoot_token(self, pe_grid.get_left() + DOWN * 1.0, p10.get_center(), color=th.AMBER, payload_val="2", run_time=0.5)
        self.screen_shake(intensity=0.03, cycles=2, run_time=0.15)

        self.play(
            p00.animate.set_fill(th.CARD, opacity=0.9).set_stroke(th.BORDER, width=2.0),
            p01.animate.set_fill(th.CYAN_DARK, opacity=0.9).set_stroke(th.CYAN, width=3.5),
            p10.animate.set_fill(th.GREEN_DARK, opacity=0.9).set_stroke(th.GREEN, width=3.5),
            FadeOut(self.pe_flow_hints[0][1]),
            FadeOut(self.pe_flow_hints[1][0]),
            sum_00.animate.move_to(p10.get_top() + DOWN * 0.25).set_color(th.MUTED).set_font_size(11),
            run_time=0.7
        )
        sum_01 = Text("Sum = 6", font=th.MONO, weight=BOLD, font_size=13, color=th.CYAN_LIGHT).move_to(p01.get_bottom() + UP * 0.25)
        sum_10 = Text("DONE: 19", font=th.MONO, weight=BOLD, font_size=13, color=th.GREEN_LIGHT).move_to(p10.get_bottom() + UP * 0.25)
        self.play(FadeIn(sum_01), FadeIn(sum_10), run_time=0.5)
        self.wait(8.5)

        # ---- CYCLE 3 ----
        clock.advance(self, 1, run_time=0.5)
        self.play(
            scope.set_cursor_cycle(3),
            Transform(banner, th.narration_banner(
                "At Clock 3, activation 2 hops East to PE(1,1). Partial sum 6 flows South. 6 + 2*8 = 22! Column 1 is complete!"
            )),
            run_time=0.6
        )
        p11 = self.pe_cells[1][1]
        LaserPacketStream.shoot_token(self, p10.get_center(), p11.get_center(), color=th.AMBER, payload_val="2", run_time=0.5)
        self.screen_shake(intensity=0.03, cycles=2, run_time=0.15)

        self.play(
            p01.animate.set_fill(th.CARD, opacity=0.9).set_stroke(th.BORDER, width=2.0),
            p10.animate.set_fill(th.CARD, opacity=0.9).set_stroke(th.BORDER, width=2.0),
            p11.animate.set_fill(th.GREEN_DARK, opacity=0.9).set_stroke(th.GREEN, width=3.5),
            FadeOut(self.pe_flow_hints[1][1]),
            sum_01.animate.move_to(p11.get_top() + DOWN * 0.25).set_color(th.MUTED).set_font_size(11),
            run_time=0.7
        )
        sum_11 = Text("DONE: 22", font=th.MONO, weight=BOLD, font_size=13, color=th.GREEN_LIGHT).move_to(p11.get_bottom() + UP * 0.25)
        self.play(FadeIn(sum_11), run_time=0.5)
        self.wait(8.5)

        # Result Vector Emergence
        res_card = th.card(6.8, 1.0, stroke=th.GREEN, radius=0.15)
        res_card.next_to(banner, UP, buff=0.22)
        res_text = Text("OUTPUT MATRIX RESULT:  C = [ 19 , 22 ]", font=th.MONO, weight=BOLD, font_size=15, color=th.GREEN_LIGHT)
        res_text.move_to(res_card)
        self.play(Create(res_card), FadeIn(res_text), run_time=0.7)

        self.play(
            Transform(banner, th.narration_banner(
                "Checking our math: 1*5 + 2*7 is 19, and 1*6 + 2*8 is 22. The physical silicon executed the exact dot product!"
            )),
            run_time=0.6
        )
        self.wait(9.0)

        self.play(
            FadeOut(wave_hdr), FadeOut(pe_grid), FadeOut(ticker_badge), FadeOut(scope),

            FadeOut(sum_00), FadeOut(sum_01), FadeOut(sum_10), FadeOut(sum_11),
            FadeOut(res_card), FadeOut(res_text), FadeOut(banner),
            run_time=0.8
        )

        # =====================================================================
        # ACT 5: ARCHITECTURAL CHECKPOINT & INTERACTIVE CHALLENGE (~45s)
        # =====================================================================
        th.checkpoint(
            self,
            "Why is this architecture called 'Systolic'?",
            [
                "Named after medical systole: like the human heart pumping blood",
                "Data pulses through the 2D grid in lockstep on every rising clock edge",
                "Weights are loaded ONCE; activations stream with zero redundant DRAM reads",
            ]
        )

        th.challenge(
            self,
            [
                "Try This Test (The Software Engineer's Challenge):",
                "Given input vector A = [3, 4] and Weight matrix W = [[1, 2], [3, 4]]:",
                "What is the output vector C emerging from the bottom pins?",
            ],
            "C = [ 3*1 + 4*3 , 3*2 + 4*4 ] = [ 15 , 22 ]"
        )

        # =====================================================================
        # ACT 6: PRE-SILICON VERIFICATION, INDUSTRY SCALE & CAREER GAP (~50s)
        # =====================================================================
        scale_hdr, _, _ = th.header(
            "FROM ACADEMIA TO PRODUCTION",
            "Google TPU Scale & Pre-Silicon Verification",
            title_size=30,
            badge_color=th.PURPLE
        )
        self.play(FadeIn(scale_hdr, shift=DOWN * 0.3), run_time=0.8)

        banner = th.narration_banner(
            "In production, Google TPUs scale this exact architecture to massive 128x128 arrays, performing 16,384 MACs per cycle."
        )
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.6)
        self.wait(9.0)

        # Left Panel: Cocotb Python Verification Code
        cocotb_lines = [
            ("# Pre-Silicon Python Cocotb Test", th.MUTED),
            ("@cocotb.test()", th.AMBER),
            ("async def test_wavefront(dut):", th.CYAN_LIGHT),
            ("  # Start cycle-accurate clock", th.MUTED),
            ("  cocotb.start_soon(Clock(dut.clk, 10, 'ns').start())", th.TEXT),
            ("  # Load weights into PE registers", th.MUTED),
            ("  await load_weights(dut, W)", th.GREEN),
            ("  # Stream input activations", th.MUTED),
            ("  await stream_row_skewed(dut, A)", th.CYAN),
            ("  # Assert bit-exact PyTorch match!", th.MUTED),
            ("  assert dut.c_out.value == np.dot(A, W)", th.GREEN_LIGHT),
        ]
        coco_win = th.code_window(cocotb_lines, title_text="PRE-SILICON COCOTB PYTHON TEST",
                                  width=5.8, height=4.2, font_size=12, title_color=th.GREEN_LIGHT)
        coco_win.move_to(LEFT * 3.3 + UP * 0.15)

        # Right Panel: Industry Specs Card
        tpu_card = th.card(5.2, 4.2, stroke=th.PURPLE, radius=0.2)
        tpu_card.move_to(RIGHT * 3.3 + UP * 0.15)
        tpu_points = th.bullets([
            "• Google TPU v5 MXU: 128 × 128 PEs = 16,384 MACs/clk",
            "• Latency: 3N - 2 cycles (382 clks for N=128)",
            "• Zero DRAM re-reads: Weights stay locked",
            "• Pre-Silicon Verified in SystemVerilog (rtl/pe.sv)",
            "• The $500k HW/SW Co-Design Talent Frontier",
        ], color=th.TEXT, font_size=13, bullet_color=th.PURPLE_LIGHT, buff=0.26)
        tpu_points.move_to(tpu_card.get_center())

        self.play(Create(coco_win), run_time=1.2)
        self.play(
            Transform(banner, th.narration_banner(
                "Because chip tape-outs cost $50M+, hardware teams verify everything pre-silicon using Python Cocotb testbenches driving SystemVerilog."
            )),
            run_time=0.6
        )
        self.wait(10.5)

        self.play(Create(tpu_card), FadeIn(tpu_points, shift=UP * 0.2), run_time=1.0)
        self.play(
            Transform(banner, th.narration_banner(
                "Notice how software engineers write verification tests in native Python, asserting bit-exact matches against PyTorch and NumPy."
            )),
            run_time=0.6
        )
        self.wait(10.5)

        self.play(
            Transform(banner, th.narration_banner(
                "The industry faces a massive talent shortage: bridging SW and HW places you in the highest tier of AI engineering."
            )),
            run_time=0.6
        )
        self.wait(10.0)

        self.play(
            FadeOut(scale_hdr), FadeOut(coco_win), FadeOut(tpu_card), FadeOut(tpu_points),
            FadeOut(banner), run_time=0.8
        )

        # Closing Call to Action
        th.recap(
            self,
            "Your Next Step: Run the Pre-Silicon Testbench",
            [
                "1. Open rtl/systolic_array.sv and tests/test_systolic_array.py",
                "2. Run the cycle-accurate verification: python labs/run_lab.py --lab 04",
                "3. View the live 2D wavefront in your browser: python visualizer/serve.py",
                "4. Synthesize to physical logic gates with Yosys: python synthesis/synthesize.py",
                "Next Lesson: Lab 05 — Hardware Square Root & Attention Scaling (1/sqrt(d_k))",
            ],
            stroke=th.GREEN,
            title_color=th.GREEN_LIGHT,
            card_w=11.2,
            wait=8.0
        )

    # -------------------------------------------------------------------------
    # HELPER BUILDERS
    # -------------------------------------------------------------------------
    def _create_2x2_annotated_grid(self):
        """Construct a labeled 2x2 PE grid with internal weight and position tags."""
        weights = [["5", "6"], ["7", "8"]]
        cells = []
        flow_hints = []
        grid = VGroup()
        spacing = 2.05

        for r in range(2):
            row = []
            f_row = []
            for c in range(2):
                box = th.card(1.95, 1.65, stroke=th.BORDER, stroke_w=2.0, radius=0.16)
                box.move_to(np.array([(c - 0.5) * spacing, -(r - 0.5) * spacing, 0]))

                pe_lbl = Text(f"PE [{r},{c}]", font=th.SANS, weight=BOLD, font_size=12, color=th.MUTED)
                pe_lbl.move_to(box.get_top() + DOWN * 0.22)

                w_txt = Text(f"Weight = {weights[r][c]}", font=th.MONO, weight=BOLD, font_size=14, color=th.AMBER_LIGHT)
                w_txt.move_to(box.get_center())

                flow_hint = Text("↓ Sum  → Act", font=th.MONO, font_size=10, color=th.FAINT)
                flow_hint.move_to(box.get_bottom() + UP * 0.22)

                pe_unit = VGroup(box, pe_lbl, w_txt, flow_hint)
                grid.add(pe_unit)
                row.append(box)
                f_row.append(flow_hint)
            cells.append(row)
            flow_hints.append(f_row)

        self.pe_cells = cells
        self.pe_flow_hints = flow_hints

        # Annotations on the outside: Input rows on the West, Weight column headers
        row0_in = Text("Row 0: [1] (Delay 0)", font=th.MONO, font_size=12, color=th.CYAN)
        row0_in.next_to(grid, LEFT, buff=0.6).shift(UP * 1.0)

        row1_in = Text("Row 1: [2] (Delay 1 cycle)", font=th.MONO, font_size=12, color=th.AMBER)
        row1_in.next_to(grid, LEFT, buff=0.6).shift(DOWN * 1.0)

        arr0 = Arrow(row0_in.get_right(), cells[0][0].get_left(), buff=0.12, color=th.CYAN)
        arr1 = Arrow(row1_in.get_right(), cells[1][0].get_left(), buff=0.12, color=th.AMBER)

        col0_lbl = Text("Col 0 (Out: C₀)", font=th.MONO, font_size=12, color=th.GREEN_LIGHT)
        col0_lbl.next_to(cells[1][0], DOWN, buff=0.22)
        col1_lbl = Text("Col 1 (Out: C₁)", font=th.MONO, font_size=12, color=th.GREEN_LIGHT)
        col1_lbl.next_to(cells[1][1], DOWN, buff=0.22)

        full_assembly = VGroup(grid, row0_in, row1_in, arr0, arr1, col0_lbl, col1_lbl)
        return full_assembly
