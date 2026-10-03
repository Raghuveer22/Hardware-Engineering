"""
Lab 04: The Systolic Array Matrix Multiplier — Living Silicon Masterclass
Architectural Implementation: Declarative Stage Lifecycle, Constraint Layout,
RTL Simulation Trace Replay (trace.json), Voiceover Auto-Sync, and Continuous Morphing.
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
    LiveOscilloscope,
    LaserPacketStream,
    SiliconWire,
    HardwareConfig,
    TextRole,
    SemanticText,
    SemanticMath,
    HStack,
    VStack,
    ConstraintAnchor,
    ProcessingElementCell,
    MemoryEnergyBar,
    PinProbe,
    TracePlayback,
    TraceDrivenController,
)


class Lab04SystolicArray(KineticSiliconScene):
    def construct(self):
        config = HardwareConfig(array_size=2)
        clock = KineticClock(initial_cycle=0)
        trace = TracePlayback()

        # HUD clock ticker docked top-right
        ticker = clock.create_ticker_badge(prefix="CLK: T = ", color=th.AMBER_LIGHT)
        ticker.to_corner(UR, buff=0.35)
        self.add(ticker)

        # =====================================================================
        # ACT 0: PRELORE — WHAT "SYSTOLIC" MEANS
        # =====================================================================
        prelore_narration = (
            "Systolic comes from the Greek word for contraction, like a heartbeat. "
            "A systolic array is a grid of tiny processors that pass data only to their immediate neighbors, "
            "in a pulsing rhythm—no cell ever reaches across the whole chip."
        )
        with self.stage("PRIMER", "What 'Systolic' Means", "A Grid That Pulses Like a Heartbeat", narration=prelore_narration) as st:
            with self.voiceover(prelore_narration) as trk:
                pre_cards = HStack(
                    th.metric_card("Grid", "Tiny cells side by side", "One weight per cell", color=th.CYAN, width=3.6, height=2.3),
                    th.metric_card("Neighbors", "Data only moves 1 hop", "No global bus wires", color=th.GREEN, width=3.6, height=2.3),
                    th.metric_card("Rhythm", "One step per clock tick", "The wavefront pulse", color=th.AMBER, width=3.6, height=2.3),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(pre_cards)
                self.play(FadeIn(pre_cards, shift=UP * 0.2), run_time=1.0)
                self.wait(max(0.3, trk.duration - 1.0))
                st.takeaway("Systolic = neighbor-to-neighbor, one pulse per clock.", wait=1.2)

        # =====================================================================
        # ACT 1: FROM PYTORCH TO SILICON & THE LLM MEMORY WALL
        # =====================================================================
        act1_narration = (
            "Here is the promise. Attention is one clean line in PyTorch. "
            "But a CPU turns it into three nested loops, and at a million-token context "
            "a single forward pass needs trillions of operations—most of them wasted waiting on memory."
        )
        with self.stage("ACT 1", "From PyTorch to Silicon", "Why LLMs Demand Spatial Hardware", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                # Left: PyTorch Attention Code
                code_lines = [
                    ("# PyTorch Self-Attention", th.MUTED),
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
                soft_win = th.code_window(
                    code_lines,
                    title_text="SOFTWARE: O(N³) NESTED LOOPS",
                    width=5.6,
                    height=4.1,
                    font_size=12
                )

                # Right: Hardware Scaling Crisis
                stat1 = th.metric_card("100+ Trillion", "Ops per Token (1M Context)", color=th.AMBER, width=4.6, height=1.6)
                stat2 = th.metric_card("90% Stalled", "Von Neumann DRAM Bottleneck", color=th.RED, width=4.6, height=1.6)
                right_panel = VStack(stat1, stat2, gap=th.SPACE_MD)

                stage_layout = HStack(soft_win, right_panel, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(stage_layout)

                self.play(Create(soft_win), FadeIn(right_panel, shift=LEFT * 0.3), run_time=min(trk.duration, 1.2))
                self.wait(max(0.2, trk.duration - 1.2))
                st.takeaway("One line in PyTorch, trillions of ops in silicon.", wait=1.2)

        # =====================================================================
        # ACT 2: PHYSICAL SILICON LIMITS & THE 1,000x MEMORY WALL
        # =====================================================================
        act2_narration = (
            "And the physics makes it worse. Computing one multiply-accumulate costs 0.2 picojoules, "
            "but reading one number from external DRAM costs 200—a thousand times more. "
            "That is why every accelerator keeps its weights inside the chip."
        )
        with self.stage("ACT 2", "The 1,000x Memory Wall", "Why Weights Must Never Be Re-Read", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                energy_bar = MemoryEnergyBar().move_to(self.layout.main_stage_center())
                st.add(energy_bar)
                self.play(FadeIn(energy_bar, shift=UP * 0.2), run_time=min(trk.duration, 1.0))
                self.wait(max(0.2, trk.duration - 1.0))
                st.takeaway("Move data 1,000× less, compute 1,000× more.", wait=1.2)

        # =====================================================================
        # ACT 3: INSIDE THE WEIGHT-STATIONARY PROCESSING ELEMENT (PE)
        # =====================================================================
        act3_narration = (
            "The cell that makes this possible is the Processing Element. "
            "Its weight stays locked in a local register, while activations stream west-to-east "
            "and partial sums accumulate north-to-south, all in a single clock beat."
        )
        with self.stage("ACT 3", "Weight-Stationary Processing Element", "Microarchitecture of a Single Tensor Core", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                pe = ProcessingElementCell(row=0, col=0, width=5.6, height=3.8).move_to(self.layout.main_stage_center())
                
                # Live Input Probes pinned to boundary ports
                probe_west = PinProbe("ACT_IN [W]", "0x01", color=th.CYAN)
                probe_west.attach_to_port(pe.chassis, edge=LEFT, gap=th.SPACE_SM)

                probe_north = PinProbe("SUM_IN [N]", "0x00", color=th.GREEN)
                probe_north.attach_to_port(pe.chassis, edge=UP, gap=th.SPACE_SM)

                st.add(pe, probe_west, probe_north)
                self.play(Create(pe), FadeIn(probe_west), FadeIn(probe_north), run_time=min(trk.duration * 0.6, 1.0))

                # Step Clock & Lock Weight
                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.play(pe.update_weight("0x05"), run_time=0.4)
                self.wait(max(0.2, trk.duration - 1.8))
                st.takeaway("One cell = one weight, one activation, one partial sum.", wait=1.2)

        # =====================================================================
        # ACT 4: 2D SYSTOLIC WAVEFRONT (RTL TRACE REPLAY)
        # =====================================================================
        act4_narration = (
            "Now we connect these cells into a real 4-by-4 grid and replay our own RTL simulation, "
            "cycle by cycle. Each row is delayed by one extra clock tick, so activations arrive "
            "on a diagonal wavefront and every cell's math lines up exactly."
        )
        with self.stage("ACT 4", "The 2D Systolic Wavefront", "Cycle-Accurate RTL Simulation Trace Replay", narration=act4_narration) as st:
            with self.voiceover(act4_narration) as trk:
                # 4x4 Grid of PEs (matches rtl/systolic_array.sv and visualizer/trace.json)
                rows = trace.dimensions.get("ROWS", 4)
                cols = trace.dimensions.get("COLS", 4)
                grid_pes = []
                grid_group = VGroup()
                for r in range(rows):
                    row_pes = []
                    for c in range(cols):
                        cell = ProcessingElementCell(row=r, col=c, width=2.4, height=1.9)
                        row_pes.append(cell)
                        grid_group.add(cell)
                    grid_pes.append(row_pes)

                grid_group.arrange_in_grid(rows=rows, cols=cols, buff=0.35).move_to(self.layout.main_stage_center() + LEFT * 1.1)

                # Connect to RTL Simulation Trace
                controller = TraceDrivenController(trace)
                for r in range(rows):
                    for c in range(cols):
                        controller.bind_pe(r, c, grid_pes[r][c])

                # Live Oscilloscope docked to right
                osc = LiveOscilloscope(total_cycles=trace.total_cycles, width=4.5, height=2.8)
                osc.next_to(grid_group, RIGHT, buff=th.SPACE_LG)

                st.add(grid_group, osc)
                self.play(FadeIn(grid_group), Create(osc), run_time=1.0)

                # Phase 1: load weights column-by-column (T=0..3)
                for cyc in range(4):
                    clock.advance(self, delta_cycles=1, run_time=0.3)
                    controller.step_to_cycle(self, cyc, run_time=0.3)
                    self.play(osc.set_cursor_cycle(cyc), run_time=0.2)

                # Phase 2: stream compute and watch sums march out (T=4..14)
                for cyc in range(4, 15):
                    clock.advance(self, delta_cycles=1, run_time=0.3)
                    controller.step_to_cycle(self, cyc, run_time=0.3)
                    self.play(osc.set_cursor_cycle(cyc), run_time=0.2)

                # Tactile Wavefront Arrival Notification
                wavefront_eq = SemanticMath(r"T_{\text{arrival}}(i, j) = i + j + \text{ROWS} - 1", role=TextRole.MATH_DISPLAY)
                wavefront_eq.next_to(grid_group, DOWN, buff=0.25)
                st.add(wavefront_eq)
                self.play(Write(wavefront_eq), run_time=0.6)
                self.wait(max(0.2, trk.duration - 3.5))
                st.takeaway("Skew each row by one tick, and the wavefront lines up.", wait=1.2)

        # =====================================================================
        # ACT 5: SILICON CO-DESIGN SUMMARY & VERIFICATION
        # =====================================================================
        act5_narration = (
            "That is the whole story of this course in one frame. "
            "Systolic computing keeps data on-chip so nearly all energy goes to math instead of memory, "
            "and that is how one chip reaches trillion-operation throughput."
        )
        with self.stage("ACT 5", "Hardware-Software Co-Design", "From Mathematical Model to Synthesizable Silicon", narration=act5_narration) as st:
            with self.voiceover(act5_narration) as trk:
                summary_cards = HStack(
                    th.metric_card("16× Area", "INT8 vs FP32 Advantage", color=th.CYAN, width=3.6, height=2.2),
                    th.metric_card("200 pJ ➔ 0.2 pJ", "1,000× Energy Wall Broken", color=th.GREEN, width=3.6, height=2.2),
                    th.metric_card("O(N) Buses", "Near-Zero Wire Resistance", color=th.AMBER, width=3.6, height=2.2),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(summary_cards)

                self.play(FadeIn(summary_cards, shift=UP * 0.25), run_time=min(trk.duration, 1.0))
                self.wait(max(0.2, trk.duration - 1.0))
                st.takeaway("Keep data local, and the memory wall disappears.", wait=1.2)
