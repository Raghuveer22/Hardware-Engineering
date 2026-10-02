# AI Hardware Tensor Engine & Pre-Silicon Emulation Platform

**🪝 YouTube Hook:** *"Ever wondered how chips like Google's TPU or NVIDIA's GPUs actually process AI models? Today, we're building a complete AI hardware accelerator from scratch, taking you from software algorithms down to silicon gates!"*


A 100% free, open-source hardware/software co-design & emulation environment for AI tensor compute engines and LLM Transformer acceleration.

---

## 🌟 Why This Project Matters (Industry Context)

In modern AI chips (Google TPU, NVIDIA Tensor Core, AWS Inferentia, Meta MTIA), tape-outs cost **$50M–$100M+ per chip**. Companies cannot afford silicon bugs or slow software integration. 

This repository demonstrates the complete **Pre-Silicon HW/SW Co-Design Pipeline**: verifying custom AI hardware architectures against real machine learning models (PyTorch/NumPy) and running high-speed cycle-accurate C++ emulators before fabrication.

```
 [ PyTorch / LLM Layer ] ──► [ Python Cocotb Golden Verification ]
                                            │
                                            ▼
 [ Virtual C++ Platform ] ──► [ Synthesizable SystemVerilog RTL ]
 (High-Speed Emulation)       (Weight-Stationary Systolic Array)
                                            │
                                            ▼
                               [ Interactive Browser Visualizer ]
                               (Live 2D Wavefront & Output Pins)
```

---

## 🧠 Deep-Dive: Accelerating LLM Transformers & The 1M Context Problem

### 1. The $O(N^2)$ Memory Bottleneck in Self-Attention
In modern LLMs (LLaMA, GPT-4, Gemini), 95% of inference time is spent computing Self-Attention:
$$\text{Attention}(Q, K, V) = \text{Softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V$$

For large context windows (e.g. **1 Million Tokens**):
* The attention matrix $Q K^T$ reaches **$10^{12}$ elements (1 Trillion numbers)**.
* Storing this intermediate matrix in off-chip DRAM takes **1 to 2 Terabytes of memory** for a single attention head.
* **Why CPUs Fail:** A standard sequential CPU spends 90% of its energy simply moving numbers back and forth between slow DRAM and CPU caches.

### 2. How Custom Hardware Solves This (Tiling & FlashAttention)
* **Weight-Stationary Dataflow:** Model weights ($W_Q, W_K, W_V$) remain locked in local Processing Element (PE) registers inside fast on-chip SRAM. Tokens stream through with zero redundant memory re-fetches.
* **Hardware Matrix Tiling:** Physical chips don't build 1-million-wide systolic arrays. Instead, a parameterized array (e.g., $4 \times 4$, $16 \times 16$, or $128 \times 128$) processes matrices chunk-by-chunk (**tiles**), accumulating results in local SRAM buffers.
* **FlashAttention (Online Softmax):** Fuses softmax scaling directly into the hardware accumulation loop, computing attention without ever materializing the massive intermediate matrix to DRAM.
* **Square Root Scaling ($1/\sqrt{d_k}$):** Keeps dot-product variance normalized to $1.0$, preventing Softmax gradients from vanishing during training and inference.

---

## 🔬 Hands-On AI Hardware Curriculum (Labs 00 - 08)

| Lab | Module | SystemVerilog RTL | Cocotb Verification | Guide | Gate Complexity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Lab 00** | Parameterized Signed Adder | [`rtl/adder.sv`](rtl/adder.sv) | [`labs/test_adder.py`](labs/test_adder.py) | [Lab 00 Guide](labs/slides/lab00_adder_slides.md) | **$O(N)$ Linear** (~42 gates) |
| **Lab 01** | Signed Multiplier (INT8) | [`rtl/multiplier_int8.sv`](rtl/multiplier_int8.sv) | [`labs/test_multiplier.py`](labs/test_multiplier.py) | [Lab 01 Guide](labs/slides/lab01_multiplier_slides.md) | **$O(N^2)$ Quadratic** (~456 gates) |
| **Lab 02** | Multiply-Accumulate (MAC) | [`rtl/mac_unit.sv`](rtl/mac_unit.sv) | [`labs/test_mac.py`](labs/test_mac.py) | [Lab 02 Guide](labs/slides/lab02_mac_unit_slides.md) | Sign-Extension (16b ➔ 32b) |
| **Lab 03** | Processing Element (PE) | [`rtl/pe.sv`](rtl/pe.sv) | [`tests/test_pe.py`](tests/test_pe.py) | [Lab 03 Guide](labs/slides/lab03_processing_element_slides.md) | 48 D-Flip-Flop Registers |
| **Lab 04** | 2D Systolic Matrix Array | [`rtl/systolic_array.sv`](rtl/systolic_array.sv) | [`tests/test_systolic_array.py`](tests/test_systolic_array.py) | [Lab 04 Guide](labs/slides/lab04_systolic_array_slides.md) | 4x4 Grid (816 Registers) |
| **Lab 05** | Square Root Unit | [`rtl/sqrt.sv`](rtl/sqrt.sv) | [`labs/test_sqrt.py`](labs/test_sqrt.py) | [Lab 05 Guide](labs/slides/lab05_sqrt_slides.md) | Attention Scaling ($1/\sqrt{d_k}$) |
| **Lab 06** | Safe Softmax Engine | [`rtl/softmax.sv`](rtl/softmax.sv) | [`labs/test_softmax.py`](labs/test_softmax.py) | [Lab 06 Guide](labs/slides/lab06_softmax_slides.md) | FlashAttention & LUT Exponentials |
| **Lab 07** | Reciprocal Sqrt (`rsqrt`) | [`rtl/rsqrt.sv`](rtl/rsqrt.sv) | [`labs/test_rsqrt.py`](labs/test_rsqrt.py) | [Lab 07 Guide](labs/slides/lab07_rsqrt_slides.md) | RMSNorm & LayerNorm SFU |
| **Lab 08** | Exponential SFU ($2^x / e^x$) | [`rtl/exp2_sfu.sv`](rtl/exp2_sfu.sv) | [`labs/test_exp2_sfu.py`](labs/test_exp2_sfu.py) | [Lab 08 Guide](labs/slides/lab08_exponential_sfu_slides.md) | Base-2 Scaler for SwiGLU / SiLU |

---

## 📂 Source Code vs. Auto-Generated Files

### 🟢 Source Code Files (Read and Edit These)

| Path | Language | Purpose |
| :--- | :--- | :--- |
| [`rtl/adder.sv`](rtl/adder.sv) | SystemVerilog | Parameterized Signed Adder with Saturation arithmetic |
| [`rtl/multiplier_int8.sv`](rtl/multiplier_int8.sv) | SystemVerilog | Signed 8-bit multiplier generating 16-bit product |
| [`rtl/mac_unit.sv`](rtl/mac_unit.sv) | SystemVerilog | Combinational Multiply-Accumulate unit (`sum_out = sum_in + a*b`) |
| [`rtl/pe.sv`](rtl/pe.sv) | SystemVerilog | Single Weight-Stationary Processing Element cell with registers |
| [`rtl/systolic_array.sv`](rtl/systolic_array.sv) | SystemVerilog | Full 2D Grid of PEs with built-in activation skewing registers |
| [`rtl/sqrt.sv`](rtl/sqrt.sv) | SystemVerilog | Digit-by-digit hardware square root unit |
| [`rtl/softmax.sv`](rtl/softmax.sv) | SystemVerilog | Safe Softmax unit with max-subtraction and exp LUT |
| [`labs/run_lab.py`](labs/run_lab.py) | Python | Master Cocotb test runner for all labs (00 - 08) |
| [`synthesis/synthesize.py`](synthesis/synthesize.py) | Python | Centralized Yosys logic synthesis & schematic generator |
| [`visualizer/index.html`](visualizer/index.html) | HTML/JS | Interactive 2D hardware visualizer with live matrix inputs |
| [`schematics/index.html`](schematics/index.html) | HTML/JS | Interactive collapsible gate-level schematic explorer |

---

## 🚀 How to Run

### 1. Run All Lab Testbenches (Labs 00 - 08)
```bash
source .venv/bin/activate
python labs/run_lab.py --lab all
```

### 2. Synthesize All Hardware Modules & Generate Interactive Schematics
```bash
python3 synthesis/synthesize.py --top all
```

### 3. Launch Interactive Hardware Visualizer & Schematics
```bash
# 2D Systolic Array Compute Wavefront:
python3 visualizer/serve.py

# Interactive Schematics Explorer:
open schematics/index.html
```

---

## 🎯 Key Interview Talking Points

* **Hardware/Software Co-Design:** *"We used Python/Cocotb with NumPy to verify mathematical correctness at the functional level, and Verilator/C++ to create a high-speed pre-silicon cycle emulator for running software drivers."*
* **$O(N)$ vs $O(N^2)$ Arithmetic Complexity:** *"Adders require linear $O(N)$ gates (~42 gates for INT8), while multipliers require quadratic $O(N^2)$ gates (~456 gates). Quantizing from INT16 to INT8 reduces multiplier silicon area by $4\times$, which is why AI chips heavily leverage quantization."*
* **Attention Scaling:** *"Dot products have variance scaling with embedding dimension $d_k$. Dividing by $\sqrt{d_k}$ in hardware normalizes variance back to $1.0$, preventing Softmax gradients from vanishing."*
* **FlashAttention / Safe Softmax:** *"Softmax in silicon subtracts the row maximum to avoid exponential overflow, keeping fixed-point representations strictly bounded within $(0, 1]$."*
