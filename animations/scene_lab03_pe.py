"""
Lab 03: a matmul loop reads the same weight on every row.
Parking that weight inside the cell stops the reads.
Weight-stationary is the name of the parking, after the counter stops.
"""

from manim import *
import sys
from pathlib import Path

ANIM_DIR = Path(__file__).resolve().parent
if str(ANIM_DIR) not in sys.path:
    sys.path.insert(0, str(ANIM_DIR))

import theme as th
from components import KineticSiliconScene

L_LOOP = (
    "This loop walks one row at a time and reaches back to memory for the weight. "
    "On every row it reads W, multiplies by the activation, and adds into the accumulator. "
    "The weight is not changing. Watch the counter climb each time W flies out of the box and back."
)
L_ROW1 = (
    "The weight left the amber box, touched the loop, and flew straight home. "
    "The counter now reads one. That was a full memory trip, and the value on this row was not modified at all. "
    "The same fetch is about to repeat on the very next row."
)
L_ROW2 = (
    "The chip just repeated the trip. Out to the loop, back into the box, and the counter now reads two. "
    "The stored weight never changed between these rows. The loop does not keep what it finished reading a moment ago."
)
L_ROW3 = (
    "The weight has gone home a third time, and the counter sits on three. "
    "Three rows, three fetches, and one unchanged weight. This is the failure. "
    "We paid for a memory read that brought nothing new into the loop."
)
L_PARK = (
    "The weight has left the amber box and it is sitting inside the cell. "
    "The next row still needs that value, but the cell already holds it. "
    "No wire has to run back to memory for the multiply. The fetch can stop on this row."
)
L_FREEZE = (
    "A fourth row just ticked. The new activation is inside the cell, and the parked weight did not move. "
    "The counter is still three. The memory box stayed dark. This row did not fetch the weight, "
    "because the cell already held it."
)
L_STILL = (
    "The weight sits still while the rows move past it. Memory is no longer on the path of this multiply. "
    "The counter froze because the cell kept the value it was tired of fetching. That parking is the whole repair."
)
L_SEVEN = (
    "Now the parked slot has a real number. The weight is seven, and it stays amber inside the cell. "
    "It will not travel when an activation shows up. Seven is exactly the value this loop kept reading "
    "from memory on every single row."
)
L_SIX = (
    "An activation arrives from the left side. This one is six. It is new data for the row, so it is allowed to move. "
    "Six comes to rest beside the parked seven. Do not add anything yet. The first job is only to multiply."
)
L_HUNDRED = (
    "A partial sum is already waiting inside the cell, before this activation arrived. "
    "It is one hundred, left behind by the rows above this one. It does not come from the memory box on this tick. "
    "Leave that hundred alone until a product exists."
)
L_TIMES = (
    "Six times seven. Work that product yourself before the cell prints anything. "
    "Six times five is thirty, and six times two is twelve, so you can finish the product in your head. "
    "The lower half of the cell is still waiting on your multiply."
)
L_ADD = (
    "Forty two just appeared under the parked weight. Now add the partial that was already waiting in the cell. "
    "One hundred plus forty two. Take one hundred plus forty, then add the two. "
    "The new total stays hidden until you have finished that add."
)
L_SUM = (
    "The running total is now one hundred forty two. It sits where one hundred used to sit. "
    "The seven never left its slot during either step. We multiplied and then added, "
    "and the amber memory box was never asked for the weight."
)
L_WIRES = (
    "Neighbor wires only. The six slides out toward the cell on the right, and a copy of one hundred forty two "
    "slides downward to the neighbor below. There is no global bus back to memory. "
    "The parked seven stays put, and so does the running total."
)
L_PASS = (
    "Look only at those two wires. Nothing broadcasts the six onto a shared highway, and nothing writes "
    "one hundred forty two back into the amber box. The right neighbor receives the activation. "
    "The neighbor below receives the partial sum."
)
L_FOUR = (
    "A second activation arrives from the left. This one is four. The seven is still parked in the cell, "
    "so nobody goes back to fetch a weight. Four times seven. Work that new product before it appears. "
    "The read counter on the left is still three."
)
L_PLUS = (
    "Twenty eight is that product. The running total inside the cell is still one hundred forty two. "
    "Add twenty eight onto one hundred forty two. The same parked seven just did a second multiply, "
    "and it still has not left the cell."
)
L_DONE = (
    "The cell now holds one hundred seventy. Same parked seven, a new activation, and no extra read of the weight. "
    "The counter never moved off three. Leaving the weight inside the cell is what stopped the loop "
    "from fetching it on every row."
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


class Lab03ProcessingElement(KineticSiliconScene):
    def construct(self):
        Path("/tmp/hw_marks_Lab03ProcessingElement.txt").write_text("")
        with self.world() as w:
            loop = Text(
                "for row:\n    acc += W[k] * A",
                font=th.MONO, font_size=24, color=th.WHITE, line_spacing=1.15,
            )
            loop.move_to(LEFT * 4.55 + UP * 2.35)
            count = _t("reads of W:  0", 26, th.WHITE)
            count.move_to(LEFT * 4.7 + DOWN * 2.45)

            mem = RoundedRectangle(
                corner_radius=0.1, width=1.7, height=1.12,
                stroke_color=th.AMBER, stroke_width=2.2,
                fill_color="#1c1408", fill_opacity=0.96,
            )
            mem_l = _t("W", 30, th.AMBER_LIGHT).move_to(mem)
            memory = VGroup(mem, mem_l).move_to(LEFT * 1.55 + UP * 2.45)

            cell = RoundedRectangle(
                corner_radius=0.12, width=4.7, height=3.55,
                stroke_color=th.CYAN, stroke_width=2.3,
                fill_color="#071422", fill_opacity=0.96,
            )
            cell_l = _t("cell", 16, th.CYAN, bold=False).move_to(cell.get_top() + DOWN * 0.28)
            cell_g = VGroup(cell, cell_l).move_to(RIGHT * 1.85 + DOWN * 0.28)

            slot_w = cell.get_center() + UP * 0.92
            slot_a = cell.get_center() + LEFT * 1.25 + UP * 0.08
            slot_p = cell.get_center() + DOWN * 0.42
            slot_prod = cell.get_center() + DOWN * 1.22
            home = mem.get_center().copy()

            opened = w.show(loop, memory, cell_g, count, run_time=0.5)
            _mark(self, "start")
            w.say(L_LOOP, already=opened)

            chip = _t("W", 30, th.AMBER_LIGHT).move_to(home)
            self.add(chip)
            w.keep(chip)
            lands = (
                LEFT * 3.15 + UP * 1.15,
                LEFT * 2.35 + UP * 0.55,
                LEFT * 3.35 + DOWN * 0.15,
            )
            trips = (
                (1, lands[0], th.WHITE, 0.42, 0.32),
                (2, lands[1], th.WHITE, 0.5, 0.36),
                (3, lands[2], th.RED_LIGHT, 0.56, 0.4),
            )
            lines = (L_ROW1, L_ROW2, L_ROW3)
            for (n, land, color, out_t, back_t), line in zip(trips, lines):
                nxt = _t(f"reads of W:  {n}", 26, color).move_to(count)
                self.bring_to_front(chip)
                self.play(
                    chip.animate.move_to(land),
                    FadeOut(count),
                    FadeIn(nxt),
                    run_time=out_t,
                )
                self.play(chip.animate.move_to(home), run_time=back_t)
                count = nxt
                w.keep(count)
                spent = out_t + back_t
                if n == 3:
                    self.screen_shake(intensity=0.04, cycles=2, run_time=0.24)
                    _mark(self, "break")
                    spent += 0.12
                w.say(line, already=spent)

            w.ask("Why fetch a weight that has not changed?", target=count, direction=UP, hold=1.45)

            park_t = 0.7
            self.play(
                chip.animate.move_to(slot_w),
                cell.animate.set_stroke(color=th.AMBER, width=3.4),
                cell_l.animate.set_color(th.AMBER_LIGHT),
                mem.animate.set_stroke(color=th.FAINT, width=1.5),
                mem_l.animate.set_color(th.FAINT),
                run_time=park_t,
            )
            w.say(L_PARK, already=park_t)

            token = _t("A", 32, th.CYAN_LIGHT).move_to(cell.get_left() + LEFT * 1.05 + UP * 0.08)
            self.play(FadeIn(token, shift=RIGHT * 0.12), run_time=0.24)
            self.play(
                token.animate.move_to(slot_a),
                count.animate.set_color(th.GREEN_LIGHT),
                run_time=0.55,
            )
            _mark(self, "repair")
            w.keep(token)
            w.say(L_FREEZE, already=0.79)
            w.say(L_STILL)
            w.name("weight-stationary", cell_g, direction=DOWN)

            self.focus_on(cell_g, buffer_factor=1.32, run_time=0.85)
            dropped = w.drop(token)
            seven = _t("7", 40, th.AMBER_LIGHT).move_to(slot_w)
            self.play(FadeOut(chip), FadeIn(seven), run_time=0.32)
            w.keep(seven)
            w.say(L_SEVEN, already=0.85 + dropped + 0.32)

            six = _t("6", 36, th.CYAN_LIGHT).move_to(cell.get_left() + LEFT * 1.15 + UP * 0.08)
            self.play(FadeIn(six, shift=RIGHT * 0.1), run_time=0.22)
            self.bring_to_front(six)
            self.play(six.animate.move_to(slot_a), run_time=0.45)
            w.keep(six)
            w.say(L_SIX, already=0.67)

            hundred = _t("100", 34, th.GREEN_LIGHT).move_to(slot_p)
            self.play(FadeIn(hundred, shift=UP * 0.08), run_time=0.3)
            w.keep(hundred)
            w.say(L_HUNDRED, already=0.3)

            w.say(L_TIMES)
            forty_two = _t("42", 34, th.WHITE).move_to(slot_prod)
            self.play(FadeIn(forty_two, shift=UP * 0.06), run_time=0.32)
            w.keep(forty_two)
            w.say(L_ADD, already=0.32)

            partial = _t("142", 38, th.GREEN_LIGHT).move_to(slot_p)
            self.play(
                FadeOut(hundred),
                FadeOut(forty_two),
                FadeIn(partial),
                run_time=0.4,
            )
            w.keep(partial)
            w.say(L_SUM, already=0.4)

            self.reset_camera(run_time=0.8)
            right_tip = cell.get_right() + RIGHT * 1.35
            down_tip = cell.get_bottom() + DOWN * 0.78
            right_wire = Arrow(
                cell.get_right(), right_tip, buff=0.02,
                color=th.CYAN, stroke_width=4, tip_length=0.16,
            )
            down_wire = Arrow(
                cell.get_bottom(), down_tip, buff=0.02,
                color=th.GREEN, stroke_width=4, tip_length=0.16,
            )
            right_pt = right_tip + RIGHT * 0.36
            down_pt = down_tip + RIGHT * 0.78 + DOWN * 0.02
            self.play(Create(right_wire), Create(down_wire), run_time=0.45)
            w.keep(right_wire, down_wire)
            copy_down = partial.copy().scale(0.72)
            self.add(copy_down)
            self.bring_to_front(six, copy_down)
            self.play(
                six.animate.move_to(right_pt),
                copy_down.animate.move_to(down_pt),
                run_time=0.65,
            )
            w.keep(copy_down)
            w.say(L_WIRES, already=0.8 + 0.45 + 0.65)
            w.say(L_PASS)

            four = _t("4", 36, th.CYAN_LIGHT).move_to(cell.get_left() + LEFT * 1.2 + UP * 0.08)
            self.play(FadeIn(four, shift=RIGHT * 0.12), run_time=0.22)
            self.bring_to_front(four)
            self.play(four.animate.move_to(slot_a), run_time=0.42)
            w.keep(four)
            w.say(L_FOUR, already=0.64)

            twenty_eight = _t("28", 34, th.WHITE).move_to(slot_prod)
            self.play(FadeIn(twenty_eight, shift=UP * 0.06), run_time=0.3)
            w.keep(twenty_eight)
            w.say(L_PLUS, already=0.3)

            one_seventy = _t("170", 38, th.GREEN_LIGHT).move_to(slot_p)
            self.play(
                FadeOut(partial),
                FadeOut(twenty_eight),
                FadeIn(one_seventy),
                run_time=0.4,
            )
            self.remove(partial, twenty_eight)
            w.keep(one_seventy)
            w.say(L_DONE, already=0.4)
