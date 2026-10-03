# AI Hardware Tensor Engine & Pre-Silicon Emulation Platform

An open-source hardware/software co-design & emulation environment for AI tensor compute engines, systolic arrays, and LLM Transformer acceleration from mathematical algorithms down to synthesizable silicon gates.

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

## 🔬 Hands-On AI Hardware Curriculum (Labs 00-Prep - 08)

| Lab | Module | SystemVerilog RTL | Cocotb Verification | Guide | Video Animation | Gate Complexity |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Lab 00-Prep** | Hardware Thinking Primer | *Conceptual & Q-Format* | *Cocotb Setup* | [Lab 00-Prep Guide](labs/slides/lab00_prep_hardware_thinking_primer.md) | [🎬 Video](media/videos/scene_lab00_prep/720p30/Lab00PrepPrimer.mp4) | Software vs. Silicon Mindset |
| **Lab 00** | Parameterized Signed Adder | [`rtl/adder.sv`](rtl/adder.sv) | [`labs/test_adder.py`](labs/test_adder.py) | [Lab 00 Guide](labs/slides/lab00_adder_slides.md) | [🎬 Video](media/videos/scene_lab00_saturation/720p30/Lab00SaturationIntro.mp4) | **$O(N)$ Linear** (~42 gates) |
| **Lab 01** | Signed Multiplier (INT8) | [`rtl/multiplier_int8.sv`](rtl/multiplier_int8.sv) | [`labs/test_multiplier.py`](labs/test_multiplier.py) | [Lab 01 Guide](labs/slides/lab01_multiplier_slides.md) | [🎬 Video](media/videos/scene_lab01_multiplier/720p30/Lab01Multiplier.mp4) | **$O(N^2)$ Quadratic** (~456 gates) |
| **Lab 02** | Multiply-Accumulate (MAC) | [`rtl/mac_unit.sv`](rtl/mac_unit.sv) | [`labs/test_mac.py`](labs/test_mac.py) | [Lab 02 Guide](labs/slides/lab02_mac_unit_slides.md) | [🎬 Video](media/videos/scene_lab02_mac_unit/720p30/Lab02MACUnit.mp4) | Sign-Extension (16b ➔ 32b) |
| **Lab 03** | Processing Element (PE) | [`rtl/pe.sv`](rtl/pe.sv) | [`tests/test_pe.py`](tests/test_pe.py) | [Lab 03 Guide](labs/slides/lab03_processing_element_slides.md) | [🎬 Video](media/videos/scene_lab03_pe/720p30/Lab03ProcessingElement.mp4) | 48 D-Flip-Flop Registers |
| **Lab 04** | 2D Systolic Matrix Array | [`rtl/systolic_array.sv`](rtl/systolic_array.sv) | [`tests/test_systolic_array.py`](tests/test_systolic_array.py) | [Lab 04 Guide](labs/slides/lab04_systolic_array_slides.md) | [🎬 Video](media/videos/scene_lab04_systolic_array/720p30/Lab04SystolicArray.mp4) | 4x4 Grid (816 Registers) |
| **Lab 05** | Square Root Unit | [`rtl/sqrt.sv`](rtl/sqrt.sv) | [`labs/test_sqrt.py`](labs/test_sqrt.py) | [Lab 05 Guide](labs/slides/lab05_sqrt_slides.md) | [🎬 Video](media/videos/scene_lab05_sqrt/720p30/Lab05SquareRoot.mp4) | Attention Scaling ($1/\sqrt{d_k}$) |
| **Lab 06** | Safe Softmax Engine | [`rtl/softmax.sv`](rtl/softmax.sv) | [`labs/test_softmax.py`](labs/test_softmax.py) | [Lab 06 Guide](labs/slides/lab06_softmax_slides.md) | [🎬 Video](media/videos/scene_lab06_softmax/720p30/Lab06Softmax.mp4) | FlashAttention & LUT Exponentials |
| **Lab 07** | Reciprocal Sqrt (`rsqrt`) | [`rtl/rsqrt.sv`](rtl/rsqrt.sv) | [`labs/test_rsqrt.py`](labs/test_rsqrt.py) | [Lab 07 Guide](labs/slides/lab07_rsqrt_slides.md) | [🎬 Video](media/videos/scene_lab07_rsqrt/720p30/Lab07RSQRT.mp4) | RMSNorm & LayerNorm SFU |
| **Lab 08** | Exponential SFU ($2^x / e^x$) | [`rtl/exp2_sfu.sv`](rtl/exp2_sfu.sv) | [`labs/test_exp2_sfu.py`](labs/test_exp2_sfu.py) | [Lab 08 Guide](labs/slides/lab08_exponential_sfu_slides.md) | [🎬 Video](media/videos/scene_lab08_exp2_sfu/720p30/Lab08ExponentialSFU.mp4) | Base-2 Scaler for SwiGLU / SiLU |

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

## 🛠️ Environment Setup (macOS & Windows)

This platform supports **macOS (Apple Silicon & Intel)** and **Windows (WSL2 & Native)**.

### 🔍 Quick Environment Check
Run the built-in diagnostic tool at any time to verify your system readiness:
```bash
python setup/check_env.py
```

---

### 🍎 Option 1: macOS Setup (Apple Silicon M1/M2/M3/M4 & Intel)

1. **Install Prerequisites via Homebrew:**
   ```bash
   brew update
   brew install icarus-verilog verilator yosys graphviz gtkwave python@3.12
   ```

2. **Automated Setup:**
   Run the setup script to create `.venv` and install Python dependencies:
   ```bash
   chmod +x setup/setup.sh
   ./setup/setup.sh
   ```

3. **Run Full Verification & Emulation:**
   ```bash
   ./build_and_run.sh
   # Or using universal cross-platform runner:
   python run_all.py
   ```

---

### 🪟 Option 2: Windows Setup

#### Method A: WSL2 (Ubuntu / Debian) — *Recommended for Open-Source EDA*
WSL2 provides a native Linux kernel with full compatibility for open-source EDA tools (Verilator, Icarus, Yosys).

1. **Open Windows PowerShell as Administrator:**
   ```powershell
   wsl --install
   ```
   *(Reboot your PC if prompted, then launch Ubuntu from the Start menu)*

2. **Inside WSL Ubuntu Terminal:**
   ```bash
   # Install EDA toolchains & C++ compiler
   sudo apt update && sudo apt install -y build-essential clang iverilog verilator yosys graphviz gtkwave python3-venv python3-pip

   # Clone and setup
   chmod +x setup/setup.sh
   ./setup/setup.sh

   # Run tests and C++ emulator
   ./build_and_run.sh
   ```

#### Method B: Native Windows (PowerShell / Command Prompt)

1. **Install Simulators & Tools via Winget / Web:**
   * **Icarus Verilog:** 
     ```powershell
     winget install -e --id Bleyer.IcarusVerilog
     ```
     *(Or download from [bleyer.org/icarus](https://bleyer.org/icarus/) — **ensure "Add to PATH" is checked** during installation)*
   * **Graphviz (for schematics):**
     ```powershell
     winget install Graphviz.Graphviz
     ```
   * **Python 3.10+:**
     ```powershell
     winget install Python.Python.3.12
     ```
   * **C++ Compiler:** Install [Visual Studio C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) or [MSYS2 MinGW-w64](https://www.msys2.org/).

2. **Automated Setup in PowerShell:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\setup\setup.ps1
   ```
   *(Or in Command Prompt: `setup\setup.bat`)*

3. **Run Full Verification & Emulation:**
   ```powershell
   .\build_and_run.ps1
   # Or using universal cross-platform runner:
   python run_all.py
   ```

---

## 🚀 Cross-Platform Execution Cheat Sheet

| Task | macOS / Linux / WSL | Windows (PowerShell) | Windows (CMD) | Universal (Pure Python) |
| :--- | :--- | :--- | :--- | :--- |
| **Run All Tests & C++ Emulator** | `./build_and_run.sh` | `.\build_and_run.ps1` | `build_and_run.bat` | `python run_all.py` |
| **Run Specific Lab (e.g. Lab 04)** | `python labs/run_lab.py --lab lab04` | `python labs\run_lab.py --lab lab04` | `python labs\run_lab.py --lab lab04` | `python labs/run_lab.py --lab lab04` |
| **Run All Labs (00 - 08)** | `python labs/run_lab.py --lab all` | `python labs\run_lab.py --lab all` | `python labs\run_lab.py --lab all` | `python run_all.py --run-labs` |
| **Build & Run C++ Emulator** | `python cpp_emulation/build_emulator.py --run` | `python cpp_emulation\build_emulator.py --run` | `python cpp_emulation\build_emulator.py --run` | `python cpp_emulation/build_emulator.py --run` |
| **Logic Synthesis & Schematics** | `python synthesis/synthesize.py --top all` | `python synthesis\synthesize.py --top all` | `python synthesis\synthesize.py --top all` | `python synthesis/synthesize.py --top all` |
| **Verilog file → SVG** | `python synthesis/generate_synthesis.py labs/lab0/adder.sv` | `python synthesis\generate_synthesis.py labs\lab0\adder.sv` | `python synthesis\generate_synthesis.py labs\lab0\adder.sv` | `python synthesis/generate_synthesis.py labs/lab0/adder.sv` |
| **Verilog → gate schematic (browser)** | `python synthesis/playground_server.py` | `python synthesis\playground_server.py` | `python synthesis\playground_server.py` | `python synthesis/playground_server.py` |
| **Launch Live 2D Visualizer** | `python visualizer/serve.py` | `python visualizer\serve.py` | `python visualizer\serve.py` | `python visualizer/serve.py` |
| **Open Schematics Explorer** | `open schematics/index.html` | `Start-Process schematics\index.html` | `start schematics\index.html` | `python -m webbrowser schematics/index.html` |
| **Check System Readiness** | `python setup/check_env.py` | `python setup\check_env.py` | `python setup\check_env.py` | `python setup/check_env.py` |

---

## 🔧 Troubleshooting & Tips

* **Verilator include paths:** On macOS and Linux, the builder dynamically locates headers via `verilator -getenv VERILATOR_ROOT`. On native Windows, WSL2 is recommended for Verilator emulation.
* **Paths with Spaces:** Verilator's native GNU Make rejects paths containing spaces (e.g., `Hardware Engineering`). Our custom build runner `cpp_emulation/build_emulator.py` completely bypasses this limitation by driving compilation directly with your C++ compiler.
* **Viewing Waveforms (`.vcd` and `.fst`):**
  * macOS: `gtkwave systolic_emulation.vcd` (or use the modern [Surfer](https://surfer-project.org/) waveform viewer: `brew install surfer`).
  * Windows: GTKWave is bundled with the Bleyer Icarus Verilog installer under `C:\iverilog\gtkwave\bin\gtkwave.exe`.
* **Port Conflict on Visualizer:** `visualizer/serve.py` automatically binds with socket address reuse and falls back to subsequent ports (8081, 8082, etc.) if 8080 is in use. You can also pass `--port <number>` manually.

---

## 🎯 Key Interview Talking Points

* **Hardware/Software Co-Design:** *"We used Python/Cocotb with NumPy to verify mathematical correctness at the functional level, and Verilator/C++ to create a high-speed pre-silicon cycle emulator for running software drivers."*
* **$O(N)$ vs $O(N^2)$ Arithmetic Complexity:** *"Adders require linear $O(N)$ gates (~42 gates for INT8), while multipliers require quadratic $O(N^2)$ gates (~456 gates). Quantizing from INT16 to INT8 reduces multiplier silicon area by $4\times$, which is why AI chips heavily leverage quantization."*
* **Attention Scaling:** *"Dot products have variance scaling with embedding dimension $d_k$. Dividing by $\sqrt{d_k}$ in hardware normalizes variance back to $1.0$, preventing Softmax gradients from vanishing."*
* **FlashAttention / Safe Softmax:** *"Softmax in silicon subtracts the row maximum to avoid exponential overflow, keeping fixed-point representations strictly bounded within $(0, 1]$."*
