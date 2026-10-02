# 🧪 Lab 08: Hardware Exponential SFU ($2^x$ & $e^x$)
### Base-2 Decomposition for Softmax, SwiGLU, and SiLU in Silicon

* **Track:** Non-Linear Transformer SFUs
* **RTL:** `rtl/exp2_sfu.sv`
* **Testbench:** `labs/test_exp2_sfu.py`

---

## 🪝 1. The Hook: Accelerating 60% of LLM FLOPs

* **The Problem:** Modern LLMs spend over 60% of their compute evaluating Feed-Forward Networks using **SwiGLU & SiLU**:
  $$\text{SiLU}(x) = \frac{x}{1 + e^{-x}}, \quad \text{SwiGLU}(x) = (\text{SiLU}(x W) \odot x V) W_2$$
* **The Silicon Barrier:** Calculating $e^x$ directly with Taylor series in silicon requires dozens of high-latency multiplier stages.
* **The Breakthrough:** Transform base-$e$ to base-$2$: $e^x = 2^{x \cdot \log_2(e)}$.
  Integer parts ($2^I$) become **free bitshifts**, and fractional parts ($2^F$) evaluate via a tiny **16-entry seed ROM**!

---

## 💡 2. Hardware Intuition: Base-2 Decomposition

$$u = x \cdot \log_2(e) = I + F \implies 2^u = 2^I \cdot 2^F$$

* **Integer Part $I$:** Evaluated with a 0-cycle barrel shifter.
* **Fractional Part $F \in [0, 1)$:** Looked up in a small 16-entry ROM table.
* **Datapath:**
  $$\text{Input } x \longrightarrow [\times 1.4427] \longrightarrow u = I + F \longrightarrow [2^I \text{ Shifter}] \times [2^F \text{ ROM}] \longrightarrow e^x \text{ (Q8.8)}$$
* **Hardware Speedup:** High-precision exponential in **1 to 2 clock cycles** instead of a 30-cycle software loop!

---

## 💻 3. SystemVerilog RTL Walkthrough

```verilog
module exp2_sfu #(
    parameter int IN_WIDTH  = 8,   // Signed Q4.4 input
    parameter int OUT_WIDTH = 16   // Unsigned Q8.8 output
)(
    input  logic signed [IN_WIDTH-1:0]  x_in,
    input  logic                        mode_e,     // 1 = e^x, 0 = 2^x
    output logic        [OUT_WIDTH-1:0] y_out,
    output logic                        overflow
);
    // 1. Optional log2(e) scaling stage for mode_e
    // 2. Integer bitshift (2^I) & 16-entry fractional ROM (2^F)
    // 3. Multiplier combiner + Q8.8 saturation clamp
endmodule
```

---

## 🧪 4. Cocotb Verification

* **Golden Reference:** NumPy `2**x` and `np.exp(x)` floating-point models converted to Q8.8.
* **Key Tests:**
  * Base-$2$ mode: $x = 0.0 \implies 256$, $x = 1.0 \implies 512$, $x = -1.0 \implies 128$
  * Base-$e$ mode: $x = 1.0 \implies e^{1.0} \approx 2.718 \implies 696$
  * Negative exponents: $x = -4.0 \implies e^{-4} \approx 0.018 \implies 5$
* **Run Testbench:**
  ```bash
  python labs/run_lab.py --lab lab08
  ```

---

## 💬 5. Comment Challenge

Drop your answers in the YouTube comments! 👇

1. How does the trick $e^x = 2^{x \cdot \log_2(e)}$ turn a hard exponential into almost-free hardware?
2. Which part of $2^I \cdot 2^F$ is a free bit-shift, and which part needs a lookup table?
