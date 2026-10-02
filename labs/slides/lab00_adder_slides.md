# 🧪 Lab 00: Parameterized Signed Adder & Saturation
### Preventing Catastrophic Activation Wrap-Around in Deep Learning

* **Track:** Silicon Arithmetic & Math Engines
* **RTL:** `rtl/adder.sv`
* **Testbench:** `labs/test_adder.py`

---

### 🪝 1. The Hook: Why Naive Silicon Breaks AI Models

* **The Problem:** In standard 8-bit two's complement arithmetic, adding two large activations ($+100 + +50 = +150$) overflows into **$-106$** due to sign-bit wrap-around!
* **The Catastrophe:** A highly confident positive neuron activation suddenly flips into an extreme negative penalty, destroying model convergence during inference and training.
* **The Silicon Fix:** **Saturation Arithmetic** clamps positive overflows to $+127$ (`0x7F`) and negative overflows to $-128$ (`0x80`).

---

## 💡 2. Hardware Intuition: Full Adder, Carry & Overflow at Bit-Level

For anyone new to digital logic and Verilog, understanding arithmetic at the bit level is essential before building accelerators.

---

### A. The 1-Bit Full Adder: Anatomy & Intuition

Every single bit addition takes **3 inputs** and produces **2 outputs**:
* **Inputs:** Operand Bit $A$, Operand Bit $B$, and incoming Carry $C_{in}$.
* **Outputs:** Local Result $\text{Sum}$ ($S$) and Carry-out ($C_{out}$).

```
                     ┌────────────────────────┐
   A  ──────────────►│                        │──────────────► Sum (S) = A ⊕ B ⊕ Cin
   B  ──────────────►│   1-Bit Full Adder     │
  Cin ──────────────►│                        │──────────────► Cout = (A·B) + Cin·(A ⊕ B)
                     └────────────────────────┘
```

#### 🔍 Why XOR for Sum and Majority for Carry?
1. **$\text{Sum} = A \oplus B \oplus C_{in}$ (Parity / Odd-1s Detector):**
   * $\text{XOR}$ outputs `1` when an **odd number of inputs** are `1` ($1$ or $3$ ones).
   * When two inputs are `1`, $1+1 = 2_{10} = 10_2$. The local bit ($\text{Sum}$) is `0` and a `1` is pushed to the next column.
2. **$C_{out} = (A \cdot B) + (C_{in} \cdot (A \oplus B))$ (Majority Voter):**
   * A carry is generated whenever **2 or more inputs** are `1`. If the inputs sum to $\ge 2_{10}$, the value cannot fit in a single 1-bit register and must carry out into the next higher power of 2.


### B. Cascading Bits: The Ripple-Carry Adder Chain

In an $N$-bit adder, 1-bit full adders are chained together. Each bit slice passes its $C_{out}$ to the next bit's $C_{in}$:

```
       A[3] B[3]         A[2] B[2]         A[1] B[1]         A[0] B[0]
         │   │             │   │             │   │             │   │
       ┌─▼───▼─┐         ┌─▼───▼─┐         ┌─▼───▼─┐         ┌─▼───▼─┐
Cout ◄─┤ FA 3  │◄──C[2]──┤ FA 2  │◄──C[1]──┤ FA 1  │◄──C[0]──┤ FA 0  │◄── Cin = 0
       └───┬───┘         └───┬───┘         └───┬───┘         └───┬───┘
           ▼                 ▼                 ▼                 ▼
        Sum[3]            Sum[2]            Sum[1]            Sum[0]
```

* **Linear Gate Complexity:** $O(N)$ ($\approx 5$ logic gates per bit $\times N$ bits $\approx 40$ gates for INT8).
* **Propagation Delay:** Notice how $C[2]$ must wait for $C[1]$, which must wait for $C[0]$. The carry ripples down the entire word width.

---

### C. The Big Distinction: Carry vs. Overflow

Beginners frequently confuse **Carry** and **Overflow**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. CARRY (Unsigned Arithmetic)                                              │
│    Occurs when the result is too large to fit in N bits unsigned [0, 2^N-1].│
│    Hardware Signal: Cout from the Most Significant Bit (MSB).               │
│                                                                             │
│ 2. OVERFLOW (Signed 2's Complement)                                         │
│    Occurs when arithmetic flips into the WRONG sign bit (+127 + 1 = -128). │
│    Hardware Signal: (A[MSB] == B[MSB]) && (Sum[MSB] != A[MSB]).             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 🚨 Visualizing Signed Overflow (The Sign-Bit Flip)
In 8-bit signed two's complement, valid numbers range from **$-128$ to $+127$**.
The Most Significant Bit (MSB, bit 7) represents the sign (`0` = Positive, `1` = Negative).

1. **Positive Overflow ($+ \text{ and } + = -$):**
   ```
     +100  (8'b0110_0100)  [Sign bit = 0]
   +  +50  (8'b0011_0010)  [Sign bit = 0]
   ──────────────────────
     -106  (8'b1001_0110)  ◄── Sign bit flipped to 1! Result became negative!
   ```
2. **Negative Overflow ($- \text{ and } - = +$):**
   ```
     -100  (8'b1001_1100)  [Sign bit = 1]
   +  -50  (8'b1100_1110)  [Sign bit = 1]
   ──────────────────────
     +106  (8'b0110_1010)  ◄── Sign bit flipped to 0! Result became positive!
   ```
3. **Adding Opposite Signs ($+ \text{ and } -$):**
   * **Can NEVER overflow**, because adding opposite signs always produces a value with a smaller magnitude than the operands.

---

## 💻 3. SystemVerilog RTL Walkthrough

```verilog
module adder #(parameter int DATA_WIDTH = 8)(
    input  logic signed [DATA_WIDTH-1:0] a, b,
    input  logic                         saturate,
    output logic signed [DATA_WIDTH-1:0] sum,
    output logic                         carry_out, overflow
);
    logic signed [DATA_WIDTH:0] raw_sum;
    assign raw_sum   = {a[DATA_WIDTH-1], a} + {b[DATA_WIDTH-1], b};
    assign overflow  = (a[DATA_WIDTH-1] == b[DATA_WIDTH-1]) && 
                       (raw_sum[DATA_WIDTH-1] != a[DATA_WIDTH-1]);

    always_comb begin
        if (saturate && overflow)
            sum = a[DATA_WIDTH-1] ? MAX_NEG : MAX_POS;
        else
            sum = raw_sum[DATA_WIDTH-1:0];
    end
endmodule
```

---

## 🧪 4. Cocotb Verification

* **Golden Reference:** Python integer arithmetic compared directly against DUT pins.
* **Corner Cases Tested:**
  * Zero addition ($0 + 0 = 0$)
  * Boundary additions ($-128 + 0 = -128$, $+127 + 0 = +127$)
  * Positive saturation ($+100 + +50 \to +127$)
  * Negative saturation ($-100 + -50 \to -128$)
* **Run Testbench:**
  ```bash
  python labs/run_lab.py --lab lab00
  ```

---

## 💬 5. Comment Challenge

Drop your answers in the YouTube comments! 👇

1. Without saturation, what does $+100 + +50$ actually compute to in 8-bit two's complement?
2. Why would that wrap-around value wreck a neural network's prediction?

---

## 🗺️ What's Next on This Journey

This adder is the first building block. Here's the roadmap we'll follow in the coming labs:

| Lab | What You'll Build | Why It Matters |
| :--- | :--- | :--- |
| **Lab 01** | Signed INT8 Multiplier | Multiplication scales $O(N^2)$ — the reason AI chips obsess over quantization |
| **Lab 02** | Multiply-Accumulate (MAC) Unit | The fused `sum + a*b` workhorse of 99% of AI compute |
| **Lab 03** | Processing Element (PE) | Adds clocked registers to hold weights stationary |
| **Lab 04** | 2D Systolic Array | Google TPU-style matrix engine built from PE grids |
| **Lab 05–08** | Transformer SFUs | Square root, Softmax, rsqrt, and exponential for LLMs |

*Next up: we multiply.*
