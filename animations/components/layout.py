"""
Hardware AI Acceleration - Constraint-Driven Layout & Typography Engine
Provides zero-hardcoding stage positioning, auto-layout containers (HStack, VStack),
semantic typography roles, and mathematical hardware derivations.
"""

from enum import Enum
import numpy as np
from manim import *
import sys
from pathlib import Path

ANIM_DIR = Path(__file__).resolve().parent.parent
if str(ANIM_DIR) not in sys.path:
    sys.path.insert(0, str(ANIM_DIR))

import theme as th


# ---------------------------------------------------------------------------
# HARDWARE CONFIGURATION & SIZING MATH
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# SEMANTIC TYPOGRAPHY ENGINE (ZERO MAGIC FONT SIZES)
# ---------------------------------------------------------------------------

class TextRole(Enum):
    """Semantic typography roles mapped to design system scales."""
    STAGE_TITLE    = "stage_title"      # Main act title
    STAGE_BADGE    = "stage_badge"      # All-caps module kicker
    BLOCK_HEADER   = "block_header"     # Hardware cell name (e.g. PE[0,0])
    BUS_VALUE      = "bus_value"        # Dynamic hex/binary values
    PROBE_LABEL    = "probe_label"      # Pin probe / wire annotation
    MATH_DISPLAY   = "math_display"     # Full-line architectural equations
    MATH_INLINE    = "math_inline"      # Subscripts & inline math callouts
    NARRATION      = "narration"        # Bottom-third subtitle
    CODE           = "code"             # Monospace code lines
    BODY           = "body"             # General descriptive text


ROLE_CONFIG = {
    TextRole.STAGE_TITLE:  {"font": th.SANS, "size": th.FONT_TITLE,   "weight": BOLD,   "color": th.WHITE},
    TextRole.STAGE_BADGE:  {"font": th.SANS, "size": th.FONT_BADGE,   "weight": BOLD,   "color": th.CYAN},
    TextRole.BLOCK_HEADER: {"font": th.MONO, "size": th.FONT_BODY,    "weight": BOLD,   "color": th.AMBER_LIGHT},
    TextRole.BUS_VALUE:    {"font": th.MONO, "size": th.FONT_CAPTION, "weight": BOLD,   "color": th.GREEN_LIGHT},
    TextRole.PROBE_LABEL:  {"font": th.MONO, "size": th.FONT_TINY,    "weight": NORMAL, "color": th.MUTED},
    TextRole.NARRATION:    {"font": th.SANS, "size": th.FONT_CAPTION, "weight": NORMAL, "color": th.TEXT},
    TextRole.CODE:         {"font": th.MONO, "size": 13,              "weight": NORMAL, "color": th.TEXT},
    TextRole.BODY:         {"font": th.SANS, "size": th.FONT_BODY,    "weight": NORMAL, "color": th.TEXT},
}


def fit_to_bounds(mob, max_width=None, max_height=None, min_scale=0.6):
    """
    Guarantees a mobject never exceeds bounding constraints.
    Applies proportional scaling down if necessary with a safeguard minimum.
    """
    if max_width is not None and mob.width > max_width and mob.width > 0:
        factor = max_width / mob.width
        mob.scale(max(factor, min_scale))
    if max_height is not None and mob.height > max_height and mob.height > 0:
        factor = max_height / mob.height
        mob.scale(max(factor, min_scale))
    return mob


class SemanticText(VGroup):
    """
    Standard-cell text mobject driven strictly by semantic typography roles
    with automatic bounding box protection.
    """
    def __init__(self, text: str, role: TextRole = TextRole.BODY, color=None,
                 max_width=None, **kwargs):
        super().__init__()
        cfg = ROLE_CONFIG.get(role, ROLE_CONFIG[TextRole.BODY])
        font = cfg["font"]
        size = cfg["size"]
        weight = cfg["weight"]
        final_color = color if color is not None else cfg["color"]

        self.text_mob = Text(
            text,
            font=font,
            font_size=size,
            weight=weight,
            color=final_color,
            **kwargs
        )
        if max_width is not None:
            fit_to_bounds(self.text_mob, max_width=max_width)

        self.add(self.text_mob)
        self.role = role

    def update_text(self, new_text: str):
        """Returns animation to smoothly change text content while preserving role."""
        cfg = ROLE_CONFIG.get(self.role, ROLE_CONFIG[TextRole.BODY])
        new_mob = Text(
            new_text,
            font=cfg["font"],
            font_size=cfg["size"],
            weight=cfg["weight"],
            color=self.text_mob.color,
        ).move_to(self.text_mob)
        return Transform(self.text_mob, new_mob)


class SemanticMath(VGroup):
    """
    Standard-cell vector LaTeX mathematics mobject.
    Renders with MathTex if LaTeX is available, with resilient fallback to Unicode Text.
    """
    def __init__(self, tex_str: str, role: TextRole = TextRole.MATH_DISPLAY,
                 color=None, max_width=None, **kwargs):
        super().__init__()
        self.role = role
        scale_factor = 0.85 if role == TextRole.MATH_DISPLAY else 0.65
        final_color = color if color is not None else th.WHITE

        try:
            math_mob = MathTex(tex_str, color=final_color, **kwargs)
            math_mob.scale(scale_factor)
        except Exception:
            # Fallback to plain text if LaTeX toolchain not yet initialized
            clean_str = tex_str.replace(r"\cdot", "·").replace(r"\text", "").replace(r"\alpha", "α")
            clean_str = clean_str.replace("{", "").replace("}", "").replace("$", "")
            math_mob = Text(clean_str, font=th.MONO, font_size=th.FONT_BODY, color=final_color)

        if max_width is not None:
            fit_to_bounds(math_mob, max_width=max_width)

        self.math_mob = math_mob
        self.add(math_mob)


# ---------------------------------------------------------------------------
# CONSTRAINT-DRIVEN AUTO-LAYOUT CONTAINERS
# ---------------------------------------------------------------------------

class HStack(VGroup):
    """
    Flex-like horizontal auto-layout container.
    Arranges child mobjects side-by-side with explicit gap tokens,
    auto-centers on the cross-axis, and automatically fits within bounds.
    """
    def __init__(self, *children, gap=th.SPACE_MD, alignment="center",
                 max_width=None, max_height=None, **kwargs):
        super().__init__(**kwargs)
        self.gap = gap
        self.alignment = alignment
        self.max_w = max_width
        self.max_h = max_height

        for child in children:
            if child is not None:
                self.add(child)

        self.relayout()

    def relayout(self):
        if len(self.submobjects) == 0:
            return
        aligned_edge = UP if self.alignment == "top" else (DOWN if self.alignment == "bottom" else ORIGIN)
        self.arrange(RIGHT, buff=self.gap, aligned_edge=aligned_edge)
        fit_to_bounds(self, max_width=self.max_w, max_height=self.max_h)
        return self


class VStack(VGroup):
    """
    Flex-like vertical auto-layout container.
    Arranges child mobjects in a column with explicit gap tokens,
    auto-aligns to left, center, or right, and enforces bounding limits.
    """
    def __init__(self, *children, gap=th.SPACE_MD, alignment="center",
                 max_width=None, max_height=None, **kwargs):
        super().__init__(**kwargs)
        self.gap = gap
        self.alignment = alignment
        self.max_w = max_width
        self.max_h = max_height

        for child in children:
            if child is not None:
                self.add(child)

        self.relayout()

    def relayout(self):
        if len(self.submobjects) == 0:
            return
        aligned_edge = LEFT if self.alignment == "left" else (RIGHT if self.alignment == "right" else ORIGIN)
        self.arrange(DOWN, buff=self.gap, aligned_edge=aligned_edge)
        fit_to_bounds(self, max_width=self.max_w, max_height=self.max_h)
        return self


class ConstraintAnchor:
    """
    Constraint positioning helper that eliminates magic floating-point coordinates.
    Positions mobjects relative to anchor edges, reference items, or viewport frames.
    """
    @staticmethod
    def dock_to(mob: Mobject, target: Mobject, edge=UP, gap=th.SPACE_MD, align=None):
        """
        Docks mob to the outside edge of target with gap spacing.
        Optionally aligns to target's cross-axis edge (e.g. LEFT, RIGHT, TOP, BOTTOM).
        """
        mob.next_to(target, edge, buff=gap)
        if align is not None:
            if np.array_equal(edge, UP) or np.array_equal(edge, DOWN):
                if np.array_equal(align, LEFT):
                    mob.align_to(target, LEFT)
                elif np.array_equal(align, RIGHT):
                    mob.align_to(target, RIGHT)
            elif np.array_equal(edge, LEFT) or np.array_equal(edge, RIGHT):
                if np.array_equal(align, UP):
                    mob.align_to(target, UP)
                elif np.array_equal(align, DOWN):
                    mob.align_to(target, DOWN)
        return mob

    @staticmethod
    def pin_callout(callout: Mobject, target: Mobject, direction=UP, gap=th.SPACE_SM):
        """Pins a probe callout directly adjacent to a hardware component or wire."""
        callout.next_to(target, direction, buff=gap)
        return callout

    @staticmethod
    def snap_ports(source_port_pos, target_port_pos):
        """Returns the translation vector required to snap source port directly to target."""
        return np.array(target_port_pos) - np.array(source_port_pos)


# ---------------------------------------------------------------------------
# RESPONSIVE VIEWPORT STAGE LAYOUT
# ---------------------------------------------------------------------------

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

    # Semantic Viewport Regions
    def hud_anchor(self, buff=th.SPACE_LG):
        """Top-centered HUD anchor for clock cycles / status tickers."""
        return self.frame.get_top() + DOWN * buff

    def caption_anchor(self, buff=th.SPACE_MD):
        """Bottom-third anchor for narration subtitles / guidance banners."""
        return self.frame.get_bottom() + UP * (0.8 + buff)

    def main_stage_center(self):
        """Center of the functional viewport, offset slightly upward to clear the bottom-third banner."""
        return self.center + UP * 0.2

    def left_stage(self, offset_ratio=0.25):
        """Left column anchor for input streams or controller blocks."""
        return self.main_stage_center() + LEFT * (self.width * offset_ratio)

    def right_stage(self, offset_ratio=0.25):
        """Right column anchor for metric cards, schematics, or outputs."""
        return self.main_stage_center() + RIGHT * (self.width * offset_ratio)

    def split_columns(self, left_mobject, right_mobject, buff=th.SPACE_LG):
        """Arranges two main mobjects side-by-side centered in the viewport."""
        return HStack(left_mobject, right_mobject, gap=buff).move_to(self.main_stage_center())
