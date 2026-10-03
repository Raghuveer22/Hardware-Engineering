"""
Lab 07: three arrows of different lengths. A wide divider lines them up
and is the slow piece. One half, from the root of four, does the same
job. Subtracting the average is a step you can remove.
"""

from manim import *
import sys
from pathlib import Path

ANIM_DIR = Path(__file__).resolve().parent
if str(ANIM_DIR) not in sys.path:
    sys.path.insert(0, str(ANIM_DIR))

import theme as th
from components import KineticSiliconScene

L1 = "Three arrows stand on the same baseline, and their heights are the lengths you are comparing. The first reaches one, the second reaches two, and the red one reaches four. Before any block arrives, the tall arrow already dominates the picture, and the short ones look like details beside it."
L2 = "That dominance is not a mood. Any later comparison, sum, or score will lean toward the red arrow, because four is so much larger than one or two. The short arrows are present, and they are real, but they cannot pull the eye or the total back."
L3 = "If you leave the heights like this, the long arrow wins every time you look. You need the three of them on one shared scale, or the picture keeps telling you that only the tall one matters and the other two can be ignored."
L4 = "A wide block comes in beside them, and the words on it are divide by length. Watch the shafts. The red one drops, the middle one settles, and the short one rises, until all three stand at the same height and the gap is gone."
L5 = "The lineup is what you wanted from the start. The trouble is the block that produced it. It is wide on purpose, and wide in this picture means slow. Every arrow has to wait on that divider before the heights are allowed to agree."
L6 = "Keep your eye on the size of that block, not only on the arrows. The divider is the expensive object. It is not a tiny mark you tuck under the baseline. It is the large piece, and the matched heights are stuck behind it until it finishes."
L7 = "Now the original lengths return, one and two and four, and the wide block leaves the picture. The lineup has to be earned a second time. This pass uses a thinner block, and the tall arrow is the one you follow, because four has a clean root."
L8 = "Stay with the red arrow. Its length is four, and the square root of four is two. That two is the only new number this arrow has to give you. It sits beside the tip so you can see the root before anything is scaled."
L9 = "One over that root is one half. The two steps aside, and one half takes its place. This is the factor that will actually scale the arrow. The thinner block takes the same factor, so the hardware and the number are telling one story."
L10 = "The tall arrow is multiplied by one half, so a length of four comes down to two. The short arrow rises to that same height, and the middle one is there. They match. The wide divider stays gone, and this is the lineup the slow block made, reached without it."
L11 = "People often insert one more step before the scale. A fourth mark appears on the baseline, and that mark is the average of one, two, and four. It stands near the arrows, almost as tall as the lineup you just made, waiting to be used."
L12 = "An extra subtraction takes that average off the arrows. Watch closely. They dip, and the dip is small. They are still level with one another. The lineup you cared about barely moves, which is the clue that this subtraction is not doing the work."
L13 = "Delete the subtraction. The average mark leaves with it. The arrows ease back onto the shared height and they stay lined up, so the step you removed was not what held them there. The scale had already done the job you could see."
L14 = "What you save is that whole subtraction. You do not need a card to say so. The picture showed a step, the arrows barely changed, and then the step was gone and the lineup held. The mean was a detour you can lift out."
L15 = "The same three arrows take a new set of lengths. Two of them are one, and the last one is nine. Let the nine sit there at full height. It is the only length in this second picture that can dominate, and the root is still hidden."
L16 = "The root of nine is three. It appears beside the tall arrow the way two appeared beside the four. You are not starting a different machine. You are reading one number off the length that dominated, and the other arrows wait."
L17 = "One over three is one third. That factor lands on the thin block while the nine is still tall. The two short arrows are still short, so you can see one third before any shaft moves, the same pause you had when one half sat beside the four."
L18 = "The tall arrow is multiplied by one third, so nine comes down, and the two short arrows rise to that same height. They match again. The second vector used the same motion as the four, and only the digits changed from one picture to the next."
L19 = "You can run the beats backward in your head and they still hold. See the dominant length, read its root, take one over that root, and shorten until the shafts agree. Nothing in that motion asked you to subtract an average first."

BASE_Y = -2.2
XS = [-3.0, -1.35, 0.35]
BLOCK_AT = RIGHT * 4.35 + UP * 0.05
SHAFT = [th.CYAN, th.AMBER, th.RED]
INK = [th.CYAN_LIGHT, th.AMBER_LIGHT, th.RED_LIGHT]
MATCH_H = 2.0
START_H = [1.0, 2.0, 4.0]
TALL9 = 4.05
H9 = [TALL9 / 9, TALL9 / 9, TALL9]
MATCH9 = TALL9 / 3
SHAFT9 = [th.CYAN, th.CYAN, th.RED]
INK9 = [th.CYAN_LIGHT, th.CYAN_LIGHT, th.RED_LIGHT]


def _mark(scene, tag):
    renderer = getattr(scene, "renderer", None)
    t = float(getattr(renderer, "time", 0.0) or 0.0)
    path = Path("/tmp") / f"hw_marks_{type(scene).__name__}.txt"
    with path.open("a") as handle:
        handle.write(f"{tag}\t{t:.3f}\n")


def _arrow_at(height, color, x, base_y):
    origin = np.array([float(x), float(base_y), 0.0])
    end = origin + UP * float(height)
    shaft = Line(origin, end, color=color, stroke_width=8)
    head = Triangle(color=color, fill_opacity=1, stroke_width=0).scale(0.1)
    head.next_to(end, UP, buff=0)
    return VGroup(shaft, head)


def _tag(text, x, base_y, color, size=30):
    label = Text(str(text), font=th.MONO, weight=BOLD, font_size=size, color=color)
    label.move_to(np.array([float(x), float(base_y) - 0.48, 0.0]))
    return label


def _forget(scene, world, *mobs):
    scene.remove(*mobs)
    for mob in mobs:
        if mob in world.cast:
            world.cast.remove(mob)


def _exchange(scene, world, outs, ins, extras=(), run_time=0.4):
    anims = [FadeOut(m) for m in outs] + [FadeIn(m) for m in ins] + list(extras)
    if anims:
        scene.play(*anims, run_time=run_time)
    if outs:
        scene.remove(*outs)
    for mob in outs:
        if mob in world.cast:
            world.cast.remove(mob)
    if ins:
        world.keep(*ins)
    return run_time


def _morph(scene, arrows, heights, colors, xs, base_y, labels=None, inks=None, run_time=0.65):
    anims = [
        Transform(arrow, _arrow_at(h, c, x, base_y))
        for arrow, h, c, x in zip(arrows, heights, colors, xs)
    ]
    if labels is not None:
        anims.extend(label.animate.set_color(c) for label, c in zip(labels, inks))
    scene.play(*anims, run_time=run_time)
    return run_time


class Lab07RSQRT(KineticSiliconScene):
    def construct(self):
        Path("/tmp/hw_marks_Lab07RSQRT.txt").write_text("")
        with self.world() as w:
            ground = Line(
                np.array([XS[0] - 0.7, BASE_Y, 0.0]),
                np.array([2.15, BASE_Y, 0.0]),
                color=th.FAINT,
                stroke_width=2,
            )
            arrows = [_arrow_at(h, c, x, BASE_Y) for h, c, x in zip(START_H, SHAFT, XS)]
            labels = [_tag(txt, x, BASE_Y, c) for txt, x, c in zip(("1", "2", "4"), XS, INK)]
            shown = w.show(ground, *arrows, *labels, run_time=0.45)
            _mark(self, "start")
            w.say(L1, already=shown)

            w.say(L2)
            self.focus_on(arrows[2], buffer_factor=1.5, run_time=0.7)
            w.say(L3, already=0.7)
            self.reset_camera(run_time=0.55)

            wide = RoundedRectangle(
                corner_radius=0.1, width=4.4, height=1.65,
                stroke_color=th.AMBER, stroke_width=2.6,
                fill_color="#1c1408", fill_opacity=0.96,
            ).move_to(BLOCK_AT)
            wide_l = Text("÷ length", font=th.MONO, font_size=28, color=th.AMBER_LIGHT).move_to(wide)
            t_block = w.show(wide, wide_l, run_time=0.35)
            t_eq = _morph(
                self, arrows, [MATCH_H] * 3, [th.GREEN] * 3, XS, BASE_Y,
                labels, [th.GREEN_LIGHT] * 3, run_time=0.7,
            )
            w.say(L4, already=0.55 + t_block + t_eq)
            w.say(L5)
            w.say(L6)
            _mark(self, "break")

            thin = RoundedRectangle(
                corner_radius=0.1, width=2.5, height=1.3,
                stroke_color=th.GREEN, stroke_width=2.4,
                fill_color="#071b11", fill_opacity=0.96,
            ).move_to(BLOCK_AT)
            t_swap = _exchange(self, w, [wide, wide_l], [thin], run_time=0.45)
            t_back = _morph(self, arrows, START_H, SHAFT, XS, BASE_Y, labels, INK, run_time=0.7)
            w.say(L7, already=t_swap + t_back)

            self.focus_on(arrows[2], buffer_factor=1.5, run_time=0.7)
            two = Text("2", font=th.MONO, weight=BOLD, font_size=42, color=th.AMBER_LIGHT)
            two.next_to(arrows[2], RIGHT, buff=0.22)
            t_two = w.show(two, run_time=0.3)
            w.say(L8, already=0.7 + t_two)

            half = Text("1/2", font=th.MONO, weight=BOLD, font_size=42, color=th.GREEN_LIGHT)
            half.move_to(two)
            mul_l = Text("× 1/2", font=th.MONO, font_size=28, color=th.GREEN_LIGHT).move_to(thin)
            self.reset_camera(run_time=0.55)
            t_half = _exchange(self, w, [two], [half, mul_l], run_time=0.4)
            w.say(L9, already=0.55 + t_half)

            t_match = 0.7
            self.play(
                FadeOut(half),
                *[
                    Transform(arrow, _arrow_at(MATCH_H, th.GREEN, x, BASE_Y))
                    for arrow, x in zip(arrows, XS)
                ],
                *[label.animate.set_color(th.GREEN_LIGHT) for label in labels],
                run_time=t_match,
            )
            _forget(self, w, half)
            w.say(L10, already=t_match)
            _mark(self, "repair")
            w.name("multiply by the reciprocal", thin, direction=UP)

            mark_x = 1.8
            avg_h = (1 + 2 + 4) / 3
            mark = DashedLine(
                np.array([mark_x, BASE_Y, 0.0]),
                np.array([mark_x, BASE_Y + avg_h, 0.0]),
                color=th.PURPLE_LIGHT,
                stroke_width=3,
                dash_length=0.1,
            )
            avg_tag = Text("avg", font=th.MONO, font_size=22, color=th.PURPLE_LIGHT)
            avg_tag.next_to(mark, DOWN, buff=0.08)
            t_mark = w.show(mark, avg_tag, run_time=0.4)
            w.say(L11, already=t_mark)

            chip = RoundedRectangle(
                corner_radius=0.08, width=1.5, height=0.62,
                stroke_color=th.PURPLE, stroke_width=2.2,
                fill_color="#1a0a28", fill_opacity=0.96,
            )
            chip.next_to(mark, UP, buff=0.12)
            chip_l = Text("- avg", font=th.MONO, font_size=22, color=th.PURPLE_LIGHT).move_to(chip)
            t_chip = w.show(chip, chip_l, run_time=0.3)
            dip = DOWN * 0.14
            self.play(
                *[m.animate.shift(dip) for m in (*arrows, *labels)],
                run_time=0.4,
            )
            w.say(L12, already=t_chip + 0.4)

            self.play(
                FadeOut(chip), FadeOut(chip_l), FadeOut(mark), FadeOut(avg_tag),
                *[m.animate.shift(UP * 0.14) for m in (*arrows, *labels)],
                run_time=0.5,
            )
            _forget(self, w, chip, chip_l, mark, avg_tag)
            w.say(L13, already=0.5)
            w.say(L14)

            fresh = [_tag(txt, x, BASE_Y, c, size=34 if txt == "9" else 30) for txt, x, c in zip(("1", "1", "9"), XS, INK9)]
            t_vec = _exchange(
                self, w, labels + [mul_l], fresh,
                extras=[
                    Transform(arrow, _arrow_at(h, c, x, BASE_Y))
                    for arrow, h, c, x in zip(arrows, H9, SHAFT9, XS)
                ],
                run_time=0.65,
            )
            labels = fresh
            self.screen_shake(intensity=0.04, cycles=2, run_time=0.24)
            w.say(L15, already=t_vec + 0.12)

            self.focus_on(arrows[2], buffer_factor=1.55, run_time=0.7)
            w.ask("What root fits the nine?", target=arrows[2], direction=RIGHT, hold=1.7)
            root3 = Text("3", font=th.MONO, weight=BOLD, font_size=42, color=th.AMBER_LIGHT)
            root3.next_to(arrows[2], RIGHT, buff=0.22)
            t_root = w.show(root3, run_time=0.3)
            w.say(L16, already=t_root)

            third = Text("1/3", font=th.MONO, weight=BOLD, font_size=42, color=th.GREEN_LIGHT)
            third.move_to(root3)
            mul3 = Text("× 1/3", font=th.MONO, font_size=28, color=th.GREEN_LIGHT).move_to(thin)
            self.reset_camera(run_time=0.55)
            t_third = _exchange(self, w, [root3], [third, mul3], run_time=0.4)
            w.say(L17, already=0.55 + t_third)

            t_hit = 0.7
            self.play(
                FadeOut(third),
                *[
                    Transform(arrow, _arrow_at(MATCH9, th.GREEN, x, BASE_Y))
                    for arrow, x in zip(arrows, XS)
                ],
                *[label.animate.set_color(th.GREEN_LIGHT) for label in labels],
                run_time=t_hit,
            )
            _forget(self, w, third)
            w.say(L18, already=t_hit)
            w.say(L19)
