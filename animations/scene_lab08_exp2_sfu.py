"""
Lab 08: Hardware Exponential SFU (2^x & e^x) for SwiGLU / SiLU

Deep-dive structure:
1.  SwiGLU/SiLU dominate >60% of modern LLM compute.
2.  The base-2 trick: e^x = 2^(x·log2e) = 2^I · 2^F.
3.  The datapath: scaler → split (I,F) → barrel shifter (2^I) + 16-entry
    LUT (2^F) → multiplier. Animated packet flows through both branches.
4.  Worked example: 2^3.5 = 2^3 · 2^0.5 = 8 · 1.414 ≈ 11.31.
5.  The SiLU curve drawn, plus the RTL recap.
"""

from manim import *
import theme as th


class Lab08ExponentialSFU(Scene):
    def construct(self):
        th.set_dark(self.camera)

        # =================================================================
        # ACT 1 — SWIGLU / SILU MOTIVATION
        # =================================================================
        hdr, _, _ = th.header("LAB 08", "The Exponential SFU")
        self.play(FadeIn(hdr, shift=DOWN * 0.3), run_time=0.7)

        card = th.card(10.6, 2.6, stroke=th.AMBER, radius=0.18)
        card.move_to(UP * 0.35)

        c1 = Text("SiLU(x) = x / (1 + e⁻ˣ)",
                  font=th.MONO, weight=BOLD, font_size=22, color=th.GREEN_LIGHT)
        c2 = Text(">60% of FLOPs in LLaMA 3 / Mistral FFN blocks",
                  font=th.SANS, font_size=18, color=th.TEXT)
        c3 = Text("Taylor-series e^x = multi-cycle DSP stalls in silicon",
                  font=th.MONO, font_size=18, color=th.RED_LIGHT)
        stack = VGroup(c1, c2, c3).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        stack.move_to(card)
        self.play(Create(card), FadeIn(stack), run_time=0.9)
        self.wait(1.0)

        trick = Text("Hardware answer:  the base-2 decomposition",
                     font=th.SANS, weight=BOLD, font_size=20, color=th.CYAN_LIGHT)
        trick.next_to(card, DOWN, buff=0.4)
        self.play(FadeIn(trick, shift=UP * 0.15), run_time=0.6)
        self.wait(0.8)

        self.play(FadeOut(hdr), FadeOut(card), FadeOut(stack), FadeOut(trick),
                  run_time=0.5)

        # =================================================================
        # ACT 2 — THE BASE-2 TRICK
        # =================================================================
        b_hdr, _, _ = th.header("LAB 08", "eˣ = 2^I × 2^F")
        self.play(FadeIn(b_hdr, shift=DOWN * 0.3), run_time=0.7)

        d1 = Text("u = x · log2(e) = I + F", font=th.MONO, weight=BOLD,
                  font_size=24, color=th.CYAN)
        d1.move_to(UP * 1.0)
        self.play(Write(d1), run_time=0.7)

        d2 = Text("2^u = 2^I · 2^F", font=th.MONO, weight=BOLD, font_size=24,
                  color=th.GREEN)
        d2.next_to(d1, DOWN, buff=0.5)
        self.play(Write(d2), run_time=0.7)

        d3 = th.bullets(
            ["2^I  →  zero-delay barrel shifter (just shift bits!)",
             "2^F  →  compact 16-entry lookup table (F ∈ [0,1))"],
            font_size=20, buff=0.28, bullet_color=th.AMBER, color=th.TEXT,
        )
        d3.next_to(d2, DOWN, buff=0.55, aligned_edge=LEFT)
        self.play(FadeIn(d3, shift=UP * 0.15), run_time=0.8)
        self.wait(1.0)

        self.play(FadeOut(b_hdr), FadeOut(d1), FadeOut(d2), FadeOut(d3),
                  run_time=0.5)

        # =================================================================
        # ACT 3 — THE DATAPATH
        # =================================================================
        p_hdr, _, _ = th.header("LAB 08", "The SFU Datapath")
        self.play(FadeIn(p_hdr, shift=DOWN * 0.3), run_time=0.7)

        scaler = th.card(2.5, 1.2, stroke=th.AMBER, radius=0.14)
        scaler.shift(LEFT * 4.3)
        sc_l = Text("Scaler\nu = x·log2e", font=th.MONO, font_size=14,
                    color=th.AMBER_LIGHT).move_to(scaler)

        split = th.card(2.3, 1.2, stroke=th.CYAN, radius=0.14)
        split.shift(LEFT * 1.4)
        sp_l = Text("Split\nu = I + F", font=th.MONO, font_size=14,
                    color=th.CYAN_LIGHT).move_to(split)

        shifter = th.card(2.5, 1.0, stroke=th.GREEN, radius=0.14)
        shifter.shift(RIGHT * 1.7 + UP * 0.9)
        sh_l = Text("Barrel Shifter\n2^I", font=th.MONO, font_size=14,
                    color=th.GREEN_LIGHT).move_to(shifter)

        lut = th.card(2.5, 1.0, stroke=th.PURPLE, radius=0.14)
        lut.shift(RIGHT * 1.7 + DOWN * 0.9)
        lu_l = Text("16-Entry LUT\n2^F", font=th.MONO, font_size=14,
                    color=th.PURPLE_LIGHT).move_to(lut)

        mul = th.card(2.3, 1.2, stroke=th.GREEN, radius=0.14)
        mul.shift(RIGHT * 4.5)
        mu_l = Text("Multiply\ny = 2^I·2^F", font=th.MONO, font_size=14,
                    color=th.GREEN_LIGHT).move_to(mul)

        a1 = Arrow(scaler.get_right(), split.get_left(), buff=0.08, color=th.AMBER)
        a_up = Arrow(split.get_right(), shifter.get_left(), buff=0.08, color=th.GREEN)
        a_dn = Arrow(split.get_right(), lut.get_left(), buff=0.08, color=th.PURPLE)
        a_c1 = Arrow(shifter.get_right(), mul.get_left() + UP * 0.3, buff=0.08,
                     color=th.GREEN)
        a_c2 = Arrow(lut.get_right(), mul.get_left() + DOWN * 0.3, buff=0.08,
                     color=th.PURPLE)

        nodes = VGroup(scaler, sc_l, split, sp_l, shifter, sh_l, lut, lu_l,
                       mul, mu_l, a1, a_up, a_dn, a_c1, a_c2)
        self.play(FadeIn(nodes), run_time=1.0)

        # Two packets: integer branch and fractional branch.
        pi = th.packet(color=th.GREEN, radius=0.12)
        pf = th.packet(color=th.PURPLE, radius=0.12)
        pi.move_to(split.get_right())
        pf.move_to(split.get_right())
        self.play(FadeIn(pi), FadeIn(pf), run_time=0.25)
        self.play(pi.animate.move_to(shifter), pf.animate.move_to(lut),
                  run_time=0.5)
        self.play(pi.animate.move_to(mul), pf.animate.move_to(mul), run_time=0.5)
        self.play(FadeOut(pi), FadeOut(pf), run_time=0.25)
        self.wait(0.6)

        self.play(FadeOut(p_hdr), FadeOut(nodes), run_time=0.5)

        # =================================================================
        # ACT 4 — WORKED EXAMPLE: 2^3.5
        # =================================================================
        w_hdr, _, _ = th.header("LAB 08", "Worked Example: 2^3.5")
        self.play(FadeIn(w_hdr, shift=DOWN * 0.3), run_time=0.7)

        s1 = Text("u = 3.5  →  I = 3,  F = 0.5", font=th.MONO, font_size=21,
                  color=th.CYAN)
        s1.move_to(UP * 1.0)
        self.play(Write(s1), run_time=0.6)

        s2 = Text("2^I = 2³ = 8  (shift left by 3)", font=th.MONO, font_size=21,
                  color=th.GREEN)
        s2.next_to(s1, DOWN, buff=0.5)
        self.play(Write(s2), run_time=0.6)

        s3 = Text("2^F = 2^0.5 ≈ 1.414  (LUT)", font=th.MONO, font_size=21,
                  color=th.PURPLE_LIGHT)
        s3.next_to(s2, DOWN, buff=0.5)
        self.play(Write(s3), run_time=0.6)

        s4 = Text("2^3.5 = 8 × 1.414 ≈ 11.31  ✓", font=th.MONO, weight=BOLD,
                  font_size=22, color=th.GREEN_LIGHT)
        s4.next_to(s3, DOWN, buff=0.5)
        self.play(FadeIn(s4, shift=UP * 0.15), run_time=0.6)
        self.wait(1.0)

        self.play(FadeOut(w_hdr), FadeOut(s1), FadeOut(s2), FadeOut(s3),
                  FadeOut(s4), run_time=0.5)

        # =================================================================
        # ACT 5 — THE SILU CURVE
        # =================================================================
        c_hdr, _, _ = th.header("LAB 08", "The SiLU Activation Curve")
        self.play(FadeIn(c_hdr, shift=DOWN * 0.3), run_time=0.7)

        curve = self._silu_curve()
        curve.move_to(DOWN * 0.2)
        self.play(Create(curve[0]), run_time=1.2)

        # Highlight the negative-x asymptote (→0) and linear positive region.
        note = Text("SiLU(x) → 0 as x → -∞,  and SiLU(x) ≈ x for x ≫ 0",
                    font=th.SANS, font_size=19, color=th.MUTED)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.6)
        self.wait(1.0)

        self.play(FadeOut(c_hdr), FadeOut(curve), FadeOut(note), run_time=0.5)

        # =================================================================
        # CHECKPOINT
        # =================================================================
        th.checkpoint(
            self,
            "Why is base-2 friendlier to silicon than base-e?",
            ["2^I is just a bit shift — zero gates of math",
             "Only 2^F (a small bounded table) needs a lookup"],
        )

        # =================================================================
        # CHALLENGE
        # =================================================================
        th.challenge(
            self,
            ["Compute 2^4.5 with the SFU.",
             "Split u = 4.5 into I = 4 and F = 0.5.",
             "The LUT gives 2^0.5 ≈ 362 in Q0.8."],
            "362 shifted left by 4 = 5792 → 22.625 (true 2^4.5 ≈ 22.63).",
        )

        # =================================================================
        # ACT 6 — RECAP
        # =================================================================
        th.recap(
            self,
            "rtl/exp2_sfu.sv",
            ["mode_e: 1 = e^x (pre-scale by log2e),  0 = 2^x",
             "Split u into integer I (barrel shift) + fraction F (LUT)",
             "Overflow clamp saturates at Q8.8 max (65535)",
             "~3.2 ns path replaces multi-cycle Taylor series",
             "You have built the whole Silicon AI stack — 00 to 08!"],
            wait=2.6,
        )

    # ------------------------------------------------------------------
    def _silu_curve(self):
        """Build the SiLU(x) = x·σ(x) curve as a VMobject over [-5, 5]."""
        import numpy as np

        def silu(x):
            return x / (1.0 + np.exp(-x))

        xs = np.linspace(-5, 5, 120)
        ys = silu(xs)
        # Normalize to the frame: x ∈ [-5,5] → [-5.5, 5.5]; y ∈ [-0.4, 5] → scale.
        points = [np.array([x * 1.0, y * 0.72, 0]) for x, y in zip(xs, ys)]
        curve = VMobject(color=th.CYAN, stroke_width=4)
        curve.set_points_smoothly(points)

        # A faint zero line.
        zero = Line(np.array([-5, 0, 0]), np.array([5, 0, 0]),
                    color=th.BORDER, stroke_width=1.5)
        return VGroup(curve, zero)
