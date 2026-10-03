"""
Lab 00-Prep: Hardware Thinking Primer for Software & AI Engineers
Bridging the Gap from Python & PyTorch to Synthesizable Silicon Gates.

Tailored for Software Engineers (3Blue1Brown Visual Standard):
- Act 0: The Trinity — Program, Gate, and Clock Wave
- Act 1: The Death of the Program Counter (Sequential Software vs 100% Concurrent Silicon)
- Act 2: The Pre-Silicon Memory Energy Wall (200 pJ DRAM vs 0.2 pJ MAC)
- Act 3: The Golden Rule: Blocking (=) vs Non-Blocking (<=) Shift Register Pipeline
- Act 4: Host-to-Device Interconnect: From PyTorch to PCIe DMA & MMIO Doorbells
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
    KineticSiliconScene,
    KineticClock,
    MemoryEnergyBar,
    HardwareConfig,
    TextRole,
    SemanticText,
    SemanticMath,
    HStack,
    VStack,
    ConstraintAnchor,
    PinProbe,
    fit_to_bounds,
)


class Lab00PrepPrimer(KineticSiliconScene):
    def construct(self):
        clock = KineticClock(initial_cycle=0)

        # Ambient Clock HUD at top right (compact)
        ticker = clock.create_ticker_badge(prefix="CLK: T = ", color=th.CYAN_LIGHT)
        ticker.to_corner(UR, buff=0.25)
        self.add(ticker)

        # =====================================================================
        # ACT 0: PRELORE — THE TRINITY: PROGRAM, GATE, CLOCK
        # =====================================================================
        prelore_narration = (
            "Before we open the silicon, let's name three ideas every software engineer already knows. "
            "A program is just an ordered list of instructions. A logic gate is a tiny switch that does exactly one "
            "arithmetic operation, like add or multiply. And a clock is the heartbeat that advances the whole circuit one step at a time."
        )
        with self.stage("PRIMER", "The Foundations of Silicon", "Program · Gate · Clock", narration=prelore_narration) as st:
            with self.voiceover(prelore_narration) as trk:
                # 3b1b style: visual representations rather than corporate cards!
                # 1. Program: An instruction tape with a glowing pointer
                prog_label = Text("PROGRAM", font=th.SANS, weight=BOLD, font_size=16, color=th.CYAN)
                tape_rects = VGroup(*[
                    RoundedRectangle(corner_radius=0.06, width=2.4, height=0.5, stroke_color=th.BORDER, stroke_width=1.5, fill_color="#0d1525", fill_opacity=0.9)
                    for _ in range(3)
                ]).arrange(DOWN, buff=0.1)
                tape_code = VGroup(
                    Text("1: a = x + y", font=th.MONO, font_size=12, color=th.TEXT),
                    Text("2: b = z * w", font=th.MONO, font_size=12, color=th.MUTED),
                    Text("3: out = a + b", font=th.MONO, font_size=12, color=th.MUTED),
                )
                for r, c in zip(tape_rects, tape_code):
                    c.move_to(r)
                pointer = Triangle(color=th.CYAN_LIGHT, fill_opacity=1.0).scale(0.09).rotate(-PI/2)
                pointer.next_to(tape_rects[0], LEFT, buff=0.12)
                prog_group = VGroup(prog_label, tape_rects, tape_code, pointer).arrange(DOWN, buff=0.18)

                # 2. Gate: A stylized arithmetic operator with glowing inputs and output
                gate_label = Text("LOGIC GATE", font=th.SANS, weight=BOLD, font_size=16, color=th.GREEN)
                gate_circle = Circle(radius=0.7, color=th.GREEN, stroke_width=2.5, fill_color="#072213", fill_opacity=0.85)
                gate_sym = MathTex(r"\mathbf{\times}", color=th.GREEN_LIGHT).scale(1.1).move_to(gate_circle)
                in_wire1 = Line(LEFT * 1.4 + UP * 0.4, LEFT * 0.7 + UP * 0.4, color=th.CYAN_LIGHT, stroke_width=2.5)
                in_wire2 = Line(LEFT * 1.4 + DOWN * 0.4, LEFT * 0.7 + DOWN * 0.4, color=th.CYAN_LIGHT, stroke_width=2.5)
                out_wire = Line(RIGHT * 0.7, RIGHT * 1.4, color=th.AMBER_LIGHT, stroke_width=2.5)
                gate_in1_lbl = Text("A", font=th.MONO, font_size=12, color=th.CYAN_LIGHT).next_to(in_wire1, LEFT, buff=0.08)
                gate_in2_lbl = Text("B", font=th.MONO, font_size=12, color=th.CYAN_LIGHT).next_to(in_wire2, LEFT, buff=0.08)
                gate_out_lbl = Text("Y", font=th.MONO, font_size=12, color=th.AMBER_LIGHT).next_to(out_wire, RIGHT, buff=0.08)
                gate_wires = VGroup(in_wire1, in_wire2, out_wire, gate_in1_lbl, gate_in2_lbl, gate_out_lbl)
                gate_group = VGroup(gate_label, VGroup(gate_circle, gate_sym, gate_wires)).arrange(DOWN, buff=0.25)

                # 3. Clock: A continuous living square wave
                clock_label = Text("CLOCK", font=th.SANS, weight=BOLD, font_size=16, color=th.AMBER)
                wave_path = VGroup()
                for i in range(4):
                    x0 = i * 0.65
                    wave_path.add(
                        Line(np.array([x0, 0, 0]), np.array([x0 + 0.32, 0, 0]), color=th.AMBER, stroke_width=2.5),
                        Line(np.array([x0 + 0.32, 0, 0]), np.array([x0 + 0.32, 0.7, 0]), color=th.AMBER_LIGHT, stroke_width=3.0),
                        Line(np.array([x0 + 0.32, 0.7, 0]), np.array([x0 + 0.65, 0.7, 0]), color=th.AMBER, stroke_width=2.5),
                        Line(np.array([x0 + 0.65, 0.7, 0]), np.array([x0 + 0.65, 0, 0]), color=th.AMBER, stroke_width=2.5),
                    )
                wave_path.center()
                pulse_dot = Dot(wave_path[0].get_start(), radius=0.08, color=th.AMBER_LIGHT)
                clock_sub = Text("Advances 1 step per tick", font=th.MONO, font_size=11, color=th.MUTED)
                clock_group = VGroup(clock_label, wave_path, clock_sub).arrange(DOWN, buff=0.2)

                trinity = HStack(prog_group, gate_group, clock_group, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(trinity)

                # Flowing choreography
                self.play(FadeIn(prog_group, shift=UP * 0.2), run_time=0.6)
                self.play(FadeIn(gate_group, shift=UP * 0.2), run_time=0.6)
                self.play(FadeIn(clock_group, shift=UP * 0.2), run_time=0.6)

                # Pulse and step the tape
                self.play(
                    pointer.animate.next_to(tape_rects[1], LEFT, buff=0.12),
                    tape_code[1].animate.set_color(th.CYAN_LIGHT),
                    tape_code[0].animate.set_color(th.MUTED),
                    gate_circle.animate.set_stroke(color=th.WHITE, width=4.0),
                    run_time=0.8
                )
                self.play(
                    pointer.animate.next_to(tape_rects[2], LEFT, buff=0.12),
                    tape_code[2].animate.set_color(th.CYAN_LIGHT),
                    tape_code[1].animate.set_color(th.MUTED),
                    gate_circle.animate.set_stroke(color=th.GREEN, width=2.5),
                    run_time=0.8
                )
                self.wait(max(0.3, trk.duration - 2.8))
                st.takeaway("Program + Gate + Clock = everything you are about to see.", wait=1.2)

        # =====================================================================
        # ACT 1: THE DEATH OF THE PROGRAM COUNTER
        # =====================================================================
        act1_narration = (
            "In software, one instruction runs at a time, stepped by the Program Counter—a pointer that moves line by line. "
            "Silicon has no Program Counter. Every gate fires the instant its inputs are ready, all at once. "
            "For y equals (a+b) times (c+d), both adders and the multiplier light up in the same picosecond."
        )
        with self.stage("ACT 1", "The Death of the Program Counter", "Sequential Software vs 100% Concurrent Silicon", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                # Top equation with color-matched terms
                math_eq = MathTex(
                    r"y", r"=", r"(a + b)", r"\times", r"(c + d)",
                    font_size=38
                ).to_edge(UP, buff=1.2)
                math_eq[0].set_color(th.GREEN_LIGHT)
                math_eq[2].set_color(th.CYAN)
                math_eq[3].set_color(th.WHITE)
                math_eq[4].set_color(th.AMBER)
                st.add(math_eq)
                self.play(Write(math_eq), run_time=0.8)

                # Left side: Sequential CPU Execution Pipeline
                cpu_title = Text("SOFTWARE: SEQUENTIAL CPU", font=th.MONO, weight=BOLD, font_size=15, color=th.AMBER)
                instr_lines = [
                    "0x00:  t1 = a + b    # Cycle 1",
                    "0x04:  t2 = c + d    # Cycle 2",
                    "0x08:  y  = t1 * t2  # Cycle 3",
                ]
                cpu_boxes = VGroup()
                for il in instr_lines:
                    b_rect = RoundedRectangle(corner_radius=0.08, width=4.8, height=0.58, stroke_color=th.BORDER, stroke_width=1.5, fill_color="#0e1526", fill_opacity=0.95)
                    b_txt = Text(il, font=th.MONO, font_size=12, color=th.TEXT)
                    b_txt.move_to(b_rect)
                    cpu_boxes.add(VGroup(b_rect, b_txt))
                cpu_boxes.arrange(DOWN, buff=0.15)
                
                pc_ptr = Arrow(LEFT * 0.6, ORIGIN, color=th.AMBER_LIGHT, stroke_width=3.5, max_tip_length_to_length_ratio=0.3)
                pc_lbl = Text("PC", font=th.MONO, weight=BOLD, font_size=12, color=th.AMBER_LIGHT).next_to(pc_ptr, LEFT, buff=0.06)
                pc_marker = VGroup(pc_ptr, pc_lbl).next_to(cpu_boxes[0], LEFT, buff=0.1)

                cpu_panel = VGroup(cpu_title, VGroup(cpu_boxes, pc_marker)).arrange(DOWN, buff=0.25)
                cpu_panel.move_to(LEFT * 3.4 + DOWN * 0.5)

                # Right side: Concurrent Hardware Dataflow Graph
                hw_title = Text("SILICON: CONCURRENT DATAFLOW", font=th.MONO, weight=BOLD, font_size=15, color=th.CYAN)
                
                # Two adders side-by-side
                add1 = VGroup(
                    Circle(radius=0.55, color=th.CYAN, stroke_width=2.5, fill_color="#091b2e", fill_opacity=0.9),
                    MathTex(r"+", color=th.CYAN_LIGHT, font_size=32)
                )
                add1[1].move_to(add1[0])
                add1_lbl = Text("ADDER 1", font=th.MONO, font_size=11, color=th.CYAN).next_to(add1, UP, buff=0.08)
                add1_unit = VGroup(add1, add1_lbl).move_to(UP * 0.8 + LEFT * 1.3)

                add2 = VGroup(
                    Circle(radius=0.55, color=th.AMBER, stroke_width=2.5, fill_color="#1d1506", fill_opacity=0.9),
                    MathTex(r"+", color=th.AMBER_LIGHT, font_size=32)
                )
                add2[1].move_to(add2[0])
                add2_lbl = Text("ADDER 2", font=th.MONO, font_size=11, color=th.AMBER).next_to(add2, UP, buff=0.08)
                add2_unit = VGroup(add2, add2_lbl).move_to(UP * 0.8 + RIGHT * 1.3)

                # Multiplier below
                mult = VGroup(
                    Circle(radius=0.6, color=th.GREEN, stroke_width=2.5, fill_color="#072213", fill_opacity=0.9),
                    MathTex(r"\times", color=th.GREEN_LIGHT, font_size=34)
                )
                mult[1].move_to(mult[0])
                mult_lbl = Text("MULTIPLIER", font=th.MONO, font_size=11, color=th.GREEN).next_to(mult, DOWN, buff=0.08)
                mult_unit = VGroup(mult, mult_lbl).move_to(DOWN * 1.1)

                w_a1_m = Arrow(add1[0].get_bottom(), mult[0].get_top() + LEFT * 0.3, color=th.CYAN, stroke_width=2.5, buff=0.08)
                w_a2_m = Arrow(add2[0].get_bottom(), mult[0].get_top() + RIGHT * 0.3, color=th.AMBER, stroke_width=2.5, buff=0.08)

                hw_circuit = VGroup(add1_unit, add2_unit, mult_unit, w_a1_m, w_a2_m)
                hw_panel = VGroup(hw_title, hw_circuit).arrange(DOWN, buff=0.25)
                hw_panel.move_to(RIGHT * 3.4 + DOWN * 0.5)

                st.add(cpu_panel, hw_panel)
                self.play(FadeIn(cpu_panel, shift=LEFT * 0.2), FadeIn(hw_panel, shift=RIGHT * 0.2), run_time=0.9)

                # Visual Execution Contrast:
                # Step 1: In CPU, only Line 1 executes. In Silicon, BOTH Adders light up simultaneously!
                pulse1 = Dot(radius=0.1, color=th.CYAN_LIGHT).move_to(add1[0])
                pulse2 = Dot(radius=0.1, color=th.AMBER_LIGHT).move_to(add2[0])
                
                self.play(
                    pc_marker.animate.next_to(cpu_boxes[0], LEFT, buff=0.1),
                    cpu_boxes[0][0].animate.set_stroke(color=th.AMBER, width=2.5),
                    add1[0].animate.set_stroke(color=th.WHITE, width=4.0),
                    add2[0].animate.set_stroke(color=th.WHITE, width=4.0),
                    run_time=0.7
                )
                clock.advance(self, delta_cycles=1, run_time=0.3)

                # Step 2: CPU moves to Line 2 (Cycle 2). Silicon streams both sums directly into Multiplier!
                self.play(
                    pc_marker.animate.next_to(cpu_boxes[1], LEFT, buff=0.1),
                    cpu_boxes[0][0].animate.set_stroke(color=th.BORDER, width=1.5),
                    cpu_boxes[1][0].animate.set_stroke(color=th.AMBER, width=2.5),
                    add1[0].animate.set_stroke(color=th.CYAN, width=2.5),
                    add2[0].animate.set_stroke(color=th.AMBER, width=2.5),
                    mult[0].animate.set_stroke(color=th.GREEN_LIGHT, width=4.0),
                    run_time=0.7
                )
                clock.advance(self, delta_cycles=1, run_time=0.3)

                # Step 3: CPU finishes Line 3 (Cycle 3).
                self.play(
                    pc_marker.animate.next_to(cpu_boxes[2], LEFT, buff=0.1),
                    cpu_boxes[1][0].animate.set_stroke(color=th.BORDER, width=1.5),
                    cpu_boxes[2][0].animate.set_stroke(color=th.GREEN, width=2.5),
                    run_time=0.6
                )
                clock.advance(self, delta_cycles=1, run_time=0.3)
                self.wait(max(0.3, trk.duration - 3.5))
                st.takeaway("Software waits in line. Silicon runs every gate at once.", wait=1.2)

        # =====================================================================
        # ACT 2: PRE-SILICON MEMORY ENERGY HIERARCHY
        # =====================================================================
        act2_narration = (
            "Now the catch: moving data is far more expensive than computing it. "
            "An INT8 multiply-accumulate burns just 0.2 picojoules, but fetching one byte from off-chip DRAM costs 200 picojoules—"
            "a thousand times more. That energy wall is why accelerators pin weights inside the chip, right next to the math."
        )
        with self.stage("ACT 2", "Memory Energy Hierarchy", "The Physical 1,000× Cost of Data Movement", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                # 3b1b style: Dynamic visual scale comparison with physical sparks and towers
                # Left: ALU MAC spark
                mac_box = RoundedRectangle(corner_radius=0.12, width=3.4, height=4.2, stroke_color=th.GREEN, stroke_width=2.0, fill_color="#071b11", fill_opacity=0.9)
                mac_title = Text("ON-CHIP COMPUTE", font=th.MONO, weight=BOLD, font_size=14, color=th.GREEN)
                mac_energy = Text("0.2 pJ", font=th.SANS, weight=BOLD, font_size=32, color=th.GREEN_LIGHT)
                mac_op = Text("INT8 MAC Operation", font=th.MONO, font_size=12, color=th.TEXT)
                mac_spark = Dot(radius=0.12, color=th.GREEN_LIGHT)
                mac_spark_halo = Circle(radius=0.28, color=th.GREEN, stroke_width=1.5, fill_opacity=0.2)
                mac_visual = VGroup(mac_spark_halo, mac_spark)
                mac_content = VStack(mac_title, mac_energy, mac_op, mac_visual, gap=th.SPACE_SM).move_to(mac_box)
                mac_group = VGroup(mac_box, mac_content).move_to(LEFT * 4.2 + DOWN * 0.2)

                # Center: On-chip SRAM Buffer
                sram_box = RoundedRectangle(corner_radius=0.12, width=3.4, height=4.2, stroke_color=th.CYAN, stroke_width=2.0, fill_color="#091b2e", fill_opacity=0.9)
                sram_title = Text("ON-CHIP SRAM", font=th.MONO, weight=BOLD, font_size=14, color=th.CYAN)
                sram_energy = Text("1.0 pJ", font=th.SANS, weight=BOLD, font_size=32, color=th.CYAN_LIGHT)
                sram_op = Text("SRAM Cache Fetch", font=th.MONO, font_size=12, color=th.TEXT)
                sram_rel = Text("5× Compute Energy", font=th.MONO, font_size=11, color=th.CYAN)
                sram_content = VStack(sram_title, sram_energy, sram_op, sram_rel, gap=th.SPACE_SM).move_to(sram_box)
                sram_group = VGroup(sram_box, sram_content).move_to(DOWN * 0.2)

                # Right: Off-Chip DRAM Monster
                dram_box = RoundedRectangle(corner_radius=0.12, width=3.8, height=4.2, stroke_color=th.RED, stroke_width=2.0, fill_color="#200a0a", fill_opacity=0.9)
                dram_title = Text("OFF-CHIP DRAM", font=th.MONO, weight=BOLD, font_size=14, color=th.RED)
                dram_energy = Text("200.0 pJ", font=th.SANS, weight=BOLD, font_size=32, color=th.RED_LIGHT)
                dram_op = Text("DDR / HBM Bus Read", font=th.MONO, font_size=12, color=th.TEXT)
                dram_factor = Text("1,000× ENERGY WALL!", font=th.MONO, weight=BOLD, font_size=13, color=th.AMBER_LIGHT)
                dram_content = VStack(dram_title, dram_energy, dram_op, dram_factor, gap=th.SPACE_SM).move_to(dram_box)
                dram_group = VGroup(dram_box, dram_content).move_to(RIGHT * 4.2 + DOWN * 0.2)

                st.add(mac_group, sram_group, dram_group)

                self.play(FadeIn(mac_group, shift=UP * 0.2), run_time=0.6)
                self.play(FadeIn(sram_group, shift=UP * 0.2), run_time=0.6)
                self.play(FadeIn(dram_group, shift=UP * 0.2), run_time=0.6)

                # Dramatic 1000x explosion visual
                arrow_1000x = CurvedArrow(mac_box.get_top() + UP * 0.1, dram_box.get_top() + UP * 0.1, color=th.AMBER, angle=-TAU/6)
                tag_1000x = Text("1,000× Energy Disparity", font=th.SANS, weight=BOLD, font_size=16, color=th.AMBER_LIGHT).next_to(arrow_1000x, UP, buff=0.1)
                st.add(arrow_1000x, tag_1000x)

                self.play(Create(arrow_1000x), Write(tag_1000x), dram_box.animate.set_stroke(color=th.RED_LIGHT, width=3.5), run_time=0.9)
                self.screen_shake(intensity=0.03, cycles=2, run_time=0.25)
                self.wait(max(0.3, trk.duration - 2.9))
                st.takeaway("Compute is nearly free. Moving data is the real cost.", wait=1.2)

        # =====================================================================
        # ACT 3: THE GOLDEN RULE: BLOCKING (=) VS NON-BLOCKING (<=)
        # =====================================================================
        act3_narration = (
            "Here is the number one bug software engineers write when they first touch RTL. "
            "Blocking equals executes one statement after another, like C++, so a pipeline collapses into a single register. "
            "Non-blocking samples every right-hand side at once, exactly like Python tuple unpacking, "
            "and commits them all in parallel."
        )
        with self.stage("ACT 3", "The Golden Rule: = vs <=", "Blocking vs Non-Blocking Shift Register Pipeline", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                # Left: Broken Blocking (=) with collapsed wire visualization
                block_title = Text("BLOCKING (=): COLLAPSED WIRE", font=th.MONO, weight=BOLD, font_size=13, color=th.RED)
                b_code = VGroup(
                    Text("always_ff @(posedge clk) begin", font=th.MONO, font_size=11, color=th.MUTED),
                    Text("    b = a;  // B gets A immediately", font=th.MONO, font_size=11, color=th.TEXT),
                    Text("    c = b;  // C gets NEW B (=A)!", font=th.MONO, font_size=11, color=th.RED_LIGHT),
                    Text("end", font=th.MONO, font_size=11, color=th.MUTED),
                ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)

                # Visual register cells: A single collapsed register
                reg_b1 = RoundedRectangle(corner_radius=0.08, width=1.6, height=1.0, stroke_color=th.RED, stroke_width=2.0, fill_color="#180b0b", fill_opacity=0.9)
                reg_b1_lbl = Text("Reg B\n(val=A)", font=th.MONO, font_size=11, color=th.RED_LIGHT).move_to(reg_b1)
                reg_c1 = RoundedRectangle(corner_radius=0.08, width=1.6, height=1.0, stroke_color=th.RED, stroke_width=2.0, fill_color="#180b0b", fill_opacity=0.9)
                reg_c1_lbl = Text("Reg C\n(val=A!)", font=th.MONO, font_size=11, color=th.RED_LIGHT).move_to(reg_c1)
                reg_collapse_wire = Arrow(reg_b1.get_right(), reg_c1.get_left(), buff=0.06, color=th.RED, stroke_width=3.0)
                tag_broken = Text("1 CYCLE COLLAPSE: Both get A!", font=th.MONO, weight=BOLD, font_size=11, color=th.RED)
                
                left_schem = VGroup(HStack(VGroup(reg_b1, reg_b1_lbl), reg_collapse_wire, VGroup(reg_c1, reg_c1_lbl), gap=0.1), tag_broken).arrange(DOWN, buff=0.15)
                left_panel = VGroup(block_title, b_code, left_schem).arrange(DOWN, buff=0.25).move_to(LEFT * 3.4 + DOWN * 0.2)

                # Right: Non-Blocking (<=): True 2-Stage Shift Register
                nonblock_title = Text("NON-BLOCKING (<=): PARALLEL LATCH", font=th.MONO, weight=BOLD, font_size=13, color=th.GREEN)
                nb_code = VGroup(
                    Text("always_ff @(posedge clk) begin", font=th.MONO, font_size=11, color=th.MUTED),
                    Text("    b <= a; // B samples old A", font=th.MONO, font_size=11, color=th.TEXT),
                    Text("    c <= b; // C samples old B!", font=th.MONO, font_size=11, color=th.GREEN_LIGHT),
                    Text("end", font=th.MONO, font_size=11, color=th.MUTED),
                ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)

                reg_b2 = RoundedRectangle(corner_radius=0.08, width=1.6, height=1.0, stroke_color=th.GREEN, stroke_width=2.0, fill_color="#071b11", fill_opacity=0.9)
                reg_b2_lbl = Text("DFF 1\n(B <= A)", font=th.MONO, font_size=11, color=th.GREEN_LIGHT).move_to(reg_b2)
                reg_c2 = RoundedRectangle(corner_radius=0.08, width=1.6, height=1.0, stroke_color=th.GREEN, stroke_width=2.0, fill_color="#071b11", fill_opacity=0.9)
                reg_c2_lbl = Text("DFF 2\n(C <= old B)", font=th.MONO, font_size=11, color=th.GREEN_LIGHT).move_to(reg_c2)
                reg_pipe_wire = Arrow(reg_b2.get_right(), reg_c2.get_left(), buff=0.06, color=th.GREEN, stroke_width=2.0)
                tag_pipeline = Text("TRUE 2-STAGE DELAY PIPELINE", font=th.MONO, weight=BOLD, font_size=11, color=th.GREEN)
                
                right_schem = VGroup(HStack(VGroup(reg_b2, reg_b2_lbl), reg_pipe_wire, VGroup(reg_c2, reg_c2_lbl), gap=0.1), tag_pipeline).arrange(DOWN, buff=0.15)
                right_panel = VGroup(nonblock_title, nb_code, right_schem).arrange(DOWN, buff=0.25).move_to(RIGHT * 3.4 + DOWN * 0.2)

                st.add(left_panel, right_panel)
                self.play(FadeIn(left_panel, shift=LEFT * 0.2), FadeIn(right_panel, shift=RIGHT * 0.2), run_time=0.9)

                # Animate token shift: in blocking, token flies all the way through; in non-blocking, two tokens shift together!
                clock.advance(self, delta_cycles=1, run_time=0.35)
                self.play(
                    reg_b1.animate.set_stroke(color=th.RED_LIGHT, width=3.5),
                    reg_c1.animate.set_stroke(color=th.RED_LIGHT, width=3.5),
                    reg_b2.animate.set_stroke(color=th.WHITE, width=3.5),
                    reg_c2.animate.set_stroke(color=th.WHITE, width=3.5),
                    run_time=0.6
                )
                self.wait(max(0.3, trk.duration - 2.2))
                st.takeaway("Blocking collapses a pipeline. Non-blocking preserves it.", wait=1.2)

        # =====================================================================
        # ACT 4: HOST-TO-DEVICE INTERCONNECT (PYTORCH TO SILICON)
        # =====================================================================
        act4_narration = (
            "Finally, how does your PyTorch tensor reach the silicon? The CPU writes a small memory-mapped doorbell register. "
            "That wakes dedicated DMA engines, which stream tensors across the PCIe bus straight into the accelerator's on-chip "
            "SRAM buffer—while the CPU goes back to doing other work."
        )
        with self.stage("ACT 4", "Host to Device Interconnect", "PCIe DMA Engines, MMIO Doorbells & PyTorch Dispatch", narration=act4_narration) as st:
            with self.voiceover(act4_narration) as trk:
                # 3-Stage Connected Hardware Pipeline
                host_node = RoundedRectangle(corner_radius=0.12, width=3.2, height=3.4, stroke_color=th.AMBER, stroke_width=2.0, fill_color="#181106", fill_opacity=0.92)
                h_title = Text("HOST CPU", font=th.MONO, weight=BOLD, font_size=15, color=th.AMBER)
                h_py = Text("torch.matmul(A, B)", font=th.MONO, font_size=12, color=th.AMBER_LIGHT)
                h_door = Text("1. Write Descriptor\n2. Ring MMIO Doorbell", font=th.MONO, font_size=11, color=th.TEXT, line_spacing=1.3)
                h_content = VStack(h_title, h_py, h_door, gap=th.SPACE_SM).move_to(host_node)
                host_group = VGroup(host_node, h_content).move_to(LEFT * 4.2 + DOWN * 0.2)

                pcie_bus = RoundedRectangle(corner_radius=0.12, width=3.2, height=3.4, stroke_color=th.CYAN, stroke_width=2.0, fill_color="#09182a", fill_opacity=0.92)
                p_title = Text("PCIe GEN5 x16", font=th.MONO, weight=BOLD, font_size=15, color=th.CYAN)
                p_stat = Text("64 GB/s Bandwidth\nAsync DMA Burst\nHost Unblocked", font=th.MONO, font_size=11, color=th.CYAN_LIGHT, line_spacing=1.3)
                p_content = VStack(p_title, p_stat, gap=th.SPACE_SM).move_to(pcie_bus)
                pcie_group = VGroup(pcie_bus, p_content).move_to(DOWN * 0.2)

                acc_node = RoundedRectangle(corner_radius=0.12, width=3.2, height=3.4, stroke_color=th.GREEN, stroke_width=2.0, fill_color="#071b11", fill_opacity=0.92)
                a_title = Text("AI ACCELERATOR", font=th.MONO, weight=BOLD, font_size=15, color=th.GREEN)
                a_stat = Text("SRAM Tile Buffers\nWeight Double-Buffer\nSystolic Engine", font=th.MONO, font_size=11, color=th.GREEN_LIGHT, line_spacing=1.3)
                a_content = VStack(a_title, a_stat, gap=th.SPACE_SM).move_to(acc_node)
                acc_group = VGroup(acc_node, a_content).move_to(RIGHT * 4.2 + DOWN * 0.2)

                wire_h_p = Arrow(host_node.get_right(), pcie_bus.get_left(), buff=0.08, color=th.AMBER_LIGHT, stroke_width=3.0)
                wire_p_a = Arrow(pcie_bus.get_right(), acc_node.get_left(), buff=0.08, color=th.CYAN_LIGHT, stroke_width=3.0)

                st.add(host_group, pcie_group, acc_group, wire_h_p, wire_p_a)
                self.play(FadeIn(host_group), FadeIn(pcie_group), FadeIn(acc_group), Create(wire_h_p), Create(wire_p_a), run_time=1.0)

                # Animate the Doorbell Ring spark and continuous DMA tensor stream
                doorbell_spark = Dot(host_node.get_right(), radius=0.14, color=th.AMBER)
                self.play(Indicate(doorbell_spark, color=th.WHITE, scale_factor=1.8), run_time=0.4)

                # Continuous tensor packet train streaming into accelerator
                packets = VGroup(*[
                    Dot(radius=0.10, color=col)
                    for col in [th.AMBER_LIGHT, th.CYAN_LIGHT, th.GREEN_LIGHT, th.AMBER_LIGHT]
                ])
                for i, pkt in enumerate(packets):
                    pkt.move_to(host_node.get_right() + LEFT * (i * 0.25))
                    st.add(pkt)

                self.play(
                    LaggedStart(*[
                        pkt.animate.move_to(acc_node.get_center())
                        for pkt in packets
                    ], lag_ratio=0.25),
                    acc_node.animate.set_stroke(color=th.GREEN_LIGHT, width=3.5),
                    run_time=1.4
                )
                clock.advance(self, delta_cycles=1, run_time=0.3)
                self.wait(max(0.3, trk.duration - 3.1))
                st.takeaway("A doorbell ring is all it takes to move a tensor.", wait=1.2)
