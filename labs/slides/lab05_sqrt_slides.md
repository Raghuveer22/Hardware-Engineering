# 🧪 Lab 05: Hardware Square Root Unit & Attention Scaling
### Attention Variance Scaling Proofs, Digit-Recurrence Silicon & Vanishing Gradient Mitigations

* **Track:** Non-Linear Transformer SFUs
* **RTL:** [`rtl/sqrt.sv`](../../rtl/sqrt.sv)
* **Testbench:** [`labs/test_sqrt.py`](../test_sqrt.py)
* **Next Lab:** [Lab 06: Hardware Softmax & FlashAttention](lab06_softmax_slides.md)

---

## 1. Educational & Architectural Importance

In Transformer Self-Attention, the core interaction between Query ($Q$) and Key ($K$) representations is defined by Scaled Dot-Product Attention:
$$\text{Attention}(Q, K, V) = \text{Softmax}\left( \frac{Q K^T}{\sqrt{d_k}} \right) V$$
where $d_k$ is the projection dimension per attention head (typically $64, 128, 256$).

Without the scaling factor $\frac{1}{\sqrt{d_k}}$, dot-product magnitudes scale linearly with feature dimension, forcing attention probabilities into extreme saturation. A specialized hardware Square Root / SFU unit is critical to stabilize activation variance.

---

## 2. Mathematical Proof: Attention Dot-Product Variance Scaling

### Theorem (Attention Variance Proportionality)
Let Query vector $q \in \mathbb{R}^{d_k}$ and Key vector $k \in \mathbb{R}^{d_k}$ have mutually independent components drawn from zero-mean, unit-variance distributions:
$$\mathbb{E}[q_i] = 0, \quad \text{Var}(q_i) = 1, \quad \mathbb{E}[k_i] = 0, \quad \text{Var}(k_i) = 1 \quad (\forall i \in \{1, \dots, d_k\})$$
Then the dot product $z = q^T k = \sum_{i=1}^{d_k} q_i k_i$ satisfies:
$$\mathbb{E}[z] = 0, \quad \text{Var}(z) = d_k$$
and scaling by $\frac{1}{\sqrt{d_k}}$ guarantees unit variance:
$$\text{Var}\left( \frac{q^T k}{\sqrt{d_k}} \right) = 1.0$$

---

### Step-by-Step Proof:

#### Step 1: Expectation of Dot Product
By linearity of expectation and independence:
$$\mathbb{E}[z] = \mathbb{E}\left[ \sum_{i=1}^{d_k} q_i k_i \right] = \sum_{i=1}^{d_k} \mathbb{E}[q_i k_i] = \sum_{i=1}^{d_k} \mathbb{E}[q_i] \cdot \mathbb{E}[k_i] = \sum_{i=1}^{d_k} 0 \cdot 0 = 0$$

#### Step 2: Variance of Individual Component Products
For two independent random variables $X$ and $Y$ with zero mean ($\mathbb{E}[X] = \mathbb{E}[Y] = 0$):
$$\text{Var}(X Y) = \mathbb{E}[(X Y)^2] - (\mathbb{E}[X Y])^2 = \mathbb{E}[X^2 Y^2] - 0$$
Since $X$ and $Y$ are independent:
$$\mathbb{E}[X^2 Y^2] = \mathbb{E}[X^2] \cdot \mathbb{E}[Y^2] = \text{Var}(X) \cdot \text{Var}(Y)$$
Applying this to $q_i$ and $k_i$:
$$\text{Var}(q_i k_i) = \text{Var}(q_i) \cdot \text{Var}(k_i) = 1 \cdot 1 = 1$$

#### Step 3: Variance of the Sum
Because component products $q_i k_i$ are independent across indices $i$:
$$\text{Var}(z) = \text{Var}\left( \sum_{i=1}^{d_k} q_i k_i \right) = \sum_{i=1}^{d_k} \text{Var}(q_i k_i) = \sum_{i=1}^{d_k} 1 = d_k$$
The standard deviation of unscaled attention logits is therefore:
$$\sigma_z = \sqrt{\text{Var}(z)} = \sqrt{d_k}$$

#### Step 4: Normalization by $1/\sqrt{d_k}$
Applying scalar variance scaling ($\text{Var}(c X) = c^2 \text{Var}(X)$):
$$\text{Var}\left( \frac{z}{\sqrt{d_k}} \right) = \left( \frac{1}{\sqrt{d_k}} \right)^2 \text{Var}(z) = \frac{1}{d_k} \cdot d_k = \mathbf{1.0} \quad \text{(Q.E.D.)}$$

---

## 3. Mathematical Proof: Vanishing Softmax Gradients Without $\sqrt{d_k}$

Why is variance normalization mandatory in hardware? Let us examine the gradient of Softmax:
$$P_i = \text{Softmax}(z)_i = \frac{e^{z_i}}{\sum_{j=1}^N e^{z_j}}$$
The Jacobian derivative of $P_i$ with respect to logit $z_j$ is:
$$\frac{\partial P_i}{\partial z_j} = P_i (\delta_{ij} - P_j)$$

### The Saturation Failure Mode:
* If $d_k = 128$, the unscaled standard deviation is $\sigma = \sqrt{128} \approx 11.31$.
* Typical logits will vary across ranges like $[-20, +25]$.
* When fed into Softmax, the maximum logit $z_{max}$ dominates the exponent:
  $$e^{25} \approx 7.2 \times 10^{10} \gg e^{5} \approx 148$$
* Softmax collapses into a discrete **one-hot distribution**:
  $$P_{max} \approx 1.0, \quad P_{j \ne max} \approx 0.0$$
* Evaluating the gradients:
  1. For the winning index ($i = j = max$):
     $$\frac{\partial P_{max}}{\partial z_{max}} = P_{max} (1 - P_{max}) \approx 1.0 \times (1.0 - 1.0) = \mathbf{0.0}$$
  2. For all other indices ($i \ne max$):
     $$\frac{\partial P_i}{\partial z_j} \approx 0.0 \times (\delta_{ij} - P_j) = \mathbf{0.0}$$
* **Result:** The gradient vector $\nabla_z P \to \mathbf{0}$ vanishes completely. Backpropagation stalls, and the attention mechanism cannot update its projection weights. Dividing by $\sqrt{d_k}$ pulls logits back into dynamic range $[-2.0, +2.0]$, where gradients remain active ($P(1-P) \approx 0.25$).

---

## 4. Hardware Sqrt Architectures: Silicon Trade-Off Analysis

$$\begin{array}{|l|c|c|c|c|l|}
\hline
\textbf{Architecture} & \textbf{Algorithm Type} & \textbf{Cycle Latency} & \textbf{Area Complexity} & \textbf{Multiplier Required?} & \textbf{Primary Silicon Application} \\
\hline
\textbf{Digit-Recurrence (Lab 05)} & \text{Shift-and-Subtract} & 1\text{ cycle (unrolled)} & O(N^2)\text{ subtractors} & \textbf{No (Zero Multipliers)} & \text{Fixed-Point SFUs, Low-Power NPUs} \\
\textbf{SRT Non-Restoring} & \text{Redundant Radix-2/4} & N/2\text{ cycles} & O(N)\text{ cells} & \textbf{No} & \text{IEEE-754 FPU Sqrt Units} \\
\textbf{CORDIC Vectoring} & \text{Hyperbolic Rotation} & N\text{ cycles} & O(N)\text{ adders} & \textbf{No} & \text{DSP co-processors, FPGA SFUs} \\
\textbf{Newton-Raphson} & \text{Quadratic Recurrence} & 3\text{--}4\text{ iterations} & \text{High (Multiplier tree)} & \textbf{Yes (DSP blocks)} & \text{GPU SFU Pipes (CUDA FP32 rsqrt)} \\
\hline
\end{array}$$

### Why Digit-Recurrence Restoring Wins for Pre-Silicon SFUs:
* **Zero Multiplier Dependency:** Requires only simple subtractors and 2:1 multiplexers.
* **Exact Integer Bounds:** Produces exact integer root $\lfloor \sqrt{X} \rfloor$ and exact remainder $R$ satisfying:
  $$X = \text{root}^2 + R, \quad 0 \le R \le 2 \cdot \text{root}$$

---

## 5. SystemVerilog RTL Architecture ([`rtl/sqrt.sv`](../../rtl/sqrt.sv))

The synthesizable module in `rtl/sqrt.sv` implements an unrolled 8-stage digit-recurrence pipeline:

```systemverilog
`timescale 1ns/1ps

module sqrt #(
    parameter int RADICAND_WIDTH = 16,                         // Input width (e.g., 16 bits for 0..65535)
    parameter int ROOT_WIDTH     = (RADICAND_WIDTH + 1) / 2    // Output root width (8 bits for 0..255)
)(
    input  logic [RADICAND_WIDTH-1:0] radicand,
    output logic [ROOT_WIDTH-1:0]     root,
    output logic [RADICAND_WIDTH-1:0] remainder
);

    // Combinational digit-by-digit non-restoring / shift-and-subtract square root algorithm
    logic [RADICAND_WIDTH+1:0] rem_reg;
    logic [ROOT_WIDTH-1:0]     root_reg;
    logic [RADICAND_WIDTH+1:0] test_val;

    always_comb begin
        rem_reg  = '0;
        root_reg = '0;

        // Iterate through bit pairs from MSB to LSB
        for (int i = ROOT_WIDTH - 1; i >= 0; i--) begin
            // Shift remainder left by 2 bits and bring down next 2 bits of radicand
            rem_reg = (rem_reg << 2) | ((radicand >> (2 * i)) & 2'b11);

            // Candidate trial value: (root * 4 + 1)
            test_val = {root_reg, 2'b01};

            if (rem_reg >= test_val) begin
                rem_reg  = rem_reg - test_val;
                root_reg = (root_reg << 1) | 1'b1;
            end else begin
                root_reg = (root_reg << 1) | 1'b0;
            end
        end

        root      = root_reg;
        remainder = rem_reg[RADICAND_WIDTH-1:0];
    end

endmodule
```

### 📐 Logic Synthesis & Hardware Schematic

![sqrt Synthesis Schematic](../../schematics/sqrt.svg)

> [!NOTE]
> **Synthesis & Complexity Analysis:**
> * **Sequential Registers (DFF):** `0 DFFs` (Unrolled Combinational Recurrence Datapath)
> * **Standard Cell Count:** $39\text{ cells}$ (8 Subtractor stages `$sub`, 16 Multiplexers `$mux`, 8 Comparators `$ge`, 7 OR gates `$or`)
> * **Critical Path Latency:** $\approx 4.2\text{ ns}$ (8-stage subtract-and-compare ripple)
> * **Arithmetic Invariant:** Exactly satisfies $\text{radicand} = \text{root}^2 + \text{remainder}$ across all $2^{16}$ input vectors.
> * **Interactive Netlist:** Open [`schematics/sqrt.svg`](../../schematics/sqrt.svg) in a browser to trace the bit-pair extraction shift logic down the 8 subtractor stages.

---

## 6. Real-World Accelerator Mapping: NVIDIA SM SFU & Google TPU VPUs

### NVIDIA CUDA Streaming Multiprocessor (SM) SFU
* In NVIDIA Hopper and Blackwell SMs, transcendentals ($\sqrt{x}$, $1/\sqrt{x}$, $2^x$, $\sin$, $\cos$) are executed in dedicated **Special Function Units (SFUs)**.
* Each SFU pipeline runs at 1/4 the throughput of standard FP32 cores.
* Quadratic Taylor expansion and minimax polynomial interpolation tables evaluate $\sqrt{x}$ in single precision FP32 with $< 1\text{ ULP}$ error.

### Google TPU Vector Processing Unit (VPU)
* In Google TPU v4/v5, vector transcendental engines execute reciprocal square root instructions vectorized across 128-lane SIMD datapaths.
* Attention head scaling factors ($1/\sqrt{d_k}$) are precomputed during kernel compilation and loaded into vector registers as scalar broadcast constants to eliminate runtime SFU bottlenecks.

---

## 7. Verification & Testing with Cocotb

The module is verified against Python `math.isqrt()` in [`labs/test_sqrt.py`](../test_sqrt.py):

* **Verified Corner Cases:**
  1. Zero and unit boundary conditions: $\text{isqrt}(0) = 0$, $\text{isqrt}(1) = 1$, $\text{isqrt}(2) = 1 \ (R=1)$, $\text{isqrt}(3) = 1 \ (R=2)$.
  2. Perfect squares: $64 \to 8 \ (R=0)$, $144 \to 12 \ (R=0)$, $65,025 \to 255 \ (R=0)$.
  3. Maximum 16-bit input: $65,535 \to \text{root}=255, \text{remainder}=510$.
  4. Exhaustive verification across all $65,536$ inputs, verifying $X = \text{root}^2 + \text{remainder}$ on every single vector.

To execute the verification suite:
```bash
python labs/run_lab.py --lab lab05
```

---

## 8. Review & Engineering Analysis Questions

1. **Variance Scaling Proof:** Derive mathematically why the variance of the inner product of two independent $d_k$-dimensional Gaussian vectors is $d_k$, and explain why dividing by $\sqrt{d_k}$ normalizes the variance to $1.0$.
2. **Softmax Saturation Jacobian:** Prove that when attention logits exhibit large variance, the Jacobian derivative $\frac{\partial \text{Softmax}_i}{\partial z_j}$ approaches zero everywhere.
3. **Remainder Upper Bound:** Prove that the remainder $R$ from an integer square root of $X$ cannot exceed $2 \cdot \text{root}$.
