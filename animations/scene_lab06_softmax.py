"""
Lab 06: scores 2, 1, 0 become shares that sum to 1. Adding 50 overflows
the register; taking 50 back restores the same bars. A running sum of 8
is halved so a box that holds 4 can keep it. Scores 3, 1, 0 do the same
after a lift of 20.
"""

from manim import *
import sys
from pathlib import Path

ANIM_DIR = Path(__file__).resolve().parent
if str(ANIM_DIR) not in sys.path:
    sys.path.insert(0, str(ANIM_DIR))

import theme as th
from components import KineticSiliconScene

L1 = "Scores 2, 1, and 0. Exponentiate each one and divide by the total, and the shares are about 0.67, 0.24, and 0.09. Add those three shares and you get 1. The bars show that split, and the register reads ok."
L2 = "Add 50 to every score in the row. The numbers become 52, 51, and 50. Each score grew by the same amount, so the gaps between them did not change, but the exponentials of these new scores are enormous."
L3 = "The bars slam into the ceiling, and the register flips from ok to ERR. The picture is no longer three calm shares. The values that should have been written into the register climbed out of the range it can hold."
L4 = "Nothing in the ordering of the scores changed, because each one was lifted by the same 50. The failure is the size of the exponential. A score of 52 is a modest integer, and e to that power does not fit."
L5 = "Take 50 off every score. 52 minus 50 is 2, 51 minus 50 is 1, and 50 minus 50 is 0. The row reads 2, 1, and 0 again. The bars drop back to the same calm shares as the start."
L6 = "The register reads ok again. The shares are about 0.67, 0.24, and 0.09, and they still add to 1. The bars match the opening picture. e to the 2 is only about 7.4, a value this register can hold."
L7 = "A running sum is climbing beside those bars. The box holds 4. The sum reaches 8, which is twice the room in the box, so the fill rises through the top and spills. The level is too high to keep."
L8 = "Multiply that running sum by 1/2. Half of 8 is 4. The fill shrinks until it sits on the rim of the box, level with the top, and the label on the fill reads 4. The spill is gone, and the level fits."
L9 = "The next scores can still fit in the register. They are not added on top of a spilled 8. They meet a running sum that has been brought back inside the box, and the register beside the bars still reads ok."
L10 = "Check a second triple you can do by hand. The scores are 3, 1, and 0. Their shares are about 0.84, 0.11, and 0.04. Those shares add to about 1, the bars show that new split, and the register reads ok."
L11 = "Add 20 to every score this time. The row becomes 23, 21, and 20. The gaps are still 3, then 1, then 0, but the exponentials are again far too large. The bars slam into the ceiling, and the register reads ERR."
L12 = "Take 20 off every score. 23 minus 20 is 3, 21 minus 20 is 1, and 20 minus 20 is 0. The row is 3, 1, and 0 again. The shares about 0.84, 0.11, and 0.04 return, and the bars match that row."
L13 = "You can check the shift without trusting the drawing. 3 plus 20 is 23, 1 plus 20 is 21, and 0 plus 20 is 20. Removing that same 20 restores the row you started from, and the register returns to ok."
L14 = "The two calm rows are different, and that is the honest result. Shares from 2, 1, and 0 are not the shares from 3, 1, and 0. Each row comes back to its own bars after its own lift is removed."
L15 = "The shares survive an equal shift because every score moves together. In the first row the gaps stay 2, then 1, then 0. In the second row the gaps stay 3, then 1, then 0. Equal moves do not change the shares."
L16 = "What left the register on this row was the exponential of 23, not the integer 3 you can see now. After 20 comes off, the largest score is 3, and e to the 3 is about 20, which is no longer past the register."
L17 = "Look again at the box. A sum of 8 could not stay inside a box that holds 4. Multiplying by 1/2 cut that level in half, from 8 down to 4, and the fill now stops on the rim instead of spilling past it."
L18 = "Both repairs are still this same picture. The register went to ERR when the scores were lifted, and it reads ok once that lift is taken away. The box that spilled at 8 now holds a level of 4, and the bars are shares."
L19 = "Recheck this second row with the exponentials themselves. e to the 3 is about 20.1, e to the 1 is about 2.7, and e to the 0 is 1. Divide each by their total near 23.8, and the shares match these bars."
L20 = "Add those three shares on the bars, about 0.84, 0.11, and 0.04, and you are back near 1. The register still reads ok. The same check on the first row was 0.67, 0.24, and 0.09, also adding to 1."

CALM = (2.2, 0.85, 0.35)
CALM_CAPS = ("0.67", "0.24", "0.09")
SECOND = (2.35, 0.32, 0.14)
SECOND_CAPS = ("0.84", "0.11", "0.04")
SLAM = (2.75, 2.66, 2.58)


def _mark(scene, tag):
    renderer = getattr(scene, "renderer", None)
    t = float(getattr(renderer, "time", 0.0) or 0.0)
    path = Path("/tmp") / f"hw_marks_{type(scene).__name__}.txt"
    with path.open("a") as handle:
        handle.write(f"{tag}\t{t:.3f}\n")


def _bars(heights, color):
    cols = VGroup()
    for h in heights:
        cols.add(Rectangle(
            width=0.7, height=max(h, 0.08),
            stroke_width=0, fill_color=color, fill_opacity=0.92,
        ))
    cols.arrange(RIGHT, buff=0.22, aligned_edge=DOWN)
    return cols


def _mono(text, size=28, color=th.WHITE, weight=NORMAL):
    return Text(text, font=th.MONO, weight=weight, font_size=size, color=color)


def _aligned(heights, color, template):
    group = _bars(heights, color)
    group.shift(UP * (template.get_bottom()[1] - group.get_bottom()[1]))
    group.set_x(template.get_x())
    return group


def _captions(group, texts, color):
    labels = []
    for rect, text in zip(group, texts):
        label = _mono(text, 20, color)
        label.next_to(rect, DOWN, buff=0.12)
        labels.append(label)
    return labels


def _exponents(group, texts, color):
    labels = []
    for rect, text in zip(group, texts):
        label = _mono(text, 18, color)
        label.next_to(rect, UP, buff=0.08)
        labels.append(label)
    return labels


def _ceiling(group):
    line = Line(
        group.get_left() + LEFT * 0.18,
        group.get_right() + RIGHT * 0.18,
        color=th.RED, stroke_width=4,
    )
    line.set_y(group.get_top()[1] + 0.03)
    return line


def _drop(scene, w, mobs):
    for mob in mobs:
        if mob is None:
            continue
        if mob in w.cast:
            w.cast.remove(mob)
        scene.remove(mob)


class Lab06Softmax(KineticSiliconScene):
    def construct(self):
        Path("/tmp/hw_marks_Lab06Softmax.txt").write_text("")
        with self.world() as w:
            anchor = _bars(CALM, th.GREEN).move_to(DOWN * 0.3)
            caps = _captions(anchor, CALM_CAPS, th.GREEN_LIGHT)
            scores = _mono("2    1    0", 28, th.WHITE).move_to(UP * 2.2)
            reg = RoundedRectangle(
                corner_radius=0.1, width=2.4, height=1.2,
                stroke_color=th.CYAN, stroke_width=2.2,
                fill_color="#071422", fill_opacity=0.96,
            ).move_to(RIGHT * 4.3)
            reg_v = _mono("ok", 24, th.GREEN_LIGHT).move_to(reg)
            w.show(scores, anchor, *caps, reg, reg_v, run_time=0.4)
            _mark(self, "start")
            w.say(L1, already=0.4)

            hot = _mono("52   51   50", 28, th.RED_LIGHT).move_to(scores)
            exploded = _aligned(SLAM, th.RED, anchor)
            ceiling = _ceiling(exploded)
            err = _mono("ERR", 28, th.RED_LIGHT, BOLD).move_to(reg)
            spent = self._exchange(
                w,
                [scores, anchor, *caps, reg_v],
                [hot, exploded, ceiling, err],
                extra=[reg.animate.set_stroke(color=th.RED, width=3.2)],
                run_time=0.6,
            )
            self.screen_shake(intensity=0.05, cycles=3, run_time=0.28)
            _mark(self, "break")
            w.say(L2, already=spent + 0.14)
            w.say(L3)
            w.ask("The shares were fine a moment ago. What overflowed?", target=reg)
            w.say(L4)

            back = _mono("2    1    0", 28, th.WHITE).move_to(UP * 2.2)
            calm = _aligned(CALM, th.GREEN, anchor)
            calm_caps = _captions(calm, CALM_CAPS, th.GREEN_LIGHT)
            ok = _mono("ok", 24, th.GREEN_LIGHT).move_to(reg)
            spent = self._exchange(
                w,
                [hot, exploded, ceiling, err],
                [back, calm, *calm_caps, ok],
                extra=[reg.animate.set_stroke(color=th.GREEN, width=2.6)],
                run_time=0.55,
            )
            _mark(self, "repair")
            w.say(L5, already=spent)
            exps = _exponents(calm, ("7.4", "2.7", "1"), th.AMBER_LIGHT)
            self.play(*[FadeIn(m) for m in exps], run_time=0.35)
            w.keep(*exps)
            w.say(L6, already=0.35)
            w.name("subtract the max", back, direction=LEFT)

            box = self._spill(w)
            self.play(Indicate(reg), Indicate(calm), run_time=0.45)
            w.say(L9, already=0.45)

            row = _mono("3    1    0", 28, th.WHITE).move_to(UP * 2.2)
            calm2 = _aligned(SECOND, th.GREEN, anchor)
            caps2 = _captions(calm2, SECOND_CAPS, th.GREEN_LIGHT)
            spent = self._exchange(
                w,
                [back, calm, *calm_caps, *exps],
                [row, calm2, *caps2],
                run_time=0.5,
            )
            w.say(L10, already=spent)

            hot2 = _mono("23   21   20", 28, th.RED_LIGHT).move_to(UP * 2.2)
            boom = _aligned(SLAM, th.RED, anchor)
            ceiling2 = _ceiling(boom)
            err2 = _mono("ERR", 28, th.RED_LIGHT, BOLD).move_to(reg)
            spent = self._exchange(
                w,
                [row, calm2, *caps2, ok],
                [hot2, boom, ceiling2, err2],
                extra=[reg.animate.set_stroke(color=th.RED, width=3.2)],
                run_time=0.55,
            )
            self.screen_shake(intensity=0.045, cycles=3, run_time=0.24)
            w.say(L11, already=spent + 0.12)

            row2 = _mono("3    1    0", 28, th.WHITE).move_to(UP * 2.2)
            calm3 = _aligned(SECOND, th.GREEN, anchor)
            caps3 = _captions(calm3, SECOND_CAPS, th.GREEN_LIGHT)
            ok2 = _mono("ok", 24, th.GREEN_LIGHT).move_to(reg)
            spent = self._exchange(
                w,
                [hot2, boom, ceiling2, err2],
                [row2, calm3, *caps3, ok2],
                extra=[reg.animate.set_stroke(color=th.GREEN, width=2.6)],
                run_time=0.55,
            )
            w.say(L12, already=spent)
            self.play(Indicate(row2), run_time=0.4)
            w.say(L13, already=0.4)
            w.say(L14)
            w.say(L15)
            self.play(Indicate(reg), run_time=0.4)
            w.say(L16, already=0.4)

            self.play(Indicate(box), run_time=0.45)
            w.say(L17, already=0.45)
            w.say(L18)

            exps2 = _exponents(calm3, ("20.1", "2.7", "1"), th.AMBER_LIGHT)
            self.play(*[FadeIn(m) for m in exps2], run_time=0.35)
            w.keep(*exps2)
            w.say(L19, already=0.35)
            self.play(
                Indicate(caps3[0]), Indicate(caps3[1]), Indicate(caps3[2]),
                run_time=0.5,
            )
            w.say(L20, already=0.5)

    def _spill(self, w):
        box = RoundedRectangle(
            corner_radius=0.1, width=1.5, height=1.55,
            stroke_color=th.CYAN, stroke_width=2.4,
            fill_color="#071422", fill_opacity=0.35,
        ).move_to(LEFT * 5.05 + DOWN * 0.35)
        pad = 0.1
        inner_bottom = box.get_bottom()[1] + pad
        fit_h = box.height - 2 * pad
        spill_h = fit_h * 2
        fill = Rectangle(
            width=1.12, height=0.12, stroke_width=0,
            fill_color=th.AMBER, fill_opacity=0.92,
        )
        fill.move_to([box.get_x(), inner_bottom + 0.06, 0])
        rim_y = inner_bottom + fit_h
        tick = Line(
            RIGHT * (box.get_right()[0] + 0.02) + UP * rim_y,
            RIGHT * (box.get_right()[0] + 0.28) + UP * rim_y,
            color=th.MUTED, stroke_width=2.5,
        )
        cap = _mono("4", 16, th.MUTED).next_to(tick, RIGHT, buff=0.06)
        val8 = _mono("8", 26, th.RED_LIGHT, BOLD)
        val8.move_to([box.get_left()[0] - 0.42, inner_bottom + spill_h - 0.02, 0])
        val4 = _mono("4", 26, th.GREEN_LIGHT, BOLD)
        val4.move_to([box.get_left()[0] - 0.42, rim_y, 0])
        half = _mono("x 1/2", 20, th.CYAN_LIGHT).next_to(box, DOWN, buff=0.14)

        w.show(box, tick, cap, fill, run_time=0.35)
        grow = (spill_h - fill.height) / 2
        self.play(
            fill.animate.stretch_to_fit_height(spill_h).shift(UP * grow).set_fill(th.RED, opacity=0.92),
            box.animate.set_stroke(color=th.RED, width=3.2),
            FadeIn(val8),
            run_time=0.75,
        )
        w.keep(val8)
        w.say(L7, already=1.1)

        shrink = (spill_h - fit_h) / 2
        self.play(
            fill.animate.stretch_to_fit_height(fit_h).shift(DOWN * shrink).set_fill(th.GREEN, opacity=0.92),
            box.animate.set_stroke(color=th.GREEN, width=2.8),
            FadeOut(val8),
            FadeIn(val4),
            FadeIn(half),
            run_time=0.8,
        )
        _drop(self, w, (val8,))
        w.keep(val4, half)
        w.say(L8, already=0.8)
        w.name("rescale", box, direction=RIGHT)
        return box

    def _exchange(self, w, outs, ins, extra=(), run_time=0.45):
        self.play(
            *[FadeOut(m) for m in outs],
            *[FadeIn(m) for m in ins],
            *extra,
            run_time=run_time,
        )
        _drop(self, w, outs)
        w.keep(*ins)
        return run_time
