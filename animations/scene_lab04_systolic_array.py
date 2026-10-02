"""
Lab 04: 4x4 Systolic Array Matrix Multiplier & 2D Wavefront

Deep-dive structure:
1.  The promise: TPU-style 2D spatial dataflow (100+ TFLOPS).
2.  A 2×2 grid with weights locked inside each PE (real numbers).
3.  Activation skewing: why Row 1 must be delayed by 1 clock cycle.
4.  The full wavefront walkthrough with real data packets: T=1, T=2, T=3.
    The correct matrix product [19, 22] emerges from the bottom.
5.  Scaling to 4×4, the latency formula 3N-2, and the RTL recap.
"""

from manim import *
import theme as th


class Lab04SystolicArray(Scene):
    def construct(self):
        th.set_dark(self.camera)

        # =================================================================
        # ACT 1 — THE PROMISE
        # =================================================================
        hdr, _, _ = th.header("LAB 04", "The Systolic Array")
        self.play(FadeIn(hdr, shift=DOWN * 0.3), run_time=0.7)

        sub = Text(
            "How TPUs hit 100+ TFLOPS: 2D spatial dataflow",
            font=th.SANS, font_size=20, color=th.MUTED,
        )
        sub.next_to(hdr, DOWN, buff=0.35)
        self.play(FadeIn(sub), run_time=0.5)

        # Three mini points: no shared bus, neighbor wires, weights stationary.
        pts = th.bullets(
            ["No shared bus: each PE talks only to its neighbours",
             "Activations stream East; partial sums stream South",
             "Weights stay locked inside each PE"],
            font_size=20, buff=0.3, bullet_color=th.CYAN, color=th.TEXT,
        )
        pts.next_to(sub, DOWN, buff=0.6, aligned_edge=LEFT)
        self.play(FadeIn(pts, shift=UP * 0.15), run_time=0.8)
        self.wait(1.0)

        self.play(FadeOut(hdr), FadeOut(sub), FadeOut(pts), run_time=0.5)

        # =================================================================
        # ACT 2 — THE 2×2 GRID WITH WEIGHTS
        # =================================================================
        g_hdr, _, _ = th.header("LAB 04", "A 2×2 Grid, Weights Locked In")
        self.play(FadeIn(g_hdr, shift=DOWN * 0.3), run_time=0.7)

        self.pe_grid = self._build_grid(2)
        self.play(Create(self.pe_grid, lag_ratio=0.04), run_time=1.0)

        # Show the input vector A = [1, 2] and weight matrix W.
        a_vec = th.matrix([["1", "2"]], color=th.CYAN, label="A row")
        w_mat = th.matrix([["5", "6"], ["7", "8"]], color=th.AMBER, label="W")
        a_vec.next_to(self.pe_grid, LEFT, buff=1.4)
        w_mat.next_to(self.pe_grid, UP, buff=0.5)
        self.play(FadeIn(a_vec), FadeIn(w_mat), run_time=0.7)
        self.wait(0.9)

        self.play(FadeOut(g_hdr), FadeOut(a_vec), FadeOut(w_mat),
                  FadeOut(self.pe_grid), run_time=0.5)

        # =================================================================
        # ACT 3 — ACTIVATION SKEWING
        # =================================================================
        s_hdr, _, _ = th.header("LAB 04", "Why Inputs Must Be Skewed")
        self.play(FadeIn(s_hdr, shift=DOWN * 0.3), run_time=0.7)

        explain = Text(
            "Row 1 must wait 1 clock so it meets the partial sum\ncoming down from Row 0.",
            font=th.SANS, font_size=21, color=th.TEXT, line_spacing=1.4,
        )
        explain.next_to(s_hdr, DOWN, buff=0.5)
        self.play(FadeIn(explain), run_time=0.6)

        # Show the two streams: row 0 immediate, row 1 delayed by a D-FF.
        r0 = VGroup(
            Text("Row 0:", font=th.MONO, font_size=19, color=th.CYAN),
            th.bit_row("21", color=th.CYAN),
        ).arrange(RIGHT, buff=0.3)
        r0.move_to(UP * 0.1)

        ff = th.card(0.9, 0.8, stroke=th.AMBER, radius=0.1)
        ff.move_to(DOWN * 1.0 + LEFT * 0.5)
        ff_l = Text("D-FF", font=th.SANS, font_size=13, color=th.AMBER_LIGHT).move_to(ff)

        r1_in = th.bit_row("43", color=th.AMBER)
        r1_in.next_to(ff, LEFT, buff=0.5)
        r1_out = th.bit_row("43", color=th.AMBER)
        r1_out.next_to(ff, RIGHT, buff=0.5)
        arrow_in = Arrow(r1_in.get_right(), ff.get_left(), buff=0.06, color=th.AMBER)
        arrow_out = Arrow(ff.get_right(), r1_out.get_left(), buff=0.06, color=th.AMBER)
        r1_lbl = Text("Row 1: 1-cycle delay", font=th.MONO, font_size=17,
                      color=th.AMBER_LIGHT).next_to(ff, DOWN, buff=0.35)

        self.play(FadeIn(r0), run_time=0.4)
        self.play(FadeIn(ff), FadeIn(ff_l), FadeIn(r1_in), FadeIn(r1_out),
                  FadeIn(arrow_in), FadeIn(arrow_out), FadeIn(r1_lbl), run_time=0.6)

        # Animate a packet being delayed.
        pk = th.packet(color=th.AMBER, radius=0.1)
        pk.move_to(r1_in.get_left())
        self.play(FadeIn(pk), run_time=0.2)
        self.play(pk.animate.move_to(ff), run_time=0.4)
        self.wait(0.4)
        self.play(pk.animate.move_to(r1_out.get_right()), run_time=0.4)
        self.play(FadeOut(pk), run_time=0.2)
        self.wait(0.6)

        self.play(FadeOut(s_hdr), FadeOut(explain), FadeOut(r0), FadeOut(ff),
                  FadeOut(ff_l), FadeOut(r1_in), FadeOut(r1_out), FadeOut(arrow_in),
                  FadeOut(arrow_out), FadeOut(r1_lbl), run_time=0.5)

        # =================================================================
        # ACT 4 — THE WAVEFRONT WALKTHROUGH
        # =================================================================
        w_hdr, _, _ = th.header("LAB 04", "The Wavefront, Clock by Clock")
        self.play(FadeIn(w_hdr, shift=DOWN * 0.3), run_time=0.7)

        grid = self._build_grid(2, show_weights=True)
        grid.move_to(DOWN * 0.15)
        self.play(Create(grid, lag_ratio=0.04), run_time=1.0)

        cycle = Text("T = 1", font=th.MONO, weight=BOLD, font_size=22,
                     color=th.GREEN_LIGHT)
        cycle.next_to(grid, UP, buff=0.6)
        self.play(FadeIn(cycle), run_time=0.3)

        # --- T=1: a=1 enters PE(0,0) ---
        pkt = th.packet(color=th.CYAN, radius=0.14)
        pkt.move_to(grid[0][0].get_left() + LEFT * 0.6)
        self.play(FadeIn(pkt), run_time=0.25)
        self.play(pkt.animate.move_to(grid[0][0]), run_time=0.4)
        self.play(grid[0][0].animate.set_fill(th.AMBER, opacity=0.9)
                  .set_stroke(th.AMBER_LIGHT, width=3), run_time=0.3)
        self.wait(0.4)

        # --- T=2: a=1 → PE(0,1); a=2 (skewed) → PE(1,0) ---
        self.play(Transform(cycle, Text("T = 2", font=th.MONO, weight=BOLD,
                                        font_size=22, color=th.GREEN_LIGHT)
                            .move_to(cycle)), run_time=0.3)
        pkt2 = th.packet(color=th.CYAN, radius=0.14)
        pkt2.move_to(grid[1][0].get_left() + LEFT * 0.6)
        self.play(pkt.animate.move_to(grid[0][1]).set_color(th.CYAN),
                  FadeIn(pkt2), run_time=0.45)
        self.play(grid[0][0].animate.set_fill(th.CARD, opacity=0.9)
                  .set_stroke(th.BORDER, width=2),
                  grid[0][1].animate.set_fill(th.CYAN, opacity=0.8)
                  .set_stroke(th.CYAN_LIGHT, width=3),
                  grid[1][0].animate.set_fill(th.AMBER, opacity=0.9)
                  .set_stroke(th.AMBER_LIGHT, width=3), run_time=0.4)
        self.wait(0.5)

        # --- T=3: a=2 → PE(1,1); outputs emerge ---
        self.play(Transform(cycle, Text("T = 3", font=th.MONO, weight=BOLD,
                                        font_size=22, color=th.GREEN_LIGHT)
                            .move_to(cycle)), run_time=0.3)
        self.play(pkt2.animate.move_to(grid[1][1]).set_color(th.CYAN), run_time=0.45)
        self.play(grid[0][1].animate.set_fill(th.CARD, opacity=0.9)
                  .set_stroke(th.BORDER, width=2),
                  grid[1][0].animate.set_fill(th.CARD, opacity=0.9)
                  .set_stroke(th.BORDER, width=2),
                  grid[1][1].animate.set_fill(th.GREEN, opacity=0.85)
                  .set_stroke(th.GREEN_LIGHT, width=3), run_time=0.4)
        self.play(FadeOut(pkt), FadeOut(pkt2), run_time=0.25)

        # Outputs: C = [19, 22] at the bottom.
        out_lbl = Text("C = [ 19 , 22 ]", font=th.MONO, weight=BOLD, font_size=24,
                       color=th.GREEN)
        out_lbl.next_to(grid, DOWN, buff=0.7)
        self.play(FadeIn(out_lbl, shift=UP * 0.2), run_time=0.5)

        verify = Text("check:  1·5 + 2·7 = 19     1·6 + 2·8 = 22",
                      font=th.MONO, font_size=17, color=th.MUTED)
        verify.next_to(out_lbl, DOWN, buff=0.3)
        self.play(FadeIn(verify), run_time=0.5)
        self.wait(1.3)

        self.play(FadeOut(w_hdr), FadeOut(grid), FadeOut(cycle), FadeOut(out_lbl),
                  FadeOut(verify), run_time=0.5)

        # =================================================================
        # CHECKPOINT
        # =================================================================
        th.checkpoint(
            self,
            "Why must Row k be delayed by exactly k clock cycles?",
            ["Row 0's partial sum takes k hops to reach Row k",
             "Delaying Row k by k aligns its data with the arriving sum"],
        )

        # =================================================================
        # CHALLENGE
        # =================================================================
        th.challenge(
            self,
            ["Compute A·W for A = [3, 4] and W = [[1, 2], [3, 4]].",
             "What is the result vector C?"],
            "C = [3·1 + 4·3, 3·2 + 4·4] = [15, 22].",
        )

        # =================================================================
        # ACT 5 — SCALE & RECAP
        # =================================================================
        th.recap(
            self,
            "Scaling Up: rtl/systolic_array.sv",
            ["4×4 array = 16 PEs = 16 MACs every clock cycle",
             "Skew registers: Row k delayed by k cycles (built-in flip-flops)",
             "Latency = 3N - 2 = 10 cycles for N=4 (initiation interval 1)",
             "Each input byte is loaded exactly once — O(N²) loads, not O(N³)",
             "Next: Lab 05 — Hardware Square Root & Attention Scaling"],
        )

    # ------------------------------------------------------------------
    def _build_grid(self, n, show_weights=False):
        """Build an n×n PE grid. Returns a 2D list of cell rectangles."""
        # Weights for the 2x2 worked example: PE(r,c) holds W[r][c].
        weights = {2: [["5", "6"], ["7", "8"]]}
        cells = []
        g = VGroup()
        spacing = 1.35
        origin = LEFT * spacing * (n - 1) / 2 + UP * spacing * (n - 1) / 2
        for r in range(n):
            row = []
            for c in range(n):
                cell = th.card(1.15, 1.15, stroke=th.BORDER, stroke_w=2, radius=0.15)
                cell.move_to(origin + RIGHT * c * spacing + DOWN * r * spacing)
                tag = Text(f"PE {r},{c}", font=th.MONO, font_size=13, color=th.MUTED)
                tag.move_to(cell.get_center() + UP * 0.25)
                cell.add(tag)
                if show_weights and n in weights:
                    w = Text(f"w={weights[n][r][c]}", font=th.MONO,
                             font_size=16, color=th.AMBER_LIGHT)
                    w.move_to(cell.get_center() + DOWN * 0.22)
                    cell.add(w)
                g.add(cell)
                row.append(cell)
            cells.append(row)
        g.move_to(ORIGIN)
        self.cells = cells
        return g
