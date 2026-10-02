# 🎬 Hardware AI Acceleration — 5 to 7 Minute Video Suite

Broadcast-quality animated video masterclasses for the **Hardware AI Acceleration & Tensor Core Engineering** curriculum.

Engineered specifically for **Computer Science Engineers and Students** transitioning from software abstractions (Python, PyTorch, C++) into physical silicon architecture (Google TPU, NVIDIA Tensor Cores, synthesizable SystemVerilog RTL).

---

## 🌟 The Software-to-Hardware Bridge ("Why Software Engineers Must Learn Silicon")

In software, matrix multiplication is written as a clean single line:
$$\text{Output} = \text{Softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V$$

On a sequential CPU, computing this for a 1-million-token LLM requires **over 1 trillion operations**, causing total cache thrashing and memory bus saturation:
* **The 1,000x Memory Energy Wall:** Reading one 32-bit float from off-chip DRAM takes **$\sim$200 picojoules**; computing the math takes **$\sim$0.2 picojoules**. The CPU burns 99% of its power moving electrons over copper PCB traces!
* **The Spatial Silicon Solution:** Custom ASICs (Google TPU, Apple Neural Engine) replace the Von Neumann bus with a **2D Systolic Wavefront**: weights stay locked stationary in local registers, while activations ripple across neighboring Processing Elements like a heartbeat.
* **The Pre-Silicon HW/SW Co-Design Career:** Chip fabrication (tape-out) costs **$50M–$100M+ per iteration**. Top AI infrastructure labs pay premium compensation ($300k–$500k+) for engineers who can bridge high-level ML kernels with hardware execution constraints.

---

## 📺 Masterclass Video Catalog

| Module | Masterclass Video | Key Concept & Software-to-Hardware Analogy | Duration | Production MP4 Path |
| :--- | :--- | :--- | :--- | :--- |
| **Lab 04 (Flagship)** | `Lab04SystolicArray` | **Google TPU 2D Wavefront:** Memory wall (200 pJ vs 0.2 pJ), unskewed failure demo, D-FF activation skewing, cycle walkthrough $T=0\dots T=4$, Cocotb Python verification | **5:10 - 5:35** | [`media/videos/scene_lab04_systolic_array/720p30/Lab04SystolicArray_narrated.mp4`](../media/videos/scene_lab04_systolic_array/720p30/Lab04SystolicArray_narrated.mp4) |
| **Lab 00-Prep** | `Lab00PrepPrimer` | **The Death of the Program Counter:** Sequential thread loops vs 100% concurrent silicon gates, wires vs D-FF registers | ~5:15 | [`media/videos/scene_lab00_prep/720p30/Lab00PrepPrimer.mp4`](../media/videos/scene_lab00_prep/720p30/Lab00PrepPrimer.mp4) |
| **Lab 00** | `Lab00SaturationIntro` | **The +100 + +50 = -106 Bug:** Signed wrap-around overflow in neural nets, 2's complement wheel & clamping | ~5:15 | [`media/videos/scene_lab00_saturation/720p30/Lab00SaturationIntro.mp4`](../media/videos/scene_lab00_saturation/720p30/Lab00SaturationIntro.mp4) |
| **Lab 01** | `Lab01Multiplier` | **The Silicon Cost of Math:** $O(N^2)$ partial product growth, why FP32 costs 16x more silicon area than INT8 | ~5:20 | [`media/videos/scene_lab01_multiplier/720p30/Lab01Multiplier.mp4`](../media/videos/scene_lab01_multiplier/720p30/Lab01Multiplier.mp4) |
| **Lab 02** | `Lab02MACUnit` | **Accumulator Headroom Math:** Dot products for $K=4096$, zero-extension traps vs signed extension | ~5:15 | [`media/videos/scene_lab02_mac_unit/720p30/Lab02MACUnit.mp4`](../media/videos/scene_lab02_mac_unit/720p30/Lab02MACUnit.mp4) |
| **Lab 03** | `Lab03ProcessingElement` | **Inside the PE:** Weight-stationary flip-flop locks, local neighbor wiring, zero shared bus contention | ~5:30 | [`media/videos/scene_lab03_pe/720p30/Lab03ProcessingElement.mp4`](../media/videos/scene_lab03_pe/720p30/Lab03ProcessingElement.mp4) |
| **Lab 05** | `Lab05SquareRoot` | **Attention Variance Scaling ($1/\sqrt{d_k}$):** Non-restoring digit-by-digit root engine preventing Softmax vanishing gradients | ~5:15 | [`media/videos/scene_lab05_sqrt/720p30/Lab05SquareRoot.mp4`](../media/videos/scene_lab05_sqrt/720p30/Lab05SquareRoot.mp4) |
| **Lab 06** | `Lab06Softmax` | **Safe Softmax & FlashAttention:** $\Delta_i = x_i - \max(X)$, exponential LUTs, and hardware accumulation pipelines | ~5:40 | [`media/videos/scene_lab06_softmax/720p30/Lab06Softmax.mp4`](../media/videos/scene_lab06_softmax/720p30/Lab06Softmax.mp4) |
| **Lab 07** | `Lab07RSQRT` | **LLaMA-3 RMSNorm Engine:** Seed ROM + digit root + Q8.8 reciprocal division unit | ~5:20 | [`media/videos/scene_lab07_rsqrt/720p30/Lab07RSQRT.mp4`](../media/videos/scene_lab07_rsqrt/720p30/Lab07RSQRT.mp4) |
| **Lab 08** | `Lab08ExponentialSFU` | **SwiGLU / SiLU Activation:** Base-2 trick $e^x = 2^I \cdot 2^F$, barrel shifter + 16-entry fractional LUT | ~5:30 | [`media/videos/scene_lab08_exp2_sfu/720p30/Lab08ExponentialSFU.mp4`](../media/videos/scene_lab08_exp2_sfu/720p30/Lab08ExponentialSFU.mp4) |

---

## 🚀 How to Run, Render & Narrate

### 1. Render Specific Video (720p 30fps)
```bash
python animations/render_all.py 04
```

### 2. Render & Automatically Synthesize Voiceover
```bash
# Renders the Manim animation, generates speech audio with macOS 'Samantha', and muxes into final MP4:
python animations/render_all.py 04 --narrate
```

### 3. Render 1080p 60fps (High Quality for YouTube)
```bash
python animations/render_all.py 04 --high --narrate
```

### 4. Standalone Voiceover Audio Generator
```bash
python animations/narrate_video.py --voice Samantha
```

---

## 📚 Pedagogical Architecture Documentation

* **Director's Cut Script:** [`animations/SYSTOLIC_ARRAY_VIDEO_SCRIPT.md`](SYSTOLIC_ARRAY_VIDEO_SCRIPT.md) — Line-by-line spoken dialogue, visual cues, sound design, and timestamps.
* **Production Master Guide:** [`animations/CSE_VIDEO_PRODUCTION_GUIDE.md`](CSE_VIDEO_PRODUCTION_GUIDE.md) — The 6-act formula, audience psychology, and selling hooks across all curriculum labs.
* **Shared Design System:** [`animations/theme.py`](theme.py) — Slate-900 dark theme, code windows, metric cards, narration banners, and hardware primitives.
