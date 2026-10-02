# 🎬 Hardware AI Acceleration — Manim Video Suite

End-to-end animated video lessons for all modules in the **Hardware AI Acceleration & Tensor Core Engineering** curriculum.

Built with [Manim Community Edition](https://www.manim.community/) and styled with high-contrast hardware engineering aesthetics (`Slate-900` dark theme, color-coded silicon dataflow, cycle-accurate timing).

---

## 📺 Generated Videos Catalog

All rendered MP4 videos are located in `media/videos/`:

| Lab | Video Scene | Key Hardware Concept Animated | Output Video Path |
| :--- | :--- | :--- | :--- |
| **Lab 00-Prep** | `Lab00PrepPrimer` | Software PC vs Concurrent Silicon Gates, Wires vs D-FF Registers | [`media/videos/scene_lab00_prep/720p30/Lab00PrepPrimer.mp4`](../media/videos/scene_lab00_prep/720p30/Lab00PrepPrimer.mp4) |
| **Lab 00** | `Lab00SaturationIntro` | The $+100 + +50 = -106$ Wrap-Around Bug, 2's Complement Wheel & Clamp | [`media/videos/scene_lab00_saturation/720p30/Lab00SaturationIntro.mp4`](../media/videos/scene_lab00_saturation/720p30/Lab00SaturationIntro.mp4) |
| **Lab 01** | `Lab01Multiplier` | $8 \times 8 \to 16$ Bit Growth, $O(N^2)$ Partial Product Silicon Area | [`media/videos/scene_lab01_multiplier/720p30/Lab01Multiplier.mp4`](../media/videos/scene_lab01_multiplier/720p30/Lab01Multiplier.mp4) |
| **Lab 02** | `Lab02MACUnit` | Accumulator Headroom Math ($K=4096$), The Zero-Extension Disaster | [`media/videos/scene_lab02_mac_unit/720p30/Lab02MACUnit.mp4`](../media/videos/scene_lab02_mac_unit/720p30/Lab02MACUnit.mp4) |
| **Lab 03** | `Lab03ProcessingElement` | DRAM Memory Wall ($200\text{ pJ}$ vs $0.2\text{ pJ}$), Weight-Stationary Spatial Dataflow | [`media/videos/scene_lab03_pe/720p30/Lab03ProcessingElement.mp4`](../media/videos/scene_lab03_pe/720p30/Lab03ProcessingElement.mp4) |
| **Lab 04** | `Lab04SystolicArray` | 4×4 PE Mesh, Activation Skewing, Diagonal Wavefront ($T_1 \dots T_4$) | [`media/videos/scene_lab04_systolic_array/720p30/Lab04SystolicArray.mp4`](../media/videos/scene_lab04_systolic_array/720p30/Lab04SystolicArray.mp4) |
| **Lab 05** | `Lab05SquareRoot` | Transformer $1/\sqrt{d_k}$ Attention Scaling, Digit-by-Digit Root Engine | [`media/videos/scene_lab05_sqrt/720p30/Lab05SquareRoot.mp4`](../media/videos/scene_lab05_sqrt/720p30/Lab05SquareRoot.mp4) |
| **Lab 06** | `Lab06Softmax` | Safe Softmax $\Delta_i = x_i - \max(X)$, 4-Stage Hardware Pipeline (Q0.8) | [`media/videos/scene_lab06_softmax/720p30/Lab06Softmax.mp4`](../media/videos/scene_lab06_softmax/720p30/Lab06Softmax.mp4) |
| **Lab 07** | `Lab07RSQRT` | RMSNorm in LLaMA 3, Seed ROM + Digit Root + Q8.8 Reciprocal Scaler | [`media/videos/scene_lab07_rsqrt/720p30/Lab07RSQRT.mp4`](../media/videos/scene_lab07_rsqrt/720p30/Lab07RSQRT.mp4) |
| **Lab 08** | `Lab08ExponentialSFU` | SwiGLU / SiLU, Base-2 Trick $e^x = 2^I \cdot 2^F$, Barrel Shifter + LUT | [`media/videos/scene_lab08_exp2_sfu/720p30/Lab08ExponentialSFU.mp4`](../media/videos/scene_lab08_exp2_sfu/720p30/Lab08ExponentialSFU.mp4) |

---

## 🚀 How to Run & Re-Render

Render all animations at standard 720p 30fps:
```bash
python animations/render_all.py
```

Render a specific lab (e.g. Lab 04 Systolic Array):
```bash
python animations/render_all.py 04
```

Render in 1080p 60fps (High Quality for YouTube export):
```bash
python animations/render_all.py --high
```
