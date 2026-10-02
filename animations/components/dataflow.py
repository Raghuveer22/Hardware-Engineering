"""
Hardware AI Acceleration - Dataflow & Interconnect Engine
Provides orthogonal Manhattan-routed wires, voltage pulses, and laser packet streams with TracedPath.
"""

from manim import *
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import theme as th


class SiliconWire(VGroup):
    """
    Manhattan-routed VLSI interconnect wire between two ports.
    Supports bus width annotations (e.g., /8 or /32) and voltage pulse surges.
    """
    def __init__(self, start_point, end_point, manhattan=True, bend_direction="horizontal_first",
                 bus_width=8, stroke_color=th.BORDER, stroke_width=2.5, **kwargs):
        super().__init__(**kwargs)
        self.start_point = np.array(start_point)
        self.end_point = np.array(end_point)
        self.bus_width = bus_width
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width

        if manhattan and (abs(self.start_point[0] - self.end_point[0]) > 0.05) and (abs(self.start_point[1] - self.end_point[1]) > 0.05):
            if bend_direction == "horizontal_first":
                corner = np.array([self.end_point[0], self.start_point[1], 0])
            else:
                corner = np.array([self.start_point[0], self.end_point[1], 0])
            self.wire_path = VMobject(color=stroke_color, stroke_width=stroke_width)
            self.wire_path.set_points_as_corners([self.start_point, corner, self.end_point])
        else:
            self.wire_path = Line(self.start_point, self.end_point, color=stroke_color, stroke_width=stroke_width)

        self.add(self.wire_path)

        # Bus width slash annotation (e.g. /8 or /32)
        if bus_width > 1:
            mid = self.wire_path.point_from_proportion(0.5)
            slash = Line(mid + DL * 0.08, mid + UR * 0.08, color=th.FAINT, stroke_width=1.5)
            lbl = Text(f"{bus_width}", font=th.MONO, font_size=th.FONT_MICRO, color=th.MUTED)
            lbl.next_to(slash, UP, buff=0.05)
            self.bus_tag = VGroup(slash, lbl)
            self.add(self.bus_tag)

    def pulse(self, scene, pulse_color=th.CYAN_LIGHT, run_time=th.RATE_FAST):
        """Creates a voltage surge flash propagating down the wire."""
        flash = self.wire_path.copy().set_color(pulse_color).set_stroke(width=self.stroke_width * 2)
        scene.play(
            ShowPassingFlash(flash, run_time=run_time, time_width=0.4),
            rate_func=linear
        )


class LaserPacketStream:
    """
    Fires glowing data tokens along an arbitrary trajectory using TracedPath.
    """
    @staticmethod
    def shoot_token(scene, start_pt, end_pt, color=th.CYAN, radius=0.12,
                    payload_val=None, run_time=th.RATE_NORMAL, rate_func=smooth):
        """
        Shoots an individual data token with a dissipating light trail.
        """
        dot = Dot(point=start_pt, radius=radius, color=color)
        trail = TracedPath(
            dot.get_center,
            stroke_color=color,
            stroke_width=4.0,
            dissipating_time=0.35
        )
        scene.add(trail, dot)

        anim_group = [dot.animate(run_time=run_time, rate_func=rate_func).move_to(end_pt)]

        if payload_val is not None:
            txt = Text(str(payload_val), font=th.MONO, weight=BOLD,
                       font_size=th.FONT_TINY, color=th.WHITE)
            txt.move_to(start_pt)
            scene.add(txt)
            anim_group.append(txt.animate(run_time=run_time, rate_func=rate_func).move_to(end_pt))

        scene.play(*anim_group)
        scene.remove(dot, trail)
        if payload_val is not None:
            scene.remove(txt)
