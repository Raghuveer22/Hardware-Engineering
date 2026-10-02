"""
Hardware AI Acceleration - Layout & Parameter Derivation Engine
Provides zero-hardcoding stage positioning and mathematical parameter derivations.
"""

import numpy as np
from manim import *
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import theme as th


class HardwareConfig:
    """
    Dynamically derives physical silicon limits, register capacities,
    and timing latencies from architectural parameters.
    """
    def __init__(self, data_width=8, vector_k=4096, array_size=4):
        self.data_width = data_width
        self.vector_k = vector_k
        self.array_size = array_size

        # Two's complement range
        self.min_val = -(1 << (data_width - 1))
        self.max_val = (1 << (data_width - 1)) - 1
        self.total_states = 1 << data_width

        # Multiplier & accumulator headroom math
        self.mult_width = 2 * data_width
        self.mult_max = (1 << (self.mult_width - 1)) - 1
        self.mult_min = -(1 << (self.mult_width - 1))
        
        self.headroom_bits = int(np.ceil(np.log2(vector_k))) if vector_k > 0 else 0
        self.acc_width = self.mult_width + self.headroom_bits
        self.acc_max = (1 << (self.acc_width - 1)) - 1
        self.acc_min = -(1 << (self.acc_width - 1))

        # Systolic array latency formula: 3N - 2 cycles
        self.systolic_latency_cycles = 3 * array_size - 2

    def to_signed_hex(self, val):
        mask = (1 << self.data_width) - 1
        return f"0x{(val & mask):0{self.data_width // 4}X}"

    def to_signed_bin(self, val):
        mask = (1 << self.data_width) - 1
        return bin(val & mask)[2:].zfill(self.data_width)


class StageLayout:
    """
    Calculates responsive viewport regions and placement anchors based on
    the active camera frame, eliminating magic floating-point coordinates.
    """
    def __init__(self, scene_or_camera):
        if hasattr(scene_or_camera, "camera"):
            cam = scene_or_camera.camera
            if hasattr(cam, "frame"):
                self.frame = cam.frame
            else:
                # Standard Scene: create a proxy rectangle matching camera bounds
                self.frame = Rectangle(width=cam.frame_width, height=cam.frame_height).move_to(ORIGIN)
        elif hasattr(scene_or_camera, "frame"):
            self.frame = scene_or_camera.frame
        else:
            self.frame = scene_or_camera

    @property
    def width(self):
        return self.frame.width

    @property
    def height(self):
        return self.frame.height

    @property
    def center(self):
        return self.frame.get_center()

    @property
    def top_edge(self):
        return self.frame.get_top()

    @property
    def bottom_edge(self):
        return self.frame.get_bottom()

    @property
    def left_edge(self):
        return self.frame.get_left()

    @property
    def right_edge(self):
        return self.frame.get_right()

    # Semantic Stage Regions
    def hud_anchor(self, buff=th.SPACE_LG):
        """Top-centered HUD anchor for clock cycles / status tickers."""
        return self.frame.get_top() + DOWN * buff

    def caption_anchor(self, buff=th.SPACE_MD):
        """Bottom-third anchor for narration subtitles / guidance banners."""
        return self.frame.get_bottom() + UP * (0.8 + buff)

    def left_stage(self, offset_ratio=0.25):
        """Left column anchor for code windows or input streams."""
        return self.frame.get_center() + LEFT * (self.width * offset_ratio)

    def right_stage(self, offset_ratio=0.25):
        """Right column anchor for metric cards, schematics, or outputs."""
        return self.frame.get_center() + RIGHT * (self.width * offset_ratio)

    def split_columns(self, left_mobject, right_mobject, buff=th.SPACE_LG):
        """Arranges two main mobjects side-by-side centered in the viewport."""
        group = VGroup(left_mobject, right_mobject).arrange(RIGHT, buff=buff)
        group.move_to(self.center + DOWN * 0.2)
        return group
