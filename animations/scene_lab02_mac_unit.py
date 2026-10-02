"""
Lab 02: Multiply-Accumulate (MAC) Unit & Accumulator Headroom

Deep-dive structure:
1.  The dot product: sum_out = sum_in + (a × b) — the backbone of AI compute.
2.  Accumulator headroom math: K=4096 terms → 16 + 12 = 28 bits → use 32.
3.  The zero-extension disaster: -5 widened with zeros becomes +65,531.
    Animated bit-by-bit.
4.  Sign-extension fixes it: replicate the MSB.
5.  The datapath: multiplier → sign-extender → 32-bit adder, with a packet
    flowing through, plus the RTL recap.
"""

from manim import *
import theme as th


class Lab02MACUnit(Scene):
    def construct(self):
        th.set_dark(self.camera)

        # =================================================================
        # ACT 1 — THE DOT PRODUCT
        # =================================================================
        hdr, _, _ = th.header("LAB 02", "The MAC Unit")
        self.play(FadeIn(hdr, shift=DOWN * 0.3), run_time=0.7)

        eq = Text("sum_out  =  sum_in  +  (a × b)",
                  font=th.MONO, weight=BOLD, font_size=26, color=th.GREEN_LIGHT)
        eq.next_to(hdr, DOWN, buff=0.45)
        self.play(Write(eq), run_time=0.8)

        sub = Text(
            "The fundamental building block of 99% of AI compute",
            font=th.SANS, font_size=20, color=th.MUTED,
        )
        sub.next_to(eq, DOWN, buff=0.4)
        self.play(FadeIn(sub), run_time=0.5)

        # A small animated MAC chain: a packet multiplies and accumulates.
        dot = th.packet(color=th.AMBER, radius=0.16)
        dot.next_to(eq, DOWN, buff=1.0)
        self.play(FadeIn(dot), run_time=0.3)
        self.play(dot.animate.shift(RIGHT * 4), run_time=0.8)
        self.play(dot.animate.shift(LEFT * 4), run_time=0.8)
        self.play(FadeOut(dot), run_time=0.3)
        self.wait(0.4)

        self.play(FadeOut(hdr), FadeOut(eq), FadeOut(sub), run_time=0.5)

        # =================================================================
        # ACT 2 — ACCUMULATOR HEADROOM
        # =================================================================
        a_hdr, _, _ = th.header("LAB 02", "How Wide Must the Accumulator Be?")
        self.play(FadeIn(a_hdr, shift=DOWN * 0.3), run_time=0.7)

        card = th.card(10.4, 3.0, stroke=th.BORDER, radius=0.18)
        card.move_to(UP * 0.3)

        m1 = Text("LLM hidden dimension K = 4096 terms in the dot product",
                  font=th.SANS, font_size=20, color=th.TEXT)
        m2 = Text("1 INT8 product = 16 bits (max +16,129)",
                  font=th.MONO, font_size=18, color=th.CYAN)
        m3 = Text("bits needed = 16 + log2(4096) = 16 + 12 = 28",
                  font=th.MONO, weight=BOLD, font_size=19, color=th.AMBER_LIGHT)
        m4 = Text("→ a 32-bit accumulator overflows only after 65,536 terms",
                  font=th.SANS, weight=BOLD, font_size=18, color=th.GREEN_LIGHT)
        stack = VGroup(m1, m2, m3, m4).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        stack.move_to(card)
        self.play(Create(card), FadeIn(stack), run_time=0.9)
        self.wait(1.2)

        self.play(FadeOut(a_hdr), FadeOut(card), FadeOut(stack), run_time=0.5)

        # =================================================================
        # ACT 3 — THE ZERO-EXTENSION DISASTER
        # =================================================================
        d_hdr, _, _ = th.header("LAB 02", "The Zero-Extension Disaster")
        self.play(FadeIn(d_hdr, shift=DOWN * 0.3), run_time=0.7)

        intro = Text("Widening a 16-bit product (-5) into a 32-bit accumulator",
                     font=th.SANS, font_size=20, color=th.MUTED)
        intro.next_to(d_hdr, DOWN, buff=0.35)
        self.play(FadeIn(intro), run_time=0.5)

        # Wrong: zero-extension.
        bad = th.card(11.2, 1.9, stroke=th.RED, fill=th.RED_DARK, radius=0.16)
        bad.move_to(UP * 0.15)
        b_label = Text("ZERO-EXTEND (pad 16 zeros)", font=th.SANS, weight=BOLD,
                       font_size=17, color=th.RED_LIGHT)
        b_label.next_to(bad.get_top(), DOWN, buff=0.2)

        zeros = th.bit_row("0000000000000000", color=th.RED)
        for cell in zeros:
            cell[1].set_color(th.RED_LIGHT)
        mag = th.bit_row("1111111111111011", color=th.RED)  # -5 in 16-bit
        for cell in mag:
            cell[1].set_color(th.RED_LIGHT)
        b_row = VGroup(zeros, mag).arrange(RIGHT, buff=0.3)
        b_val = Text("→ +65,531 !", font=th.MONO, weight=BOLD, font_size=22,
                     color=th.RED)
        b_content = VGroup(b_row, b_val).arrange(RIGHT, buff=0.4).move_to(bad)
        self.play(Create(bad), FadeIn(b_label), FadeIn(b_content), run_time=0.8)
        self.wait(1.0)

        # Good: sign-extension.
        good = th.card(11.2, 1.9, stroke=th.GREEN, fill=th.GREEN_DARK, radius=0.16)
        good.next_to(bad, DOWN, buff=0.45)
        g_label = Text("SIGN-EXTEND (replicate MSB)", font=th.SANS, weight=BOLD,
                       font_size=17, color=th.GREEN_LIGHT)
        g_label.next_to(good.get_top(), DOWN, buff=0.2)

        ones = th.bit_row("1111111111111111", color=th.GREEN)
        for cell in ones:
            cell[1].set_color(th.GREEN_LIGHT)
        mag2 = th.bit_row("1111111111111011", color=th.GREEN)  # -5 preserved
        for cell in mag2:
            cell[1].set_color(th.GREEN_LIGHT)
        g_row = VGroup(ones, mag2).arrange(RIGHT, buff=0.3)
        g_val = Text("→ -5  (preserved!)", font=th.MONO, weight=BOLD, font_size=22,
                     color=th.GREEN)
        g_content = VGroup(g_row, g_val).arrange(RIGHT, buff=0.4).move_to(good)
        self.play(Create(good), FadeIn(g_label), FadeIn(g_content), run_time=0.8)
        self.wait(1.3)

        # Highlight the difference: zeros vs ones in the top 16 bits.
        for cell in zeros:
            self.play(Flash(cell, color=th.RED, line_length=0.25), run_time=0.02)
        for cell in ones:
            self.play(Flash(cell, color=th.GREEN, line_length=0.25), run_time=0.02)
        self.wait(0.5)

        self.play(FadeOut(d_hdr), FadeOut(intro), FadeOut(bad), FadeOut(b_label),
                  FadeOut(b_content), FadeOut(good), FadeOut(g_label),
                  FadeOut(g_content), run_time=0.5)

        # =================================================================
        # ACT 4 — THE DATAPATH
        # =================================================================
        p_hdr, _, _ = th.header("LAB 02", "The MAC Datapath")
        self.play(FadeIn(p_hdr, shift=DOWN * 0.3), run_time=0.7)

        mult = th.card(2.6, 1.1, stroke=th.AMBER, radius=0.14)
        mult.shift(LEFT * 3.6 + UP * 0.2)
        mult_t = Text("8×8\nMultiplier", font=th.SANS, font_size=15,
                      color=th.AMBER_LIGHT).move_to(mult)

        ext = th.card(2.6, 1.1, stroke=th.CYAN, radius=0.14)
        ext.move_to(UP * 0.2)
        ext_t = Text("Sign-Extend\n16b → 32b", font=th.SANS, font_size=15,
                     color=th.CYAN_LIGHT).move_to(ext)

        add = th.card(2.6, 1.1, stroke=th.GREEN, radius=0.14)
        add.shift(RIGHT * 3.6 + UP * 0.2)
        add_t = Text("32-bit\nAdder", font=th.SANS, font_size=15,
                     color=th.GREEN_LIGHT).move_to(add)

        a1 = Arrow(mult.get_right(), ext.get_left(), buff=0.08, color=th.AMBER)
        a2 = Arrow(ext.get_right(), add.get_left(), buff=0.08, color=th.CYAN)
        out = Arrow(add.get_right(), add.get_right() + RIGHT * 1.3, buff=0.08,
                    color=th.GREEN)
        out_l = Text("sum_out [31:0]", font=th.MONO, font_size=15, color=th.GREEN)
        out_l.next_to(out, UP, buff=0.08)

        sum_in = Arrow(add.get_top() + UP * 0.4, add.get_top(), buff=0.05,
                       color=th.GREEN)
        sum_in_l = Text("sum_in", font=th.MONO, font_size=14, color=th.GREEN)
        sum_in_l.next_to(sum_in, UP, buff=0.05)

        nodes = VGroup(mult, mult_t, ext, ext_t, add, add_t, a1, a2, out, out_l,
                       sum_in, sum_in_l)
        self.play(FadeIn(nodes), run_time=1.0)

        # Packet flowing through the pipeline.
        p = th.packet(color=th.AMBER, radius=0.16)
        p.move_to(mult.get_left() + LEFT * 0.7)
        self.play(FadeIn(p), run_time=0.25)
        self.play(p.animate.move_to(mult), run_time=0.45)
        self.play(p.animate.move_to(ext).set_color(th.CYAN), run_time=0.45)
        self.play(p.animate.move_to(add).set_color(th.GREEN), run_time=0.45)
        self.play(p.animate.move_to(out.get_end()), run_time=0.45)
        self.play(FadeOut(p), run_time=0.25)
        self.wait(0.6)

        self.play(FadeOut(p_hdr), FadeOut(nodes), run_time=0.5)

        # =================================================================
        # ACT 5 — RTL RECAP
        # =================================================================
        card = th.card(10.0, 3.9, stroke=th.GREEN, radius=0.22)
        t = Text("rtl/mac_unit.sv", font=th.SANS, weight=BOLD, font_size=26,
                 color=th.GREEN_LIGHT)
        t.next_to(card.get_top(), DOWN, buff=0.35)
        pts = th.bullets(
            ["assign mult_product = a * b",
             "Sign-extend: {{(ACC-16){MSB}}, product}",
             "assign sum_out = sum_in + extended product",
             "32-bit accumulator → zero overflow up to 65,536 terms",
             "Next: Lab 03 — The Weight-Stationary PE"],
            font_size=18, buff=0.28, bullet_color=th.GREEN, color=th.TEXT,
        )
        pts.next_to(t, DOWN, buff=0.4, aligned_edge=LEFT)
        pts.move_to(card.get_center() + DOWN * 0.15)
        self.play(Create(card), Write(t), FadeIn(pts, shift=UP * 0.2), run_time=1.1)
        self.wait(2.4)
