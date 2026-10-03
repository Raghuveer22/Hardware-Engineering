"""
Lab 05: a short dot product looks fine. Lengthening to 64 sends the score
off the chart until softmax is one spike. Dividing by 8 brings a readable
bar back. The root of 64, then of 16, is tested one place at a time.
"""

from manim import *
import sys
from pathlib import Path

ANIM_DIR = Path(__file__).resolve().parent
if str(ANIM_DIR) not in sys.path:
    sys.path.insert(0, str(ANIM_DIR))

import theme as th
from components import KineticSiliconScene

L1 = "Two short vectors. Their dot product is 2. The bars stay calm. The bar on the left is that small score, and the three softmax bars beside it each keep a visible share instead of collapsing into a spike."
L2 = "Lengthen both vectors until each one has 64 entries. Every new pair multiplies and then adds into the same score. The bar that showed 2 climbs until the score reads 64, and that bar runs off the chart."
L3 = "Softmax now sees a score of 64 standing next to much smaller neighbors. One bar spikes and takes almost the whole share. The other two collapse into thin slivers, so the calm row has become one spike."
L4 = "The entries themselves did not become huge. There are simply 64 products in the sum, so the score spreads as the length grows. One score pulls far away from the others, and softmax treats that one score as almost certain."
L5 = "Divide that score of 64 by 8. Eight times 8 is 64, so the result is exactly 8, a number you can read. The tall bar drops back onto the screen, and the label on that bar now reads 8."
L6 = "The three softmax bars open again beside it. They are no longer one spike and two thin slivers. Each bar holds a visible share, the same kind of calm row you saw when the score on the left was only 2."
L7 = "Now build that 8 from 64, testing the highest place first. The places run 16, then 8, then 4, then 2, then 1. Form a candidate, square it, and cross the place out when that square is too big to fit."
L8 = "Try the 16 place first. The candidate is 16, and 16 times 16 is 256. That square sits far above 64, so this place does not fit. Cross it out, and leave a zero written in the 16 place."
L9 = "Try the 8 place next. The candidate is 8, and 8 times 8 is 64. That square matches the number we are rooting, so this place fits. Keep the place. The root so far now stands at 8."
L10 = "The next place is 4. Adding it to the 8 we kept makes the candidate 12, and 12 times 12 is 144. That square is larger than 64, so the place is too big. Cross it out, and the root stays 8."
L11 = "The next place is 2. Adding it to 8 makes the candidate 10, and 10 times 10 is 100. One hundred is still larger than 64, so this place does not fit either. Cross it out, and leave the root at 8."
L12 = "The last place is 1. Adding it makes the candidate 9, and 9 times 9 is 81. That square is still too big for 64, so the place is thrown away. The root does not grow, and it remains 8."
L13 = "Every lower place lost the test. The only place we kept is 8, and 8 times 8 is 64 with nothing left over. That root is the same 8 that brought the tall score back down to a bar you can read."
L14 = "Look up at those bars again. The score that ran off the chart was 64, and dividing by 8 left 8. The softmax bars are calm because that score is no longer huge sitting beside its smaller neighbors."
L15 = "You can check the rejected tries. A candidate of 16 squared to 256, which was too big. A candidate of 9 squared to 81, which was also too big. Only 8 squared lands on 64 exactly."
L16 = "Try a second number with the same test. The number is now 16. The highest place squared is 16 times 16, which is 256, far too big, so that place is crossed out and we keep testing downward."
L17 = "The 8 place is too big for a root of 16. Eight times 8 is 64, and 64 is well above 16, so that place is crossed out. Leave a zero there. The root of 16 does not begin with 8."
L18 = "The 4 place fits this number. Four times 4 is 16, exactly, so keep that place. The root so far is 4. The square matches 16 with nothing left over, which you can check by multiplying."
L19 = "Adding the 2 place would make the candidate 6, and 6 times 6 is 36. That square is larger than 16, so cross the place out. Adding 1 would make 5, and 5 times 5 is 25, which is still too big."
L20 = "The lower places are gone, and the root of 16 is 4, because 4 times 4 is 16. Above it, the first root remains 8, the score bar still reads 8, and the three softmax bars are still calm."

EQ_POINT = DOWN * 1.9 + RIGHT * 0.35


def _mark(scene, tag):
    renderer = getattr(scene, "renderer", None)
    t = float(getattr(renderer, "time", 0.0) or 0.0)
    path = Path("/tmp") / f"hw_marks_{type(scene).__name__}.txt"
    with path.open("a") as handle:
        handle.write(f"{tag}\t{t:.3f}\n")


def _bar(height, color):
    return Rectangle(
        width=0.55, height=max(height, 0.08),
        stroke_width=0, fill_color=color, fill_opacity=0.92,
    )


def _mono(text, size=28, color=th.WHITE, weight=NORMAL):
    return Text(text, font=th.MONO, weight=weight, font_size=size, color=color)


def _drop(scene, w, mobs):
    for mob in mobs:
        if mob is None:
            continue
        if mob in w.cast:
            w.cast.remove(mob)
        scene.remove(mob)


class Lab05SquareRoot(KineticSiliconScene):
    def construct(self):
        Path("/tmp/hw_marks_Lab05SquareRoot.txt").write_text("")
        with self.world() as w:
            chart = self._chart(w)
            self._bits(w, chart)

    def _chart(self, w):
        score = _bar(0.7, th.CYAN)
        score.move_to(LEFT * 4.2 + DOWN * 0.2)
        label = _mono("2", 26, th.CYAN_LIGHT, BOLD)
        label.next_to(score, UP, buff=0.15)
        soft = VGroup(*[_bar(h, th.GREEN) for h in (0.9, 0.7, 0.8)]).arrange(RIGHT, buff=0.16)
        soft.move_to(RIGHT * 2.2 + DOWN * 0.6)
        length = _mono("len 2", 18, th.MUTED)
        length.next_to(score, DOWN, buff=0.16)
        w.show(score, label, soft, length, run_time=0.4)
        _mark(self, "start")
        w.say(L1, already=0.4)

        tall = _bar(3.2, th.RED).move_to(LEFT * 4.3 + UP * 0.35)
        big = _mono("64", 26, th.RED_LIGHT, BOLD).next_to(tall, UP, buff=0.12)
        len64 = _mono("len 64", 18, th.RED_LIGHT).next_to(tall, DOWN, buff=0.14)
        spikes = VGroup(*[
            _bar(h, th.RED if i == 0 else th.MUTED)
            for i, h in enumerate((2.4, 0.14, 0.14))
        ]).arrange(RIGHT, buff=0.16, aligned_edge=DOWN)
        spikes.move_to(RIGHT * 2.4 + DOWN * 0.15)
        self.play(
            FadeOut(score), FadeOut(label), FadeOut(soft), FadeOut(length),
            FadeIn(tall), FadeIn(big), FadeIn(len64), FadeIn(spikes),
            run_time=0.55,
        )
        _drop(self, w, (score, label, soft, length))
        w.keep(tall, big, len64, spikes)
        self.screen_shake(intensity=0.05, cycles=3, run_time=0.28)
        _mark(self, "break")
        w.say(L2, already=0.69)
        w.say(L3)
        w.ask("The vectors only got longer. Why did one bar eat the rest?", target=spikes)
        w.say(L4)

        calm = _bar(1.15, th.CYAN).move_to(LEFT * 4.3 + DOWN * 0.05)
        calm_l = _mono("8", 26, th.CYAN_LIGHT, BOLD).next_to(calm, UP, buff=0.12)
        len_keep = _mono("len 64", 18, th.MUTED).next_to(calm, DOWN, buff=0.14)
        restored = VGroup(*[_bar(h, th.GREEN) for h in (0.9, 0.7, 0.8)])
        restored.arrange(RIGHT, buff=0.16, aligned_edge=DOWN)
        restored.move_to(RIGHT * 2.4 + DOWN * 0.35)
        self.play(
            FadeOut(tall), FadeOut(big), FadeOut(len64), FadeOut(spikes),
            FadeIn(calm), FadeIn(calm_l), FadeIn(len_keep), FadeIn(restored),
            run_time=0.55,
        )
        _drop(self, w, (tall, big, len64, spikes))
        w.keep(calm, calm_l, len_keep, restored)
        _mark(self, "repair")
        w.say(L5, already=0.55)
        w.say(L6)
        w.name("square root", calm_l, direction=RIGHT)
        return calm, calm_l, len_keep, restored

    def _bits(self, w, chart):
        calm, calm_l, len_keep, restored = chart
        shift = UP * 1.65
        self.play(
            calm.animate.shift(shift),
            calm_l.animate.shift(shift),
            len_keep.animate.shift(shift),
            restored.animate.shift(shift),
            run_time=0.6,
        )
        frames, captions, digits = self._place_row()
        rad = _mono("64", 42, th.WHITE, BOLD).move_to(LEFT * 2.85 + DOWN * 1.9)
        w.show(rad, *frames, *captions, *digits, run_time=0.45)
        w.say(L7, already=1.05)

        digits[0], eq, cross, spent = self._decide(
            w, frames[0], digits[0], None, None, "16 x 16 = 256", False,
        )
        w.say(L8, already=spent)

        digits[1], eq, cross, spent = self._decide(
            w, frames[1], digits[1], eq, cross, "8 x 8 = 64", True,
        )
        w.say(L9, already=spent)
        w.name("one bit at a time", eq, direction=DOWN)

        digits[2], eq, cross, spent = self._decide(
            w, frames[2], digits[2], eq, cross, "12 x 12 = 144", False,
        )
        w.say(L10, already=spent)

        digits[3], eq, cross, spent = self._decide(
            w, frames[3], digits[3], eq, cross, "10 x 10 = 100", False,
        )
        w.say(L11, already=spent)

        digits[4], eq, cross, spent = self._decide(
            w, frames[4], digits[4], eq, cross, "9 x 9 = 81", False,
        )
        w.say(L12, already=spent)

        final = _mono("8 x 8 = 64", 30, th.GREEN_LIGHT, BOLD).move_to(EQ_POINT)
        self.play(FadeOut(eq), FadeOut(cross), FadeIn(final), run_time=0.4)
        _drop(self, w, (eq, cross))
        w.keep(final)
        w.say(L13, already=0.4)

        self.play(Indicate(calm_l), Indicate(restored), run_time=0.5)
        w.say(L14, already=0.5)
        self.play(
            Indicate(digits[0]), Indicate(digits[4]), Indicate(digits[1]),
            run_time=0.55,
        )
        w.say(L15, already=0.55)

        parked = _mono("8 x 8 = 64", 22, th.GREEN_LIGHT, BOLD)
        parked.move_to(DOWN * 3.15 + RIGHT * 4.15)
        rad16 = _mono("16", 42, th.WHITE, BOLD).move_to(rad)
        dashes = []
        outs = [final, rad, *digits]
        ins = [parked, rad16]
        for frame, digit in zip(frames, digits):
            dash = _mono("-", 28, th.FAINT, BOLD).move_to(frame)
            dashes.append(dash)
            ins.append(dash)
        self.play(
            *[FadeOut(m) for m in outs],
            *[FadeIn(m) for m in ins],
            *[frame.animate.set_stroke(color=th.BORDER, width=2) for frame in frames],
            run_time=0.5,
        )
        _drop(self, w, outs)
        w.keep(*ins)
        digits = dashes

        digits[0], eq, cross, spent = self._decide(
            w, frames[0], digits[0], None, None, "16 x 16 = 256", False,
        )
        w.say(L16, already=0.5 + spent)

        digits[1], eq, cross, spent = self._decide(
            w, frames[1], digits[1], eq, cross, "8 x 8 = 64", False,
        )
        w.say(L17, already=spent)

        digits[2], eq, cross, spent = self._decide(
            w, frames[2], digits[2], eq, cross, "4 x 4 = 16", True,
        )
        w.say(L18, already=spent)

        digits[3], eq6, cross6, spent6 = self._decide(
            w, frames[3], digits[3], None, None, "6 x 6 = 36", False,
            eq_point=DOWN * 2.75 + RIGHT * 0.35,
        )
        digits[4], eq5, cross5, spent5 = self._decide(
            w, frames[4], digits[4], None, None, "5 x 5 = 25", False,
            eq_point=DOWN * 3.35 + LEFT * 3.15,
        )
        w.say(L19, already=spent6 + spent5)
        self.play(Indicate(eq), Indicate(calm_l), run_time=0.5)
        w.say(L20, already=0.5)

    def _place_row(self):
        frames, captions, digits = [], [], []
        for place in (16, 8, 4, 2, 1):
            frame = Rectangle(
                width=0.78, height=0.78,
                stroke_color=th.BORDER, stroke_width=2,
                fill_color=th.CARD, fill_opacity=0.92,
            )
            cap = _mono(str(place), 16, th.MUTED)
            dig = _mono("-", 28, th.FAINT, BOLD)
            frames.append(frame)
            captions.append(cap)
            digits.append(dig)
        buff = 0.16
        cell = 0.78
        total = cell * 5 + buff * 4
        x = 0.45 - total / 2 + cell / 2
        for frame, cap, dig in zip(frames, captions, digits):
            frame.move_to(RIGHT * x + DOWN * 0.15)
            cap.next_to(frame, UP, buff=0.1)
            dig.move_to(frame)
            x += cell + buff
        return frames, captions, digits

    def _decide(self, w, frame, digit, old_eq, old_cross, eq_text, keep, eq_point=EQ_POINT):
        outs = [digit]
        if old_eq is not None:
            outs.append(old_eq)
        if old_cross is not None:
            outs.append(old_cross)
        color = th.GREEN_LIGHT if keep else th.RED_LIGHT
        new_digit = _mono("1" if keep else "0", 28, color, BOLD).move_to(frame)
        eq = _mono(eq_text, 30, color, BOLD).move_to(eq_point)
        stroke = th.GREEN if keep else th.RED
        self.play(
            frame.animate.set_stroke(color=stroke, width=3.4),
            *[FadeOut(m) for m in outs],
            FadeIn(new_digit),
            FadeIn(eq),
            run_time=0.42,
        )
        _drop(self, w, outs)
        w.keep(new_digit, eq)
        spent = 0.42
        cross = None
        if not keep:
            cross = Line(
                eq.get_left() + LEFT * 0.06,
                eq.get_right() + RIGHT * 0.06,
                color=th.RED, stroke_width=4.5,
            )
            self.play(Create(cross), run_time=0.28)
            w.keep(cross)
            spent += 0.28
        return new_digit, eq, cross, spent
