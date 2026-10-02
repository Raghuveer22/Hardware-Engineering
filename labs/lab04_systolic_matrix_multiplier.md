# 🧪 Lab 04: 2D Systolic Matrix Multiplier Engine

In this capstone lab, you connect the PEs from Lab 03 into a **2D Systolic Grid (4x4)** to execute full matrix multiplications ($C = A \cdot W$).

You will learn how **Activation Skewing Registers** synchronize the diagonal wavefront, verify the matrix multiplication bit-by-bit against **NumPy**, and watch the live dataflow in the **Browser Visualizer**.

---

## 📚 1. Hardware Theory: The 2D Systolic Wavefront

### Why Skewing Registers Are Essential:
In a 2D systolic array, activations travel **Left $\to$ Right** while partial sums travel **Top $\to$ Bottom**.
To ensure that $A_{i,k}$ meets $W_{k,j}$ at the exact clock cycle when the partial sum for $C_{i,j}$ arrives:
* **Row 0** receives $A_{0,:}$ with **0 cycles delay**.
* **Row 1** receives $A_{1,:}$ delayed by **1 clock cycle**.
* **Row 2** receives $A_{2,:}$ delayed by **2 clock cycles**.
* **Row $r$** receives $A_{r,:}$ delayed by **$r$ clock cycles**.

```
  Row 0 In: [ A00 ][ A01 ][ A02 ] ─────────────► [ PE 0,0 ] ──► [ PE 0,1 ]
  Row 1 In: [ 0   ][ A10 ][ A11 ] ─[ Delay 1 ]─► [ PE 1,0 ] ──► [ PE 1,1 ]
  Row 2 In: [ 0   ][ 0   ][ A20 ] ─[ Delay 2 ]─► [ PE 2,0 ] ──► [ PE 2,1 ]
                                                     │              │
                                                     ▼              ▼
                                                [ Col 0 Out ]  [ Col 1 Out ]
```

---

## 💻 2. SystemVerilog RTL Code (`rtl/systolic_array.sv`)

[`rtl/systolic_array.sv`](../rtl/systolic_array.sv):

```systemverilog
`timescale 1ns/1ps

module systolic_array #(
    parameter int ROWS        = 4,
    parameter int COLS        = 4,
    parameter int DATA_WIDTH  = 8,
    parameter int ACC_WIDTH   = 32
)(
    input  logic                                  clk,
    input  logic                                  rst_n,
    input  logic                                  en,
    input  logic                                  weight_load_en,

    input  logic signed [DATA_WIDTH-1:0]          weights_in     [COLS],
    input  logic signed [DATA_WIDTH-1:0]          activations_in [ROWS],
    input  logic signed [ACC_WIDTH-1:0]           sum_in_top     [COLS],
    output logic signed [ACC_WIDTH-1:0]           sum_out_bot    [COLS],
    output logic signed [DATA_WIDTH-1:0]          activations_out[ROWS]
);

    // 1. Activation Skew Registers
    logic signed [DATA_WIDTH-1:0] act_skewed [ROWS];
    generate
        for (genvar r = 0; r < ROWS; r++) begin : gen_act_skew
            if (r == 0) begin
                assign act_skewed[0] = activations_in[0];
            end else begin
                logic signed [DATA_WIDTH-1:0] delay_pipe [r];
                always_ff @(posedge clk or negedge rst_n) begin
                    if (!rst_n) for (int d=0; d<r; d++) delay_pipe[d] <= '0;
                    else if (en) begin
                        delay_pipe[0] <= activations_in[r];
                        for (int d=1; d<r; d++) delay_pipe[d] <= delay_pipe[d-1];
                    end
                end
                assign act_skewed[r] = delay_pipe[r-1];
            end
        end
    endgenerate

    // 2. 2D Interconnect Grid & PE Instantiations
    logic signed [DATA_WIDTH-1:0] h_act [ROWS][COLS+1];
    logic signed [ACC_WIDTH-1:0]  v_sum [ROWS+1][COLS];
    logic signed [DATA_WIDTH-1:0] v_weight [ROWS+1][COLS];

    generate
        for (genvar r = 0; r < ROWS; r++) begin : gen_pe_rows
            for (genvar c = 0; c < COLS; c++) begin : gen_pe_cols
                pe #(.DATA_WIDTH(DATA_WIDTH), .ACC_WIDTH(ACC_WIDTH)) u_pe (
                    .clk(clk), .rst_n(rst_n), .en(en), .weight_load_en(weight_load_en),
                    .weight_in(v_weight[r][c]), .weight_out(v_weight[r+1][c]),
                    .a_in(h_act[r][c]),         .a_out(h_act[r][c+1]),
                    .sum_in(v_sum[r][c]),       .sum_out(v_sum[r+1][c])
                );
            end
        end
    endgenerate

endmodule
```

---

## 🧪 3. Python Verification vs. NumPy Golden Model (`tests/test_systolic_array.py`)

[`tests/test_systolic_array.py`](../tests/test_systolic_array.py):

```python
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import numpy as np

@cocotb.test()
async def test_systolic_gemm_4x4(dut):
    """Test 4x4 Matrix Multiplication C = A @ W against NumPy"""
    A = np.random.randint(-20, 20, size=(4, 4), dtype=np.int32)
    W = np.random.randint(-20, 20, size=(4, 4), dtype=np.int32)
    C_golden = A @ W

    # 1. Load weights
    dut.weight_load_en.value = 1
    for r in range(3, -1, -1):
        for c in range(4): dut.weights_in[c].value = int(W[r, c])
        await RisingEdge(dut.clk)
    dut.weight_load_en.value = 0

    # 2. Stream Activations & Harvest Output
    dut.en.value = 1
    # ... Stream rows of A and collect from sum_out_bot[c] ...
    # Verify C_hw == C_golden
```

### Run the Test:
```bash
python3 labs/run_lab.py --lab lab04
```

---

## 🖥️ 4. Watch Live in the Interactive Visualizer

Launch the browser visualizer:
```bash
python3 visualizer/serve.py
```
* Open [http://localhost:8080](http://localhost:8080)
* Watch **Column 0 through Column 3 bottom pins** light up in green as the matrix result elements stream out cycle-by-cycle!

---

## 🎯 Key Content & Interview Takeaways
1. **Systolic Throughput:** Once the pipeline fills, a $4 \times 4$ array computes **16 MAC operations (32 FLOPS/IOPS) per clock cycle**.
2. **Matrix Tiling for Large LLMs:** A $4 \times 4$ physical array can process arbitrarily large matrices ($1024 \times 1024$ or 1M context) by chopping them into $4 \times 4$ tiles in software.
