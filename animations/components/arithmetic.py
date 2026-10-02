"""
Hardware AI Acceleration - Arithmetic Intuition Engine
Provides physical silicon metaphors: the 2's complement speedometer wheel,
mechanical spring saturation clamp, and dynamic accumulator fluid tanks.
"""

from manim import *
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import theme as th
from components.layout import HardwareConfig


class TwosComplementWheel(VGroup):
    """
    Parametric Two's Complement Speedometer Dial.
    Visually exposes why positive addition wraps into negative numbers
    and demonstrates physical saturation clamping at the +127 boundary.
    """
    def __init__(self, bits=8, radius=2.3, **kwargs):
        super().__init__(**kwargs)
        self.bits = bits
        self.config = HardwareConfig(data_width=bits)
        self.radius = radius

        # Outer circular dial
        # Top = 0 (12 o'clock = angle PI/2 in standard trig)
        # Clockwise progression: 0 -> +127 at bottom (6 o'clock), then -128 -> -1
        self.positive_arc = Arc(
            radius=radius,
            start_angle=np.pi / 2,
            angle=-np.pi,
            color=th.GREEN,
            stroke_width=4.0
        )
        self.negative_arc = Arc(
            radius=radius,
            start_angle=-np.pi / 2,
            angle=-np.pi,
            color=th.RED,
            stroke_width=4.0
        )
        self.dial_frame = Circle(
            radius=radius + 0.15,
            color=th.BORDER,
            stroke_width=1.5
        )
        self.center_hub = Dot(ORIGIN, radius=0.15, color=th.TEXT)

        # Cardinal Tick Labels
        self.ticks = VGroup()
        label_configs = [
            (0, np.pi / 2, "0", th.TEXT),
            (self.config.max_val // 2, np.pi / 4, f"+{self.config.max_val // 2}", th.GREEN_LIGHT),
            (self.config.max_val, -np.pi / 2 + 0.15, f"+{self.config.max_val}", th.GREEN),
            (self.config.min_val, -np.pi / 2 - 0.15, f"{self.config.min_val}", th.RED),
            (self.config.min_val // 2, -3 * np.pi / 4, f"{self.config.min_val // 2}", th.RED_LIGHT),
        ]
        for val, angle, lbl_str, col in label_configs:
            pos = np.array([np.cos(angle), np.sin(angle), 0]) * (radius + 0.5)
            t = Text(lbl_str, font=th.MONO, weight=BOLD, font_size=th.FONT_TINY, color=col)
            t.move_to(pos)
            self.ticks.add(t)

        # Danger zone marker at the 6 o'clock boundary
        discontinuity_line = DashedLine(
            DOWN * (radius - 0.3),
            DOWN * (radius + 0.3),
            color=th.AMBER,
            stroke_width=2.5
        )
        disc_label = Text("OVERFLOW DISCONTINUITY", font=th.MONO, font_size=th.FONT_MICRO, color=th.AMBER)
        disc_label.next_to(discontinuity_line, DOWN, buff=0.15)
        self.discontinuity_marker = VGroup(discontinuity_line, disc_label)

        # Needle pointer
        self.current_val = 0
        self.needle = Arrow(
            start=ORIGIN,
            end=UP * (radius * 0.8),
            buff=0,
            color=th.CYAN,
            stroke_width=4.0,
            max_tip_length_to_length_ratio=0.18
        )

        # Value readout HUD below center
        self.readout_dec = Text("Decimal: +0", font=th.MONO, weight=BOLD,
                                font_size=th.FONT_CAPTION, color=th.CYAN_LIGHT)
        self.readout_bin = Text("Binary:  00000000", font=th.MONO,
                                font_size=th.FONT_TINY, color=th.MUTED)
        self.readout_group = VGroup(self.readout_dec, self.readout_bin).arrange(DOWN, buff=0.1)
        self.readout_group.move_to(DOWN * (radius * 0.4))

        # Clamp barrier (hidden by default)
        self.clamp_bar = Rectangle(
            width=0.6,
            height=0.15,
            fill_color=th.AMBER,
            fill_opacity=1.0,
            stroke_color=th.WHITE,
            stroke_width=2.0
        )
        self.clamp_bar.move_to(DOWN * (radius - 0.05) + RIGHT * 0.15)
        self.clamp_label = Text("SATURATION CLAMP (+127)", font=th.MONO, weight=BOLD,
                                font_size=th.FONT_MICRO, color=th.AMBER)
        self.clamp_label.next_to(self.clamp_bar, RIGHT, buff=0.15)
        self.clamp_unit = VGroup(self.clamp_bar, self.clamp_label)
        self.clamp_active = False

        self.add(
            self.dial_frame, self.positive_arc, self.negative_arc,
            self.center_hub, self.ticks, self.discontinuity_marker,
            self.needle, self.readout_group
        )

    def val_to_angle(self, val):
        """Maps signed integer to dial angle (top=0, clockwise)."""
        # 0 -> PI/2
        # +127 -> -PI/2 + epsilon (bottom right)
        # -128 -> -PI/2 - epsilon (bottom left)
        # -1 -> PI/2 + delta (top left)
        if val >= 0:
            frac = val / (self.config.max_val + 1)
            return (np.pi / 2) - (frac * np.pi)
        else:
            # val in [-128, -1]
            frac = (val - self.config.min_val) / abs(self.config.min_val)
            return (-np.pi / 2) - (frac * np.pi)

    def set_value_instant(self, val):
        """Immediately snaps needle and readout to val."""
        self.current_val = val
        angle = self.val_to_angle(val)
        target_pt = np.array([np.cos(angle), np.sin(angle), 0]) * (self.radius * 0.8)
        self.needle.put_start_and_end_on(ORIGIN, target_pt)
        col = th.GREEN_LIGHT if val >= 0 else th.RED
        self.readout_dec.become(
            Text(f"Decimal: {val:+d}", font=th.MONO, weight=BOLD,
                 font_size=th.FONT_CAPTION, color=col).move_to(self.readout_dec)
        )
        self.readout_bin.become(
            Text(f"Binary:  {self.config.to_signed_bin(val)}", font=th.MONO,
                 font_size=th.FONT_TINY, color=th.MUTED).move_to(self.readout_bin)
        )

    def animate_sweep(self, scene, target_val, run_time=th.RATE_NORMAL, clamp=False):
        """
        Smoothly sweeps the needle across the dial.
        If clamp=True, stops at +127 and emits an elastic clamp bounce.
        """
        start_val = self.current_val
        is_overflow = (target_val > self.config.max_val) and not clamp
        final_val = min(self.config.max_val, target_val) if clamp else (
            ((target_val + 128) % 256) - 128 if target_val > self.config.max_val else target_val
        )

        # Animate continuous intermediate steps
        steps = 30
        val_path = np.linspace(start_val, target_val, steps)
        dt = run_time / steps

        for v in val_path:
            int_v = int(round(v))
            if clamp and int_v >= self.config.max_val:
                self.set_value_instant(self.config.max_val)
                scene.wait(dt)
                break
            elif not clamp and int_v > self.config.max_val:
                # Wrapped around!
                wrapped = ((int_v + 128) % 256) - 128
                self.set_value_instant(wrapped)
            else:
                self.set_value_instant(int_v)
            scene.wait(dt)

        self.set_value_instant(final_val)

    def deploy_clamp_barrier(self, scene):
        """Drops the mechanical saturation clamp barrier into place."""
        self.clamp_active = True
        scene.play(
            FadeIn(self.clamp_unit, shift=DOWN * 0.4),
            run_time=th.RATE_FAST,
            rate_func=rate_functions.ease_out_bounce
        )


class FullAdderGateSchematic(VGroup):
    """
    1-Bit Full Adder Gate-Level Schematic.
    Draws logic gates: XOR-1, XOR-2, AND-1, AND-2, OR-1.
    Demonstrates Sum = A ^ B ^ Cin and Cout = (A & B) | (Cin & (A ^ B)).
    """
    def __init__(self, width=7.2, height=3.6, **kwargs):
        super().__init__(**kwargs)
        self.box = RoundedRectangle(
            corner_radius=0.18, width=width, height=height,
            stroke_color=th.CYAN, stroke_width=2.0,
            fill_color=th.CARD, fill_opacity=0.95
        )
        self.title = Text("1-BIT FULL ADDER (FA)", font=th.SANS, weight=BOLD,
                          font_size=th.FONT_BADGE, color=th.CYAN_LIGHT)
        self.title.next_to(self.box.get_top(), DOWN, buff=0.18)

        # Gate representations
        xor1 = RoundedRectangle(width=1.3, height=0.6, corner_radius=0.1, color=th.CYAN, fill_color=th.BG, fill_opacity=0.8)
        xor1_lbl = Text("XOR", font=th.MONO, font_size=11, color=th.CYAN).move_to(xor1)
        self.xor1_grp = VGroup(xor1, xor1_lbl).move_to(self.box.get_center() + LEFT * 1.5 + UP * 0.6)

        xor2 = RoundedRectangle(width=1.3, height=0.6, corner_radius=0.1, color=th.GREEN, fill_color=th.BG, fill_opacity=0.8)
        xor2_lbl = Text("XOR", font=th.MONO, font_size=11, color=th.GREEN).move_to(xor2)
        self.xor2_grp = VGroup(xor2, xor2_lbl).move_to(self.box.get_center() + RIGHT * 1.4 + UP * 0.6)

        and1 = RoundedRectangle(width=1.3, height=0.55, corner_radius=0.1, color=th.AMBER, fill_color=th.BG, fill_opacity=0.8)
        and1_lbl = Text("AND", font=th.MONO, font_size=11, color=th.AMBER).move_to(and1)
        self.and1_grp = VGroup(and1, and1_lbl).move_to(self.box.get_center() + LEFT * 1.5 + DOWN * 0.7)

        and2 = RoundedRectangle(width=1.3, height=0.55, corner_radius=0.1, color=th.AMBER, fill_color=th.BG, fill_opacity=0.8)
        and2_lbl = Text("AND", font=th.MONO, font_size=11, color=th.AMBER).move_to(and2)
        self.and2_grp = VGroup(and2, and2_lbl).move_to(self.box.get_center() + RIGHT * 0.0 + DOWN * 0.4)

        or1 = RoundedRectangle(width=1.3, height=0.55, corner_radius=0.1, color=th.RED, fill_color=th.BG, fill_opacity=0.8)
        or1_lbl = Text("OR", font=th.MONO, font_size=11, color=th.RED).move_to(or1)
        self.or1_grp = VGroup(or1, or1_lbl).move_to(self.box.get_center() + RIGHT * 1.8 + DOWN * 0.7)

        # Pins
        self.pin_a = Text("A", font=th.MONO, weight=BOLD, font_size=13, color=th.TEXT).next_to(self.box.get_left(), RIGHT, buff=0.15).shift(UP * 0.9)
        self.pin_b = Text("B", font=th.MONO, weight=BOLD, font_size=13, color=th.TEXT).next_to(self.box.get_left(), RIGHT, buff=0.15).shift(UP * 0.4)
        self.pin_cin = Text("Cin", font=th.MONO, weight=BOLD, font_size=13, color=th.CYAN_LIGHT).next_to(self.box.get_left(), RIGHT, buff=0.15).shift(DOWN * 0.6)

        self.pin_sum = Text("Sum = A ⊕ B ⊕ Cin", font=th.MONO, weight=BOLD, font_size=12, color=th.GREEN_LIGHT).next_to(self.box.get_right(), LEFT, buff=0.15).shift(UP * 0.6)
        self.pin_cout = Text("Cout = (A·B) + Cin(A⊕B)", font=th.MONO, weight=BOLD, font_size=11, color=th.AMBER_LIGHT).next_to(self.box.get_right(), LEFT, buff=0.15).shift(DOWN * 0.7)

        self.add(
            self.box, self.title,
            self.xor1_grp, self.xor2_grp, self.and1_grp, self.and2_grp, self.or1_grp,
            self.pin_a, self.pin_b, self.pin_cin, self.pin_sum, self.pin_cout
        )


class RippleCarryChain(VGroup):
    """
    8-Bit Ripple Carry Adder Cascade.
    Shows FA[0] through FA[7] with carry bit rippling horizontally.
    Exposes propagation delay (t_pd) across 8 bit slices.
    """
    def __init__(self, bits=8, width=11.2, height=1.6, **kwargs):
        super().__init__(**kwargs)
        self.bits = bits
        self.cells = VGroup()
        self.carry_wires = VGroup()

        cell_w = (width - (bits - 1) * 0.18) / bits
        cell_h = height

        for i in range(bits):
            # i=0 on right (LSB), i=7 on left (MSB)
            c_box = RoundedRectangle(
                corner_radius=0.1, width=cell_w, height=cell_h,
                stroke_color=th.CYAN if i < 7 else th.RED,
                stroke_width=1.5, fill_color=th.CARD, fill_opacity=0.9
            )
            lbl = Text(f"FA {i}", font=th.MONO, weight=BOLD, font_size=12, color=th.TEXT).move_to(c_box.get_center() + UP * 0.3)
            sub = Text(f"2^{i}", font=th.MONO, font_size=10, color=th.MUTED).next_to(lbl, DOWN, buff=0.08)
            grp = VGroup(c_box, lbl, sub)
            self.cells.add(grp)

        self.cells.arrange(LEFT, buff=0.18)

        # Wire connections between FAs (carry propagation right-to-left)
        for i in range(bits - 1):
            fa_curr = self.cells[i]
            fa_next = self.cells[i + 1]
            arrow = Arrow(
                fa_curr.get_left(), fa_next.get_right(),
                buff=0.02, color=th.AMBER, stroke_width=2.0, max_tip_length_to_length_ratio=0.25
            )
            self.carry_wires.add(arrow)

        # Cin arrow into FA 0 (rightmost)
        fa0 = self.cells[0]
        cin_arrow = Arrow(fa0.get_right() + RIGHT * 0.6, fa0.get_right(), buff=0.02, color=th.GREEN, stroke_width=2.0)
        cin_lbl = Text("Cin=0", font=th.MONO, font_size=10, color=th.GREEN).next_to(cin_arrow, UP, buff=0.06)
        self.cin_grp = VGroup(cin_arrow, cin_lbl)

        # Cout arrow out of FA 7 (leftmost)
        fa7 = self.cells[-1]
        cout_arrow = Arrow(fa7.get_left(), fa7.get_left() + LEFT * 0.7, buff=0.02, color=th.RED, stroke_width=2.0)
        cout_lbl = Text("Cout", font=th.MONO, font_size=10, color=th.RED).next_to(cout_arrow, UP, buff=0.06)
        self.cout_grp = VGroup(cout_arrow, cout_lbl)

        self.add(self.cells, self.carry_wires, self.cin_grp, self.cout_grp)

    def animate_ripple(self, scene, run_time=1.8):
        """Animates carry token rippling from FA 0 to FA 7."""
        dot = Dot(self.cin_grp[0].get_start(), radius=0.08, color=th.AMBER_LIGHT)
        scene.play(FadeIn(dot), run_time=0.15)
        path_pts = [self.cin_grp[0].get_start(), self.cells[0].get_center()]
        for i in range(self.bits - 1):
            path_pts.append(self.carry_wires[i].get_start())
            path_pts.append(self.carry_wires[i].get_end())
            path_pts.append(self.cells[i + 1].get_center())
        path_pts.append(self.cout_grp[0].get_end())

        for pt in path_pts:
            scene.play(dot.animate.move_to(pt), run_time=run_time / len(path_pts), rate_func=linear)
        scene.play(FadeOut(dot), run_time=0.15)


class AccumulatorGauge(VGroup):
    """
    Visual Dynamic Accumulator Fluid Gauge.
    Demonstrates bit growth: 16-bit multiplier output accumulating into 32-bit register.
    Shows the headroom threshold before overflow.
    """
    def __init__(self, width=2.4, height=4.2, **kwargs):
        super().__init__(**kwargs)
        self.tank = RoundedRectangle(
            corner_radius=0.15, width=width, height=height,
            stroke_color=th.BORDER, stroke_width=2.5,
            fill_color=th.CARD, fill_opacity=0.6
        )
        self.fluid = Rectangle(
            width=width - 0.2, height=0.4,
            fill_color=th.CYAN, fill_opacity=0.7, stroke_width=0
        )
        self.fluid.align_to(self.tank, DOWN).shift(UP * 0.1)

        # Capacity markers
        self.markers = VGroup()
        levels = [
            ("32-bit MAX", 0.90, th.RED),
            ("28-bit (K=4096)", 0.65, th.AMBER),
            ("20-bit (K=16)", 0.35, th.GREEN_LIGHT),
            ("16-bit Multiplier", 0.15, th.CYAN_LIGHT),
        ]
        for name, frac, col in levels:
            y_pos = self.tank.get_bottom()[1] + frac * height
            line = DashedLine(
                [self.tank.get_left()[0], y_pos, 0],
                [self.tank.get_right()[0], y_pos, 0],
                color=col, stroke_width=1.5
            )
            t = Text(name, font=th.MONO, font_size=9, color=col)
            t.next_to(line, RIGHT, buff=0.12)
            self.markers.add(VGroup(line, t))

        title = Text("32-BIT ACCUMULATOR", font=th.MONO, weight=BOLD, font_size=11, color=th.TEXT)
        title.next_to(self.tank, UP, buff=0.15)
        self.add(self.tank, self.fluid, self.markers, title)

    def set_fluid_level(self, scene, frac, color=None, run_time=0.6):
        """Animates fluid filling up the tank to fraction frac in [0, 1]."""
        new_h = max(0.1, (self.tank.height - 0.2) * frac)
        new_fluid = Rectangle(
            width=self.tank.width - 0.2, height=new_h,
            fill_color=color if color else self.fluid.fill_color, fill_opacity=0.8, stroke_width=0
        )
        new_fluid.align_to(self.tank, DOWN).shift(UP * 0.1)
        scene.play(Transform(self.fluid, new_fluid), run_time=run_time)

