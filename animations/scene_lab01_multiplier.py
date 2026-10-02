"""
Lab 01: Signed INT8 Multiplier & O(N^2) Silicon Scaling

Deep-dive structure:
1.  Why multiplication dominates AI silicon (GEMM > 90% of energy).
2.  Bit growth: 8-bit × 8-bit → 16-bit, with the -128 × -128 = +16384
    corner case as the proof.
3.  How silicon multiplies: shift-and-add partial products, animated with
    real numbers (6 × 3 = 18).
4.  Area scaling: adder O(N) vs multiplier O(N²); the 8×8 dot grid fills in.
5.  RTL recap: multiplier_int8.sv — pure combinational signed product.
"""

from manim import *
import theme as th


class Lab01Multiplier(Scene):
    def construct(self):
        th.set_dark(self.camera)

        # =================================================================
        # ACT 1 — WHY MULTIPLICATION DOMINATES
        # =================================================================
        hdr, _, _ = th.header("LAB 01", "The INT8 Multiplier")
        self.play(FadeIn(hdr, shift=DOWN * 0.3), run_time=0.7)

        stat = Text(
            "LLM inference spends >90% of energy on matrix multiplies (GEMM)",
            font=th.SANS, font_size=20, color=th.MUTED,
        )
        stat.next_to(hdr, DOWN, buff=0.35)
        self.play(FadeIn(stat), run_time=0.6)

        # A matrix-multiply mini diagram: A @ W = C, with animated MAC pulses.
        a_mat, a_cells = self._matrix([["a00", "a01"], ["a10", "a11"]], th.CYAN)
        w_mat, w_cells = self._matrix([["w00", "w01"], ["w10", "w11"]], th.AMBER)
        c_mat, c_cells = self._matrix([["c00", "c01"], ["c10", "c11"]], th.GREEN)
        times = Text("×", font=th.MONO, weight=BOLD, font_size=30, color=th.TEXT)
        equals = Text("=", font=th.MONO, weight=BOLD, font_size=30, color=th.TEXT)
        row = VGroup(a_mat, times, w_mat, equals, c_mat).arrange(RIGHT, buff=0.5)
        row.next_to(stat, DOWN, buff=0.6)
        self.play(FadeIn(row), run_time=0.8)

        # Pulse: a00*w00 + a10*w10 -> c00
        c00 = c_cells[0][1]
        self.play(c00.animate.set_color(th.GREEN_LIGHT), run_time=0.3)
        self.play(Indicate(c00, color=th.GREEN, scale_factor=1.1), run_time=0.6)
        self.wait(0.8)

        self.play(FadeOut(hdr), FadeOut(stat), FadeOut(row), run_time=0.5)

        # =================================================================
        # ACT 2 — BIT GROWTH
        # =================================================================
        b_hdr, _, _ = th.header("LAB 01", "8 bits × 8 bits = 16 bits")
        self.play(FadeIn(b_hdr, shift=DOWN * 0.3), run_time=0.7)

        card = th.card(10.6, 2.2, stroke=th.BORDER, radius=0.18)
        card.move_to(UP * 0.4)

        a = Text("A: 8-bit signed", font=th.MONO, font_size=18, color=th.CYAN)
        x = Text("×", font=th.MONO, weight=BOLD, font_size=30, color=th.TEXT)
        b = Text("B: 8-bit signed", font=th.MONO, font_size=18, color=th.AMBER)
        arrow = Text("→", font=th.MONO, font_size=30, color=th.TEXT)
        p = Text("Product: 16-bit signed", font=th.MONO, font_size=18, color=th.GREEN)
        grp = VGroup(a, x, b, arrow, p).arrange(RIGHT, buff=0.5).move_to(card)
        self.play(Create(card), FadeIn(grp), run_time=0.8)
        self.wait(0.5)

        # Worst-case proof.
        proof = th.card(10.6, 1.2, stroke=th.AMBER, fill=th.AMBER_DARK, radius=0.14)
        proof.next_to(card, DOWN, buff=0.4)
        proof_t = Text(
            "Corner case:  (-128) × (-128) = +16,384  → needs 16 bits, not 15!",
            font=th.MONO, font_size=17, color=th.AMBER_LIGHT,
        ).move_to(proof)
        self.play(Create(proof), FadeIn(proof_t), run_time=0.7)
        self.wait(1.0)

        self.play(FadeOut(b_hdr), FadeOut(card), FadeOut(grp), FadeOut(proof),
                  FadeOut(proof_t), run_time=0.5)

        # =================================================================
        # ACT 3 — SHIFT-AND-ADD: 6 × 3 = 18
        # =================================================================
        m_hdr, _, _ = th.header("LAB 01", "How Silicon Multiplies: 6 × 3")
        self.play(FadeIn(m_hdr, shift=DOWN * 0.3), run_time=0.7)

        # Binary operands.
        a_bits = th.bit_row("0110", color=th.CYAN)   # 6
        b_bits = th.bit_row("0011", color=th.AMBER)  # 3
        a_lbl = Text("A = 6", font=th.MONO, font_size=17, color=th.CYAN)
        b_lbl = Text("B = 3", font=th.MONO, font_size=17, color=th.AMBER)
        a_grp = VGroup(a_lbl, a_bits).arrange(RIGHT, buff=0.3)
        b_grp = VGroup(b_lbl, b_bits).arrange(RIGHT, buff=0.3)
        ops = VGroup(a_grp, b_grp).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        ops.move_to(UP * 0.7)

        self.play(FadeIn(ops), run_time=0.7)

        # Partial products (each row: A shifted left by k, gated by B[k]).
        pp_rows = [
            ("0110", "A × B[0]=1  (shift 0)", th.GREEN),
            ("0110", "A × B[1]=1  (shift 1)", th.GREEN),
            ("0000", "A × B[2]=0  (shift 2)", th.FAINT),
            ("0000", "A × B[3]=0  (shift 3)", th.FAINT),
        ]
        pp_group = VGroup()
        for i, (bits, note, col) in enumerate(pp_rows):
            row_bits = th.bit_row(bits, color=col)
            for cell in row_bits:
                cell[0].set_stroke(col if col != th.FAINT else th.BORDER, width=1.5)
                cell[1].set_color(col)
            row_note = Text(note, font=th.MONO, font_size=14, color=col)
            row_grp = VGroup(row_bits, row_note).arrange(RIGHT, buff=0.5)
            pp_group.add(row_grp)
        pp_group.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        pp_group.next_to(ops, DOWN, buff=0.6)

        # Show one partial product at a time.
        for i, pp in enumerate(pp_group):
            self.play(FadeIn(pp, shift=UP * 0.1), run_time=0.45)
        self.wait(0.6)

        # Sum line and result 10010 = 18.
        sum_line = Line(pp_group.get_left() + DOWN * 0.35,
                        pp_group.get_right() + DOWN * 0.35,
                        color=th.BORDER, stroke_width=2)
        self.play(Create(sum_line), run_time=0.4)

        res_bits = th.bit_row("10010", color=th.GREEN)
        for cell in res_bits:
            cell[0].set_stroke(th.GREEN, width=2)
            cell[1].set_color(th.GREEN_LIGHT)
        res_lbl = Text("= 18", font=th.MONO, weight=BOLD, font_size=20, color=th.GREEN)
        res_grp = VGroup(res_bits, res_lbl).arrange(RIGHT, buff=0.4)
        res_grp.next_to(sum_line, DOWN, buff=0.35)
        self.play(FadeIn(res_grp, shift=UP * 0.1), run_time=0.6)
        self.wait(1.0)

        self.play(FadeOut(m_hdr), FadeOut(ops), FadeOut(pp_group), FadeOut(sum_line),
                  FadeOut(res_grp), run_time=0.5)

        # =================================================================
        # ACT 4 — O(N) vs O(N²) AREA
        # =================================================================
        a_hdr, _, _ = th.header("LAB 01", "The Silicon Cost: O(N²)")
        self.play(FadeIn(a_hdr, shift=DOWN * 0.3), run_time=0.7)

        # 8x8 dot grid of partial products fills in.
        dots = VGroup()
        for i in range(8):
            for j in range(8):
                d = Dot(point=np.array([(j - 3.5) * 0.46, (3.5 - i) * 0.42 - 0.4, 0]),
                        radius=0.06, color=th.CYAN)
                dots.add(d)
        grid_lbl = Text("8 × 8 = 64 partial products", font=th.SANS,
                        weight=BOLD, font_size=20, color=th.CYAN_LIGHT)
        grid_lbl.next_to(dots, UP, buff=0.4)
        self.play(FadeIn(grid_lbl), run_time=0.4)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.015),
                  run_time=1.4)
        self.wait(0.5)

        # Compare adder vs multiplier.
        comp = th.card(10.0, 1.4, stroke=th.BORDER, radius=0.16)
        comp.to_edge(DOWN, buff=0.5)
        c1 = Text("Adder:  O(N)  ≈ 42 gates", font=th.MONO, font_size=18,
                  color=th.GREEN)
        c2 = Text("Multiplier:  O(N²)  ≈ 456 gates", font=th.MONO, font_size=18,
                  color=th.RED)
        comp_grp = VGroup(c1, c2).arrange(DOWN, buff=0.15).move_to(comp)
        self.play(Create(comp), FadeIn(comp_grp), run_time=0.7)
        self.wait(1.2)

        self.play(FadeOut(a_hdr), FadeOut(dots), FadeOut(grid_lbl), FadeOut(comp),
                  FadeOut(comp_grp), run_time=0.5)

        # =================================================================
        # ACT 5 — RTL RECAP
        # =================================================================
        card = th.card(10.0, 3.9, stroke=th.GREEN, radius=0.22)
        t = Text("rtl/multiplier_int8.sv", font=th.SANS, weight=BOLD, font_size=26,
                 color=th.GREEN_LIGHT)
        t.next_to(card.get_top(), DOWN, buff=0.35)
        pts = th.bullets(
            ["Inputs: signed [7:0] a, signed [7:0] b",
             "Output: signed [15:0] product — zero precision loss",
             "Pure combinational: assign product = a * b",
             "Verified vs all 65,536 input pairs in Cocotb",
             "Next: Lab 02 — MAC Unit & Accumulator Headroom"],
            font_size=18, buff=0.28, bullet_color=th.GREEN, color=th.TEXT,
        )
        pts.next_to(t, DOWN, buff=0.4, aligned_edge=LEFT)
        pts.move_to(card.get_center() + DOWN * 0.15)
        self.play(Create(card), Write(t), FadeIn(pts, shift=UP * 0.2), run_time=1.1)
        self.wait(2.4)

    # ------------------------------------------------------------------
    def _matrix(self, vals, color):
        """Build a small labelled 2x2 matrix. Returns (VGroup, cells as list)."""
        cells = []
        g = VGroup()
        for r in range(2):
            for c in range(2):
                box = Square(side_length=0.62, stroke_color=th.BORDER,
                             stroke_width=1.5, fill_color=th.CARD, fill_opacity=0.95)
                box.move_to(np.array([c * 0.75, -r * 0.75, 0]))
                lbl = Text(vals[r][c], font=th.MONO, font_size=17, color=color)
                lbl.move_to(box)
                unit = VGroup(box, lbl)
                g.add(unit)
                cells.append(unit)
        g.move_to(ORIGIN)
        return g, cells
