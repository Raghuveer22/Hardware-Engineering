# 🎥 CSE Hardware Animation Production Master Guide

A comprehensive architectural blueprint for creating high-retention, broadcast-quality **5-to-7 minute video lessons** for Computer Science Engineers and students who are new to physical hardware design.

---

## 🎯 Target Audience Profile & Pedagogical Mission

* **Who they are:** Computer Science & AI students, software developers, ML engineers, backend/systems programmers.
* **What they know:** Python, PyTorch, C/C++, Big-O complexity, multithreading, memory pointers, tensors, matrix arithmetic ($C = A \cdot B$).
* **What they struggle with:**
  1. *The Concurrency Illusion:* Thinking hardware executes instructions sequentially with a Program Counter.
  2. *The Memory Wall:* Not understanding why a CPU spends 90% of its power and time moving bytes across a PCB instead of computing.
  3. *Clock Latency:* Not realizing that in physical silicon, every register (flip-flop) introduces a real 1-clock delay ($T_{\text{clk}}$).
  4. *Area & Power Tradeoffs:* Why we use INT8 or FP8 instead of FP32 in production AI chips.

---

## 📐 The 5-to-7 Minute (300 - 420s) Formula

Every lab video must follow this proven **6-Act Narrative Arc**:

```
┌────────────────────────────────────────────────────────────────────────┐
│ Act 1: The Software Hook & The Failure Mode            (0:00 - 1:00)   │
│ Act 2: The Physical Silicon Limits & The Energy Wall   (1:00 - 2:00)   │
│ Act 3: Inside the Hardware Datapath & Gates            (2:00 - 3:15)   │
│ Act 4: Cycle-by-Cycle Execution with Real Numbers      (3:15 - 4:45)   │
│ Act 5: Interactive Checkpoints & Math Challenge        (4:45 - 5:30)   │
│ Act 6: Pre-Silicon Verification & Career Call-to-Action(5:30 - 6:30)   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 💡 How We "Sell": The HW/SW Co-Design Value Proposition

To keep viewers hooked and convert them into enthusiastic hardware designers, every video must hammer these key value propositions:

1. **The Software Ceiling:** Software optimizations (AVX, loop tiling, CUDA kernels) hit a physical wall when DRAM bandwidth saturates. Only custom silicon breaks through.
2. **The $100M Pre-Silicon Reality:** Chip fabrication (tape-out) costs $50M–$100M. Bugs cannot be patched with a Git commit. Pre-silicon verification (Python Cocotb + SystemVerilog) is where the most critical engineering happens.
3. **The $300k–$500k Career Frontier:** AI infrastructure companies (NVIDIA, Apple, Google, Meta, OpenAI, Groq, Tenstorrent) desperately need engineers who can bridge the gap between high-level frameworks (PyTorch/Triton) and silicon architecture.

---

## 🎬 Curriculum Video Roadmap (All 10 Labs)

| Module | Video Title / Hook | Core Software Analogy | Hardware Reality Taught | Target Duration |
| :--- | :--- | :--- | :--- | :--- |
| **Lab 00-Prep** | *Your Brain on Silicon: The Death of the Program Counter* | `a = b + c; d = a * 2;` line-by-line | 100% concurrent gates, wires vs D-FF registers, setup/hold time | 5:30 (330s) |
| **Lab 00** | *The 100+50 = -106 Disaster: Why LLMs Need Hardware Saturation* | Signed integer overflow, 2's complement wheel | Parameterized signed clamp, sticky bit detection, NaN prevention | 5:15 (315s) |
| **Lab 01** | *The Silicon Cost of Math: Why Multipliers are O(N²) in Area* | `x * y` single operator in Python | 64 partial product AND gates, adder trees, 16x area jump of FP32 | 5:20 (320s) |
| **Lab 02** | *Headroom Math: Why 16-Bit Multipliers Need 32-Bit Accumulators* | `sum += a * b` in dot product | $K=4096$ accumulation growth, sign-extension traps, bit headroom | 5:15 (315s) |
| **Lab 03** | *The 1000x Memory Wall: Weight-Stationary Processing Elements* | Cache misses in large matrix loops | DRAM (200 pJ) vs MAC (0.2 pJ), local register locks, neighbor wires | 5:30 (330s) |
| **Lab 04** | *Inside the Google TPU: 4x4 Systolic Wavefronts & Skewing* | `Q @ K.T` in self-attention | 2D PE mesh, activation skew registers, diagonal wavefront | 5:35 (335s) |
| **Lab 05** | *Attention Scaling in Silicon: Hardware Digit-by-Digit Square Root* | `1.0 / math.sqrt(d_k)` | Non-restoring square root datapath, keeping Softmax variance 1.0 | 5:15 (315s) |
| **Lab 06** | *Why Softmax Blows Up: Safe Softmax & FlashAttention in Hardware* | `torch.softmax(x)` numerical overflow | $\Delta_i = x_i - \max(X)$, exp LUT, reciprocal scaling in Q0.8 | 5:40 (340s) |
| **Lab 07** | *LLaMA-3 RMSNorm: Fast Reciprocal Square Root ($1/\sqrt{x}$)* | `F.rms_norm(x)` | Seed ROM + digit-by-digit root + Q8.8 reciprocal engine | 5:20 (320s) |
| **Lab 08** | *SwiGLU & SiLU Activation SFU: The Base-2 Exponentiation Trick* | `x * torch.sigmoid(x)` | $e^x = 2^I \cdot 2^F$, barrel shifter + 16-entry fractional LUT | 5:30 (330s) |

---

## 🛠 Production Tools & Commands

### 1. Render the Animation
```bash
# Render specific lab (e.g. Lab 04 Masterclass in 720p 30fps)
python animations/render_all.py 04

# Render high-quality 1080p 60fps for YouTube distribution
python animations/render_all.py 04 --high
```

### 2. Generate Voiceover & Mux Audio
```bash
# Automatically synthesizes speech with macOS 'Samantha' and muxes audio track into video
python animations/render_all.py 04 --narrate
```

Output video location:
`media/videos/scene_lab04_systolic_array/720p30/Lab04SystolicArray_narrated.mp4`
