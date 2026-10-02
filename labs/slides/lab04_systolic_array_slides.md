# 🧪 Lab 04: 2D Systolic Matrix Multiplier Array
### 2D Wavefront Pipeline, Activation Skewing & O(3N) Speedup

* **Track:** TPU & 2D Systolic Tensor Cores
* **RTL:** `rtl/systolic_array.sv`
* **Testbench:** `tests/test_systolic_array.py`

---

## 🪝 1. The Hook: Beating $O(N^3)$ CPU Complexity

* **The Problem:** Multiplying two $N \times N$ matrices on a single CPU core takes $O(N^3)$ operations. For large LLM matrices ($N = 4096$), that is **68 Billion operations** on a slow sequential bus.
* **The Breakthrough:** H.T. Kung's **2D Systolic Array** arranges PEs in a grid. Activations stream from the West, partial sums flow from the North, and results emerge from the South in just **$O(3N)$ clock cycles**!
* **Scale in Silicon:** Google TPU v1 through v5 and NVIDIA Tensor Cores are all direct evolutions of this exact 2D systolic mesh.

---

## 💡 2. Hardware Intuition & 2D Diagonal Wavefront

* **Why Skewing is Required:** PE[0][0] finishes its first dot-product multiplication at Cycle 1, while PE[1][1] cannot begin until Cycle 2.
* **Built-in Skewing FIFO Registers:**
  * Row 0: Delay $= 0$ cycles
  * Row 1: Delay $= 1$ cycle (`[D-FF]`)
  * Row 2: Delay $= 2$ cycles (`[D-FF] ──► [D-FF]`)
  * Row 3: Delay $= 3$ cycles (`[D-FF] ──► [D-FF] ──► [D-FF]`)
* **Total Latency:** For an $N \times N$ matrix ($4 \times 4$):
  $$T_{\text{total}} = 3N - 2 = 10\text{ clock cycles to stream entire matrix!}$$

---

## 💻 3. SystemVerilog RTL Architecture

```verilog
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
    // Skew registers + 4x4 PE 2D Grid Interconnections
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

---

## 🧪 4. Cocotb Verification & Wavefront Timing

* **Cycle Execution Pipeline ($4 \times 4$ Matrix):**
  * **Cycles 0–3:** Skewed activation rows enter array
  * **Cycle 4:** First valid result element $C[0][0]$ exits bottom of Column 0
  * **Cycle 7:** Entire $4 \times 4$ matrix multiplication complete
* **Automated Verification:** Testbench generates 100 random $4 \times 4$ integer matrices, computes NumPy reference $C = A \cdot W$, and asserts exact cycle-by-cycle equality on DUT output pins.
* **Run Testbench:**
  ```bash
  python labs/run_lab.py --lab lab04
  ```

---

## 💬 5. Comment Challenge

Drop your answers in the YouTube comments! 👇

1. For a $4 \times 4$ systolic array, how many clock cycles pass before the *first* result exits the bottom?
2. Why does Row 1 need a 1-cycle delay but Row 3 needs 3 cycles?
