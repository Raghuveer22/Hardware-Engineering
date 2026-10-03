"""The layout solver owns stage coordinates. These tests pin that contract."""

import importlib.util
from pathlib import Path

import numpy as np

_SPEC = importlib.util.spec_from_file_location(
    "constraints",
    Path(__file__).resolve().parents[1] / "animations" / "components" / "constraints.py",
)
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)

Region = _MOD.Region
content_region = _MOD.content_region
edge_at = _MOD.edge_at
layout_columns = _MOD.layout_columns
map_point = _MOD.map_point
place = _MOD.place
reserve_lane = _MOD.reserve_lane
snapshot = _MOD.snapshot


class _Edge:
    def __init__(self, left, right, bottom, top):
        self._left = np.array([left, 0.0, 0.0])
        self._right = np.array([right, 0.0, 0.0])
        self._bottom = np.array([0.0, bottom, 0.0])
        self._top = np.array([0.0, top, 0.0])
        self.width = right - left
        self.height = top - bottom

    def get_left(self):
        return self._left

    def get_right(self):
        return self._right

    def get_bottom(self):
        return self._bottom

    def get_top(self):
        return self._top


class _Mob:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center = np.zeros(3)
        self.scale_factor = 1.0

    def scale(self, factor):
        self.width *= factor
        self.height *= factor
        self.scale_factor *= factor
        return self

    def move_to(self, point):
        self.center = np.array(point, dtype=float)
        return self

    def get_center(self):
        return self.center

    def get_left(self):
        return np.array([self.center[0] - self.width / 2, self.center[1], 0.0])

    def get_right(self):
        return np.array([self.center[0] + self.width / 2, self.center[1], 0.0])

    def get_bottom(self):
        return np.array([self.center[0], self.center[1] - self.height / 2, 0.0])

    def get_top(self):
        return np.array([self.center[0], self.center[1] + self.height / 2, 0.0])


def test_split_x_respects_weights_and_gap():
    region = Region(-6, 6, -2, 2)
    left, right = region.split_x(1, 3, gap=2)
    assert left.left == -6
    assert right.right == 6
    assert abs((left.width + right.width) - (region.width - 2)) < 1e-9
    assert abs(right.width / left.width - 3) < 1e-9
    assert left.right + 2 == right.left


def test_split_y_is_top_to_bottom():
    region = Region(0, 10, 0, 9)
    top, bottom = region.split_y(1, 2, gap=0)
    assert top.top == 9
    assert bottom.bottom == 0
    assert top.height * 2 == bottom.height
    assert top.bottom == bottom.top


def test_taller_header_shrinks_content():
    frame = _Edge(-7, 7, -4, 4)
    short = content_region(frame, header=_Edge(-2, 2, 2.5, 3.5), footer=_Edge(-6, 6, -3.5, -2.5), margin=0.4, gap=0.2)
    tall = content_region(frame, header=_Edge(-2, 2, 1.0, 3.5), footer=_Edge(-6, 6, -3.5, -2.5), margin=0.4, gap=0.2)
    assert tall.top < short.top
    assert tall.bottom == short.bottom
    assert tall.height < short.height


def test_place_scales_down_and_never_up():
    region = Region(-2, 2, -1, 1)
    big = _Mob(8, 2)
    place(big, region)
    assert big.width <= region.width + 1e-9
    assert big.height <= region.height + 1e-9
    assert abs(big.center[0]) < 1e-9

    small = _Mob(1, 0.5)
    place(small, region)
    assert small.scale_factor == 1.0
    assert abs(small.center[1]) < 1e-9


def test_columns_track_region_when_it_changes():
    narrow = Region(-4, 4, -1, 1)
    wide = Region(-8, 8, -1, 1)
    first = [_Mob(3, 1), _Mob(3, 1)]
    second = [_Mob(3, 1), _Mob(3, 1)]
    layout_columns(narrow, first, gap=0.4)
    layout_columns(wide, second, gap=0.4)
    assert first[1].center[0] < second[1].center[0]
    assert first[0].center[0] > second[0].center[0]


def test_takeaway_lane_stays_below_the_diagram():
    body, lane = reserve_lane(Region(-5, 5, -2, 3), lane_height=1.0, gap=0.2)
    assert lane.top <= body.bottom
    assert abs(lane.height - 1.0) < 1e-9
    assert body.top == 3


def test_map_point_follows_scale_then_move():
    mob = _Mob(4, 2)
    mob.move_to(np.array([0.0, 0.0, 0.0]))
    saved = snapshot(mob)
    mob.scale(0.5)
    mob.move_to(np.array([10.0, 0.0, 0.0]))
    mapped = map_point(saved, mob, np.array([2.0, 0.0, 0.0]))
    assert abs(mapped[0] - 11.0) < 1e-9
    assert abs(mapped[1]) < 1e-9


def test_edge_at_follows_the_component():
    mob = _Mob(4, 2)
    mob.move_to(np.array([10.0, 5.0, 0.0]))
    top_left = edge_at(mob, "left", 1.0)
    mid_right = edge_at(mob, np.array([1.0, 0.0, 0.0]), 0.5)
    assert abs(top_left[0] - 8.0) < 1e-9
    assert abs(top_left[1] - 6.0) < 1e-9
    assert abs(mid_right[0] - 12.0) < 1e-9
    assert abs(mid_right[1] - 5.0) < 1e-9
