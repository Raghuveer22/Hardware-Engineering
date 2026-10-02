# 📊 Hardware AI Acceleration — Interactive Presenter & Lab Guides

Teaching and presentation materials for the **Hardware AI Acceleration & Tensor Core Engineering** curriculum.

---

## 📖 Primary Curriculum Guides

All lectures and walkthroughs are taught directly from the camera-ready, scrollable Markdown guides in [`labs/slides/`](../labs/slides/):

| Lab | Module | Topic & Focus | Guide Link |
| :--- | :--- | :--- | :--- |
| **Lab 00-Prep** | Foundations | Software vs Silicon Mindset, Two's Complement, Q-Format, Cocotb | [Lab 00-Prep Guide](../labs/slides/lab00_prep_hardware_thinking_primer.md) |
| **Lab 00** | Silicon Math | Parameterized Signed Adder & Saturation Arithmetic | [Lab 00 Guide](../labs/slides/lab00_adder_slides.md) |
| **Lab 01** | Silicon Math | Signed INT8 Multiplier & $O(N^2)$ Silicon Scaling | [Lab 01 Guide](../labs/slides/lab01_multiplier_slides.md) |
| **Lab 02** | Silicon Math | Multiply-Accumulate (MAC) Unit & 32-bit Accumulator Sizing | [Lab 02 Guide](../labs/slides/lab02_mac_unit_slides.md) |
| **Lab 03** | 2D Tensor Cores | Weight-Stationary Processing Element (PE) Registers | [Lab 03 Guide](../labs/slides/lab03_processing_element_slides.md) |
| **Lab 04** | 2D Tensor Cores | 4×4 2D Systolic Matrix Multiplier Mesh & Activation Skewing | [Lab 04 Guide](../labs/slides/lab04_systolic_array_slides.md) |
| **Lab 05** | Transformer SFUs | Hardware Square Root ($1/\sqrt{d_k}$ Attention Scaling) | [Lab 05 Guide](../labs/slides/lab05_sqrt_slides.md) |
| **Lab 06** | Transformer SFUs | Safe Softmax Engine & FlashAttention Foundations | [Lab 06 Guide](../labs/slides/lab06_softmax_slides.md) |
| **Lab 07** | Transformer SFUs | Fast Reciprocal Square Root (`rsqrt`) for RMSNorm / LayerNorm | [Lab 07 Guide](../labs/slides/lab07_rsqrt_slides.md) |
| **Lab 08** | Transformer SFUs | Hardware Exponential SFU ($2^x / e^x$) for SwiGLU / SiLU | [Lab 08 Guide](../labs/slides/lab08_exponential_sfu_slides.md) |

---

## ⚡ Interactive Browser Presenter

To launch the live interactive browser visualizer & demo deck:

```bash
python3 slides/serve.py
```

Open **http://localhost:8000** to access:
* **Interactive Adder Simulator** — Live two's-complement overflow & saturation clamp tester.
* **Systolic Wavefront Grid** — Step-by-step matrix flow animation.
* **KaTeX Rendering** — Live mathematical formulas and architecture diagrams.
