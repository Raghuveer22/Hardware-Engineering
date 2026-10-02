"""
Lab 07: Fast Reciprocal Square Root (rsqrt) for RMSNorm

Deep-dive structure:
1.  RMSNorm in modern LLMs (LLaMA 3, Mistral) — every layer.
2.  The bottleneck: sqrt + divide ≈ 30-40 cycles in software.
3.  The hybrid datapath: zero check, seed ROM (small x), digit root
    (large x), Q8.8 reciprocal scaler.
4.  Worked example: rsqrt(64) = 1/8 = 0.125 → 32 in Q8.8.
5.  RTL recap: rtl/rsqrt.sv — single combinational pass.
"""

from manim import *
import theme as th


class Lab07RSQRT(Scene):
    def construct(self):
        th.set_dark(self.camera)

        # =================================================================
        # ACT 1 — RMSNORM MOTIVATION
        # =================================================================
        hdr, _, _ = th.header("LAB 07", "Fast RSQRT for RMSNorm")
        self.play(FadeIn(hdr, shift=DOWN * 0.3), run_time=0.7)

        card = th.card(10.6, 2.6, stroke=th.CYAN, radius=0.18)
        card.move_to(UP * 0.35)

        c1 = Text("RMSNorm(x) = x · rsqrt( (1/d)·Σxᵢ² + ε )",
                  font=th.MONO, weight=BOLD, font_size=21, color=th.GREEN_LIGHT)
        c2 = Text("LLaMA 3, Mistral, DeepSeek: RMSNorm at every layer",
                  font=th.SANS, font_size=18, color=th.TEXT)
        c3 = Text("Software sqrt + divide ≈ 30–40 cycles per token",
                  font=th.MONO, font_size=18, color=th.RED_LIGHT)
        stack = VGroup(c1, c2, c3).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        stack.move_to(card)
        self.play(Create(card), FadeIn(stack), run_time=0.9)
        self.wait(1.0)

        sfx = Text("Silicon SFU: 1/sqrt(x) in ONE combinational pass",
                   font=th.SANS, weight=BOLD, font_size=20, color=th.AMBER_LIGHT)
        sfx.next_to(card, DOWN, buff=0.4)
        self.play(FadeIn(sfx, shift=UP * 0.15), run_time=0.6)
        self.wait(0.8)

        self.play(FadeOut(hdr), FadeOut(card), FadeOut(stack), FadeOut(sfx),
                  run_time=0.5)

        # =================================================================
        # ACT 2 — THE HYBRID DATAPATH
        # =================================================================
        d_hdr, _, _ = th.header("LAB 07", "The Hybrid SFU Datapath")
        self.play(FadeIn(d_hdr, shift=DOWN * 0.3), run_time=0.7)

        # Zero check.
        z = th.card(2.8, 1.0, stroke=th.RED, radius=0.12)
        z.shift(LEFT * 3.6 + UP * 0.5)
        z_t = Text("Zero Detect\nvalid = (x != 0)", font=th.MONO, font_size=14,
                   color=th.RED_LIGHT).move_to(z)

        # Seed ROM.
        rom = th.card(3.0, 1.0, stroke=th.AMBER, radius=0.12)
        rom.shift(RIGHT * 1.6 + UP * 1.1)
        rom_t = Text("Seed ROM\nx ∈ [1,15]", font=th.MONO, font_size=14,
                     color=th.AMBER_LIGHT).move_to(rom)

        # Digit root engine.
        root = th.card(3.0, 1.0, stroke=th.GREEN, radius=0.12)
        root.shift(RIGHT * 1.6 + DOWN * 0.3)
        root_t = Text("Digit Root\nr = floor(√x)", font=th.MONO, font_size=14,
                      color=th.GREEN_LIGHT).move_to(root)

        # Q8.8 scaler.
        scale = th.card(2.8, 1.0, stroke=th.CYAN, radius=0.12)
        scale.shift(RIGHT * 4.7 + DOWN * 0.3)
        scale_t = Text("Q8.8 Scaler\ny = 256 / r", font=th.MONO, font_size=14,
                       color=th.CYAN_LIGHT).move_to(scale)

        a_root = Arrow(root.get_right(), scale.get_left(), buff=0.08, color=th.GREEN)

        diag = VGroup(z, z_t, rom, rom_t, root, root_t, scale, scale_t, a_root)
        self.play(FadeIn(diag), run_time=1.0)
        self.wait(1.0)

        # Pulse through the large-x path.
        pk = th.packet(color=th.GREEN, radius=0.13)
        pk.move_to(root.get_left() + LEFT * 0.5)
        self.play(FadeIn(pk), run_time=0.25)
        self.play(pk.animate.move_to(root), run_time=0.4)
        self.play(pk.animate.move_to(scale).set_color(th.CYAN), run_time=0.4)
        self.play(FadeOut(pk), run_time=0.25)
        self.wait(0.6)

        self.play(FadeOut(d_hdr), FadeOut(diag), run_time=0.5)

        # =================================================================
        # ACT 3 — WORKED EXAMPLE
        # =================================================================
        w_hdr, _, _ = th.header("LAB 07", "Worked Example: rsqrt(64)")
        self.play(FadeIn(w_hdr, shift=DOWN * 0.3), run_time=0.7)

        s1 = Text("1.  digit root:  √64 = 8", font=th.MONO, font_size=21,
                  color=th.GREEN)
        s1.move_to(UP * 1.1)
        self.play(Write(s1), run_time=0.6)

        s2 = Text("2.  reciprocal scale (Q8.8):  256 / 8 = 32",
                  font=th.MONO, font_size=21, color=th.CYAN)
        s2.next_to(s1, DOWN, buff=0.5)
        self.play(Write(s2), run_time=0.6)

        s3 = Text("3.  32 in Q8.8 = 0.125 = 1/8  ✓",
                  font=th.MONO, weight=BOLD, font_size=22, color=th.GREEN_LIGHT)
        s3.next_to(s2, DOWN, buff=0.5)
        self.play(FadeIn(s3, shift=UP * 0.15), run_time=0.6)

        # A few seed-ROM examples for contrast.
        examples = Text(
            "Seed ROM:  x=1 → 256,  x=4 → 128,  x=16 → 64",
            font=th.MONO, font_size=17, color=th.MUTED,
        )
        examples.next_to(s3, DOWN, buff=0.5)
        self.play(FadeIn(examples), run_time=0.5)
        self.wait(1.2)

        self.play(FadeOut(w_hdr), FadeOut(s1), FadeOut(s2), FadeOut(s3),
                  FadeOut(examples), run_time=0.5)

        # =================================================================
        # ACT 3b — THE SEED-ROM PATH: rsqrt(4)
        # =================================================================
        w2_hdr, _, _ = th.header("LAB 07", "Small x: The Seed ROM Path")
        self.play(FadeIn(w2_hdr, shift=DOWN * 0.3), run_time=0.7)

        s1b = Text("x = 4  →  exact ROM entry (no root engine)",
                   font=th.MONO, font_size=20, color=th.AMBER_LIGHT)
        s1b.move_to(UP * 0.9)
        self.play(Write(s1b), run_time=0.6)

        s2b = Text("1/√4 = 0.5  →  128 in Q8.8", font=th.MONO, weight=BOLD,
                   font_size=22, color=th.GREEN_LIGHT)
        s2b.next_to(s1b, DOWN, buff=0.5)
        self.play(FadeIn(s2b, shift=UP * 0.15), run_time=0.6)

        # Show a tiny ROM table.
        rom = th.card(6.4, 1.7, stroke=th.AMBER, radius=0.14)
        rom.next_to(s2b, DOWN, buff=0.6)
        rom_rows = VGroup(
            Text("x=1 → 256", font=th.MONO, font_size=16, color=th.TEXT),
            Text("x=2 → 181", font=th.MONO, font_size=16, color=th.TEXT),
            Text("x=4 → 128", font=th.MONO, font_size=16, color=th.GREEN_LIGHT),
            Text("x=9 → 85", font=th.MONO, font_size=16, color=th.TEXT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        rom_rows.move_to(rom)
        self.play(Create(rom), FadeIn(rom_rows), run_time=0.7)
        self.wait(1.0)

        self.play(FadeOut(w2_hdr), FadeOut(s1b), FadeOut(s2b), FadeOut(rom),
                  FadeOut(rom_rows), run_time=0.5)

        # =================================================================
        # CHECKPOINT
        # =================================================================
        th.checkpoint(
            self,
            "Why keep a seed ROM for small x instead of one engine?",
            ["Small variances (x < 16) are where gradients are most sensitive",
             "Exact ROM entries preserve precision exactly there"],
        )

        # =================================================================
        # CHALLENGE
        # =================================================================
        th.challenge(
            self,
            ["What is rsqrt(256) in Q8.8 fixed point?",
             "(1/sqrt(256) × 256)"],
            "1/sqrt(256) = 1/16 = 0.0625 → 0.0625 × 256 = 16.",
        )

        # =================================================================
        # ACT 4 — RECAP
        # =================================================================
        th.recap(
            self,
            "rtl/rsqrt.sv",
            ["Zero check sets valid_out=0 (divide-by-zero guard)",
             "Small x → 16-entry seed ROM; large x → digit root",
             "Q8.8 reciprocal scaler: y = 256 / r",
             "~4.6 ns path replaces ~30-cycle software loops",
             "Next: Lab 08 — Exponential SFU for SwiGLU / SiLU"],
        )
