#!/usr/bin/env python3
"""
Turn a SystemVerilog sketch into a gate-level SVG.

Yosys techmap breaks operators into AND, OR, XOR, MUX, and flip-flop cells.
Graphviz draws those cells. A small module finishes well under a few seconds.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import time
from collections import Counter
from pathlib import Path

MAX_SOURCE_CHARS = 200_000
SYNTH_TIMEOUT_SEC = 20

_CELL_NODE = re.compile(
    r'^(c\d+) \[ shape=record, label="(.*?)\$\d+\\n\$_([A-Z][A-Z0-9_]*)_(.*?)",\s*\];\s*$',
    re.M,
)
_HDL_NODE = re.compile(
    r'^(c\d+) \[ shape=record, label="(.*?)\$\d+\\n\$([A-Za-z0-9_]+)(\|\{.*?\}|\|)",\s*\];\s*$',
    re.M,
)
_MODULE_NAME = re.compile(r"(?m)^\s*module\s+([A-Za-z_][A-Za-z0-9_]*)\b")
_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

# Longer prefixes first so DFFE is not classified as DFF, and NAND is not AND.
_FAMILY = (
    ("DLATCH", "LATCH"),
    ("ALDFFE", "DFF"),
    ("ALDFF", "DFF"),
    ("SDFFCE", "DFF"),
    ("SDFFE", "DFF"),
    ("SDFF", "DFF"),
    ("DFFE", "DFF"),
    ("DFF", "DFF"),
    ("NAND", "NAND"),
    ("ANDNOT", "AND"),
    ("AND", "AND"),
    ("XNOR", "XNOR"),
    ("XOR", "XOR"),
    ("NOR", "NOR"),
    ("ORNOT", "OR"),
    ("OR", "OR"),
    ("NOT", "NOT"),
    ("NMUX", "MUX"),
    ("MUX16", "MUX"),
    ("MUX8", "MUX"),
    ("MUX4", "MUX"),
    ("MUX", "MUX"),
    ("AOI4", "AOI"),
    ("AOI3", "AOI"),
    ("OAI4", "OAI"),
    ("OAI3", "OAI"),
    ("TBUF", "BUF"),
    ("SR", "LATCH"),
)

_HDL_FAMILY = {
    "add": "ADD",
    "sub": "SUB",
    "mul": "MUL",
    "div": "DIV",
    "mod": "MOD",
    "eq": "EQ",
    "ne": "NE",
    "eqx": "EQ",
    "nex": "NE",
    "lt": "CMP",
    "le": "CMP",
    "gt": "CMP",
    "ge": "CMP",
    "logic_and": "AND",
    "logic_or": "OR",
    "logic_not": "NOT",
    "and": "AND",
    "or": "OR",
    "xor": "XOR",
    "xnor": "XNOR",
    "not": "NOT",
    "mux": "MUX",
    "pmux": "MUX",
    "dff": "DFF",
    "adff": "DFF",
    "sdff": "DFF",
    "dffe": "DFF",
    "dlatch": "LATCH",
    "reduce_and": "AND",
    "reduce_or": "OR",
    "reduce_xor": "XOR",
    "reduce_bool": "OR",
    "pos": "BUF",
    "neg": "NEG",
    "shl": "SHIFT",
    "shr": "SHIFT",
    "sshl": "SHIFT",
    "sshr": "SHIFT",
    "fa": "ADD",
    "lcu": "ADD",
    "alu": "ALU",
}

# fill, stroke
_STYLE = {
    "AND": ("#dcfce7", "#15803d"),
    "NAND": ("#dcfce7", "#15803d"),
    "OR": ("#dbeafe", "#1d4ed8"),
    "NOR": ("#dbeafe", "#1d4ed8"),
    "XOR": ("#f3e8ff", "#7e22ce"),
    "XNOR": ("#f3e8ff", "#7e22ce"),
    "NOT": ("#f1f5f9", "#475569"),
    "MUX": ("#ffedd5", "#c2410c"),
    "DFF": ("#ccfbf1", "#0f766e"),
    "LATCH": ("#fee2e2", "#b91c1c"),
    "AOI": ("#fef9c3", "#a16207"),
    "OAI": ("#fef9c3", "#a16207"),
    "BUF": ("#f8fafc", "#64748b"),
    "ADD": ("#fee2e2", "#b91c1c"),
    "SUB": ("#fee2e2", "#b91c1c"),
    "MUL": ("#fee2e2", "#b91c1c"),
    "DIV": ("#fee2e2", "#b91c1c"),
    "MOD": ("#fee2e2", "#b91c1c"),
    "EQ": ("#e0e7ff", "#4338ca"),
    "NE": ("#e0e7ff", "#4338ca"),
    "CMP": ("#e0e7ff", "#4338ca"),
    "NEG": ("#f1f5f9", "#475569"),
    "SHIFT": ("#ffedd5", "#c2410c"),
    "ALU": ("#fee2e2", "#b91c1c"),
}

_SEQ_PINS = {"C": "CLK", "R": "RST", "E": "EN", "S": "SET"}


def synthesize_source(source: str, top: str | None = None) -> dict:
    """Synthesize source to an SVG plus gate counts. Never raises for user RTL errors."""
    started = time.perf_counter()

    def finish(**payload):
        payload["elapsed_ms"] = int((time.perf_counter() - started) * 1000)
        return payload

    text = source if source is not None else ""
    if not text.strip():
        return finish(ok=False, error="Paste a SystemVerilog module, then click Generate.")
    if len(text) > MAX_SOURCE_CHARS:
        return finish(ok=False, error="That sketch is too large for this playground. Keep it under 200 KB.")

    top_name = (top or "").strip()
    if top_name and not _IDENT.fullmatch(top_name):
        return finish(ok=False, error="Top module name must be a Verilog identifier.")

    if shutil.which("yosys") is None:
        return finish(ok=False, error="Yosys is not on PATH. Install it with: brew install yosys")
    if shutil.which("dot") is None:
        return finish(ok=False, error="Graphviz is not on PATH. Install it with: brew install graphviz")

    modules = _MODULE_NAME.findall(text)
    if not modules:
        return finish(ok=False, error="No module found. Start with module name ( ... ); and end with endmodule.")
    if top_name and top_name not in modules:
        found = ", ".join(modules)
        return finish(ok=False, error=f"Top module '{top_name}' is not in this file. Modules found: {found}.")

    hierarchy = f"hierarchy -top {top_name}" if top_name else "hierarchy -auto-top"
    script = "\n".join([
        "read_verilog -sv design.sv",
        hierarchy,
        "proc",
        "flatten",
        "opt",
        "fsm",
        "opt",
        "memory",
        "opt",
        "techmap",
        "opt_clean",
        "stat",
        "show -format dot -prefix schematic -notitle",
        "",
    ])

    try:
        with tempfile.TemporaryDirectory(prefix="gate-schematic-") as tmp:
            work = Path(tmp)
            (work / "design.sv").write_text(text, encoding="utf-8")
            (work / "run.ys").write_text(script, encoding="utf-8")
            try:
                proc = subprocess.run(
                    ["yosys", "-q", "run.ys"],
                    cwd=work,
                    capture_output=True,
                    text=True,
                    timeout=SYNTH_TIMEOUT_SEC,
                )
            except subprocess.TimeoutExpired:
                return finish(
                    ok=False,
                    error="Synthesis took more than 20 seconds. Generate a smaller module.",
                )

            log = (proc.stdout or "") + "\n" + (proc.stderr or "")
            messages = _extract_messages(log)
            dot_path = work / "schematic.dot"
            if proc.returncode != 0 or not dot_path.exists():
                error = "\n".join(messages) if messages else _tail(log)
                if not error.strip():
                    error = "Yosys could not synthesize this sketch."
                if not top_name and "top module" in error.lower() and modules:
                    error += "\nModules found: " + ", ".join(modules) + ". Set the top module and Generate again."
                return finish(ok=False, error=error)

            styled, groups = _restyle_dot(dot_path.read_text(encoding="utf-8"))
            styled_path = work / "schematic.styled.dot"
            styled_path.write_text(styled, encoding="utf-8")
            svg_path = work / "schematic.svg"
            draw = subprocess.run(
                ["dot", "-Tsvg", str(styled_path), "-o", str(svg_path)],
                capture_output=True,
                text=True,
                timeout=SYNTH_TIMEOUT_SEC,
            )
            if draw.returncode != 0 or not svg_path.exists():
                detail = (draw.stderr or draw.stdout or "Graphviz failed").strip()
                return finish(ok=False, error=detail[-2000:])

            svg = svg_path.read_text(encoding="utf-8")
    except OSError as exc:
        return finish(ok=False, error=f"Could not run synthesis: {exc}")

    stat_top = _stat_module(log)
    resolved_top = top_name or stat_top or (modules[-1] if len(modules) == 1 else "")
    cells = _cell_rows(groups)
    notes = _notes(cells)
    warnings = [m for m in messages if m.lower().startswith("warning")]

    return finish(
        ok=True,
        svg=svg,
        top=resolved_top,
        cells=cells,
        gate_count=sum(row["count"] for row in cells),
        warnings=warnings,
        notes=notes,
    )


def _family(token: str) -> str:
    for prefix, name in _FAMILY:
        if token == prefix or token.startswith(prefix + "_") or token.startswith(prefix):
            return name
    return token


def _seq_detail(token: str) -> str | None:
    match = re.fullmatch(r"DFF_([PN])", token)
    if match:
        return "posedge clock" if match.group(1) == "P" else "negedge clock"
    match = re.fullmatch(r"DFF_([PN])([PN])([01])", token)
    if match:
        clock = "posedge" if match.group(1) == "P" else "negedge"
        reset = "async reset" if match.group(2) == "P" else "async active-low reset"
        return f"{clock} clock, {reset} to {match.group(3)}"
    match = re.fullmatch(r"DFFE_([PN])([PN])", token)
    if match:
        clock = "posedge" if match.group(1) == "P" else "negedge"
        enable = "active-high enable" if match.group(2) == "P" else "active-low enable"
        return f"{clock} clock, {enable}"
    if token.startswith("DLATCH") or token.startswith("SR"):
        return "level-sensitive latch"
    return None


def _rename_seq_pins(fragment: str) -> str:
    def repl(match: re.Match) -> str:
        pin = match.group(2)
        return match.group(1) + _SEQ_PINS.get(pin, pin)

    return re.sub(r"(> )([A-Z]+)(?=[|}])", repl, fragment)


def _paint(node_id: str, label: str, kind: str) -> str:
    fill, stroke = _STYLE.get(kind, ("#f8fafc", "#334155"))
    return (
        f'{node_id} [ shape=record, style=filled, fillcolor="{fill}", '
        f'color="{stroke}", fontcolor="#0f172a", penwidth=1.6, fontsize=14, '
        f'label="{label}" ];'
    )


def _restyle_dot(dot: str) -> tuple[str, list[tuple[str, str | None]]]:
    groups: list[tuple[str, str | None]] = []

    def paint_gate(match: re.Match) -> str:
        token = match.group(3)
        kind = _family(token)
        detail = _seq_detail(token)
        groups.append((kind, detail))
        left, right = match.group(2), match.group(4)
        if kind in {"DFF", "LATCH"}:
            left, right = _rename_seq_pins(left), _rename_seq_pins(right)
        return _paint(match.group(1), f"{left}{kind}{right}", kind)

    def paint_hdl(match: re.Match) -> str:
        token = match.group(3)
        kind = _HDL_FAMILY.get(token, token.upper())
        groups.append((kind, None))
        return _paint(match.group(1), f"{match.group(2)}{kind}{match.group(4)}", kind)

    styled = _CELL_NODE.sub(paint_gate, dot)
    styled = _HDL_NODE.sub(paint_hdl, styled)
    styled = re.sub(
        r'\[ shape=octagon, label="([^"]*)", color="black", fontcolor="black" \]',
        r'[ shape=octagon, style=filled, fillcolor="#e0f2fe", color="#0369a1", fontcolor="#0c4a6e", penwidth=1.4, label="\1" ]',
        styled,
    )
    styled = re.sub(
        r'^(v\d+) \[ label="([^"]*)" \];\s*$',
        lambda m: (
            f'{m.group(1)} [ label="{m.group(2)}", shape=box, style=filled, '
            f'fillcolor="#fef9c3", color="#a16207", fontcolor="#713f12", fontsize=11 ];'
        ),
        styled,
        flags=re.M,
    )
    styled = re.sub(
        r'\[ shape=record, style=rounded, label="([^"]*)", color="black", fontcolor="black" \]',
        r'[ shape=record, style="rounded,filled", fillcolor="#f8fafc", color="#cbd5e1", fontcolor="#64748b", fontsize=10, label="\1" ]',
        styled,
    )
    styled = styled.replace('color="black"', 'color="#64748b"')
    styled = styled.replace(
        'rankdir="LR";\nremincross=true;',
        "\n".join([
            'rankdir="LR";',
            "remincross=true;",
            'bgcolor="white";',
            'nodesep=0.28;',
            'ranksep=0.55;',
            'node [fontname="Helvetica"];',
            'edge [fontname="Helvetica"];',
        ]),
        1,
    )
    return styled, groups


def _cell_rows(groups: list[tuple[str, str | None]]) -> list[dict]:
    counts: Counter[tuple[str, str | None]] = Counter(groups)
    order = list(dict.fromkeys(groups))
    rows = []
    for key in order:
        name, detail = key
        rows.append({"name": name, "count": counts[key], "detail": detail})
    return rows


def _notes(cells: list[dict]) -> list[str]:
    notes = []
    latch_count = sum(row["count"] for row in cells if row["name"] == "LATCH")
    if latch_count:
        notes.append(
            "Yosys inferred a latch. A signal assigned on only some paths of an always block "
            "keeps its old value, so it becomes memory. Assign it on every path, or use always_ff for a flip-flop."
        )
    high_level = [row["name"] for row in cells if row["name"] in {"ADD", "MUL", "DIV", "ALU", "SUB"}]
    if high_level:
        names = ", ".join(sorted(set(high_level)))
        notes.append(f"Yosys left {names} as a block instead of breaking it into gates.")
    if not cells:
        notes.append("No gates left. Yosys folded this description into wires.")
    return notes


def _extract_messages(log: str) -> list[str]:
    found = []
    for raw in log.splitlines():
        line = raw.strip()
        if not line:
            continue
        if "ERROR:" in line or line.startswith("Warning:") or "syntax error" in line.lower():
            line = re.sub(r"design\.sv:(\d+):", r"Line \1:", line)
            if line not in found:
                found.append(line)
        if len(found) >= 20:
            break
    return found


def _stat_module(log: str) -> str:
    match = re.search(r"(?m)^=== (\S+) ===", log)
    return match.group(1) if match else ""


def _tail(log: str) -> str:
    lines = [line.strip() for line in log.splitlines() if line.strip()]
    skip = ("executing", "generating", "using ", "continuing", "end of script", "time spent", "yosys ")
    useful = [line for line in lines if not line.lower().startswith(skip)]
    chosen = useful or lines
    return "\n".join(chosen[-12:])
