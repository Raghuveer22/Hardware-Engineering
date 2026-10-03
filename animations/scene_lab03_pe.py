"""
Lab 03: The Memory Wall — Weight-Stationary Processing Element (PE)
Architectural Implementation: Declarative Stage Lifecycle, Constraint Layout,
ProcessingElementCell Standard Cell, Voiceover Auto-Sync, and Semantic Typography.
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


class Lab03ProcessingElement(KineticSiliconScene):
    def construct(self):
        config = HardwareConfig(data_width=8)
        clock = KineticClock(initial_cycle=0)

        # Ambient Clock HUD at top right
        ticker = clock.create_ticker_badge(prefix="CLK: T = ", color=th.AMBER_LIGHT)
        ticker.to_corner(UR, buff=0.35)
        self.add(ticker)

        # =====================================================================
        # ACT 1: PHYSICAL SILICON ENERGY & THE 1,000x MEMORY WALL
        # =====================================================================
        act1_narration = "In physical silicon, accessing external DRAM costs 200 picojoules, while an INT8 MAC operation costs just 0.2 picojoules."
        with self.stage("ACT 1", "The 1,000x Memory Energy Wall", "Why Spatial Dataflows Are Mandatory in AI", narration=act1_narration) as st:
            with self.voiceover(act1_narration) as trk:
                energy_bar = MemoryEnergyBar().move_to(self.layout.main_stage_center())
                st.add(energy_bar)
                self.play(FadeIn(energy_bar, shift=UP * 0.2), run_time=min(trk.duration, 1.0))
                self.wait(max(0.2, trk.duration - 1.0))

        # =====================================================================
        # ACT 2: SPATIAL DATAFLOW TAXONOMY (WS vs OS vs IS)
        # =====================================================================
        act2_narration = "Accelerators reuse data using three spatial taxonomies: Weight-Stationary in Google TPUs, Output-Stationary, and Input-Stationary."
        with self.stage("ACT 2", "Spatial Dataflow Taxonomy", "Weight-Stationary vs Output-Stationary vs Input-Stationary", narration=act2_narration) as st:
            with self.voiceover(act2_narration) as trk:
                card_ws = th.metric_card("Weight-Stationary", "Google TPU v1-v5", "Weights locked locally; activations stream", color=th.AMBER, width=3.8, height=2.4)
                card_os = th.metric_card("Output-Stationary", "Stanford Eyeriss", "Accumulator locked locally; partial sums stay", color=th.GREEN, width=3.8, height=2.4)
                card_is = th.metric_card("Input-Stationary", "NVDLA Architecture", "Activations broadcast; weights stream", color=th.CYAN, width=3.8, height=2.4)

                cards_layout = HStack(card_ws, card_os, card_is, gap=th.SPACE_MD).move_to(self.layout.main_stage_center())
                st.add(cards_layout)

                self.play(FadeIn(cards_layout, shift=UP * 0.2), run_time=min(trk.duration, 1.0))
                self.wait(max(0.2, trk.duration - 1.0))

        # =====================================================================
        # ACT 3: DUAL-PHASE PROCESSING ELEMENT EXECUTION
        # =====================================================================
        act3_narration = "In Phase 1, weights load and lock into local registers. In Phase 2, activations stream from West and partial sums accumulate South."
        with self.stage("ACT 3", "Inside the Weight-Stationary PE", "Dual-Phase Execution & Orthogonal Signal Routing", narration=act3_narration) as st:
            with self.voiceover(act3_narration) as trk:
                pe = ProcessingElementCell(row=0, col=0, width=5.8, height=3.8).move_to(self.layout.main_stage_center())

                # Ports and Probes
                probe_west = PinProbe("ACT_WEST [8b]", "0x03", color=th.CYAN)
                probe_west.attach_to_port(pe.chassis, edge=LEFT, gap=th.SPACE_SM)

                probe_north = PinProbe("SUM_NORTH [32b]", "0x00", color=th.GREEN)
                probe_north.attach_to_port(pe.chassis, edge=UP, gap=th.SPACE_SM)

                probe_east = PinProbe("ACT_EAST [8b]", "0x03", color=th.CYAN_LIGHT)
                probe_east.attach_to_port(pe.chassis, edge=RIGHT, gap=th.SPACE_SM)

                probe_south = PinProbe("SUM_SOUTH [32b]", "0x4E", color=th.GREEN_LIGHT)
                probe_south.attach_to_port(pe.chassis, edge=DOWN, gap=th.SPACE_SM)

                st.add(pe, probe_west, probe_north)
                self.play(Create(pe), FadeIn(probe_west), FadeIn(probe_north), run_time=1.0)

                # Phase 1: Lock Weight
                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.play(pe.update_weight("0x1A"), run_time=0.4)

                # Phase 2: Compute MAC & Latch Outputs
                clock.advance(self, delta_cycles=1, run_time=0.4)
                self.play(
                    FadeIn(probe_east),
                    FadeIn(probe_south),
                    run_time=0.6
                )
                self.wait(max(0.2, trk.duration - 2.8))

        # =====================================================================
        # ACT 4: 48 D-FF BUDGET & APPLE ANE MAPPING
        # =====================================================================
        act4_narration = "A single PE requires exactly 48 D-flip-flops. With zero long global wires, parasitic capacitance is microscopic."
        with self.stage("ACT 4", "Silicon Gate Budget & Apple ANE", "Physical Area Breakdown & Micro-Wire Routing", narration=act4_narration) as st:
            with self.voiceover(act4_narration) as trk:
                budget_cards = HStack(
                    th.metric_card("48 D-FFs", "Per-PE Register Budget", "8b W + 8b Act + 32b Sum", color=th.CYAN, width=3.8, height=2.2),
                    th.metric_card("Zero Buses", "Neighbor-Only Interconnect", "Eliminates parasitic wire RC delay", color=th.GREEN, width=3.8, height=2.2),
                    th.metric_card("Apple ANE", "16-Core Neural Engine", "Scaled across modern Apple silicon", color=th.AMBER, width=3.8, height=2.2),
                    gap=th.SPACE_MD
                ).move_to(self.layout.main_stage_center())
                st.add(budget_cards)

                self.play(FadeIn(budget_cards, shift=UP * 0.2), run_time=min(trk.duration, 1.0))
                self.wait(max(0.2, trk.duration - 1.0))
