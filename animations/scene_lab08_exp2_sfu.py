"""
Lab 08: Hardware Exponential SFU (2^x & e^x) for SwiGLU
Explains:
1. Why SwiGLU and SiLU dominate >60% of modern LLM compute.
2. The Silicon Base-2 Trick: e^x = 2^(x * log2(e)) = 2^I * 2^F.
3. Barrel Shifter (2^I) + 16-Entry LUT (2^F) Datapath.
"""

from manim import *

class Lab08ExponentialSFU(Scene):
    def construct(self):
        self.camera.background_color = "#0f172a"

        # -----------------------------------------------------------
        # SCENE 1: THE SWIGLU / SILU ACTIVATION CHALLENGE
        # -----------------------------------------------------------
        badge = Text("LAB 08: TRANSFORMER SFUS", font="Arial", weight=BOLD, font_size=20, color="#38bdf8")
        title = Text("Hardware Exponential SFU for SwiGLU & SiLU", font="Arial", weight=BOLD, font_size=30, color=WHITE)
        header = VGroup(badge, title).arrange(DOWN, buff=0.2).to_edge(UP, buff=0.6)

        self.play(FadeIn(header, shift=DOWN * 0.3), run_time=0.8)

        card = RoundedRectangle(corner_radius=0.2, height=2.2, width=10.5, stroke_color="#f59e0b", fill_color="#1e293b", fill_opacity=0.95)
        card.move_to(UP * 0.2)

        s1 = Text("In LLaMA 3 & Mistral, >60% of FLOPs are in SwiGLU FFN layers:", font="Arial", weight=BOLD, font_size=19, color=WHITE)
        s2 = Text("SiLU(x) = x / (1 + e^(-x))", font="Courier", weight=BOLD, font_size=20, color="#38bdf8")
        s3 = Text("🚨 Computing e^x via Taylor Series requires multi-cycle DSP stalls!", font="Courier", font_size=17, color="#ef4444")
        s4 = Text("⚡ Hardware Solution: Base-2 Mathematical Decomposition!", font="Arial", weight=BOLD, font_size=18, color="#4ade80")

        s_stack = VGroup(s1, s2, s3, s4).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(card)

        self.play(Create(card), FadeIn(s_stack), run_time=1.0)
        self.wait(1.8)

        self.play(FadeOut(header), FadeOut(card), FadeOut(s_stack), run_time=0.5)

        # -----------------------------------------------------------
        # SCENE 2: THE BASE-2 DECOMPOSITION FORMULA
        # -----------------------------------------------------------
        f_title = Text("The Base-2 Silicon Secret: e^x = 2^I × 2^F", font="Arial", weight=BOLD, font_size=28, color="#4ade80")
        f_title.to_edge(UP, buff=0.6)
        self.play(Write(f_title), run_time=0.6)

        decomp_card = RoundedRectangle(corner_radius=0.2, height=2.4, width=10.0, stroke_color="#38bdf8", fill_color="#1e293b", fill_opacity=0.9)
        decomp_card.move_to(UP * 0.3)

        d1 = Text("Step 1: Scale by log2(e) ➔  u = x × 1.442695", font="Courier", weight=BOLD, font_size=20, color="#38bdf8")
        d2 = Text("Step 2: Split u into Integer (I) + Fractional (F in [0, 1))", font="Courier", weight=BOLD, font_size=18, color="#f59e0b")
        d3 = Text("• 2^I  ➔  Evaluated via zero-delay hardware Barrel Shifter!", font="Arial", font_size=18, color="#4ade80")
        d4 = Text("• 2^F  ➔  Evaluated via compact 16-entry seed lookup table (LUT)!", font="Arial", font_size=18, color="#86efac")

        d_grp = VGroup(d1, d2, d3, d4).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(decomp_card)

        self.play(Create(decomp_card), FadeIn(d_grp), run_time=1.0)
        self.wait(2.0)

        self.play(FadeOut(f_title), FadeOut(decomp_card), FadeOut(d_grp), run_time=0.5)

        # -----------------------------------------------------------
        # SCENE 3: HARDWARE DATAPATH: rtl/exp2_sfu.sv
        # -----------------------------------------------------------
        dp_title = Text("Exponential SFU Datapath: rtl/exp2_sfu.sv", font="Arial", weight=BOLD, font_size=28, color="#38bdf8")
        dp_title.to_edge(UP, buff=0.6)
        self.play(Write(dp_title), run_time=0.6)

        # Datapath nodes
        scaler_node = RoundedRectangle(corner_radius=0.15, height=1.2, width=2.6, stroke_color="#f59e0b", fill_color="#1e293b", fill_opacity=0.9).shift(LEFT * 4.2)
        sc_lbl = Text("Mode Selector\nu = x * log2(e)", font="Arial", font_size=14, color=WHITE).move_to(scaler_node)

        split_node = RoundedRectangle(corner_radius=0.15, height=1.2, width=2.4, stroke_color="#38bdf8", fill_color="#1e293b", fill_opacity=0.9).shift(LEFT * 1.4)
        sp_lbl = Text("Decompose\nu = I + F", font="Arial", font_size=15, color=WHITE).move_to(split_node)

        shifter_node = RoundedRectangle(corner_radius=0.15, height=1.0, width=2.4, stroke_color="#4ade80", fill_color="#1e293b", fill_opacity=0.9).shift(RIGHT * 1.6 + UP * 0.8)
        sh_lbl = Text("Barrel Shifter\n(2^I)", font="Arial", font_size=14, color=WHITE).move_to(shifter_node)

        lut_node = RoundedRectangle(corner_radius=0.15, height=1.0, width=2.4, stroke_color="#a855f7", fill_color="#1e293b", fill_opacity=0.9).shift(RIGHT * 1.6 + DOWN * 0.8)
        lu_lbl = Text("16-Entry LUT\n(2^F)", font="Arial", font_size=14, color=WHITE).move_to(lut_node)

        comb_node = RoundedRectangle(corner_radius=0.15, height=1.2, width=2.2, stroke_color="#4ade80", fill_color="#1e293b", fill_opacity=0.9).shift(RIGHT * 4.4)
        co_lbl = Text("Multiplier\ny = 2^I * 2^F", font="Arial", font_size=14, color=WHITE).move_to(comb_node)

        a1 = Arrow(start=scaler_node.get_right(), end=split_node.get_left(), buff=0.08, color="#94a3b8")
        a_up = Arrow(start=split_node.get_right(), end=shifter_node.get_left(), buff=0.08, color="#4ade80")
        a_dn = Arrow(start=split_node.get_right(), end=lut_node.get_left(), buff=0.08, color="#a855f7")
        a_c1 = Arrow(start=shifter_node.get_right(), end=comb_node.get_left() + UP * 0.3, buff=0.08, color="#4ade80")
        a_c2 = Arrow(start=lut_node.get_right(), end=comb_node.get_left() + DOWN * 0.3, buff=0.08, color="#a855f7")

        nodes = VGroup(scaler_node, sc_lbl, split_node, sp_lbl, shifter_node, sh_lbl,
                       lut_node, lu_lbl, comb_node, co_lbl, a1, a_up, a_dn, a_c1, a_c2)

        self.play(FadeIn(nodes), run_time=1.2)
        self.wait(1.5)

        # Summary
        summary_card = RoundedRectangle(corner_radius=0.2, height=1.4, width=10.0, stroke_color="#4ade80", fill_color="#1e293b", fill_opacity=0.95)
        summary_card.to_edge(DOWN, buff=0.5)
        s_msg = Text("✓ Hardware Speedup: Replaces 40-cycle software loops with ~3.2 ns combinational logic!\n🎓 You have mastered the entire Silicon AI Acceleration Architecture!", font="Arial", weight=BOLD, font_size=16, color="#86efac").move_to(summary_card)

        self.play(Create(summary_card), Write(s_msg), run_time=0.8)
        self.wait(2.5)
