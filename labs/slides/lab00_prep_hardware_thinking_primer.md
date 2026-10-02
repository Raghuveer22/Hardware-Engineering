# 🚀 Lab 00-Prep: Hardware Thinking Primer for Software & AI Engineers
### Bridging the Gap from Python & PyTorch to Synthesizable Silicon Gates

* **Track:** Silicon Fundamentals & Hardware/Software Co-Design
* **Prerequisites:** Basic Python, knowledge of loops, and elementary binary numbers
* **Next Lab:** [Lab 00: Parameterized Signed Adder & Saturation](lab00_adder_slides.md)

---

## 1. The Fundamental Mental Shift: Software vs. Hardware

If you come from Python, C++, or PyTorch, your brain is trained on **Sequential Execution**:
```python
# Software: Line 1 runs, THEN Line 2 runs, THEN Line 3 runs
a = b + c
d = a * 2
e = d + 10
```
In software, a single CPU core has a **Program Counter (PC)** that steps through memory instructions one by one.

### In Silicon Hardware, Everything Happens Everywhere, All at Once!
When you write Hardware Description Language (HDL like **SystemVerilog**), you are **NOT writing a program that runs on a processor**. You are drawing a **physical blueprint of copper wires, logic gates, and transistor switches** etched into silicon:

```
 SOFTWARE WORLD (CPU / GPU Thread)          HARDWARE WORLD (Silicon ASIC / FPGA)
 ─────────────────────────────────          ────────────────────────────────────
 • Instructions execute sequentially       • All logic gates evaluate concurrently
 • Variables live in RAM or Cache          • Values flow continuously through physical copper wires
 • Loops take N clock iterations           • Loops unroll into N physical parallel silicon units
 • Functions are jumped to and returned    • Modules are permanent physical circuits on the die
```

```
                        ┌───────────────────────────────────┐
                        │      CONCURRENT SILICON GATES     │
                        └───────────────────────────────────┘
                                          │
            ┌─────────────────────────────┼─────────────────────────────┐
            ▼                             ▼                             ▼
    ┌───────────────┐             ┌───────────────┐             ┌───────────────┐
    │  Adder Block  │             │ Multiplier PE │             │  Softmax SFU  │
    │ (Always Live) │             │ (Always Live) │             │ (Always Live) │
    └───────────────┘             └───────────────┘             └───────────────┘
            ▲                             ▲                             ▲
            └─────────────────────────────┴─────────────────────────────┘
                              Continuous Power & Voltage
```

> [!IMPORTANT]
> In hardware, an Adder does not "wait to be called". The moment electricity is applied, the inputs at its pins travel through silicon gates at the speed of light, and the output pins change voltage within fractions of a nanosecond.

---

## 2. Hardware Building Blocks: Wires vs. Registers (Flip-Flops)

All digital computing in modern AI chips (TPUs, GPUs, Cerebras) boils down to two fundamental constructs:

```
┌──────────────────────────────────────┬──────────────────────────────────────┐
│ 1. Combinational Logic (Wires/Gates) │ 2. Sequential Logic (Registers/D-FF) │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ • Pure math/boolean calculation      │ • Memory / State storage             │
│ • No memory, no clock required       │ • Updates ONLY on a Clock Edge (↑)   │
│ • Output changes as inputs change    │ • Holds value stable between clocks  │
│ • Keyword: `always_comb` or `assign` │ • Keyword: `always_ff @(posedge clk)`│
└──────────────────────────────────────┴──────────────────────────────────────┘
```

### A. Combinational Logic (Wires & Gates)
Think of combinational logic as a pipeline of pipes and valves. If you pour water in, water comes out the other end immediately (after a small physical propagation delay $t_{pd}$).

```systemverilog
// Pure combinational logic: Wires connected to an ADD gate
assign sum = a + b;

// Or equivalently in an always_comb block:
always_comb begin
    if (enable)
        out = in1 + in2;
    else
        out = 0;
end
```

### B. Sequential Logic (The D-Flip-Flop: The Master of Time)
A **D Flip-Flop (D-FF)** is a 1-bit memory cell. It acts like a camera shutter:
1. It ignores whatever is happening at its input `D` while the clock is low or high.
2. The exact instant the clock transitions from `0` to `1` (**Positive Clock Edge $\uparrow$**), it snaps a photo of input `D` and copies it to output `Q`.
3. It locks that value on `Q` until the *next* clock edge arrives.

```
                  ┌──────────────────────┐
    D (Input) ───►│ D                  Q ├───► Q (Output: Stable for 1 cycle)
                  │      D-Flip-Flop     │
  clk (Clock) ───►│ > (posedge)          │
                  │                      │
  rst_n ─────────►│ rst_n (Active Low)   │
                  └──────────────────────┘
```

In SystemVerilog:
```systemverilog
always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        q <= 8'd0;       // Reset state to 0
    end else begin
        q <= d;          // Sample input 'd' on every clock tick
    end
end
```

---

## 3. The Golden Rule of SystemVerilog: `=` vs. `<=`

This is the #1 mistake software engineers make when learning hardware.

| Assignment Operator | Name | Where to Use It | Hardware Meaning |
| :--- | :--- | :--- | :--- |
| **`=`** | **Blocking Assignment** | **ONLY** in `always_comb` | Updates variable immediately, blocking subsequent lines (like software). |
| **`<=`** | **Non-Blocking Assignment** | **ONLY** in `always_ff @(posedge clk)` | All registers evaluate their right-hand sides simultaneously and update in parallel on the clock tick! |

### The Classic Shift Register Example
Consider this hardware shift register transferring data $A \to B \to C$:

```
        Clock Tick ───► [ Register A ] ───► [ Register B ] ───► [ Register C ]
```

```systemverilog
// ✅ CORRECT HARDWARE (Non-Blocking <=):
always_ff @(posedge clk) begin
    b <= a;  // B gets old value of A
    c <= b;  // C gets old value of B simultaneously!
end

// ❌ BROKEN HARDWARE (Blocking =):
always_ff @(posedge clk) begin
    b = a;   // B gets A immediately
    c = b;   // C gets NEW value of B! (Both became A in 1 cycle, ruining the pipeline!)
end
```

> [!TIP]
> **Memory Rule:**
> - `always_comb` $\longrightarrow$ Use **`=`**
> - `always_ff` $\longrightarrow$ Use **`<=`**
> - **Never** mix them in the same block!

---

## 4. Number Representation in AI Hardware: Two's Complement & Q-Format

In AI hardware, we cannot afford power-hungry 32-bit floating point arithmetic inside our massive systolic matrix multipliers. Instead, we use **Fixed-Point Quantized Integers**.

---

### A. Two's Complement Signed Integers
In an $N$-bit signed integer, the Most Significant Bit (MSB, Bit $N-1$) has a **negative weight** of $-2^{N-1}$.

For an 8-bit signed integer (`INT8`):
$$\text{Bit Weights: } \begin{pmatrix} -2^7 & 2^6 & 2^5 & 2^4 & 2^3 & 2^2 & 2^1 & 2^0 \end{pmatrix} = \begin{pmatrix} \mathbf{-128} & 64 & 32 & 16 & 8 & 4 & 2 & 1 \end{pmatrix}$$

#### Quick Conversion Examples:
* `8'b0000_0101` $= +5$
* `8'b0111_1111` $= 64 + 32 + 16 + 8 + 4 + 2 + 1 = \mathbf{+127}$ (Maximum Positive)
* `8'b1000_0000` $= \mathbf{-128}$ (Maximum Negative)
* `8'b1111_1111` $= -128 + 64 + 32 + 16 + 8 + 4 + 2 + 1 = \mathbf{-1}$

> [!CAUTION]
> **The Two's Complement Asymmetry Trap:**
> The range of an 8-bit signed integer is $[-128, +127]$.  
> Notice that **$+128$ does NOT exist!** If you compute $-(-128)$, hardware overflows back to $-128$ unless properly guarded.

---

### B. Fixed-Point Q-Format (Simulating Real Numbers with Integers)
How do we represent fractions like $0.75$ or weights like $-1.5$ in pure integer silicon? We use **Q-Format**!

A **Q4.4** number has:
* **4 integer bits** (including sign)
* **4 fractional bits** (representing halves, quarters, eighths, sixteenths)

$$\text{Bit Weights for Q4.4: } \begin{array}{cccc|cccc}
-2^3 & 2^2 & 2^1 & 2^0 & 2^{-1} & 2^{-2} & 2^{-3} & 2^{-4} \\
\mathbf{-8} & \mathbf{4} & \mathbf{2} & \mathbf{1} & \mathbf{0.5} & \mathbf{0.25} & \mathbf{0.125} & \mathbf{0.0625}
\end{array}$$

#### How to convert between Python Float and Hardware Integer:
* **Python to Hardware Integer:** $\text{Raw\_Int} = \text{round}(\text{Float\_Value} \times 2^{\text{Fractional\_Bits}})$
* **Hardware Integer to Float:** $\text{Float\_Value} = \frac{\text{Raw\_Int}}{2^{\text{Fractional\_Bits}}}$

#### Example: Representing $+1.5$ in Q4.4
1. $\text{Raw} = 1.5 \times 2^4 = 1.5 \times 16 = 24_{10}$
2. Binary: `8'b0001_1000`
3. Check: $1 \times (2^0) + 1 \times (2^{-1}) = 1 + 0.5 = 1.5$ ✅

---

## 5. Bit Growth Rules: Preventing Silicon Arithmetic Overflow

When performing operations in silicon, bit widths **grow**. If you do not allocate enough output wire width, your calculation truncates silently!

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. ADDITION / SUBTRACTION: Bit width grows by +1 Bit                        │
│    N bits + N bits = (N + 1) bits                                           │
│    Example: INT8 + INT8 (-128 + -128 = -256) requires 9 bits                │
│                                                                             │
│ 2. MULTIPLICATION: Bit width DOUBLES (Sum of input widths)                  │
│    N bits × M bits = (N + M) bits                                           │
│    Example: INT8 × INT8 (-128 × -128 = +16384) requires 8 + 8 = 16 bits     │
│                                                                             │
│ 3. ACCUMULATION (Summing K products in a MAC / Tensor Engine):              │
│    Acc_Width = Product_Width + ceil(log2(K))                                │
│    Example: Summing 16 INT8 products = 16 + log2(16) = 16 + 4 = 20 bits     │
│    (AI chips use 32-bit accumulators to guarantee zero overflow)            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Verification: How Python Tests Silicon via Cocotb

In this course, we do **NOT** test circuits using painful legacy Verilog testbenches. Instead, we use **Cocotb** (COroutine-based COsimulation TestBench), which lets you drive hardware pins directly from **modern Python testbenches**!

```
 ┌───────────────────────────┐                ┌───────────────────────────┐
 │       PYTHON TESTBENCH    │                │    SYSTEMVERILOG SILICON  │
 │      (`test_adder.py`)    │                │       (`adder.sv`)        │
 │                           │   GPI / VPI    │                           │
 │ • Generate NumPy vectors  │ ─────────────► │ • Physical logic gates    │
 │ • `dut.a.value = 10`      │                │ • Evaluates combinational │
 │ • `await RisingEdge(clk)` │ ◄───────────── │   sum & overflow          │
 │ • Assert `dut.sum == 10`  │                │                           │
 └───────────────────────────┘                └───────────────────────────┘
```

### The 4 Cocotb Commands You Need to Know:
1. **Drive an input pin:**
   ```python
   dut.a.value = 42          # Assign integer to port 'a'
   dut.rst_n.value = 1       # Deassert reset
   ```
2. **Step time / Advance Clock:**
   ```python
   from cocotb.triggers import RisingEdge, Timer
   await RisingEdge(dut.clk) # Advance simulator to the next positive clock edge
   await Timer(1, units="ns")# Advance simulation time by 1 nanosecond (for combinational logic)
   ```
3. **Read an output pin:**
   ```python
   result = dut.sum.value.signed_integer # Read port as signed two's complement
   ```
4. **Assert correctness:**
   ```python
   assert result == expected_val, f"Hardware bug! Expected {expected_val}, got {result}"
   ```

---

## 7. Cycle-by-Cycle Visual Waveform: Clock & Signal Timing

Here is what happens during a 3-cycle pipelined calculation inside hardware:

```
Cycle Index :      Cycle 0         Cycle 1         Cycle 2         Cycle 3
Time (ns)   :   0ns     10ns    20ns    30ns    40ns    50ns    60ns    70ns
                ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐
clk         : ──┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───
                ▲               ▲               ▲               ▲
                │ Clock Edge 0  │ Clock Edge 1  │ Clock Edge 2  │ Clock Edge 3

rst_n       : ──────────────────┬───────────────────────────────────────────────
                                │ (Reset released to High)

a_in        : ===<   X   >======<     10      ><     20      ><     30      >===

Reg_A (D-FF): ===<   0   >======<      0      ><     10      ><     20      >===
                                (Sampled at ↑1) (Sampled at ↑2) (Sampled at ↑3)
```

---

## 8. 🧠 The 10 Ironclad Rules of Digital Hardware Design

Before you start Lab 00, memorize these 10 golden rules:

1. **Hardware is parallel by default:** All lines outside `always` blocks execute simultaneously.
2. **Every wire has a bit width:** Always declare exact widths: `logic signed [7:0] a;`.
3. **Match bit-widths in expressions:** Adding an 8-bit signal to a 16-bit signal requires explicit sign-extension (`{{8{a[7]}}, a}`).
4. **Avoid unintended latches:** In `always_comb`, every `if` must have an `else`, and every `case` must have a `default`.
5. **Never write to the same signal from two different `always` blocks:** In silicon, that creates a physical short-circuit!
6. **Clock only in `always_ff`:** Never use `clk` as a data input inside combinational logic.
7. **Reset all registers:** Every flip-flop in `always_ff` must have a deterministic reset condition.
8. **Mind the critical path:** Long chains of combinational operations between two flip-flops slow down the maximum operating frequency ($F_{\max}$).
9. **Quantization is lossy, saturation is safe:** Wrapping around on overflow causes catastrophic accuracy loss in neural networks; always prefer saturation.
10. **Simulate before synthesizing:** A bug caught in Python Cocotb costs 0 seconds; a bug caught in synthesized silicon costs $50M and 6 months.

---

## 🎯 Next Step: Start Hands-On RTL

Now that you have the complete mental model of digital hardware, proceed to:
* **[Lab 00: Parameterized Signed Adder & Saturation Arithmetic](lab00_adder_slides.md)**
* Run your first testbench:
  ```bash
  source .venv/bin/activate
  python labs/run_lab.py --lab lab00
  ```
