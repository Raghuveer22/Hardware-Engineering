# 🎬 Lab 04 Masterclass Video Script & Production Blueprint

**Title:** *Inside the Google TPU: How Systolic Arrays Accelerate LLMs 100x Faster Than CPUs*  
**Subtitle:** *A Software Engineer's Visual Guide to AI Silicon, 2D Wavefronts, and the Memory Wall*  
**Target Audience:** Computer Science Engineers & Students (Familiar with Python/PyTorch/C++, new to physical hardware)  
**Total Target Runtime:** 5:10 - 5:35 (310 - 335 seconds)  
**Visual Style:** Slate-900 Dark High-Contrast Theme (`#0f172a`), Monospace Bit-Streams, Dynamic Subtitle Banners, Real Arithmetic Values  

---

## 🎭 The 6-Act Pedagogical & Selling Arc

```
[ Act 1: The Software Hook ] ────► [ Act 2: The Physical Silicon Limits ]
  (PyTorch Code & 1M Tokens)          (The 1,000x Memory Energy Wall)
                                                    │
                                                    ▼
[ Act 4: The 2D Systolic Wavefront ] ◄── [ Act 3: Inside the Weight-Stationary PE ]
  (Cycle Walkthrough T0..T4 & Skewing)     (Internal Datapath & INT8 Math)
                 │
                 ▼
[ Act 5: Interactive Knowledge Check ] ──► [ Act 6: Pre-Silicon Cocotb & Career Frontier ]
  (Pause & Think, Math Challenge)             (Python Verification & The $500k HW/SW Gap)
```

---

## 📜 Scene-by-Scene Director's Cut

### **Act 1: The Software Paradox & The LLM Scaling Crisis (0:00 - 0:50)**
* **Visual Cue:**
  * Top kicker badge: `FROM PYTORCH TO SILICON` in Cyan.
  * Title: `Why Modern LLMs Demand Custom Hardware` in bold white.
  * Left Panel: Mac-style terminal IDE window with highlighted code:
    ```python
    scores = Q @ K.T / sqrt(d_k)
    probs  = softmax(scores)
    output = probs @ V
    ```
    Followed by C++ CPU 3-nested loop (`for i: for j: for k: C[i][j] += A[i][k]*B[k][j]`).
  * Right Panel: Stat cards: `1 Trillion Operations per Token` (Amber), `90% Stalled: Von Neumann Bottleneck` (Red).
* **Narrative Voiceover (Spoken by Samantha):**
  > *"Welcome to Hardware AI Acceleration. Today, we bridge the fundamental gap between software code in PyTorch and physical silicon gates on a chip.*  
  > *As software engineers, we write matrix multiplications as clean single-line abstractions, like Q times K transpose in self-attention.*  
  > *Under the hood, a standard sequential CPU translates this into three nested loops, running with O of N cubed time complexity.*  
  > *In modern Large Language Models with one-million-token context windows, a single attention head requires over one trillion arithmetic operations.*  
  > *On standard CPUs, this causes catastrophic cache thrashing. The processor spends ninety percent of its clock cycles and power simply waiting for memory from DRAM.*  
  > *How do Google TPUs and NVIDIA Tensor Cores solve this? The answer lies in Spatial Hardware Computing."*

---

### **Act 2: CPU vs GPU vs TPU & The 1,000x Memory Wall (0:50 - 1:45)**
* **Visual Cue:**
  * Kicker: `THE PHYSICS OF SILICON` (Red badge).
  * Title: `The 1,000x Memory Energy Wall`.
  * Animated Horizontal Bar Chart with exact physical energy numbers:
    * **DRAM Read (Off-Chip Memory):** `200.0 pJ` (Red bar: 7.2 units) — *1,000x Energy Penalty!*
    * **On-Chip SRAM Buffer (Cache):** `5.0 pJ` (Amber bar: 2.2 units) — *25x cheaper than DRAM*
    * **PE Local Register (Flip-Flop):** `1.0 pJ` (Cyan bar: 0.9 units) — *Local in-place storage*
    * **INT8 MAC Math Operation:** `0.2 pJ` (Green bar: 0.4 units) — *The math itself is virtually FREE!*
* **Narrative Voiceover:**
  > *"In computer science, we analyze algorithmic Big-O complexity. But in silicon physics, wire distance and energy dissipation dictate everything.*  
  > *Look at the physical numbers: performing an eight-bit multiply-accumulate operation takes just zero-point-two picojoules of energy.*  
  > *Accessing an on-chip SRAM cache takes five picojoules. But fetching that same number from external DRAM takes two hundred picojoules!*  
  > *That is a one-thousand-times energy penalty just to move a number across circuit board traces!*  
  > *A CPU moves numbers back and forth over a shared bus on every iteration. To achieve massive AI throughput, we must never re-read weights from memory.*  
  > *This fundamental insight gave birth to the Weight-Stationary Systolic Array."*

---

### **Act 3: Inside the Weight-Stationary PE Datapath (1:45 - 2:40)**
* **Visual Cue:**
  * Kicker: `LAB 03 & 04 ARCHITECTURE` (Amber badge).
  * Title: `Inside the Weight-Stationary Processing Element`.
  * Detailed internal PE block diagram:
    * Amber register: `Weight Reg (Locked Stationary)`.
    * Green MAC unit: `sum_out = sum_in + a*w`.
    * Cyan register: `East Reg (Act Forwarding)`.
    * Green register: `South Reg (Sum Forwarding)`.
  * Animated glowing cyan activation packet and green sum packet enter, MAC engine flashes white upon firing.
  * Bullet points explain zero shared buses and INT8 16x silicon area reduction.
* **Narrative Voiceover:**
  > *"Let us zoom into the silicon floorplan and inspect a single Processing Element, or P-E.*  
  > *Each Processing Element contains a dedicated weight register, an eight-bit MAC engine, an activation forwarding register, and a partial sum forwarding register.*  
  > *Weights are pre-loaded once before matrix multiplication begins, and remain locked stationary in local flip-flops.*  
  > *Activations stream horizontally from West to East. Partial sums accumulate vertically from North to South.*  
  > *There are zero shared memory buses. Every Processing Element communicates only with its immediate physical neighbors.*  
  > *Because wire lengths are microscopic, parasitic resistance is near zero, allowing modern tensor engines to clock at gigahertz speeds."*

---

### **Act 4: The 2D Systolic Wavefront & Activation Skewing (2:40 - 4:05)**
* **Visual Cue:**
  * Kicker: `THE HEARTBEAT OF SILICON` (Green badge).
  * Title: `Activation Skewing & The 2D Wavefront`.
  * **The Naive Failure Screen (Red Alert):** Shows what happens if inputs are not skewed ($T=1$ simultaneous arrival: $PE(1,0)$ fires with partial sum 0, computing $0 + 2 \times 7 = 14$ instead of $19$).
  * **2×2 Mesh Grid with Real Numbers:**
    * Input vector: $A = [1, 2]$
    * Weight matrix: $W = \begin{bmatrix} 5 & 6 \\ 7 & 8 \end{bmatrix}$
    * Row 0: `[1] (Delay 0)`, Row 1: `[2] (Delay 1 cycle via D-FF)`
  * **Cycle-by-Cycle Wavefront Execution:**
    * **$T=1$ (Cyan):** Activation 1 enters PE(0,0). $1 \times 5 = 5$. Partial sum latches South.
    * **$T=2$ (Amber):** Wavefront spreads diagonally. $A_0=1$ hops East to PE(0,1) ($1 \times 6 = 6$). Skewed $A_1=2$ enters PE(1,0): $5 + (2 \times 7) = 19$! Column 0 is COMPLETE!
    * **$T=3$ (Green):** Wavefront reaches PE(1,1). $A_1=2$ hops East, sum 6 flows South: $6 + (2 \times 8) = 22$! Column 1 is COMPLETE!
    * **$T=4$ (Result Emergence):** Vector $C = [19, 22]$ streams out of bottom pins.
* **Narrative Voiceover:**
  > *"Now connect PEs into a two-dimensional spatial grid. Here we encounter the central architectural puzzle: Activation Skewing.*  
  > *Watch what happens if we feed inputs naively without skewing: PE one-zero calculates before PE zero-zero's sum arrives!*  
  > *Because registers have physical propagation latency, software-style instant execution produces total mathematical corruption.*  
  > *The architectural solution is input skewing. Row k is delayed by exactly k clock cycles using hardware D flip-flop registers.*  
  > *At Clock One, activation one enters PE zero-zero. One times five equals five. The partial sum five latches into the South register.*  
  > *At Clock Two, activation one hops East to PE zero-one. Skewed activation two enters PE one-zero. Five plus two times seven equals nineteen! Column zero is complete!*  
  > *At Clock Three, activation two hops East to PE one-one. Partial sum six flows South. Six plus two times eight equals twenty-two! Column one is complete!*  
  > *At Clock Four, the final result vector C equals nineteen, twenty-two streams out of the chip's bottom pins.*  
  > *Checking our software math: one times five plus two times seven is nineteen, and one times six plus two times eight is twenty-two. The physical silicon executed the exact dot product!"*

---

### **Act 5: Checkpoint & Interactive Challenge (4:05 - 4:45)**
* **Visual Cue:**
  * "PAUSE & THINK" Cyan Card with pulsing dot.
  * Question: *"Why is this architecture called 'Systolic'?"*
  * Answer reveals: Like the human heart pumping blood, data pulses in lockstep on every clock edge.
  * "TRY IT YOURSELF" Amber Challenge Card:
    * Given $A = [3, 4]$ and $W = \begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}$, what is $C$?
    * Solution reveals: $C = [3 \cdot 1 + 4 \cdot 3, 3 \cdot 2 + 4 \cdot 4] = [15, 22]$.
* **Narrative Voiceover:**
  > *"Pause and think: Why is this called a Systolic Array? Like the medical systole of a human heart pumping blood, data pulses through the silicon grid on every rising clock edge.*  
  > *Try this test: for input vector three, four and weight matrix one, two, three, four, the result vector is fifteen, twenty-two."*

---

### **Act 6: Pre-Silicon Verification & Career Frontier (4:45 - 5:25)**
* **Visual Cue:**
  * Kicker: `FROM ACADEMIA TO PRODUCTION` (Purple badge).
  * Title: `Google TPU Scale & Pre-Silicon Verification`.
  * Left Panel: Cocotb Python Verification Code Window:
    ```python
    @cocotb.test()
    async def test_wavefront(dut):
        cocotb.start_soon(Clock(dut.clk, 10, 'ns').start())
        await load_weights(dut, W)
        await stream_row_skewed(dut, A)
        assert dut.c_out.value == np.dot(A, W)
    ```
  * Right Panel: TPU v5 Specs card ($128 \times 128$ array = 16,384 MACs/clk, $3N-2$ latency).
  * Closing Recap Card with actionable steps: `rtl/systolic_array.sv`, `labs/run_lab.py --lab 04`, `visualizer/serve.py`, `synthesis/synthesize.py`.
* **Narrative Voiceover:**
  > *"In production, Google TPUs scale this exact architecture to massive one-hundred-twenty-eight by one-hundred-twenty-eight systolic arrays, performing over sixteen thousand operations every clock cycle.*  
  > *Because chip tape-outs cost fifty to one hundred million dollars, hardware teams verify everything pre-silicon using Python Cocotb testbenches driving synthesizable SystemVerilog.*  
  > *Notice how software engineers write verification tests in native Python, asserting bit-exact matches against PyTorch and NumPy.*  
  > *The tech industry faces a massive shortage of engineers who understand both software frameworks and hardware architecture. Bridging this gap places you in the highest-compensation tier of AI engineering.*  
  > *Your next step: open rtl slash systolic array dot sv, run the Cocotb testbench, and launch the interactive visualizer to see the wavefront live."*

---

## 🛠 Production Assets & Outputs

| Asset Type | File Path | Status |
| :--- | :--- | :--- |
| **Manim Scene Script** | [`animations/scene_lab04_systolic_array.py`](scene_lab04_systolic_array.py) | ✅ Fully implemented (334s, 112 animations) |
| **Master Voiceover Audio** | `animations/temp_audio/lab04_master_voiceover.wav` | ✅ Generated via macOS Speech Synthesis (`Samantha`) |
| **Silent 720p30 MP4** | `media/videos/scene_lab04_systolic_array/720p30/Lab04SystolicArray.mp4` | ✅ Rendered (5m 34s duration) |
| **Narrated Production MP4** | [`media/videos/scene_lab04_systolic_array/720p30/Lab04SystolicArray_narrated.mp4`](../media/videos/scene_lab04_systolic_array/720p30/Lab04SystolicArray_narrated.mp4) | ✅ Muxed with crystal-clear voiceover (5m 10s) |
| **Automated Narration Tool**| [`animations/narrate_video.py`](narrate_video.py) | ✅ Reusable for all curriculum labs |
