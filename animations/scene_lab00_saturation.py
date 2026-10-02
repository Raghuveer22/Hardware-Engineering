"""
Lab 00: Signed Adder & Saturation Arithmetic

Deep-dive structure:
1.  The bug: +100 + +50 should be +150, but 8-bit wrap-around yields -106.
    A real 8-bit adder bit-row is shown flipping as the carry corrupts the sign.
2.  The 2's-complement number wheel: a pointer physically rotates past +127
    and wraps to -106 — the "overflow cliff".
3.  The fix: saturation. The same wheel now has a clamp that stops the pointer
    at +127. The overflow-detection formula is animated on the adder.
4.  RTL recap: rtl/adder.sv — always_comb, overflow flag, saturation mux.
"""

from manim import *
import theme as th


class Lab00SaturationIntro(Scene):
    def construct(self):
        th.set_dark(self.camera)

        # =================================================================
        # ACT 1 — THE BUG: WRAP-AROUND CORRUPTION
        # =================================================================
        hdr, _, _ = th.header("LAB 00", "The 8-Bit Wrap-Around Bug")
        self.play(FadeIn(hdr, shift=DOWN * 0.3), run_time=0.7)

        # Math expectation row.
        math_card = th.card(9.0, 1.9, stroke=th.BORDER, radius=0.18)
        math_card.move_to(UP * 0.75)
        op1 = Text("+100", font=th.MONO, weight=BOLD, font_size=34, color=th.CYAN)
        plus = Text("+", font=th.MONO, weight=BOLD, font_size=34, color=th.TEXT)
        op2 = Text("+50", font=th.MONO, weight=BOLD, font_size=34, color=th.AMBER)
        eq = Text("=", font=th.MONO, weight=BOLD, font_size=34, color=th.TEXT)
        expect = Text("+150", font=th.MONO, weight=BOLD, font_size=36, color=th.GREEN)
        row = VGroup(op1, plus, op2, eq, expect).arrange(RIGHT, buff=0.35)
        row.move_to(math_card)
        self.play(Create(math_card), FadeIn(row), run_time=0.8)
        self.wait(0.6)

        # Reveal the signed 8-bit range.
        rng = Text("8-bit signed range: [-128, +127]",
                   font=th.MONO, font_size=20, color=th.MUTED)
        rng.next_to(math_card, DOWN, buff=0.3)
        self.play(FadeIn(rng), run_time=0.5)
        self.wait(0.7)

        # Cross out +150 and slam in -106.
        strike = Line(expect.get_left() + LEFT * 0.1,
                      expect.get_right() + RIGHT * 0.1,
                      color=th.RED, stroke_width=5)
        self.play(Create(strike), run_time=0.35)
        bug = Text("-106", font=th.MONO, weight=BOLD, font_size=40, color=th.RED)
        bug.move_to(expect)
        self.play(Transform(expect, bug), FadeOut(strike), run_time=0.5)

        banner = Text("SIGN BIT CORRUPTED!", font=th.SANS, weight=BOLD,
                      font_size=26, color=th.RED_LIGHT)
        banner.next_to(rng, DOWN, buff=0.4)
        self.play(FadeIn(banner, shift=UP * 0.2), run_time=0.5)
        self.wait(0.9)

        # Animate the bit-level cause: an 8-bit adder with carry rippling
        # into the sign bit. Show both operands and the (wrong) result.
        self.play(FadeOut(banner), FadeOut(rng), FadeOut(math_card),
                  FadeOut(row), run_time=0.5)

        # =================================================================
        # ACT 1b — WHY? BIT-LEVEL VIEW OF THE OVERFLOW
        # =================================================================
        sub = Text("Why? Carry ripples into the sign bit.",
                   font=th.SANS, font_size=22, color=th.MUTED)
        sub.next_to(hdr, DOWN, buff=0.3)
        self.play(FadeIn(sub), run_time=0.4)

        # Operand A = +100 -> 01100100 ; B = +50 -> 00110010
        a_bits = th.bit_row("01100100")
        b_bits = th.bit_row("00110010")
        s_bits = th.bit_row("10010110")  # -106 in 8-bit
        for br, c in [(a_bits, th.CYAN), (b_bits, th.AMBER), (s_bits, th.RED)]:
            for cell in br:
                cell[0].set_stroke(c, width=1.5)
                cell[1].set_color(c)

        a_lbl = Text("A = +100", font=th.MONO, font_size=17, color=th.CYAN)
        b_lbl = Text("B = +50", font=th.MONO, font_size=17, color=th.AMBER)
        s_lbl = Text("SUM", font=th.MONO, font_size=17, color=th.RED)

        a_grp = VGroup(a_lbl, a_bits).arrange(RIGHT, buff=0.4)
        b_grp = VGroup(b_lbl, b_bits).arrange(RIGHT, buff=0.4)
        s_grp = VGroup(s_lbl, s_bits).arrange(RIGHT, buff=0.4)
        stack = VGroup(a_grp, b_grp).arrange(DOWN, buff=0.4)
        s_grp.next_to(stack, DOWN, buff=0.7)

        # Align columns: center the bit rows.
        group = VGroup(a_grp, b_grp, s_grp).move_to(DOWN * 0.8)
        self.play(FadeIn(a_grp, b_grp), run_time=0.6)
        self.play(FadeIn(s_grp), run_time=0.5)

        # Highlight the sign bit corruption: MSB is 1 -> negative!
        msb = s_bits[0]
        box = SurroundingRectangle(msb, color=th.RED, buff=0.06, stroke_width=3)
        self.play(Create(box), run_time=0.4)
        note = Text("MSB = 1  →  interpreted as NEGATIVE",
                    font=th.MONO, font_size=17, color=th.RED_LIGHT)
        note.next_to(group, DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.4)
        self.wait(1.2)

        self.play(FadeOut(hdr), FadeOut(sub), FadeOut(group), FadeOut(box),
                  FadeOut(note), run_time=0.5)

        # =================================================================
        # ACT 2 — THE NUMBER WHEEL
        # =================================================================
        w_hdr, _, _ = th.header("LAB 00", "The 2's Complement Number Wheel")
        self.play(FadeIn(w_hdr, shift=DOWN * 0.3), run_time=0.7)

        center = DOWN * 0.4
        radius = 2.3
        outer = Circle(radius=radius, color=th.BORDER, stroke_width=4)
        outer.move_to(center)

        # The overflow cliff between +127 and -128 at the bottom.
        cliff_start = center + DOWN * radius
        cliff = Line(cliff_start, cliff_start + DOWN * 1.1, color=th.RED,
                     stroke_width=5)
        cliff_lbl = Text("OVERFLOW CLIFF", font=th.SANS, weight=BOLD,
                         font_size=16, color=th.RED)
        cliff_lbl.next_to(cliff, DOWN, buff=0.12)

        # Tick labels at cardinal points.
        lab_0 = Text("0", font=th.MONO, font_size=17, color=th.CYAN)
        lab_0.next_to(center + UP * radius, UP, buff=0.1)
        lab_pos = Text("+127", font=th.MONO, font_size=17, color=th.GREEN)
        lab_pos.next_to(center + DOWN * radius * 0.85 + RIGHT * radius * 0.6,
                        RIGHT, buff=0.1)
        lab_neg = Text("-128", font=th.MONO, font_size=17, color=th.RED)
        lab_neg.next_to(center + DOWN * radius * 0.85 + LEFT * radius * 0.6,
                        LEFT, buff=0.1)

        self.play(Create(outer), Create(cliff), FadeIn(cliff_lbl),
                  FadeIn(lab_0), FadeIn(lab_pos), FadeIn(lab_neg), run_time=0.9)

        # Pointer.
        pointer = Arrow(start=center, end=center + UP * radius * 0.82,
                        buff=0, color=th.AMBER, stroke_width=6, max_tip_length_to_length_ratio=0.2)
        readout = Text("+100", font=th.MONO, weight=BOLD, font_size=24,
                       color=th.AMBER).move_to(center)
        self.play(GrowArrow(pointer), FadeIn(readout), run_time=0.6)

        # +100 is at angle -0.75π from the top; +50 adds -0.45π more.
        self.play(Rotate(pointer, angle=-PI * 0.75, about_point=center),
                  run_time=1.2)
        self.wait(0.4)

        # Adding +50: normal rotation would pass the cliff. We rotate through
        # it so the viewer sees the pointer sweep into -106 territory.
        self.play(Rotate(pointer, angle=-PI * 0.45, about_point=center),
                  Transform(readout, Text("-106", font=th.MONO, weight=BOLD,
                                          font_size=24, color=th.RED).move_to(center)),
                  pointer.animate.set_color(th.RED), run_time=1.6)
        self.wait(0.8)

        # Wrap note.
        wrap = Text("No barrier: the number wraps around.",
                    font=th.SANS, font_size=20, color=th.MUTED)
        wrap.next_to(cliff_lbl, DOWN, buff=0.35)
        self.play(FadeIn(wrap), run_time=0.5)
        self.wait(1.0)
        self.play(FadeOut(wrap), run_time=0.3)

        # =================================================================
        # ACT 3 — SATURATION: THE CLAMP
        # =================================================================
        # Rewind the pointer back to +100 to replay with saturation.
        self.play(Rotate(pointer, angle=+PI * 0.45, about_point=center),
                  Transform(readout, Text("+100", font=th.MONO, weight=BOLD,
                                          font_size=24, color=th.AMBER).move_to(center)),
                  pointer.animate.set_color(th.AMBER), run_time=1.2)
        self.wait(0.3)

        clamp = th.card(2.6, 0.75, stroke=th.GREEN, radius=0.12, fill=th.GREEN_DARK)
        clamp.next_to(cliff, DOWN, buff=0.1)
        clamp_t = Text("CLAMP", font=th.SANS, weight=BOLD, font_size=18,
                       color=th.GREEN_LIGHT).move_to(clamp)
        self.play(Create(clamp), Write(clamp_t), run_time=0.5)

        # Pointer now tries to add +50 but gets stopped at +127.
        target = center + DOWN * radius * 0.82 + RIGHT * radius * 0.25
        self.play(pointer.animate.put_start_and_end_on(center, target),
                  Transform(readout, Text("+127", font=th.MONO, weight=BOLD,
                                          font_size=26, color=th.GREEN).move_to(center)),
                  run_time=1.0)
        self.wait(0.3)

        sat_note = Text("Saturation clamps to MAX_POS = +127",
                        font=th.SANS, weight=BOLD, font_size=22, color=th.GREEN_LIGHT)
        sat_note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(sat_note, shift=UP * 0.2), run_time=0.6)
        self.wait(1.2)

        self.play(FadeOut(w_hdr), FadeOut(outer), FadeOut(cliff), FadeOut(cliff_lbl),
                  FadeOut(lab_0), FadeOut(lab_pos), FadeOut(lab_neg),
                  FadeOut(pointer), FadeOut(readout), FadeOut(clamp), FadeOut(clamp_t),
                  FadeOut(sat_note), run_time=0.5)

        # =================================================================
        # ACT 4 — THE OVERFLOW DETECTOR + SATURATION MUX
        # =================================================================
        f_hdr, _, _ = th.header("LAB 00", "How the Hardware Detects Overflow")
        self.play(FadeIn(f_hdr, shift=DOWN * 0.3), run_time=0.7)

        formula = Text(
            "overflow = (A[7] == B[7])  &  (SUM[7] != A[7])",
            font=th.MONO, weight=BOLD, font_size=22, color=th.AMBER_LIGHT,
        )
        formula.next_to(f_hdr, DOWN, buff=0.5)
        self.play(Write(formula), run_time=0.9)
        self.wait(0.5)

        expl = th.bullets(
            ["Both inputs share the same sign bit",
             "But the sum's sign bit flipped",
             "→ impossible result: a positive overflow!"],
            font_size=19, buff=0.25, bullet_color=th.RED, color=th.TEXT,
        )
        expl.next_to(formula, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(FadeIn(expl, shift=UP * 0.15), run_time=0.8)
        self.wait(1.0)

        # The saturation mux: overflow selects the clamp value.
        mux_card = th.card(9.4, 2.2, stroke=th.GREEN, radius=0.16)
        mux_card.to_edge(DOWN, buff=0.5)
        mux_t = Text("Saturation Mux", font=th.SANS, weight=BOLD, font_size=20,
                     color=th.GREEN_LIGHT).next_to(mux_card.get_top(), DOWN, buff=0.25)

        in1 = Text("wrap sum  -106", font=th.MONO, font_size=17, color=th.RED)
        in2 = Text("clamp  +127", font=th.MONO, font_size=17, color=th.GREEN)
        sel = Text("overflow flag", font=th.MONO, font_size=16, color=th.AMBER)
        out = Text("+127", font=th.MONO, weight=BOLD, font_size=22, color=th.GREEN)

        mux_rows = VGroup(in1, in2).arrange(RIGHT, buff=1.2)
        mux_rows.move_to(mux_card.get_center() + UP * 0.25)
        sel.next_to(mux_rows, DOWN, buff=0.35)
        out.next_to(mux_card, RIGHT, buff=0.7)

        self.play(Create(mux_card), FadeIn(mux_t), FadeIn(mux_rows), FadeIn(sel),
                  run_time=0.7)
        # Select clamp.
        self.play(FadeIn(out), run_time=0.3)
        arrow_out = Arrow(mux_card.get_right(), out.get_left(), buff=0.05,
                          color=th.GREEN)
        self.play(Create(arrow_out), run_time=0.4)
        self.wait(1.0)

        self.play(FadeOut(f_hdr), FadeOut(formula), FadeOut(expl), FadeOut(mux_card),
                  FadeOut(mux_t), FadeOut(mux_rows), FadeOut(sel), FadeOut(out),
                  FadeOut(arrow_out), run_time=0.5)

        # =================================================================
        # ACT 5 — RECAP
        # =================================================================
        card = th.card(10.0, 3.8, stroke=th.CYAN, radius=0.22)
        t = Text("Lab 00 Takeaway", font=th.SANS, weight=BOLD, font_size=26,
                 color=th.CYAN)
        t.next_to(card.get_top(), DOWN, buff=0.35)
        pts = th.bullets(
            ["Plain addition wraps: +100 + +50 → -106 (sign corrupted)",
             "Overflow detector: A[7]==B[7] & SUM[7]!=A[7]",
             "Saturation mux clamps to +127 / -128 (rtl/adder.sv)",
             "Next: Lab 01 — The INT8 Multiplier & O(N²) Silicon"],
            font_size=19, buff=0.3, bullet_color=th.GREEN, color=th.TEXT,
        )
        pts.next_to(t, DOWN, buff=0.4, aligned_edge=LEFT)
        pts.move_to(card.get_center() + DOWN * 0.2)
        self.play(Create(card), Write(t), FadeIn(pts, shift=UP * 0.2), run_time=1.1)
        self.wait(2.4)
