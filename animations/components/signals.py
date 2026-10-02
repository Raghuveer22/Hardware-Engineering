"""
Hardware AI Acceleration - Signals & Clock Generation Engine
Provides parameterized clock tracking, live digital logic oscilloscopes,
and cue-point narration synchronization.
"""

from manim import *
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import theme as th


class KineticClock:
    """
    Central hardware clock generator. Tracks cycle count T using a ValueTracker
    and renders a live posedge reactive ticker badge.
    """
    def __init__(self, initial_cycle=0):
        self.tracker = ValueTracker(initial_cycle)

    @property
    def cycle(self):
        return int(round(self.tracker.get_value()))

    def advance(self, scene, delta_cycles=1, run_time=th.RATE_NORMAL, rate_func=linear):
        """Advances hardware clock by delta_cycles with animation."""
        target = self.tracker.get_value() + delta_cycles
        scene.play(
            self.tracker.animate.set_value(target),
            run_time=run_time,
            rate_func=rate_func
        )

    def create_ticker_badge(self, prefix="CYCLE: T = ", color=th.AMBER_LIGHT):
        """Returns a self-updating HUD badge displaying current clock cycle."""
        def _build():
            cyc = int(round(self.tracker.get_value()))
            txt = Text(
                f"{prefix}{cyc} [posedge ↑]",
                font=th.MONO,
                weight=BOLD,
                font_size=th.FONT_CAPTION,
                color=color
            )
            bg = RoundedRectangle(
                corner_radius=0.1,
                width=txt.width + 0.4,
                height=txt.height + 0.25,
                stroke_color=color,
                stroke_width=1.5,
                fill_color="#0a101d",
                fill_opacity=0.92
            )
            txt.move_to(bg)
            return VGroup(bg, txt)
        return always_redraw(_build)


class LiveOscilloscope(VGroup):
    """
    Digital logic timing analyzer displaying multi-channel waveforms
    (e.g., CLK, VALID, DATA, ACC) with a scanning vertical cursor needle.
    """
    def __init__(self, signals=None, total_cycles=6, width=6.2, height=2.2, **kwargs):
        super().__init__(**kwargs)
        self.total_cycles = total_cycles
        self.chart_width = width
        self.chart_height = height
        self.signals = signals or [
            ("CLK", [1, 0] * total_cycles, th.GREEN),
            ("VALID", [0, 1, 1, 1, 0, 0], th.CYAN),
            ("ACC_EN", [0, 0, 1, 1, 1, 0], th.AMBER),
        ]

        # Background panel
        self.bg = RoundedRectangle(
            corner_radius=0.15,
            width=width,
            height=height,
            stroke_color=th.BORDER,
            stroke_width=1.5,
            fill_color="#090e17",
            fill_opacity=0.94
        )
        self.add(self.bg)

        # Header title
        title = Text("DIGITAL TIMING ANALYZER", font=th.MONO, weight=BOLD,
                     font_size=th.FONT_TINY, color=th.MUTED)
        title.next_to(self.bg.get_top(), DOWN, buff=0.12)
        self.add(title)

        # Channel traces
        n_channels = len(self.signals)
        chan_h = (height - 0.7) / n_channels
        self.traces = VGroup()
        self.cursor_x_start = self.bg.get_left()[0] + 1.2
        self.cursor_x_end = self.bg.get_right()[0] - 0.3
        self.span_x = self.cursor_x_end - self.cursor_x_start

        for i, (name, waveform, color) in enumerate(self.signals):
            y_base = self.bg.get_top()[1] - 0.65 - (i * chan_h) - (chan_h * 0.5)
            
            # Label
            lbl = Text(name, font=th.MONO, font_size=th.FONT_TINY, color=color)
            lbl.move_to(np.array([self.bg.get_left()[0] + 0.6, y_base, 0]))
            self.add(lbl)

            # Horizontal baseline
            base_line = Line(
                np.array([self.cursor_x_start, y_base - chan_h * 0.25, 0]),
                np.array([self.cursor_x_end, y_base - chan_h * 0.25, 0]),
                stroke_color="#1e293b",
                stroke_width=1.0
            )
            self.add(base_line)

            # Square wave path
            step_w = self.span_x / len(waveform)
            pts = []
            curr_x = self.cursor_x_start
            h_amp = chan_h * 0.5
            for val in waveform:
                y_val = (y_base - chan_h * 0.25) + (h_amp if val else 0)
                pts.append(np.array([curr_x, y_val, 0]))
                pts.append(np.array([curr_x + step_w, y_val, 0]))
                curr_x += step_w

            wave = VMobject(color=color, stroke_width=2.0)
            wave.set_points_as_corners(pts)
            self.traces.add(wave)

        self.add(self.traces)

        # Scanning cursor line
        self.cursor = Line(
            np.array([self.cursor_x_start, self.bg.get_top()[1] - 0.45, 0]),
            np.array([self.cursor_x_start, self.bg.get_bottom()[1] + 0.15, 0]),
            color=th.RED,
            stroke_width=2.0
        )
        self.add(self.cursor)

    def set_cursor_cycle(self, cycle_idx):
        """Returns animation to shift the cursor needle to a specific cycle."""
        frac = min(1.0, max(0.0, cycle_idx / self.total_cycles))
        target_x = self.cursor_x_start + frac * self.span_x
        curr_y = self.cursor.get_center()[1]
        return self.cursor.animate.move_to(np.array([target_x, curr_y, 0]))


class StoryboardTimeline:
    """
    Manages named narrative cue points, completely eliminating magic self.wait() floats.
    Allows easy retiming when voiceover audio changes.
    """
    def __init__(self, cue_dict=None):
        self.cues = cue_dict or {}

    def wait_for(self, scene, cue_name, default_wait=1.0):
        """Waits for duration mapped to cue_name, or default_wait if unspecified."""
        duration = self.cues.get(cue_name, default_wait)
        scene.wait(duration)
