"""
Lab 08: a modest input fits in the box. A larger exponential does not.
5.75 and 3.25 each split into a shift and a small table, and the product fits.
The integer is a shift because the base is two.
"""

from manim import *
import sys
from pathlib import Path

ANIM_DIR = Path(__file__).resolve().parent
if str(ANIM_DIR) not in sys.path:
    sys.path.insert(0, str(ANIM_DIR))

import theme as th
from components import KineticSiliconScene

L1 = "A small input, the number one, sits over the box. What the box holds is about two point seven, and that value rests inside the walls with space around it. Nothing presses the boundary. This is the exponential of a modest input, and it fits."
L2 = "Treat this as the comfortable case. The box was built to hold a result of about this size, and the stroke stays calm. A tiny input does not ask the hardware for a huge number, so the picture looks almost quiet, which is the trap."
L3 = "Push the input from one to eight. The box cannot keep the exponential. Inside, you do not get a finished value. You get the overflow mark, because e to the eight will not fit. The walls flash, and the frame shakes, because the range is already gone."
L4 = "These are the same walls that held the small result a moment ago. The input changed, and the box did not grow. The red mark is the failure, not a new answer. Hardware that tries to store the full exponential here has already given up."
L5 = "Leave the red mark where it is and bring in one ordinary number, five point seven five. It is not eight, and it is not the final exponential yet. It is one input, still whole, sitting under the box, about to come apart into two pieces."
L6 = "Watch the split. The five moves one way and the point seven five moves the other way. They are no longer a single token. The integer has a job, the fraction has a different job, and nothing has gone back into the box yet."
L7 = "The five travels into the shifter. A shift of five places is a multiply by thirty two, because two raised to the five is thirty two. The shifter does not build a tower of multiplies. It slides bits, which is work this hardware already has."
L8 = "The point seven five travels the other direction, into a tiny table. The table is small on purpose, a few entries and no more. The entry it returns for this fraction is about one point six eight. That lookup is the whole contribution of the fraction."
L9 = "The two results are ready to meet. Thirty two from the shifter, and about one point six eight from the table. Thirty two times about one point six eight is about fifty four. Fifty four is an ordinary width, nothing like the overflow that eight produced."
L10 = "Fifty four travels back into the box. The red stroke gives way to a calm one, and the value sits inside the walls, in the same place the small result sat at the start. The overflow mark is gone. This number landed where eight could not."
L11 = "Walk it as one trip, not four separate tricks. The number splits, the integer moves to the shifter, the fraction moves to the table, and the product returns to the box. Fifty four sitting inside is the proof that this path fits where the raw exponential did not."
L12 = "One success can be a special case, so the same parts take another input. The next number is three point two five. The box, the shifter, and the tiny table stay where they are. Only the digits change, which is how a method shows that it is a method."
L13 = "Look at the split before any product appears. Three is the integer, and point two five is the fraction. They sit apart on the picture, and the box has not been given an answer. You should be able to see both pieces before they go to work."
L14 = "The three moves onto the shifter. Two raised to the three is eight, so this integer becomes a shift by eight, not a shift by thirty two. The shifter itself does not grow. Only the distance of the shift changes, and the block stays the same size."
L15 = "The point two five reaches the table, and a different entry lights. The value that comes back is about one point one nine. It is still a small number from a small table. Nothing about the fraction asked the box to hold an overflowing exponential."
L16 = "Only now does the product exist. Eight times about one point one nine is about nine point five. Nine point five goes into the box, and it fits, with the same calm the fifty four had. You saw the split first, and the product came after it."
L17 = "Both inputs obeyed the same order. A split you can see, a shift taken from the integer, a small lookup from the fraction, then a product the box can hold. Eight never got that far, because the full exponential was asked to land in one piece."
L18 = "The integer part is a shift because the base is two, and a shift is a motion this box already knows how to do, so the hardware slides those bits instead of building the huge exponential that would not fit inside the same walls."

NUM_AT = DOWN * 1.02
SH_AT = LEFT * 3.9 + DOWN * 2.62
TB_AT = RIGHT * 3.9 + DOWN * 2.62


def _mark(scene, tag):
    renderer = getattr(scene, "renderer", None)
    t = float(getattr(renderer, "time", 0.0) or 0.0)
    path = Path("/tmp") / f"hw_marks_{type(scene).__name__}.txt"
    with path.open("a") as handle:
        handle.write(f"{tag}\t{t:.3f}\n")


def _mono(text, size, color, weight=NORMAL):
    return Text(str(text), font=th.MONO, weight=weight, font_size=size, color=color)


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


def _table(center):
    cells = []
    for dx, dy in ((-0.42, 0.26), (0.42, 0.26), (-0.42, -0.26), (0.42, -0.26)):
        cell = RoundedRectangle(
            corner_radius=0.05, width=0.74, height=0.44,
            stroke_color=th.PURPLE, stroke_width=1.6,
            fill_color=th.PURPLE_DARK, fill_opacity=0.35,
        )
        cell.move_to(center + RIGHT * dx + UP * dy)
        cells.append(cell)
    return cells


class Lab08ExponentialSFU(KineticSiliconScene):
    def construct(self):
        Path("/tmp/hw_marks_Lab08ExponentialSFU.txt").write_text("")
        with self.world() as w:
            box = RoundedRectangle(
                corner_radius=0.12, width=3.2, height=1.6,
                stroke_color=th.CYAN, stroke_width=2.4,
                fill_color="#071422", fill_opacity=0.96,
            ).move_to(UP * 0.4)
            val = _mono("2.7", 36, th.GREEN_LIGHT, BOLD).move_to(box)
            inp = _mono("input  1", 24, th.MUTED)
            inp.next_to(box, UP, buff=0.3)
            shown = w.show(box, val, inp, run_time=0.4)
            _mark(self, "start")
            w.say(L1, already=shown)
            w.say(L2)

            err = _mono("e^8", 40, th.RED_LIGHT, BOLD).move_to(box)
            big_in = _mono("input  8", 24, th.RED_LIGHT).move_to(inp)
            t_over = _exchange(
                self, w, [val, inp], [err, big_in],
                extras=[box.animate.set_stroke(color=th.RED, width=3.6).set_fill("#2a0c0c", opacity=0.96)],
                run_time=0.45,
            )
            self.screen_shake(intensity=0.05, cycles=3, run_time=0.3)
            _mark(self, "break")
            w.say(L3, already=t_over + 0.15)
            w.say(L4)
            w.ask("The box held 2.7. Why not this one?", target=box, direction=DOWN)

            num = _mono("5.75", 40, th.WHITE, BOLD).move_to(NUM_AT)
            in_575 = _mono("input  5.75", 24, th.TEXT).move_to(big_in)
            t_num = _exchange(self, w, [big_in], [in_575, num], run_time=0.4)
            w.say(L5, already=t_num)

            five = _mono("5", 36, th.AMBER_LIGHT, BOLD).move_to(num)
            frac = _mono("0.75", 32, th.CYAN_LIGHT, BOLD).move_to(num)
            t_split = _exchange(self, w, [num], [five, frac], run_time=0.3)
            self.play(five.animate.shift(LEFT * 1.15), frac.animate.shift(RIGHT * 1.25), run_time=0.45)
            w.say(L6, already=t_split + 0.45)

            sh_box = RoundedRectangle(
                corner_radius=0.1, width=2.65, height=1.28,
                stroke_color=th.AMBER, stroke_width=2.4,
                fill_color="#1c1408", fill_opacity=0.96,
            ).move_to(SH_AT)
            sh_name = _mono("shifter", 18, th.AMBER_LIGHT)
            sh_name.next_to(sh_box, UP, buff=0.1)
            t_sh = w.show(sh_box, sh_name, run_time=0.3)
            sh_box.set_z_index(1)
            sh_name.set_z_index(2)
            five.set_z_index(4)
            self.play(five.animate.move_to(sh_box.get_center() + UP * 0.24), run_time=0.5)
            times32 = _mono("×32", 26, th.AMBER_LIGHT).move_to(sh_box.get_center() + DOWN * 0.28)
            times32.set_z_index(4)
            t_32 = w.show(times32, run_time=0.25)
            w.say(L7, already=t_sh + 0.5 + t_32)

            cells = _table(TB_AT)
            tb_name = _mono("table", 18, th.PURPLE_LIGHT).move_to(TB_AT + UP * 0.78)
            t_tb = w.show(*cells, tb_name, run_time=0.3)
            self.play(cells[2].animate.set_fill(th.PURPLE, opacity=0.9), run_time=0.25)
            self.play(frac.animate.scale(0.55).move_to(cells[2]), run_time=0.45)
            got = _mono("1.68", 28, th.CYAN_LIGHT, BOLD).move_to(TB_AT + LEFT * 1.45)
            t_got = _exchange(self, w, [frac], [got], run_time=0.35)
            w.say(L8, already=t_tb + 0.25 + 0.45 + t_got)

            prod = _mono("54", 40, th.GREEN_LIGHT, BOLD).move_to(NUM_AT)
            t_prod = w.show(prod, run_time=0.3)
            w.say(L9, already=t_prod)

            t_land = 0.6
            self.play(
                prod.animate.move_to(box),
                FadeOut(err),
                box.animate.set_stroke(color=th.GREEN, width=3).set_fill("#071b11", opacity=0.96),
                run_time=t_land,
            )
            _forget(self, w, err)
            _mark(self, "repair")
            w.say(L10, already=t_land)
            w.name("shift, then a small table", box, direction=DOWN)
            w.say(L11)

            in_325 = _mono("input  3.25", 24, th.TEXT).move_to(in_575)
            num2 = _mono("3.25", 40, th.WHITE, BOLD).move_to(NUM_AT)
            t_clear = _exchange(
                self, w, [five, times32, got, prod, in_575], [in_325, num2],
                extras=[
                    cells[2].animate.set_fill(th.PURPLE_DARK, opacity=0.35),
                    box.animate.set_stroke(color=th.CYAN, width=2.4).set_fill("#071422", opacity=0.96),
                ],
                run_time=0.45,
            )
            w.say(L12, already=t_clear)

            three = _mono("3", 36, th.AMBER_LIGHT, BOLD).move_to(num2)
            three.set_z_index(4)
            quart = _mono("0.25", 32, th.CYAN_LIGHT, BOLD).move_to(num2)
            t_sp2 = _exchange(self, w, [num2], [three, quart], run_time=0.3)
            self.play(three.animate.shift(LEFT * 1.15), quart.animate.shift(RIGHT * 1.25), run_time=0.45)
            w.say(L13, already=t_sp2 + 0.45)

            self.play(three.animate.move_to(sh_box.get_center() + UP * 0.24), run_time=0.5)
            times8 = _mono("×8", 26, th.AMBER_LIGHT).move_to(sh_box.get_center() + DOWN * 0.28)
            t_8 = w.show(times8, run_time=0.25)
            w.say(L14, already=0.5 + t_8)

            self.play(
                cells[1].animate.set_fill(th.PURPLE, opacity=0.9),
                run_time=0.25,
            )
            self.play(quart.animate.scale(0.55).move_to(cells[1]), run_time=0.45)
            got2 = _mono("1.19", 28, th.CYAN_LIGHT, BOLD).move_to(TB_AT + LEFT * 1.45)
            t_119 = _exchange(self, w, [quart], [got2], run_time=0.35)
            w.say(L15, already=0.25 + 0.45 + t_119)

            fit = _mono("9.5", 36, th.GREEN_LIGHT, BOLD).move_to(NUM_AT)
            t_fit = w.show(fit, run_time=0.25)
            self.play(
                fit.animate.move_to(box),
                box.animate.set_stroke(color=th.GREEN, width=3).set_fill("#071b11", opacity=0.96),
                run_time=0.55,
            )
            w.say(L16, already=t_fit + 0.55)
            w.say(L17)

            shift_arrow = Arrow(
                sh_box.get_left() + LEFT * 1.2,
                sh_box.get_right() + RIGHT * 2.2,
                color=th.AMBER,
                stroke_width=9,
                buff=0,
                max_tip_length_to_length_ratio=0.1,
            )
            bits = VGroup(*[
                Square(side_length=0.24, stroke_width=0, fill_color=th.AMBER, fill_opacity=0.92)
                for _ in range(4)
            ]).arrange(RIGHT, buff=0.08)
            bits.move_to(shift_arrow.get_start() + RIGHT * 0.7)
            t_pic = _exchange(
                self, w,
                [three, times8, got2, tb_name, *cells],
                [shift_arrow, bits],
                run_time=0.45,
            )
            self.play(bits.animate.shift(RIGHT * 1.5), run_time=0.55)
            self.focus_on(shift_arrow, buffer_factor=1.45, run_time=0.8)
            w.say(L18, already=t_pic + 0.55 + 0.8)
