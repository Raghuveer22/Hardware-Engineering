# Lab 00 — Write a Signed Adder in SystemVerilog
### Camera deck · concepts → code → test

* **You will write:** [`rtl/adder.sv`](../../rtl/adder.sv)
* **You will run:** `python labs/run_lab.py --lab lab00`
* **How to use:** short on-screen text · speak the **SAY** lines

---

## Hook

### Software: `100 + 50 = 150`
### INT8 wire: `100 + 50 = −106`

**SAY:**  
“Today we don’t just explain that — we **write the SystemVerilog** that adds, flags overflow, and optionally saturates.  
Beginner lab: signed ints first, then we type the module line by line.”

---

## Dual goal of this lab

| Goal | What “done” looks like |
| :--- | :--- |
| **Understand** | two’s complement, full adder, overflow |
| **Write** | a parameterized `adder` module that simulates clean |

**SAY:**  
“If you only watch diagrams, you miss the point.  
By the end you should be able to open a blank `.sv` and build this adder.”

---

## Roadmap

| # | Block |
| :---: | :--- |
| 1 | Signed integers (why the bits look like that) |
| 2 | Full-adder intuition (what silicon is doing) |
| 3 | **Write SystemVerilog** (main skill) |
| 4 | Overflow + saturation in code |
| 5 | Run Cocotb |

**SAY:**  
“Blocks 1–2 are short. Block 3 is where we live — typing RTL.”

---

# PART 1 — Signed integers (fast)

---

## Bits vs numbers

### Bits = wires (`0` / `1`)
### Number = **interpretation** of the pattern

**SAY:**  
“Python hides encoding. SystemVerilog does not.  
`logic signed [7:0]` means: eight wires, two’s complement meaning.”

---

## INT8 two’s complement

### MSB weight = **−128** · rest = +64 … +1  
### Range: **[−128 … +127]**

| Bits | Value |
| :---: | :---: |
| `0000_0101` | +5 |
| `1111_1111` | −1 |
| `1000_0000` | −128 |
| `0111_1111` | +127 |

**SAY:**  
“Decode one out loud. That’s enough signed-int for writing the adder.”

---

## The bug we’ll fix in RTL

```
  +100 + +50  →  pattern looks like −106
```

**SAY:**  
“True math is +150 — won’t fit in 8 signed bits.  
Our module must **detect** that. Optionally **clamp**. First: understand the adder.”

---

# PART 2 — Adder intuition (fast)

---

## 1-bit full adder

![1-bit full adder block](../../schematics/full_adder_block.svg)

### A, B, Cin → Sum, Cout

**SAY:**  
“Every bit slice is this box.  
We won’t instantiate FAs by hand — synthesis builds them from `+`.  
But you must know what `+` becomes.”

---

## Gates inside

![Full adder gate-level schematic](../../schematics/full_adder_gates.svg)

### Sum = XOR path · Cout = AND/OR (majority)

**SAY:**  
“Glance and move on. The RTL uses the `+` operator; the tool maps it to these gates.”

---

## Ripple = many FAs

![4-bit ripple-carry adder](../../schematics/ripple_carry_adder.svg)

**SAY:**  
“N-bit add ≈ N full adders chained.  
When we write `a + b` in SV, this is the hardware idea.”

---

# PART 3 — Write the SystemVerilog

---

## Mental shift before typing

| Software | SystemVerilog |
| :--- | :--- |
| Runs line-by-line on a CPU | Describes **gates and wires** |
| `int x` lives in memory | `logic [7:0] x` is **8 wires** |
| Function is called | Module is **always there** |

**SAY:**  
“You are not writing a program. You are drawing a circuit with text.”

---

## Skeleton — start here

```systemverilog
`timescale 1ns/1ps

module adder #(
    parameter int DATA_WIDTH = 8
)(
    // ports next...
);

endmodule
```

**SAY:**  
“Open `rtl/adder.sv` or a blank file.  
`module` / `endmodule` is the chip boundary.  
`parameter` makes width reusable — default 8.”

---

## Ports — name the pins

```systemverilog
module adder #(
    parameter int DATA_WIDTH = 8
)(
    input  logic signed [DATA_WIDTH-1:0] a,
    input  logic signed [DATA_WIDTH-1:0] b,
    input  logic                         saturate,
    output logic signed [DATA_WIDTH-1:0] sum,
    output logic                         carry_out,
    output logic                         overflow
);
```

**SAY:**  
“Read each pin:  
`logic` = wire type.  
`signed` = two’s complement math.  
`[DATA_WIDTH-1:0]` = MSB on the left.  
`saturate` is 1-bit control — we wire it later.”

---

## Keyword cheat sheet (keep on screen)

| Write this | Means |
| :--- | :--- |
| `logic` | 1-bit or bus wire / variable |
| `signed` | treat bus as two’s complement |
| `[7:0]` | 8 bits, bit 7 is MSB |
| `parameter` | constant chosen at compile / instance |
| `input` / `output` | direction through the module |

**SAY:**  
“Beginners trip on forgetting `signed`.  
Without it, `a + b` is unsigned — wrong for our lab.”

---

## Internals — declare before use

```systemverilog
    // Wider sum: one extra bit
    logic signed [DATA_WIDTH:0] raw_sum;

    // Clamp constants for INT8: +127 and -128
    localparam logic signed [DATA_WIDTH-1:0] MAX_POS =
        {1'b0, {(DATA_WIDTH-1){1'b1}}};
    localparam logic signed [DATA_WIDTH-1:0] MAX_NEG =
        {1'b1, {(DATA_WIDTH-1){1'b0}}};
```

**SAY:**  
“`raw_sum` is DATA_WIDTH+1 bits — room to see carry.  
`localparam` builds +127 / −128 from the width — don’t hardcode only for 8 if you can avoid it.  
Replication: `{(DATA_WIDTH-1){1'b1}}` means repeat `1` that many times.”

---

## `always_comb` — combinational block

```systemverilog
    always_comb begin
        // assignments with =  (blocking)
    end
```

**SAY:**  
“No clock in Lab 00. Pure combo.  
Rule from the prep lab: inside `always_comb`, use `=` not `<=`.  
Every output you drive must be assigned on all paths — or you infer a latch.”

---

## Step 1 — write the add (wide)

```systemverilog
        // Sign-extend each operand by 1 bit, then add
        raw_sum = {a[DATA_WIDTH-1], a} + {b[DATA_WIDTH-1], b};
```

**SAY:**  
“`{sign, a}` copies the MSB to make a wider signed value.  
Then `+` is the adder.  
This is the most important line in the file.”

---

## Why sign-extend? (point while coding)

| Wrong | Right |
| :--- | :--- |
| `raw_sum = a + b` in same width | lose the extra bit |
| zero-extend `{1'b0, a}` | breaks negatives |
| `{a[MSB], a}` | keeps sign, grows width by 1 |

**SAY:**  
“We need one extra bit to read carry and to reason about overflow.  
Sign-extend, don’t zero-extend.”

---

## Step 2 — carry_out

```systemverilog
        carry_out = raw_sum[DATA_WIDTH];
```

**SAY:**  
“Top bit of the wide sum is the unsigned-style carry.  
One wire. Assign it.”

---

## Step 3 — overflow flag

```systemverilog
        overflow = (a[DATA_WIDTH-1] == b[DATA_WIDTH-1]) &&
                   (raw_sum[DATA_WIDTH-1] != a[DATA_WIDTH-1]);
```

**SAY:**  
“Same signs in, different sign in the result → overflow.  
Type it carefully — two compares and an AND.”

---

## Overflow examples (while that line is on screen)

```
+100 + +50 → sign flips → overflow = 1
−100 + −50 → sign flips → overflow = 1
 +40 + −10 → opposite signs → overflow = 0
```

**SAY:**  
“Match the code to the examples.  
If the flag doesn’t match, the compare is wrong.”

---

## Step 4 — choose sum (wrap first)

```systemverilog
        // Default: wrap (take low DATA_WIDTH bits)
        sum = raw_sum[DATA_WIDTH-1:0];
```

**SAY:**  
“Before saturation, always assign wrap.  
`100+50` becomes `−106` in the low 8 bits — that’s correct wrap.”

---

## Step 5 — saturation MUX

```systemverilog
        if (saturate && overflow) begin
            if (a[DATA_WIDTH-1] == 1'b0)
                sum = MAX_POS;   // was positive overflow
            else
                sum = MAX_NEG;   // was negative overflow
        end else begin
            sum = raw_sum[DATA_WIDTH-1:0];
        end
```

**SAY:**  
“If saturate and overflow: clamp.  
Use **operand** sign `a[MSB]` to pick +max vs −max.  
Else wrap. Walk both branches out loud.”

---

## Full module (assemble — don’t rush)

```systemverilog
`timescale 1ns/1ps
module adder #(
    parameter int DATA_WIDTH = 8
)(
    input  logic signed [DATA_WIDTH-1:0] a, b,
    input  logic                         saturate,
    output logic signed [DATA_WIDTH-1:0] sum,
    output logic                         carry_out, overflow
);
    logic signed [DATA_WIDTH:0] raw_sum;
    localparam logic signed [DATA_WIDTH-1:0] MAX_POS =
        {1'b0, {(DATA_WIDTH-1){1'b1}}};
    localparam logic signed [DATA_WIDTH-1:0] MAX_NEG =
        {1'b1, {(DATA_WIDTH-1){1'b0}}};

    always_comb begin
        raw_sum   = {a[DATA_WIDTH-1], a} + {b[DATA_WIDTH-1], b};
        carry_out = raw_sum[DATA_WIDTH];
        overflow  = (a[DATA_WIDTH-1] == b[DATA_WIDTH-1]) &&
                    (raw_sum[DATA_WIDTH-1] != a[DATA_WIDTH-1]);
        if (saturate && overflow)
            sum = (a[DATA_WIDTH-1] == 1'b0) ? MAX_POS : MAX_NEG;
        else
            sum = raw_sum[DATA_WIDTH-1:0];
    end
endmodule
```

**SAY:**  
“Scroll top to bottom once: ports → locals → always_comb four jobs.  
Compare to [`rtl/adder.sv`](../../rtl/adder.sv) — should match in spirit.”

---

## Beginner mistakes (fix these)

| Mistake | Fix |
| :--- | :--- |
| Forgot `signed` | add `signed` on `a`, `b`, `sum`, `raw_sum` |
| Used `<=` in combo | use `=` in `always_comb` |
| `sum` not set in an `else` | always assign `sum` every path |
| Hardcoded `[7:0]` only | use `DATA_WIDTH` |
| Zero-extend instead of sign-extend | `{a[MSB], a}` |

**SAY:**  
“If sim fails weirdly, check `signed` first.  
If synth warns latch, you missed an else.”

---

## What synthesis thinks you drew

![adder Synthesis Schematic](../../schematics/adder.svg)

# Combinational only · O(N) gates · no DFFs

**SAY:**  
“Your text became an adder + compare + MUX.  
That’s the point of HDL.”

---

# PART 4 — Prove it with Cocotb

---

## Run

```bash
python labs/run_lab.py --lab lab00
```

**SAY:**  
“Cocotb drives `a`, `b`, `saturate` from Python and checks `sum` / `overflow`.  
You’re testing the circuit you described.”

---

## Cases your code must pass

| Inputs | saturate | Expect |
| :--- | :---: | :--- |
| `100 + 50` | 0 | sum `−106`, overflow 1 |
| `100 + 50` | 1 | sum `+127`, overflow 1 |
| `−100 + −50` | 1 | sum `−128`, overflow 1 |
| `50 + 50` | 0 or 1 | sum `100`, overflow 0 |

**SAY:**  
“Narrate one wrap and one saturate live if you can.”

---

## Recap — concept + SV skill

| Concept | SystemVerilog move |
| :--- | :--- |
| Two’s complement | `logic signed [N-1:0]` |
| Adder | `raw_sum = {sign,a} + {sign,b}` |
| Carry | `raw_sum[N]` |
| Overflow | same MSB in, flipped MSB out |
| Saturation | `if (saturate && overflow) clamp` |

**SAY:**  
“Next lab (multiplier): same port style, same `always_comb` habits — more arithmetic.”

---

## Review (ask them to write, not only talk)

1. From memory: write the module ports for `adder`.
2. Write the `raw_sum` line with sign-extend.
3. Write the `overflow` expression.
4. Explain why `always_comb` uses `=` here.
5. What does `100+50` return with `saturate=0` vs `1`?

---

## Files

| Thing | Path |
| :--- | :--- |
| RTL to write | [`rtl/adder.sv`](../../rtl/adder.sv) |
| Tests | [`labs/test_adder.py`](../test_adder.py) |
| FA gates | [`schematics/full_adder_gates.svg`](../../schematics/full_adder_gates.svg) |
| Ripple | [`schematics/ripple_carry_adder.svg`](../../schematics/ripple_carry_adder.svg) |
