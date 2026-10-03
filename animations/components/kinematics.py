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
from components.constraints import content_region, layout_bands, layout_columns, place, reserve_lane


def _lead_sentence(text: str) -> str:
    """First sentence, ignoring decimals such as 0.2."""
    match = re.search(r"[A-Za-z][.!?](?:\s|$)", text.strip())
    if not match:
        return text.strip()
    return text.strip()[: match.end()].strip()


class VoiceoverTracker:
    """
    Estimates how long a line takes to say.

    A real duration is used only when audio_path points at a WAV file.
    Otherwise this is a 145 words-per-minute guess. It does not synthesize
    speech and it does not lock a later ffmpeg mux to the Manim timeline.
    narrate_video.py is a separate pass and only covers the scenes in SCRIPTS.
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
        self.content = None
        self.takeaway_lane = None
        self.morphed = False

    def _header_max_width(self):
        """Header stays clear of the corner HUD. The HUD width is measured, not guessed."""
        frame_w = self.scene.camera.frame.width
        hud = getattr(self.scene, "hud", None)
        hud_w = float(getattr(hud, "width", 0.0) or 0.0)
        side = (hud_w + th.SPACE_MD) if hud_w > 0 else th.SPACE_XL
        return max(4.5, frame_w - 2 * side)

    def _banner_width(self):
        return max(6.0, self.scene.camera.frame.width - 2 * th.SPACE_LG)

    def refresh_content(self):
        """
        Recompute the diagram rectangle from the live header and caption.

        A longer title or a taller banner shrinks `content`. The takeaway
        keeps a reserved lane at the bottom so it does not cover the diagram.
        """
        full = content_region(
            self.scene.camera.frame,
            header=self.header_group,
            footer=self.banner,
            margin=th.SPACE_MD,
            gap=th.SPACE_SM,
        )
        self.content, self.takeaway_lane = reserve_lane(
            full, th.TAKEAWAY_HEIGHT, gap=th.SPACE_XS,
        )
        return self.content

    def place(self, mob, region=None, padding=0.0):
        """Fit `mob` inside a solved region. Defaults to the diagram area."""
        return place(mob, self.content if region is None else region, padding=padding)

    def columns(self, *mobs, weights=None, gap=th.SPACE_LG, padding=0.0, region=None):
        """Left-to-right slots. Weights are relative shares of the region."""
        return layout_columns(
            self.content if region is None else region,
            mobs, weights=weights, gap=gap, padding=padding,
        )

    def bands(self, *mobs, weights=None, gap=th.SPACE_SM, padding=0.0, region=None):
        """Top-to-bottom slots. The first mobject is the top band."""
        return layout_bands(
            self.content if region is None else region,
            mobs, weights=weights, gap=gap, padding=padding,
        )

    def __enter__(self):
        # Build stage header docked to top HUD
        kicker_text = f"{self.act_id}: {self.title.upper()}"
        self.kicker = SemanticText(kicker_text, role=TextRole.STAGE_BADGE, color=th.CYAN)
        header_w = self._header_max_width()

        if self.subtitle:
            self.sub_t = SemanticText(self.subtitle, role=TextRole.STAGE_TITLE, color=th.WHITE)
            fit_to_bounds(self.sub_t, max_width=header_w)
            self.header_group = VGroup(self.kicker, self.sub_t).arrange(DOWN, buff=th.SPACE_XS)
        else:
            self.header_group = VGroup(self.kicker)

        fit_to_bounds(self.header_group, max_width=header_w)
        self.header_group.to_edge(UP, buff=th.SPACE_MD)
        # Header and caption arrive together so an act does not open on an
        # empty frame with only a fading title.
        enter = [FadeIn(self.header_group, shift=DOWN * th.SPACE_SM)]
        if self.narration:
            self.banner = th.narration_banner(
                _lead_sentence(self.narration), width=self._banner_width(),
            )
            enter.append(FadeIn(self.banner, shift=UP * th.SPACE_SM))
        self.scene.play(*enter, run_time=0.35)

        self.refresh_content()
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
        # Same rule as the opening banner: one sentence. A wrapped second
        # line grows into whatever was placed just above the caption.
        new_banner = th.narration_banner(
            _lead_sentence(new_narration), width=self._banner_width(),
        )
        if self.banner is not None:
            self.scene.play(Transform(self.banner, new_banner), run_time=run_time)
        else:
            self.banner = new_banner
            self.scene.play(FadeIn(self.banner, shift=UP * th.SPACE_SM), run_time=run_time)

    def takeaway(self, text: str, wait: float = 1.4, color=th.CYAN, run_time=0.6):
        """
        Shows a one-line "so the point is..." transition bar at the end of an act,
        giving the viewer time to absorb the concept before the next depth jump.
        The bar is registered into the stage pool so it cleans up with the act.
        """
        lane = self.takeaway_lane
        bar = th.takeaway_callout(
            text,
            color=color,
            width=self.content.width if self.content is not None else None,
            height=th.TAKEAWAY_HEIGHT,
        )
        if lane is not None and lane.height > 0:
            self.place(bar, lane)
        elif self.banner is not None:
            bar.next_to(self.banner, UP, buff=th.SPACE_SM)
        else:
            bar.to_edge(DOWN, buff=th.SPACE_MD)
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
                self.scene.play(*cleanups, run_time=0.35)


class WorldContext:
    """
    One picture for a whole scene.

    No act title, no narration banner, no takeaway lane. The cast stays
    when the context exits, so a later beat can move the camera or morph
    what is already on screen instead of fading up a new slide.
    """

    def __init__(self, scene):
        self.scene = scene
        self.cast = []
        frame = scene.camera.frame
        self.content = content_region(frame, header=None, footer=None, margin=th.SPACE_LG, gap=0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def keep(self, *mobs):
        for mob in mobs:
            if mob is not None and mob not in self.cast:
                self.cast.append(mob)
        if len(mobs) == 1:
            return mobs[0]
        return mobs

    def show(self, *mobs, run_time=0.5, shift=UP * 0.1):
        """Fade mobjects in and remember them as part of the picture."""
        self.keep(*mobs)
        anims = [FadeIn(m, shift=shift) for m in mobs if m is not None]
        if anims:
            self.scene.play(*anims, run_time=run_time)
        return run_time

    def drop(self, *mobs, run_time=0.35):
        """Remove a temporary piece. Anything not passed here stays."""
        present = [m for m in mobs if m is not None]
        if not present:
            return 0.0
        self.scene.play(*[FadeOut(m) for m in present], run_time=run_time)
        self.scene.remove(*present)
        for mob in present:
            if mob in self.cast:
                self.cast.remove(mob)
        return run_time

    def say(self, line, already=0.0):
        """Hold for the spoken line. The words are not drawn on screen."""
        if not line:
            return 0.0
        dur = VoiceoverTracker(line).duration
        remain = dur - float(already)
        if remain > 0.05:
            self.scene.wait(remain)
        return dur

    def play_and_say(self, line, *anims, run_time=0.7):
        """Play motion and keep the voice overlapping it, not trailing a caption."""
        if anims:
            self.scene.play(*anims, run_time=run_time)
            spent = run_time
        else:
            spent = 0.0
        self.say(line, already=spent)
        return spent

    def _fit(self, text, font_size, weight, color):
        label = Text(text, font=th.SANS, weight=weight, font_size=font_size, color=color)
        max_w = float(self.scene.camera.frame.width) * 0.78
        if label.width > max_w:
            label.scale_to_fit_width(max_w)
        return label

    def _clamp(self, mob, margin=0.28):
        frame = self.scene.camera.frame
        left = frame.get_left()[0] + margin
        right = frame.get_right()[0] - margin
        bottom = frame.get_bottom()[1] + margin
        top = frame.get_top()[1] - margin
        dx = 0.0
        dy = 0.0
        if mob.get_left()[0] < left:
            dx += left - mob.get_left()[0]
        if mob.get_right()[0] > right:
            dx -= mob.get_right()[0] - right
        if mob.get_bottom()[1] < bottom:
            dy += bottom - mob.get_bottom()[1]
        if mob.get_top()[1] > top:
            dy -= mob.get_top()[1] - top
        if dx or dy:
            mob.shift(RIGHT * dx + UP * dy)
        return mob

    def ask(self, text, target=None, hold=1.15, direction=DOWN):
        """
        One short question beside the action. It holds, then leaves.
        The picture underneath is not cleared.
        """
        question = self._fit(text, 28, BOLD, th.WHITE)
        if target is not None:
            question.next_to(target, direction, buff=0.22)
        else:
            question.move_to(self.scene.camera.frame.get_bottom() + UP * 0.55)
        self._clamp(question)
        self.scene.play(FadeIn(question, shift=UP * 0.05), run_time=0.25)
        self.scene.wait(hold)
        self.scene.play(FadeOut(question), run_time=0.2)
        self.scene.remove(question)
        return 0.45 + hold

    def name(self, text, target, direction=UP, color=None, hold=1.25):
        """
        After the picture already works, attach a short name beside `target`.
        The label leaves so it does not become a caption bar.
        """
        if color is None:
            color = th.CYAN_LIGHT
        label = self._fit(text, 24, BOLD, color)
        label.next_to(target, direction, buff=0.16)
        self._clamp(label)
        self.scene.play(FadeIn(label), run_time=0.28)
        self.scene.wait(hold)
        self.scene.play(FadeOut(label), run_time=0.22)
        self.scene.remove(label)
        return 0.5 + hold


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
        Yields a VoiceoverTracker. Duration is exact only if a WAV path is passed.
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
        New scenes use world() so the picture persists across beats.
        """
        return StageContext(self, act_id, title, subtitle, narration)

    def world(self):
        """Persistent picture. No title card, banner, or takeaway."""
        return WorldContext(self)

    def morph_components(self, source, target, run_time=th.RATE_NORMAL):
        """Performs continuous morphing transformation between two silicon components."""
        return self.play(ReplacementTransform(source, target), run_time=run_time)
