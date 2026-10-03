"""
Hardware AI Acceleration - Silicon Standard Cells & Component Library
Provides modular, encapsulated hardware primitives for broadcast-quality chip visualizations.
"""

from manim import *
import numpy as np
import sys
from pathlib import Path

ANIM_DIR = Path(__file__).resolve().parent.parent
if str(ANIM_DIR) not in sys.path:
    sys.path.insert(0, str(ANIM_DIR))

import theme as th
from components.layout import TextRole, SemanticText, HStack, VStack, ConstraintAnchor, fit_to_bounds


class PinProbe(VGroup):
    """
    Live signal probe badge pinned to an input/output wire or pin port.
    Displays dynamic hex/signed signal states without hardcoded coordinates.
    """
    def __init__(self, label: str, value: str = "", color=th.CYAN,
                 direction=UP, **kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.direction = direction

        self.lbl = SemanticText(label, role=TextRole.PROBE_LABEL, color=color)
        elements = [self.lbl]

        if value:
            self.val = SemanticText(value, role=TextRole.BUS_VALUE, color=th.WHITE)
            elements.append(self.val)
        else:
            self.val = None

        content = HStack(*elements, gap=th.SPACE_XS)
        self.badge_bg = RoundedRectangle(
            corner_radius=0.08,
            width=content.width + 0.3,
            height=content.height + 0.18,
            stroke_color=color,
            stroke_width=1.2,
            fill_color="#080f1d",
            fill_opacity=0.92
        )
        content.move_to(self.badge_bg)
        self.add(self.badge_bg, content)
        self.content = content

    def attach_to_port(self, target_mob, edge=UP, gap=th.SPACE_SM):
        """Docks probe directly adjacent to a pin port or wire."""
        ConstraintAnchor.dock_to(self, target_mob, edge=edge, gap=gap)
        return self

    def set_value(self, new_val_str: str, new_color=None):
        """Returns animation to update probe reading."""
        col = new_color if new_color is not None else self.color
        if self.val:
            anim = self.val.update_text(new_val_str)
        else:
            self.val = SemanticText(new_val_str, role=TextRole.BUS_VALUE, color=th.WHITE)
            self.content.add(self.val)
            self.content.relayout()
            anim = FadeIn(self.val)
        return anim


class DieFootprint(VGroup):
    """
    Parameterized silicon die standard-cell footprint.
    Visualizes relative chip area scaling, gate count, and thermal switching glow.
    """
    def __init__(self, title: str, gates: int, width=3.2, height=3.2,
                 color=th.CYAN, fill_color="#091424", **kwargs):
        super().__init__(**kwargs)
        self.die_width = width
        self.die_height = height
        self.base_color = color
        self.gates = gates

        # Die boundary ring
        self.chassis = RoundedRectangle(
            corner_radius=0.14,
            width=width,
            height=height,
            stroke_color=color,
            stroke_width=2.0,
            fill_color=fill_color,
            fill_opacity=0.92
        )

        # Header tag
        self.header = SemanticText(title, role=TextRole.BLOCK_HEADER, color=color)
        self.header.next_to(self.chassis.get_top(), DOWN, buff=0.18)
        fit_to_bounds(self.header, max_width=width - 0.4)

        # Gate count metric
        self.gate_lbl = SemanticText(f"{gates:,} GATES", role=TextRole.BUS_VALUE, color=th.WHITE)
        self.gate_lbl.next_to(self.header, DOWN, buff=0.1)

        # Silicon wafer texture grid
        n_dots = int(np.clip(int(np.sqrt(gates / 12)), 3, 6))
        self.dots = VGroup(*[
            Square(
                side_length=0.22,
                stroke_color=color,
                stroke_width=0.8,
                fill_color=color,
                fill_opacity=0.35
            )
            for _ in range(n_dots * n_dots)
        ]).arrange_in_grid(rows=n_dots, cols=n_dots, buff=0.08)
        self.dots.move_to(self.chassis.get_center() + DOWN * 0.35)

        self.add(self.chassis, self.header, self.gate_lbl, self.dots)

    def thermal_glow(self, color=th.RED, scale_factor=1.12):
        """Returns animation to trigger a thermal switching surge with expanded boundary."""
        return AnimationGroup(
            self.chassis.animate.scale(scale_factor).set_stroke(color=color, width=3.5).set_fill(color="#290909", opacity=0.96),
            self.dots.animate.scale(scale_factor).set_color(color),
            self.header.animate.set_color(color),
            self.gate_lbl.animate.set_color(th.RED_LIGHT)
        )


class MemoryEnergyBar(VGroup):
    """
    Physical memory energy hierarchy comparison bar.
    Visualizes the 1,000x DRAM memory wall vs on-chip SRAM and MAC operations.
    """
    def __init__(self, categories=None, total_width=10.5, **kwargs):
        super().__init__(**kwargs)
        cats = categories or [
            ("DRAM Read (Off-Chip / HBM)", "200.0 pJ", 4.2, th.RED, "1,000× Energy Wall"),
            ("On-Chip SRAM Buffer",        "  5.0 pJ", 2.0, th.AMBER, "25× Cheaper than DRAM"),
            ("PE Flip-Flop Register",      "  1.0 pJ", 1.0, th.CYAN, "Local Storage"),
            ("INT8 MAC Operation",         "  0.2 pJ", 0.45, th.GREEN, "Virtually FREE in Silicon"),
        ]

        self.card_bg = RoundedRectangle(
            corner_radius=0.18,
            width=total_width,
            height=3.8,
            stroke_color=th.BORDER,
            stroke_width=1.5,
            fill_color="#080e18",
            fill_opacity=0.95
        )
        self.add(self.card_bg)

        rows = []
        for name, pJ_val, bar_w, col, tag in cats:
            name_t = SemanticText(name, role=TextRole.BODY, color=th.TEXT)
            name_t.scale_to_fit_width(2.8)
            
            bar = RoundedRectangle(
                corner_radius=0.06, width=bar_w, height=0.3,
                stroke_color=col, fill_color=col, fill_opacity=0.85
            )
            val_t = SemanticText(pJ_val, role=TextRole.BUS_VALUE, color=col)
            tag_t = SemanticText(tag, role=TextRole.PROBE_LABEL, color=th.MUTED)
            
            row = HStack(name_t, bar, val_t, tag_t, gap=th.SPACE_SM, alignment="center")
            rows.append(row)

        self.rows_group = VStack(*rows, gap=th.SPACE_MD, alignment="left")
        self.rows_group.move_to(self.card_bg.get_center())
        self.add(self.rows_group)


class ProcessingElementCell(VGroup):
    """
    Modular Weight-Stationary Processing Element (PE).
    Encapsulates weight register, MAC engine, East activation latch, and South sum latch.
    Features addressable boundary pin ports for auto-routing wires.
    """
    def __init__(self, row=0, col=0, width=5.6, height=3.8, color=th.AMBER, **kwargs):
        super().__init__(**kwargs)
        self.row = row
        self.col = col
        self.color = color

        # Main chassis
        self.chassis = RoundedRectangle(
            corner_radius=0.18,
            width=width,
            height=height,
            stroke_color=color,
            stroke_width=2.2,
            fill_color="#0c1422",
            fill_opacity=0.96
        )
        self.add(self.chassis)

        # Title badge
        self.title = SemanticText(f"PE [{row}, {col}]", role=TextRole.BLOCK_HEADER, color=color)
        self.title.next_to(self.chassis.get_top(), DOWN, buff=0.18)
        self.add(self.title)

        # Sub-blocks:
        # 1. Weight Register (locked local)
        self.w_box = RoundedRectangle(
            corner_radius=0.08, width=1.8, height=0.7,
            stroke_color=th.AMBER, stroke_width=1.5,
            fill_color="#2b1a05", fill_opacity=0.9
        ).move_to(self.chassis.get_center() + UP * 0.55 + LEFT * 1.3)
        self.w_lbl = SemanticText("W_REG [8b]", role=TextRole.PROBE_LABEL, color=th.AMBER_LIGHT)
        self.w_val = SemanticText("0x00", role=TextRole.BUS_VALUE, color=th.WHITE)
        w_sub = VStack(self.w_lbl, self.w_val, gap=th.SPACE_XS).move_to(self.w_box)
        self.add(self.w_box, w_sub)

        # 2. East Activation Forwarding Register
        self.east_box = RoundedRectangle(
            corner_radius=0.08, width=1.6, height=0.65,
            stroke_color=th.CYAN, stroke_width=1.5,
            fill_color="#091d2d", fill_opacity=0.9
        ).move_to(self.chassis.get_right() + LEFT * 1.1 + UP * 0.55)
        self.east_lbl = SemanticText("ACT", role=TextRole.PROBE_LABEL, color=th.CYAN_LIGHT)
        self.act_val = SemanticText("0", role=TextRole.BUS_VALUE, color=th.WHITE)
        east_sub = VGroup(self.east_lbl, self.act_val).arrange(DOWN, buff=0.06).move_to(self.east_box)
        self.add(self.east_box, east_sub)

        # 3. MAC Engine (Multiplier + Adder)
        self.mac_box = RoundedRectangle(
            corner_radius=0.08, width=2.4, height=0.85,
            stroke_color=th.GREEN, stroke_width=1.8,
            fill_color="#072213", fill_opacity=0.92
        ).move_to(self.chassis.get_center() + DOWN * 0.15)
        self.mac_lbl = SemanticText("MAC ENGINE", role=TextRole.PROBE_LABEL, color=th.GREEN_LIGHT)
        self.mac_eq = SemanticText("sum += a·w", role=TextRole.BUS_VALUE, color=th.WHITE)
        mac_sub = VStack(self.mac_lbl, self.mac_eq, gap=th.SPACE_XS).move_to(self.mac_box)
        self.add(self.mac_box, mac_sub)

        # 4. South Sum Forwarding Register
        self.south_box = RoundedRectangle(
            corner_radius=0.08, width=1.8, height=0.55,
            stroke_color=th.GREEN, stroke_width=1.5,
            fill_color="#061e11", fill_opacity=0.9
        ).move_to(self.chassis.get_bottom() + UP * 0.45)
        self.south_lbl = SemanticText("SUM", role=TextRole.PROBE_LABEL, color=th.GREEN_LIGHT)
        self.sum_val = SemanticText("0", role=TextRole.BUS_VALUE, color=th.WHITE)
        south_sub = VGroup(self.south_lbl, self.sum_val).arrange(DOWN, buff=0.06).move_to(self.south_box)
        self.add(self.south_box, south_sub)

        # 5. Internal Datapath Wires (connecting ports and registers)
        w_in_act = Line(self.west_port, self.east_box.get_left(), color=th.CYAN_DARK, stroke_width=1.5)
        w_act_mac = Arrow(self.west_port + RIGHT * 0.6, self.mac_box.get_left() + UP * 0.15, buff=0, color=th.CYAN_DARK, stroke_width=1.5, max_tip_length_to_length_ratio=0.2)
        w_w_mac = Arrow(self.w_box.get_bottom(), self.mac_box.get_top() + LEFT * 0.5, buff=0, color=th.AMBER_DARK, stroke_width=1.5, max_tip_length_to_length_ratio=0.2)
        w_sum_in = Arrow(self.north_port, self.mac_box.get_top() + RIGHT * 0.5, buff=0, color=th.GREEN_DARK, stroke_width=1.5, max_tip_length_to_length_ratio=0.2)
        w_mac_south = Arrow(self.mac_box.get_bottom(), self.south_box.get_top(), buff=0, color=th.GREEN_DARK, stroke_width=1.5, max_tip_length_to_length_ratio=0.2)
        w_act_out = Line(self.east_box.get_right(), self.east_port, color=th.CYAN_DARK, stroke_width=1.5)
        w_sum_out = Line(self.south_box.get_bottom(), self.south_port, color=th.GREEN_DARK, stroke_width=1.5)
        self.internal_wires = VGroup(w_in_act, w_act_mac, w_w_mac, w_sum_in, w_mac_south, w_act_out, w_sum_out)
        self.add(self.internal_wires)

    @property
    def west_port(self):
        """Input port for activations streaming from the left."""
        return self.chassis.get_left() + UP * 0.45

    @property
    def east_port(self):
        """Output port forwarding activations to the right neighbor."""
        return self.chassis.get_right() + UP * 0.45

    @property
    def north_port(self):
        """Input port for partial sums entering from the top."""
        return self.chassis.get_top() + RIGHT * 0.0

    @property
    def south_port(self):
        """Output port forwarding partial sums downward."""
        return self.chassis.get_bottom() + RIGHT * 0.0

    def update_weight(self, new_val_hex: str):
        """Updates locked weight register."""
        return self.w_val.update_text(new_val_hex)

    def update_act(self, new_val):
        """Updates the activation forwarding readout."""
        return self.act_val.update_text(str(new_val))

    def update_sum(self, new_val):
        """Updates the partial sum forwarding readout."""
        return self.sum_val.update_text(str(new_val))


class LogicGateNode(VGroup):
    """
    Standard cell logic gate symbol (AND, OR, ADD, MULT).
    Encapsulates input wires, gate body, symbol, and output wire with conducts/pulses.
    """
    def __init__(self, op_sym=r"\times", title="MULTIPLIER", color=th.GREEN, radius=0.65, **kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.circle = Circle(radius=radius, color=color, stroke_width=2.5, fill_color="#072213", fill_opacity=0.9)
        self.sym = MathTex(op_sym, color=th.WHITE, font_size=34).move_to(self.circle)
        self.title_lbl = Text(title, font=th.MONO, font_size=10, color=color).next_to(self.circle, UP, buff=0.08)

        self.in1 = Line(self.circle.get_left() + UP * 0.3 + LEFT * 0.8, self.circle.get_left() + UP * 0.3, color=th.CYAN, stroke_width=2.2)
        self.in2 = Line(self.circle.get_left() + DOWN * 0.3 + LEFT * 0.8, self.circle.get_left() + DOWN * 0.3, color=th.CYAN, stroke_width=2.2)
        self.out = Line(self.circle.get_right(), self.circle.get_right() + RIGHT * 0.8, color=th.AMBER, stroke_width=2.2)

        self.add(self.circle, self.sym, self.title_lbl, self.in1, self.in2, self.out)


class DFlipFlopNode(VGroup):
    """
    IEEE Standard D-Flip-Flop Standard Cell.
    Features D input (left), Q output (right), dynamic Clock triangle > (lower-left),
    and active synchronous state display.
    """
    def __init__(self, name="DFF", val="0", width=2.2, height=2.8, color=th.CYAN, has_leads=True, **kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.has_leads = has_leads
        self.chassis = RoundedRectangle(
            corner_radius=0.12, width=width, height=height,
            stroke_color=color, stroke_width=2.2, fill_color="#081528", fill_opacity=0.95
        )
        self.name_tag = Text(name, font=th.MONO, weight=BOLD, font_size=12, color=color).next_to(self.chassis.get_top(), DOWN, buff=0.16)
        
        # Clock triangle on lower left
        tri_size = 0.20
        clk_y = self.chassis.get_bottom()[1] + 0.65
        p1 = np.array([self.chassis.get_left()[0], clk_y + tri_size/2, 0])
        p2 = np.array([self.chassis.get_left()[0] + tri_size, clk_y, 0])
        p3 = np.array([self.chassis.get_left()[0], clk_y - tri_size/2, 0])
        self.clk_tri = Polygon(p1, p2, p3, stroke_color=th.AMBER, fill_color=th.AMBER, fill_opacity=0.85, stroke_width=1.5)
        self.clk_lbl = Text("clk", font=th.MONO, font_size=9, color=th.AMBER).next_to(self.clk_tri, UR, buff=0.02)

        # Port pin labels inside
        self.d_lbl = Text("D", font=th.MONO, weight=BOLD, font_size=12, color=th.TEXT).move_to(self.chassis.get_left() + RIGHT * 0.3 + UP * 0.4)
        self.q_lbl = Text("Q", font=th.MONO, weight=BOLD, font_size=12, color=th.GREEN_LIGHT).move_to(self.chassis.get_right() + LEFT * 0.3 + UP * 0.4)

        # Stored value badge in center
        self.val_box = RoundedRectangle(corner_radius=0.06, width=1.0, height=0.5, stroke_color=th.BORDER, fill_color="#050a12", fill_opacity=0.92)
        self.val_box.move_to(self.chassis.get_center() + DOWN * 0.08)
        self.val_txt = Text(str(val), font=th.MONO, weight=BOLD, font_size=13, color=th.WHITE).move_to(self.val_box)

        self.add(self.chassis, self.name_tag, self.clk_tri, self.clk_lbl, self.d_lbl, self.q_lbl, self.val_box, self.val_txt)

        # Optional external wire leads
        if has_leads:
            self.d_wire = Line(self.chassis.get_left() + UP * 0.4 + LEFT * 0.7, self.chassis.get_left() + UP * 0.4, color=th.TEXT, stroke_width=2.2)
            self.q_wire = Line(self.chassis.get_right() + UP * 0.4, self.chassis.get_right() + UP * 0.4 + RIGHT * 0.7, color=th.GREEN_LIGHT, stroke_width=2.2)
            clk_port = np.array([self.chassis.get_left()[0], clk_y, 0.0])
            self.clk_wire = Line(clk_port + LEFT * 0.7, clk_port, color=th.AMBER, stroke_width=2.2)
            self.add(self.d_wire, self.q_wire, self.clk_wire)

    def set_value(self, new_val, color=th.GREEN_LIGHT):
        new_t = Text(str(new_val), font=th.MONO, weight=BOLD, font_size=13, color=color).move_to(self.val_box)
        return Transform(self.val_txt, new_t)

