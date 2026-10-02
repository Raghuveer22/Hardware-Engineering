# 🧪 Lab 03: Weight-Stationary Processing Element (PE)
### Clocked Registers, Stationary Weights & Pipelined Activation Forwarding

* **Track:** TPU & 2D Systolic Tensor Cores
* **RTL:** `rtl/pe.sv`
* **Testbench:** `tests/test_pe.py`

---

## 🪝 1. The Hook: The $200\times$ DRAM Energy Wall

* **The Problem:** Moving a single byte of data from off-chip DRAM to a CPU/GPU core takes **$\approx 200\times$ more energy** than performing the actual multiplication!
* **The CPU Flaw:** A standard processor constantly re-fetches the same weights over and over from slow memory caches.
* **The Silicon Fix:** **Weight-Stationary Dataflow.** Load weights into on-chip PE registers *once*, lock them in place, and stream activations across the silicon mesh with zero redundant memory fetches.

---

## 💡 2. Hardware Intuition & Clocked Pipeline

```
                     Activation a_in [7:0]
                              │
                      [ D-FF Reg (8b) ] ──► a_out (Passes East)
                              │
      Weight w_reg [7:0] ───►[*] (8b x 8b)
                              │  (16b Product)
                              ▼
  Accum in sum_in [31:0] ──► [+]
                              │
                      [ D-FF Reg (32b) ] ──► sum_out (Passes South)
```

* **Registers inside 1 PE:** 8-bit weight register + 8-bit activation forward register + 32-bit accumulation register = **48 D-Flip-Flops total**.
* **Cycle Behavior (Sequential):**
  * Cycle 0: Assert `load_weight = 1` $\to$ weight locked into `w_reg`.
  * Cycle 1+: Feed `a_in` and `sum_in` $\to$ computes dot product, forwards outputs on next rising clock edge.

---

## 💻 3. SystemVerilog RTL Walkthrough

```verilog
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
    // MAC combinational math
    logic signed [ACC_WIDTH-1:0] mac_result;
    mac_unit #(.A_WIDTH(A_WIDTH), .B_WIDTH(B_WIDTH), .ACC_WIDTH(ACC_WIDTH))
        u_mac (.a(a_in), .b(w_reg), .sum_in(sum_in), .sum_out(mac_result));

    // Clocked D-Flip-Flop Output Registers
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            w_reg <= '0; a_out <= '0; sum_out <= '0;
        end else begin
            if (load_weight) w_reg <= w_in;
            a_out   <= a_in;
            sum_out <= clr ? '0 : mac_result;
        end
    end
endmodule
```

---

## 🧪 4. Cocotb Verification & Cycle Waveforms

* **Cycle-by-Cycle Execution:**
  * **T=0:** Reset low, verify all registers initialize to `0`.
  * **T=1:** Set `w_in = 5`, `load_weight = 1`, pulse clock $\to$ `w_reg` becomes $5$.
  * **T=2:** Set `a_in = 10`, `sum_in = 0`, pulse clock $\to$ `sum_out = 50`, `a_out = 10`.
  * **T=3:** Set `a_in = -4`, `sum_in = 50`, pulse clock $\to$ `sum_out = 50 + (-20) = 30`.
* **Run Testbench:**
  ```bash
  python labs/run_lab.py --lab lab03
  ```

---

## 💬 5. Comment Challenge

Drop your answers in the YouTube comments! 👇

1. Why is "weight-stationary" dataflow more energy-efficient than re-fetching weights every cycle?
2. How many D-flip-flops are inside one PE, and what is each one used for?
