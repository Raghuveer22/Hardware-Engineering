"""
Lab 02: The second product changes sign.

128 x 128 = 16384 fits under a 32767 ceiling. The second add reaches
32768 and the reading flips to -32768, whose bits are 0x8000.
Widening the tank lets +32768 sit inside. Zero-painting -5 climbs;
one-painting falls, and only then is the trick named. A third
128 x 128 in the wide tank lands on 49152 and still fits.
"""

from manim import *
import sys
from pathlib import Path

ANIM_DIR = Path(__file__).resolve().parent
if str(ANIM_DIR) not in sys.path:
    sys.path.insert(0, str(ANIM_DIR))

import theme as th
from components import KineticSiliconScene

L_FIRST = (
    "One hundred twenty eight times one hundred twenty eight is sixteen "
    "thousand three hundred eighty four. Watch the tank. A sixteen bit reading "
    "tops out at thirty two thousand seven hundred sixty seven. This first product "
    "climbs halfway and stays under the ceiling."
)
L_ROOM = (
    "Look at the empty space above the fill. The level stopped near the middle, "
    "and the color is still calm. Nothing has crossed the line marked at the rim. "
    "Remember this height. The next copy of the same product is about to be poured in."
)
L_INVITE = (
    "A second product is the same sixteen thousand three hundred eighty four. "
    "Add it to the sixteen thousand three hundred eighty four already in the tank. "
    "Do the sum on the side before you trust the reading. The pencil total and the "
    "tank may disagree."
)
L_PENCIL = (
    "Sixteen thousand three hundred eighty four plus itself is thirty two thousand "
    "seven hundred sixty eight. That is the honest total. It is one step past the "
    "rim of a sixteen bit tank. The pencil has the right number. The tank has not answered yet."
)
L_FLIP = (
    "The level hits the rim and the reading breaks. Thirty two thousand seven hundred "
    "sixty eight does not fit in this tank. The digits flip, and the window reports "
    "negative thirty two thousand seven hundred sixty eight. The pencil total is still positive."
)
L_BITS = (
    "Look at the bits of that flipped reading. The pattern is one followed by fifteen "
    "zeros. In hex that single hot bit is written zero x eight zero zero zero. Only "
    "the sign bit is on. Every magnitude bit beside it is off."
)
L_WHY = (
    "Both products were ordinary positive copies, and their pencil sum is positive too. "
    "The tank stores the sum in sixteen bits. With only the top bit set, the hardware "
    "reads the most negative sixteen bit value, even though we added positives."
)
L_GROW = (
    "Now let the tank grow upward, past the old rim. The old ceiling stays drawn where "
    "it was, so you can still see the line that used to stop us. The same quantity is "
    "poured back in. Watch whether it crosses that remembered line or sits on it."
)
L_FITS = (
    "The honest total, thirty two thousand seven hundred sixty eight, now sits inside. "
    "The fill reaches the old rim and then stops, and empty wall shows above it. The "
    "reading is positive again. There is room in the tank for another pour."
)
L_FIVE = (
    "Leave the wide tank where it is. On the side, take a small negative, negative five. "
    "The low bits of negative five are one zero one one. What you paint to the left of "
    "those bits decides whether the value stays negative or climbs away."
)
L_ZEROS = (
    "Paint zeros on the left, so the row reads zero zero zero zero one zero one one. "
    "The meter beside it rises. The hardware now sees a positive eleven, not negative "
    "five. The sign was lost when those zeros covered the left side."
)
L_HOLD = (
    "Stay with that wrong climb for a moment. The true value is still negative five, "
    "written beside the bits, but the painted row no longer says so. Zeros on the left "
    "turned a negative into a positive. The meter is high for a reason."
)
L_ONES = (
    "Paint ones on the left instead, so the row reads one one one one one zero one one. "
    "Watch the meter. It falls. The left side is carrying the sign down with the value, "
    "and the climb we just saw is undone by those ones."
)
L_STAYS = (
    "Negative five stays negative five. The low bits never changed. Only the paint on "
    "the left changed, and that was enough to bring the level back down. A negative "
    "kept its direction because the left bits agreed with the sign."
)
L_THIRD = (
    "Come back to the wide tank. It still holds thirty two thousand seven hundred sixty "
    "eight. Pour in one more product, another sixteen thousand three hundred eighty four. "
    "Add those two yourself before the level moves. The room above the fill matters."
)
L_SUM = (
    "Thirty two thousand seven hundred sixty eight plus sixteen thousand three hundred "
    "eighty four is forty nine thousand one hundred fifty two. That is three copies of "
    "the original product. Check the pencil column against the number that lands in the reading."
)
L_LEVEL = (
    "The level rises to that new total and the color stays calm. The fill is higher than "
    "the old rim and still short of the top. Forty nine thousand one hundred fifty two "
    "fits. You can see leftover wall above the liquid."
)
L_WHY_WIDE = (
    "A narrow tank would have flipped again on this third copy, the same way it flipped "
    "on the second. The wide tank exists so a running sum of positive products can keep "
    "climbing without the sign bit turning the total around."
)


def _mark(scene, tag):
    renderer = getattr(scene, "renderer", None)
    t = float(getattr(renderer, "time", 0.0) or 0.0)
    path = Path("/tmp") / f"hw_marks_{type(scene).__name__}.txt"
    with path.open("a") as handle:
        handle.write(f"{tag}\t{t:.3f}\n")


def _mono(text, size=22, color=th.TEXT):
    return Text(text, font=th.MONO, font_size=size, color=color)


def _num(text, size=28, color=th.WHITE):
    return Text(text, font=th.MONO, weight=BOLD, font_size=size, color=color)


def _fill_to(tank, y_top, color):
    y_bottom = tank.get_bottom()[1] + 0.12
    y_limit = tank.get_top()[1] - 0.1
    y_top = max(y_bottom + 0.12, min(y_top, y_limit))
    rect = Rectangle(
        width=max(0.24, tank.width - 0.26),
        height=y_top - y_bottom,
        stroke_width=0,
        fill_color=color,
        fill_opacity=0.9,
    )
    rect.move_to([tank.get_x(), (y_bottom + y_top) / 2, 0])
    return rect


def _meter_fill(meter, fraction, color):
    fraction = max(0.08, min(fraction, 1.0))
    height = (meter.height - 0.16) * fraction
    rect = Rectangle(
        width=meter.width - 0.12,
        height=height,
        stroke_width=0,
        fill_color=color,
        fill_opacity=0.92,
    )
    rect.align_to(meter, DOWN).shift(UP * 0.08)
    rect.set_x(meter.get_x())
    return rect


def _bit_row():
    cells = []
    for i in range(16):
        hot = i == 0
        box = RoundedRectangle(
            corner_radius=0.04,
            width=0.30,
            height=0.44,
            stroke_width=1.6 if hot else 1.1,
            stroke_color=th.RED_LIGHT if hot else th.BORDER,
            fill_color=th.RED if hot else "#0e1526",
            fill_opacity=0.96,
        )
        glyph = _mono("1" if hot else "0", 15, th.WHITE if hot else th.MUTED)
        glyph.move_to(box)
        cells.append(VGroup(box, glyph))
    row = VGroup(*cells).arrange(RIGHT, buff=0.04)
    return row


class Lab02MACUnit(KineticSiliconScene):
    def construct(self):
        Path("/tmp/hw_marks_Lab02MACUnit.txt").write_text("")
        with self.world() as w:
            tank, reading, fill, rim_y, levels = self._open_tank(w)
            reading, fill = self._second_product(w, tank, reading, fill, levels)
            self._widen(w, tank, reading, fill, rim_y, levels)
            self._sign_paint(w)
            self._third_product(w, tank, levels)

    def _replace(self, reading, text, color, size=30):
        new = _num(text, size, color)
        new.move_to(reading.get_left(), aligned_edge=LEFT)
        self.play(FadeOut(reading), run_time=0.16)
        self.remove(reading)
        self.play(FadeIn(new), run_time=0.18)
        return new, 0.34

    def _open_tank(self, w):
        tank = RoundedRectangle(
            corner_radius=0.1,
            width=2.15,
            height=3.4,
            stroke_color=th.CYAN,
            stroke_width=2.4,
            fill_color="#071422",
            fill_opacity=0.4,
        )
        tank.move_to(LEFT * 4.55 + DOWN * 0.95)
        rim = Line(
            tank.get_left() + RIGHT * 0.06,
            tank.get_right() + LEFT * 0.06,
            color=th.AMBER,
            stroke_width=3,
        )
        rim.set_y(tank.get_top()[1] - 0.02)
        cap = _mono("32767", 18, th.MUTED).next_to(rim, LEFT, buff=0.1)
        reading = _num("0", 30, th.WHITE).next_to(tank, RIGHT, buff=0.55)
        rim_y = tank.get_top()[1]
        y_in = tank.get_bottom()[1] + 0.12
        y_full = rim_y - 0.05
        levels = {
            "half": y_in + 0.5 * (y_full - y_in),
            "full": y_full,
            "third": y_in + (y_full - y_in) * (49152 / 32768),
        }
        shown = w.show(tank, rim, cap, reading, run_time=0.35)
        fill = _fill_to(tank, tank.get_bottom()[1] + 0.28, th.GREEN)
        self.fill = fill
        w.keep(fill)
        self.play(FadeIn(fill), run_time=0.2)
        _mark(self, "start")
        half = _fill_to(tank, levels["half"], th.GREEN)
        self.play(Transform(fill, half), run_time=0.6)
        reading, swap = self._replace(reading, "16384", th.WHITE)
        w.keep(reading)
        w.say(L_FIRST, already=shown + 0.2 + 0.6 + swap)
        w.say(L_ROOM, already=0)
        return tank, reading, fill, rim_y, levels

    def _second_product(self, w, tank, reading, fill, levels):
        left = 1.7
        first = _num("16384", 28, th.WHITE)
        first.move_to(RIGHT * left + UP * 1.45, aligned_edge=LEFT)
        second = _num("+16384", 28, th.AMBER_LIGHT).next_to(first, DOWN, aligned_edge=LEFT, buff=0.14)
        rule = Line(ORIGIN, RIGHT * 1.45, color=th.MUTED, stroke_width=2)
        rule.next_to(second, DOWN, aligned_edge=LEFT, buff=0.08)
        honest = _num("32768", 30, th.WHITE).next_to(rule, DOWN, aligned_edge=LEFT, buff=0.1)
        extra = _num("+16384", 28, th.AMBER_LIGHT).next_to(honest, DOWN, aligned_edge=LEFT, buff=0.16)
        result = _num("49152", 32, th.GREEN_LIGHT).next_to(extra, DOWN, aligned_edge=LEFT, buff=0.1)
        self.pencil = (first, second, rule, honest, extra, result)

        spent = w.show(first, second, run_time=0.4)
        w.say(L_INVITE, already=spent)
        spent = w.show(rule, honest, run_time=0.4)
        w.say(L_PENCIL, already=spent)

        burst = _fill_to(tank, levels["full"], th.RED)
        self.play(
            Transform(fill, burst),
            tank.animate.set_stroke(color=th.RED, width=3.4),
            run_time=0.6,
        )
        reading, swap = self._replace(reading, "-32768", th.RED_LIGHT)
        w.keep(reading)
        self.screen_shake(intensity=0.05, cycles=3, run_time=0.24)
        _mark(self, "break")
        w.say(L_FLIP, already=0.6 + swap + 0.24)

        bits = _bit_row()
        hex_label = _num("0x8000", 26, th.RED_LIGHT)
        pattern = VGroup(hex_label, bits).arrange(DOWN, buff=0.12)
        pattern.move_to(RIGHT * 2.55 + UP * 3.05)
        spent = w.show(pattern, run_time=0.4)
        self.focus_on(pattern, buffer_factor=1.45, run_time=0.8)
        w.say(L_BITS, already=spent + 0.8)
        self.reset_camera(run_time=0.6)
        w.ask("Why did a positive sum change sign?")
        w.say(L_WHY, already=0)
        return reading, fill

    def _widen(self, w, tank, reading, fill, rim_y, levels):
        wide = RoundedRectangle(
            corner_radius=0.1,
            width=tank.width,
            height=6.05,
            stroke_color=th.GREEN,
            stroke_width=2.4,
            fill_color="#071422",
            fill_opacity=0.4,
        )
        wide.align_to(tank, DOWN)
        wide.set_x(tank.get_x())
        calmed = _fill_to(wide, levels["full"], th.GREEN)
        self.play(
            Transform(tank, wide),
            Transform(fill, calmed),
            run_time=0.95,
        )
        reading, swap = self._replace(reading, "+32768", th.GREEN_LIGHT)
        w.keep(reading)
        _mark(self, "repair")
        w.say(L_GROW, already=0.95 + swap)
        w.say(L_FITS, already=0)
        room = Square(side_length=0.2, stroke_opacity=0, fill_opacity=0)
        room.move_to([tank.get_right()[0] + 0.15, (tank.get_top()[1] + rim_y) / 2, 0])
        w.name("32-bit headroom", room, direction=RIGHT)
        self.reading = reading

    def _sign_paint(self, w):
        true = _num("-5", 34, th.WHITE)
        low = _mono("1 0 1 1", 26, th.WHITE)
        zeros = _mono("0 0 0 0", 26, th.AMBER_LIGHT)
        ones = _mono("1 1 1 1", 26, th.GREEN_LIGHT)
        low.move_to(RIGHT * 2.35 + DOWN * 2.15)
        zeros.next_to(low, LEFT, buff=0.12)
        ones.move_to(zeros)
        true.next_to(VGroup(zeros, low), UP, buff=0.16)
        meter = RoundedRectangle(
            corner_radius=0.08,
            width=0.5,
            height=1.7,
            stroke_color=th.CYAN,
            stroke_width=2.2,
            fill_color="#071422",
            fill_opacity=0.35,
        )
        meter.next_to(low, RIGHT, buff=0.45)
        spent = w.show(true, low, run_time=0.4)
        w.say(L_FIVE, already=spent)

        low_fill = _meter_fill(meter, 0.12, th.AMBER)
        high_fill = _meter_fill(meter, 0.88, th.RED)
        wrong = _num("+11", 28, th.RED_LIGHT).next_to(meter, DOWN, buff=0.12)
        spent = w.show(zeros, meter, run_time=0.35)
        w.keep(low_fill)
        self.play(FadeIn(low_fill), run_time=0.15)
        self.play(Transform(low_fill, high_fill), FadeIn(wrong), run_time=0.7)
        w.keep(wrong)
        w.say(L_ZEROS, already=spent + 0.15 + 0.7)
        w.say(L_HOLD, already=0)

        fallen = _meter_fill(meter, 0.28, th.GREEN)
        stayed = _num("-5", 28, th.GREEN_LIGHT).move_to(wrong)
        self.play(FadeOut(zeros), run_time=0.16)
        self.remove(zeros)
        self.play(FadeIn(ones), run_time=0.2)
        w.keep(ones)
        self.play(Transform(low_fill, fallen), run_time=0.65)
        self.play(FadeOut(wrong), run_time=0.16)
        self.remove(wrong)
        self.play(FadeIn(stayed), run_time=0.2)
        w.keep(stayed)
        w.say(L_ONES, already=0.16 + 0.2 + 0.65 + 0.16 + 0.2)
        w.say(L_STAYS, already=0)
        w.name("sign extension", ones, direction=UP)

    def _third_product(self, w, tank, levels):
        extra = self.pencil[4]
        result = self.pencil[5]
        spent = w.show(extra, run_time=0.35)
        w.say(L_THIRD, already=spent)
        spent = w.show(result, run_time=0.35)
        w.say(L_SUM, already=spent)

        higher = _fill_to(tank, levels["third"], th.GREEN)
        self.play(Transform(self.fill, higher), run_time=0.85)
        self.reading, swap = self._replace(self.reading, "49152", th.GREEN_LIGHT, size=30)
        w.keep(self.reading)
        w.say(L_LEVEL, already=0.85 + swap)
        w.say(L_WHY_WIDE, already=0)
