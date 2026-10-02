"""
Lab 07: Fast Reciprocal Square Root (rsqrt) SFU for RMSNorm
Explains:
1. Why LLaMA 3 and modern LLMs use RMSNorm instead of LayerNorm.
2. The 30-cycle software division bottleneck.
3. The Hardware SFU: Seed ROM + Digit-by-Digit Root + Q8.8 fixed-point scaling.
"""

from manim import *

class Lab07RSQRT(Scene):
    def construct(self):
        self.camera.background_color = "#0f172a"

        # -----------------------------------------------------------
        # SCENE 1: THE LLM MOTIVATION (RMSNorm in LLaMA 3)
        # -----------------------------------------------------------
        badge = Text("LAB 07: TRANSFORMER SFUS", font="Arial", weight=BOLD, font_size=20, color="#38bdf8")
        title = Text("Fast Reciprocal Square Root (rsqrt) for RMSNorm", font="Arial", weight=BOLD, font_size=30, color=WHITE)
        header = VGroup(badge, title).arrange(DOWN, buff=0.2).to_edge(UP, buff=0.6)

        self.play(FadeIn(header, shift=DOWN * 0.3), run_time=0.8)

        card = RoundedRectangle(corner_radius=0.2, height=2.2, width=10.5, stroke_color="#38bdf8", fill_color="#1e293b", fill_opacity=0.95)
        card.move_to(UP * 0.2)

        c1 = Text("LLaMA 3, Mistral, and DeepSeek use RMSNorm at EVERY layer:", font="Arial", weight=BOLD, font_size=19, color=WHITE)
        c2 = Text("RMSNorm(x) = x * rsqrt( (1/d) * sum(x_i^2) + eps )", font="Courier", weight=BOLD, font_size=20, color="#4ade80")
        c3 = Text("🚨 In CPU/Software: Square root + Division takes ~30-40 clock cycles!", font="Courier", font_size=17, color="#ef4444")
        c4 = Text("⚡ In Silicon SFU: Computes 1 / sqrt(x) in a single combinational pass!", font="Arial", weight=BOLD, font_size=18, color="#f59e0b")

        c_group = VGroup(c1, c2, c3, c4).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(card)

        self.play(Create(card), FadeIn(c_group), run_time=1.0)
        self.wait(1.8)

        self.play(FadeOut(header), FadeOut(card), FadeOut(c_group), run_time=0.5)

        # -----------------------------------------------------------
        # SCENE 2: HYBRID HARDWARE DATAPATH
        # -----------------------------------------------------------
        dp_title = Text("Hybrid SFU Datapath: rtl/rsqrt.sv", font="Arial", weight=BOLD, font_size=28, color="#38bdf8")
        dp_title.to_edge(UP, buff=0.6)
        self.play(Write(dp_title), run_time=0.6)

        # Zero check
        zero_box = RoundedRectangle(corner_radius=0.15, height=1.0, width=3.2, stroke_color="#ef4444", fill_color="#1e293b", fill_opacity=0.9).shift(LEFT * 3.6 + UP * 0.6)
        z_txt = Text("Zero Detector\nvalid_out = (x != 0)", font="Courier", font_size=14, color="#f87171").move_to(zero_box)

        # Small x ROM
        rom_box = RoundedRectangle(corner_radius=0.15, height=1.0, width=3.4, stroke_color="#f59e0b", fill_color="#1e293b", fill_opacity=0.9).shift(RIGHT * 1.5 + UP * 1.1)
        rom_txt = Text("Small x in [1, 15]\n16-Entry Seed ROM", font="Arial", font_size=14, color="#fde68a").move_to(rom_box)

        # Large x Root Engine
        root_box = RoundedRectangle(corner_radius=0.15, height=1.0, width=3.4, stroke_color="#4ade80", fill_color="#1e293b", fill_opacity=0.9).shift(RIGHT * 1.5 + DOWN * 0.3)
        root_txt = Text("Large x >= 16\nDigit Root: r = floor(sqrt(x))", font="Arial", font_size=14, color="#86efac").move_to(root_box)

        # Q8.8 Scaler
        scaler_box = RoundedRectangle(corner_radius=0.15, height=1.0, width=2.8, stroke_color="#38bdf8", fill_color="#1e293b", fill_opacity=0.9).shift(RIGHT * 4.6 + DOWN * 0.3)
        sc_txt = Text("Q8.8 Scaler\ny = 256 / r", font="Courier", weight=BOLD, font_size=15, color="#38bdf8").move_to(scaler_box)

        arrow_root = Arrow(start=root_box.get_right(), end=scaler_box.get_left(), buff=0.08, color="#4ade80")

        diag = VGroup(zero_box, z_txt, rom_box, rom_txt, root_box, root_txt, scaler_box, sc_txt, arrow_root)

        self.play(FadeIn(diag), run_time=1.2)
        self.wait(1.5)

        # Takeaway
        summary_card = RoundedRectangle(corner_radius=0.2, height=1.5, width=10.0, stroke_color="#4ade80", fill_color="#1e293b", fill_opacity=0.95)
        summary_card.to_edge(DOWN, buff=0.5)
        t1 = Text("✓ Path Delay: ~4.6 ns (Zero-Cycle Combinational Throughput)", font="Arial", font_size=18, color=WHITE)
        t2 = Text("Next Lab: The Hardware Exponential SFU (2^x and e^x) for SwiGLU!", font="Arial", weight=BOLD, font_size=19, color="#f59e0b")
        s_grp = VGroup(t1, t2).arrange(DOWN, buff=0.2).move_to(summary_card)

        self.play(Create(summary_card), FadeIn(s_grp), run_time=0.8)
        self.wait(2.2)
