"""
Lab 00-Prep: one expression, followed until the hardware idea is forced.

y = (a + b) * (c + d) with a=3, b=2, c=4, d=1 stays on screen.
The CPU, graph, register, and bus grow out of that picture. Spoken lines
are not printed. Questions and short names are drawn, not said.
"""

from manim import *
import sys
from pathlib import Path

ANIM_DIR = Path(__file__).resolve().parent
if str(ANIM_DIR) not in sys.path:
    sys.path.insert(0, str(ANIM_DIR))

import theme as th
from components import KineticSiliconScene
from components.kinematics import VoiceoverTracker

# Spoken lines, in order. On-screen questions and names are not in this list.
L_KNOW = "You already know this. a is 3, b is 2, c is 4, and d is 1. Add on the left, add on the right, then multiply those two results. Nothing here is new arithmetic. What changes is who does each step, and when that result is allowed to move."
L_CPU = "A CPU runs one line, then the next, then the one after that. Right now the only live line is t1 equals a plus b. The second add and the multiply are still waiting. Until this line finishes, those other two lines do not run."
L_LEFT = "Watch only the left adder. The inputs on it are 3 and 2. Add them yourself before the 5 appears: 3 plus 2. The right adder is still empty, and the multiply has nothing to read. The CPU is still pointing at that first line."
L_RIGHT = "Now the right adder. Its inputs are 4 and 1. Add those before its 5 appears: 4 plus 1. Both adders will hold the same number, and neither result has traveled yet. The multiply is still waiting on the two wires beneath it."
L_INTO = "Both fives leave the adders and ride the short wires into the multiply. Do not wait for the CPU. Multiply them yourself, 5 times 5, and say that product out loud. It stays hidden until you have had a moment to answer."
L_LIVE = "There is the product, 25, already fixed by the two fives. Look back at the CPU. It is still on t1 equals a plus b. The other two lines never became the current line. The graph held 5, 5, and 25 while that first line stayed put."
L_WIRE = "The multiply is already finished. A byte from memory is still charging the long wire, and that trip is not free. The short wire costs about two tenths of a picojoule. The long wire costs about two hundred. The arithmetic was the cheap part."
L_COMB = "The pair on the left is only a wire. Change the input from 0 to 1 and the output moves with it, in the same moment, with nothing stored between them. There is no tick. If the input falls back to 0, the output falls back too."
L_FLOP = "The box on the right waits. Its input changes to 1, and its output stays the old 0. On the timeline the data edge sits well to the left of the tick, so the new bit has been quiet. When the tick arrives, the output copies that settled 1."
L_WINDOW = "Look at the shaded gap between that data edge and the tick. The bit arrived early, sat still, and the tick took a clean picture of it. The output became 1 because the change and the tick were far apart. Keep your eye on the edge."
L_META = "The same edge now slides right, into the tick itself. The bit is still changing while the picture is taken, so there is no settled value to copy. The output does not become 1. It comes back as X, which means the box stored garbage."
L_ORDER = "C is supposed to receive what B holds. B holds 20, and A holds 10. Watch the ordered write. B is updated to 10 first, and the 20 leaves the box. C then reads B and receives 10. The 20 that C needed never arrives."
L_FREEZE = "Put 20 back into B, and clear C. This time both right-hand sides are read before either write. The 10 from A and the 20 from B are held still, then the writes land together. B receives 10, and C still receives 20."
L_PREDICT = "New numbers, same two writes. A now holds 4, and B now holds 7. C is empty again. Use the rule you just watched. If the writes go in order, B changes before C reads. If the right-hand sides freeze, C reads the value B holds now."
L_SECOND = "The frozen pair lands. B receives 4, the value A held. C receives 7, the value B held before either write. Check the ordered alternative in your head: that path would have handed C a 4. The cells show 7, so the old value moved."
L_KNOCK = "The CPU writes a single 1 into this register. That 1 is the whole message. As soon as the write finishes, the CPU dims and steps away. It does not stay to push the remaining bytes. The register holds the 1 so the other side can notice."
L_BANKS = "Count the bytes into the left bank: 1, then 2, then 3, then 4. Those four arrive from the bus after the CPU has already left. The right bank is not waiting on them. It is already working the previous batch, so the banks are on different jobs."
L_PY1 = "Same adder, driven the way a Python check drives it. First stimulus: 3 plus 2. You already know this pair from the expression above. The sum is 5. The circle does not remember the expression. It only adds the two numbers placed on it."
L_PY2 = "Second check, smaller on purpose. 1 plus 1. Add it before you trust the circle: the only honest answer is 2. If the adder had kept the previous 5, this check would fail. The old sum leaves, and 2 replaces it."
L_PY3 = "Third check: 8 plus negative 1. The bits of 8 are 1000, and the signed nibble for negative 1 is 1111. Add the columns yourself. The low four bits are 0111, and that pattern is 7. Eight plus negative one is 7."
L_CLOSE = "The expression above never left. The two adds and the multiply were already live while the CPU sat on the first line. A register kept an old value that an ordered write would have destroyed. Moving a byte on the long wire cost more than the multiply."


def _mark(scene, tag):
    renderer = getattr(scene, "renderer", None)
    t = float(getattr(renderer, "time", 0.0) or 0.0)
    path = Path("/tmp") / f"hw_marks_{type(scene).__name__}.txt"
    with path.open("a") as handle:
        handle.write(f"{tag}\t{t:.3f}\n")


def _op(symbol, color):
    circ = Circle(
        radius=0.46, color=color, stroke_width=2.6,
        fill_color="#071422", fill_opacity=0.96,
    )
    sym = Text(symbol, font=th.MONO, weight=BOLD, font_size=28, color=th.WHITE).move_to(circ)
    return VGroup(circ, sym)


def _code_line(text, active):
    box = RoundedRectangle(
        corner_radius=0.08, width=4.5, height=0.58,
        stroke_color=th.AMBER if active else th.BORDER,
        stroke_width=2.4 if active else 1.2,
        fill_color="#1c1408" if active else "#0e1526",
        fill_opacity=0.96 if active else 0.35,
    )
    lbl = Text(
        text, font=th.MONO, font_size=20,
        color=th.AMBER_LIGHT if active else th.MUTED,
    ).move_to(box)
    if not active:
        lbl.set_opacity(0.28)
    return VGroup(box, lbl)


def _expr_pair(left, right, color):
    a = Text(left, font=th.MONO, weight=BOLD, font_size=28, color=color)
    op = Text("+", font=th.MONO, font_size=26, color=th.MUTED)
    b = Text(right, font=th.MONO, weight=BOLD, font_size=28, color=color)
    return VGroup(a, op, b).arrange(RIGHT, buff=0.1)


def _box_value(title, val, color, center):
    box = RoundedRectangle(
        corner_radius=0.1, width=1.55, height=1.2,
        stroke_color=color, stroke_width=2.2,
        fill_color="#0e1526", fill_opacity=0.96,
    )
    box.move_to(center)
    cap = Text(title, font=th.MONO, font_size=16, color=color).move_to(box.get_top() + DOWN * 0.24)
    num = Text(str(val), font=th.MONO, weight=BOLD, font_size=30, color=th.WHITE)
    num.move_to(box.get_center() + DOWN * 0.1)
    return box, cap, num


def _plain_bit(val, color, center):
    box = RoundedRectangle(
        corner_radius=0.08, width=0.72, height=0.72,
        stroke_color=color, stroke_width=2.2,
        fill_color="#0e1526", fill_opacity=0.96,
    )
    box.move_to(center)
    txt = Text(str(val), font=th.MONO, weight=BOLD, font_size=28, color=color).move_to(box)
    return box, txt


def _nibble_row(label, bits, color):
    cap = Text(label, font=th.MONO, font_size=18, color=color)
    glyphs = VGroup()
    for bit in bits:
        box = RoundedRectangle(
            corner_radius=0.04, width=0.42, height=0.48,
            stroke_color=color, stroke_width=1.6,
            fill_color="#0e1526", fill_opacity=0.96,
        )
        txt = Text(bit, font=th.MONO, weight=BOLD, font_size=18, color=color).move_to(box)
        glyphs.add(VGroup(box, txt))
    glyphs.arrange(RIGHT, buff=0.06)
    cap.next_to(glyphs, LEFT, buff=0.16)
    return VGroup(cap, glyphs)


def _line_dur(line):
    return VoiceoverTracker(line).duration


class Lab00PrepPrimer(KineticSiliconScene):
    """One expression. The CPU stays on line 1 while the graph already holds 25."""

    def construct(self):
        mark_path = Path("/tmp") / "hw_marks_Lab00PrepPrimer.txt"
        mark_path.write_text("")
        with self.world() as w:
            eq = Text(
                "y  =  (a + b)  ×  (c + d)",
                font=th.MONO, weight=BOLD, font_size=34, color=th.WHITE,
            )
            given = Text(
                "a = 3      b = 2      c = 4      d = 1",
                font=th.MONO, font_size=22, color=th.MUTED,
            )
            given.next_to(eq, DOWN, buff=0.16)
            hero = VGroup(eq, given).move_to(UP * 3.15)
            w.show(hero, run_time=0.45)
            w.say(L_KNOW, already=0.45)

            state = self._build_machine(w)
            self._run_adders(w, state)
            self._energy(w, state)
            self._wire_versus_register(w, state)
            self._ordered_versus_frozen(w, state)
            self._doorbell(w, state)
            self._python_checks(w, state)

            keepers = VGroup(hero, state["cpu"], state["graph"])
            if state["long_wire"] is not None:
                keepers.add(state["long_wire"])
            if state["b_box"] is not None:
                keepers.add(state["b_box"], state["b_num"])
            self.reset_camera(run_time=0.45)
            self.focus_on(keepers, buffer_factor=1.4, run_time=0.65)
            w.say(L_CLOSE, already=1.1)
            self.reset_camera(run_time=0.4)

    def _swap(self, w, old, new, run_time=0.3):
        new.move_to(old)
        self.play(FadeOut(old), FadeIn(new), run_time=run_time)
        if old in w.cast:
            w.cast.remove(old)
        w.keep(new)
        return new

    def _cpu(self):
        lines = VGroup(
            _code_line("t1 = a + b", True),
            _code_line("t2 = c + d", False),
            _code_line("y  = t1 * t2", False),
        ).arrange(DOWN, buff=0.14)
        pc = Triangle(color=th.AMBER_LIGHT, fill_opacity=1).scale(0.11).rotate(-PI / 2)
        pc.next_to(lines[0], LEFT, buff=0.14)
        return VGroup(lines, pc)

    def _replace_symbol(self, node, glyph, run_time=0.32):
        sym = node[1]
        node.remove(sym)
        self.add(sym)
        glyph.move_to(node[0])
        self.play(FadeOut(sym), FadeIn(glyph), run_time=run_time)
        self.remove(sym)
        node.add(glyph)
        return glyph

    def _build_machine(self, w):
        cpu = self._cpu()
        cpu.move_to(DOWN * 0.05)
        opened = w.show(cpu, run_time=0.35)

        add1 = _op("+", th.CYAN)
        add2 = _op("+", th.AMBER)
        mul = _op("×", th.GREEN)
        add1.move_to(RIGHT * 2.0 + UP * 0.95)
        add2.move_to(RIGHT * 4.3 + UP * 0.95)
        mul.move_to(RIGHT * 3.15 + DOWN * 0.75)
        left_w = Arrow(
            add1.get_bottom(), mul.get_top() + LEFT * 0.22,
            buff=0.06, color=th.CYAN, stroke_width=2.4,
        )
        right_w = Arrow(
            add2.get_bottom(), mul.get_top() + RIGHT * 0.22,
            buff=0.06, color=th.AMBER, stroke_width=2.4,
        )
        short_cap = Text("0.2 pJ", font=th.MONO, font_size=16, color=th.GREEN)
        short_cap.next_to(left_w, LEFT, buff=0.08)
        short_cap.set_opacity(0)
        graph = VGroup(add1, add2, mul, left_w, right_w, short_cap)

        self.play(
            cpu.animate.scale(0.82).move_to(LEFT * 3.85 + DOWN * 0.05),
            FadeIn(graph),
            run_time=1.1,
        )
        w.keep(graph)
        spent = opened + 1.1
        w.say(L_CPU, already=spent)
        w.ask("Where are the other two?", target=cpu[0][2], hold=1.2)

        return {
            "cpu": cpu,
            "add1": add1,
            "add2": add2,
            "mul": mul,
            "left_w": left_w,
            "right_w": right_w,
            "short_cap": short_cap,
            "graph": graph,
            "five_l": None,
            "five_r": None,
            "product": None,
            "long_wire": None,
            "long_cap": None,
            "reg": None,
            "d_box": None,
            "q_box": None,
            "d_txt": None,
            "q_txt": None,
            "a_box": None,
            "b_box": None,
            "c_box": None,
            "a_num": None,
            "b_num": None,
            "c_num": None,
            "bell_num": None,
            "banks": None,
        }

    def _run_adders(self, w, state):
        add1, add2, mul = state["add1"], state["add2"], state["mul"]
        left_in = _expr_pair("3", "2", th.CYAN_LIGHT).next_to(add1, UP, buff=0.14)
        w.show(left_in, run_time=0.25)
        self.focus_on(add1, buffer_factor=3.4, run_time=0.55)
        hold = max(0.2, _line_dur(L_LEFT) - 0.25 - 0.55 - 0.55)
        self.wait(hold)
        self.play(FadeOut(left_in), run_time=0.2)
        if left_in in w.cast:
            w.cast.remove(left_in)
        five_l = Text("5", font=th.MONO, weight=BOLD, font_size=28, color=th.CYAN_LIGHT)
        self._replace_symbol(add1, five_l, run_time=0.35)
        w.keep(five_l)
        state["five_l"] = five_l
        self.reset_camera(run_time=0.35)

        right_in = _expr_pair("4", "1", th.AMBER_LIGHT).next_to(add2, UP, buff=0.14)
        w.show(right_in, run_time=0.25)
        self.focus_on(add2, buffer_factor=3.4, run_time=0.55)
        hold = max(0.2, _line_dur(L_RIGHT) - 0.25 - 0.55 - 0.55)
        self.wait(hold)
        self.play(FadeOut(right_in), run_time=0.2)
        if right_in in w.cast:
            w.cast.remove(right_in)
        five_r = Text("5", font=th.MONO, weight=BOLD, font_size=28, color=th.AMBER_LIGHT)
        self._replace_symbol(add2, five_r, run_time=0.35)
        w.keep(five_r)
        state["five_r"] = five_r
        self.reset_camera(run_time=0.35)

        ride_l = five_l.copy()
        ride_r = five_r.copy()
        self.add(ride_l, ride_r)
        self.focus_on(mul, buffer_factor=3.6, run_time=0.5)
        into_dur = _line_dur(L_INTO)
        ride_time = min(4.5, into_dur * 0.45)
        self.play(
            ride_l.animate.move_to(mul.get_top() + LEFT * 0.32 + UP * 0.02),
            ride_r.animate.move_to(mul.get_top() + RIGHT * 0.32 + UP * 0.02),
            run_time=ride_time,
        )
        hidden = max(0.8, into_dur - 0.5 - ride_time)
        self.wait(hidden)
        product = Text("25", font=th.MONO, weight=BOLD, font_size=26, color=th.GREEN_LIGHT)
        product.move_to(mul[0])
        mul_sym = mul[1]
        mul.remove(mul_sym)
        self.add(mul_sym)
        self.play(
            FadeOut(ride_l), FadeOut(ride_r), FadeOut(mul_sym), FadeIn(product),
            mul[0].animate.set_stroke(color=th.WHITE, width=4.5),
            run_time=0.45,
        )
        self.remove(ride_l, ride_r, mul_sym)
        mul.add(product)
        w.keep(product)
        state["product"] = product
        _mark(self, "product_while_cpu_on_line1")

        # Pull back so the CPU on line 1 and the product share the frame for L_LIVE.
        self.reset_camera(run_time=0.45)
        live_dur = _line_dur(L_LIVE)
        flash = min(1.2, live_dur * 0.25)
        self.play(
            Indicate(state["cpu"][0][0], color=th.AMBER_LIGHT, scale_factor=1.04),
            run_time=flash,
        )
        w.say(L_LIVE, already=0.45 + 0.45 + flash)
        w.name("no program counter", state["graph"], direction=DOWN)

    def _energy(self, w, state):
        mul = state["mul"]
        left_w, right_w = state["left_w"], state["right_w"]
        short_cap = state["short_cap"]
        long_start = mul.get_bottom() + DOWN * 0.05
        long_end = long_start + DOWN * 1.55 + LEFT * 0.2
        long_wire = Line(long_start, long_end, color=th.AMBER, stroke_width=4.5)
        long_cap = Text("200 pJ", font=th.MONO, font_size=18, color=th.AMBER_LIGHT)
        long_cap.next_to(long_wire, RIGHT, buff=0.12)
        rider = Dot(radius=0.11, color=th.WHITE).move_to(long_start)
        mem = Text("mem", font=th.MONO, font_size=16, color=th.MUTED).next_to(
            long_end, DOWN, buff=0.1,
        )

        wire_dur = _line_dur(L_WIRE)
        self.play(
            FadeIn(long_wire), FadeIn(long_cap), FadeIn(rider), FadeIn(mem),
            short_cap.animate.set_opacity(1),
            run_time=0.55,
        )
        w.keep(long_wire, long_cap, rider, mem)
        state["long_wire"] = long_wire
        state["long_cap"] = long_cap
        self.play(
            ShowPassingFlash(left_w.copy().set_color(th.WHITE).set_stroke(width=8), time_width=0.4),
            ShowPassingFlash(right_w.copy().set_color(th.WHITE).set_stroke(width=8), time_width=0.4),
            run_time=1.1,
        )
        ride = min(6.0, max(2.0, wire_dur - 1.65))
        self.play(rider.animate.move_to(long_end), run_time=ride)
        w.say(L_WIRE, already=0.55 + 1.1 + ride)
        w.name("the wire, not the math", long_wire, direction=LEFT)

    def _wire_versus_register(self, w, state):
        src_box, src = _plain_bit("0", th.CYAN, LEFT * 0.35 + UP * 1.35)
        dst_box, dst = _plain_bit("0", th.GREEN, RIGHT * 1.35 + UP * 1.35)
        link = Line(src_box.get_right(), dst_box.get_left(), color=th.CYAN_LIGHT, stroke_width=3)
        reg = RoundedRectangle(
            corner_radius=0.12, width=2.9, height=1.55,
            stroke_color=th.CYAN, stroke_width=2.4,
            fill_color="#081528", fill_opacity=0.96,
        )
        reg.move_to(state["long_wire"].get_end() + DOWN * 0.15 + RIGHT * 2.4)
        d_box, d_txt = _plain_bit("0", th.CYAN, reg.get_center() + LEFT * 0.55)
        q_box, q_txt = _plain_bit("0", th.GREEN, reg.get_center() + RIGHT * 0.55)
        d_cap = Text("D", font=th.MONO, font_size=16, color=th.CYAN).next_to(d_box, UP, buff=0.08)
        q_cap = Text("Q", font=th.MONO, font_size=16, color=th.GREEN).next_to(q_box, UP, buff=0.08)

        self.play(
            state["graph"].animate.scale(0.78).shift(UP * 0.35 + LEFT * 0.35),
            state["cpu"].animate.scale(0.9).shift(UP * 0.25),
            FadeIn(src_box), FadeIn(src), FadeIn(dst_box), FadeIn(dst), FadeIn(link),
            FadeIn(reg), FadeIn(d_box), FadeIn(d_txt), FadeIn(q_box), FadeIn(q_txt),
            FadeIn(d_cap), FadeIn(q_cap),
            run_time=0.7,
        )
        w.keep(src_box, src, dst_box, dst, link, reg, d_box, d_txt, q_box, q_txt, d_cap, q_cap)
        state["reg"] = reg
        state["d_box"], state["q_box"] = d_box, q_box
        state["d_txt"], state["q_txt"] = d_txt, q_txt
        state["src"] = src
        state["dst"] = dst

        one_src = Text("1", font=th.MONO, weight=BOLD, font_size=28, color=th.CYAN)
        one_dst = Text("1", font=th.MONO, weight=BOLD, font_size=28, color=th.GREEN)
        src = self._swap(w, src, one_src, run_time=0.35)
        dst = self._swap(w, dst, one_dst, run_time=0.35)
        zero_src = Text("0", font=th.MONO, weight=BOLD, font_size=28, color=th.CYAN)
        zero_dst = Text("0", font=th.MONO, weight=BOLD, font_size=28, color=th.GREEN)
        hold = max(0.4, _line_dur(L_COMB) - 0.7 - 0.7 - 0.7)
        self.wait(hold * 0.55)
        src = self._swap(w, src, zero_src, run_time=0.35)
        dst = self._swap(w, dst, zero_dst, run_time=0.35)
        state["src"], state["dst"] = src, dst
        w.say(L_COMB, already=0.7 + 0.7 + hold * 0.55 + 0.7)

        timing, parts = self._timeline()
        timing.scale(0.92).shift(DOWN * 0.15)
        parts["window"].scale(0.92).shift(DOWN * 0.15)
        w.show(timing, parts["window"], run_time=0.35)
        one_d = Text("1", font=th.MONO, weight=BOLD, font_size=28, color=th.CYAN)
        d_txt = self._swap(w, d_txt, one_d, run_time=0.3)
        state["d_txt"] = d_txt
        tick_line = parts["rise"]
        self.play(tick_line.animate.set_color(th.WHITE).set_stroke(width=5), run_time=0.25)
        one_q = Text("1", font=th.MONO, weight=BOLD, font_size=28, color=th.GREEN)
        q_txt = self._swap(w, q_txt, one_q, run_time=0.3)
        state["q_txt"] = q_txt
        self.play(tick_line.animate.set_color(th.AMBER).set_stroke(width=3), run_time=0.18)
        w.say(L_FLOP, already=1.38)
        self.focus_on(parts["window"], buffer_factor=4.2, run_time=0.55)
        w.say(L_WINDOW, already=0.55)
        self.reset_camera(run_time=0.35)

        slide = self._slide_edge(w, parts)
        bad = Text("X", font=th.MONO, weight=BOLD, font_size=28, color=th.RED_LIGHT)
        q_txt = self._swap(w, q_txt, bad, run_time=0.3)
        state["q_txt"] = q_txt
        self.play(
            d_box.animate.set_stroke(color=th.RED, width=3),
            q_box.animate.set_stroke(color=th.RED, width=3),
            reg.animate.set_stroke(color=th.RED, width=3.5),
            run_time=0.3,
        )
        _mark(self, "register_x")
        self.screen_shake(intensity=0.05, cycles=3, run_time=0.28)
        w.say(L_META, already=slide + 0.88)
        w.name("setup and hold", timing, direction=DOWN)

    def _timeline(self):
        x0, x1 = -3.35, 3.35
        tick_x = 1.15
        edge_x = -1.55
        y_lo, y_hi = -2.55, -2.15
        d_lo, d_hi = -3.25, -2.85
        clk_low = Line([x0, y_lo, 0], [tick_x, y_lo, 0], color=th.AMBER, stroke_width=3)
        clk_rise = Line([tick_x, y_lo, 0], [tick_x, y_hi, 0], color=th.AMBER, stroke_width=3)
        clk_high = Line([tick_x, y_hi, 0], [x1, y_hi, 0], color=th.AMBER, stroke_width=3)
        d_low = Line([x0, d_lo, 0], [edge_x, d_lo, 0], color=th.CYAN, stroke_width=3.2)
        d_rise = Line([edge_x, d_lo, 0], [edge_x, d_hi, 0], color=th.CYAN, stroke_width=3.6)
        d_high = Line([edge_x, d_hi, 0], [x1, d_hi, 0], color=th.CYAN, stroke_width=3.2)
        window = Rectangle(
            width=tick_x - edge_x, height=0.5,
            stroke_width=0, fill_color=th.AMBER, fill_opacity=0.28,
        )
        window.move_to([(edge_x + tick_x) / 2, (d_lo + d_hi) / 2, 0])
        tick_lbl = Text("tick", font=th.MONO, font_size=16, color=th.AMBER)
        tick_lbl.next_to(clk_rise, UP, buff=0.08)
        d_lbl = Text("D", font=th.MONO, font_size=16, color=th.CYAN)
        d_lbl.next_to(d_rise, DOWN, buff=0.08)
        group = VGroup(
            clk_low, clk_rise, clk_high, d_low, d_rise, d_high, tick_lbl, d_lbl,
        )
        parts = {
            "window": window,
            "rise": clk_rise,
            "d_low": d_low,
            "d_rise": d_rise,
            "d_high": d_high,
            "d_lbl": d_lbl,
            "x0": x0,
            "x1": x1,
            "tick_x": tick_x,
            "d_lo": d_lo,
            "d_hi": d_hi,
        }
        return group, parts

    def _slide_edge(self, w, parts):
        x0 = parts["x0"]
        x1 = parts["x1"]
        tick_x = parts["tick_x"]
        d_lo = parts["d_lo"]
        d_hi = parts["d_hi"]
        window = parts["window"]
        narrow = Rectangle(
            width=0.14, height=0.5,
            stroke_width=0, fill_color=th.RED, fill_opacity=0.45,
        )
        narrow.move_to([tick_x, (d_lo + d_hi) / 2, 0])
        delta = tick_x - parts["d_rise"].get_center()[0]
        run = 1.2
        self.play(
            parts["d_low"].animate.put_start_and_end_on([x0, d_lo, 0], [tick_x, d_lo, 0]),
            parts["d_rise"].animate.put_start_and_end_on([tick_x, d_lo, 0], [tick_x, d_hi, 0]),
            parts["d_high"].animate.put_start_and_end_on([tick_x, d_hi, 0], [x1, d_hi, 0]),
            parts["d_lbl"].animate.shift(RIGHT * delta),
            FadeOut(window),
            FadeIn(narrow),
            run_time=run,
        )
        if window in w.cast:
            w.cast.remove(window)
        w.keep(narrow)
        return run

    def _ordered_versus_frozen(self, w, state):
        reg = state["reg"]
        centers = [
            reg.get_center() + LEFT * 2.45 + UP * 0.05,
            reg.get_center() + UP * 0.05,
            reg.get_center() + RIGHT * 2.45 + UP * 0.05,
        ]
        titles = [("A", "10", th.MUTED), ("B", "20", th.AMBER), ("C", "?", th.CYAN)]
        boxes, caps, nums = [], [], []
        for center, (title, val, color) in zip(centers, titles):
            box, cap, num = _box_value(title, val, color, center)
            boxes.append(box)
            caps.append(cap)
            nums.append(num)

        hide = [
            m for m in (
                state["d_box"], state["q_box"], state["d_txt"], state["q_txt"],
            ) if m is not None
        ]
        anims = [FadeIn(b) for b in boxes] + [FadeIn(c) for c in caps] + [FadeIn(n) for n in nums]
        anims.append(reg.animate.set_stroke(color=th.CYAN, width=2.0).set_opacity(0.35))
        for m in hide:
            anims.append(FadeOut(m))
        self.play(*anims, run_time=0.55)
        for m in hide:
            if m in w.cast:
                w.cast.remove(m)
        w.keep(*boxes, *caps, *nums)
        a_box, b_box, c_box = boxes
        state["a_box"], state["b_box"], state["c_box"] = a_box, b_box, c_box
        state["a_num"], state["b_num"], state["c_num"] = nums[0], nums[1], nums[2]
        b_num, c_num = nums[1], nums[2]

        flying = b_num.copy().set_color(th.RED_LIGHT)
        self.add(flying)
        landed_b = Text("10", font=th.MONO, weight=BOLD, font_size=30, color=th.WHITE)
        landed_b.move_to(b_num)
        self.play(
            FadeOut(b_num),
            FadeIn(landed_b),
            flying.animate.shift(UP * 0.55).set_opacity(0),
            run_time=0.85,
        )
        self.remove(flying)
        if b_num in w.cast:
            w.cast.remove(b_num)
        w.keep(landed_b)
        read_c = Text("10", font=th.MONO, weight=BOLD, font_size=30, color=th.RED_LIGHT)
        c_num = self._swap(w, c_num, read_c, run_time=0.45)
        _mark(self, "ordered_write_drops_20")
        w.say(L_ORDER, already=0.55 + 1.3)
        state["b_num"], state["c_num"] = landed_b, c_num

        back_b = Text("20", font=th.MONO, weight=BOLD, font_size=30, color=th.WHITE)
        blank_c = Text("?", font=th.MONO, weight=BOLD, font_size=30, color=th.WHITE)
        landed_b = self._swap(w, landed_b, back_b, run_time=0.3)
        c_num = self._swap(w, c_num, blank_c, run_time=0.3)
        ghost_a = Text("10", font=th.MONO, weight=BOLD, font_size=26, color=th.AMBER_LIGHT)
        ghost_b = Text("20", font=th.MONO, weight=BOLD, font_size=26, color=th.CYAN_LIGHT)
        ghost_a.next_to(a_box, UP, buff=0.12)
        ghost_b.next_to(b_box, UP, buff=0.12)
        w.show(ghost_a, ghost_b, run_time=0.25)
        self.play(
            ghost_a.animate.move_to(landed_b),
            ghost_b.animate.move_to(c_num),
            FadeOut(landed_b),
            FadeOut(c_num),
            run_time=0.9,
        )
        if landed_b in w.cast:
            w.cast.remove(landed_b)
        if c_num in w.cast:
            w.cast.remove(c_num)
        self.play(
            ghost_a.animate.set_color(th.WHITE),
            ghost_b.animate.set_color(th.GREEN_LIGHT),
            run_time=0.2,
        )
        w.say(L_FREEZE, already=1.95)
        w.name("<=  keeps the old value", b_box, direction=DOWN)
        state["b_num"], state["c_num"] = ghost_a, ghost_b

        four = Text("4", font=th.MONO, weight=BOLD, font_size=30, color=th.WHITE)
        seven = Text("7", font=th.MONO, weight=BOLD, font_size=30, color=th.WHITE)
        blank = Text("?", font=th.MONO, weight=BOLD, font_size=30, color=th.WHITE)
        a_num = self._swap(w, state["a_num"], four, run_time=0.25)
        b_num = self._swap(w, ghost_a, seven, run_time=0.25)
        c_num = self._swap(w, ghost_b, blank, run_time=0.25)
        state["a_num"], state["b_num"], state["c_num"] = a_num, b_num, c_num
        w.say(L_PREDICT, already=0.75)
        w.ask("What does C receive?", target=c_box, hold=1.2, direction=UP)

        hold_a = Text("4", font=th.MONO, weight=BOLD, font_size=26, color=th.AMBER_LIGHT)
        hold_b = Text("7", font=th.MONO, weight=BOLD, font_size=26, color=th.CYAN_LIGHT)
        hold_a.next_to(a_box, UP, buff=0.12)
        hold_b.next_to(b_box, UP, buff=0.12)
        w.show(hold_a, hold_b, run_time=0.25)
        self.play(
            hold_a.animate.move_to(b_num),
            hold_b.animate.move_to(c_num),
            FadeOut(b_num),
            FadeOut(c_num),
            run_time=0.85,
        )
        if b_num in w.cast:
            w.cast.remove(b_num)
        if c_num in w.cast:
            w.cast.remove(c_num)
        self.play(
            hold_a.animate.set_color(th.WHITE),
            hold_b.animate.set_color(th.GREEN_LIGHT),
            run_time=0.2,
        )
        w.keep(hold_a, hold_b)
        state["b_num"], state["c_num"] = hold_a, hold_b
        residue = Text("kept", font=th.MONO, font_size=16, color=th.MUTED)
        residue.next_to(c_box, DOWN, buff=0.1)
        w.show(residue, run_time=0.2)
        w.say(L_SECOND, already=1.5)

    def _doorbell(self, w, state):
        cpu = state["cpu"]
        bell_box = state["b_box"]
        one = Text("1", font=th.MONO, weight=BOLD, font_size=30, color=th.GREEN_LIGHT)
        self.play(
            cpu.animate.set_opacity(1).shift(RIGHT * 0.15),
            Indicate(bell_box, color=th.CYAN_LIGHT, scale_factor=1.05),
            run_time=0.45,
        )
        bell_num = self._swap(w, state["b_num"], one, run_time=0.4)
        state["bell_num"] = bell_num
        state["b_num"] = bell_num
        self.play(cpu.animate.set_opacity(0.28).shift(LEFT * 0.85), run_time=0.55)
        w.say(L_KNOCK, already=1.4)
        w.name("doorbell", bell_box, direction=DOWN)

        bank_a = RoundedRectangle(
            corner_radius=0.1, width=3.4, height=1.25,
            stroke_color=th.CYAN, stroke_width=2.2, fill_color="#071422", fill_opacity=0.96,
        )
        bank_b = RoundedRectangle(
            corner_radius=0.1, width=3.4, height=1.25,
            stroke_color=th.GREEN, stroke_width=2.2, fill_color="#071b11", fill_opacity=0.96,
        )
        bank_a.move_to(LEFT * 2.3 + DOWN * 2.55)
        bank_b.move_to(RIGHT * 2.3 + DOWN * 2.55)
        busy = VGroup()
        for i in range(4):
            sq = RoundedRectangle(
                corner_radius=0.04, width=0.4, height=0.4,
                stroke_color=th.GREEN_LIGHT, stroke_width=1.6,
                fill_color=th.GREEN, fill_opacity=0.85,
            )
            sq.move_to(bank_b.get_center() + RIGHT * (i - 1.5) * 0.55)
            busy.add(sq)
        bus = Line(bell_box.get_bottom(), bank_a.get_top() + UP * 0.05, color=th.CYAN, stroke_width=2.2)
        w.show(bank_a, bank_b, busy, bus, run_time=0.35)
        state["banks"] = VGroup(bank_a, bank_b, busy, bus)

        bank_dur = _line_dur(L_BANKS)
        step = max(0.55, (bank_dur - 0.35) / 4.2)
        for i, digit in enumerate("1234"):
            glyph = Text(digit, font=th.MONO, weight=BOLD, font_size=28, color=th.CYAN_LIGHT)
            glyph.move_to(bank_a.get_center() + RIGHT * (i - 1.5) * 0.55)
            self.play(
                FadeIn(glyph, shift=UP * 0.06),
                bank_b.animate.set_stroke(color=th.WHITE, width=4),
                run_time=step * 0.7,
            )
            self.play(bank_b.animate.set_stroke(color=th.GREEN, width=2.2), run_time=step * 0.3)
            w.keep(glyph)
        w.say(L_BANKS, already=0.35 + step * 4)
        w.name("ping-pong", bank_b, direction=DOWN)

    def _python_checks(self, w, state):
        add1 = state["add1"]
        # Dim the side cast so the original left adder is the only active machine.
        dim = []
        if state["banks"] is not None:
            dim.append(state["banks"].animate.set_opacity(0.28))
        for key in ("src", "dst"):
            if state.get(key) is not None:
                dim.append(state[key].animate.set_opacity(0.2))
        for key in ("a_box", "c_box", "a_num", "c_num"):
            if state.get(key) is not None:
                dim.append(state[key].animate.set_opacity(0.35))
        if dim:
            self.play(*dim, run_time=0.3)
        # Give the adder a clear pad above for the stimulus chips.
        self.play(state["graph"].animate.shift(DOWN * 0.15), run_time=0.25)

        five = Text("5", font=th.MONO, weight=BOLD, font_size=28, color=th.CYAN_LIGHT)
        chip = _expr_pair("3", "2", th.CYAN_LIGHT).next_to(add1, UP, buff=0.12)
        w.show(chip, run_time=0.2)
        self.focus_on(add1, buffer_factor=3.2, run_time=0.45)
        self.play(add1[0].animate.set_stroke(color=th.WHITE, width=4.5), run_time=0.2)
        current = state["five_l"]
        if current is not None and current in self.mobjects:
            five = self._swap(w, current, five, run_time=0.3)
        else:
            five = self._replace_symbol(add1, five, run_time=0.3)
            w.keep(five)
        state["five_l"] = five
        self.play(
            FadeOut(chip),
            add1[0].animate.set_stroke(color=th.CYAN, width=2.6),
            run_time=0.25,
        )
        if chip in w.cast:
            w.cast.remove(chip)
        w.say(L_PY1, already=1.4)
        self.reset_camera(run_time=0.3)

        chip2 = _expr_pair("1", "1", th.CYAN_LIGHT).next_to(add1, UP, buff=0.12)
        two = Text("2", font=th.MONO, weight=BOLD, font_size=28, color=th.GREEN_LIGHT)
        w.show(chip2, run_time=0.2)
        self.focus_on(add1, buffer_factor=3.2, run_time=0.4)
        hold = max(0.5, _line_dur(L_PY2) - 1.2)
        self.wait(hold * 0.5)
        five = self._swap(w, five, two, run_time=0.35)
        state["five_l"] = five
        self.play(FadeOut(chip2), run_time=0.2)
        if chip2 in w.cast:
            w.cast.remove(chip2)
        w.say(L_PY2, already=0.95 + hold * 0.5)
        self.reset_camera(run_time=0.3)

        chip3 = Text("8 + -1", font=th.MONO, font_size=24, color=th.WHITE)
        chip3.next_to(add1, UP, buff=0.12)
        seven = Text("7", font=th.MONO, weight=BOLD, font_size=28, color=th.GREEN_LIGHT)
        bits = VGroup(
            _nibble_row("8", "1000", th.AMBER_LIGHT),
            _nibble_row("-1", "1111", th.CYAN_LIGHT),
            _nibble_row("7", "0111", th.GREEN_LIGHT),
        ).arrange(DOWN, buff=0.1, aligned_edge=RIGHT)
        bits.next_to(add1, RIGHT, buff=0.35)
        if bits.get_right()[0] > 6.6:
            bits.shift(LEFT * (bits.get_right()[0] - 6.6))
        w.show(chip3, bits, run_time=0.35)
        self.focus_on(VGroup(add1, bits), buffer_factor=2.8, run_time=0.5)
        hold = max(0.8, _line_dur(L_PY3) - 1.4)
        self.wait(hold * 0.55)
        five = self._swap(w, five, seven, run_time=0.35)
        state["five_l"] = five
        self.play(FadeOut(chip3), bits.animate.set_opacity(0.55), run_time=0.25)
        if chip3 in w.cast:
            w.cast.remove(chip3)
        w.say(L_PY3, already=1.2 + hold * 0.55)
        self.reset_camera(run_time=0.35)
