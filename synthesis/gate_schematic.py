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
# Ripple-mapped full adder: {{<p12> a|...}|$add.bit[0].fa\nFA|{<p9> sum|...}}
_FA_NODE = re.compile(
    r'^(c\d+) \[ shape=record, label="\{\{(?P<ins>.*?)\}\|(?P<inst>.*?)\\nFA\|\{(?P<outs>.*?)\}\}",\s*\];\s*$',
    re.M,
)
_FA_PORT = re.compile(r"<p\d+> [A-Za-z0-9_]+")
_MODULE_NAME = re.compile(r"(?m)^\s*module\s+([A-Za-z_][A-Za-z0-9_]*)\b")
_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_PORT_TYPE_WORDS = frozenset(
    {"wire", "logic", "reg", "integer", "int", "bit", "byte", "signed", "unsigned", "ref"}
)
# Compact one-line ports are common while teaching: input logic [7:0]a
# Also accept the student form name[7:0] and normalize it for the box view.
_PORT_DECL = re.compile(
    r"(?P<dir>input|output|inout)\b"
    r"(?:\s+(?:wire|logic|reg|integer|int|bit|byte|signed|unsigned|ref))*"
    r"(?:\s*\[(?P<pre_width>[^\]]+)\])?"
    r"\s*(?P<names>[A-Za-z_][A-Za-z0-9_]*"
    r"(?:\s*,\s*(?!(?:input|output|inout)\b)[A-Za-z_][A-Za-z0-9_]*)*)"
    r"(?:\s*\[(?P<post_width>[^\]]+)\])?"
)
_BODY_LOGIC = re.compile(r"(?m)^\s*(assign|always|always_comb|always_ff|always_latch)\b")
_BODY_INSTANCE = re.compile(r"(?m)^\s*[A-Za-z_][A-Za-z0-9_]*\s+(?:#\s*\([^;]*\)\s*)?[A-Za-z_][A-Za-z0-9_]*\s*\(")

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
    "fa": "FA",
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
    "FA": ("#ffe4e6", "#be123c"),
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


_FA_BLACKBOX = """\
(* blackbox *)
module FA(input a, input b, input cin, output sum, output cout);
endmodule
"""

# Map $add onto a ripple of 1-bit full adders. Cin of bit 0 is 0.
_RIPPLE_ADD_MAP = r"""
(* techmap_celltype = "$add" *)
module _add_ripple (A, B, Y);
    parameter A_SIGNED = 0;
    parameter B_SIGNED = 0;
    parameter A_WIDTH = 1;
    parameter B_WIDTH = 1;
    parameter Y_WIDTH = 1;

    (* force_downto *)
    input [A_WIDTH-1:0] A;
    (* force_downto *)
    input [B_WIDTH-1:0] B;
    (* force_downto *)
    output [Y_WIDTH-1:0] Y;

    (* force_downto *)
    wire [Y_WIDTH-1:0] AA, BB;
    (* force_downto *)
    wire [Y_WIDTH:0] carry;

    generate
        if (A_WIDTH >= Y_WIDTH)
            assign AA = A[Y_WIDTH-1:0];
        else if (A_SIGNED)
            assign AA = {{(Y_WIDTH-A_WIDTH){A[A_WIDTH-1]}}, A};
        else
            assign AA = {{(Y_WIDTH-A_WIDTH){1'b0}}, A};

        if (B_WIDTH >= Y_WIDTH)
            assign BB = B[Y_WIDTH-1:0];
        else if (B_SIGNED)
            assign BB = {{(Y_WIDTH-B_WIDTH){B[B_WIDTH-1]}}, B};
        else
            assign BB = {{(Y_WIDTH-B_WIDTH){1'b0}}, B};
    endgenerate

    assign carry[0] = 1'b0;

    genvar i;
    generate
        for (i = 0; i < Y_WIDTH; i = i + 1) begin : bit
            FA fa (
                .a(AA[i]),
                .b(BB[i]),
                .cin(carry[i]),
                .sum(Y[i]),
                .cout(carry[i+1])
            );
        end
    endgenerate
endmodule
"""


def synthesize_source(
    source: str,
    top: str | None = None,
    expand_adders: bool = False,
    box_only: bool = False,
) -> dict:
    """Synthesize source to an SVG plus cell counts. Never raises for user RTL errors.

    expand_adders keeps each addition as a ripple of 1-bit full adders instead of
    breaking it into AND, OR, and XOR gates. Other operators stay as blocks.

    box_only draws the module as a port box (highest-level view) without Yosys.
    Empty modules also fall back to that box view instead of failing.
    """
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

    modules = _MODULE_NAME.findall(text)
    if not modules:
        return finish(ok=False, error="No module found. Start with module name ( ... ); and end with endmodule.")
    if top_name and top_name not in modules:
        found = ", ".join(modules)
        return finish(ok=False, error=f"Top module '{top_name}' is not in this file. Modules found: {found}.")

    resolved_top = top_name or (modules[0] if len(modules) == 1 else "")
    if not resolved_top and len(modules) > 1:
        return finish(
            ok=False,
            error="Modules found: " + ", ".join(modules) + ". Set the top module and Generate again.",
        )

    ports = _module_ports(text, resolved_top)
    if box_only or _module_body_empty(text, resolved_top):
        ops = _rtl_operator_blocks(text, resolved_top)
        note = (
            "Hierarchical module view (Vivado-style). Click + on the box to open RTL internals."
            if box_only
            else "Empty module body — showing the chip box. Click + after you add assign / always_comb logic."
        )
        svg = _box_level_svg(resolved_top, ports, ops)
        return finish(
            ok=True,
            svg=svg,
            html=_box_level_html(resolved_top, ports, ops),
            top=resolved_top,
            cells=[{"name": op["kind"], "count": 1, "detail": op.get("expr")} for op in ops],
            gate_count=0,
            warnings=[],
            notes=[note],
            view="box",
            format="html",
        )

    if shutil.which("yosys") is None:
        return finish(ok=False, error="Yosys is not on PATH. Install it with: brew install yosys")
    if shutil.which("dot") is None:
        return finish(ok=False, error="Graphviz is not on PATH. Install it with: brew install graphviz")

    hierarchy = f"hierarchy -top {resolved_top}"
    show_target = resolved_top
    show = "show -format dot -prefix schematic -notitle"
    if expand_adders and show_target:
        show = f"show -format dot -prefix schematic -notitle {show_target}"
    if expand_adders:
        tail = [
            "read_verilog -sv full_adder_bb.v",
            "techmap -map ripple_add.v",
            "opt_clean",
            "stat",
            show,
        ]
    else:
        tail = [
            "techmap",
            "opt_clean",
            "stat",
            show,
        ]
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
        *tail,
        "",
    ])

    try:
        with tempfile.TemporaryDirectory(prefix="gate-schematic-") as tmp:
            work = Path(tmp)
            (work / "design.sv").write_text(text, encoding="utf-8")
            (work / "run.ys").write_text(script, encoding="utf-8")
            if expand_adders:
                (work / "full_adder_bb.v").write_text(_FA_BLACKBOX, encoding="utf-8")
                (work / "ripple_add.v").write_text(_RIPPLE_ADD_MAP, encoding="utf-8")
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
                # Empty / optimized-away netlist: teach with the module box instead of failing.
                if _is_empty_netlist_error(error):
                    ops = _rtl_operator_blocks(text, resolved_top)
                    svg = _box_level_svg(resolved_top, ports, ops)
                    return finish(
                        ok=True,
                        svg=svg,
                        html=_box_level_html(resolved_top, ports, ops),
                        top=resolved_top,
                        cells=[{"name": op["kind"], "count": 1, "detail": op.get("expr")} for op in ops],
                        gate_count=0,
                        warnings=[m for m in messages if m.lower().startswith("warning")],
                        notes=[
                            "No gate netlist — showing hierarchical module box. "
                            "Click + to open RTL internals, or pass --box for this view on purpose."
                        ],
                        view="box",
                        format="html",
                    )
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
            if expand_adders:
                svg = _attach_fa_expanders(svg)
    except OSError as exc:
        return finish(ok=False, error=f"Could not run synthesis: {exc}")

    stat_top = _stat_module(log)
    resolved_top = top_name or stat_top or resolved_top
    cells = _cell_rows(groups)
    notes = _notes(cells)
    warnings = [m for m in messages if m.lower().startswith("warning")]

    return finish(
        ok=True,
        svg=svg,
        html=_wrap_schematic_html(resolved_top or "schematic", svg),
        top=resolved_top,
        cells=cells,
        gate_count=sum(row["count"] for row in cells),
        warnings=warnings,
        notes=notes,
        view="gates",
        format="html",
    )


def _matching_paren(text: str, open_idx: int) -> int:
    depth = 0
    for i in range(open_idx, len(text)):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
    return -1


def _module_header_span(text: str, name: str) -> tuple[int, int] | None:
    match = re.search(rf"(?m)^\s*module\s+{re.escape(name)}\b", text)
    if not match:
        return None
    i = match.end()
    while i < len(text) and text[i].isspace():
        i += 1
    if i < len(text) and text[i] == "#":
        while i < len(text) and text[i] != "(":
            i += 1
        if i >= len(text) or text[i] != "(":
            return None
        close = _matching_paren(text, i)
        if close < 0:
            return None
        i = close + 1
        while i < len(text) and text[i].isspace():
            i += 1
    if i >= len(text) or text[i] != "(":
        return None
    close = _matching_paren(text, i)
    if close < 0:
        return None
    return i + 1, close


def _module_ports(text: str, name: str) -> list[dict]:
    span = _module_header_span(text, name)
    if not span:
        return []
    port_text = text[span[0] : span[1]]
    ports: list[dict] = []
    for match in _PORT_DECL.finditer(port_text):
        direction = match.group("dir")
        width = (match.group("pre_width") or match.group("post_width") or "").strip()
        for raw in match.group("names").split(","):
            pname = raw.strip()
            if not pname or pname in _PORT_TYPE_WORDS or pname in {"input", "output", "inout"}:
                continue
            label = f"{pname}[{width}]" if width else pname
            ports.append({"name": pname, "direction": direction, "width": width, "label": label})
    return ports


def _module_body_empty(text: str, name: str) -> bool:
    span = _module_header_span(text, name)
    if not span:
        # module adder; with no port list — treat as empty shell if no logic keywords
        start = re.search(rf"(?m)^\s*module\s+{re.escape(name)}\b", text)
        if not start:
            return True
        body_start = text.find(";", start.end())
        if body_start < 0:
            return True
        body_start += 1
    else:
        semi = text.find(";", span[1])
        if semi < 0:
            return True
        body_start = semi + 1
    end = re.search(r"(?m)^\s*endmodule\b", text[body_start:])
    if not end:
        return True
    body = text[body_start : body_start + end.start()]
    # Strip block and line comments before looking for logic.
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    body = re.sub(r"//.*?$", "", body, flags=re.M)
    if _BODY_LOGIC.search(body):
        return False
    if _BODY_INSTANCE.search(body):
        return False
    return True


def _is_empty_netlist_error(error: str) -> bool:
    lower = error.lower()
    return (
        "nothing there to show" in lower
        or "did not match any module" in lower
        or "can't find module" in lower
    )


def _escape_xml(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


_ASSIGN_STMT = re.compile(r"(?m)^\s*assign\s+(.+?)\s*;")
_EQ_STMT = re.compile(r"(?m)^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+?)\s*;")
_BIN_EXPR = re.compile(
    r"^([A-Za-z_][A-Za-z0-9_]*(?:\s*\[[^\]]+\])?)\s*"
    r"([+\-*/]|&&|\|\||&|\||\^)\s*"
    r"([A-Za-z_][A-Za-z0-9_]*(?:\s*\[[^\]]+\])?)$"
)
_OP_KIND = {
    "+": "ADD",
    "-": "SUB",
    "*": "MUL",
    "/": "DIV",
    "&": "AND",
    "|": "OR",
    "^": "XOR",
    "&&": "AND",
    "||": "OR",
}


def _module_body_text(text: str, name: str) -> str:
    span = _module_header_span(text, name)
    if not span:
        start = re.search(rf"(?m)^\s*module\s+{re.escape(name)}\b", text)
        if not start:
            return ""
        body_start = text.find(";", start.end())
        if body_start < 0:
            return ""
        body_start += 1
    else:
        semi = text.find(";", span[1])
        if semi < 0:
            return ""
        body_start = semi + 1
    end = re.search(r"(?m)^\s*endmodule\b", text[body_start:])
    if not end:
        return ""
    body = text[body_start : body_start + end.start()]
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    body = re.sub(r"//.*?$", "", body, flags=re.M)
    return body


def _rtl_operator_blocks(text: str, name: str) -> list[dict]:
    """Parse simple RTL operators for a Xilinx-style expanded interior (no Yosys)."""
    body = _module_body_text(text, name)
    if not body.strip():
        return []

    ops: list[dict] = []
    seen: set[tuple[str, str, str, str]] = set()

    def add_op(lhs: str, expr: str) -> None:
        expr = " ".join(expr.split())
        lhs = lhs.strip()
        match = _BIN_EXPR.match(expr)
        if not match:
            return
        left, op, right = match.group(1).strip(), match.group(2), match.group(3).strip()
        kind = _OP_KIND.get(op)
        if not kind:
            return
        key = (kind, left, right, lhs)
        if key in seen:
            return
        seen.add(key)
        ops.append(
            {
                "kind": kind,
                "op": op,
                "left": left,
                "right": right,
                "out": lhs,
                "expr": f"{lhs} = {left} {op} {right}",
            }
        )

    for match in _ASSIGN_STMT.finditer(body):
        stmt = match.group(1)
        if "=" not in stmt:
            continue
        lhs, expr = stmt.split("=", 1)
        add_op(lhs, expr)

    # always_comb / always bodies: capture plain blocking assigns not already seen.
    for match in _EQ_STMT.finditer(body):
        add_op(match.group(1), match.group(2))

    return ops


def _port_bus_label(port: dict) -> str:
    if port.get("width"):
        return f'{port["name"]}[{port["width"]}]'
    return port["name"]


def _wrap_schematic_html(title: str, svg: str, extra_script: str = "") -> str:
    """Full HTML page so Cursor Simple Browser / Live Preview can open it."""
    safe_title = _escape_xml(title)
    script = extra_script or ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{safe_title} · Schematic</title>
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      background: #d8d8d8;
      font-family: Arial, Helvetica, sans-serif;
    }}
    .page {{
      min-height: 100vh;
      box-sizing: border-box;
      padding: 8px 8px 24px;
    }}
    svg {{
      display: block;
      max-width: 100%;
      height: auto;
      background: #d8d8d8;
    }}
  </style>
</head>
<body>
  <div class="page">
{svg}
  </div>
{script}
</body>
</html>
"""


def _box_level_html(module: str, ports: list[dict], ops: list[dict] | None = None) -> str:
    svg = _box_level_svg(module, ports, ops)
    # Move interactivity into the HTML page (more reliable than SVG-embedded script).
    script = """<script>
function toggleComponent(id) {
  var comp = document.getElementById(id);
  if (!comp) return;
  if (comp.classList.contains('collapsed')) {
    comp.classList.remove('collapsed');
    comp.classList.add('expanded');
  } else {
    comp.classList.remove('expanded');
    comp.classList.add('collapsed');
  }
}
</script>"""
    # Strip any script already inside the SVG.
    svg = re.sub(r"<script\b[^>]*>[\s\S]*?</script>", "", svg, flags=re.I)
    return _wrap_schematic_html(module, svg, script)


def _box_level_svg(module: str, ports: list[dict], ops: list[dict] | None = None) -> str:
    """Elaborated RTL schematic in the Vivado Schematic window style.

    Collapsed: hierarchical symbol with pin stubs inside + outside the cell.
    Expanded (+): Expand Inside — leaf operator cells and orthogonal bus nets.
    """
    ops = ops or []
    inputs = [p for p in ports if p["direction"] in {"input", "inout"}]
    outputs = [p for p in ports if p["direction"] == "output"]
    n_in, n_out = len(inputs), len(outputs)
    rows = max(n_in, n_out, 1)

    # Collapsed hierarchical symbol size (tight, like Vivado).
    coll_w = 220
    coll_h = max(120, 36 + rows * 28)

    # Expanded hierarchy sheet: room for leaf cell + routing channels.
    leaf_w, leaf_h = 150, 96
    exp_w = 520
    exp_h = max(260, 80 + max(len(ops), 1) * (leaf_h + 50))

    # Canvas sized for expanded view; collapsed symbol is centered in same sheet.
    margin_l, margin_r, margin_t, margin_b = 120, 120, 48, 36
    width = margin_l + exp_w + margin_r
    height = margin_t + exp_h + margin_b

    # Collapsed symbol placement (centered).
    cx = margin_l + (exp_w - coll_w) / 2
    cy = margin_t + (exp_h - coll_h) / 2

    # Expanded hierarchy boundary (full sheet).
    hx, hy = margin_l, margin_t
    hw, hh = exp_w, exp_h

    def side_pin_ys(count: int, top: float, box_h: float) -> list[float]:
        if count <= 0:
            return []
        if count == 1:
            return [top + box_h / 2]
        span = box_h - 48
        return [top + 28 + i * (span / (count - 1)) for i in range(count)]

    coll_in_ys = side_pin_ys(n_in, cy, coll_h)
    coll_out_ys = side_pin_ys(n_out, cy, coll_h)
    exp_in_ys = side_pin_ys(n_in, hy, hh)
    exp_out_ys = side_pin_ys(n_out, hy, hh)

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        """<defs>
  <pattern id="vivGrid" width="20" height="20" patternUnits="userSpaceOnUse">
    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#b0b0b0" stroke-width="0.6"/>
  </pattern>
  <style>
    .collapsed .expanded-only { display: none; }
    .expanded .collapsed-only { display: none; }
    .hier-plus { cursor: pointer; }
    .cell-hit { cursor: pointer; }
    .bus { fill: none; stroke: #0000aa; stroke-width: 3.2; stroke-linecap: square; stroke-linejoin: miter; }
    .wire { fill: none; stroke: #000000; stroke-width: 1.4; stroke-linecap: square; }
    .pin-stub { stroke: #000000; stroke-width: 1.4; }
    .cell-body { fill: #ffffff; stroke: #000000; stroke-width: 1.4; }
    .hier-body { fill: #ffffff; stroke: #000000; stroke-width: 1.6; }
    .hier-dash { fill: #f7f7f7; stroke: #000000; stroke-width: 1.4; stroke-dasharray: 6 3; }
    .lbl { font-family: Arial, Helvetica, sans-serif; font-size: 12px; fill: #000000; }
    .lbl-sm { font-family: Arial, Helvetica, sans-serif; font-size: 11px; fill: #000000; }
    .lbl-inst { font-family: Arial, Helvetica, sans-serif; font-size: 13px; fill: #000000; font-weight: 700; }
    .banner { font-family: Arial, Helvetica, sans-serif; font-size: 12px; fill: #333333; }
  </style>
</defs>""",
        # Vivado schematic canvas
        '<rect width="100%" height="100%" fill="#d8d8d8"/>',
        '<rect width="100%" height="100%" fill="url(#vivGrid)"/>',
        f'<text x="12" y="20" class="banner">Elaborated Design · Schematic · '
        f"{_escape_xml(module)}</text>",
        f'<text x="12" y="36" class="lbl-sm" fill="#444444">Click + to Expand Inside</text>',
        '<g id="comp_top" class="collapsible-comp collapsed">',
    ]

    # ----- Collapsed hierarchical symbol -----
    parts.append('<g class="collapsed-only">')
    parts.append(
        f'<rect class="hier-body" x="{cx}" y="{cy}" width="{coll_w}" height="{coll_h}"/>'
    )
    # Vivado puts instance name near top-center
    parts.append(
        f'<text x="{cx + coll_w / 2}" y="{cy + 18}" text-anchor="middle" class="lbl-inst">'
        f"{_escape_xml(module)}</text>"
    )
    # + control (upper-left, square — Vivado schematic)
    parts.append(
        f'<g class="hier-plus" onclick="toggleComponent(\'comp_top\')" '
        f'transform="translate({cx + 4}, {cy + 4})">'
        f'<rect width="16" height="16" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>'
        f'<text id="plus_glyph" x="8" y="12.5" text-anchor="middle" '
        f'font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" '
        f'fill="#000000">+</text></g>'
    )
    # Clicking body also expands
    parts.append(
        f'<rect class="cell-hit" x="{cx + 24}" y="{cy}" width="{coll_w - 28}" height="22" '
        f'fill="transparent" onclick="toggleComponent(\'comp_top\')"/>'
    )

    stub = 14  # pin stub length inside / outside

    for i, port in enumerate(inputs):
        y = coll_in_ys[i]
        label = _escape_xml(_port_bus_label(port))
        # outside stub + inside stub (Vivado pin both sides of boundary)
        parts.append(
            f'<line class="pin-stub" x1="{cx - stub}" y1="{y}" x2="{cx + stub}" y2="{y}"/>'
        )
        parts.append(
            f'<text x="{cx + stub + 4}" y="{y + 4}" class="lbl-sm">{label}</text>'
        )
        # external port label (left of outside stub)
        parts.append(
            f'<text x="{cx - stub - 4}" y="{y + 4}" text-anchor="end" class="lbl-sm">{label}</text>'
        )
        # thick bus tail to the left
        parts.append(
            f'<line class="bus" x1="{cx - stub - 40}" y1="{y}" x2="{cx - stub}" y2="{y}"/>'
        )

    for i, port in enumerate(outputs):
        y = coll_out_ys[i]
        label = _escape_xml(_port_bus_label(port))
        parts.append(
            f'<line class="pin-stub" x1="{cx + coll_w - stub}" y1="{y}" '
            f'x2="{cx + coll_w + stub}" y2="{y}"/>'
        )
        parts.append(
            f'<text x="{cx + coll_w - stub - 4}" y="{y + 4}" text-anchor="end" class="lbl-sm">{label}</text>'
        )
        parts.append(
            f'<text x="{cx + coll_w + stub + 4}" y="{y + 4}" class="lbl-sm">{label}</text>'
        )
        parts.append(
            f'<line class="bus" x1="{cx + coll_w + stub}" y1="{y}" '
            f'x2="{cx + coll_w + stub + 40}" y2="{y}"/>'
        )

    if not ports:
        parts.append(
            f'<text x="{cx + coll_w / 2}" y="{cy + coll_h / 2 + 8}" text-anchor="middle" '
            f'class="lbl-sm">(no ports)</text>'
        )
    parts.append("</g>")  # collapsed-only

    # ----- Expanded Inside -----
    parts.append('<g class="expanded-only">')
    # Hierarchy boundary (dashed) — parent module opened
    parts.append(
        f'<rect class="hier-dash" x="{hx}" y="{hy}" width="{hw}" height="{hh}"/>'
    )
    parts.append(
        f'<text x="{hx + 28}" y="{hy + 16}" class="lbl-inst">{_escape_xml(module)}</text>'
    )
    parts.append(
        f'<g class="hier-plus" onclick="toggleComponent(\'comp_top\')" '
        f'transform="translate({hx + 4}, {hy + 4})">'
        f'<rect width="16" height="16" fill="#ffffff" stroke="#000000" stroke-width="1.2"/>'
        f'<text x="8" y="12.5" text-anchor="middle" '
        f'font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" '
        f'fill="#000000">-</text></g>'
    )

    # Parent pin stubs on hierarchy boundary
    for i, port in enumerate(inputs):
        y = exp_in_ys[i]
        label = _escape_xml(_port_bus_label(port))
        parts.append(
            f'<line class="pin-stub" x1="{hx - stub}" y1="{y}" x2="{hx + stub}" y2="{y}"/>'
        )
        parts.append(
            f'<text x="{hx - stub - 4}" y="{y + 4}" text-anchor="end" class="lbl-sm">{label}</text>'
        )
        parts.append(
            f'<line class="bus" x1="{hx - stub - 40}" y1="{y}" x2="{hx - stub}" y2="{y}"/>'
        )

    for i, port in enumerate(outputs):
        y = exp_out_ys[i]
        label = _escape_xml(_port_bus_label(port))
        parts.append(
            f'<line class="pin-stub" x1="{hx + hw - stub}" y1="{y}" '
            f'x2="{hx + hw + stub}" y2="{y}"/>'
        )
        parts.append(
            f'<text x="{hx + hw + stub + 4}" y="{y + 4}" class="lbl-sm">{label}</text>'
        )
        parts.append(
            f'<line class="bus" x1="{hx + hw + stub}" y1="{y}" '
            f'x2="{hx + hw + stub + 40}" y2="{y}"/>'
        )

    if not ops:
        parts.extend(
            [
                f'<rect class="cell-body" x="{hx + hw / 2 - 90}" y="{hy + hh / 2 - 30}" '
                f'width="180" height="60"/>',
                f'<text x="{hx + hw / 2}" y="{hy + hh / 2 - 4}" text-anchor="middle" class="lbl-sm">'
                f"No elaborated logic</text>",
                f'<text x="{hx + hw / 2}" y="{hy + hh / 2 + 16}" text-anchor="middle" class="lbl-sm" '
                f'font-family="Courier New,Courier,monospace">assign sum = a + b;</text>',
            ]
        )
    else:
        # Place leaf operator cells in the center channel
        for i, op in enumerate(ops):
            lx = hx + (hw - leaf_w) / 2
            ly = hy + 50 + i * (leaf_h + 40)
            # Leaf cell body
            inst = f'{op["kind"].lower()}_{i}'
            parts.append(
                f'<rect class="cell-body" x="{lx}" y="{ly}" width="{leaf_w}" height="{leaf_h}"/>'
            )
            parts.append(
                f'<text x="{lx + leaf_w / 2}" y="{ly + 16}" text-anchor="middle" class="lbl-inst">'
                f"{_escape_xml(inst)}</text>"
            )
            parts.append(
                f'<text x="{lx + leaf_w / 2}" y="{ly + 32}" text-anchor="middle" class="lbl-sm">'
                f'{_escape_xml(op["kind"])} {_escape_xml(op["op"])}</text>'
            )

            # Leaf pins A / B / Y (Vivado $add style)
            a_y = ly + 48
            b_y = ly + 70
            y_y = ly + leaf_h / 2 + 8
            for pin_name, py, side in (("A", a_y, "in"), ("B", b_y, "in"), ("Y", y_y, "out")):
                if side == "in":
                    parts.append(
                        f'<line class="pin-stub" x1="{lx - stub}" y1="{py}" x2="{lx + stub}" y2="{py}"/>'
                    )
                    parts.append(
                        f'<text x="{lx + stub + 3}" y="{py + 4}" class="lbl-sm">{pin_name}</text>'
                    )
                else:
                    parts.append(
                        f'<line class="pin-stub" x1="{lx + leaf_w - stub}" y1="{py}" '
                        f'x2="{lx + leaf_w + stub}" y2="{py}"/>'
                    )
                    parts.append(
                        f'<text x="{lx + leaf_w - stub - 3}" y="{py + 4}" text-anchor="end" '
                        f'class="lbl-sm">{pin_name}</text>'
                    )

            # Orthogonal bus routes: parent pin → leaf pin
            def route_h_then(x0, y0, x1, y1):
                mid = (x0 + x1) / 2
                return (
                    f'<polyline class="bus" points="{x0},{y0} {mid},{y0} {mid},{y1} {x1},{y1}"/>'
                )

            # Match operand names to parent ports when possible
            left_name = op["left"].split("[", 1)[0]
            right_name = op["right"].split("[", 1)[0]
            out_name = op["out"].split("[", 1)[0]

            def find_y(name: str, ys: list[float], plist: list[dict]) -> float | None:
                for idx, p in enumerate(plist):
                    if p["name"] == name:
                        return ys[idx]
                return None

            py_a = find_y(left_name, exp_in_ys, inputs)
            py_b = find_y(right_name, exp_in_ys, inputs)
            py_y = find_y(out_name, exp_out_ys, outputs)

            if py_a is not None:
                parts.append(route_h_then(hx + stub, py_a, lx - stub, a_y))
                parts.append(
                    f'<text x="{(hx + lx) / 2}" y="{min(py_a, a_y) - 6}" text-anchor="middle" '
                    f'class="lbl-sm">{_escape_xml(op["left"])}</text>'
                )
            if py_b is not None:
                parts.append(route_h_then(hx + stub, py_b, lx - stub, b_y))
                parts.append(
                    f'<text x="{(hx + lx) / 2}" y="{max(py_b, b_y) + 14}" text-anchor="middle" '
                    f'class="lbl-sm">{_escape_xml(op["right"])}</text>'
                )
            if py_y is not None:
                parts.append(route_h_then(lx + leaf_w + stub, y_y, hx + hw - stub, py_y))
                parts.append(
                    f'<text x="{(lx + leaf_w + hx + hw) / 2}" y="{min(y_y, py_y) - 6}" '
                    f'text-anchor="middle" class="lbl-sm">{_escape_xml(op["out"])}</text>'
                )

    parts.append("</g>")  # expanded-only
    parts.append("</g>")  # collapsible

    parts.append(
        """<script><![CDATA[
function toggleComponent(id) {
  var comp = document.getElementById(id);
  if (!comp) return;
  if (comp.classList.contains('collapsed')) {
    comp.classList.remove('collapsed');
    comp.classList.add('expanded');
  } else {
    comp.classList.remove('expanded');
    comp.classList.add('collapsed');
  }
}
]]></script>"""
    )
    parts.append("</svg>")
    return "\n".join(parts)


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

    def paint_fa(match: re.Match) -> str:
        inst = match.group("inst")
        bit = re.search(r"bit\[(\d+)\]", inst)
        title = f"FA{bit.group(1)}" if bit else "FA"
        groups.append(("FA", None))
        left = _order_fa_ports(match.group("ins"), ("a", "b", "cin"))
        right = _order_fa_ports(match.group("outs"), ("sum", "cout"))
        return _paint(match.group(1), "{{" + left + "}|" + title + "|{" + right + "}}", "FA")

    styled = _FA_NODE.sub(paint_fa, dot)
    styled = _CELL_NODE.sub(paint_gate, styled)
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


def _order_fa_ports(fragment: str, order: tuple[str, ...]) -> str:
    renamed = {"a": "A", "b": "B", "cin": "Cin", "sum": "Sum", "cout": "Cout"}
    by_name = {}
    for port in _FA_PORT.findall(fragment):
        port_id, name = port.split()
        by_name[name.lower()] = port_id
    pieces = []
    for key in order:
        port_id = by_name.get(key)
        if port_id:
            pieces.append(f"{port_id} {renamed[key]}")
    return "|".join(pieces)


_NODE_GROUP = re.compile(r'<g id="(node\d+)" class="node">(.*?)</g>', re.S)
_FA_LABEL = re.compile(r">FA(\d+)</text>")
_VIEWBOX = re.compile(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"')

_FA_POPUP_W = 468
_FA_POPUP_H = 252


def _attach_fa_expanders(svg: str) -> str:
    """Add a + control on each full adder that opens its gate wiring."""
    if not _FA_LABEL.search(svg):
        return svg

    view = _VIEWBOX.search(svg)
    view_w = float(view.group(1)) if view else 2000.0
    view_h = float(view.group(2)) if view else 1600.0
    popups: list[str] = []

    def replacer(match: re.Match) -> str:
        body = match.group(2)
        label = _FA_LABEL.search(body)
        if label is None:
            return match.group(0)
        points = re.search(r'points="([^"]+)"', body)
        if points is None:
            return match.group(0)
        bit = label.group(1)
        min_x, min_y, max_x, max_y = _point_bbox(points.group(1))
        cx = (min_x + max_x) / 2
        button = _fa_button(bit, cx, min_y)
        ox, oy = _fa_popup_origin(min_x, min_y, max_x, max_y, view_w, view_h)
        popups.append(_fa_popup(bit, ox, oy))
        return f'<g id="{match.group(1)}" class="node">{body}{button}</g>'

    svg = _NODE_GROUP.sub(replacer, svg)
    if not popups:
        return svg

    open_tag = re.search(r"<svg[^>]*>", svg)
    if open_tag is None:
        return svg
    defs = (
        "<defs><filter id=\"fa-shadow\" x=\"-15%\" y=\"-15%\" width=\"140%\" height=\"150%\">"
        "<feDropShadow dx=\"0\" dy=\"2\" stdDeviation=\"2.5\" flood-color=\"#0f172a\" flood-opacity=\"0.16\"/>"
        "</filter></defs>"
    )
    script = """<script type="text/ecmascript"><![CDATA[
function toggleFA(bit) {
  var popup = document.getElementById("fa-open-" + bit);
  if (!popup) return;
  var opening = popup.style.display !== "inline";
  var popups = document.getElementsByClassName("fa-popup");
  for (var i = 0; i < popups.length; i++) popups[i].style.display = "none";
  var toggles = document.getElementsByClassName("fa-toggle");
  for (var j = 0; j < toggles.length; j++) {
    var plus = toggles[j].querySelector(".fa-plus");
    var minus = toggles[j].querySelector(".fa-minus");
    if (plus) plus.style.display = "inline";
    if (minus) minus.style.display = "none";
  }
  if (!opening) return;
  popup.style.display = "inline";
  var button = document.getElementById("fa-toggle-" + bit);
  if (!button) return;
  var showPlus = button.querySelector(".fa-plus");
  var showMinus = button.querySelector(".fa-minus");
  if (showPlus) showPlus.style.display = "none";
  if (showMinus) showMinus.style.display = "inline";
}
]]></script>"""
    svg = svg[: open_tag.end()] + defs + svg[open_tag.end() :]
    close = svg.rfind("</g>")
    svg = svg[:close] + "".join(popups) + svg[close:]
    return svg.replace("</svg>", script + "</svg>", 1)


def _point_bbox(points: str) -> tuple[float, float, float, float]:
    nums = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", points)]
    xs, ys = nums[0::2], nums[1::2]
    return min(xs), min(ys), max(xs), max(ys)


def _fa_popup_origin(
    min_x: float,
    min_y: float,
    max_x: float,
    max_y: float,
    view_w: float,
    view_h: float,
) -> tuple[float, float]:
    ox = max_x + 18
    if ox + _FA_POPUP_W > view_w - 16:
        ox = min_x - 18 - _FA_POPUP_W
    ox = min(max(ox, 8.0), view_w - _FA_POPUP_W - 8)
    oy = min_y
    top_limit = -(view_h - 16)
    bottom_limit = -8 - _FA_POPUP_H
    if oy + _FA_POPUP_H > -8:
        oy = bottom_limit
    if oy < top_limit:
        oy = top_limit
    return ox, oy


def _fa_button(bit: str, cx: float, top: float) -> str:
    return (
        f'<g id="fa-toggle-{bit}" class="fa-toggle" style="cursor:pointer" onclick="toggleFA(\'{bit}\')">'
        f"<title>Show the gates inside FA{bit}</title>"
        f'<circle cx="{cx:.2f}" cy="{top:.2f}" r="9" fill="#ffffff" stroke="#be123c" stroke-width="1.6"/>'
        f'<text class="fa-plus" x="{cx:.2f}" y="{top:.2f}" text-anchor="middle" dominant-baseline="central" '
        f'font-family="Helvetica,sans-serif" font-size="16" font-weight="700" fill="#be123c">+</text>'
        f'<text class="fa-minus" x="{cx:.2f}" y="{top:.2f}" text-anchor="middle" dominant-baseline="central" '
        f'font-family="Helvetica,sans-serif" font-size="16" font-weight="700" fill="#be123c" '
        f'style="display:none">−</text></g>'
    )


def _fa_popup(bit: str, ox: float, oy: float) -> str:
    if bit == "0":
        cin_note = "Cin is 0"
    else:
        cin_note = f"Cin from FA{int(bit) - 1}"
    return (
        f'<g id="fa-open-{bit}" class="fa-popup" display="none" transform="translate({ox:.2f},{oy:.2f})">'
        f'<rect width="{_FA_POPUP_W}" height="{_FA_POPUP_H}" rx="10" fill="#ffffff" stroke="#be123c" '
        f'stroke-width="1.5" filter="url(#fa-shadow)"/>'
        f'<rect width="{_FA_POPUP_W}" height="36" rx="10" fill="#ffe4e6"/>'
        f'<rect y="18" width="{_FA_POPUP_W}" height="18" fill="#ffe4e6"/>'
        f'<text x="16" y="24" font-family="Helvetica,sans-serif" font-size="14" font-weight="700" fill="#9f1239">'
        f"FA{bit}</text>"
        f'<text x="58" y="24" font-family="Helvetica,sans-serif" font-size="13" fill="#881337">1-bit full adder</text>'
        f'<text x="{_FA_POPUP_W - 16}" y="24" text-anchor="end" font-family="Helvetica,sans-serif" '
        f'font-size="12" fill="#9f1239">{cin_note}</text>'
        f'<text x="16" y="56" font-family="Helvetica,sans-serif" font-size="12" fill="#334155">'
        f"Sum = A XOR B XOR Cin</text>"
        f'<text x="16" y="74" font-family="Helvetica,sans-serif" font-size="12" fill="#334155">'
        f"Cout = (A AND B) OR (Cin AND (A XOR B))</text>"
        f"{_fa_gate_diagram()}"
        f"</g>"
    )


def _fa_gate_diagram() -> str:
    """XOR/AND/OR network for one full adder, in popup-local coordinates."""
    parts: list[str] = []

    def wire(points: list[tuple[float, float]]) -> None:
        start = f"M{points[0][0]:.1f},{points[0][1]:.1f}"
        rest = "".join(f"L{x:.1f},{y:.1f}" for x, y in points[1:])
        parts.append(
            f'<path d="{start}{rest}" fill="none" stroke="#64748b" stroke-width="1.5" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
        )

    def dot(x: float, y: float) -> None:
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.4" fill="#334155"/>')

    def gate(x: float, y: float, w: float, h: float, label: str, fill: str, stroke: str) -> None:
        parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
            f'<text x="{x + w / 2:.1f}" y="{y + h / 2 + 4:.1f}" text-anchor="middle" '
            f'font-family="Helvetica,sans-serif" font-size="12" fill="#0f172a">{label}</text>'
        )

    def label(x: float, y: float, text: str, anchor: str = "start", fill: str = "#9f1239") -> None:
        parts.append(
            f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Helvetica,sans-serif" '
            f'font-size="12" font-weight="700" fill="{fill}">{text}</text>'
        )

    # Sum path on top, carry path below. A crossing without a dot is not a join.
    wire([(40, 105), (100, 105)])
    wire([(48, 105), (48, 159), (100, 159)])
    dot(48, 105)
    wire([(40, 175), (100, 175)])
    wire([(64, 175), (64, 121), (100, 121)])
    dot(64, 175)
    wire([(172, 113), (230, 105)])
    wire([(200, 113), (200, 213), (230, 213)])
    dot(200, 113)
    wire([(40, 229), (230, 229)])
    wire([(186, 229), (186, 121), (230, 121)])
    dot(186, 229)
    wire([(172, 167), (340, 165)])
    wire([(302, 221), (324, 221), (324, 181), (340, 181)])
    wire([(302, 113), (430, 113)])
    wire([(404, 173), (430, 173)])

    gate(100, 96, 72, 34, "XOR", "#f3e8ff", "#7e22ce")
    gate(100, 150, 72, 34, "AND", "#dcfce7", "#15803d")
    gate(230, 96, 72, 34, "XOR", "#f3e8ff", "#7e22ce")
    gate(230, 204, 72, 34, "AND", "#dcfce7", "#15803d")
    gate(340, 156, 64, 34, "OR", "#dbeafe", "#1d4ed8")

    label(12, 109, "A")
    label(12, 179, "B")
    label(12, 233, "Cin")
    label(436, 117, "Sum")
    label(436, 177, "Cout")
    return "".join(parts)


def _notes(cells: list[dict]) -> list[str]:
    notes = []
    fa_count = sum(row["count"] for row in cells if row["name"] == "FA")
    if fa_count:
        notes.append(
            f"Addition is a ripple of {fa_count} full adders. "
            "FA0 is the least significant bit and its carry-in is 0. "
            "Click + on a full adder to open its XOR, AND, and OR wiring."
        )
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
