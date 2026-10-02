"""
Lab 03: Weight-Stationary Processing Element (PE)

Deep-dive structure:
1.  The memory wall: 0.2 pJ per MAC vs 200 pJ per DRAM byte (1000×).
2.  The PE anatomy: stationary weight register, MAC, activation (W→E) and
    partial-sum (N→S) paths — all drawn as a real block diagram.
3.  A worked clock-by-clock example: load weight, then 2 cycles of compute
    with an animated clock edge and the register values updating.
4.  RTL recap: rtl/pe.sv — 48 flip-flops, always_ff @posedge clk.
"""

from manim import *
import theme as th


class Lab03ProcessingElement(Scene):
    def construct(self):
        th.set_dark(self.camera)

        # =================================================================
        # ACT 1 — THE MEMORY WALL
        # =================================================================
        hdr, _, _ = th.header("LAB 03", "The Weight-Stationary PE")
        self.play(FadeIn(hdr, shift=DOWN * 0.3), run_time=0.7)

        # Energy comparison with animated bars.
        bar_card = th.card(10.4, 3.0, stroke=th.BORDER, radius=0.18)
        bar_card.move_to(UP * 0.2)

        bar_label = Text("Energy cost of ONE operation", font=th.SANS, weight=BOLD,
                         font_size=18, color=th.TEXT)
        bar_label.next_to(bar_card.get_top(), DOWN, buff=0.25)

        # Two bars: MAC (tiny) vs DRAM fetch (huge).
        mac_bar = Rectangle(width=0.6, height=0.15, fill_color=th.GREEN,
                            fill_opacity=1.0, stroke_width=0)
        mac_bar.next_to(bar_label, DOWN, buff=0.5, aligned_edge=LEFT)
        mac_bar.shift(RIGHT * 1.0)
        mac_lbl = Text("MAC in silicon: 0.2 pJ", font=th.MONO, font_size=17,
                       color=th.GREEN_LIGHT)
        mac_lbl.next_to(mac_bar, RIGHT, buff=0.3)

        dram_bar = Rectangle(width=0.6, height=2.4, fill_color=th.RED,
                             fill_opacity=1.0, stroke_width=0)
        dram_bar.next_to(mac_bar, RIGHT, buff=1.6, aligned_edge=DOWN)
        dram_lbl = Text("DRAM byte fetch: 200 pJ  (1000×!)",
                        font=th.MONO, font_size=17, color=th.RED_LIGHT)
        dram_lbl.next_to(dram_bar, UP, buff=0.15)

        self.play(Create(bar_card), FadeIn(bar_label), run_time=0.6)
        self.play(GrowFromEdge(mac_bar, DOWN), FadeIn(mac_lbl), run_time=0.5)
        self.play(GrowFromEdge(dram_bar, DOWN), FadeIn(dram_lbl), run_time=0.9)
        self.wait(0.7)

        fix = Text("Fix: keep weights ON-CHIP, stationary in registers",
                   font=th.SANS, weight=BOLD, font_size=20, color=th.AMBER_LIGHT)
        fix.next_to(bar_card, DOWN, buff=0.4)
        self.play(FadeIn(fix, shift=UP * 0.15), run_time=0.6)
        self.wait(0.8)

        self.play(FadeOut(hdr), FadeOut(bar_card), FadeOut(bar_label),
                  FadeOut(mac_bar), FadeOut(mac_lbl), FadeOut(dram_bar),
                  FadeOut(dram_lbl), FadeOut(fix), run_time=0.5)

        # =================================================================
        # ACT 2 — PE ANATOMY
        # =================================================================
        p_hdr, _, _ = th.header("LAB 03", "Inside the PE")
        self.play(FadeIn(p_hdr, shift=DOWN * 0.3), run_time=0.7)

        pe = th.card(5.8, 4.2, stroke=th.CYAN, stroke_w=3.0, radius=0.2)
        pe.move_to(DOWN * 0.1)

        w_box = th.card(2.5, 0.75, stroke=th.AMBER, fill=th.AMBER_DARK, radius=0.1)
        w_box.next_to(pe.get_top(), DOWN, buff=0.4)
        w_lbl = Text("weight_reg [7:0]", font=th.MONO, font_size=15,
                     color=th.AMBER_LIGHT).move_to(w_box)

        mult = Circle(radius=0.42, color=th.AMBER, stroke_width=3,
                      fill_color=th.CARD, fill_opacity=1.0)
        mult.move_to(pe.get_center() + LEFT * 0.5 + UP * 0.4)
        mult_sym = Text("×", font=th.SANS, weight=BOLD, font_size=24,
                        color=th.AMBER).move_to(mult)

        add = Circle(radius=0.42, color=th.GREEN, stroke_width=3,
                     fill_color=th.CARD, fill_opacity=1.0)
        add.move_to(pe.get_center() + LEFT * 0.5 + DOWN * 0.8)
        add_sym = Text("+", font=th.SANS, weight=BOLD, font_size=24,
                       color=th.GREEN).move_to(add)

        # Weight → multiplier.
        w_to_m = Arrow(w_box.get_bottom(), mult.get_top(), buff=0.05, color=th.AMBER)

        # Activation: West → East through a register.
        a_in = Arrow(pe.get_left() + LEFT * 1.6 + UP * 0.6,
                     pe.get_left() + UP * 0.6, buff=0, color=th.CYAN, stroke_width=5)
        a_out = Arrow(pe.get_right() + UP * 0.6,
                      pe.get_right() + RIGHT * 1.6 + UP * 0.6, buff=0, color=th.CYAN,
                      stroke_width=5)
        a_in_l = Text("a_in", font=th.MONO, font_size=15, color=th.CYAN)
        a_in_l.next_to(a_in, UP, buff=0.08)
        a_out_l = Text("a_out (1 clk delay)", font=th.MONO, font_size=13, color=th.CYAN)
        a_out_l.next_to(a_out, UP, buff=0.08)

        # Partial sum: North → South.
        s_in = Arrow(pe.get_top() + UP * 1.0 + RIGHT * 1.0,
                     pe.get_top() + RIGHT * 1.0, buff=0, color=th.GREEN, stroke_width=5)
        s_out = Arrow(pe.get_bottom() + RIGHT * 1.0,
                      pe.get_bottom() + DOWN * 1.0 + RIGHT * 1.0, buff=0,
                      color=th.GREEN, stroke_width=5)
        s_in_l = Text("sum_in", font=th.MONO, font_size=14, color=th.GREEN)
        s_in_l.next_to(s_in, RIGHT, buff=0.08)
        s_out_l = Text("sum_out (1 clk delay)", font=th.MONO, font_size=13,
                       color=th.GREEN)
        s_out_l.next_to(s_out, RIGHT, buff=0.08)

        pe_grp = VGroup(pe, w_box, w_lbl, mult, mult_sym, add, add_sym, w_to_m,
                        a_in, a_out, a_in_l, a_out_l, s_in, s_out, s_in_l, s_out_l)
        self.play(FadeIn(pe_grp), run_time=1.1)
        self.wait(0.9)

        self.play(FadeOut(p_hdr), FadeOut(pe_grp), run_time=0.5)

        # =================================================================
        # ACT 3 — WORKED CLOCK-BY-CLOCK EXAMPLE
        # =================================================================
        c_hdr, _, _ = th.header("LAB 03", "A Clocked Worked Example")
        self.play(FadeIn(c_hdr, shift=DOWN * 0.3), run_time=0.7)

        # A live table: weight, a_in, sum_in → sum_out.
        self._show_cycle_table()
        self.wait(1.0)

        self.play(FadeOut(c_hdr), FadeOut(Group(*self.mobjects)), run_time=0.6)

        # =================================================================
        # ACT 4 — RTL RECAP
        # =================================================================
        card = th.card(10.0, 3.9, stroke=th.GREEN, radius=0.22)
        t = Text("rtl/pe.sv", font=th.SANS, weight=BOLD, font_size=26,
                 color=th.GREEN_LIGHT)
        t.next_to(card.get_top(), DOWN, buff=0.35)
        pts = th.bullets(
            ["Weight stationary: loaded once, reused for every token",
             "a_out and sum_out registered → 1-clock pipeline delay",
             "48 D flip-flops per PE (8 + 8 + 32)",
             "always_ff @(posedge clk or negedge rst_n)",
             "Next: Lab 04 — The 4×4 Systolic Array"],
            font_size=18, buff=0.28, bullet_color=th.GREEN, color=th.TEXT,
        )
        pts.next_to(t, DOWN, buff=0.4, aligned_edge=LEFT)
        pts.move_to(card.get_center() + DOWN * 0.15)
        self.play(Create(card), Write(t), FadeIn(pts, shift=UP * 0.2), run_time=1.1)
        self.wait(2.4)

    # ------------------------------------------------------------------
    def _show_cycle_table(self):
        """Animate a cycle-by-cycle register update table with a clock pulse."""
        # Header row.
        cols = ["cycle", "weight", "a_in", "sum_in", "sum_out"]
        header_cells = VGroup()
        for c in cols:
            box = Rectangle(width=1.5, height=0.6, stroke_color=th.BORDER,
                            stroke_width=1.5, fill_color=th.CARD, fill_opacity=0.9)
            lbl = Text(c, font=th.MONO, font_size=16, color=th.MUTED)
            lbl.move_to(box)
            header_cells.add(VGroup(box, lbl))
        header_cells.arrange(RIGHT, buff=0.12)
        header_cells.move_to(UP * 1.2)

        # Data rows.
        rows_data = [
            ("0", "5", "—", "0", "—"),
            ("1", "5", "10", "0", "50"),
            ("2", "5", "-4", "50", "30"),
        ]
        rows = VGroup()
        for rd in rows_data:
            row_cells = VGroup()
            for c in rd:
                box = Rectangle(width=1.5, height=0.6, stroke_color=th.BORDER,
                                stroke_width=1.5, fill_color=th.CARD, fill_opacity=0.9)
                lbl = Text(c, font=th.MONO, font_size=16, color=th.TEXT)
                lbl.move_to(box)
                row_cells.add(VGroup(box, lbl))
            row_cells.arrange(RIGHT, buff=0.12)
            rows.add(row_cells)
        rows.arrange(DOWN, buff=0.12)
        rows.next_to(header_cells, DOWN, buff=0.12)

        table = VGroup(header_cells, rows).move_to(ORIGIN)
        self.play(FadeIn(header_cells), run_time=0.4)

        # Clock edge glyph.
        edge = th.clock_symbol(color=th.PURPLE)
        edge.next_to(table, LEFT, buff=1.2)

        for i, row in enumerate(rows):
            self.play(FadeIn(row, shift=UP * 0.1), run_time=0.4)
            if i > 0:
                self._flash_edge(edge)
            self.wait(0.4)
        self.play(FadeIn(edge), run_time=0.3)
        self._flash_edge(edge)
        self.wait(0.3)

        # Annotate: weight loaded once, then compute.
        note = Text(
            "Weight 5 is loaded once.\nEach clock edge:  a_out=a_in,  sum_out = sum_in + a×w",
            font=th.SANS, font_size=17, color=th.AMBER_LIGHT, line_spacing=1.3,
        )
        note.next_to(table, DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.5)

    def _flash_edge(self, edge_glyph):
        self.play(edge_glyph.animate.set_color(th.RED), run_time=0.15)
        self.play(edge_glyph.animate.set_color(th.PURPLE), run_time=0.2)
