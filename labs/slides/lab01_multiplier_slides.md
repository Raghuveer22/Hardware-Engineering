# 🧪 Lab 01: Parameterized Signed Multiplier (INT8)
### Wallace Trees, Two's Complement Sign Extensions & Bit-Growth

* **Track:** Silicon Arithmetic & Math Engines
* **RTL:** `rtl/multiplier_int8.sv`
* **Testbench:** `labs/test_multiplier.py`

---

## 🪝 1. The Hook: Why Multipliers Dominate Silicon Area

* **The Problem:** 99% of modern Deep Learning operations are Matrix Multiplications ($Y = W \cdot X$).
* **The Silicon Reality:** While an adder scales linearly $O(N)$, a multiplier scales quadratically $O(N^2)$ in logic gates ($\approx 456$ gates for 8-bit).
* **The Disaster:** Multiplying two 8-bit numbers produces a 16-bit product. Truncating prematurely causes catastrophic precision loss; over-allocating bits wastes millions of transistors!

---

## 💡 2. Hardware Intuition & Bit Growth

$$\text{Range: } [-128 \times +127 = -16256] \dots [-128 \times -128 = +16384]$$

* **Required Output Width:** $W_{\text{out}} = W_A + W_B = 8 + 8 = 16\text{ bits}$.
* **Sign Extension:** Must perform signed arithmetic: `signed'(a) * signed'(b)` to avoid treating negative two's complement values as large unsigned numbers (e.g., $-1$ becoming $255$).
* **Timing & Cycles:** Single combinational stage ($0$ clock cycles) or pipelined into DSP blocks on FPGAs.

---

## 💻 3. SystemVerilog RTL Walkthrough

```verilog
module multiplier_int8 #(
    parameter int A_WIDTH = 8,
    parameter int B_WIDTH = 8,
    localparam int PROD_WIDTH = A_WIDTH + B_WIDTH
)(
    input  logic signed [A_WIDTH-1:0]    a,
    input  logic signed [B_WIDTH-1:0]    b,
    output logic signed [PROD_WIDTH-1:0] product
);
    // Explicit signed multiplication datapath
    assign product = a * b;
endmodule
```

* Synthesizes directly to standard multiplier trees or dedicated DSP slices.

---

## 🧪 4. Cocotb Verification

* **Golden Reference:** Python `a * b` signed model.
* **Key Corner Cases Verified:**
  * Zero multiplication: $0 \times 127 = 0$
  * Maximum negative product: $-128 \times +127 = -16256$
  * Asymmetric two's complement boundary: $-128 \times -128 = +16384$
  * Identity scaling: $-45 \times 1 = -45$
* **Run Testbench:**
  ```bash
  python labs/run_lab.py --lab lab01
  ```

---

## 💬 5. Comment Challenge

Drop your answers in the YouTube comments! 👇

1. Why does multiplying two 8-bit numbers need a **16-bit** result?
2. What's the one special product that *doesn't* fit in 15 bits and why? (Hint: $-128 \times -128$)
