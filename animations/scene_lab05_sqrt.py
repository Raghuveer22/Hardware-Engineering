"""
Lab 05: Hardware Square Root Unit & Attention Scaling

Deep-dive structure:
1.  Why transformers need 1/sqrt(d_k): unscaled logits saturate softmax.
2.  The hardware idea: digit-by-digit shift-and-subtract, no multiplier.
3.  Worked example sqrt(64) = 8, animated bit-pair by bit-pair.
4.  RTL recap: rtl/sqrt.sv — 8 unrolled stages, zero multipliers.
"""

from manim import *
import theme as th


class Lab05SquareRoot(Scene):
    def construct(self):
        th.set_dark(self.camera)

        # =================================================================
        # ACT 1 — ATTENTION SCALING
        # =================================================================
        hdr, _, _ = th.header("LAB 05", "Hardware Square Root")
        self.play(FadeIn(hdr, shift=DOWN * 0.3), run_time=0.7)

        card = th.card(10.6, 2.6, stroke=th.CYAN, radius=0.18)
        card.move_to(UP * 0.35)

        a1 = Text("Attention(Q,K,V) = Softmax( (Q·Kᵀ) / √d_k ) · V",
                  font=th.MONO, weight=BOLD, font_size=21, color=th.GREEN_LIGHT)
        a2 = Text("Without 1/√d_k: dot-product variance grows with d_k",
                  font=th.SANS, font_size=18, color=th.RED_LIGHT)
        a3 = Text("Huge logits push softmax into saturation → dead gradients",
                  font=th.SANS, font_size=18, color=th.AMBER_LIGHT)
        stack = VGroup(a1, a2, a3).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        stack.move_to(card)
        self.play(Create(card), FadeIn(stack), run_time=0.9)
        self.wait(1.2)

        self.play(FadeOut(hdr), FadeOut(card), FadeOut(stack), run_time=0.5)

        # =================================================================
        # ACT 2 — THE HARDWARE IDEA
        # =================================================================
        i_hdr, _, _ = th.header("LAB 05", "Root Without a Multiplier")
        self.play(FadeIn(i_hdr, shift=DOWN * 0.3), run_time=0.7)

        idea = th.bullets(
            ["Digit-by-digit: shift-and-subtract, like long division",
             "Consumes 2 radicand bits → produces 1 root bit",
             "Only muxes, subtractors and shifters — zero multipliers",
             "rtl/sqrt.sv: 8 unrolled stages, ~4.2 ns path"],
            font_size=20, buff=0.3, bullet_color=th.CYAN, color=th.TEXT,
        )
        idea.move_to(UP * 0.4)
        self.play(FadeIn(idea, shift=UP * 0.15), run_time=0.9)
        self.wait(1.0)

        self.play(FadeOut(i_hdr), FadeOut(idea), run_time=0.5)

        # =================================================================
        # ACT 3 — WORKED EXAMPLE: sqrt(64)
        # =================================================================
        w_hdr, _, _ = th.header("LAB 05", "Worked Example: √64")
        self.play(FadeIn(w_hdr, shift=DOWN * 0.3), run_time=0.7)

        radicand = Text("radicand = 64  (0100 0000)", font=th.MONO,
                        font_size=20, color=th.CYAN)
        radicand.next_to(w_hdr, DOWN, buff=0.5)
        self.play(FadeIn(radicand), run_time=0.5)

        # Bit-pair extraction: group radicand bits into pairs from MSB.
        pairs = ["01", "00", "00", "00"]
        pair_group = VGroup()
        for p in pairs:
            pair_group.add(th.bit_row(p, color=th.CYAN))
        pair_group.arrange(RIGHT, buff=0.3)
        pair_group.next_to(radicand, DOWN, buff=0.6)
        self.play(FadeIn(pair_group), run_time=0.5)

        # Root register filling in, MSB first.
        root_title = Text("root (built bit-by-bit)", font=th.MONO, font_size=17,
                          color=th.GREEN)
        root_title.next_to(pair_group, DOWN, buff=0.7)

        self.play(FadeIn(root_title), run_time=0.3)

        # Show the recurrence result at each stage.
        stages = [
            ("stage 1:  rem=1,  root=1", th.AMBER),
            ("stage 2:  rem=0,  root=10", th.AMBER),
            ("stage 3:  rem=0,  root=100", th.AMBER),
            ("stage 4:  rem=0,  root=1000", th.GREEN),
        ]
        stage_group = VGroup()
        for s, c in stages:
            stage_group.add(Text(s, font=th.MONO, font_size=18, color=c))
        stage_group.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        stage_group.next_to(root_title, DOWN, buff=0.35)

        for i, st in enumerate(stage_group):
            self.play(FadeIn(st, shift=UP * 0.1), run_time=0.4)
            self.wait(0.25)

        # Final result.
        result = Text("√64 = 8   (remainder 0)", font=th.MONO, weight=BOLD,
                      font_size=24, color=th.GREEN_LIGHT)
        result.next_to(stage_group, DOWN, buff=0.5)
        self.play(FadeIn(result, shift=UP * 0.2), run_time=0.5)
        self.wait(1.2)

        self.play(FadeOut(w_hdr), FadeOut(radicand), FadeOut(pair_group),
                  FadeOut(root_title), FadeOut(stage_group), FadeOut(result),
                  run_time=0.5)

        # =================================================================
        # ACT 4 — RECAP
        # =================================================================
        card = th.card(10.0, 3.7, stroke=th.GREEN, radius=0.22)
        t = Text("rtl/sqrt.sv", font=th.SANS, weight=BOLD, font_size=26,
                 color=th.GREEN_LIGHT)
        t.next_to(card.get_top(), DOWN, buff=0.35)
        pts = th.bullets(
            ["16-bit radicand → 8-bit root (floor) + remainder",
             "Digit recurrence: rem = (rem<<2) | next 2 bits",
             "Trial subtract: if rem ≥ (root<<2 | 1), set bit & subtract",
             "Attention use: 1/√d_k scales logits to unit variance",
             "Next: Lab 06 — Safe Softmax & FlashAttention"],
            font_size=18, buff=0.28, bullet_color=th.GREEN, color=th.TEXT,
        )
        pts.next_to(t, DOWN, buff=0.4, aligned_edge=LEFT)
        pts.move_to(card.get_center() + DOWN * 0.15)
        self.play(Create(card), Write(t), FadeIn(pts, shift=UP * 0.2), run_time=1.1)
        self.wait(2.4)
