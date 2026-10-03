"""
Lab 00-Prep: Hardware Thinking Primer for Software & AI Engineers
Bridging the Gap from Python & PyTorch to Synthesizable Silicon Gates.

Tailored for Software Engineers:
- Act 1: The Death of the Program Counter (Sequential CPU vs Concurrent Silicon)
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

        # Ambient Clock HUD at top right (compact to avoid title collisions)
        ticker = clock.create_ticker_badge(prefix="CLK: T = ", color=th.CYAN_LIGHT)
        ticker.to_corner(UR, buff=0.25)
        self.add(ticker)

        # =====================================================================
        # ACT 0: PRELORE — THREE IDEAS YOU ALREADY KNOW
        # =====================================================================
        prelore_narration = (
            "Before we open the silicon, let's name three ideas every software engineer already knows. "
            "A program is just an ordered list of instructions. A logic gate is a tiny switch that does exactly one "
            "arithmetic operation, like add or multiply. And a clock is the heartbeat that advances the whole circuit one step at a time."
        )
        with self.stage("PRIMER", "Three Ideas You Already Know", "Program · Gate · Clock", narration=prelore_narration) as st:
            with self.voiceover(prelore_narration) as trk:
                pre_cards = HStack(
                    th.metric_card("Program", "Ordered list of instructions", "Runs one line at a time", color=th.CYAN, width=3.6, height=2.3),
                    th.metric_card("Gate", "One arithmetic operation", "Add, multiply, compare", color=th.GREEN, width=3.6, height=2.3),
                    th.metric_card("Clock", "The circuit heartbeat", "Advances one step per tick", color=th.AMBER, width=3.6, height=2.3),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(pre_cards)
                self.play(FadeIn(pre_cards, shift=UP * 0.2), run_time=1.0)
                self.wait(max(0.3, trk.duration - 1.0))
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
                # Left side: Sequential CPU Instruction Pipeline with active PC pointer
                cpu_panel = RoundedRectangle(
                    corner_radius=0.15, width=5.5, height=4.2,
                    stroke_color=th.BORDER, stroke_width=1.5,
                    fill_color="#090e17", fill_opacity=0.95
                )
                cpu_title = SemanticText("SOFTWARE: SEQUENTIAL CPU", role=TextRole.BLOCK_HEADER, color=th.AMBER)
                cpu_title.next_to(cpu_panel.get_top(), DOWN, buff=0.15)

                instr_texts = [
                    "0x00:  t1 = a + b    # Cycle 1",
                    "0x04:  t2 = c + d    # Cycle 2",
                    "0x08:  y  = t1 * t2  # Cycle 3",
                    "0x0C:  return y"
                ]
                instr_boxes = []
                for itxt in instr_texts:
                    box = RoundedRectangle(corner_radius=0.08, width=4.8, height=0.55, stroke_color=th.BORDER, stroke_width=1.2, fill_color=th.CARD, fill_opacity=0.85)
                    txt = SemanticText(itxt, role=TextRole.CODE, color=th.TEXT)
                    instr_boxes.append(VGroup(box, txt))

                instr_group = VGroup(*instr_boxes).arrange(DOWN, buff=0.12).move_to(cpu_panel.get_center() + DOWN * 0.15)

                # Animated PC Pointer arrow
                pc_arrow = Arrow(LEFT * 0.55, ORIGIN, buff=0, color=th.AMBER, stroke_width=3.5, max_tip_length_to_length_ratio=0.3)
                pc_arrow.next_to(instr_boxes[0], LEFT, buff=0.1)
                pc_lbl = Text("PC", font=th.MONO, weight=BOLD, font_size=11, color=th.AMBER_LIGHT).next_to(pc_arrow, LEFT, buff=0.06)
                pc_unit = VGroup(pc_arrow, pc_lbl)

                cpu_group = VGroup(cpu_panel, cpu_title, instr_group, pc_unit)

                # Right side: Concurrent Hardware Dataflow
                silicon_panel = RoundedRectangle(
                    corner_radius=0.15, width=5.8, height=4.2,
                    stroke_color=th.CYAN, stroke_width=1.5,
                    fill_color="#090e17", fill_opacity=0.95
                )
                silicon_title = SemanticText("SILICON: CONCURRENT DATAFLOW", role=TextRole.BLOCK_HEADER, color=th.CYAN)
                silicon_title.next_to(silicon_panel.get_top(), DOWN, buff=0.15)

                # Two parallel adders feeding one multiplier
                add1_box = RoundedRectangle(corner_radius=0.08, width=2.2, height=0.75, stroke_color=th.CYAN_DARK, stroke_width=1.5, fill_color="#0d1f33", fill_opacity=0.9)
                add1_lbl = SemanticText("ADDER 1 (a+b)", role=TextRole.CODE, color=th.CYAN)
                add1 = VGroup(add1_box, add1_lbl).move_to(silicon_panel.get_center() + UP * 0.7 + LEFT * 1.3)

                add2_box = RoundedRectangle(corner_radius=0.08, width=2.2, height=0.75, stroke_color=th.CYAN_DARK, stroke_width=1.5, fill_color="#0d1f33", fill_opacity=0.9)
                add2_lbl = SemanticText("ADDER 2 (c+d)", role=TextRole.CODE, color=th.CYAN)
                add2 = VGroup(add2_box, add2_lbl).move_to(silicon_panel.get_center() + UP * 0.7 + RIGHT * 1.3)

                mult_box = RoundedRectangle(corner_radius=0.08, width=2.6, height=0.75, stroke_color=th.GREEN_DARK, stroke_width=1.5, fill_color="#072213", fill_opacity=0.9)
                mult_lbl = SemanticText("MULTIPLIER (t1*t2)", role=TextRole.CODE, color=th.GREEN_LIGHT)
                mult = VGroup(mult_box, mult_lbl).move_to(silicon_panel.get_center() + DOWN * 0.7)

                wire1 = Arrow(add1.get_bottom(), mult.get_top() + LEFT * 0.5, buff=0.08, color=th.CYAN_LIGHT, stroke_width=2.0)
                wire2 = Arrow(add2.get_bottom(), mult.get_top() + RIGHT * 0.5, buff=0.08, color=th.CYAN_LIGHT, stroke_width=2.0)

                tag_concurrent = SemanticText("PARALLEL COMMIT: 1 CLOCK CYCLE", role=TextRole.PROBE_LABEL, color=th.GREEN_LIGHT)
                tag_concurrent.next_to(mult, DOWN, buff=0.2)

                silicon_circuit = VGroup(add1, add2, mult, wire1, wire2, tag_concurrent)
                silicon_group = VGroup(silicon_panel, silicon_title, silicon_circuit)

                stage_layout = HStack(cpu_group, silicon_group, gap=th.SPACE_MD).move_to(self.layout.main_stage_center())
                st.add(stage_layout)

                self.play(FadeIn(cpu_group), FadeIn(silicon_group), run_time=1.0)

                # Step 1: PC moves to 0x04 in CPU while BOTH Adders ignite simultaneously in silicon
                self.play(
                    pc_unit.animate.next_to(instr_boxes[1], LEFT, buff=0.1),
                    add1_box.animate.set_stroke(color=th.CYAN_LIGHT, width=2.5).set_fill(color=th.CYAN_DARK, opacity=0.95),
                    add2_box.animate.set_stroke(color=th.CYAN_LIGHT, width=2.5).set_fill(color=th.CYAN_DARK, opacity=0.95),
                    run_time=0.7
                )
                clock.advance(self, delta_cycles=1, run_time=0.3)

                # Step 2: PC moves to 0x08 in CPU while Multiplier receives both results concurrently
                self.play(
                    pc_unit.animate.next_to(instr_boxes[2], LEFT, buff=0.1),
                    mult_box.animate.set_stroke(color=th.GREEN_LIGHT, width=2.5).set_fill(color=th.GREEN_DARK, opacity=0.95),
                    run_time=0.6
                )
                clock.advance(self, delta_cycles=1, run_time=0.3)
                self.screen_shake(intensity=0.02, cycles=2, run_time=0.2)
                self.wait(max(0.3, trk.duration - 3.1))
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
                energy_bar = MemoryEnergyBar().move_to(self.layout.main_stage_center())
                st.add(energy_bar)
                self.play(FadeIn(energy_bar, shift=UP * 0.2), run_time=1.0)
                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.wait(max(0.3, trk.duration - 1.4))
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
                # Left side: Broken Blocking (=)
                card_blocking = RoundedRectangle(
                    corner_radius=0.15, width=5.6, height=4.2,
                    stroke_color=th.RED, stroke_width=1.5,
                    fill_color="#180b0b", fill_opacity=0.92
                )
                title_blocking = SemanticText("[BROKEN] BLOCKING (=)", role=TextRole.BLOCK_HEADER, color=th.RED)
                title_blocking.next_to(card_blocking.get_top(), DOWN, buff=0.15)

                code_block = VGroup(
                    Text("always_ff @(posedge clk) begin", font=th.MONO, font_size=11, color=th.MUTED),
                    Text("    b = a;  // B gets A immediately", font=th.MONO, font_size=11, color=th.TEXT),
                    Text("    c = b;  // C gets NEW B (=A)!", font=th.MONO, font_size=11, color=th.RED_LIGHT),
                    Text("end", font=th.MONO, font_size=11, color=th.MUTED),
                ).arrange(DOWN, aligned_edge=LEFT, buff=0.10)
                code_block.next_to(title_blocking, DOWN, buff=0.2)

                # Hardware reality of blocking: collapsed register
                hw_b_box = RoundedRectangle(corner_radius=0.08, width=4.6, height=0.8, stroke_color=th.RED_DARK, fill_color="#2b0a0a", fill_opacity=0.9)
                hw_b_txt = SemanticText("Hardware: 1 Collapsed Register (Both get A in Cycle 1!)", role=TextRole.PROBE_LABEL, color=th.RED_LIGHT)
                hw_b_txt.move_to(hw_b_box)
                hw_b_grp = VGroup(hw_b_box, hw_b_txt).next_to(code_block, DOWN, buff=0.25)

                left_group = VGroup(card_blocking, title_blocking, code_block, hw_b_grp)

                # Right side: Correct Non-Blocking (<=)
                card_nonblock = RoundedRectangle(
                    corner_radius=0.15, width=5.6, height=4.2,
                    stroke_color=th.GREEN, stroke_width=1.5,
                    fill_color="#071b11", fill_opacity=0.92
                )
                title_nonblock = SemanticText("[CORRECT] NON-BLOCKING (<=)", role=TextRole.BLOCK_HEADER, color=th.GREEN)
                title_nonblock.next_to(card_nonblock.get_top(), DOWN, buff=0.15)

                code_nonblock = VGroup(
                    Text("always_ff @(posedge clk) begin", font=th.MONO, font_size=11, color=th.MUTED),
                    Text("    b <= a; // B samples old A", font=th.MONO, font_size=11, color=th.TEXT),
                    Text("    c <= b; // C samples old B simultaneously", font=th.MONO, font_size=11, color=th.GREEN_LIGHT),
                    Text("end", font=th.MONO, font_size=11, color=th.MUTED),
                ).arrange(DOWN, aligned_edge=LEFT, buff=0.10)
                code_nonblock.next_to(title_nonblock, DOWN, buff=0.2)

                # Hardware reality of non-blocking: true 2-stage shift register
                hw_nb_box = RoundedRectangle(corner_radius=0.08, width=4.6, height=0.8, stroke_color=th.GREEN_DARK, fill_color="#072213", fill_opacity=0.9)
                hw_nb_txt = SemanticText("Hardware: 2 DFFs in Series: (b, c) = (a, b) commit", role=TextRole.PROBE_LABEL, color=th.GREEN_LIGHT)
                hw_nb_txt.move_to(hw_nb_box)
                hw_nb_grp = VGroup(hw_nb_box, hw_nb_txt).next_to(code_nonblock, DOWN, buff=0.25)

                right_group = VGroup(card_nonblock, title_nonblock, code_nonblock, hw_nb_grp)

                pipeline_layout = HStack(left_group, right_group, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(pipeline_layout)

                self.play(FadeIn(left_group), FadeIn(right_group), run_time=1.0)
                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.wait(max(0.3, trk.duration - 1.4))
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
                # 3-Stage Pipeline Block: Host CPU -> PCIe Bus -> Accelerator SRAM
                host_box = RoundedRectangle(corner_radius=0.12, width=3.4, height=3.2, stroke_color=th.AMBER, stroke_width=1.5, fill_color="#181106", fill_opacity=0.92)
                h_title = SemanticText("HOST CPU", role=TextRole.BLOCK_HEADER, color=th.AMBER)
                h_sub = Text("torch.matmul(A, B)\n1. Write DMA Descriptor\n2. MMIO Doorbell Ring", font=th.MONO, font_size=11, color=th.TEXT, line_spacing=1.3)
                h_content = VStack(h_title, h_sub, gap=th.SPACE_SM).move_to(host_box)
                host_group = VGroup(host_box, h_content)

                pcie_bus = RoundedRectangle(corner_radius=0.12, width=3.4, height=3.2, stroke_color=th.CYAN, stroke_width=1.5, fill_color="#09182a", fill_opacity=0.92)
                p_title = SemanticText("PCIe GEN5 x16", role=TextRole.BLOCK_HEADER, color=th.CYAN)
                p_sub = Text("64 GB/s Bandwidth\nAsynchronous DMA\nZero Host Polling", font=th.MONO, font_size=11, color=th.CYAN_LIGHT, line_spacing=1.3)
                p_content = VStack(p_title, p_sub, gap=th.SPACE_SM).move_to(pcie_bus)
                pcie_group = VGroup(pcie_bus, p_content)

                acc_box = RoundedRectangle(corner_radius=0.12, width=3.4, height=3.2, stroke_color=th.GREEN, stroke_width=1.5, fill_color="#071b11", fill_opacity=0.92)
                a_title = SemanticText("AI ACCELERATOR", role=TextRole.BLOCK_HEADER, color=th.GREEN)
                a_sub = Text("On-Chip SRAM Buffer\nWeight Preload\nSystolic Compute Grid", font=th.MONO, font_size=11, color=th.GREEN_LIGHT, line_spacing=1.3)
                a_content = VStack(a_title, a_sub, gap=th.SPACE_SM).move_to(acc_box)
                acc_group = VGroup(acc_box, a_content)

                bus_layout = HStack(host_group, pcie_group, acc_group, gap=th.SPACE_MD).move_to(self.layout.main_stage_center())
                st.add(bus_layout)

                self.play(FadeIn(bus_layout, shift=UP * 0.2), run_time=1.0)

                # Animate active packet traveling from Host across PCIe to Accelerator
                pkt = Dot(radius=0.12, color=th.AMBER_LIGHT).move_to(host_box.get_right())
                st.add(pkt)
                self.play(FadeIn(pkt), run_time=0.2)
                self.play(pkt.animate.move_to(pcie_bus.get_center()), run_time=0.5)
                self.play(pkt.animate.move_to(acc_box.get_left()), run_time=0.5)
                self.play(FadeOut(pkt), run_time=0.2)
                clock.advance(self, delta_cycles=1, run_time=0.3)
                self.wait(max(0.3, trk.duration - 2.2))
                st.takeaway("A doorbell ring is all it takes to move a tensor.", wait=1.2)
