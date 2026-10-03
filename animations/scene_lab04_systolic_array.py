"""
Lab 04: row 1 enters on the same tick as row 0, before the partial sum arrives.
The cell computes garbage. Holding row 1 for one tick is the repair.
Skew and systolic are named after 19 and 22 land.
"""

from manim import *
import sys
from pathlib import Path

ANIM_DIR = Path(__file__).resolve().parent
if str(ANIM_DIR) not in sys.path:
    sys.path.insert(0, str(ANIM_DIR))

import theme as th
from components import KineticSiliconScene

L_ARRIVE = (
    "Two rows want to enter on the same tick. The top cells hold weights five and six, "
    "and the bottom cells hold seven and eight. Activation one is still at the top door. "
    "Activation two is already waiting on the weight seven cell, which is too soon."
)
L_GARBAGE = (
    "The partial sum from the cell above has not arrived. The weight seven cell multiplies anyway, "
    "and the center fills with an X. That X is garbage. A product written while the partial is missing "
    "is not a number anyone can pass downward."
)
L_HOLD = (
    "Hold the two for one tick, outside the cell, in the small box on the left. "
    "The top row is allowed to go first. The two waits there until a real partial exists above it. "
    "We will not feed the lower cell early a second time."
)
L_ZERO = (
    "Tick zero is only the hold. Every center is still empty, and the two is outside the grid. "
    "On the next tick the top left cell is the only one allowed to multiply. "
    "Be ready to take one times five as soon as that activation steps inside."
)
L_MUL5 = (
    "Tick one. Activation one steps into the top left cell, and the weight waiting there is five. "
    "One times five. Do that multiply before the center of the cell prints a number. "
    "The two is still sitting in the hold box, unused."
)
L_MEET = (
    "Five now sits in the top left cell, and a copy of it travels down into the gap. "
    "The held two finally enters the weight seven cell. Two times seven, then add that product to the five from above. "
    "Finish the whole sum before the lower cell prints it."
)
L_AFTER19 = (
    "Nineteen is correct. The two waited one tick, so it met the five instead of an empty partial from above. "
    "The little box on the left is what kept the lower cell patient. "
    "The top left cell did its multiply alone, on the earlier tick."
)
L_MUL6 = (
    "Next tick, the other column starts. Activation one has passed to the right, into the cell whose parked weight is six. "
    "One times six. Work that product before the center of the top right cell changes. "
    "The lower right cell is still empty."
)
L_MUL8 = (
    "Six is the partial above the bottom right cell, and the two passes across into the weight eight cell. "
    "Two times eight, then add that product to the six. Finish the sum before the bottom right cell prints it. "
    "The center has not printed yet."
)
L_AFTER22 = (
    "Twenty two just landed in the bottom right cell. Column zero finished at nineteen, "
    "and column one finished at twenty two. Each lower cell waited for a partial from above "
    "and an activation from the left. The whole grid kept the same beat."
)
L_NEW = (
    "Same grid, new weights. The top row is now one and two. The bottom row is now three and four. "
    "The centers are clear again. If the lower activation waits one tick, the way the two just waited, "
    "you can call both columns before either total prints."
)
L_EARLY = (
    "First, try the wrong timing on purpose. Activation three is at the top door and activation four "
    "is already at the weight three cell. The partial from above is missing again. "
    "The lower left cell should not know a real sum yet. Let the early four step in."
)
L_BAD = (
    "The lower cell wrote garbage again. Four arrived before the top cell could multiply three by one "
    "and hand a partial down. Clear that X out of the center. We will hold four for one tick "
    "and let the top left cell go first."
)
L_HOLD4 = (
    "Four steps back into the hold box and waits there. Three enters the top left cell, whose weight is now one. "
    "Three times one. Do that small product before the center prints anything. "
    "The held four still has not touched the lower cell."
)
L_COL = (
    "Three is now the partial sitting above. Four leaves the hold box and meets the cell whose weight is three. "
    "Four times three, then add that product to the three coming down. That sum is the whole first column. "
    "Call it before the cell shows you."
)
L_FIFTEEN = (
    "Fifteen just landed in column zero. That was three times one, plus four times three. "
    "The hold gave the top cell a tick to build the partial, and the lower cell added the second product. "
    "The right hand column has not run yet."
)
L_MUL32 = (
    "Activation three passes to the right, into the cell whose parked weight is two. Three times two. "
    "Work that product before the top right center changes. Four is still moving across, "
    "toward the bottom cell whose weight is four."
)
L_MUL44 = (
    "Six travels down as the partial from the top right cell. Four arrives beside the weight four. "
    "Four times four, then add that product onto the six. This is the whole second column. "
    "Finish the add before the number prints in the cell."
)
L_DONE = (
    "Twenty two landed again, on the new weights. Column zero was fifteen, and column one is twenty two. "
    "The lower activation waited one tick, the partial from above was real, "
    "and the early row did not get to write garbage this time."
)


def _mark(scene, tag):
    renderer = getattr(scene, "renderer", None)
    t = float(getattr(renderer, "time", 0.0) or 0.0)
    path = Path("/tmp") / f"hw_marks_{type(scene).__name__}.txt"
    with path.open("a") as handle:
        handle.write(f"{tag}\t{t:.3f}\n")


def _t(body, size=28, color=th.WHITE, bold=True):
    return Text(
        str(body),
        font=th.MONO,
        weight=BOLD if bold else NORMAL,
        font_size=size,
        color=color,
    )


def _box(color):
    return RoundedRectangle(
        corner_radius=0.1, width=2.2, height=1.7,
        stroke_color=color, stroke_width=2.2,
        fill_color="#071422", fill_opacity=0.96,
    )


def _enter(box):
    return box.get_center() + LEFT * 0.42 + DOWN * 0.18


def _exit(box):
    return box.get_right() + RIGHT * 0.34


def _val(box):
    return box.get_center() + DOWN * 0.04


def _gap(upper, lower):
    return (upper.get_bottom() + lower.get_top()) / 2


class Lab04SystolicArray(KineticSiliconScene):
    def construct(self):
        Path("/tmp/hw_marks_Lab04SystolicArray.txt").write_text("")
        with self.world() as w:
            b00 = _box(th.CYAN)
            b01 = _box(th.CYAN)
            b10 = _box(th.AMBER)
            b11 = _box(th.AMBER)
            top = VGroup(b00, b01).arrange(RIGHT, buff=0.68)
            bot = VGroup(b10, b11).arrange(RIGHT, buff=0.68)
            grid = VGroup(top, bot).arrange(DOWN, buff=0.74)
            grid.move_to(RIGHT * 1.15 + UP * 0.32)

            def weight(box, n):
                lab = _t(str(n), 22, th.AMBER_LIGHT)
                lab.move_to(box.get_top() + DOWN * 0.3)
                return lab

            def dot(box):
                lab = _t("·", 26, th.FAINT)
                lab.move_to(_val(box))
                return lab

            w00, w01 = weight(b00, 5), weight(b01, 6)
            w10, w11 = weight(b10, 7), weight(b11, 8)
            v00, v01 = dot(b00), dot(b01)
            v10, v11 = dot(b10), dot(b11)

            a1 = _t("1", 32, th.CYAN_LIGHT).move_to(_enter(b00) + LEFT * 0.95)
            a2 = _t("2", 32, th.CYAN_LIGHT).move_to(_enter(b10) + LEFT * 0.78)
            missing = _t("psum ?", 16, th.RED_LIGHT, bold=False).move_to(_gap(b00, b10))
            tick_at = LEFT * 5.35 + UP * 3.0
            tick = _t("same tick", 24, th.RED_LIGHT).move_to(tick_at)
            c0 = _t("col 0", 16, th.MUTED, bold=False).next_to(b10, DOWN, buff=0.12)
            c1 = _t("col 1", 16, th.MUTED, bold=False).next_to(b11, DOWN, buff=0.12)

            delay = RoundedRectangle(
                corner_radius=0.08, width=1.25, height=0.92,
                stroke_color=th.AMBER, stroke_width=2.2,
                fill_color="#1c1408", fill_opacity=0.96,
            )
            delay.move_to(b10.get_center() + LEFT * 2.55)

            opened = w.show(
                grid, w00, w01, w10, w11, v00, v01, v10, v11,
                a1, a2, missing, tick, c0, c1,
                run_time=0.5,
            )
            _mark(self, "start")
            w.say(L_ARRIVE, already=opened)

            xmark = _t("X", 36, th.RED_LIGHT).move_to(_val(b10))
            self.bring_to_front(a2)
            self.play(
                a2.animate.move_to(_enter(b10)),
                FadeOut(v10),
                FadeIn(xmark),
                b10.animate.set_stroke(color=th.RED, width=3.4),
                run_time=0.45,
            )
            _mark(self, "break")
            self.screen_shake(intensity=0.045, cycles=2, run_time=0.24)
            self.focus_on(b10, buffer_factor=3.5, run_time=0.8)
            w.say(L_GARBAGE, already=0.45 + 0.12 + 0.8)
            w.ask("The 2 arrived. What is missing?", target=b10, direction=DOWN, hold=1.4)

            fresh = dot(b10)
            tick0 = _t("tick 0", 24, th.AMBER_LIGHT).move_to(tick_at)
            self.reset_camera(run_time=0.75)
            self.bring_to_front(a2)
            self.play(
                FadeIn(delay),
                a2.animate.move_to(delay.get_center()),
                FadeOut(missing),
                FadeOut(xmark),
                FadeIn(fresh),
                FadeOut(tick),
                FadeIn(tick0),
                b10.animate.set_stroke(color=th.AMBER, width=2.2),
                run_time=0.6,
            )
            w.keep(delay)
            tick = tick0
            v10 = fresh
            w.say(L_HOLD, already=0.75 + 0.6)
            w.say(L_ZERO)

            tick1 = _t("tick 1", 24, th.CYAN_LIGHT).move_to(tick_at)
            self.bring_to_front(a1)
            self.play(
                a1.animate.move_to(_enter(b00)),
                FadeOut(v00),
                FadeOut(tick),
                FadeIn(tick1),
                b00.animate.set_stroke(color=th.CYAN_LIGHT, width=3.2),
                run_time=0.45,
            )
            tick = tick1
            w.say(L_MUL5, already=0.45)

            five = _t("5", 32, th.GREEN_LIGHT).move_to(_val(b00))
            self.play(
                FadeIn(five),
                a1.animate.move_to(_exit(b00)),
                b00.animate.set_stroke(color=th.GREEN, width=3),
                run_time=0.38,
            )
            w.keep(five)

            trav5 = five.copy()
            self.add(trav5)
            tick2 = _t("tick 2", 24, th.CYAN_LIGHT).move_to(tick_at)
            self.bring_to_front(trav5, a2)
            self.play(
                trav5.animate.move_to(_gap(b00, b10)),
                a2.animate.move_to(_enter(b10)),
                FadeOut(v10),
                FadeOut(tick),
                FadeIn(tick2),
                b10.animate.set_stroke(color=th.CYAN_LIGHT, width=3.2),
                run_time=0.55,
            )
            tick = tick2
            w.say(L_MEET, already=0.38 + 0.55)

            nineteen = _t("19", 32, th.GREEN_LIGHT).move_to(_val(b10))
            self.play(
                FadeOut(trav5),
                FadeIn(nineteen),
                a2.animate.move_to(_exit(b10)),
                b10.animate.set_stroke(color=th.GREEN, width=3),
                run_time=0.4,
            )
            w.keep(nineteen)
            _mark(self, "repair")
            w.say(L_AFTER19, already=0.4)
            w.name("skew", delay, direction=DOWN)

            tick3 = _t("tick 3", 24, th.CYAN_LIGHT).move_to(tick_at)
            self.bring_to_front(a1)
            self.play(
                a1.animate.move_to(_enter(b01)),
                FadeOut(v01),
                FadeOut(tick),
                FadeIn(tick3),
                b01.animate.set_stroke(color=th.CYAN_LIGHT, width=3.2),
                run_time=0.45,
            )
            tick = tick3
            w.say(L_MUL6, already=0.45)

            six = _t("6", 32, th.GREEN_LIGHT).move_to(_val(b01))
            self.play(
                FadeIn(six),
                a1.animate.move_to(_exit(b01)),
                b01.animate.set_stroke(color=th.GREEN, width=3),
                run_time=0.36,
            )
            w.keep(six)

            trav6 = six.copy()
            self.add(trav6)
            tick4 = _t("tick 4", 24, th.CYAN_LIGHT).move_to(tick_at)
            self.bring_to_front(trav6, a2)
            self.play(
                trav6.animate.move_to(_gap(b01, b11)),
                a2.animate.move_to(_enter(b11)),
                FadeOut(v11),
                FadeOut(tick),
                FadeIn(tick4),
                b11.animate.set_stroke(color=th.CYAN_LIGHT, width=3.2),
                run_time=0.55,
            )
            tick = tick4
            w.say(L_MUL8, already=0.36 + 0.55)

            twenty_two = _t("22", 32, th.GREEN_LIGHT).move_to(_val(b11))
            self.play(
                FadeOut(trav6),
                FadeIn(twenty_two),
                FadeOut(a2),
                b11.animate.set_stroke(color=th.GREEN, width=3),
                run_time=0.4,
            )
            w.keep(twenty_two)
            w.say(L_AFTER22, already=0.4)
            w.name("systolic", grid, direction=UP)

            n00, n01 = weight(b00, 1), weight(b01, 2)
            n10, n11 = weight(b10, 3), weight(b11, 4)
            d00, d01 = dot(b00), dot(b01)
            d10, d11 = dot(b10), dot(b11)
            tick_b = _t("clear", 24, th.MUTED).move_to(tick_at)
            self.play(
                FadeOut(w00), FadeIn(n00),
                FadeOut(w01), FadeIn(n01),
                FadeOut(w10), FadeIn(n10),
                FadeOut(w11), FadeIn(n11),
                FadeOut(five), FadeIn(d00),
                FadeOut(six), FadeIn(d01),
                FadeOut(nineteen), FadeIn(d10),
                FadeOut(twenty_two), FadeIn(d11),
                FadeOut(a1),
                FadeOut(tick), FadeIn(tick_b),
                b00.animate.set_stroke(color=th.CYAN, width=2.2),
                b01.animate.set_stroke(color=th.CYAN, width=2.2),
                b10.animate.set_stroke(color=th.AMBER, width=2.2),
                b11.animate.set_stroke(color=th.AMBER, width=2.2),
                c0.animate.set_color(th.MUTED),
                run_time=0.6,
            )
            w00, w01, w10, w11 = n00, n01, n10, n11
            v00, v01, v10, v11 = d00, d01, d10, d11
            tick = tick_b
            w.keep(w00, w01, w10, w11, v00, v01, v10, v11)
            w.say(L_NEW, already=0.6)

            b3 = _t("3", 32, th.CYAN_LIGHT).move_to(_enter(b00) + LEFT * 0.9)
            b4 = _t("4", 32, th.CYAN_LIGHT).move_to(_enter(b10) + LEFT * 0.78)
            same = _t("same tick", 24, th.RED_LIGHT).move_to(tick_at)
            self.play(
                FadeIn(b3, shift=RIGHT * 0.08),
                FadeIn(b4, shift=RIGHT * 0.08),
                FadeOut(tick),
                FadeIn(same),
                run_time=0.35,
            )
            tick = same
            w.keep(b3, b4)
            w.say(L_EARLY, already=0.35)

            bad = _t("X", 36, th.RED_LIGHT).move_to(_val(b10))
            self.bring_to_front(b4)
            self.play(
                b4.animate.move_to(_enter(b10)),
                FadeOut(v10),
                FadeIn(bad),
                b10.animate.set_stroke(color=th.RED, width=3.4),
                run_time=0.42,
            )
            w.say(L_BAD, already=0.42)

            held = dot(b10)
            tick_h = _t("tick 1", 24, th.CYAN_LIGHT).move_to(tick_at)
            self.bring_to_front(b4, b3)
            self.play(
                b4.animate.move_to(delay.get_center()),
                FadeOut(bad),
                FadeIn(held),
                b3.animate.move_to(_enter(b00)),
                FadeOut(v00),
                FadeOut(tick),
                FadeIn(tick_h),
                b10.animate.set_stroke(color=th.AMBER, width=2.2),
                b00.animate.set_stroke(color=th.CYAN_LIGHT, width=3.2),
                run_time=0.6,
            )
            tick = tick_h
            v10 = held
            w.say(L_HOLD4, already=0.6)

            three = _t("3", 32, th.GREEN_LIGHT).move_to(_val(b00))
            self.play(
                FadeIn(three),
                b3.animate.move_to(_exit(b00)),
                b00.animate.set_stroke(color=th.GREEN, width=3),
                run_time=0.34,
            )
            w.keep(three)

            trav3 = three.copy()
            self.add(trav3)
            tick_c = _t("tick 2", 24, th.CYAN_LIGHT).move_to(tick_at)
            self.bring_to_front(trav3, b4)
            self.play(
                trav3.animate.move_to(_gap(b00, b10)),
                b4.animate.move_to(_enter(b10)),
                FadeOut(v10),
                FadeOut(tick),
                FadeIn(tick_c),
                b10.animate.set_stroke(color=th.CYAN_LIGHT, width=3.2),
                c0.animate.set_color(th.CYAN_LIGHT),
                run_time=0.55,
            )
            tick = tick_c
            w.say(L_COL, already=0.34 + 0.55)
            w.ask("What does the first column equal?", target=c0, direction=DOWN, hold=1.6)

            fifteen = _t("15", 32, th.GREEN_LIGHT).move_to(_val(b10))
            self.play(
                FadeOut(trav3),
                FadeIn(fifteen),
                b4.animate.move_to(_exit(b10)),
                b10.animate.set_stroke(color=th.GREEN, width=3),
                c0.animate.set_color(th.GREEN_LIGHT),
                run_time=0.4,
            )
            w.keep(fifteen)
            w.say(L_FIFTEEN, already=0.4)

            tick_r = _t("tick 3", 24, th.CYAN_LIGHT).move_to(tick_at)
            self.bring_to_front(b3)
            self.play(
                b3.animate.move_to(_enter(b01)),
                FadeOut(v01),
                FadeOut(tick),
                FadeIn(tick_r),
                b01.animate.set_stroke(color=th.CYAN_LIGHT, width=3.2),
                run_time=0.45,
            )
            tick = tick_r
            w.say(L_MUL32, already=0.45)

            six_b = _t("6", 32, th.GREEN_LIGHT).move_to(_val(b01))
            self.play(
                FadeIn(six_b),
                b3.animate.move_to(_exit(b01)),
                b01.animate.set_stroke(color=th.GREEN, width=3),
                run_time=0.34,
            )
            w.keep(six_b)

            trav_b = six_b.copy()
            self.add(trav_b)
            tick_f = _t("tick 4", 24, th.CYAN_LIGHT).move_to(tick_at)
            self.bring_to_front(trav_b, b4)
            self.play(
                trav_b.animate.move_to(_gap(b01, b11)),
                b4.animate.move_to(_enter(b11)),
                FadeOut(v11),
                FadeOut(tick),
                FadeIn(tick_f),
                b11.animate.set_stroke(color=th.CYAN_LIGHT, width=3.2),
                run_time=0.55,
            )
            w.say(L_MUL44, already=0.34 + 0.55)

            ans = _t("22", 32, th.GREEN_LIGHT).move_to(_val(b11))
            self.play(
                FadeOut(trav_b),
                FadeIn(ans),
                FadeOut(b4),
                b11.animate.set_stroke(color=th.GREEN, width=3),
                c1.animate.set_color(th.GREEN_LIGHT),
                run_time=0.4,
            )
            w.keep(ans)
            w.say(L_DONE, already=0.4)
