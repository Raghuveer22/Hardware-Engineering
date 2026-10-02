# 🧪 Lab 02: Multiply-Accumulate (MAC) Unit
### The Fundamental Arithmetic Building Block of Tensor Acceleration

* **Track:** Silicon Arithmetic & Math Engines
* **RTL:** [`rtl/mac_unit.sv`](../../rtl/mac_unit.sv)
* **Testbench:** [`labs/test_mac.py`](../test_mac.py)

---

## 1. Educational & Architectural Importance

The Multiply-Accumulate (MAC) operation ($\text{Accumulator} \leftarrow \text{Accumulator} + (A \times B)$) forms the computational backbone of 99% of AI compute (matrix-vector products, 2D convolutions, and Transformer attention projections).

* **Accumulator Bit-Growth Dynamics:** When multiplying two 8-bit values ($127 \times 127 = 16,129$), a 16-bit register would overflow after accumulating only two or three terms.
* **32-Bit Accumulator Headroom Math:** 
  * Each INT8 product takes up to 16 bits.
  * If an LLM reduces a dot-product vector of length $K = 4096$:
    $$\text{Required Bits} = \text{Product Bits} + \lceil \log_2(K) \rceil = 16 + \log_2(4096) = 16 + 12 = 28 \text{ bits}$$
  * A **32-bit accumulator** provides safe headroom to sum over **$65,536$ consecutive INT8 terms** with zero risk of intermediate overflow.

---

## 2. Hardware Intuition: Sign Extension (16b ➔ 32b)

### A. Why We Must Sign-Extend (Replicate MSB)
When adding a 16-bit product into a 32-bit accumulator, the hardware must widen the 16-bit value without changing its mathematical value.

```
Positive Number (+5):
16-bit: [ 0000 0000 0000 0101 ]
32-bit: [ 0000 0000 0000 0000 | 0000 0000 0000 0101 ]  (Padded with 16 zeros)

Negative Number (-5):
16-bit: [ 1111 1111 1111 1011 ]  (MSB = 1)
32-bit: [ 1111 1111 1111 1111 | 1111 1111 1111 1011 ]  (Padded with 16 ones!)
          ▲───────────────────▲
          Replicating the MSB (Sign Bit) preserves the negative value!
```

### 🚨 The Zero-Extension Disaster
* If you accidentally zero-extend a negative number (pad with 16 zeros instead of ones):
  * $-5$ (`16'b1111_1111_1111_1011`) becomes `32'b0000_0000_0000_0000_1111_1111_1111_1011` = **$+65,531_{10}$**!
  * Adding a negative loss or penalty would suddenly add a massive $+65,531$ to the neuron, destroying the neural network output.

### B. Hardware Block Diagram

```
   a [7:0] ──┐
             ├──► [*] (8b x 8b Multiplier)
   b [7:0] ──┘     │
                   ▼ (16b Product)
          [ Sign-Extension Stage ] (Replicate Bit 15 across 16 MSBs)
                   │
                   ▼ (32b Extended Product)
sum_in [31:0] ───► [+] (32b Adder)
                   │
                   ▼
              sum_out [31:0]
```

---

## 3. SystemVerilog RTL Architecture

```systemverilog
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

### 📐 Logic Synthesis & Hardware Schematic

![mac_unit Synthesis Schematic](../../schematics/mac_unit.svg)

> [!NOTE]
> **Synthesis & Complexity Analysis:**
> * **Sequential Registers (DFF):** `0 DFFs` (Fused Combinational MAC Datapath)
> * **Gate Complexity:** $O(N^2 + M)$ ($\approx 310$ Logic Gates: Booth Multiplier, 16b $\to$ 32b Sign Extender, 32-Bit CLA Adder)
> * **Latency & Critical Path:** $0\text{ Clock Cycles}$ ($\approx 3.6\text{ ns}$ Multiplier + Adder Combined Path)
> * **Accumulator Headroom:** 32-bit Accumulator allows up to **$65,536$ consecutive INT8 products** without intermediate overflow.
> * **Interactive Controls:** Open [`schematics/mac_unit.svg`](../../schematics/mac_unit.svg) in your browser to interactively collapse/expand submodules (Multiplier, Sign-Extender, and CLA Adder).

---

## 4. Verification & Testing with Cocotb

The MAC unit is verified against Python golden numerical models.

* **Tested Scenarios:**
  * Zero initialization: `sum_in = 0, a = 12, b = -5` $\to -60$
  * Multi-step chained accumulation: verifying 100 consecutive dot products
  * Deep negative accumulation: $-128 \times 127 = -16256$ accumulated 10 times $\to -162560$

To execute the testbench:
```bash
python labs/run_lab.py --lab lab02
```

---

## 5. Review & Engineering Analysis Questions

1. **Accumulator Sizing:** For an inner-product reduction dimension $K = 4096$ with INT8 inputs, calculate the minimum accumulator bit-width required to guarantee zero overflow under worst-case inputs.
2. **Sign Extension Correctness:** What mathematical error occurs if a negative 16-bit two's complement product is zero-extended into a 32-bit accumulator instead of sign-extended?
3. **Pipelining Considerations:** How does placing a pipeline register between the multiplier and the adder impact maximum clock frequency ($F_{\text{max}}$) versus operational latency?
