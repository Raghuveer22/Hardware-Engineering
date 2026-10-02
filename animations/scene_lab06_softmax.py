"""
Lab 06: Hardware Safe Softmax Engine & FlashAttention

Deep-dive structure:
1.  The overflow trap: e^50 ≈ 5×10^21 overflows fixed-point registers.
2.  Safe softmax: Δi = xi - max(X) ≤ 0 → e^Δi in (0,1]. Bounded forever.
3.  Worked example: logits [12, 10, 8, 6] → [0.813, 0.110, 0.015, 0.002]
    computed stage by stage through the 4-stage pipeline.
4.  FlashAttention note (online rescaling, O(N) memory).
5.  RTL recap: rtl/softmax.sv.
"""

from manim import *
import theme as th


class Lab06Softmax(Scene):
    def construct(self):
        th.set_dark(self.camera)

        # =================================================================
        # ACT 1 — THE OVERFLOW TRAP
        # =================================================================
        hdr, _, _ = th.header("LAB 06", "Safe Softmax")
        self.play(FadeIn(hdr, shift=DOWN * 0.3), run_time=0.7)

        card = th.card(10.6, 2.4, stroke=th.RED, radius=0.18)
        card.move_to(UP * 0.35)

        b1 = Text("Raw softmax:  P_i = e^xi / Σ e^xj",
                  font=th.MONO, weight=BOLD, font_size=21, color=th.TEXT)
        b2 = Text("If a logit x = 50 → e^50 ≈ 5.18 × 10²¹",
                  font=th.MONO, font_size=18, color=th.RED_LIGHT)
        b3 = Text("Exceeds 64-bit registers → NaN / overflow in silicon",
                  font=th.SANS, font_size=18, color=th.RED)
        stack = VGroup(b1, b2, b3).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        stack.move_to(card)
        self.play(Create(card), FadeIn(stack), run_time=0.9)
        self.wait(1.0)

        # The fix.
        fix = Text("Fix: subtract the maximum before exponentiating",
                   font=th.SANS, weight=BOLD, font_size=21, color=th.GREEN_LIGHT)
        fix.next_to(card, DOWN, buff=0.4)
        self.play(FadeIn(fix, shift=UP * 0.15), run_time=0.6)
        self.wait(0.8)

        self.play(FadeOut(hdr), FadeOut(card), FadeOut(stack), FadeOut(fix),
                  run_time=0.5)

        # =================================================================
        # ACT 2 — THE MATHEMATICAL GUARANTEE
        # =================================================================
        m_hdr, _, _ = th.header("LAB 06", "Why It Is Safe")
        self.play(FadeIn(m_hdr, shift=DOWN * 0.3), run_time=0.7)

        f1 = Text("Δi = xi − max(X)  ≤  0", font=th.MONO, weight=BOLD,
                  font_size=26, color=th.CYAN)
        f1.move_to(UP * 0.9)
        self.play(Write(f1), run_time=0.8)

        f2 = Text("→  e^Δi ∈ (0, 1]", font=th.MONO, weight=BOLD, font_size=22,
                  color=th.GREEN)
        f2.next_to(f1, DOWN, buff=0.5)
        self.play(FadeIn(f2, shift=UP * 0.15), run_time=0.6)

        f3 = Text("Bounded forever — fits Q0.8 registers, zero overflow",
                  font=th.SANS, font_size=20, color=th.AMBER_LIGHT)
        f3.next_to(f2, DOWN, buff=0.5)
        self.play(FadeIn(f3), run_time=0.5)
        self.wait(1.0)

        self.play(FadeOut(m_hdr), FadeOut(f1), FadeOut(f2), FadeOut(f3),
                  run_time=0.5)

        # =================================================================
        # ACT 3 — WORKED EXAMPLE THROUGH THE PIPELINE
        # =================================================================
        p_hdr, _, _ = th.header("LAB 06", "Logits [12, 10, 8, 6] → Probabilities")
        self.play(FadeIn(p_hdr, shift=DOWN * 0.3), run_time=0.7)

        # The four pipeline stages as cards. Numbers are the exact fixed-point
        # values from rtl/softmax.sv's Q0.8 exp LUT + normalizer.
        stages = [
            ("1 · MAX", "max = 12", th.AMBER),
            ("2 · DELTA", "Δ = [0,-2,-4,-6]", th.CYAN),
            ("3 · EXP LUT", "e^Δ = [255,94,35,13]", th.PURPLE),
            ("4 · NORMALIZE", "P = [163,60,22,8]", th.GREEN),
        ]
        cards = VGroup()
        for i, (name, detail, color) in enumerate(stages):
            c = th.card(3.4, 1.5, stroke=color, radius=0.14)
            c.move_to(LEFT * 4.4 + RIGHT * i * 2.95)
            nm = Text(name, font=th.SANS, weight=BOLD, font_size=17, color=color)
            nm.next_to(c.get_top(), DOWN, buff=0.18)
            dt = Text(detail, font=th.MONO, font_size=13, color=th.TEXT)
            dt.move_to(c.get_center() + DOWN * 0.15)
            cards.add(VGroup(c, nm, dt))

        # Connect with arrows.
        arrows = VGroup()
        for i in range(3):
            a = Arrow(cards[i][0].get_right(), cards[i + 1][0].get_left(),
                      buff=0.15, color=th.BORDER)
            arrows.add(a)

        self.play(FadeIn(cards), FadeIn(arrows), run_time=1.0)

        # Reveal stages one at a time to walk through the computation.
        for i in range(len(stages)):
            self.play(Indicate(cards[i][0], color=stages[i][2], scale_factor=1.05),
                      run_time=0.5)
        self.wait(1.2)

        # FlashAttention note.
        flash = Text(
            "FlashAttention fuses this online: O(N) memory, no O(N²) attention matrix.",
            font=th.SANS, font_size=18, color=th.AMBER_LIGHT,
        )
        flash.to_edge(DOWN, buff=0.55)
        self.play(FadeIn(flash, shift=UP * 0.15), run_time=0.6)
        self.wait(1.0)

        self.play(FadeOut(p_hdr), FadeOut(cards), FadeOut(arrows), FadeOut(flash),
                  run_time=0.5)

        # =================================================================
        # ACT 3b — SECOND EXAMPLE: UNIFORM INPUT
        # =================================================================
        u_hdr, _, _ = th.header("LAB 06", "Uniform Logits [10, 10, 10, 10]")
        self.play(FadeIn(u_hdr, shift=DOWN * 0.3), run_time=0.7)

        u1 = Text("max = 10  →  Δ = [0, 0, 0, 0]", font=th.MONO, font_size=21,
                  color=th.CYAN)
        u1.move_to(UP * 0.9)
        self.play(Write(u1), run_time=0.6)

        u2 = Text("e^Δ = [255, 255, 255, 255]  (all 1.0 in Q0.8)",
                  font=th.MONO, font_size=21, color=th.PURPLE_LIGHT)
        u2.next_to(u1, DOWN, buff=0.5)
        self.play(Write(u2), run_time=0.6)

        u3 = Text("sum = 1020  →  P = [63, 63, 63, 63]  (each ≈ ¼)",
                  font=th.MONO, weight=BOLD, font_size=22, color=th.GREEN_LIGHT)
        u3.next_to(u2, DOWN, buff=0.5)
        self.play(FadeIn(u3, shift=UP * 0.15), run_time=0.6)

        # Equal bars.
        bars = VGroup()
        for i in range(4):
            b = Rectangle(width=0.6, height=1.6, fill_color=th.GREEN,
                          fill_opacity=0.9, stroke_width=0)
            bars.add(b)
        bars.arrange(RIGHT, buff=0.6)
        bars.next_to(u3, DOWN, buff=0.7)
        bar_lbl = Text("All four probabilities are equal (uniform)",
                       font=th.SANS, font_size=18, color=th.MUTED)
        bar_lbl.next_to(bars, DOWN, buff=0.25)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars],
                              lag_ratio=0.1), run_time=0.8)
        self.play(FadeIn(bar_lbl), run_time=0.4)
        self.wait(1.0)

        self.play(FadeOut(u_hdr), FadeOut(u1), FadeOut(u2), FadeOut(u3),
                  FadeOut(bars), FadeOut(bar_lbl), run_time=0.5)

        # =================================================================
        # CHECKPOINT
        # =================================================================
        th.checkpoint(
            self,
            "Why does subtracting the max leave softmax unchanged?",
            ["e^(x-C) / Σ e^(x-C) = e^x / Σ e^x  (C cancels)",
             "But now all exponents ≤ 1 → no overflow possible"],
        )

        # =================================================================
        # CHALLENGE
        # =================================================================
        th.challenge(
            self,
            ["Run the RTL softmax on logits [5, 5, 0, 0].",
             "Use the Q0.8 LUT: e^0 = 255, e^-5 = 21.",
             "What is the output probability vector?"],
            "exp = [255, 255, 21, 21], sum = 552 → P = [117, 117, 9, 9].",
        )

        # =================================================================
        # ACT 4 — RECAP
        # =================================================================
        th.recap(
            self,
            "rtl/softmax.sv",
            ["Max tree → subtract → exp LUT → normalize",
             "Invariant: output probabilities sum to 255 (Q0.8 = 1.0)",
             "All exponents stay in (0,1] — no overflow possible",
             "Next: Lab 07 — Fast RSQRT for RMSNorm"],
        )
