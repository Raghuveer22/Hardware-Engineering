# 🧪 Lab 03: Weight-Stationary Processing Element (PE)
### Clocked Registers, Stationary Weights & Spatial Dataflow

* **Track:** TPU & 2D Systolic Tensor Cores
* **RTL:** [`rtl/pe.sv`](../../rtl/pe.sv)
* **Testbench:** [`tests/test_pe.py`](../../tests/test_pe.py)

---

## 1. The Starting Point: Traditional Matrix Multiplication on CPUs

Every software engineer learns matrix multiplication ($C = A \times B$) as three nested loops:

```python
# Traditional Matrix Multiplication (O(N^3))
for i in range(M):          # Loop over Rows of A
    for j in range(N):      # Loop over Columns of B
        for k in range(K):  # Dot-product reduction
            C[i][j] += A[i][k] * B[k][j]
```

### 🚨 How Traditional CPUs Execute This (The Von Neumann Bottleneck)

On a standard CPU or single ALU processor:

```
┌─────────────────────────────────────────────────────────────┐
│                    OFF-CHIP MEMORY (DRAM)                   │
└──────────────────────────────┬──────────────────────────────┘
                               │  🚨 100x-200x Energy Penalty per fetch!
                               ▼
                        [ L1/L2 Cache ]
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
       [ Load A[i][k] ]                [ Load B[k][j] ]
               │                               │
               └───────────────┬───────────────┘
                               ▼
                       ┌───────────────┐
                       │  Single ALU   │  ◄── Multiply & Accumulate
                       └───────┬───────┘
                               ▼
                       [ Store C[i][j] ]
```

* **The Problem (Redundant Memory Fetches):** To compute an $N \times N$ matrix, the CPU performs $N^3$ operations. Naively, each element $A[i][k]$ is loaded from memory **$N$ separate times**!
* **The Energy Wall:** 
  * Computing $1 \text{ MAC}$ in silicon costs **$\approx 0.2 \text{ pJ}$ (picojoules)**.
  * Fetching $1 \text{ Byte}$ from DRAM costs **$\approx 100\text{--}200 \text{ pJ}$ ($1,000\times$ more energy!)**.
* **Result:** The CPU spends $>90\%$ of its time and power simply moving numbers back and forth across slow memory buses while the ALU sits idle waiting for data.

---

## 2. The Silicon Solution: The Weight-Stationary Processing Element (PE)

To solve the memory wall, AI accelerators (like Google TPU and NVIDIA Tensor Cores) use **Spatial Dataflow**:
1. **Load Weights Once:** Model weights ($W$) are loaded directly into local flip-flop registers inside the compute cell and **locked in place (stationary)**.
2. **Stream Activations & Pass to Neighbors:** Activations ($A$) enter from the West, multiply with the stationary weight, and are passed to the Eastern neighbor on the next clock tick.
3. **Accumulate Partial Sums:** Partial sums flow vertically from North to South, accumulating results as they travel down the column.

```
                     Activation a_in [7:0] (from West)
                               │
                       [ D-FF Reg (8b) ] ──► a_out (Passes East)
                               │
       Weight w_reg [7:0] ───►[*] (8b x 8b Multiplier)
       (Stationary on-chip)    │  (16b Product)
                               ▼
   Accum in sum_in [31:0] ───►[+] (32b Adder)
   (from North)                │
                       [ D-FF Reg (32b) ] ──► sum_out (Passes South)
```

* **Register Budget inside 1 PE:**
  * $1 \times \text{8-bit}$ stationary weight register (`w_reg`)
  * $1 \times \text{8-bit}$ horizontal activation forwarding register (`a_out`)
  * $1 \times \text{32-bit}$ vertical accumulator register (`sum_out`)
  * **Total:** $48 \text{ D-Flip-Flop registers per PE}$.
* **Sequential Timing (The 1-Clock Delay):**
  * **Cycle 0 (Weight Load):** Assert `load_weight = 1` $\to$ weight latched into `w_reg`.
  * **Cycle 1+ (Compute & Forward):** Apply `a_in` and `sum_in` $\to$ combinational MAC produces product, registered to `a_out` and `sum_out` at the rising clock edge.

---

## 3. SystemVerilog RTL Architecture

```systemverilog
module pe #(
    parameter int A_WIDTH   = 8,
    parameter int B_WIDTH   = 8,
    parameter int ACC_WIDTH = 32
)(
    input  logic clk, rst_n, clr, load_weight,
    input  logic signed [A_WIDTH-1:0]   a_in,
    input  logic signed [B_WIDTH-1:0]   w_in,
    input  logic signed [ACC_WIDTH-1:0] sum_in,
    output logic signed [A_WIDTH-1:0]   a_out,
    output logic signed [ACC_WIDTH-1:0] sum_out
);
    logic signed [B_WIDTH-1:0] w_reg;
    logic signed [ACC_WIDTH-1:0] mac_result;

    mac_unit #(.A_WIDTH(A_WIDTH), .B_WIDTH(B_WIDTH), .ACC_WIDTH(ACC_WIDTH))
        u_mac (.a(a_in), .b(w_reg), .sum_in(sum_in), .sum_out(mac_result));

    // Clocked D-Flip-Flop Output Registers
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            w_reg   <= '0;
            a_out   <= '0;
            sum_out <= '0;
        end else begin
            if (load_weight) w_reg <= w_in;
            a_out   <= a_in;
            sum_out <= clr ? '0 : mac_result;
        end
    end
endmodule
```

### 📐 Logic Synthesis & Hardware Schematic

![pe Synthesis Schematic](../../schematics/pe.svg)

> [!NOTE]
> **Synthesis & Complexity Analysis:**
> * **Sequential Registers (DFF):** `48 DFFs` per PE (`w_reg [7:0]`: 8 DFFs, `a_out [7:0]`: 8 DFFs, `sum_out [31:0]`: 32 DFFs)
> * **Gate Complexity:** $O(N^2 + M)$ ($\approx 385$ Logic Gates + 48 D-Flip-Flop Cells)
> * **Latency & Throughput:** $1\text{ Clock Cycle}$ Latency ($\text{Initiation Interval } II = 1$, $F_{\text{max}} \approx 850\text{ MHz}$)
> * **Spatial Architecture:** Weight-Stationary Dataflow (local register reuse eliminates DRAM weight-fetch traffic)
> * **Interactive Controls:** Open [`schematics/pe.svg`](../../schematics/pe.svg) in your browser to interactively expand/collapse the internal registers (`weight_reg`, `a_reg`, `sum_reg`) and the `u_mac` arithmetic core.

---

## 4. Verification & Testing with Cocotb

The cycle-accurate behavior of the PE is verified over clock steps.

* **Cycle-by-Cycle Execution:**
  * **Cycle 0:** Reset assertion; verify all registers initialize to `0`.
  * **Cycle 1:** Assert `load_weight = 1`, `w_in = 5` $\to$ `w_reg` latches $5$.
  * **Cycle 2:** Apply `a_in = 10`, `sum_in = 0` $\to$ on clock edge, `sum_out = 50`, `a_out = 10`.
  * **Cycle 3:** Apply `a_in = -4`, `sum_in = 50` $\to$ on clock edge, `sum_out = 50 + (-20) = 30`.

To execute the testbench:
```bash
python labs/run_lab.py --lab lab03
```

---

## 5. Review & Engineering Analysis Questions

1. **Dataflow Classification:** Compare Weight-Stationary, Output-Stationary, and Weight-Streaming dataflows in terms of local SRAM buffer bandwidth requirements.
2. **Register Cost vs Frequency:** Why are `a_out` and `sum_out` both registered with D-Flip-Flops instead of passing directly combinational wires between PEs?
3. **Control Signals:** What is the functional distinction between asynchronous reset (`rst_n`) and synchronous accumulator clearing (`clr`)?
