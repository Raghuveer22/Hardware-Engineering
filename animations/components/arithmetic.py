"""
Hardware AI Acceleration - Arithmetic Intuition Engine
Provides physical silicon metaphors: the 2's complement speedometer wheel,
mechanical spring saturation clamp, and dynamic accumulator fluid tanks.
"""

from manim import *
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import theme as th
from components.layout import HardwareConfig


class TwosComplementWheel(VGroup):
    """
    Parametric Two's Complement Speedometer Dial.
    Visually exposes why positive addition wraps into negative numbers
    and demonstrates physical saturation clamping at the +127 boundary.
    """
    def __init__(self, bits=8, radius=2.3, **kwargs):
        super().__init__(**kwargs)
        self.bits = bits
        self.config = HardwareConfig(data_width=bits)
        self.radius = radius

        # Outer circular dial
        # Top = 0 (12 o'clock = angle PI/2 in standard trig)
        # Clockwise progression: 0 -> +127 at bottom (6 o'clock), then -128 -> -1
        self.positive_arc = Arc(
            radius=radius,
            start_angle=np.pi / 2,
            angle=-np.pi,
            color=th.GREEN,
            stroke_width=4.0
        )
        self.negative_arc = Arc(
            radius=radius,
            start_angle=-np.pi / 2,
            angle=-np.pi,
            color=th.RED,
            stroke_width=4.0
        )
        self.dial_frame = Circle(
            radius=radius + 0.15,
            color=th.BORDER,
            stroke_width=1.5
        )
        self.center_hub = Dot(ORIGIN, radius=0.15, color=th.TEXT)

        # Cardinal Tick Labels
        self.ticks = VGroup()
        label_configs = [
            (0, np.pi / 2, "0", th.TEXT),
            (self.config.max_val // 2, np.pi / 4, f"+{self.config.max_val // 2}", th.GREEN_LIGHT),
            (self.config.max_val, -np.pi / 2 + 0.15, f"+{self.config.max_val}", th.GREEN),
            (self.config.min_val, -np.pi / 2 - 0.15, f"{self.config.min_val}", th.RED),
            (self.config.min_val // 2, -3 * np.pi / 4, f"{self.config.min_val // 2}", th.RED_LIGHT),
        ]
        for val, angle, lbl_str, col in label_configs:
            pos = np.array([np.cos(angle), np.sin(angle), 0]) * (radius + 0.5)
            t = Text(lbl_str, font=th.MONO, weight=BOLD, font_size=th.FONT_TINY, color=col)
            t.move_to(pos)
            self.ticks.add(t)

        # Danger zone marker at the 6 o'clock boundary
        discontinuity_line = DashedLine(
            DOWN * (radius - 0.3),
            DOWN * (radius + 0.3),
            color=th.AMBER,
            stroke_width=2.5
        )
        disc_label = Text("OVERFLOW DISCONTINUITY", font=th.MONO, font_size=th.FONT_MICRO, color=th.AMBER)
        disc_label.next_to(discontinuity_line, DOWN, buff=0.15)
        self.discontinuity_marker = VGroup(discontinuity_line, disc_label)

        # Needle pointer
        self.current_val = 0
        self.needle = Arrow(
            start=ORIGIN,
            end=UP * (radius * 0.8),
            buff=0,
            color=th.CYAN,
            stroke_width=4.0,
            max_tip_length_to_length_ratio=0.18
        )

        # Value readout HUD below center
        self.readout_dec = Text("Decimal: +0", font=th.MONO, weight=BOLD,
                                font_size=th.FONT_CAPTION, color=th.CYAN_LIGHT)
        self.readout_bin = Text("Binary:  00000000", font=th.MONO,
                                font_size=th.FONT_TINY, color=th.MUTED)
        self.readout_group = VGroup(self.readout_dec, self.readout_bin).arrange(DOWN, buff=0.1)
        self.readout_group.move_to(DOWN * (radius * 0.4))

        # Clamp barrier (hidden by default)
        self.clamp_bar = Rectangle(
            width=0.6,
            height=0.15,
            fill_color=th.AMBER,
            fill_opacity=1.0,
            stroke_color=th.WHITE,
            stroke_width=2.0
        )
        self.clamp_bar.move_to(DOWN * (radius - 0.05) + RIGHT * 0.15)
        self.clamp_label = Text("SATURATION CLAMP (+127)", font=th.MONO, weight=BOLD,
                                font_size=th.FONT_MICRO, color=th.AMBER)
        self.clamp_label.next_to(self.clamp_bar, RIGHT, buff=0.15)
        self.clamp_unit = VGroup(self.clamp_bar, self.clamp_label)
        self.clamp_active = False

        self.add(
            self.dial_frame, self.positive_arc, self.negative_arc,
            self.center_hub, self.ticks, self.discontinuity_marker,
            self.needle, self.readout_group
        )

    def val_to_angle(self, val):
        """Maps signed integer to dial angle (top=0, clockwise)."""
        # 0 -> PI/2
        # +127 -> -PI/2 + epsilon (bottom right)
        # -128 -> -PI/2 - epsilon (bottom left)
        # -1 -> PI/2 + delta (top left)
        if val >= 0:
            frac = val / (self.config.max_val + 1)
            return (np.pi / 2) - (frac * np.pi)
        else:
            # val in [-128, -1]
            frac = (val - self.config.min_val) / abs(self.config.min_val)
            return (-np.pi / 2) - (frac * np.pi)

    def set_value_instant(self, val):
        """Immediately snaps needle and readout to val."""
        self.current_val = val
        angle = self.val_to_angle(val)
        target_pt = np.array([np.cos(angle), np.sin(angle), 0]) * (self.radius * 0.8)
        self.needle.put_start_and_end_on(ORIGIN, target_pt)
        col = th.GREEN_LIGHT if val >= 0 else th.RED
        self.readout_dec.become(
            Text(f"Decimal: {val:+d}", font=th.MONO, weight=BOLD,
                 font_size=th.FONT_CAPTION, color=col).move_to(self.readout_dec)
        )
        self.readout_bin.become(
            Text(f"Binary:  {self.config.to_signed_bin(val)}", font=th.MONO,
                 font_size=th.FONT_TINY, color=th.MUTED).move_to(self.readout_bin)
        )

    def animate_sweep(self, scene, target_val, run_time=th.RATE_NORMAL, clamp=False):
        """
        Smoothly sweeps the needle across the dial.
        If clamp=True, stops at +127 and emits an elastic clamp bounce.
        """
        start_val = self.current_val
        is_overflow = (target_val > self.config.max_val) and not clamp
        final_val = min(self.config.max_val, target_val) if clamp else (
            ((target_val + 128) % 256) - 128 if target_val > self.config.max_val else target_val
        )

        # Animate continuous intermediate steps
        steps = 30
        val_path = np.linspace(start_val, target_val, steps)
        dt = run_time / steps

        for v in val_path:
            int_v = int(round(v))
            if clamp and int_v >= self.config.max_val:
                self.set_value_instant(self.config.max_val)
                scene.wait(dt)
                break
            elif not clamp and int_v > self.config.max_val:
                # Wrapped around!
                wrapped = ((int_v + 128) % 256) - 128
                self.set_value_instant(wrapped)
            else:
                self.set_value_instant(int_v)
            scene.wait(dt)

        self.set_value_instant(final_val)

    def deploy_clamp_barrier(self, scene):
        """Drops the mechanical saturation clamp barrier into place."""
        self.clamp_active = True
        scene.play(
            FadeIn(self.clamp_unit, shift=DOWN * 0.4),
            run_time=th.RATE_FAST,
            rate_func=rate_functions.ease_out_bounce
        )
