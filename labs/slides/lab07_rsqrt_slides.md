# 🧪 Lab 07: Fast Reciprocal Square Root Unit (`rsqrt`)
### Hardware SFU for RMSNorm & LayerNorm in Modern LLMs

* **Track:** Non-Linear Transformer SFUs
* **RTL:** `rtl/rsqrt.sv`
* **Testbench:** `labs/test_rsqrt.py`

---

## 🪝 1. The Hook: Why RMSNorm is in Every LLM Layer

* **The Scale:** LLaMA 3, Mistral, Gemma, and DeepSeek execute **Root Mean Square Normalization (RMSNorm)** before every single attention and FFN block ($2 \times \text{Layers}$ per token):
  $$\text{RMSNorm}(x) = x \cdot \text{rsqrt}\left(\frac{1}{d} \sum_{i=1}^d x_i^2 + \epsilon\right)$$
* **The Silicon Pipeline Stall:** Computing full software floating-point division by square root ($x / \sqrt{v}$) stalls vector pipelines for dozens of cycles.
* **The Silicon Fix:** A dedicated **`rsqrt` Special Function Unit (SFU)** calculates $1/\sqrt{v}$ in fixed-point, converting division into a single fast multiplication!

---

## 💡 2. Hardware Intuition: Seed LUT + Fixed-Point Scaling

* **Why $1/\sqrt{x}$ Gets Silicon Priority Over $n$-th Root:**
  * $1/\sqrt{x}$ is executed billions of times per token; arbitrary $n$-th root is almost never used in neural networks.
* **Architecture:**
  * **Range $x \in [1, 15]$:** Precomputed 16-entry seed ROM for maximum precision at small variances.
  * **Range $x \ge 16$:** Digit-by-digit integer square root engine extracts root $r = \lfloor \sqrt{x} \rfloor$, scaled to Q8.8 fixed-point:
    $$y_{\text{out}} = \frac{256}{r}$$
* **Divide-by-Zero Safety:** Dedicated `valid_out` pin drops low if input $x = 0$.

---

## 💻 3. SystemVerilog RTL Walkthrough

```verilog
module rsqrt #(
    parameter int INPUT_WIDTH  = 16,
    parameter int OUTPUT_WIDTH = 16
)(
    input  logic [INPUT_WIDTH-1:0]  x_in,
    output logic [OUTPUT_WIDTH-1:0] y_out,
    output logic                    valid_out
);
    // 1. Zero input detector
    assign valid_out = (x_in != '0);

    // 2. Small x Seed LUT + Digit Root Extractor
    // ...
    // 3. Q8.8 Fixed-Point Scaler Output
endmodule
```

---

## 🧪 4. Cocotb Verification

* **Golden Reference:** NumPy floating-point `round(256.0 / math.sqrt(x))` compared against Q8.8 output.
* **Test Matrix:**
  * Zero input: $x = 0 \implies \text{valid\_out} = 0$
  * Small numbers: $x = 1 \implies 256$, $x = 4 \implies 128$
  * Perfect squares: $x = 16 \implies 64$, $x = 64 \implies 32$
  * 1,000 random variance values across full 16-bit range
* **Run Testbench:**
  ```bash
  python labs/run_lab.py --lab lab07
  ```

---

## 💬 5. Comment Challenge

Drop your answers in the YouTube comments! 👇

1. What does `rsqrt(x)` compute, and which LLM layer uses it billions of times per token?
2. What should a good hardware `rsqrt` unit do when given $x = 0$?
