"""
Shared design system for the Hardware AI Acceleration Manim video suite.

Every scene in this package imports from here so all 10 lab videos share a
consistent look: Slate-900 dark background, color-coded silicon dataflow,
monospace bit-strings, and reusable "hardware" primitives (cards, badges,
data packets, clock edges, bit rows).

The palette is intentionally consistent with the repository's schematics and
visualizer so the videos feel like one coherent series.
"""

from manim import *

# ---------------------------------------------------------------------------
# PALETTE
# ---------------------------------------------------------------------------
BG          = "#0f172a"   # slate-900  (camera background)
CARD        = "#1e293b"   # slate-800  (panel fill)
CARD_ALT    = "#16203280" # subtle alternate panel
BORDER      = "#334155"   # slate-700  (panel stroke)
TEXT        = "#e2e8f0"   # slate-200  (primary text)
MUTED       = "#94a3b8"   # slate-400  (secondary text)
FAINT       = "#64748b"   # slate-500

CYAN        = "#38bdf8"   # sky-400    -> dataflow / activations
CYAN_LIGHT  = "#7dd3fc"
CYAN_DARK   = "#0c4a6e"
AMBER       = "#f59e0b"   # amber-500  -> weights / emphasis
AMBER_LIGHT = "#fde68a"
AMBER_DARK  = "#78350f"
GREEN       = "#4ade80"   # green-400  -> success / partial sums
GREEN_LIGHT = "#86efac"
GREEN_DARK  = "#064e3b"
RED         = "#ef4444"   # red-500    -> bugs / overflow / danger
RED_LIGHT   = "#fca5a5"
RED_DARK    = "#450a0a"
PURPLE      = "#a855f7"   # purple-400 -> LUTs / special functions
PURPLE_LIGHT= "#d8b4fe"
PURPLE_DARK = "#3b0764"
ORANGE      = "#fb923c"
PINK        = "#f472b6"
WHITE       = "#ffffff"

# ---------------------------------------------------------------------------
# FONTS  (Pango names; no LaTeX on this machine, so we use Text everywhere)
# ---------------------------------------------------------------------------
SANS  = "Helvetica"
MONO  = "Menlo"

# ---------------------------------------------------------------------------
# REUSABLE CONSTRUCTORS
# ---------------------------------------------------------------------------

def set_dark(camera):
    """Apply the series background to a Scene's camera."""
    camera.background_color = BG


def badge(text, color=CYAN, font_size=20):
    """Small all-caps kicker shown above a title."""
    return Text(text, font=SANS, weight=BOLD, font_size=font_size, color=color)


def title(text, font_size=34, color=WHITE):
    return Text(text, font=SANS, weight=BOLD, font_size=font_size, color=color)


def header(badge_text, title_text, title_size=34, badge_color=CYAN):
    """Centered two-line header pinned to the top of the frame."""
    b = badge(badge_text, color=badge_color)
    t = title(title_text, title_size)
    grp = VGroup(b, t).arrange(DOWN, buff=0.16).to_edge(UP, buff=0.5)
    return grp, b, t


def card(width, height, stroke=BORDER, fill=CARD, radius=0.2, stroke_w=2.0,
         fill_opacity=0.95):
    """Rounded panel used as a container for text and diagrams."""
    return RoundedRectangle(
        corner_radius=radius, width=width, height=height,
        stroke_color=stroke, stroke_width=stroke_w,
        fill_color=fill, fill_opacity=fill_opacity,
    )


def packet(color=AMBER, radius=0.14, fill_opacity=1.0):
    """A small glowing 'data token' that travels along a datapath."""
    return Dot(point=ORIGIN, radius=radius, color=color, fill_opacity=fill_opacity)


def bit_cell(bit, color=WHITE, cell_w=0.42, cell_h=0.58, font_size=22):
    """One bit of a bit-string, drawn as a small framed cell."""
    frame = Rectangle(
        width=cell_w, height=cell_h,
        stroke_color=BORDER, stroke_width=1.5,
        fill_color=CARD, fill_opacity=0.9,
    )
    lbl = Text(str(bit), font=MONO, weight=BOLD, font_size=font_size, color=color)
    lbl.move_to(frame)
    return VGroup(frame, lbl)


def bit_row(bits, colors=None, text_colors=None, cell_w=0.42, cell_h=0.58,
            font_size=22, buff=0.08, color=None):
    """
    Horizontal row of bit cells.
    bits:      str or list of str (e.g. "01111111")
    colors:    per-cell frame/stroke accent colour (optional list or single)
    text_colors: per-cell glyph colour (optional)
    color:     convenience: set both frame and glyph colour for every cell
    """
    if isinstance(bits, str):
        bits = list(bits)
    n = len(bits)
    if color is not None:
        colors = [color] * n
        text_colors = [color] * n
    if colors is None:
        colors = [BORDER] * n
    elif not isinstance(colors, (list, tuple)):
        colors = [colors] * n
    if text_colors is None:
        text_colors = [WHITE] * n
    elif not isinstance(text_colors, (list, tuple)):
        text_colors = [text_colors] * n
    cells = VGroup()
    for b, c, tc in zip(bits, colors, text_colors):
        frame = Rectangle(
            width=cell_w, height=cell_h,
            stroke_color=c, stroke_width=1.5,
            fill_color=CARD, fill_opacity=0.9,
        )
        lbl = Text(str(b), font=MONO, weight=BOLD, font_size=font_size, color=tc)
        lbl.move_to(frame)
        cells.add(VGroup(frame, lbl))
    cells.arrange(RIGHT, buff=buff)
    return cells


def bit_label(text, color=MUTED, font_size=15):
    """Small monospace annotation under/over a bit cell."""
    return Text(text, font=MONO, font_size=font_size, color=color)


def bullet(text, color=TEXT, font_size=18, bullet_color=None, font=SANS):
    """Single bullet line: '• text'. Colour of the dot follows the text by default."""
    if bullet_color is None:
        bullet_color = color
    dot = Dot(point=ORIGIN, radius=0.045, color=bullet_color)
    t = Text(text, font=font, font_size=font_size, color=color)
    g = VGroup(dot, t).arrange(RIGHT, buff=0.18, aligned_edge=UP)
    return g


def bullets(lines, color=TEXT, font_size=18, bullet_color=None, buff=0.22,
            aligned_edge=LEFT):
    """A vertical stack of bullet lines, left-aligned."""
    items = [bullet(l, color=color, font_size=font_size, bullet_color=bullet_color)
             for l in lines]
    return VGroup(*items).arrange(DOWN, buff=buff, aligned_edge=aligned_edge)


def arrows(*n, **kwargs):
    return Arrow(*n, **kwargs)


def clock_symbol(color=CYAN, radius=0.16, stroke_width=3.0):
    """A tiny square-wave glyph used to mark a rising clock edge."""
    w = 0.5
    h = 0.42
    sq = VGroup(
        Line(ORIGIN, RIGHT * w * 0.25, color=color, stroke_width=stroke_width),
        Line(RIGHT * w * 0.25, UP * h * 0.7 + RIGHT * w * 0.25, color=color, stroke_width=stroke_width),
        Line(UP * h * 0.7 + RIGHT * w * 0.25, UP * h * 0.7 + RIGHT * w * 0.5, color=color, stroke_width=stroke_width),
        Line(UP * h * 0.7 + RIGHT * w * 0.5, DOWN * h * 0.7 + RIGHT * w * 0.5, color=color, stroke_width=stroke_width),
        Line(DOWN * h * 0.7 + RIGHT * w * 0.5, DOWN * h * 0.7 + RIGHT * w * 0.75, color=color, stroke_width=stroke_width),
        Line(DOWN * h * 0.7 + RIGHT * w * 0.75, RIGHT * w, color=color, stroke_width=stroke_width),
    )
    return sq


def glow(mob, color=CYAN, n=24, opacity=0.25, buff=0.12):
    """Return a VGroup containing a soft glow behind a mobject."""
    if not isinstance(mob, Mobject):
        mob = VGroup(*mob)
    halo = mob.copy()
    halo.set_style(stroke_color=color, fill_color=color, stroke_width=0)
    halo.set_fill(color, opacity)
    return halo


def label_arrow(text, color=MUTED, font_size=15, direction=UP):
    """Small text label, optionally with an arrowhead-less connector."""
    return Text(text, font=MONO, font_size=font_size, color=color)


def make_counter(tracker, prefix="", suffix="", font_size=28, color=WHITE,
                font=MONO, weight=BOLD):
    """Return an always_redraw Text that tracks a ValueTracker's integer value."""
    def _build():
        return Text(
            f"{prefix}{int(round(tracker.get_value()))}{suffix}",
            font=font, weight=weight, font_size=font_size, color=color,
        )
    return always_redraw(_build)


def animate_counter(scene, tracker, target, run_time=1.2, rate_func=smooth):
    """Animate a ValueTracker to a new value (for use with make_counter)."""
    return tracker.animate.set_value(target).set_run_time(run_time)


def pulse_edge(scene, glyph, flash_color=RED, rest_color=PURPLE):
    """Flash a clock-edge glyph once to represent a rising edge (in place)."""
    scene.play(glyph.animate.set_color(flash_color), run_time=0.15)
    scene.play(glyph.animate.set_color(rest_color), run_time=0.2)


def labeled_bit_row(bits, label, bits_color=WHITE, label_color=MUTED,
                    font_size=17, buff=0.35, cell_w=0.42, cell_h=0.58):
    """A bit-row with a monospace label to its left. Returns a VGroup."""
    bits_row = bit_row(bits, color=bits_color, cell_w=cell_w, cell_h=cell_h)
    lbl = Text(label, font=MONO, font_size=font_size, color=label_color)
    return VGroup(lbl, bits_row).arrange(RIGHT, buff=buff)


def matrix(cells, color=WHITE, cell=0.62, label=None, mono_size=17,
           label_color=MUTED, stroke=BORDER, fill=CARD):
    """
    Build a labelled matrix of monospace text cells.
    cells: list of rows (list of str). Returns a VGroup whose first rows*cols
    submobjects are the cell units (box + text), optionally + a label above.
    """
    g = VGroup()
    rows = len(cells)
    cols = len(cells[0]) if rows else 0
    for r in range(rows):
        for c in range(cols):
            box = Square(side_length=cell, stroke_color=stroke, stroke_width=1.5,
                         fill_color=fill, fill_opacity=0.95)
            box.move_to(np.array([(c - (cols - 1) / 2) * cell * 1.2,
                                  -((r - (rows - 1) / 2) * cell * 1.2), 0]))
            lbl = Text(cells[r][c], font=MONO, font_size=mono_size, color=color)
            lbl.move_to(box)
            g.add(VGroup(box, lbl))
    if label is not None:
        l = Text(label, font=MONO, font_size=15, color=label_color)
        l.next_to(g, UP, buff=0.18)
        g.add(l)
    g.move_to(ORIGIN)
    return g


def dot_grid(rows, cols, dx=0.46, dy=0.42, radius=0.06, color=CYAN):
    """A rows×cols grid of dots, centered at ORIGIN. Returns a VGroup."""
    dots = VGroup()
    for r in range(rows):
        for c in range(cols):
            d = Dot(point=np.array([(c - (cols - 1) / 2) * dx,
                                    ((rows - 1) / 2 - r) * dy, 0]),
                    radius=radius, color=color)
            dots.add(d)
    return dots


def recap(scene, title, points, stroke=GREEN, title_color=GREEN_LIGHT,
          card_w=10.0, font_size=18, title_size=26, bullet_color=GREEN,
          wait=2.4):
    """
    Standard closing card: a bordered panel with a title and bullet points.
    Builds the mobjects, plays the entrance animation, and waits.
    """
    n = len(points)
    card_h = max(3.2, 0.9 + 0.55 * n)
    c = card(card_w, card_h, stroke=stroke, radius=0.22)
    t = Text(title, font=SANS, weight=BOLD, font_size=title_size, color=title_color)
    t.next_to(c.get_top(), DOWN, buff=0.35)
    pts = bullets(points, font_size=font_size, buff=0.28,
                  bullet_color=bullet_color, color=TEXT)
    pts.next_to(t, DOWN, buff=0.4, aligned_edge=LEFT)
    pts.move_to(c.get_center() + DOWN * 0.15)
    scene.play(Create(c), Write(t), FadeIn(pts, shift=UP * 0.2), run_time=1.1)
    scene.wait(wait)


def checkpoint(scene, question, answer_lines, answer_color=GREEN_LIGHT):
    """
    Insert a "Pause & Think" interlude: a question card appears, the viewer is
    given time to think, then the answer slides in. Returns nothing; plays
    animations directly on the scene.

    question:     str  — the review question
    answer_lines: list[str] — the revealed answer bullets
    """
    q_card = card(10.6, 2.6, stroke=CYAN, radius=0.18)
    q_card.move_to(UP * 0.4)

    kick = Text("PAUSE & THINK", font=SANS, weight=BOLD, font_size=20,
                color=CYAN)
    kick.next_to(q_card.get_top(), DOWN, buff=0.3)
    q = Text(question, font=SANS, weight=BOLD, font_size=22, color=TEXT,
             line_spacing=1.3)
    q.next_to(kick, DOWN, buff=0.4)
    q.move_to(q_card.get_center())

    scene.play(Create(q_card), FadeIn(kick), FadeIn(q), run_time=0.7)
    # Think time: a pulsing dot.
    dot = Dot(point=q_card.get_bottom() + DOWN * 0.55, radius=0.09,
              color=AMBER, fill_opacity=1.0)
    scene.play(FadeIn(dot), run_time=0.3)
    scene.play(dot.animate.scale(1.8).set_opacity(0.3), run_time=1.2)
    scene.play(dot.animate.scale(1 / 1.8).set_opacity(1.0), run_time=1.2)
    scene.play(FadeOut(dot), run_time=0.2)

    # Answer reveal.
    scene.play(FadeOut(q), FadeOut(kick), run_time=0.3)
    ans_title = Text("ANSWER", font=SANS, weight=BOLD, font_size=20,
                     color=answer_color)
    ans_title.next_to(q_card.get_top(), DOWN, buff=0.3)
    ans = bullets(answer_lines, font_size=20, buff=0.28,
                  bullet_color=answer_color, color=TEXT)
    ans.next_to(ans_title, DOWN, buff=0.4, aligned_edge=LEFT)
    ans.move_to(q_card.get_center() + DOWN * 0.15)
    scene.play(FadeIn(ans_title), FadeIn(ans, shift=UP * 0.15), run_time=0.7)
    scene.wait(1.4)
    scene.play(FadeOut(q_card), FadeOut(ans_title), FadeOut(ans), run_time=0.5)


def challenge(scene, prompt_lines, answer, accent=AMBER_LIGHT):
    """
    Insert a "Try It Yourself" interlude: a prompt appears, the viewer pauses to
    work it out, then the answer slides in. Plays animations directly on scene.

    prompt_lines: list[str] — the problem statement (one line per bullet)
    answer:       str      — the revealed solution
    """
    c = card(10.6, 2.8, stroke=AMBER, radius=0.18)
    c.move_to(UP * 0.3)

    kick = Text("TRY IT YOURSELF", font=SANS, weight=BOLD, font_size=20,
                color=AMBER_LIGHT)
    kick.next_to(c.get_top(), DOWN, buff=0.28)
    prompt = bullets(prompt_lines, font_size=20, buff=0.26,
                     bullet_color=AMBER, color=TEXT)
    prompt.next_to(kick, DOWN, buff=0.35, aligned_edge=LEFT)
    prompt.move_to(c.get_center() + DOWN * 0.1)

    scene.play(Create(c), FadeIn(kick), FadeIn(prompt), run_time=0.7)
    # Pause for the viewer to work it out.
    dot = Dot(point=c.get_bottom() + DOWN * 0.55, radius=0.09,
              color=AMBER, fill_opacity=1.0)
    scene.play(FadeIn(dot), run_time=0.3)
    scene.play(dot.animate.scale(1.8).set_opacity(0.3), run_time=1.4)
    scene.play(dot.animate.scale(1 / 1.8).set_opacity(1.0), run_time=1.4)
    scene.play(FadeOut(dot), run_time=0.2)

    # Reveal answer.
    scene.play(FadeOut(prompt), FadeOut(kick), run_time=0.3)
    ans_title = Text("ANSWER", font=SANS, weight=BOLD, font_size=20,
                     color=accent)
    ans_title.next_to(c.get_top(), DOWN, buff=0.28)
    ans = Text(answer, font=MONO, weight=BOLD, font_size=21, color=GREEN_LIGHT)
    ans.move_to(c.get_center() + DOWN * 0.1)
    scene.play(FadeIn(ans_title), FadeIn(ans, shift=UP * 0.15), run_time=0.7)
    scene.wait(1.5)
    scene.play(FadeOut(c), FadeOut(ans_title), FadeOut(ans), run_time=0.5)


def tex_free_number_line(x_range, length=6, include_numbers=True, **kwargs):
    """
    NumberLine configured to work without LaTeX: tick labels rendered as Text.
    """
    return NumberLine(
        x_range=x_range,
        length=length,
        include_numbers=include_numbers,
        label_constructor=Text,
        font_size=16,
        color=MUTED,
        **kwargs,
    )
