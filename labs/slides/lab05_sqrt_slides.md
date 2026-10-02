# 🧪 Lab 05: Hardware Square Root Unit & Attention Scaling
### Digit-by-Digit Hardware Algorithm & Gradient Vanishing Prevention

* **Track:** Non-Linear Transformer SFUs
* **RTL:** `rtl/sqrt.sv`
* **Testbench:** `labs/test_sqrt.py`

---

## 🪝 1. The Hook: Why Attention Collapses Without $\sqrt{d_k}$

* **The Problem:** In Transformer Attention $\text{Softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right)$, Query & Key dot-products grow in variance proportional to the hidden dimension $d_k$.
* **The Disaster:** For $d_k = 128$, standard deviation $\sigma = \sqrt{128} \approx 11.3$. Logits reach $+35$, pushing Softmax into a sharp one-hot distribution ($[1.0, 0.0, 0.0...]$).
* **The Consequence:** Gradients $\frac{\partial p}{\partial z} \to 0$ **vanish completely**, halting model learning!
* **The Silicon Fix:** Dividing logits by $\sqrt{d_k}$ scales variance back to $1.0$, keeping Softmax in its active gradient zone.

---

## 💡 2. Hardware Intuition: Digit-by-Digit $\sqrt{X}$

* **How Silicon Computes $\lfloor \sqrt{X} \rfloor$ without Division:**
  * Uses digit-by-digit shift-and-subtract (analogous to binary long division).
  * Processes **2 radicand bits per stage** to determine 1 root bit.
* **Stage Equation ($i = 7 \dots 0$ for 16-bit input):**
  1. $\text{rem} = (\text{rem} \ll 2) \mid (\text{radicand}[2i+1 : 2i])$
  2. $\text{test} = (\text{root} \ll 2) \mid 1$
  3. If $\text{rem} \ge \text{test}$: $\text{rem} = \text{rem} - \text{test}, \quad \text{root} = (\text{root} \ll 1) \mid 1$
* **Complexity:** Zero DSP multipliers needed! Built entirely from cheap adders and bit-shifters.

---

## 💻 3. SystemVerilog RTL Walkthrough

```verilog
module sqrt #(
    parameter int RADICAND_WIDTH = 16,
    parameter int ROOT_WIDTH     = RADICAND_WIDTH / 2
)(
    input  logic [RADICAND_WIDTH-1:0] radicand_in,
    output logic [ROOT_WIDTH-1:0]     root_out,
    output logic [RADICAND_WIDTH-1:0] remainder_out
);
    logic [RADICAND_WIDTH-1:0] rem[ROOT_WIDTH+1];
    logic [ROOT_WIDTH-1:0]     root[ROOT_WIDTH+1];

    assign rem[0] = '0; assign root[0] = '0;
    generate
        for (genvar i = 0; i < ROOT_WIDTH; i++) begin : gen_stage
            // 8 unrolled digit-by-digit extraction stages
            // ...
        end
    endgenerate
endmodule
```

---

## 🧪 4. Cocotb Verification

* **Golden Reference:** Python `math.isqrt(x)` and remainder check `rem = x - root**2`.
* **Exhaustive Corner Testing:**
  * Zero & small inputs: $0 \to 0$, $1 \to 1$, $2 \to 1$
  * Perfect squares: $64 \to 8$, $144 \to 12$, $65025 \to 255$
  * Maximum 16-bit: $65535 \to \text{root}=255, \text{rem}=510$
* **Run Testbench:**
  ```bash
  python labs/run_lab.py --lab lab05
  ```

---

## 💬 5. Comment Challenge

Drop your answers in the YouTube comments! 👇

1. Why do we divide attention logits by $\sqrt{d_k}$ in the first place?
2. How does the digit-by-digit algorithm get a square root with **zero multipliers**?
