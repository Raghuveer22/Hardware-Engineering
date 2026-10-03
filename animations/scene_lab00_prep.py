"""
Lab 00-Prep: Hardware Thinking Primer for Software & AI Engineers
Architectural Implementation: Declarative Stage Lifecycle, Constraint Layout,
Living Concurrent Gate Array, Voiceover Auto-Sync, and Vector LaTeX MathTex.
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
)


class Lab00PrepPrimer(KineticSiliconScene):
    def construct(self):
        clock = KineticClock(initial_cycle=0)

        # Ambient Clock HUD at top right
        ticker = clock.create_ticker_badge(prefix="CLK: T = ", color=th.CYAN_LIGHT)
        ticker.to_corner(UR, buff=0.35)
        self.add(ticker)

        # =====================================================================
        # ACT 1: THE DEATH OF THE PROGRAM COUNTER
        # =====================================================================
        act1_narration = "In software, a single Program Counter steps sequentially line-by-line. In silicon, there is NO PC: voltage surges through all gates at once."
        with self.stage("ACT 1", "The Death of the Program Counter", "Sequential Software vs 100% Concurrent Silicon", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                # Left side: Sequential CPU Instruction Pipeline
                cpu_panel = RoundedRectangle(
                    corner_radius=0.15, width=5.4, height=4.0,
                    stroke_color=th.BORDER, stroke_width=1.5,
                    fill_color="#090e17", fill_opacity=0.95
                )
                cpu_title = SemanticText("VON NEUMANN CPU (SEQUENTIAL)", role=TextRole.BLOCK_HEADER, color=th.AMBER)
                cpu_title.next_to(cpu_panel.get_top(), DOWN, buff=0.15)

                instr_texts = [
                    "[0x00] ADD r1, r2, r3",
                    "[0x04] MUL r4, r1, #2",
                    "[0x08] SUB r5, r4, r0",
                    "[0x0C] STR r5, [SP+4]"
                ]
                instr_boxes = VGroup(*[
                    VGroup(
                        RoundedRectangle(corner_radius=0.08, width=4.6, height=0.52, stroke_color=th.BORDER, stroke_width=1.2, fill_color=th.CARD, fill_opacity=0.8),
                        SemanticText(itxt, role=TextRole.CODE, color=th.MUTED)
                    )
                    for itxt in instr_texts
                ]).arrange(DOWN, buff=0.12).move_to(cpu_panel.get_center() + DOWN * 0.1)

                cpu_group = VGroup(cpu_panel, cpu_title, instr_boxes)

                # Right side: Concurrent Gate Array
                silicon_panel = RoundedRectangle(
                    corner_radius=0.15, width=5.4, height=4.0,
                    stroke_color=th.CYAN, stroke_width=1.5,
                    fill_color="#090e17", fill_opacity=0.95
                )
                silicon_title = SemanticText("SPATIAL SILICON (100% CONCURRENT)", role=TextRole.BLOCK_HEADER, color=th.CYAN)
                silicon_title.next_to(silicon_panel.get_top(), DOWN, buff=0.15)

                gate_grid = VGroup(*[
                    VGroup(
                        RoundedRectangle(corner_radius=0.08, width=1.3, height=0.8, stroke_color=th.CYAN_DARK, stroke_width=1.5, fill_color="#0d1f33", fill_opacity=0.8),
                        SemanticText(lbl, role=TextRole.BLOCK_HEADER, color=th.CYAN)
                    )
                    for lbl in ["ADD", "MUL", "LUT", "MAC", "RELU", "XOR", "SUB", "CMP", "DIV"]
                ]).arrange_in_grid(rows=3, cols=3, buff=0.2).move_to(silicon_panel.get_center() + DOWN * 0.1)

                silicon_group = VGroup(silicon_panel, silicon_title, gate_grid)

                stage_layout = HStack(cpu_group, silicon_group, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(stage_layout)

                self.play(FadeIn(cpu_group), FadeIn(silicon_group), run_time=1.0)

                # Assert VDD Power Rail: All gates ignite simultaneously
                flashes = [
                    g[0].animate.set_stroke(color=th.CYAN_LIGHT, width=2.5).set_fill(color=th.CYAN_DARK, opacity=0.95)
                    for g in gate_grid
                ]
                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.play(*flashes, run_time=0.6)
                self.screen_shake(intensity=0.03, cycles=2, run_time=0.2)
                self.wait(max(0.2, trk.duration - 2.2))

        # =====================================================================
        # ACT 2: PRE-SILICON MEMORY ENERGY HIERARCHY
        # =====================================================================
        act2_narration = "Compute is virtually free in modern silicon. The entire architecture of AI hardware exists to avoid fetching data from DRAM."
        with self.stage("ACT 2", "Memory Energy Hierarchy", "The Fundamental Constraint of Chip Architecture", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                energy_bar = MemoryEnergyBar().move_to(self.layout.main_stage_center())
                st.add(energy_bar)
                self.play(FadeIn(energy_bar, shift=UP * 0.2), run_time=min(trk.duration, 1.0))
                self.wait(max(0.2, trk.duration - 1.0))

        # =====================================================================
        # ACT 3: SETUP & HOLD TIMING THEOREMS
        # =====================================================================
        act3_narration = "In physical circuits, data must stabilize before the rising clock edge. Violating setup time causes catastrophic flip-flop metastability."
        with self.stage("ACT 3", "Clock Setup & Hold Theorems", "Physical Propagation Delay & Metastability Prevention", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                setup_eq = SemanticMath(
                    r"T_{\text{clk}} \ge t_{\text{cq}} + t_{\text{comb}} + t_{\text{setup}}",
                    role=TextRole.MATH_DISPLAY,
                    color=th.GREEN_LIGHT
                )
                hold_eq = SemanticMath(
                    r"t_{\text{hold}} \le t_{\text{cq}} + t_{\text{comb},\min}",
                    role=TextRole.MATH_DISPLAY,
                    color=th.AMBER_LIGHT
                )

                timing_cards = HStack(
                    th.metric_card("t_setup", "Setup Window (Before Edge)", "Data must remain steady", color=th.GREEN, width=3.8, height=2.0),
                    th.metric_card("t_hold", "Hold Window (After Edge)", "Prevents race conditions", color=th.AMBER, width=3.8, height=2.0),
                    th.metric_card("t_comb", "Critical Path Delay", "Limits maximum clock F_max", color=th.CYAN, width=3.8, height=2.0),
                    gap=th.SPACE_MD
                )

                timing_layout = VStack(setup_eq, hold_eq, timing_cards, gap=th.SPACE_MD).move_to(self.layout.main_stage_center())
                st.add(timing_layout)

                self.play(Write(setup_eq), Write(hold_eq), FadeIn(timing_cards, shift=UP * 0.2), run_time=min(trk.duration, 1.2))
                self.wait(max(0.2, trk.duration - 1.2))

        # =====================================================================
        # ACT 4: PCIE DMA VS HOST MMIO
        # =====================================================================
        act4_narration = "CPUs communicate with accelerators across PCIe buses using DMA descriptors, offloading tensor matrices without CPU intervention."
        with self.stage("ACT 4", "Host to Device Interconnect", "PCIe DMA Engines & MMIO Control Registers", narration=act4_narration) as st:
            with self.voiceover(act4_narration) as trk:
                pcie_cards = HStack(
                    th.metric_card("PCIe Gen 5", "64 GB/s Host Bandwidth", "High-speed tensor streaming", color=th.CYAN, width=3.8, height=2.2),
                    th.metric_card("DMA Engine", "Zero-Copy Data Transfer", "Bypasses CPU instruction loops", color=th.GREEN, width=3.8, height=2.2),
                    th.metric_card("Ring Buffer", "Command Queue / Doorbell", "Asynchronous tensor dispatch", color=th.AMBER, width=3.8, height=2.2),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(pcie_cards)

                self.play(FadeIn(pcie_cards, shift=UP * 0.2), run_time=min(trk.duration, 1.0))
                self.wait(max(0.2, trk.duration - 1.0))
