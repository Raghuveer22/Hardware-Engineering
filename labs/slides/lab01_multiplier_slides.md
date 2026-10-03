# 🔬 Lab 01: Parameterized Signed Multiplier (INT8)
### Wallace Trees, Radix-4 Modified Booth Encoding & $O(N^2)$ Silicon Area Dynamics

* **Track:** Silicon Arithmetic & Math Engines
* **RTL:** [`rtl/multiplier_int8.sv`](../../rtl/multiplier_int8.sv)
* **Testbench:** [`labs/test_multiplier.py`](../test_multiplier.py)
* **Next Lab:** [Lab 02: Multiply-Accumulate (MAC) Unit](lab02_mac_unit_slides.md)

---

## 1. Educational & Architectural Importance

Matrix multiplication ($Y = W \cdot X$) accounts for over 90% of total arithmetic operations and energy dissipation in Deep Learning workloads (Transformers, Convolutional Networks, Recommendation Models).

### A. Quadratic Silicon Area Scaling: $O(N)$ Adder vs. $O(N^2)$ Multiplier
While an adder requires $N$ full-adder cells scaling linearly ($O(N)$), an $N$-bit multiplier must compute all combinations of input bit pairs:
$$\text{Number of 1-bit Partial Products} = N \times N = N^2$$
* For **INT8** ($8 \times 8$): $8^2 = 64$ partial product bits, synthesized into $\approx 456$ standard cell gates.
* For **INT16** ($16 \times 16$): $16^2 = 256$ partial product bits, synthesized into $\approx 1,824$ gates ($4\times$ area increase).
* For **FP32** ($24$-bit mantissa multiplier + exponent datapath + normalizer): $> 7,000$ gates ($16\times$ area and energy increase).

### B. The Quantization Energy Dividend
Transitioning a neural network from 32-bit floating point (FP32) to 8-bit quantized integer (INT8) provides exponential silicon savings:
$$\text{Area Savings} = \frac{\text{Area}(24\text{-bit Mantissa Mul})}{\text{Area}(8\text{-bit INT8 Mul})} \approx \frac{576}{64} \approx 9\times \text{ (Arithmetic Core)}$$
Including control, rounding, and normalization logic, total FP32 to INT8 datapath energy drops by **$16\times$ ($4.0\text{ pJ} \to 0.2\text{ pJ}$)**. This fundamental physical reality enables modern AI accelerators (such as Google TPU and NVIDIA Hopper) to pack hundreds of thousands of parallel multipliers onto a single silicon die.

---

## 2. Hardware Intuition: How Silicon Multiplies

### A. Partial Product Generation ($8 \times 8$ AND Matrix)
In digital silicon, binary multiplication begins by generating an array of 1-bit partial products $p_{i,j} = a_i \cdot b_j$ using 2-input AND gates:

```
                  a7    a6    a5    a4    a3    a2    a1    a0   (Multiplicand A)
            x     b7    b6    b5    b4    b3    b2    b1    b0   (Multiplier B)
            ──────────────────────────────────────────────────
Row 0:           p0,7  p0,6  p0,5  p0,4  p0,3  p0,2  p0,1  p0,0  (A · b0 << 0)
Row 1:     p1,7  p1,6  p1,5  p1,4  p1,3  p1,2  p1,1  p1,0        (A · b1 << 1)
Row 2:     ...                                                 (A · b2 << 2)
Row 7: p7,7 ...                                                (A · b7 << 7)
```
Each row $j$ represents multiplicand $A$ gated by bit $b_j$ and physically shifted left by $j$ bit positions.

---

### B. The Signed Two's Complement Trap & Baugh-Wooley Algorithm
Naively feeding signed two's complement numbers into an unsigned shift-and-add multiplier leads to catastrophic numerical corruption:
* In two's complement, the MSB bit weight is **negative** ($-2^{N-1}$):
  $$A = -a_{N-1} 2^{N-1} + \sum_{i=0}^{N-2} a_i 2^i, \quad B = -b_{N-1} 2^{N-1} + \sum_{j=0}^{N-2} b_j 2^j$$
* The full product expansion contains cross-terms with negative weights:
  $$A \cdot B = \left( a_{N-1} b_{N-1} 2^{2N-2} \right) + \sum_{i=0}^{N-2} \sum_{j=0}^{N-2} a_i b_j 2^{i+j} - 2^{N-1} \sum_{i=0}^{N-2} a_i b_{N-1} 2^i - 2^{N-1} \sum_{j=0}^{N-2} a_{N-1} b_j 2^j$$
* **Baugh-Wooley Architecture:** Rather than performing sign-extension (which wastes gates and wire tracks), Baugh-Wooley transforms negative terms into positive terms using the identity $-X = \overline{X} - 1$. By inverting specific partial product bits and injecting constant bias bits ($1$) into specific columns, all partial products are treated as positive operands, enabling a regular, high-density silicon layout.

---

### C. Bit Growth Proof & The Asymmetric Corner Case
When multiplying two signed numbers with bitwidths $W_A$ and $W_B$, the required output bitwidth is:
$$\text{PROD\_WIDTH} = W_A + W_B$$

#### The Asymmetric Two's Complement Proof:
Consider $W_A = W_B = 8$ (Range: $[-128, +127]$):
1. **Positive Maximum:**
   $$+127 \times +127 = +16,129_{10} = \text{0011\_1111\_0000\_0001}_2 \quad \text{(Requires 15 bits)}$$
2. **Negative Maximum:**
   $$-128 \times +127 = -16,256_{10} = \text{1100\_0000\_1100\_0000}_2 \quad \text{(Requires 15 bits)}$$
3. **The Asymmetric Corner Case ($(-128) \times (-128)$):**
   $$-128 \times -128 = \mathbf{+16,384_{10}}$$
   In 16-bit signed two's complement:
   $$+16,384_{10} = \mathbf{0100\_0000\_0000\_0000}_2$$
   * Notice that Bit 14 is `1` and Bit 15 (Sign Bit) is `0`.
   * If the output were truncated to **15 bits**, Bit 14 would become the sign bit, misinterpreting $+16,384$ as **$-16,384$**!
   * Hence, exactly **16 bits** ($W_A + W_B$) are strictly necessary to represent all signed products without overflow.

---

## 3. High-Speed Multiplier Microarchitectures

Real-world AI accelerators do not use slow $O(N)$ ripple carry arrays to sum partial products. They employ a three-stage pipelined architecture:
1. **Recoding (Radix-4 Modified Booth Encoding)**: Halves the number of partial product rows.
2. **Compression (Wallace / Dadda Carry-Save Trees)**: Compresses rows from $M$ down to $2$ in $O(\log_{1.5} M)$ time.
3. **Vector Merge (Carry-Propagate Adder)**: Sums the final carry and sum vectors.

```
       [ Operands A & B ]
               │
               ▼
   ┌───────────────────────┐
   │ Radix-4 Booth Encoder │ ──► Cuts 8 partial product rows down to 4 rows
   └───────────┬───────────┘
               │ (4 Rows)
               ▼
   ┌───────────────────────┐
   │ Wallace CSA Tree      │ ──► Compresses 4 rows to 2 vectors (Carry & Sum)
   └───────────┬───────────┘
               │ (2 Vectors: Carry & Sum)
               ▼
   ┌───────────────────────┐
   │ Final CPA (16-bit)    │ ──► Resolves to final 16-bit Product
   └───────────────────────┘
```

---

### A. Radix-4 Modified Booth Encoding
Modified Booth recoding scans the multiplier $B$ in **overlapping 3-bit windows** $(b_{2i+1}, b_{2i}, b_{2i-1})$ with an implicit $b_{-1} = 0$:

$$\text{Value} = -2 b_{2i+1} + b_{2i} + b_{2i-1}$$

#### Radix-4 Recoding Truth Table
$$\begin{array}{|c|c|c|c|c|l|}
\hline
b_{2i+1} & b_{2i} & b_{2i-1} & \text{Recoded Digit } d_i & \text{Operation on } A & \text{Hardware Implementation} \\
\hline
0 & 0 & 0 & 0 & 0 \times A & \text{Zero out partial product row} \\
0 & 0 & 1 & +1 & +1 \times A & \text{Pass } A \text{ unchanged} \\
0 & 1 & 0 & +1 & +1 \times A & \text{Pass } A \text{ unchanged} \\
0 & 1 & 1 & +2 & +2 \times A & \text{Hardwired 1-bit left shift of } A \\
1 & 0 & 0 & -2 & -2 \times A & \text{Invert bits of } 2A \text{ and inject } +1 \text{ carry} \\
1 & 0 & 1 & -1 & -1 \times A & \text{Invert bits of } A \text{ and inject } +1 \text{ carry} \\
1 & 1 & 0 & -1 & -1 \times A & \text{Invert bits of } A \text{ and inject } +1 \text{ carry} \\
1 & 1 & 1 & 0 & 0 \times A & \text{Zero out partial product row} \\
\hline
\end{array}$$

* **Silicon Impact:** For an 8-bit multiplier ($N=8$), the number of partial product rows is reduced from $N=8$ down to $\lceil N/2 \rceil = 4$. Halving the partial products eliminates half the adder cells and reduces tree depth significantly!

---

### B. Carry-Save Adder (CSA) Reduction: Wallace & Dadda Trees
Once partial products are generated, summing them row-by-row with standard adders would incur a crippling $O(N)$ propagation delay. Instead, hardware uses **Carry-Save Adders (CSA)**:
* A Full Adder acts as a **3:2 Compressor**: it takes 3 input bits at weight $2^k$ and outputs 1 sum bit at weight $2^k$ and 1 carry bit at weight $2^{k+1}$.
* **Crucial Property:** The carry does **NOT propagate** across adjacent columns! It is simply routed to the next stage's column. Every CSA stage evaluates in $O(1)$ constant time ($\approx 1$ gate delay).

#### Logarithmic Wallace Tree Height Reduction
The height of the partial product matrix reduces by a factor of $1.5\times$ per level:
$$h_{j+1} = \left\lfloor \frac{2}{3} h_j \right\rfloor + (h_j \pmod 3)$$
For 8 initial rows (without Booth) or 4 rows (with Booth):
* **With Booth (4 rows):**
  * Stage 1: Compress 3 rows using 3:2 adders $\to$ produces 2 rows + 1 uncompressed row = 3 rows.
  * Stage 2: Compress 3 rows $\to$ 2 rows.
  * Total CSA reduction depth: **2 gate levels**!
* **Wallace Tree Depth:** $O(\log_{1.5}(N))$, slashing combinational propagation delay from $\approx 8\text{ ns}$ down to $\approx 2.8\text{ ns}$.

---

## 4. SystemVerilog RTL Architecture ([`rtl/multiplier_int8.sv`](../../rtl/multiplier_int8.sv))

The synthesizable module in `rtl/multiplier_int8.sv` implements a clean, parameterized interface:

```systemverilog
`timescale 1ns/1ps

module multiplier_int8 #(
    parameter int DATA_WIDTH = 8,
    parameter int PROD_WIDTH = 2 * DATA_WIDTH // 16 bits for 8x8
)(
    input  logic signed [DATA_WIDTH-1:0] a,
    input  logic signed [DATA_WIDTH-1:0] b,
    output logic signed [PROD_WIDTH-1:0] product
);

    // Combinational signed multiplication
    // Synthesis maps this to standard cell Booth/Wallace tree multipliers
    assign product = a * b;

endmodule
```

### 📐 Logic Synthesis & Hardware Schematic

![multiplier_int8 Synthesis Schematic](../../schematics/multiplier_int8.svg)

> [!NOTE]
> **Synthesis & Complexity Metrics:**
> * **Sequential Registers (DFF):** `0 DFFs` (Pure Combinational Circuit)
> * **Combinational Standard Cells:** $1\text{ macro cell}$ (synthesizes to $\approx 456$ equivalent logic gates)
> * **Critical Path Latency:** $\approx 2.8\text{ ns}$ (Wallace Tree CSA + 16-bit CPA)
> * **Operand Precision:** Signed INT8 ($[-128, +127]$) $\times$ Signed INT8 $\to$ Signed INT16 ($[-16,256 \dots +16,384]$)
> * **Interactive Netlist:** Open [`schematics/multiplier_int8.svg`](../../schematics/multiplier_int8.svg) in a browser to trace operand input buses through the internal multiplier netlist.

---

## 5. Accelerator Mapping: NVIDIA Tensor Cores & Google TPU

### NVIDIA Tensor Core INT8 Execution Tile
In NVIDIA Ampere (A100) and Hopper (H100) GPUs, Tensor Cores process integer matrix math via native instructions:
* **`mma.sync.aligned.m16n8k32.row.col`**: Executes a dense matrix multiply-accumulate tile $D = A \times B + C$ where $A$ and $B$ are INT8 matrices and accumulation occurs in INT32.
* Inside each Tensor Core sub-core, a cluster of 64 INT8 multipliers execute in parallel every cycle.
* Multiplier outputs feed directly into internal 4:2 carry-save compressor trees to merge products before updating the 32-bit register file.

### Google TPU v1–v4 Multiplier Arrays
* The Google TPU Matrix Multiply Unit (MXU) contains a 2D grid of $128 \times 128$ (TPU v2/v3) or $256 \times 256$ (TPU v1) processing elements.
* Every processing element integrates an INT8 signed multiplier coupled to a 32-bit adder.
* The multiplier datapath is optimized for extreme low-power FinFET operation, consuming approximately **$200\text{ fJ} \ (0.2\text{ pJ})$** per $8\text{-bit} \times 8\text{-bit}$ multiply.

---

## 6. Verification & Testing with Cocotb

The module is verified using Cocotb in [`labs/test_multiplier.py`](../test_multiplier.py) against Python signed arithmetic:

* **Corner Cases Evaluated:**
  1. Identity scaling ($a \times 1 = a$, $a \times 0 = 0$).
  2. Maximum positive multiplication ($+127 \times +127 = +16,129$).
  3. Maximum negative multiplication ($-128 \times +127 = -16,256$).
  4. The two's complement asymmetric boundary ($-128 \times -128 = +16,384$).
  5. Uniformly distributed pseudorandom signed test vectors across the entire $2^{16}$ input space.

To run the verification suite:
```bash
python labs/run_lab.py --lab lab01
```

---

## 7. Review & Engineering Analysis Questions

1. **Analytical Gate Scaling:** Derive why an $N$-bit multiplier scales as $O(N^2)$ in silicon area, and calculate the exact gate ratio between a 32-bit mantissa multiplier and an 8-bit multiplier.
2. **Booth Recoding Efficiency:** How does Radix-4 Modified Booth Encoding halve the number of partial product rows, and what hardware trade-off is introduced in generating the $-2A$ and $+2A$ terms?
3. **The 16th Bit Necessity:** Explain why $-128 \times -128 = +16,384$ strictly requires a 16-bit two's complement output representation, and detail what numerical error occurs if a 15-bit accumulator is used.
