"""
Lab 00: 100 + 50 walks past the end of a signed 8-bit line and lands on -106.
-100 + -50 wraps the other way, to 106. The clamp stops the same walks at 127 and -128.
Overflow is named only after the carries disagree. Saturation is named only after the marker stops.
The signed line and bit rows stay for the whole scene. Visited stops leave a trail.
"""

from manim import *
import sys
from pathlib import Path

ANIM_DIR = Path(__file__).resolve().parent
if str(ANIM_DIR) not in sys.path:
    sys.path.insert(0, str(ANIM_DIR))

import theme as th
from components import KineticSiliconScene
from components.kinematics import VoiceoverTracker

L_WALK = "Start at 100 on this signed byte. Add 50. Both numbers are positive, so the marker should travel to the right and land further along the line. Follow each step and add it yourself. Nothing has crossed the end yet. The right-hand end of this line is 127."
L_STEPS = "The 50 is spent in beats of 5, then a final 2. The stops are 105, 110, 115, 120, 125, and 127. Add each one from 100 before the marker lands, and check the label. None of these stops has crossed the end of the line."
L_MID = "The marker should now read 115. That is 100 plus 15. Three beats of 5 are done, and 35 of the 50 remain. The next stops are 120, then 125, then 127. Add those three yourself, and check each label before the line runs out."
L_EDGE = "The marker is on 127, the last positive value this byte can hold. From 100 to 127 used 27, so 23 were never added. A true sum would be 150, and 150 is not on this line. Watch where the marker is sent next."
L_WRAP = "It crossed the end and came back on the negative side. The label reads negative 106. You can check the landing: 150 minus 256 is negative 106. The two inputs were positive, and the place it stopped is not. The line folded instead of growing."
L_SIGN = "These eight bits are the sum, 10010110. Cover the top bit and the rest is 22. The top bit is the sign, worth negative 128 here. Negative 128 plus 22 is negative 106. That top bit is why the side flipped."
L_RIPPLE = "Add the bits yourself, from the low end upward. 100 is 01100100 and 50 is 00110010. Most columns are quiet. The carry starts where the two 1s meet, then climbs toward the top of the byte. Watch each carry appear above its column."
L_DISAGREE = "The carry into the top bit is 1. The carry out of that same bit is 0. Those two numbers should match when the sign is honest, and here they do not. The sign flipped because the carry into it had nowhere to match."
L_NEG = "Second walk. Start at negative 100 and add negative 50. Both are negative, so the marker should travel left. Step by fives through negative 105, negative 110, negative 115, negative 120, negative 125, and negative 128. The true sum is negative 150."
L_RAIL = "The marker has reached negative 128, the most negative value on this byte. Negative 150 is still further left, and there is no tick there. Part of the negative 50 never fit. Wait before you decide which side of the line it will reappear on."
L_POS = "It wrapped the other way and came back positive. The label is 106. Check it: negative 150 plus 256 is 106. The bits of 106 are 01101010, a clear positive sign. Two negatives were asked to go further left, and the byte turned them around."
L_AGAIN = "Run the positive walk again from 100, adding the same 50. This time the marker is not allowed to cross the end. It may travel right only while the next beat still exists on the line. When the next beat would leave the line, it has to stay."
L_STOP127 = "The beats reach 127 and stop. The unused 23 are thrown away. The label stays 127, and the marker does not jump to the other end. 100 plus 50, on this repaired walk, is the end of the positive side. Leave it there and watch that it does not move."
L_STOP128 = "The negative walk gets the same treatment. From negative 100 toward negative 150, the marker may step left only until negative 128. It stops on that tick. It does not bounce to 106. Both repaired walks are now sitting on an end, and neither one wrapped."
L_FITS = "One more sum, chosen because it fits. Start at 20 and add 30. The beats are 25, 30, 35, 40, 45, and 50. Every one of those ticks exists. The marker walks to 50 and rests in the middle of the line, far from either end."
L_DIFF = "Same line, three endings. 100 plus 50 wrapped to negative 106. The repaired walks stopped at 127 and at negative 128. 20 plus 30 landed on 50, and nothing had to catch it. You can see the difference: the ends only matter when a step would pass them."


def _mark(scene, tag):
    renderer = getattr(scene, "renderer", None)
    t = float(getattr(renderer, "time", 0.0) or 0.0)
    path = Path("/tmp") / f"hw_marks_{type(scene).__name__}.txt"
    with path.open("a") as handle:
        handle.write(f"{tag}\t{t:.3f}\n")


def _bit_row(bits, color):
    cells = VGroup()
    for bit in bits:
        box = RoundedRectangle(
            corner_radius=0.05, width=0.52, height=0.58,
            stroke_color=color, stroke_width=1.7,
            fill_color="#0e1526", fill_opacity=0.96,
        )
        txt = Text(bit, font=th.MONO, weight=BOLD, font_size=22, color=color).move_to(box)
        cells.add(VGroup(box, txt))
    cells.arrange(RIGHT, buff=0.08)
    return cells


def _line_dur(line):
    return VoiceoverTracker(line).duration


class Lab00SaturationIntro(KineticSiliconScene):
    def construct(self):
        Path("/tmp/hw_marks_Lab00SaturationIntro.txt").write_text("")
        with self.world() as w:
            axis, line, left_tick, right_tick, left_lbl, right_lbl = self._axis()
            w.show(axis, run_time=0.4)
            _mark(self, "start")
            y = line.get_center()[1]

            def xpos(val):
                # Extend past the rails so 150 / -150 can sit off the line.
                return line.get_start()[0] + (val + 128) / 256.0 * line.width

            caption = Text("100 + 50", font=th.MONO, weight=BOLD, font_size=28, color=th.WHITE)
            caption.move_to(UP * 3.35)
            marker = Dot(radius=0.13, color=th.GREEN)
            marker.move_to([xpos(100), y, 0])
            tag = Text("100", font=th.MONO, weight=BOLD, font_size=26, color=th.GREEN_LIGHT)
            tag.move_to([xpos(100), y + 0.48, 0])
            w.show(caption, marker, tag, run_time=0.35)
            hold = [tag]
            trails = VGroup()
            residues = {}

            # Highlight 127 while walking is introduced.
            self.play(
                right_tick.animate.set_color(th.AMBER),
                right_lbl.animate.set_color(th.AMBER_LIGHT),
                run_time=0.4,
            )
            w.say(L_WALK, already=0.75)

            step_dur = _line_dur(L_STEPS)
            hop = max(0.7, (step_dur - 0.2) / 3.5)
            self._walk_trail(
                w, marker, hold, trails, xpos, y,
                [105, 110, 115],
                th.GREEN, th.GREEN_LIGHT, hop,
            )
            w.say(L_STEPS, already=hop * 3)

            mid_tick = self._trail_label(trails, 115)
            if mid_tick is not None:
                self.play(Indicate(mid_tick, color=th.GREEN_LIGHT, scale_factor=1.08), run_time=0.5)
            w.say(L_MID, already=0.5)

            hop2 = max(0.7, 2.4)
            self._walk_trail(
                w, marker, hold, trails, xpos, y,
                [120, 125, 127],
                th.GREEN, th.GREEN_LIGHT, hop2,
            )
            # Motion after L_MID is the "check each label" beat before the edge.
            self.wait(0.15)

            # Edge: show 150 past the line and unused 23.
            beyond = Text("150", font=th.MONO, weight=BOLD, font_size=24, color=th.RED_LIGHT)
            beyond.move_to([xpos(150), y + 0.55, 0])
            unused = Text("23 left", font=th.MONO, font_size=18, color=th.AMBER_LIGHT)
            unused.next_to(beyond, DOWN, buff=0.12)
            ghost_dot = Dot(radius=0.1, color=th.RED_LIGHT).move_to([xpos(150), y, 0])
            edge_open = w.show(beyond, unused, ghost_dot, run_time=0.4)
            self.play(
                right_tick.animate.set_color(th.RED),
                right_lbl.animate.set_color(th.RED_LIGHT),
                run_time=0.3,
            )
            w.say(L_EDGE, already=edge_open + 0.3)

            # Wrap: travel past the end, then fold onto -106.
            wrap_dur = _line_dur(L_WRAP)
            out_x = xpos(140)
            land_x = xpos(-106)
            wrapped = Text("-106", font=th.MONO, weight=BOLD, font_size=26, color=th.RED_LIGHT)
            wrapped.move_to([land_x, y + 0.48, 0])
            self.play(
                marker.animate.move_to([out_x, y, 0]).set_color(th.RED),
                ghost_dot.animate.set_opacity(0.35),
                run_time=min(1.4, wrap_dur * 0.25),
            )
            self.play(
                marker.animate.move_to([land_x, y, 0]),
                FadeIn(wrapped),
                left_tick.animate.set_color(th.RED),
                left_lbl.animate.set_color(th.RED_LIGHT),
                run_time=min(2.2, wrap_dur * 0.4),
            )
            # Keep the live tag; leave trail residue for -106.
            old = hold[0]
            self.play(old.animate.set_opacity(0.35).scale(0.85), run_time=0.25)
            w.keep(wrapped)
            hold[0] = wrapped
            residues["wrap_neg"] = wrapped
            _mark(self, "break")
            self.screen_shake(intensity=0.05, cycles=3, run_time=0.24)
            spent = min(1.4, wrap_dur * 0.25) + min(2.2, wrap_dur * 0.4) + 0.49
            w.say(L_WRAP, already=spent)
            w.ask("Both were positive. Why is the sign wrong?", hold=1.2)

            # Bit rows under the line — stay for the rest of the scene.
            sum_row = _bit_row("10010110", th.TEXT)
            sum_row[0][0].set_stroke(color=th.RED_LIGHT, width=2.4)
            sum_row[0][1].set_color(th.RED_LIGHT)
            sum_label = Text("sum", font=th.MONO, font_size=16, color=th.RED_LIGHT)
            sum_label.next_to(sum_row, LEFT, buff=0.18)
            block = VGroup(sum_label, sum_row).move_to(DOWN * 0.05)
            w.show(block, run_time=0.35)
            self.focus_on(sum_row[0], buffer_factor=5.5, run_time=0.5)
            w.say(L_SIGN, already=0.85)
            self.reset_camera(run_time=0.35)

            bits_a = _bit_row("01100100", th.CYAN_LIGHT)
            bits_b = _bit_row("00110010", th.AMBER_LIGHT)
            bits_a.align_to(sum_row, LEFT).align_to(sum_row, UP)
            bits_a.shift(DOWN * 0.85)
            bits_b.align_to(sum_row, LEFT).align_to(bits_a, UP)
            bits_b.shift(DOWN * 0.72)
            lab_a = Text("100", font=th.MONO, font_size=16, color=th.CYAN_LIGHT)
            lab_b = Text("50", font=th.MONO, font_size=16, color=th.AMBER_LIGHT)
            lab_a.next_to(bits_a, LEFT, buff=0.16)
            lab_b.next_to(bits_b, LEFT, buff=0.16)
            rows = VGroup(lab_a, bits_a, lab_b, bits_b)
            w.show(rows, run_time=0.35)

            cin = [1, 1, 0, 0, 0, 0, 0, 0]
            carries = []
            for i, bit in enumerate(cin):
                glyph = Text(str(bit), font=th.MONO, weight=BOLD, font_size=18, color=th.AMBER_LIGHT)
                glyph.next_to(sum_row[i], UP, buff=0.1)
                carries.append(glyph)
            cout = Text("0", font=th.MONO, weight=BOLD, font_size=18, color=th.CYAN_LIGHT)
            cout.next_to(sum_label, UP, buff=0.1)
            order = list(reversed(carries)) + [cout]
            for glyph in order:
                w.keep(glyph)
            ripple_dur = _line_dur(L_RIPPLE)
            self.play(
                LaggedStart(*[FadeIn(glyph) for glyph in order], lag_ratio=0.18),
                run_time=min(ripple_dur - 0.4, 4.5),
            )
            w.say(L_RIPPLE, already=0.35 + min(ripple_dur - 0.4, 4.5))

            self.play(
                carries[0].animate.set_color(th.RED_LIGHT).scale(1.35),
                cout.animate.set_color(th.CYAN_LIGHT).scale(1.35),
                run_time=0.4,
            )
            cin_lbl = Text("into sign  1", font=th.MONO, font_size=20, color=th.RED_LIGHT)
            cout_lbl = Text("out of sign  0", font=th.MONO, font_size=20, color=th.CYAN_LIGHT)
            labels = VGroup(cin_lbl, cout_lbl).arrange(RIGHT, buff=0.7)
            labels.next_to(rows, DOWN, buff=0.22)
            if labels.get_bottom()[1] < -3.55:
                labels.shift(UP * (-3.55 - labels.get_bottom()[1]))
            w.show(labels, run_time=0.3)
            w.say(L_DISAGREE, already=0.7)
            w.name("overflow", labels, direction=DOWN)

            # Dim bit labels slightly; keep them. Negative walk on the same line.
            self.play(
                block.animate.set_opacity(0.55),
                rows.animate.set_opacity(0.55),
                labels.animate.set_opacity(0.45),
                VGroup(*carries, cout).animate.set_opacity(0.45),
                beyond.animate.set_opacity(0.25),
                unused.animate.set_opacity(0.25),
                ghost_dot.animate.set_opacity(0.2),
                run_time=0.3,
            )
            caption = self._retitle(w, caption, "-100 + -50")
            self._calm(left_tick, right_tick, left_lbl, right_lbl)
            # Keep -106 residue; move marker to -100 without erasing evidence.
            start_tag = Text("-100", font=th.MONO, weight=BOLD, font_size=24, color=th.GREEN_LIGHT)
            start_tag.move_to([xpos(-100), y + 0.48, 0])
            self.play(
                marker.animate.move_to([xpos(-100), y, 0]).set_color(th.GREEN),
                FadeIn(start_tag),
                wrapped.animate.set_opacity(0.45).scale(0.9),
                run_time=0.45,
            )
            if hold[0] is not wrapped and hold[0] in w.cast:
                self.play(hold[0].animate.set_opacity(0.3), run_time=0.2)
            w.keep(start_tag)
            hold[0] = start_tag

            neg_dur = _line_dur(L_NEG)
            hop_n = max(0.5, (neg_dur - 0.5) / 6.5)
            self._walk_trail(
                w, marker, hold, trails, xpos, y,
                [-105, -110, -115, -120, -125, -128],
                th.GREEN, th.GREEN_LIGHT, hop_n,
            )
            w.say(L_NEG, already=0.45 + hop_n * 6)

            neg_beyond = Text("-150", font=th.MONO, weight=BOLD, font_size=24, color=th.RED_LIGHT)
            neg_beyond.move_to([xpos(-150), y + 0.55, 0])
            neg_ghost = Dot(radius=0.1, color=th.RED_LIGHT).move_to([xpos(-150), y, 0])
            rail_open = w.show(neg_beyond, neg_ghost, run_time=0.35)
            self.play(
                left_tick.animate.set_color(th.RED),
                left_lbl.animate.set_color(th.RED_LIGHT),
                run_time=0.25,
            )
            w.say(L_RAIL, already=rail_open + 0.25)
            w.ask("Where does -150 land?", hold=1.2)

            pos_dur = _line_dur(L_POS)
            out_x = xpos(-140)
            land_x = xpos(106)
            landed = Text("106", font=th.MONO, weight=BOLD, font_size=26, color=th.RED_LIGHT)
            landed.move_to([land_x, y + 0.48, 0])
            self.play(
                marker.animate.move_to([out_x, y, 0]).set_color(th.RED),
                run_time=min(1.2, pos_dur * 0.22),
            )
            self.play(
                marker.animate.move_to([land_x, y, 0]),
                FadeIn(landed),
                right_tick.animate.set_color(th.RED),
                right_lbl.animate.set_color(th.RED_LIGHT),
                run_time=min(2.0, pos_dur * 0.38),
            )
            self.play(hold[0].animate.set_opacity(0.35).scale(0.85), run_time=0.2)
            w.keep(landed)
            hold[0] = landed
            residues["wrap_pos"] = landed
            self.screen_shake(intensity=0.05, cycles=3, run_time=0.24)

            # Update bit rows in place to 106 = 01101010.
            new_sum = _bit_row("01101010", th.TEXT)
            new_sum.move_to(sum_row)
            new_a = _bit_row("10011100", th.CYAN_LIGHT)  # -100
            new_b = _bit_row("11001110", th.AMBER_LIGHT)  # -50
            new_a.move_to(bits_a)
            new_b.move_to(bits_b)
            new_lab_a = Text("-100", font=th.MONO, font_size=16, color=th.CYAN_LIGHT).move_to(lab_a)
            new_lab_b = Text("-50", font=th.MONO, font_size=16, color=th.AMBER_LIGHT).move_to(lab_b)
            self.play(
                FadeOut(sum_row), FadeIn(new_sum),
                FadeOut(bits_a), FadeIn(new_a),
                FadeOut(bits_b), FadeIn(new_b),
                FadeOut(lab_a), FadeIn(new_lab_a),
                FadeOut(lab_b), FadeIn(new_lab_b),
                block.animate.set_opacity(0.9),
                rows.animate.set_opacity(0.9),
                run_time=0.55,
            )
            for old in (sum_row, bits_a, bits_b, lab_a, lab_b):
                if old in w.cast:
                    w.cast.remove(old)
            w.keep(new_sum, new_a, new_b, new_lab_a, new_lab_b)
            sum_row, bits_a, bits_b = new_sum, new_a, new_b
            spent = min(1.2, pos_dur * 0.22) + min(2.0, pos_dur * 0.38) + 0.99
            w.say(L_POS, already=spent)

            # Saturation: positive walk refuses the wrap.
            caption = self._retitle(w, caption, "100 + 50")
            self._calm(left_tick, right_tick, left_lbl, right_lbl)
            start_tag = Text("100", font=th.MONO, weight=BOLD, font_size=24, color=th.GREEN_LIGHT)
            start_tag.move_to([xpos(100), y + 0.48, 0])
            self.play(
                marker.animate.move_to([xpos(100), y, 0]).set_color(th.GREEN),
                FadeIn(start_tag),
                landed.animate.set_opacity(0.4),
                run_time=0.4,
            )
            w.keep(start_tag)
            hold[0] = start_tag
            again_dur = _line_dur(L_AGAIN)
            hop_a = max(0.45, (again_dur - 0.4) / 6.5)
            self._walk_trail(
                w, marker, hold, trails, xpos, y,
                [105, 110, 115, 120, 125, 127],
                th.GREEN, th.GREEN_LIGHT, hop_a, leave_active=True,
            )
            w.say(L_AGAIN, already=0.4 + hop_a * 6)

            # Ghost toward -106; marker refuses; remainder falls away.
            ghost_wrap = Text("-106", font=th.MONO, font_size=22, color=th.RED_LIGHT)
            ghost_wrap.move_to([xpos(-106), y + 0.85, 0]).set_opacity(0.7)
            discard = Text("23", font=th.MONO, weight=BOLD, font_size=22, color=th.AMBER_LIGHT)
            discard.move_to([xpos(127), y + 0.95, 0])
            self.play(FadeIn(ghost_wrap), FadeIn(discard), run_time=0.35)
            self.play(
                ghost_wrap.animate.set_opacity(0.15),
                discard.animate.shift(DOWN * 0.7).set_opacity(0),
                right_tick.animate.set_color(th.GREEN),
                right_lbl.animate.set_color(th.GREEN_LIGHT),
                marker.animate.set_color(th.GREEN),
                run_time=0.7,
            )
            clamp127 = Text("127", font=th.MONO, weight=BOLD, font_size=24, color=th.GREEN_LIGHT)
            clamp127.move_to([xpos(127), y + 0.48, 0])
            if hold[0] is not clamp127:
                # Active tag may already be 127 from the walk.
                if str(getattr(hold[0], "text", "")) != "127":
                    self.play(FadeOut(hold[0]), FadeIn(clamp127), run_time=0.25)
                    if hold[0] in w.cast:
                        w.cast.remove(hold[0])
                    w.keep(clamp127)
                    hold[0] = clamp127
            residues["clamp_pos"] = hold[0]
            _mark(self, "repair")
            w.say(L_STOP127, already=1.05)
            self.play(FadeOut(ghost_wrap), run_time=0.2)

            # Negative saturation.
            caption = self._retitle(w, caption, "-100 + -50")
            start_tag = Text("-100", font=th.MONO, weight=BOLD, font_size=24, color=th.GREEN_LIGHT)
            start_tag.move_to([xpos(-100), y + 0.48, 0])
            self.play(
                marker.animate.move_to([xpos(-100), y, 0]).set_color(th.GREEN),
                FadeIn(start_tag),
                hold[0].animate.set_opacity(0.55),
                run_time=0.4,
            )
            w.keep(start_tag)
            hold[0] = start_tag
            stop_dur = _line_dur(L_STOP128)
            hop_s = max(0.4, (stop_dur - 1.2) / 6.5)
            self._walk_trail(
                w, marker, hold, trails, xpos, y,
                [-105, -110, -115, -120, -125, -128],
                th.GREEN, th.GREEN_LIGHT, hop_s, leave_active=True,
            )
            ghost_pos = Text("106", font=th.MONO, font_size=22, color=th.RED_LIGHT)
            ghost_pos.move_to([xpos(106), y + 0.85, 0]).set_opacity(0.7)
            self.play(FadeIn(ghost_pos), run_time=0.3)
            self.play(
                ghost_pos.animate.set_opacity(0.15),
                left_tick.animate.set_color(th.GREEN),
                left_lbl.animate.set_color(th.GREEN_LIGHT),
                run_time=0.55,
            )
            residues["clamp_neg"] = hold[0]
            w.say(L_STOP128, already=0.4 + hop_s * 6 + 0.85)
            w.name("saturation", marker, direction=DOWN)
            self.play(FadeOut(ghost_pos), run_time=0.2)

            # Fits in the middle.
            caption = self._retitle(w, caption, "20 + 30")
            self._calm(left_tick, right_tick, left_lbl, right_lbl)
            start_tag = Text("20", font=th.MONO, weight=BOLD, font_size=24, color=th.GREEN_LIGHT)
            start_tag.move_to([xpos(20), y + 0.48, 0])
            self.play(
                marker.animate.move_to([xpos(20), y, 0]).set_color(th.GREEN),
                FadeIn(start_tag),
                hold[0].animate.set_opacity(0.5),
                run_time=0.35,
            )
            w.keep(start_tag)
            hold[0] = start_tag
            fits_dur = _line_dur(L_FITS)
            hop_f = max(0.4, (fits_dur - 0.35) / 6.5)
            self._walk_trail(
                w, marker, hold, trails, xpos, y,
                [25, 30, 35, 40, 45, 50],
                th.GREEN, th.GREEN_LIGHT, hop_f, leave_active=True,
            )
            residues["fit"] = hold[0]
            w.say(L_FITS, already=0.35 + hop_f * 6)

            # Final compare: light up all three endings.
            wrap_n = residues.get("wrap_neg")
            wrap_p = residues.get("wrap_pos")
            clamp_p = residues.get("clamp_pos")
            clamp_n = residues.get("clamp_neg")
            fit = residues.get("fit")
            glow = []
            for mob in (wrap_n, wrap_p, clamp_p, clamp_n, fit):
                if mob is not None:
                    glow.append(mob.animate.set_opacity(1).set_color(
                        th.RED_LIGHT if mob in (wrap_n, wrap_p) else th.GREEN_LIGHT
                    ))
            if glow:
                self.play(*glow, run_time=0.55)
            callouts = VGroup()
            for mob, note, col in (
                (wrap_n, "wrapped", th.RED_LIGHT),
                (clamp_p, "clamp", th.GREEN_LIGHT),
                (clamp_n, "clamp", th.GREEN_LIGHT),
                (fit, "fits", th.CYAN_LIGHT),
            ):
                if mob is None:
                    continue
                lbl = Text(note, font=th.MONO, font_size=14, color=col)
                lbl.next_to(mob, UP, buff=0.08)
                callouts.add(lbl)
            if len(callouts):
                w.show(*callouts, run_time=0.35)
            w.say(L_DIFF, already=0.9)

    def _axis(self):
        line = Line(LEFT * 5.6, RIGHT * 5.6, color=th.MUTED, stroke_width=3)
        ticks = VGroup()
        for frac, label in ((0.0, "-128"), (0.5, "0"), (1.0, "127")):
            pt = line.point_from_proportion(frac)
            tick = Line(pt + DOWN * 0.12, pt + UP * 0.12, color=th.MUTED, stroke_width=2)
            cap = Text(label, font=th.MONO, font_size=18, color=th.MUTED).next_to(tick, DOWN, buff=0.1)
            ticks.add(VGroup(tick, cap))
        axis = VGroup(line, ticks).move_to(UP * 1.85)
        return axis, line, ticks[0][0], ticks[2][0], ticks[0][1], ticks[2][1]

    def _walk_trail(
        self, w, marker, hold, trails, xpos, y, values, dot_color, text_color,
        hop=0.55, leave_active=False,
    ):
        for value in values:
            # Stagger trail lanes so successive stops do not stack on one glyph.
            lane = 0.48
            new = Text(str(value), font=th.MONO, weight=BOLD, font_size=22, color=text_color)
            new.move_to([xpos(value), y + lane, 0])
            tick = Line(
                [xpos(value), y - 0.1, 0], [xpos(value), y + 0.1, 0],
                color=dot_color, stroke_width=2,
            )
            old = hold[0]
            anims = [
                marker.animate.move_to([xpos(value), y, 0]).set_color(dot_color),
                FadeIn(new),
                FadeIn(tick),
            ]
            # Park previous labels above/below the line on alternating lanes.
            if old is not None and old in self.mobjects:
                n = len(trails)
                park = (0.68 + 0.22 * (n % 2)) if n % 2 == 0 else -(0.42 + 0.18 * (n % 2))
                ox = old.get_center()[0]
                anims.append(
                    old.animate.set_opacity(0.4).scale(0.78).move_to([ox, y + park, 0])
                )
            self.play(*anims, run_time=hop)
            w.keep(new, tick)
            trails.add(VGroup(tick, new))
            hold[0] = new
        if leave_active and hold[0] is not None:
            self.play(hold[0].animate.set_opacity(1), run_time=0.2)

    def _trail_label(self, trails, value):
        target = str(value)
        for group in trails:
            if len(group) >= 2 and getattr(group[1], "text", None) == target:
                return group[1]
        return None

    def _retitle(self, w, old, text):
        new = Text(text, font=th.MONO, weight=BOLD, font_size=28, color=th.WHITE)
        new.move_to(old)
        self.play(FadeOut(old), FadeIn(new), run_time=0.25)
        if old in w.cast:
            w.cast.remove(old)
        w.keep(new)
        self._caption = new
        return new

    def _calm(self, left_tick, right_tick, left_lbl, right_lbl):
        self.play(
            left_tick.animate.set_color(th.MUTED),
            right_tick.animate.set_color(th.MUTED),
            left_lbl.animate.set_color(th.MUTED),
            right_lbl.animate.set_color(th.MUTED),
            run_time=0.2,
        )
