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

## 💡 2. Hardware Intuition & Logic Sizing

$$\text{Sum } S = A \oplus B \oplus C_{\text{in}}, \quad C_{\text{out}} = (A \cdot B) + (C_{\text{in}} \cdot (A \oplus B))$$

$$\text{Overflow Detection: } \text{ovf} = (A[\text{MSB}] == B[\text{MSB}]) \land (\text{Sum}[\text{MSB}] \ne A[\text{MSB}])$$

* **Gate Complexity:** $O(N)$ Linear ($\approx 5$ logic gates per bit).
* **Timing & Cycles:** Purely combinational circuit ($0$ clock cycles latency). Critical path is the ripple-carry chain of $N$ full adders.
* **Waveforms needed?** No sequential clocking — combinational propagation delay only.

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
