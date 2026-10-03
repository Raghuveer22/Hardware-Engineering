# Lab 00 — Write a Signed Adder in SystemVerilog
### Camera deck · type the file with them

* **Write along in:** [`labs/labs_playground/lab0/adder.sv`](../labs_playground/lab0/adder.sv) *(blank teaching file)*
* **Finished reference:** [`rtl/adder.sv`](../../rtl/adder.sv)
* **How to use:** keep the editor full screen · type what is on each slide · speak the **SAY** lines

---

## Hook

### Software: `100 + 50 = 150`
### Eight signed wires: `100 + 50 = −106`

**SAY:**  
“Today we open a blank `.sv` and type an adder.  
We start with three pins and one `+`. Signed, overflow, and saturation come after that works.”

---

## Goal

| Done when |
| :--- |
| You can type a module from a blank file |
| You can read one port left to right |
| You know what `a + b` becomes in silicon |

**SAY:**  
“No parameter yet. Fixed eight bits. One idea at a time.”

---

## Roadmap — type in this order

| # | Type this |
| :---: | :--- |
| 1 | `module` / `endmodule` box |
| 2 | Three pins: `a`, `b`, `sum` |
| 3 | `assign sum = a + b` |
| 4 | Add `signed` |
| 5 | Wider add + `overflow` |
| 6 | `saturate` clamp |
| 7 | *(later)* replace `8` with `DATA_WIDTH` |

**SAY:**  
“We live in the editor. Diagrams are short. Typing is the lab.”

---

# STEP 0 — Open the blank file

---

## File

Open [`labs/labs_playground/lab0/adder.sv`](../labs_playground/lab0/adder.sv).  
Delete everything except a blank page (or leave a short file header).

**SAY:**  
“This is practice RTL. Not the graded `rtl/adder.sv` yet.  
We grow this file slide by slide.”

---

# STEP 1 — Timescale + empty module

---

## Type this first

```systemverilog
`timescale 1ns/1ps

module adder (
);

endmodule
```

**SAY:**  
“`1ns` is the time unit in a testbench. `#1` means one nanosecond.  
`1ps` is the simulation precision — the finest time step.  
This line does not change the gates. The adder has no delays.  
`module` / `endmodule` is the chip boundary. Name: `adder`.”

---

## What you just drew

```
        ┌─────────┐
        │  adder  │
        └─────────┘
```

**SAY:**  
“A box with no pins yet. Next we name the wires that cross the boundary.”

---

# STEP 2 — Three pins (unsigned on purpose)

---

## Type the ports

```systemverilog
`timescale 1ns/1ps

module adder (
    input  logic [7:0] a,
    input  logic [7:0] b,
    output logic [7:0] sum
);

endmodule
```

**SAY:**  
“Read one pin left to right. Same words every time.”

---

## Read one pin (keep on screen)

| Word | Means |
| :--- | :--- |
| `input` | This pin enters the module |
| `logic` | The signal (each bit is a wire) |
| `[7:0]` | Eight bits. Bit 7 is the MSB (left) |
| `a` | Name of that signal |

**SAY:**  
“`output logic [7:0] sum` is the same sentence with the pin leaving.  
`[7:0]` is hard-coded eight. No parameter yet — keep it simple.”

---

## Box with pins

```
   a[7:0] ──►┌─────────┐──► sum[7:0]
   b[7:0] ──►│  adder  │
             └─────────┘
```

**SAY:**  
“Two operands in. One result out. The inside is still empty.”

---

# STEP 3 — Make it add

---

## Type the body

```systemverilog
`timescale 1ns/1ps

module adder (
    input  logic [7:0] a,
    input  logic [7:0] b,
    output logic [7:0] sum
);
    assign sum = a + b;
endmodule
```

**SAY:**  
“`a` and `b` are the operands. `+` is the adder. `sum` is the result.  
`assign` means: this wire is continuously that expression. No clock.”

---

## Tiny check (say out loud)

```
a = 8'b0000_0101   (+5)
b = 8'b0000_0011   (+3)
sum → 8'b0000_1000 (+8)
```

**SAY:**  
“If they can read that, the first module works.  
Next we make the same eight wires mean signed numbers.”

---

# STEP 4 — Add `signed`

---

## Change only the types

```systemverilog
module adder (
    input  logic signed [7:0] a,
    input  logic signed [7:0] b,
    output logic signed [7:0] sum
);
    assign sum = a + b;
endmodule
```

**SAY:**  
“Same eight wires. `signed` changes how `+` reads the top bit.  
MSB weight is −128. Range is −128 … +127.  
Without `signed`, this lab’s math is wrong.”

---

## The wrap you will see

```
100 + 50  →  true math +150
         →  eight signed bits look like −106
```

**SAY:**  
“The circuit did not ‘fail.’ Eight bits cannot hold 150 as signed.  
Next we detect that. Then optionally clamp.”

---

# STEP 5 — Wider add + overflow

---

## Mental picture first

### Bits = wires · Number = how you read the pattern

| Bits | Signed value |
| :---: | :---: |
| `0111_1111` | +127 |
| `1000_0000` | −128 |
| `1111_1111` | −1 |

**SAY:**  
“Glance and type. We need one extra bit so carry and overflow are visible.”

---

## Replace `assign` with this

```systemverilog
module adder (
    input  logic signed [7:0] a,
    input  logic signed [7:0] b,
    output logic signed [7:0] sum,
    output logic              overflow
);
    logic signed [8:0] raw_sum;   // 9 bits: room for carry

    always_comb begin
        // Sign-extend, then add
        raw_sum  = {a[7], a} + {b[7], b};
        overflow = (a[7] == b[7]) && (raw_sum[7] != a[7]);
        sum      = raw_sum[7:0];   // wrap: keep low 8 bits
    end
endmodule
```

**SAY:**  
“`{a[7], a}` copies the sign bit — grows the operand by one.  
Do not zero-extend.  
`overflow`: same signs in, different sign in the result.  
`always_comb` = combinational. Use `=` inside, not `<=`.”

---

## Overflow examples (while that line is up)

```
+100 + +50 → sign flips → overflow = 1
−100 + −50 → sign flips → overflow = 1
 +40 + −10 → opposite signs → overflow = 0
```

**SAY:**  
“Match the code to one example out loud.”

---

# STEP 6 — Saturation

---

## Add the control pin and clamp

```systemverilog
module adder (
    input  logic signed [7:0] a,
    input  logic signed [7:0] b,
    input  logic              saturate,
    output logic signed [7:0] sum,
    output logic              carry_out,
    output logic              overflow
);
    logic signed [8:0] raw_sum;
    localparam logic signed [7:0] MAX_POS = 8'sd127;   // +127
    localparam logic signed [7:0] MAX_NEG = -8'sd128;  // −128

    always_comb begin
        raw_sum   = {a[7], a} + {b[7], b};
        carry_out = raw_sum[8];
        overflow  = (a[7] == b[7]) && (raw_sum[7] != a[7]);

        if (saturate && overflow) begin
            if (a[7] == 1'b0)
                sum = MAX_POS;   // positive overflow → +127
            else
                sum = MAX_NEG;   // negative overflow → −128
        end else begin
            sum = raw_sum[7:0];  // wrap
        end
    end
endmodule
```

**SAY:**  
“`saturate` is one control wire.  
If saturate and overflow: clamp.  
Use **operand** sign `a[7]` to pick +127 vs −128 — not the wrapped sum’s sign.  
Else wrap. Walk both branches.”

---

## Cases to say out loud

| Inputs | saturate | Expect |
| :--- | :---: | :--- |
| `100 + 50` | 0 | sum `−106`, overflow 1 |
| `100 + 50` | 1 | sum `+127`, overflow 1 |
| `−100 + −50` | 1 | sum `−128`, overflow 1 |
| `50 + 50` | 0 or 1 | sum `100`, overflow 0 |

---

# STEP 7 — Parameter (only after the 8-bit file works)

---

## Why wait until now

**SAY:**  
“`DATA_WIDTH` is the count `8`. The pins are the eight signals that count describes.  
If we open with `parameter`, beginners mix `int` on the count with `logic` on the pins.  
Now that `[7:0]` is solid, we lift the width.”

---

## Swap hard-coded 8 → `DATA_WIDTH`

```systemverilog
`timescale 1ns/1ps

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
“`parameter int DATA_WIDTH = 8` — `int` is only the type of the number 8.  
Pins stay `logic signed [DATA_WIDTH-1:0]`.  
Compare to [`rtl/adder.sv`](../../rtl/adder.sv). Should match in spirit.”

---

# Short silicon picture (after code exists)

---

## What `+` becomes

![1-bit full adder block](../../schematics/full_adder_block.svg)

### A, B, Cin → Sum, Cout · N-bit ≈ N of these chained

**SAY:**  
“We never instantiate full adders by hand.  
`a + b` is the text; synthesis draws the chain.”

---

## Your netlist

![adder Synthesis Schematic](../../schematics/adder.svg)

# Combinational only · O(N) gates · no DFFs

---

# Prove it

---

## Run (when playground matches `rtl/adder.sv`)

```bash
python labs/run_lab.py --lab lab00
```

**SAY:**  
“Cocotb drives `a`, `b`, `saturate` and checks `sum` / `overflow`.  
Copy the finished playground into `rtl/adder.sv` when you are ready to test.”

---

## Beginner mistakes

| Mistake | Fix |
| :--- | :--- |
| Forgot `signed` | add `signed` on `a`, `b`, `sum`, `raw_sum` |
| Used `<=` in combo | use `=` in `always_comb` |
| `sum` not set in an `else` | assign `sum` on every path |
| Zero-extend instead of sign-extend | `{a[MSB], a}` |
| Opened with `parameter` first | learn `[7:0]` first, then lift |

---

## Review (they write, you watch)

1. From a blank file: `module` + three unsigned pins + `assign sum = a + b`.
2. Add `signed` on those ports.
3. Write the `raw_sum` line with sign-extend.
4. Write the `overflow` expression.
5. Say what `100+50` returns with `saturate=0` vs `1`.

---

## Files

| Thing | Path |
| :--- | :--- |
| Write-along file | [`labs/labs_playground/lab0/adder.sv`](../labs_playground/lab0/adder.sv) |
| Graded / reference RTL | [`rtl/adder.sv`](../../rtl/adder.sv) |
| Tests | [`labs/test_adder.py`](../test_adder.py) |
| FA gates | [`schematics/full_adder_gates.svg`](../../schematics/full_adder_gates.svg) |
| Ripple | [`schematics/ripple_carry_adder.svg`](../../schematics/ripple_carry_adder.svg) |
