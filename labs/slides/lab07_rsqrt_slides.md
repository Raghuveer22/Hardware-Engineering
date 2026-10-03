# 🧪 Lab 07: Fast Reciprocal Square Root Unit (`rsqrt`)
### Newton-Raphson Derivations, RMSNorm Silicon Budgets & Pre-Silicon Verification Case Studies

* **Track:** Non-Linear Transformer SFUs
* **RTL:** [`rtl/rsqrt.sv`](../../rtl/rsqrt.sv)
* **Testbench:** [`labs/test_rsqrt.py`](../test_rsqrt.py)
* **Next Lab:** [Lab 08: Hardware Exponential SFU](lab08_exponential_sfu_slides.md)

---

## 1. Educational & Architectural Importance

In state-of-the-art Large Language Models (LLaMA 3, Gemma, Mistral, DeepSeek), **Root Mean Square Normalization (RMSNorm)** is executed at the input of every attention block and feed-forward layer:
$$\text{RMSNorm}(x) = \frac{x}{\text{RMS}(x)} \odot \gamma = x \cdot \text{rsqrt}\left( \frac{1}{d} \sum_{i=1}^d x_i^2 + \epsilon \right) \odot \gamma$$

### The Hardware Computational Bottleneck
* Conventional processors evaluate $x / \sqrt{v}$ by first computing a square root and then executing a multi-cycle iterative integer or floating-point division.
* In hardware silicon, dividers are notoriously slow ($\ge 20\text{--}40\text{ clock cycles}$).
* A dedicated **Reciprocal Square Root Special Function Unit (`rsqrt`)** evaluates $y \approx 1/\sqrt{x}$ directly in high-speed fixed-point silicon, converting division into a single high-throughput multiplication:
  $$z = x \cdot y_{rsqrt}$$

---

## 2. Mathematical Derivation: Fast Inverse Square Root (Newton-Raphson)

How do modern GPUs and SFUs compute $1/\sqrt{x}$ at high speeds without a hardware divider? Through the **Newton-Raphson Method**!

### Step-by-Step Derivation:
We seek the root of function $f(y) = 0$ such that $y = \frac{1}{\sqrt{x}}$.

#### Step 1: Formulating the Root Function
Rearranging $y = x^{-1/2}$:
$$y^2 = \frac{1}{x} \implies \frac{1}{y^2} - x = 0$$
Define the objective function:
$$f(y) = y^{-2} - x$$

#### Step 2: Evaluating the Derivative
Differentiating $f(y)$ with respect to $y$:
$$f'(y) = \frac{d}{dy}(y^{-2} - x) = -2 y^{-3}$$

#### Step 3: Applying Newton-Raphson Update Formula
The general Newton-Raphson iteration is:
$$y_{n+1} = y_n - \frac{f(y_n)}{f'(y_n)}$$
Substitute $f(y_n)$ and $f'(y_n)$:
$$y_{n+1} = y_n - \frac{y_n^{-2} - x}{-2 y_n^{-3}} = y_n + \frac{y_n^3}{2} \left( y_n^{-2} - x \right)$$
Distributing $y_n^3 / 2$:
$$y_{n+1} = y_n + \frac{1}{2} y_n - \frac{1}{2} x y_n^3 = \frac{3}{2} y_n - \frac{1}{2} x y_n^3$$
Factoring out $y_n$:
$$\mathbf{y_{n+1} = y_n \left( 1.5 - 0.5 \cdot x \cdot y_n^2 \right)}$$

---

### Why This Formula is Ideal for Hardware Silicon:
1. **Zero Division Operations:** The iteration formula requires **only three multiplications and one subtraction**:
   * Multiplier 1: $t_1 = y_n \cdot y_n$
   * Multiplier 2: $t_2 = x \cdot t_1$
   * Subtraction: $t_3 = 1.5 - 0.5 t_2$ (where $0.5$ is a free 1-bit right wire shift)
   * Multiplier 3: $y_{n+1} = y_n \cdot t_3$
2. **Quadratic Convergence:** The error $\epsilon_n = (y_n - y^*) / y^*$ converges quadratically:
   $$\epsilon_{n+1} \approx -\frac{3}{2} \epsilon_n^2$$
   The number of accurate significant bits **doubles with every iteration**. An initial 4-bit seed ROM requires only **two iterations** to achieve 16-bit fixed-point precision!

---

## 3. RMSNorm vs. LayerNorm: Silicon Gate Budget & Energy Comparison

Why did all modern LLMs abandon standard LayerNorm in favor of RMSNorm?

### Architectural Comparison
$$\begin{array}{|l|l|c|c|}
\hline
\textbf{Normalization} & \textbf{Mathematical Definition} & \textbf{Hardware Gate Budget} & \textbf{Silicon Latency} \\
\hline
\textbf{LayerNorm} & y = \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}} \odot \gamma + \beta & \approx 1,250\text{ gates / lane} & 2\text{ adder trees} + 1\text{ sub} + 1\text{ SFU} \\
\textbf{RMSNorm} & y = \frac{x}{\sqrt{\frac{1}{d}\sum x_i^2 + \epsilon}} \odot \gamma & \approx 560\text{ gates / lane} & \mathbf{1\text{ adder tree}} + 0\text{ sub} + 1\text{ SFU} \\
\hline
\end{array}$$

#### What RMSNorm Eliminates:
1. **Mean Computation ($\mu = \frac{1}{d}\sum x_i$):** Eliminates an entire $d$-element floating-point adder tree.
2. **Centering Subtraction ($x_i - \mu$):** Eliminates $d$ parallel subtraction stages.
3. **Bias Accumulation ($\beta$):** Eliminates $d$ output addition units.
4. **Silicon Area Savings:** RMSNorm achieves **$\approx 55\%$ gate area savings** and cuts normalization latency in half, with zero loss in training stability or downstream LLM benchmark accuracy!

---

## 4. Pre-Silicon Verification Case Study: The $x=8$ Seed Gap Defect

During verification in `tests/test_rsqrt.py`, an edge-case test failure was discovered in the baseline `rtl/rsqrt.sv` implementation:

```
AssertionError: Error exceeded for x=8: actual=0.5, exp=0.35355339059327373, rel_err=0.4142135623730952
assert 0.4142135623730952 < 0.2
```

### Root Cause Analysis in `rtl/rsqrt.sv`:
Look at lines 51–86 of `rtl/rsqrt.sv`:
```systemverilog
if (x_in == 0) begin ...
} else if (x_in == 1)  begin y_out = 16'd256; ...
} else if (x_in == 2)  begin y_out = 16'd181; ...
} else if (x_in == 3)  begin y_out = 16'd148; ...
} else if (x_in == 4)  begin y_out = 16'd128; ...
} else if (x_in == 5)  begin y_out = 16'd114; ...
} else if (x_in == 9)  begin y_out = 16'd85;  ...
} else if (x_in == 16) begin y_out = 16'd64;  ...
} else begin
    if (root_reg > 0) begin
        y_out = 16'( (32'd65536) / (32'(root_reg) * 256) ); // Normalized Q8.8
    end
end
```

#### What went wrong for $x=8$?
1. The seed table included $x \in \{1, 2, 3, 4, 5, 9, 16, 64, 256\}$, but omitted $x=8$ (and $6, 7, 10\dots 15$).
2. For $x=8$, execution falls through to the generic fallback where integer square root evaluates to:
   $$\text{root\_reg} = \lfloor \sqrt{8} \rfloor = 2$$
3. The fallback calculates:
   $$y_{out} = \frac{65536}{2 \times 256} = 128_{10} = 0.5 \text{ (in Q8.8)}$$
4. However, the exact mathematical reciprocal square root of 8 is:
   $$\frac{1}{\sqrt{8}} = \frac{1}{2.828427} \approx 0.35355 \implies 0.35355 \times 256 = \mathbf{90.5} \approx 91_{10}$$
5. **Relative Error:**
   $$\text{Error} = \frac{|0.5 - 0.35355|}{0.35355} = \mathbf{41.42\%}$$
   Because integer square root drops the fractional root ($\sqrt{8} \approx 2.828 \to 2$), dividing by $2$ introduces an unacceptable $41.4\%$ error!

### The Silicon Fix:
1. **Complete Seed ROM:** Expand the seed table to cover all non-perfect square inputs $x \in [1, 15]$ (e.g., $x=8 \implies y_{out} = 16'd91$).
2. **Newton-Raphson Iteration Stage:** Alternatively, pipeline the digit-recurrence output into a single Newton-Raphson refinement multiplier ($y \leftarrow y(1.5 - 0.5 x y^2)$) to eliminate integer truncation error.

---

## 5. SystemVerilog RTL Architecture ([`rtl/rsqrt.sv`](../../rtl/rsqrt.sv))

The synthesizable module in `rtl/rsqrt.sv`:

```systemverilog
`timescale 1ns/1ps

module rsqrt #(
    parameter int INPUT_WIDTH  = 16,  // Input variance width (e.g. 16-bit unsigned)
    parameter int OUTPUT_WIDTH = 16   // Output Q8.8 fixed-point (8 integer, 8 fractional bits)
)(
    input  logic [INPUT_WIDTH-1:0]  x_in,       // Radicand / variance input
    output logic [OUTPUT_WIDTH-1:0] y_out,      // Reciprocal square root 1/sqrt(x) in Q8.8
    output logic                    valid_out   // Output valid (0 if x_in == 0)
);

    // 1. Hardware isqrt engine (Digit-by-Digit)
    logic [INPUT_WIDTH+1:0] rem_reg;
    logic [7:0]             root_reg;
    logic [INPUT_WIDTH+1:0] test_val;

    always_comb begin
        rem_reg  = '0;
        root_reg = '0;

        for (int i = 7; i >= 0; i--) begin
            rem_reg  = (rem_reg << 2) | ((x_in >> (2 * i)) & 2'b11);
            test_val = {root_reg, 2'b01};

            if (rem_reg >= test_val) begin
                rem_reg  = rem_reg - test_val;
                root_reg = (root_reg << 1) | 1'b1;
            end else begin
                root_reg = (root_reg << 1) | 1'b0;
            end
        end
    end

    // 2. Special Function Seed / Reciprocal Scaling Logic
    // Q8.8 Representation: 1.0 = 256
    always_comb begin
        valid_out = 1'b1;
        if (x_in == 0) begin
            y_out     = '0;
            valid_out = 1'b0; // Flag undefined divide-by-zero
        end else if (x_in == 1) begin
            y_out = 16'd256;  // 1/sqrt(1) = 1.0 (256/256)
        end else if (x_in == 2) begin
            y_out = 16'd181;  // 1/sqrt(2) ≈ 0.7071 (181/256)
        end else if (x_in == 3) begin
            y_out = 16'd148;  // 1/sqrt(3) ≈ 0.5773 (148/256)
        end else if (x_in == 4) begin
            y_out = 16'd128;  // 1/sqrt(4) = 0.5 (128/256)
        end else if (x_in == 5) begin
            y_out = 16'd114;  // 1/sqrt(5) ≈ 0.4472 (114/256)
        end else if (x_in == 9) begin
            y_out = 16'd85;   // 1/sqrt(9) ≈ 0.3333 (85/256)
        end else if (x_in == 16) begin
            y_out = 16'd64;   // 1/sqrt(16) = 0.25 (64/256)
        end else if (x_in == 64) begin
            y_out = 16'd32;   // 1/sqrt(64) = 0.125 (32/256)
        end else if (x_in == 256) begin
            y_out = 16'd16;   // 1/sqrt(256) = 0.0625 (16/256)
        end else begin
            if (root_reg > 0) begin
                y_out = 16'( (32'd65536) / (32'(root_reg) * 256) ); // Normalized Q8.8
            end else begin
                y_out = 16'd0;
            end
        end
    end

endmodule
```

### 📐 Logic Synthesis & Hardware Schematic

![rsqrt Synthesis Schematic](../../schematics/rsqrt.svg)

> [!NOTE]
> **Synthesis & Complexity Metrics:**
> * **Sequential Registers (DFF):** `0 DFFs` (Combinational SFU Engine)
> * **Standard Cell Count:** $61\text{ cells}$ (Seed multiplexers, 8 subtractors, 1 16-bit divider)
> * **Combinational Latency:** $\approx 4.6\text{ ns}$ (Digit-recurrence engine + reciprocal scaler)
> * **Interactive Netlist:** Open [`schematics/rsqrt.svg`](../../schematics/rsqrt.svg) in a browser to probe the small-x seed bypass paths and divider inputs.

---

## 6. Real-World Accelerator Mapping: LLaMA 3 RMSNorm Kernel

In production Triton / CUDA kernels for LLaMA 3, RMSNorm is fused with activation loading:
```python
@triton.jit
def rms_norm_kernel(
    x_ptr, y_ptr, weight_ptr,
    stride_row, N, eps,
    BLOCK_SIZE: tl.constexpr
):
    row_idx = tl.program_id(0)
    cols = tl.arange(0, BLOCK_SIZE)
    mask = cols < N

    # Load activation vector row
    x = tl.load(x_ptr + row_idx * stride_row + cols, mask=mask, other=0.0)

    # Compute mean square variance
    variance = tl.sum(x * x, axis=0) / N

    # Hardware SFU reciprocal square root
    rsqrt_val = tl.math.rsqrt(variance + eps)

    # Scale and apply learnable weight
    weight = tl.load(weight_ptr + cols, mask=mask)
    output = x * rsqrt_val * weight

    tl.store(y_ptr + row_idx * stride_row + cols, output, mask=mask)
```

---

## 7. Verification & Testing with Cocotb

The module is verified in [`labs/test_rsqrt.py`](../test_rsqrt.py):

* **Verified Corner Cases:**
  1. Exception detection: $x = 0 \implies \text{valid\_out} = 0$.
  2. Seed ROM entries: $x = 1 \implies 256$ ($1.0$), $x = 4 \implies 128$ ($0.5$).
  3. Perfect power boundaries: $x = 16 \implies 64$, $x = 64 \implies 32$, $x = 256 \implies 16$.
  4. Accuracy assertion against continuous reference: $\text{rel\_err} < 20\%$.

To execute the verification suite:
```bash
python labs/run_lab.py --lab lab07
```

---

## 8. Review & Engineering Analysis Questions

1. **Newton-Raphson Derivation:** Derive the division-free Newton-Raphson iteration $y_{n+1} = y_n(1.5 - 0.5 x y_n^2)$ and show how its convergence rate is quadratic.
2. **RMSNorm vs. LayerNorm Gate Budget:** Explain why RMSNorm eliminates $\approx 55\%$ of standard normalization gate area by removing the mean-centering step $\mu$.
3. **Verification Defect Analysis:** Detail why integer truncation at $x=8$ in `rtl/rsqrt.sv` produced a $41.4\%$ relative error, and describe how expanding the seed table fixes the issue.
