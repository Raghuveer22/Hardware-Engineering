"""
Constraint layout for the kinetic scenes.

Stage coordinates used to be literals (LEFT * 3.2, max_width=12.2, DOWN * 0.42).
Those numbers are a snapshot of one iteration: change the header, the caption,
the frame, or a panel, and every literal is wrong.

This module solves rectangles from the camera frame and from relationships
between siblings. Scenes declare columns, bands, and ports. The solver owns
the numbers.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Region:
    """Axis-aligned rectangle in Manim coordinates (y grows upward)."""

    left: float
    right: float
    bottom: float
    top: float

    def __post_init__(self):
        if self.right < self.left or self.top < self.bottom:
            raise ValueError(
                f"degenerate region left={self.left} right={self.right} "
                f"bottom={self.bottom} top={self.top}"
            )

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.top - self.bottom

    @property
    def center(self):
        return np.array([
            (self.left + self.right) / 2.0,
            (self.bottom + self.top) / 2.0,
            0.0,
        ])

    def inset(self, margin):
        """Shrink equally on every side. A margin that would collapse the
        region returns the center point instead of raising."""
        margin = float(margin)
        if margin <= 0:
            return self
        if self.width <= 2 * margin or self.height <= 2 * margin:
            c = self.center
            return Region(c[0], c[0], c[1], c[1])
        return Region(
            self.left + margin,
            self.right - margin,
            self.bottom + margin,
            self.top - margin,
        )

    def split_x(self, *weights, gap=0.0):
        """Left-to-right bands. Weights are relative; they do not have to sum to 1."""
        return _split(self, weights, gap, axis="x")

    def split_y(self, *weights, gap=0.0):
        """Top-to-bottom bands. The first weight is the top band."""
        return _split(self, weights, gap, axis="y")


def _split(region, weights, gap, axis):
    if len(weights) == 0:
        return []
    total = float(sum(weights))
    if total <= 0:
        raise ValueError("split weights must sum to a positive number")
    n = len(weights)
    gap = max(0.0, float(gap))
    span = region.width if axis == "x" else region.height
    gaps = gap * (n - 1)
    if span <= gaps:
        gap = 0.0
        gaps = 0.0
    usable = span - gaps
    cursor = region.left if axis == "x" else region.top
    out = []
    for i, weight in enumerate(weights):
        size = usable * (float(weight) / total)
        if axis == "x":
            nxt = cursor + size
            out.append(Region(cursor, nxt, region.bottom, region.top))
            cursor = nxt + (gap if i < n - 1 else 0.0)
        else:
            nxt = cursor - size
            out.append(Region(region.left, region.right, nxt, cursor))
            cursor = nxt - (gap if i < n - 1 else 0.0)
    return out


def content_region(frame, header=None, footer=None, margin=0.4, gap=0.2):
    """
    Usable rectangle between the stage header and the caption banner.

    `frame`, `header`, and `footer` only need get_left/get_right/get_top/get_bottom.
    Growing the header or the banner shrinks this region. Callers do not
    subtract those heights themselves.
    """
    margin = float(margin)
    gap = float(gap)
    left = float(frame.get_left()[0]) + margin
    right = float(frame.get_right()[0]) - margin
    if header is not None:
        top = float(header.get_bottom()[1]) - gap
    else:
        top = float(frame.get_top()[1]) - margin
    if footer is not None:
        bottom = float(footer.get_top()[1]) + gap
    else:
        bottom = float(frame.get_bottom()[1]) + margin
    if right < left:
        mid = (left + right) / 2.0
        left = right = mid
    if top < bottom:
        mid = (top + bottom) / 2.0
        top = bottom = mid
    return Region(left, right, bottom, top)


def reserve_lane(region, lane_height, gap=0.1):
    """
    Split a strip off the bottom of `region`.

    Returns (body, lane). The lane is where the end-of-act takeaway sits,
    so a taller diagram cannot cover it. If the region is too short to spare
    a lane, the body is the whole region and the lane is empty at its bottom edge.
    """
    lane_height = float(lane_height)
    gap = float(gap)
    needed = lane_height + gap
    if region.height <= needed + 1.0:
        edge = region.bottom
        return region, Region(region.left, region.right, edge, edge)
    lane = Region(region.left, region.right, region.bottom, region.bottom + lane_height)
    body = Region(region.left, region.right, region.bottom + needed, region.top)
    return body, lane


def snapshot(mob):
    """Center and width before a layout pass. Pair with `map_point`."""
    return (np.array(mob.get_center(), dtype=float), float(mob.width))


def map_point(saved, mob, point):
    """
    Push a point through the same scale-then-move that `place` applied to `mob`.

    Geometry built before the solver runs (a waveform corner, a rising-edge x)
    has to travel with the component. Reading the old x after `place` leaves
    the mark behind.
    """
    pre_center, pre_width = saved
    factor = (float(mob.width) / pre_width) if pre_width else 1.0
    return (np.array(point, dtype=float) - pre_center) * factor + np.array(mob.get_center(), dtype=float)


def place(mob, region, padding=0.0):
    """
    Center `mob` in `region`, scaling it down until it fits.

    Never scales up. A diagram that is already smaller than its slot stays
    at the size it was drawn.
    """
    inner = region.inset(padding) if padding else region
    factor = 1.0
    if mob.width > inner.width > 0:
        factor = min(factor, inner.width / mob.width)
    if mob.height > inner.height > 0:
        factor = min(factor, inner.height / mob.height)
    if factor < 1.0:
        mob.scale(factor)
    mob.move_to(inner.center)
    return mob


def layout_columns(region, mobs, weights=None, gap=0.4, padding=0.0):
    """Place each mobject in its own left-to-right slot of `region`."""
    mobs = [m for m in mobs if m is not None]
    if not mobs:
        return []
    if weights is None:
        weights = [1.0] * len(mobs)
    if len(weights) != len(mobs):
        raise ValueError("column weights must match the number of mobjects")
    slots = region.split_x(*weights, gap=gap)
    for mob, slot in zip(mobs, slots):
        place(mob, slot, padding=padding)
    return slots


def layout_bands(region, mobs, weights=None, gap=0.2, padding=0.0):
    """Place each mobject in its own top-to-bottom slot of `region`."""
    mobs = [m for m in mobs if m is not None]
    if not mobs:
        return []
    if weights is None:
        weights = [1.0] * len(mobs)
    if len(weights) != len(mobs):
        raise ValueError("band weights must match the number of mobjects")
    slots = region.split_y(*weights, gap=gap)
    for mob, slot in zip(mobs, slots):
        place(mob, slot, padding=padding)
    return slots


def _direction_name(direction):
    if isinstance(direction, str):
        return direction.lower()
    vec = np.array(direction, dtype=float).reshape(-1)
    x = float(vec[0]) if vec.size else 0.0
    y = float(vec[1]) if vec.size > 1 else 0.0
    if abs(x) >= abs(y):
        return "left" if x < 0 else "right"
    return "down" if y < 0 else "up"


def edge_at(mob, direction, t=0.5):
    """
    A point on one edge of `mob`.

    `t` runs from 0 to 1 along that edge. Vertical edges start at the bottom.
    Horizontal edges start at the left. `direction` may be 'left'/'right'/
    'up'/'down' or a Manim vector such as LEFT.

    Port positions stay attached to the component when its size changes.
    """
    t = min(1.0, max(0.0, float(t)))
    name = _direction_name(direction)
    if name == "left":
        x = float(mob.get_left()[0])
        y = float(mob.get_bottom()[1]) + t * float(mob.height)
    elif name == "right":
        x = float(mob.get_right()[0])
        y = float(mob.get_bottom()[1]) + t * float(mob.height)
    elif name == "down":
        y = float(mob.get_bottom()[1])
        x = float(mob.get_left()[0]) + t * float(mob.width)
    elif name == "up":
        y = float(mob.get_top()[1])
        x = float(mob.get_left()[0]) + t * float(mob.width)
    else:
        raise ValueError(f"unknown edge {direction!r}")
    return np.array([x, y, 0.0])


def code_line(window, index):
    """Syntax line inside a theme.code_window. The line group is the last child."""
    return window[-1][index]
