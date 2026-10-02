# 🧪 Lab 02: Multiply-Accumulate (MAC) Unit
### The Fundamental Compute Atom of Modern AI Tensor Engines

* **Track:** Silicon Arithmetic & Math Engines
* **RTL:** `rtl/mac_unit.sv`
* **Testbench:** `labs/test_mac.py`

---

## 🪝 1. The Hook: The Single Most Executed Operation on Earth

* **The Scale:** A single 70B parameter LLM inference run executes **hundreds of trillions** of Multiply-Accumulate operations:
  $$\text{Accumulator} = \text{Accumulator} + (A \times B)$$
* **The Silicon Disaster (Accumulator Overflow):**
  * If the accumulator is only 16 bits, summing 10 consecutive products of $127 \times 127 \approx 16129$ overflows $161,290 > 32767$, wrapping to garbage!
* **The Solution:** Expanding the accumulator to **32 bits** provides enough headroom to sum over **$65,000$ consecutive INT8 products** without a single overflow!

---

## 💡 2. Hardware Intuition & Sign Extension

$$\text{Bit-Growth Rule: } \text{sum\_out} = \text{sum\_in} + \text{sign\_extend}_{32}(A_{8\text{b}} \times B_{8\text{b}})$$

* **16-bit Product $\to$ 32-bit Sign Extension:**
  `{{16{prod[15]}}, prod}` ensures negative numbers preserve their mathematical value when added into the 32-bit register.
* **Latency & Timing:** Combinational path: $t_{\text{mult}} + t_{\text{add32}}$. Purely combinational in this module; register slices are introduced inside the Processing Element (Lab 03).

---

## 💻 3. SystemVerilog RTL Walkthrough

```verilog
module mac_unit #(
    parameter int A_WIDTH   = 8,
    parameter int B_WIDTH   = 8,
    parameter int ACC_WIDTH = 32
)(
    input  logic signed [A_WIDTH-1:0]   a,
    input  logic signed [B_WIDTH-1:0]   b,
    input  logic signed [ACC_WIDTH-1:0] sum_in,
    output logic signed [ACC_WIDTH-1:0] sum_out
);
    localparam int PROD_WIDTH = A_WIDTH + B_WIDTH;
    logic signed [PROD_WIDTH-1:0] mult_product;
    logic signed [ACC_WIDTH-1:0]  mult_product_ext;

    assign mult_product     = a * b;
    assign mult_product_ext = {{(ACC_WIDTH-PROD_WIDTH){mult_product[PROD_WIDTH-1]}}, mult_product};
    assign sum_out          = sum_in + mult_product_ext;
endmodule
```

---

## 🧪 4. Cocotb Verification

* **Golden Reference:** Python `sum_in + (a * b)`.
* **Tested Accumulation Scenarios:**
  * Zero initialization: `sum_in = 0, a = 12, b = -5` $\to -60$
  * Multi-step chained accumulation: verifying 100 random dot products
  * Deep negative accumulation: $-128 \times 127 = -16256$ added 10 times $\to -162560$
* **Run Testbench:**
  ```bash
  python labs/run_lab.py --lab lab02
  ```

---

## 💬 5. Comment Challenge

Drop your answers in the YouTube comments! 👇

1. Why does the MAC use a **32-bit** accumulator even though its inputs are only 8-bit?
2. What would go wrong if we just zero-padded a negative 16-bit product instead of sign-extending it?
