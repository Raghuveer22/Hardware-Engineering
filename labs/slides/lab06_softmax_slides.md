# 🧪 Lab 06: Hardware Softmax & FlashAttention
### Preventing Fixed-Point Overflow via Safe Softmax & Online Normalization

* **Track:** Non-Linear Transformer SFUs
* **RTL:** `rtl/softmax.sv`
* **Testbench:** `labs/test_softmax.py`

---

## 🪝 1. The Hook: Why Naive Softmax Destroys Silicon

* **The Problem:** In Self-Attention, raw logits $x_i$ can easily reach $+50$ or $+100$.
* **The Catastrophe:** Computing $e^{50} \approx 5.18 \times 10^{21}$ overflows even a 64-bit integer ($2^{64} \approx 1.84 \times 10^{19}$). In silicon, values wrap around to 0, producing NaN probabilities and total model crash!
* **The Silicon Fix (Safe Softmax):** Subtract row-maximum $M = \max(x_i)$ before computing exponentials:
  $$\Delta_i = x_i - M \le 0 \implies e^{\Delta_i} \in (0.0, 1.0]$$
  Exponentials never overflow and fit cleanly into **Q0.8 fixed-point** registers!

---

## 💡 2. Hardware Intuition & FlashAttention Online Tiling

* **Hardware Datapath Pipeline:**
  $$\text{Inputs } [x_0, x_1, x_2, x_3] \longrightarrow \text{Max-Finder } (M) \longrightarrow \Delta_i = x_i - M \longrightarrow \text{Exp LUT} \longrightarrow \text{Adder Tree} \longrightarrow \text{Divider}$$
* **FlashAttention (Tri Dao et al.):**
  * Traditional PyTorch: 3 full High-Bandwidth Memory (HBM) read/write passes.
  * **Online Softmax:** Fuses max-subtraction and sum accumulation into local SRAM tiles using dynamic rescaling:
    $$S_{\text{new}} = S_{\text{old}} \cdot e^{M_{\text{old}} - M_{\text{new}}} + e^{x_i - M_{\text{new}}}$$

---

## 💻 3. SystemVerilog RTL Walkthrough

```verilog
module softmax #(
    parameter int VECTOR_SIZE = 4,
    parameter int IN_WIDTH    = 8,
    parameter int OUT_WIDTH   = 8
)(
    input  logic signed [IN_WIDTH-1:0]  logits_in[VECTOR_SIZE],
    output logic        [OUT_WIDTH-1:0] probs_out[VECTOR_SIZE]
);
    // 1. Find Max Logit
    logic signed [IN_WIDTH-1:0] max_val;
    // 2. Compute delta_i = logits_in[i] - max_val (<= 0)
    // 3. Exponential Lookup Table (Q0.8 fixed-point)
    // 4. Sum Exponentials & Fixed-Point Normalization
endmodule
```

---

## 🧪 4. Cocotb Verification

* **Golden Reference:** PyTorch `torch.nn.functional.softmax(logits, dim=-1) * 255`.
* **Corner Cases Tested:**
  * Equal logits ($[10, 10, 10, 10] \to [64, 64, 64, 64]$)
  * Extreme dominance ($[100, 0, 0, 0] \to [255, 0, 0, 0]$)
  * Deep negative logits ($[-50, -40, -30, -20]$)
  * Probability sum invariant: $\sum P_i \approx 255$
* **Run Testbench:**
  ```bash
  python labs/run_lab.py --lab lab06
  ```

---

## 💬 5. Comment Challenge

Drop your answers in the YouTube comments! 👇

1. Why do we subtract $\max(x)$ before computing the exponentials in Softmax?
2. What range do the values $e^{x_i - M}$ always land in, and why does that matter for hardware?
