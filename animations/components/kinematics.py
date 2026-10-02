"""
Hardware AI Acceleration - Kinematics & Camera Rig
Provides dynamic camera framing, macro-to-micro zooms, and tactile screen impact effects.
"""

from manim import *
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import theme as th
from components.layout import StageLayout


class SiliconCameraRig(MovingCameraScene):
    """
    Enhanced MovingCameraScene with built-in silicon die navigation,
    tactile screen vibrations on timing/overflow traps, and relative layout.
    """
    def setup(self):
        super().setup()
        th.set_dark(self.camera)
        self.default_frame_width = self.camera.frame.width
        self.default_frame_height = self.camera.frame.height
        self.layout = StageLayout(self)

    def focus_on(self, mobject, buffer_factor=1.35, run_time=th.RATE_SLOW, rate_func=smooth):
        """
        Smoothly swoops and crops the camera to highlight a specific sub-circuit,
        register, or logic gate with a comfortable padding buffer.
        """
        target_center = mobject.get_center()
        target_width = max(mobject.width * buffer_factor, mobject.height * buffer_factor * (16 / 9))
        return self.play(
            self.camera.frame.animate.set_width(target_width).move_to(target_center),
            run_time=run_time,
            rate_func=rate_func
        )

    def reset_camera(self, run_time=th.RATE_NORMAL, rate_func=smooth):
        """
        Restores camera frame back to full-canvas default viewport.
        """
        return self.play(
            self.camera.frame.animate.set_width(self.default_frame_width).move_to(ORIGIN),
            run_time=run_time,
            rate_func=rate_func
        )

    def pan_to(self, target_point, run_time=th.RATE_NORMAL, rate_func=smooth):
        """Pans the camera frame center to target_point while preserving current zoom."""
        return self.play(
            self.camera.frame.animate.move_to(target_point),
            run_time=run_time,
            rate_func=rate_func
        )

    def screen_shake(self, intensity=0.08, cycles=3, run_time=0.25):
        """
        Tactile screen vibration effect triggered when arithmetic overflows,
        saturation clamps, or physical clock latch occurs.
        """
        original_center = self.camera.frame.get_center().copy()
        shifts = []
        dt = run_time / (cycles * 2)
        for i in range(cycles):
            dx = ((-1) ** i) * intensity * (1.0 - i / cycles)
            dy = ((-1) ** (i + 1)) * intensity * 0.5 * (1.0 - i / cycles)
            self.camera.frame.shift(RIGHT * dx + UP * dy)
            self.wait(dt)
        self.camera.frame.move_to(original_center)
