"""
Lab 03: The Memory Wall — Weight-Stationary Processing Element (PE)
Spatial Dataflow Taxonomy, Register Budgets & Quantitative Memory Energy Reduction.

Tailored for Software Engineers:
- Act 1: Mapping the Triply-Nested Loop (128x Memory & 113.5x Energy Reduction)
- Act 2: Spatial Dataflow Taxonomy (Weight-Stationary vs Output-Stationary vs Input-Stationary)
- Act 3: Inside the Weight-Stationary PE: The 48 DFF Datapath in Action
- Act 4: Dual-Phase Control: Weight Preload & Continuous Systolic Streaming
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
    ProcessingElementCell,
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


class Lab03ProcessingElement(KineticSiliconScene):
    def construct(self):
        config = HardwareConfig(data_width=8)
        clock = KineticClock(initial_cycle=0)

        # Ambient Clock HUD at top right (compact)
        ticker = clock.create_ticker_badge(prefix="CLK: T = ", color=th.AMBER_LIGHT)
        ticker.to_corner(UR, buff=0.25)
        self.add(ticker)

        # =====================================================================
        # ACT 0: PRELORE — THE LOOP YOU ALREADY WRITE
        # =====================================================================
        prelore_narration = (
            "Matrix multiplication is just three nested loops, and you have written them a hundred times. "
            "The outer two loops pick a row and a column. The inner loop walks the shared dimension, "
            "multiplying and adding into one output cell."
        )
        with self.stage("PRIMER", "The Loop You Already Write", "Rows · Columns · Accumulate", narration=prelore_narration) as st:
            with self.voiceover(prelore_narration) as trk:
                pre_code = th.code_window(
                    [
                        ("for i in range(M):", th.AMBER_LIGHT),
                        ("  for j in range(N):", th.GREEN_LIGHT),
                        ("    for k in range(K):", th.CYAN_LIGHT),
                        ("      C[i][j] += A[i][k]*B[k][j]", th.WHITE),
                    ],
                    title_text="MATRIX MULTIPLY",
                    width=6.0, height=2.9, font_size=13
                )
                pre_lbl = SemanticText("The triple loop = one output cell per (i, j)", role=TextRole.PROBE_LABEL, color=th.MUTED)
                pre_lbl.next_to(pre_code, DOWN, buff=0.3)
                pre_group = VGroup(pre_code, pre_lbl).move_to(self.layout.main_stage_center())
                st.add(pre_group)
                self.play(Create(pre_code), FadeIn(pre_lbl), run_time=1.0)
                self.wait(max(0.3, trk.duration - 1.0))
                st.takeaway("Three loops, one output cell.", wait=1.2)

        # =====================================================================
        # ACT 1: MAPPING THE TRIPLY-NESTED LOOP & 128x MEMORY WALL
        # =====================================================================
        act1_narration = (
            "Now freeze those loops onto silicon. The outer i and j loops unroll into a 2D grid of Processing Elements—"
            "rows and columns in space. The inner k loop becomes clock ticks in time. "
            "If the array is as wide as N and nothing is cached, weight and activation reads drop by 128 times. "
            "Energy drops by about 113 times, because the multiply energy does not shrink. Output writeback is not in that count."
        )
        with self.stage("ACT 1", "Mapping the Nested Loop", "Loop Unrolling: Converting Software Loops to Silicon Space", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                # The primer already showed the loops. This beat is the mapping.
                code_panel = RoundedRectangle(corner_radius=0.12, width=5.6, height=3.8, stroke_color=th.CYAN, stroke_width=1.5, fill_color="#09182a", fill_opacity=0.92)
                c_title = SemanticText("THE LOOP BECOMES A GRID", role=TextRole.BLOCK_HEADER, color=th.CYAN)
                c_lines = VGroup(
                    Text("i  →  a row of PEs", font=th.MONO, font_size=16, color=th.AMBER_LIGHT),
                    Text("j  →  a column of PEs", font=th.MONO, font_size=16, color=th.GREEN_LIGHT),
                    Text("k  →  one clock tick", font=th.MONO, font_size=16, color=th.CYAN_LIGHT),
                ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
                code_content = VStack(c_title, c_lines, gap=th.SPACE_SM).move_to(code_panel)
                code_group = VGroup(code_panel, code_content)

                # Right side: Quantitative Energy Savings (Batch 128)
                savings_panel = RoundedRectangle(corner_radius=0.12, width=5.6, height=3.8, stroke_color=th.GREEN, stroke_width=1.5, fill_color="#071b11", fill_opacity=0.92)
                s_title = SemanticText("QUANTITATIVE SAVINGS (BATCH 128)", role=TextRole.BLOCK_HEADER, color=th.GREEN)
                s_lines = VGroup(
                    Text("Reads, no cache: 4.19 MB → 32.8 KB", font=th.MONO, font_size=12, color=th.TEXT),
                    Text("128× reads. Array holds all of N.", font=th.MONO, font_size=12, color=th.MUTED),
                    Text("Energy: 0.839 mJ → 0.00739 mJ", font=th.MONO, font_size=12, color=th.GREEN_LIGHT),
                    Text("113×, not 128×: MAC energy stays.", font=th.MONO, font_size=12, color=th.AMBER_LIGHT),
                    Text("Writeback omitted: 64 KB of int32.", font=th.MONO, font_size=12, color=th.CYAN_LIGHT),
                ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
                savings_content = VStack(s_title, s_lines, gap=th.SPACE_SM).move_to(savings_panel)
                savings_group = VGroup(savings_panel, savings_content)

                act1_layout = HStack(code_group, savings_group, gap=th.SPACE_LG).move_to(self.layout.main_stage_center())
                st.add(act1_layout)

                self.play(FadeIn(code_group, shift=LEFT * 0.2), FadeIn(savings_group, shift=RIGHT * 0.2), run_time=1.0)
                self.wait(max(0.3, trk.duration - 1.0))
                st.takeaway("Loops in time become cells in space.", wait=1.2)

        # =====================================================================
        # ACT 2: SPATIAL DATAFLOW TAXONOMY (WS vs OS vs IS)
        # =====================================================================
        act2_narration = (
            "Different accelerators answer the same question: which data should stay put? "
            "Weight-stationary keeps weights local. That is the Google TPU v1. "
            "Output-stationary keeps partial sums local. ShiDianNao is the example. "
            "Row-stationary keeps a filter row local. That is Eyeriss, from ISCA 2016."
        )
        with self.stage("ACT 2", "Spatial Dataflow Taxonomy", "Weight-Stationary vs Output-Stationary vs Input-Stationary", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                card_ws = th.metric_card("Weight-Stationary", "Google TPU v1", "Weights stay in the 8-bit register", color=th.AMBER, width=3.8, height=2.4)
                card_os = th.metric_card("Output-Stationary", "ShiDianNao", "Partial sums stay in the PE", color=th.GREEN, width=3.8, height=2.4)
                card_is = th.metric_card("Row-Stationary", "Eyeriss, ISCA 2016", "A filter row stays put", color=th.CYAN, width=3.8, height=2.4)

                cards_layout = HStack(card_ws, card_os, card_is, gap=th.SPACE_MD).move_to(self.layout.main_stage_center())
                st.add(cards_layout)

                self.play(FadeIn(cards_layout, shift=UP * 0.2), run_time=1.0)
                self.wait(max(0.3, trk.duration - 1.0))
                st.takeaway("Weight-stationary is the design we zoom into next.", wait=1.2)

        # =====================================================================
        # ACT 3: INSIDE THE WEIGHT-STATIONARY PE (48 DFF BUDGET)
        # =====================================================================
        act3_narration = (
            "Let's open one Processing Element. It holds just three registers: "
            "8 bits for the stationary weight, 8 bits to pass activations eastward, "
            "and 32 bits to pass partial sums southward. That is 48 flip-flops, and no shared bus at all."
        )
        with self.stage("ACT 3", "Inside the Weight-Stationary PE", "The 48 D-Flip-Flop Architecture in Synthesizable RTL", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                # Compact height (3.1) ensures external boundary probes never collide with headers or banners
                pe = ProcessingElementCell(row=0, col=0, width=5.6, height=3.1).move_to(self.layout.main_stage_center())

                # Ports and Probes docked to boundary pins
                probe_west = PinProbe("ACT_WEST [8b]", "idle", color=th.CYAN)
                probe_west.attach_to_port(pe.chassis, edge=LEFT, gap=th.SPACE_SM)

                probe_north = PinProbe("SUM_NORTH [32b]", "idle", color=th.GREEN)
                probe_north.attach_to_port(pe.chassis, edge=UP, gap=th.SPACE_XS)

                probe_east = PinProbe("ACT_EAST [8b]", "6", color=th.CYAN_LIGHT)
                probe_east.attach_to_port(pe.chassis, edge=RIGHT, gap=th.SPACE_SM)

                probe_south = PinProbe("SUM_SOUTH [32b]", "142", color=th.GREEN_LIGHT)
                probe_south.attach_to_port(pe.chassis, edge=DOWN, gap=th.SPACE_XS)

                st.add(pe, probe_west, probe_north, probe_east, probe_south)

                self.play(Create(pe), FadeIn(probe_west), FadeIn(probe_north), run_time=0.8)

                # Weight stays. Then the activation and the partial sum arrive.
                clock.advance(self, delta_cycles=1, run_time=0.3)
                self.play(
                    pe.update_weight("7"),
                    probe_west.set_value("6"),
                    probe_north.set_value("100"),
                    run_time=0.5,
                )

                # 100 + 6*7 = 142, drawn inside the cell before the outputs appear.
                clock.advance(self, delta_cycles=1, run_time=0.3)
                self.play(pe.update_act("6"), pe.mac_eq.update_text("100+6*7"), run_time=0.45)
                self.play(
                    pe.update_sum("142"),
                    pe.mac_eq.update_text("= 142"),
                    FadeIn(probe_east),
                    FadeIn(probe_south),
                    run_time=0.6,
                )
                self.wait(max(0.3, trk.duration - 2.8))
                st.takeaway("48 flip-flops: weight, activation, and partial sum.", wait=1.2)

        # =====================================================================
        # ACT 4: DUAL-PHASE CONTROL & APPLE ANE
        # =====================================================================
        act4_narration = (
            "The whole grid runs on two phases. Phase one loads every weight down its column, once. "
            "Phase two switches to compute: activations and partial sums stream through with no shared bus. "
            "Clock-gating a zero activation, as Apple's Neural Engine does, is a later idea. It is not in this lab's RTL."
        )
        with self.stage("ACT 4", "Dual-Phase Control & Apple ANE", "Weight Configuration vs Compute Streaming in Silicon", narration=act4_narration) as st:
            with self.voiceover(act4_narration) as trk:
                budget_cards = HStack(
                    th.metric_card("48 D-FFs", "Per-PE Register Budget", "8b W + 8b Act + 32b Sum", color=th.CYAN, width=3.8, height=2.2),
                    th.metric_card("2 Phases", "Control Signal States", "Phase 1: Preload | Phase 2: Stream", color=th.GREEN, width=3.8, height=2.2),
                    th.metric_card("Zero skip", "CONCEPT, not rtl/pe.sv", "Clock-gate only if act is 0", color=th.AMBER, width=3.8, height=2.2),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(budget_cards)

                self.play(FadeIn(budget_cards, shift=UP * 0.2), run_time=1.0)
                self.wait(max(0.3, trk.duration - 1.0))
                st.takeaway("Load once, then stream forever.", wait=1.2)
