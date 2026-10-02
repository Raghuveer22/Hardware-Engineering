# 🧪 Lab 07: Fast Reciprocal Square Root Unit (`rsqrt`)
### Dedicated Special Function Unit (SFU) for RMSNorm & LayerNorm Acceleration

* **Track:** Non-Linear Transformer SFUs
* **RTL:** [`rtl/rsqrt.sv`](../../rtl/rsqrt.sv)
* **Testbench:** [`labs/test_rsqrt.py`](../test_rsqrt.py)

---

## 1. Educational & Architectural Importance

Modern Large Language Models (including LLaMA 3, Mistral, Gemma, and DeepSeek) apply **Root Mean Square Normalization (RMSNorm)** at the input of every attention block and feed-forward network layer:
$$\text{RMSNorm}(x) = \frac{x}{\sqrt{\frac{1}{d} \sum_{i=1}^d x_i^2 + \epsilon}} = x \cdot \text{rsqrt}\left(\frac{1}{d}\sum_{i=1}^d x_i^2 + \epsilon\right)$$

* **Computational Bottleneck:** Computing reciprocal square root via iterative software division ($x / \sqrt{v}$) stalls vector pipelines by dozens of cycles per token.
* **Dedicated SFU Acceleration:** Implementing a specialized hardware `rsqrt` unit computes $1/\sqrt{v}$ directly in fixed-point, converting costly division operations into high-throughput single-cycle multiplications.

---

## 2. Hardware Intuition: Seed LUT & Hybrid Fixed-Point Scaling

* **Hybrid Architecture Strategy:**
  * **Low-Variance Range ($x \in [1, 15]$):** Employs a precomputed 16-entry seed ROM for maximum precision where gradient sensitivity is highest.
  * **Wide Dynamic Range ($x \ge 16$):** Integrates an unrolled digit-by-digit square root extractor to determine integer root $r = \lfloor \sqrt{x} \rfloor$, scaled to Q8.8 fixed-point representation:
    $$y_{\text{out}} = \frac{256}{r}$$
* **Exception Handling:** Includes dedicated zero-detection logic asserting `valid_out = 0` when $x = 0$ to prevent undefined division-by-zero states.

---

## 3. SystemVerilog RTL Architecture

```systemverilog
module rsqrt #(
    parameter int INPUT_WIDTH  = 16,
    parameter int OUTPUT_WIDTH = 16
)(
    input  logic [INPUT_WIDTH-1:0]  x_in,
    output logic [OUTPUT_WIDTH-1:0] y_out,
    output logic                    valid_out
);
    // 1. Division-by-zero detection
    assign valid_out = (x_in != '0);

    // 2. Small-x Seed ROM + Digit-by-Digit Root Engine
    // 3. Fixed-point normalizer and Q8.8 scaling
endmodule
```

### 📐 Logic Synthesis & Hardware Schematic

![rsqrt Synthesis Schematic](../../schematics/rsqrt.svg)

> [!NOTE]
> **Synthesis & Complexity Analysis:**
> * **Sequential Registers (DFF):** `0 DFFs` (Combinational Special Function Unit)
> * **Gate Complexity:** $O(N^2)$ Digit-Recurrence ($\approx 210$ Logic Gates: Small-X Seed ROM + 8-Stage Root Engine + Q8.8 Fixed-Point Scaler)
> * **Latency & Speedup:** $0\text{ Clock Cycles}$ ($\approx 4.6\text{ ns}$ Path Delay, replacing $\sim 30\text{ cycle}$ software division loops)
> * **Target Transformer Layers:** Accelerates RMSNorm & LayerNorm input normalizations in modern LLMs (LLaMA 3, Gemma, Mistral).
> * **Interactive Controls:** Open [`schematics/rsqrt.svg`](../../schematics/rsqrt.svg) in your browser to interactively inspect the Seed ROM, unrolled recurrence stages, and Q8.8 scaling engine.

---

## 4. Verification & Testing with Cocotb

The module is verified against floating-point reference models: $\text{round}(256.0 / \sqrt{x})$.

* **Verification Coverage:**
  * Zero input exception handling: $x = 0 \implies \text{valid\_out} = 0$
  * Small numbers in seed table: $x = 1 \implies 256$, $x = 4 \implies 128$
  * Perfect square inputs: $x = 16 \implies 64$, $x = 64 \implies 32$
  * 1,000 randomized variance values spanning full 16-bit range

To execute the testbench:
```bash
python labs/run_lab.py --lab lab07
```

---

## 5. Review & Engineering Analysis Questions

1. **Algorithmic Alternatives:** How does the Fast Inverse Square Root algorithm (Goldschmidt / Newton-Raphson iterations) compare to digit-recurrence in terms of multiplier silicon budget?
2. **Numerical Precision:** Why is preserving high precision in the small variance range ($x < 16$) critical for stabilizing LayerNorm/RMSNorm gradient backpropagation?
3. **Pipelining Integration:** How does an SFU integrate alongside vector ALUs in a modern Tensor Processing Unit?
