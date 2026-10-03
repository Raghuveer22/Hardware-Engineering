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
import textwrap

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
# DESIGN TOKENS: SPACING, TYPOGRAPHY & MOTION SCALES (Zero-Hardcoding Scales)
# ---------------------------------------------------------------------------
# Spacing scale (multiples of Manim viewport grid units)
SPACE_XS   = 0.10
SPACE_SM   = 0.20
SPACE_MD   = 0.40
SPACE_LG   = 0.80
SPACE_XL   = 1.40

# Typographic scale
FONT_MICRO = 10
FONT_TINY  = 12
FONT_BADGE = 14
FONT_CAPTION = 16
FONT_BODY  = 20
FONT_SUBHEAD = 24
FONT_TITLE = 30
FONT_HERO  = 40

# Motion duration tokens (seconds)
RATE_SNAP   = 0.20  # Instantaneous clock ticks, bit toggles
RATE_FAST   = 0.40  # Snappy transitions, packet step
RATE_NORMAL = 0.80  # Standard animations, transforms
RATE_SLOW   = 1.40  # Dramatic reveals, camera zoom-ins, circuit unfold

# Stage chrome. The constraint solver reads these; scenes do not copy them.
BANNER_HEIGHT = 1.05
TAKEAWAY_HEIGHT = 1.15


# ---------------------------------------------------------------------------
# REUSABLE CONSTRUCTORS
# ---------------------------------------------------------------------------

def set_dark(camera):
    """Apply the series background to a Scene's camera."""
    camera.background_color = BG


def fit_width(mob, max_width):
    """Scale a mobject down if it exceeds max_width. Returns the mobject."""
    if mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    return mob


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
    max_inner_w = card_w - 0.8
    if t.width > max_inner_w:
        t.scale_to_fit_width(max_inner_w)
    t.next_to(c.get_top(), DOWN, buff=0.35)
    pts = bullets(points, font_size=font_size, buff=0.28,
                  bullet_color=bullet_color, color=TEXT)
    if pts.width > max_inner_w:
        pts.scale_to_fit_width(max_inner_w)
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
    max_q_w = 10.6 - 0.8
    if q.width > max_q_w:
        q.scale_to_fit_width(max_q_w)
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
    max_ans_w = 10.6 - 0.8
    if ans.width > max_ans_w:
        ans.scale_to_fit_width(max_ans_w)
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
    max_inner_w = 10.6 - 0.8
    if prompt.width > max_inner_w:
        prompt.scale_to_fit_width(max_inner_w)
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
    if ans.width > max_inner_w:
        ans.scale_to_fit_width(max_inner_w)
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


# ---------------------------------------------------------------------------
# LONG-FORM VIDEO PEDAGOGICAL WIDGETS (CSE / SOFTWARE-TO-HARDWARE)
# ---------------------------------------------------------------------------

def narration_banner(text, font_size=15, width=None, height=None, color=TEXT,
                     accent=CYAN):
    """
    Sleek bottom-third caption bar displaying timed narrative guidance.
    Width follows the camera frame unless the stage solver passes one.
    """
    if width is None:
        width = config.frame_width - 2 * SPACE_LG
    if height is None:
        height = BANNER_HEIGHT
    bg = RoundedRectangle(
        corner_radius=0.15, width=width, height=height,
        stroke_color=BORDER, stroke_width=1.5,
        fill_color="#0b1120", fill_opacity=0.92,
    ).to_edge(DOWN, buff=SPACE_MD)

    pip = Dot(point=bg.get_left() + RIGHT * 0.35, radius=0.07, color=accent)
    pip.match_y(bg)

    wrapped = textwrap.fill(text, width=76)
    t = Text(wrapped, font=SANS, font_size=font_size, color=color, line_spacing=1.15)
    max_w = width - 1.2
    max_h = height - 0.35
    if t.width > max_w:
        t.scale_to_fit_width(max_w)
    if t.height > max_h:
        t.scale_to_fit_height(max_h)
    t.next_to(pip, RIGHT, buff=0.25)
    t.match_y(bg)

    return VGroup(bg, pip, t)


def takeaway_callout(text, color=CYAN, font_size=17, width=None, height=None):
    """
    Transition "takeaway" bar shown at the END of an act, before moving to the
    next stage: a one-line "so the point is..." summary that bridges acts and
    gives the viewer time to absorb the concept before the next depth jump.
    """
    if width is None:
        width = config.frame_width - 2 * SPACE_XL
    if height is None:
        height = TAKEAWAY_HEIGHT
    c = card(width, height, stroke=color, radius=0.15)
    pip = Dot(point=c.get_left() + RIGHT * 0.32, radius=0.06, color=color)
    pip.match_y(c)

    t = Text(text, font=SANS, weight=BOLD, font_size=font_size, color=TEXT)
    max_w = width - 1.1
    if t.width > max_w:
        t.scale_to_fit_width(max_w)
    t.next_to(pip, RIGHT, buff=0.25)
    t.match_y(c)

    return VGroup(c, pip, t)


def code_window(code_lines, title_text="PYTORCH / SOFTWARE", width=5.6, height=3.6,
                font_size=13, title_color=CYAN):
    """
    Terminal / IDE code window with title bar, window controls, and syntax lines.
    Automatically handles indentation, empty spacer lines, and dynamic height fitting.
    """
    sample_char = Text("M", font=MONO, font_size=font_size)
    char_w = sample_char.width
    line_h = sample_char.height

    lines_vg = VGroup()
    for item in code_lines:
        if isinstance(item, tuple):
            text_str, line_col = item
        else:
            text_str, line_col = item, TEXT

        # Handle empty lines with invisible spacer
        if not text_str or not text_str.strip():
            spacer = Rectangle(width=char_w, height=line_h, stroke_width=0, fill_opacity=0)
            lines_vg.add(spacer)
            continue

        stripped = text_str.lstrip(" ")
        num_spaces = len(text_str) - len(stripped)
        txt = Text(stripped, font=MONO, font_size=font_size, color=line_col)

        if num_spaces > 0:
            indent = Rectangle(width=num_spaces * char_w * 0.95, height=line_h, stroke_width=0, fill_opacity=0)
            line_unit = VGroup(indent, txt).arrange(RIGHT, buff=0)
            lines_vg.add(line_unit)
        else:
            lines_vg.add(txt)

    lines_vg.arrange(DOWN, aligned_edge=LEFT, buff=0.15)

    req_h = lines_vg.height + 0.55 + 0.55
    actual_h = max(height, req_h)

    win = RoundedRectangle(
        corner_radius=0.18, width=width, height=actual_h,
        stroke_color=BORDER, stroke_width=1.5,
        fill_color="#0d1525", fill_opacity=0.96,
    )
    bar = RoundedRectangle(
        corner_radius=0.18, width=width, height=0.55,
        stroke_color=BORDER, stroke_width=1.0,
        fill_color="#1e293b", fill_opacity=0.95,
    ).align_to(win, UP)

    # Window dots (Mac style)
    dots = VGroup(
        Dot(radius=0.07, color=RED),
        Dot(radius=0.07, color=AMBER),
        Dot(radius=0.07, color=GREEN),
    ).arrange(RIGHT, buff=0.12)
    dots.move_to(bar).align_to(bar, LEFT).shift(RIGHT * 0.25)

    ttl = Text(title_text, font=MONO, weight=BOLD, font_size=13, color=title_color)
    max_title_w = width - 1.6  # Leave room for window dots
    if ttl.width > max_title_w:
        ttl.scale_to_fit_width(max_title_w)
    ttl.move_to(bar)

    max_code_w = width - 0.7
    if lines_vg.width > max_code_w:
        lines_vg.scale_to_fit_width(max_code_w)

    lines_vg.next_to(bar, DOWN, buff=0.25).align_to(win, LEFT).shift(RIGHT * 0.35)

    return VGroup(win, bar, dots, ttl, lines_vg)



def metric_card(value, label, subtext="", color=CYAN, width=3.4, height=1.9):
    """
    High-contrast stat card highlighting 1000x improvements, area, or energy.
    """
    c = card(width, height, stroke=color, radius=0.18)
    val = Text(value, font=SANS, weight=BOLD, font_size=28, color=color)
    val.move_to(c.get_center() + UP * 0.25)
    max_inner_w = width - 0.5
    if val.width > max_inner_w:
        val.scale_to_fit_width(max_inner_w)
    lbl = Text(label, font=SANS, weight=BOLD, font_size=14, color=WHITE)
    lbl.next_to(val, DOWN, buff=0.15)
    if lbl.width > max_inner_w:
        lbl.scale_to_fit_width(max_inner_w)
    if subtext:
        sub = Text(subtext, font=MONO, font_size=12, color=MUTED)
        if sub.width > max_inner_w:
            sub.scale_to_fit_width(max_inner_w)
        sub.next_to(lbl, DOWN, buff=0.1)
        return VGroup(c, val, lbl, sub)
    return VGroup(c, val, lbl)


# ---------------------------------------------------------------------------
# KINETIC INTERACTIVE HARDWARE WIDGETS
# ---------------------------------------------------------------------------

class BitRegister(VGroup):
    """
    An N-bit digital hardware register with individually addressable bit cells.
    Supports MSB highlighting, carry propagation visual, and dynamic updates.
    """
    def __init__(self, width_bits=8, initial_val="00000000", cell_width=0.65,
                 cell_height=0.8, highlight_msb=True, msb_color=RED, cell_color=CYAN,
                 bg_color="#0d1525", **kwargs):
        super().__init__(**kwargs)
        self.width_bits = width_bits
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.highlight_msb = highlight_msb
        self.msb_color = msb_color
        self.cell_color = cell_color
        self.bg_color = bg_color

        self.cells = []
        self.bit_texts = []

        val_str = initial_val.zfill(width_bits)[-width_bits:]

        for i in range(width_bits):
            is_msb = (i == 0) and highlight_msb
            stroke_col = msb_color if is_msb else BORDER
            rect = RoundedRectangle(
                corner_radius=0.08, width=cell_width, height=cell_height,
                stroke_color=stroke_col, stroke_width=2.0 if is_msb else 1.2,
                fill_color=self.bg_color, fill_opacity=0.95
            )
            bit_char = val_str[i]
            txt_col = msb_color if is_msb else (CYAN_LIGHT if bit_char == '1' else MUTED)
            txt = Text(bit_char, font=MONO, weight=BOLD, font_size=24, color=txt_col)
            txt.move_to(rect)

            # Bit index label below cell (e.g. [7] for MSB, [0] for LSB)
            idx_num = width_bits - 1 - i
            idx_lbl = Text(f"[{idx_num}]", font=MONO, font_size=11, color=FAINT)
            idx_lbl.next_to(rect, DOWN, buff=0.1)

            cell_unit = VGroup(rect, txt, idx_lbl)
            self.cells.append(rect)
            self.bit_texts.append(txt)
            self.add(cell_unit)

        self.arrange(RIGHT, buff=0.08)

    def get_bit_text(self, index_from_left):
        return self.bit_texts[index_from_left]

    def update_bits(self, new_val_str):
        """Returns animation transforms for changing bit values."""
        padded = new_val_str.zfill(self.width_bits)[-self.width_bits:]
        anims = []
        for i, char in enumerate(padded):
            is_msb = (i == 0) and self.highlight_msb
            col = self.msb_color if is_msb else (CYAN_LIGHT if char == '1' else MUTED)
            new_txt = Text(char, font=MONO, weight=BOLD, font_size=24, color=col).move_to(self.cells[i])
            anims.append(Transform(self.bit_texts[i], new_txt))
        return anims


class DynamicBarChartWidget(VGroup):
    """
    Animated bar chart for visualizing transformer logits, exponential scaling,
    and probability normalization.
    """
    def __init__(self, values, labels, max_val=50.0, chart_width=6.0, chart_height=3.2,
                 bar_color=CYAN, **kwargs):
        super().__init__(**kwargs)
        self.chart_width = chart_width
        self.chart_height = chart_height
        self.max_val = max_val
        self.bar_color = bar_color

        # Base axis line
        self.baseline = Line(LEFT * (chart_width / 2), RIGHT * (chart_width / 2),
                             color=BORDER, stroke_width=2.5)
        self.add(self.baseline)

        self.bars = []
        self.labels = []
        self.val_texts = []

        n = len(values)
        bar_w = (chart_width / n) * 0.55
        spacing = chart_width / n

        for i, (v, lbl_str) in enumerate(zip(values, labels)):
            x_pos = -chart_width / 2 + (i + 0.5) * spacing
            norm_h = max(0.08, min(chart_height, (abs(v) / max_val) * chart_height))
            
            bar = RoundedRectangle(
                corner_radius=0.06, width=bar_w, height=norm_h,
                stroke_color=bar_color, stroke_width=1.5,
                fill_color=bar_color, fill_opacity=0.75
            )
            # Anchor bottom to baseline
            bar.move_to(np.array([x_pos, norm_h / 2, 0]))

            lbl = Text(lbl_str, font=MONO, font_size=13, color=MUTED)
            lbl.next_to(np.array([x_pos, 0, 0]), DOWN, buff=0.18)

            val_t = Text(f"{v:.1f}" if isinstance(v, float) else str(v),
                         font=MONO, weight=BOLD, font_size=13, color=WHITE)
            val_t.next_to(bar, UP, buff=0.1)

            self.bars.append(bar)
            self.labels.append(lbl)
            self.val_texts.append(val_t)
            self.add(bar, lbl, val_t)


class ClockWaveform(VGroup):
    """
    Digital square clock waveform with rising edge triggers.
    """
    def __init__(self, cycles=3, width=4.8, height=0.9, color=GREEN, **kwargs):
        super().__init__(**kwargs)
        period = width / cycles
        half = period / 2

        path_points = []
        curr_x = -width / 2
        for _ in range(cycles):
            # Low
            path_points.append(np.array([curr_x, -height/2, 0]))
            path_points.append(np.array([curr_x + half, -height/2, 0]))
            # Rising edge
            path_points.append(np.array([curr_x + half, height/2, 0]))
            # High
            path_points.append(np.array([curr_x + period, height/2, 0]))
            # Falling edge
            path_points.append(np.array([curr_x + period, -height/2, 0]))
            curr_x += period

        wave = VMobject(color=color, stroke_width=2.5)
        wave.set_points_as_corners(path_points)

        lbl = Text("CLK (posedge ↑)", font=MONO, weight=BOLD, font_size=13, color=color)
        lbl.next_to(wave, LEFT, buff=0.2)

        self.add(wave, lbl)
        self.wave = wave


class LiquidTankWidget(VGroup):
    """
    Graduated liquid reservoir / tank widget for visualizing accumulator headroom
    and register capacity overflow.
    """
    def __init__(self, capacity=32767, width=2.4, height=3.2, title="16-BIT TANK",
                 tank_color=BORDER, fluid_color=CYAN, **kwargs):
        super().__init__(**kwargs)
        self.capacity = capacity
        self._tank_width = width
        self._tank_height = height
        self.tank_color = tank_color
        self.fluid_color = fluid_color

        # Outer glass beaker / tank frame (left wall, bottom, right wall)
        tank_walls = VMobject(color=tank_color, stroke_width=3.0)
        tank_walls.set_points_as_corners([
            np.array([-width/2, height/2, 0]),
            np.array([-width/2, -height/2, 0]),
            np.array([width/2, -height/2, 0]),
            np.array([width/2, height/2, 0])
        ])

        # Title at top
        t_lbl = Text(title, font=MONO, weight=BOLD, font_size=13, color=WHITE)
        t_lbl.next_to(tank_walls, UP, buff=0.15)

        # Baseline fill (empty)
        self.fluid = Rectangle(
            width=width - 0.15, height=0.05,
            stroke_width=0, fill_color=fluid_color, fill_opacity=0.75
        )
        self.fluid.move_to(tank_walls.get_bottom() + UP * (0.05 / 2 + 0.02))

        # Max capacity line
        max_line = DashedLine(
            np.array([-width/2, height/2 - 0.2, 0]),
            np.array([width/2, height/2 - 0.2, 0]),
            color=RED, stroke_width=2.0
        )
        cap_lbl = Text(f"MAX: {capacity:,}", font=MONO, font_size=11, color=RED_LIGHT)
        cap_lbl.next_to(max_line, RIGHT, buff=0.1)

        self.tank_walls = tank_walls
        self.max_line = max_line
        self.add(tank_walls, t_lbl, self.fluid, max_line, cap_lbl)

    def set_fluid_fraction(self, frac, color=None):
        """Returns animation to adjust fluid height."""
        clamped_frac = max(0.01, min(1.2, frac))
        new_h = self._tank_height * 0.9 * clamped_frac
        fill_col = color if color is not None else self.fluid_color
        new_fluid = Rectangle(
            width=self._tank_width - 0.15, height=new_h,
            stroke_width=0, fill_color=fill_col, fill_opacity=0.85
        )
        cx = self.tank_walls.get_center()[0]
        bot_y = self.tank_walls.get_bottom()[1]
        new_fluid.move_to(np.array([cx, bot_y + new_h / 2 + 0.05, 0]))
        return Transform(self.fluid, new_fluid)



