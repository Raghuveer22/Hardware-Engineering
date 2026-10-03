"""
Hardware AI Acceleration - Kinematics, Camera Rig & Stage Lifecycle
Provides dynamic camera framing, voiceover audio synchronization, declarative stage lifecycle,
and continuous morphing transitions between architectural acts.
"""

from manim import *
import numpy as np
import sys
import re
from pathlib import Path

ANIM_DIR = Path(__file__).resolve().parent.parent
if str(ANIM_DIR) not in sys.path:
    sys.path.insert(0, str(ANIM_DIR))

import theme as th
from components.layout import StageLayout, TextRole, SemanticText, ConstraintAnchor, fit_to_bounds


class VoiceoverTracker:
    """
    Tracks voiceover audio clip duration to auto-scale animation runtimes.
    Eliminates magic self.wait() floats and prevents audio-visual drift.
    """
    def __init__(self, text: str, audio_path: Path = None, default_wpm: int = 145):
        self.text = text
        self.audio_path = audio_path
        self.duration = self._derive_duration(default_wpm)

    def _derive_duration(self, wpm: int) -> float:
        # Check if real audio file exists and has duration
        if self.audio_path and self.audio_path.exists():
            try:
                import wave
                with wave.open(str(self.audio_path), 'rb') as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    return max(0.5, float(frames) / float(rate))
            except Exception:
                pass

        # High-accuracy fallback estimation: ~145 WPM + punctuation pauses
        words = len(re.findall(r'\b\w+\b', self.text))
        seconds_per_word = 60.0 / wpm
        base_dur = words * seconds_per_word
        # Add slight pause for commas, semicolons, and periods
        pauses = self.text.count('.') * 0.35 + self.text.count(',') * 0.15 + self.text.count('!') * 0.4
        return max(1.2, base_dur + pauses)


class StageContext:
    """
    Context manager managing the lifecycle of an architectural act / stage.
    Handles automatic mobject registration, HUD headers, bottom narration banners,
    and zero-boilerplate continuous morphing exits.
    """
    def __init__(self, scene, act_id: str, title: str, subtitle: str = "", narration: str = ""):
        self.scene = scene
        self.act_id = act_id
        self.title = title
        self.subtitle = subtitle
        self.narration = narration
        self.mobjects = []
        self.header_group = None
        self.banner = None
        self.morphed = False

    def __enter__(self):
        # Build stage header docked to top HUD
        kicker_text = f"{self.act_id}: {self.title.upper()}"
        self.kicker = SemanticText(kicker_text, role=TextRole.STAGE_BADGE, color=th.CYAN)
        
        if self.subtitle:
            self.sub_t = SemanticText(self.subtitle, role=TextRole.STAGE_TITLE, color=th.WHITE)
            fit_to_bounds(self.sub_t, max_width=8.0)
            self.header_group = VGroup(self.kicker, self.sub_t).arrange(DOWN, buff=0.10)
        else:
            self.header_group = VGroup(self.kicker)

        fit_to_bounds(self.header_group, max_width=8.2)
        self.header_group.to_edge(UP, buff=0.35)
        self.scene.play(FadeIn(self.header_group, shift=DOWN * 0.2), run_time=0.5)

        # Build bottom narration banner if provided
        if self.narration:
            self.banner = th.narration_banner(self.narration)
            self.scene.play(FadeIn(self.banner, shift=UP * 0.2), run_time=0.4)

        return self

    def add(self, *mobs):
        """Registers mobjects into the stage tracking pool and adds to scene."""
        for mob in mobs:
            if mob is not None:
                self.mobjects.append(mob)
                self.scene.add(mob)
        return mobs[0] if len(mobs) == 1 else mobs

    def register(self, *mobs):
        """Registers mobjects for automatic stage lifecycle tracking without immediate scene.add."""
        for mob in mobs:
            if mob is not None and mob not in self.mobjects:
                self.mobjects.append(mob)
        return mobs[0] if len(mobs) == 1 else mobs

    def update_narration(self, new_narration: str, run_time=0.5):
        """Smoothly updates the bottom-third guidance banner."""
        self.narration = new_narration
        new_banner = th.narration_banner(new_narration)
        if self.banner is not None:
            self.scene.play(Transform(self.banner, new_banner), run_time=run_time)
        else:
            self.banner = new_banner
            self.scene.play(FadeIn(self.banner, shift=UP * 0.2), run_time=run_time)

    def takeaway(self, text: str, wait: float = 1.4, color=th.CYAN, run_time=0.6):
        """
        Shows a one-line "so the point is..." transition bar at the end of an act,
        giving the viewer time to absorb the concept before the next depth jump.
        The bar is registered into the stage pool so it cleans up with the act.
        """
        bar = th.takeaway_callout(text, color=color)
        bar.move_to(self.scene.layout.main_stage_center())
        self.scene.play(FadeIn(bar, shift=UP * 0.15), run_time=run_time)
        self.scene.wait(wait)
        self.scene.play(FadeOut(bar), run_time=0.35)

    def morph_to(self, target_mobjects, run_time=th.RATE_NORMAL):
        """
        Continuous morphing transition: transforms active stage mobjects directly
        into target mobjects of the next stage (3Blue1Brown principle).
        """
        self.morphed = True
        fade_anims = [FadeOut(self.header_group)]
        if self.banner:
            fade_anims.append(FadeOut(self.banner))

        morph_anims = []
        if isinstance(target_mobjects, (list, tuple)) and len(target_mobjects) == len(self.mobjects):
            for src, tgt in zip(self.mobjects, target_mobjects):
                morph_anims.append(ReplacementTransform(src, tgt))
        elif isinstance(target_mobjects, Mobject):
            src_group = VGroup(*self.mobjects)
            morph_anims.append(ReplacementTransform(src_group, target_mobjects))

        self.scene.play(*fade_anims, *morph_anims, run_time=run_time)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Automated smooth exit cleanup if not explicitly morphed
        if not self.morphed:
            cleanups = []
            if self.header_group:
                cleanups.append(FadeOut(self.header_group))
            if self.banner:
                cleanups.append(FadeOut(self.banner))
            for mob in self.mobjects:
                cleanups.append(FadeOut(mob))
            if cleanups:
                self.scene.play(*cleanups, run_time=0.6)


class SiliconCameraRig(MovingCameraScene):
    """
    Camera Rig with built-in silicon die navigation,
    tactile screen vibrations on timing/overflow traps, and relative layout.
    """
    def setup(self):
        super().setup()
        th.set_dark(self.camera)
        self.default_frame_width = self.camera.frame.width
        self.default_frame_height = self.camera.frame.height
        self.layout = StageLayout(self)

    def focus_on(self, mobject, buffer_factor=1.35, run_time=th.RATE_SLOW, rate_func=smooth):
        """Smoothly swoops and crops camera to a specific sub-circuit or gate."""
        target_center = mobject.get_center()
        target_width = max(mobject.width * buffer_factor, mobject.height * buffer_factor * (16 / 9))
        return self.play(
            self.camera.frame.animate.set_width(target_width).move_to(target_center),
            run_time=run_time,
            rate_func=rate_func
        )

    def reset_camera(self, run_time=th.RATE_NORMAL, rate_func=smooth):
        """Restores camera frame back to full-canvas default viewport."""
        return self.play(
            self.camera.frame.animate.set_width(self.default_frame_width).move_to(ORIGIN),
            run_time=run_time,
            rate_func=rate_func
        )

    def pan_to(self, target_point, run_time=th.RATE_NORMAL, rate_func=smooth):
        """Pans camera frame center to target_point while preserving current zoom."""
        return self.play(
            self.camera.frame.animate.move_to(target_point),
            run_time=run_time,
            rate_func=rate_func
        )

    def screen_shake(self, intensity=0.08, cycles=3, run_time=0.25):
        """Tactile screen vibration effect triggered when arithmetic overflows or clamps."""
        original_center = self.camera.frame.get_center().copy()
        dt = run_time / (cycles * 2)
        for i in range(cycles):
            dx = ((-1) ** i) * intensity * (1.0 - i / cycles)
            dy = ((-1) ** (i + 1)) * intensity * 0.5 * (1.0 - i / cycles)
            self.camera.frame.shift(RIGHT * dx + UP * dy)
            self.wait(dt)
        self.camera.frame.move_to(original_center)


class KineticSiliconScene(SiliconCameraRig):
    """
    Base Scene class for all Hardware AI Acceleration animations.
    Equipped with voiceover duration synchronization, declarative stage lifecycle,
    and continuous component morphing.
    """
    def voiceover(self, text: str, audio_path: Path = None):
        """
        Voiceover context manager pattern.
        Yields a VoiceoverTracker containing the exact duration of the spoken text.
        """
        class _VoiceoverContext:
            def __init__(self, scene, txt, apath):
                self.scene = scene
                self.tracker = VoiceoverTracker(txt, apath)

            def __enter__(self):
                return self.tracker

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        return _VoiceoverContext(self, text, audio_path)

    def stage(self, act_id: str, title: str, subtitle: str = "", narration: str = ""):
        """
        Declarative stage context manager.
        Automates headers, mobject tracking, and smooth transitions.
        """
        return StageContext(self, act_id, title, subtitle, narration)

    def morph_components(self, source, target, run_time=th.RATE_NORMAL):
        """Performs continuous morphing transformation between two silicon components."""
        return self.play(ReplacementTransform(source, target), run_time=run_time)
