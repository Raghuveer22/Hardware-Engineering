# 🧪 Lab 04: 2D Systolic Matrix Multiplier Array
### 2D Wavefront Pipeline, Activation Skewing & High-Throughput Spatial GEMM

* **Track:** TPU & 2D Systolic Tensor Cores
* **RTL:** [`rtl/systolic_array.sv`](../../rtl/systolic_array.sv)
* **Testbench:** [`tests/test_systolic_array.py`](../../tests/test_systolic_array.py)

---

## 1. Traditional Matrix Multiplication vs. The Systolic Array

### A. The Standard Software Way ($O(N^3)$ Triple Loop)
In standard software (Python, C++), matrix multiplication ($C = A \times W$) computes dot products row-by-column:

$$\begin{pmatrix} C_{00} & C_{01} \\ C_{10} & C_{11} \end{pmatrix} = \begin{pmatrix} a_{00} & a_{01} \\ a_{10} & a_{11} \end{pmatrix} \begin{pmatrix} w_{00} & w_{01} \\ w_{10} & w_{11} \end{pmatrix}$$

$$\begin{aligned}
C_{00} &= a_{00}w_{00} + a_{01}w_{10} \\
C_{01} &= a_{00}w_{01} + a_{01}w_{11} \\
C_{10} &= a_{10}w_{00} + a_{11}w_{10} \\
C_{11} &= a_{10}w_{01} + a_{11}w_{11}
\end{aligned}$$

### B. Traditional CPU/GPU vs. 2D Systolic Array Comparison

| Feature | Traditional CPU (Sequential ALU) | Parallel GPU / SIMD | 2D Systolic Array (TPU-style) |
| :--- | :--- | :--- | :--- |
| **Compute Execution** | 1 MAC per cycle in 1 ALU | Vector of MACs per cycle | **2D Grid of PEs simultaneously** |
| **Data Movement** | Read/Write DRAM every cycle | Shared central register file | **Direct PE-to-PE neighbor wires** |
| **Memory Bandwidth** | $O(N^3)$ loads (repeated re-fetching) | High bandwidth memory (HBM) | **$O(N^2)$ loads** (each byte loaded once) |
| **Energy Consumption** | $>90\%$ wasted on memory transfers | High power on crossbar routing | **Ultra-low energy** (data reuse in mesh) |

---

## 2. Hardware Intuition: 2D Wavefront & Activation Skewing

In a Weight-Stationary Systolic Array, matrix weights $W$ stay locked in their respective PEs:

```
                    [Col 0: sum_in=0]     [Col 1: sum_in=0]
                            │                     │
                            ▼                     ▼
[Row 0: a00, a01] ──► ┌───────────┐         ┌───────────┐
                      │  PE[0][0] ├──► a ──►│  PE[0][1] ├──► (discard)
                      │ (Holds w00)│        │ (Holds w01)│
                      └─────┬─────┘         └─────┬─────┘
                            │ sum                 │ sum
                            ▼                     ▼
[Row 1: a10, a11] ──► ┌───────────┐         ┌───────────┐
                      │  PE[1][0] ├──► a ──►│  PE[1][1] ├──► (discard)
                      │ (Holds w10)│        │ (Holds w11)│
                      └─────┬─────┘         └─────┬─────┘
                            ▼                     ▼
                       C[0] Output           C[1] Output
```

### 🚨 Why Inputs Must Be "Skewed" (Staggered by Clock Cycles)
* If Row 0 and Row 1 activations were injected at the exact same clock cycle $T=1$:
  * $a_{00}$ enters $PE_{00}$ and multiplies with $w_{00}$ $\to$ Correct!
  * But the partial sum from $PE_{00}$ takes **1 clock cycle to travel South** to $PE_{10}$.
  * If $a_{10}$ arrived at $PE_{10}$ at $T=1$, it would accumulate with an **empty/garbage partial sum** before the top result ever arrived!
* **The Fix (Activation Skewing):** Delay Row 1 inputs by **1 clock cycle** using a flip-flop register. In general, **Row $k$ is delayed by $k$ clock cycles**.

```
Row 0 Activation Stream: [ a01 ]  [ a00 ]          (Delay = 0 cycles)
Row 1 Activation Stream: [ a11 ]  [ a10 ]  [ 0 ]   (Delay = 1 cycle via D-FF)
                                     │       │
                                    T=2     T=1
```

### ⏱️ Cycle-by-Cycle Wavefront Walkthrough ($2 \times 2$ Grid)

* **$T=0$ (Setup):** Weights $w_{00}, w_{01}, w_{10}, w_{11}$ loaded into PEs. Accumulators cleared.
* **$T=1$:** 
  * $a_{00}$ enters $PE_{00}$ $\to$ computes $a_{00}w_{00}$.
  * Row 1 feeds `0` (waiting for skew delay).
* **$T=2$:** 
  * $a_{01}$ enters $PE_{00}$. $a_{00}$ forwarded East into $PE_{01}$ $\to$ computes $a_{00}w_{01}$.
  * $a_{10}$ enters $PE_{10}$, receives partial sum ($a_{00}w_{00}$) from North $\to$ computes $\mathbf{C_{00}} = a_{00}w_{00} + a_{10}w_{10}$!
* **$T=3$:** 
  * $a_{01}$ forwarded East into $PE_{01}$.
  * $a_{11}$ enters $PE_{11}$, receives partial sum ($a_{00}w_{01}$) from North $\to$ computes $\mathbf{C_{01}} = a_{00}w_{01} + a_{11}w_{11}$!
  * First column outputs valid $C_{00}$ at bottom pin!

* **Total Latency Formula for $N \times N$ Array:**
  $$T_{\text{total}} = 3N - 2 \text{ clock cycles} \quad (10 \text{ cycles for a } 4 \times 4 \text{ array})$$

---

## 3. SystemVerilog RTL Architecture

```systemverilog
module systolic_array #(
    parameter int ARRAY_SIZE = 4,
    parameter int A_WIDTH    = 8,
    parameter int B_WIDTH    = 8,
    parameter int ACC_WIDTH  = 32
)(
    input  logic clk, rst_n, clr, load_weights,
    input  logic signed [A_WIDTH-1:0]   a_in[ARRAY_SIZE],
    input  logic signed [B_WIDTH-1:0]   w_in[ARRAY_SIZE][ARRAY_SIZE],
    output logic signed [ACC_WIDTH-1:0] c_out[ARRAY_SIZE]
);
    // Skew registers + 2D PE Grid Interconnections
    genvar r, c;
    generate
        for (r = 0; r < ARRAY_SIZE; r++) begin : gen_row
            for (c = 0; c < ARRAY_SIZE; c++) begin : gen_col
                pe #(.A_WIDTH(A_WIDTH), .B_WIDTH(B_WIDTH), .ACC_WIDTH(ACC_WIDTH)) u_pe (
                    .clk(clk), .rst_n(rst_n), .clr(clr), .load_weight(load_weights),
                    .w_in(w_in[r][c]), .a_in(horiz_wires[r][c]),
                    .sum_in(vert_wires[r][c]), .a_out(horiz_wires[r][c+1]),
                    .sum_out(vert_wires[r+1][c])
                );
            end
        end
    endgenerate
endmodule
```

### 📐 Logic Synthesis & Hardware Schematic

![systolic_array Synthesis Schematic](../../schematics/systolic_array.svg)

> [!NOTE]
> **Synthesis & Complexity Analysis:**
> * **Sequential Registers (DFF):** `816 DFFs` (16 PEs $\times$ 48 DFFs = 768 DFFs + 48 DFFs in Skew Delay Pipelines)
> * **Gate Complexity:** $O(K^2 \cdot N^2)$ ($\approx 6,160$ Logic Gates + 816 D-Flip-Flop Cells across 16 MAC Units)
> * **Wavefront Latency:** $T_{\text{total}} = 3N - 2 = 10\text{ Clock Cycles}$ for a $4 \times 4$ Array ($\text{Initiation Interval } II = 1$)
> * **Peak Compute Density:** $16\text{ MACs/cycle}$ ($32\text{ INT8 Operations/cycle}$ @ $850\text{ MHz}$)
> * **Interactive Controls:** Open [`schematics/systolic_array.svg`](../../schematics/systolic_array.svg) in your browser to interactively click any individual PE cell in the 4x4 matrix and expand its internal registers and MAC datapath in-place.

---

## 4. Verification & Wavefront Timing with Cocotb

The complete 2D array is verified cycle-by-cycle against NumPy golden GEMM outputs.

* **Wavefront Timing for $4 \times 4$ Array:**
  * **Cycles 0–3:** Skewed activation vectors stream into the array.
  * **Cycle 4:** First valid result element $C[0][0]$ exits the bottom of Column 0.
  * **Cycle 7–10:** Full $4 \times 4$ matrix accumulation finishes and clears.

To execute the testbench:
```bash
python labs/run_lab.py --lab lab04
```

---

## 5. Review & Engineering Analysis Questions

1. **Wavefront Skew Derivation:** Derive mathematically why Row $k$ requires exactly $k$ flip-flop delay stages for the spatial wavefront to align along the matrix diagonal.
2. **Matrix Tiling in Hardware:** If physical silicon implements a $16 \times 16$ systolic array, how does a hardware DMA controller tile a $1024 \times 1024$ LLM weight projection matrix across the array?
3. **PE Utilization Efficiency:** What percentage of total PEs in an $N \times N$ array are actively performing useful MAC arithmetic during the initial ramp-up and ramp-down phases?
