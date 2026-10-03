"""
Lab 01: Multiply is a pile of copies.

6 x 5 is copied by hand, then added to 30. An 8-bit grid fills
toward 64 copies beside a 42-gate adder and a multiplier that
grows to 456. -128 x -128 is +16384, and a 15-bit window reads
the sign bit as negative. The tall pile folds after it is shown.
3 x 5 is predicted one AND row at a time.
"""

from manim import *
import sys
from pathlib import Path

ANIM_DIR = Path(__file__).resolve().parent
if str(ANIM_DIR) not in sys.path:
    sys.path.insert(0, str(ANIM_DIR))

import theme as th
from components import KineticSiliconScene

L_COPY = (
    "Six times five is the product you can already finish by hand. "
    "The lower number is zero one zero one. Where that bit is one, "
    "copy zero one one zero into a fresh row. Where that bit is zero, "
    "copy nothing and leave the shift blank."
)
L_ROWS = (
    "Three rows are sitting under the problem now. The first copy is six, "
    "and it is not shifted at all. The middle copy is zero because that bit "
    "was off. The last copy is six moved two places, so it is worth twenty four."
)
L_SIX = (
    "Add the slow way, one copy at a time, the way you would check a column "
    "on paper. Six plus the blank middle row is still six. The zero bit "
    "contributed nothing, so the running total does not move. Keep that six."
)
L_JOIN = (
    "The shifted copy, worth twenty four, is the one that still has to join. "
    "Add it to the six you just kept. Look down the columns from the right "
    "before you trust a written total. Let the bits gather into a single pattern you can check."
)
L_THIRTY = (
    "Six plus twenty four is thirty. The columns settled on zero zero one one "
    "one one zero. That pattern is sixteen plus eight plus four plus two, and "
    "the ones place stays off. The pile of copies and the decimal agree."
)
L_GRID = (
    "Four bits needed only a few copies, and one of them was empty. Count every "
    "pair of bits in an eight bit multiply and the pile becomes sixty four copies. "
    "Watch the grid fill. Each new square is another copy to keep."
)
L_GATES = (
    "Beside the full grid sits a small adder, marked forty two gates. It only "
    "joins two numbers. The multiplier has to form every copy and then add the "
    "shifted rows, so its box grows until the count reads four hundred fifty six."
)
L_SIZE = (
    "The picture is the size you see. The adder stays small because adding is a "
    "short job. The multiplier keeps this large body because every copy has to "
    "be formed and then added, and sixty four copies are a lot of work."
)
L_NEG = (
    "The same pile works for negative numbers, until the window is too narrow "
    "to hold the answer. Take negative one hundred twenty eight times itself. "
    "Two negatives should give a positive, and the true product is sixteen "
    "thousand three hundred eighty four."
)
L_WINDOW = (
    "Write that product in bits. It is a one followed by fourteen zeros, with "
    "a leading zero still in front. In a wide enough row that leading zero keeps "
    "the number positive. A fifteen bit window cuts the leading zero off."
)
L_FLIP = (
    "The bit that used to mean sixteen thousand three hundred eighty four is now "
    "the sign. It did not change its ink. The window changed its job. Read as a "
    "sign, that same one flips the product, and the box shows a negative."
)
L_TALL = (
    "Come back to the copies themselves. Four partial product rows already stand "
    "in a tall stack, and a real multiply has many more. Adding every row one "
    "after another takes a long path. The stack can fold instead of waiting."
)
L_PAIRS = (
    "Watch the pairs close. The top two rows fold into one shorter row. The bottom "
    "two rows fold into one shorter row. The product does not change. Only the "
    "height changes. Two rows now hold what four rows held."
)
L_SHORT = (
    "That shorter stack is the compression. Each pair was reduced before the final "
    "add, so the waiting height is the two rows you see, not the four you started "
    "with. The copies are still all there. They are stacked in pairs."
)
L_PREDICT = (
    "Try one you can finish before the picture does. Three times five. Three is "
    "zero zero one one. Five is zero one zero one. Cover the answer and call the "
    "rows yourself. Every one bit in five copies three. Every zero bit copies nothing."
)
L_AND = (
    "The lowest bit of five is one, so the first row is a copy of three, zero zero "
    "one one. An and gate does that copy. It does not add yet. It only decides "
    "whether this shift position keeps the bits or throws them away."
)
L_BLANK = (
    "The next bit of five is zero, so the second row copies nothing. You should see "
    "a blank shift, zeros all the way across, moved one place to the left. If a one "
    "appears there, the rule was broken. Hold the blank and check it."
)
L_FIFTEEN = (
    "The following bit of five is one again, so another copy of three appears, "
    "shifted two places. That shift is worth twelve. Three plus a blank plus twelve "
    "is fifteen. The bits read zero zero one one one one, and the pile agrees."
)

GRID = DOWN * 8.2
SIGN = DOWN * 16.4
FOLD = DOWN * 24.6
PRED = DOWN * 32.8
PITCH = 0.46


def _mark(scene, tag):
    renderer = getattr(scene, "renderer", None)
    t = float(getattr(renderer, "time", 0.0) or 0.0)
    path = Path("/tmp") / f"hw_marks_{type(scene).__name__}.txt"
    with path.open("a") as handle:
        handle.write(f"{tag}\t{t:.3f}\n")


def _mono(text, size=22, color=th.TEXT):
    return Text(text, font=th.MONO, font_size=size, color=color)


def _num(text, size=32, color=th.WHITE):
    return Text(text, font=th.MONO, weight=BOLD, font_size=size, color=color)


def _mini(ch, color):
    box = RoundedRectangle(
        corner_radius=0.04,
        width=0.40,
        height=0.48,
        stroke_width=1.5,
        stroke_color=color,
        fill_color="#0e1526",
        fill_opacity=0.96,
    )
    glyph = _mono(ch, 16, color)
    glyph.move_to(box)
    return VGroup(box, glyph)


def _bits_at(pattern, shift, color, lsb):
    cells = []
    for i, ch in enumerate(reversed(pattern)):
        ink = color if ch == "1" else th.MUTED
        cell = _mini(ch, ink)
        cell.move_to(lsb + LEFT * (i + shift) * PITCH)
        cells.append(cell)
    return VGroup(*cells)


def _entry(shift, num, color):
    label = _mono(shift, 18, th.MUTED)
    value = _num(num, 32, color)
    label.next_to(value, LEFT, buff=0.32)
    return VGroup(label, value), value


class Lab01Multiplier(KineticSiliconScene):
    def construct(self):
        Path("/tmp/hw_marks_Lab01Multiplier.txt").write_text("")
        with self.world() as w:
            row2 = self._opening(w)
            self._sum_to_thirty(w, row2)
            self._eight_bit(w)
            self._signed_window(w)
            self._fold(w)
            self._three_times_five(w)

    def _go(self, dest, run_time=1.0):
        self.play(
            self.camera.frame.animate.set_width(self.default_frame_width).move_to(dest),
            run_time=run_time,
            rate_func=smooth,
        )
        return run_time

    def _opening(self, w):
        head = VGroup(
            _mono("    0 1 1 0", 26, th.WHITE),
            _mono("  × 0 1 0 1", 26, th.AMBER_LIGHT),
            _mono("  ---------", 26, th.MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        head.move_to(UP * 1.6 + LEFT * 3.2)
        w.show(head, run_time=0.4)
        _mark(self, "start")

        row1 = _mono("    0 1 1 0    ×1", 24, th.GREEN_LIGHT)
        row0 = _mono("  0 0 0 0      ×0", 24, th.MUTED)
        row2 = _mono("0 1 1 0        ×1", 24, th.GREEN_LIGHT)
        rows = VGroup(row1, row0, row2).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        rows.next_to(head, DOWN, buff=0.2, aligned_edge=LEFT)
        self.play(FadeIn(row1, shift=UP * 0.05), run_time=0.35)
        self.play(FadeIn(row0, shift=UP * 0.05), run_time=0.3)
        self.play(FadeIn(row2, shift=UP * 0.05), run_time=0.35)
        w.keep(rows)
        w.say(L_COPY, already=1.4)
        return row2

    def _sum_to_thirty(self, w, row2):
        e6, n6 = _entry("shift 0", "6", th.GREEN_LIGHT)
        e0, n0 = _entry("shift 1", "0", th.MUTED)
        e24, n24 = _entry("shift 2", "24", th.AMBER_LIGHT)
        col = VGroup(e6, e0, e24).arrange(DOWN, aligned_edge=RIGHT, buff=0.18)
        col.move_to(RIGHT * 2.55 + UP * 0.45)
        spent = w.show(col, run_time=0.5)
        w.say(L_ROWS, already=spent)

        sub = _num("6", 32, th.GREEN_LIGHT).next_to(n0, RIGHT, buff=0.65)
        spent = w.show(sub, run_time=0.35)
        w.say(L_SIX, already=spent)

        self.play(
            n24.animate.set_color(th.WHITE),
            sub.animate.set_color(th.AMBER_LIGHT),
            run_time=0.35,
        )
        w.say(L_JOIN, already=0.35)

        bits = _mono("0 0 1 1 1 1 0", 26, th.CYAN_LIGHT)
        bits.next_to(row2, DOWN, buff=0.32, aligned_edge=LEFT)
        total = _num("30", 40, th.WHITE).next_to(n24, RIGHT, buff=0.55)
        spent = w.show(bits, total, run_time=0.45)
        w.say(L_THIRTY, already=spent)

    def _eight_bit(self, w):
        cells = VGroup(*[
            Rectangle(
                width=0.32,
                height=0.32,
                stroke_width=1.2,
                stroke_color=th.AMBER,
                fill_color=th.AMBER,
                fill_opacity=0.06,
            )
            for _ in range(64)
        ]).arrange_in_grid(rows=8, cols=8, buff=0.05)
        cells.move_to(GRID + LEFT * 3.55)

        adder_box = RoundedRectangle(
            corner_radius=0.08,
            width=1.8,
            height=1.7,
            stroke_color=th.GREEN,
            stroke_width=2.2,
            fill_color="#0e1526",
            fill_opacity=0.95,
        )
        adder_lab = _mono("adder", 16, th.GREEN)
        adder_num = _num("42", 26, th.WHITE)
        adder_inner = VGroup(adder_lab, adder_num).arrange(DOWN, buff=0.08).move_to(adder_box)
        adder = VGroup(adder_box, adder_inner)
        adder.move_to(GRID + RIGHT * 0.15)

        mult_box = RoundedRectangle(
            corner_radius=0.08,
            width=1.45,
            height=1.3,
            stroke_color=th.AMBER,
            stroke_width=2.2,
            fill_color="#0e1526",
            fill_opacity=0.95,
        )
        mult_lab = _mono("multiply", 16, th.AMBER_LIGHT)
        mult_lab.move_to(mult_box.get_center() + UP * 0.22)
        mult = VGroup(mult_box, mult_lab)
        mult.move_to(GRID + RIGHT * 3.85)

        copies = _num("64", 32, th.AMBER_LIGHT).next_to(cells, DOWN, buff=0.18)

        move = self._go(GRID, run_time=1.0)
        shown = w.show(cells, adder, mult, run_time=0.4)
        self.play(
            LaggedStart(
                *[c.animate.set_fill(th.AMBER, opacity=0.92) for c in cells],
                lag_ratio=0.03,
            ),
            run_time=8.4,
        )
        label = w.show(copies, run_time=0.3)
        w.say(L_GRID, already=move + shown + 8.4 + label)

        self.play(mult.animate.scale(1.9), run_time=1.25)
        gates = _num("456", 32, th.WHITE)
        gates.move_to(mult.get_center() + DOWN * 0.4)
        gate_in = w.show(gates, run_time=0.3)
        w.say(L_GATES, already=1.25 + gate_in)
        w.say(L_SIZE, already=0)

    def _signed_window(self, w):
        move = self._go(SIGN, run_time=1.0)
        expr = _num("-128  ×  -128", 30, th.WHITE).move_to(SIGN + UP * 2.15)
        positive = _num("+16384", 36, th.GREEN_LIGHT).move_to(SIGN + UP * 1.15)
        shown = w.show(expr, positive, run_time=0.45)
        w.say(L_NEG, already=move + shown)

        pattern = "0100000000000000"
        row = VGroup(*[
            _mini(ch, th.AMBER_LIGHT if i == 1 else th.MUTED)
            for i, ch in enumerate(pattern)
        ]).arrange(RIGHT, buff=0.045)
        row.move_to(SIGN + DOWN * 0.35)
        left = row[1].get_left()[0] - 0.08
        right = row[15].get_right()[0] + 0.08
        bracket = RoundedRectangle(
            corner_radius=0.06,
            width=right - left,
            height=row.height + 0.18,
            stroke_color=th.AMBER,
            stroke_width=2.6,
            fill_opacity=0,
        )
        bracket.move_to([(left + right) / 2, row.get_y(), 0])
        spent = w.show(row, run_time=0.4)
        self.play(
            FadeIn(bracket),
            row[0].animate.set_opacity(0.22),
            run_time=0.45,
        )
        w.keep(bracket)
        w.say(L_WINDOW, already=spent + 0.45)
        w.ask("What sign will this window report?", target=bracket, direction=DOWN)

        negative = _num("-16384", 36, th.RED_LIGHT).move_to(positive)
        hot_box = row[1][0]
        hot_glyph = row[1][1]
        self.play(FadeOut(positive), run_time=0.16)
        self.remove(positive)
        dim = [
            row[i].animate.set_opacity(0.32)
            for i in range(16)
            if i != 1
        ]
        self.play(
            FadeIn(negative),
            hot_box.animate.set_fill(th.RED, opacity=0.96).set_stroke(th.RED_LIGHT, width=3.2),
            hot_glyph.animate.set_color(th.WHITE),
            bracket.animate.set_stroke(th.RED, width=3.2),
            *dim,
            run_time=0.5,
        )
        w.keep(negative)
        self.screen_shake(intensity=0.04, cycles=2, run_time=0.22)
        self.focus_on(row[1], buffer_factor=9, run_time=0.85)
        _mark(self, "break")
        w.say(L_FLIP, already=0.16 + 0.5 + 0.22 + 0.85)

    def _fold(self, w):
        bars = VGroup(*[
            RoundedRectangle(
                corner_radius=0.05,
                width=5.4 - i * 0.55,
                height=0.42,
                stroke_width=0,
                fill_color=th.AMBER,
                fill_opacity=0.92,
            )
            for i in range(4)
        ]).arrange(DOWN, buff=0.16)
        bars.move_to(FOLD)
        move = self._go(FOLD, run_time=1.05)
        shown = w.show(bars, run_time=0.4)
        w.say(L_TALL, already=move + shown)

        folded = VGroup(*[
            RoundedRectangle(
                corner_radius=0.05,
                width=width,
                height=0.5,
                stroke_width=0,
                fill_color=th.GREEN,
                fill_opacity=0.92,
            )
            for width in (5.2, 4.5)
        ]).arrange(DOWN, buff=0.2)
        folded.move_to(bars)
        self.play(ReplacementTransform(bars, folded), run_time=1.15)
        w.keep(folded)
        w.say(L_PAIRS, already=1.15)
        w.say(L_SHORT, already=0)
        _mark(self, "repair")
        w.name("Wallace", folded, direction=DOWN)

    def _three_times_five(self, w):
        lsb3 = PRED + RIGHT * 1.9 + UP * 2.05
        lsb5 = PRED + RIGHT * 1.9 + UP * 1.35
        lsb_p0 = PRED + RIGHT * 1.9 + UP * 0.25
        lsb_p1 = PRED + RIGHT * 1.9 + DOWN * 0.45
        lsb_p2 = PRED + RIGHT * 1.9 + DOWN * 1.15
        lsb_sum = PRED + RIGHT * 1.9 + DOWN * 2.05

        three = _num("3", 28, th.WHITE).move_to(lsb3 + LEFT * 2.6)
        five = _num("5", 28, th.AMBER_LIGHT).move_to(lsb5 + LEFT * 2.6)
        times = _mono("×", 26, th.AMBER_LIGHT).move_to(five.get_center() + LEFT * 0.7)
        factor3 = _bits_at("0011", 0, th.WHITE, lsb3)
        factor5 = _bits_at("0101", 0, th.AMBER_LIGHT, lsb5)

        move = self._go(PRED, run_time=1.0)
        shown = w.show(three, five, times, factor3, factor5, run_time=0.45)
        w.say(L_PREDICT, already=move + shown)

        row_and = _bits_at("0011", 0, th.GREEN_LIGHT, lsb_p0)
        tag1 = _mono("×1", 16, th.GREEN_LIGHT).move_to(lsb_p0 + RIGHT * 0.7)
        running = _num("3", 36, th.GREEN_LIGHT).move_to(PRED + RIGHT * 4.55 + UP * 0.15)
        spent = w.show(row_and, tag1, running, run_time=0.4)
        self.play(factor5[0][0].animate.set_stroke(th.GREEN_LIGHT, width=3.2), run_time=0.25)
        w.say(L_AND, already=spent + 0.25)

        row_zero = _bits_at("0000", 1, th.MUTED, lsb_p1)
        tag0 = _mono("×0", 16, th.MUTED).move_to(lsb_p1 + RIGHT * 0.7)
        spent = w.show(row_zero, tag0, run_time=0.4)
        self.play(factor5[1][0].animate.set_stroke(th.MUTED, width=3.0), run_time=0.25)
        w.say(L_BLANK, already=spent + 0.25)

        row_shift = _bits_at("0011", 2, th.GREEN_LIGHT, lsb_p2)
        tag2 = _mono("×1", 16, th.GREEN_LIGHT).move_to(lsb_p2 + RIGHT * 0.7)
        rule = Line(
            lsb_sum + LEFT * 2.5 + UP * 0.38,
            lsb_sum + RIGHT * 0.35 + UP * 0.38,
            color=th.MUTED,
            stroke_width=2,
        )
        total_bits = _bits_at("001111", 0, th.WHITE, lsb_sum)
        fifteen = _num("15", 40, th.GREEN_LIGHT).move_to(running)
        spent = w.show(row_shift, tag2, run_time=0.4)
        self.play(factor5[2][0].animate.set_stroke(th.GREEN_LIGHT, width=3.2), run_time=0.25)
        self.play(FadeOut(running), run_time=0.16)
        self.remove(running)
        self.play(FadeIn(rule), FadeIn(total_bits), FadeIn(fifteen), run_time=0.4)
        w.keep(rule, total_bits, fifteen)
        w.say(L_FIFTEEN, already=spent + 0.25 + 0.16 + 0.4)
