# 📺 YouTube Masterclass Metadata & Packaging Guide

A complete YouTube distribution guide for the **Hardware AI Acceleration & Tensor Core Engineering** video suite.
Optimized for high Click-Through Rate (CTR), viewer retention, and YouTube search/algorithm discovery.

---

## 🎬 Video Catalog & YouTube Packaging

---

### 1. Lab 00-Prep: Hardware Thinking Primer
* **YouTube Title:** *Why Software Engineers Struggle with Silicon: The Death of the Program Counter*
* **Alternative Title:** *Your Brain on Silicon: How Hardware Thinks (Software vs ASIC)*
* **Thumbnail Concept:**
  * **Visual:** Split-screen — Left: Dark IDE code window with yellow Program Counter cursor frozen at `a = b + c`. Right: Glowing cyan silicon die with hundreds of parallel logic gates firing electric lightning sparks simultaneously.
  * **Text Hook:** `DEATH OF THE PROGRAM COUNTER` (Cyan & Gold, Bold Sans).
* **YouTube Description:**
  ```markdown
  Transitioning from Python/PyTorch/C++ into physical chip design? In software, your brain is trained on sequential execution: Line 1 runs, then Line 2, driven by a single Program Counter.
  
  In custom silicon (Google TPU, NVIDIA Tensor Cores), there is NO Program Counter. Voltage flows continuously through copper traces, and millions of logic gates compute concurrently. This visual-first lesson breaks down the foundational mental shift needed to design AI accelerators.

  ⏱️ Chapters & Timestamps:
  0:00 - The Program Counter Illusion: Sequential Software Loops
  0:50 - The Silicon Reality: 100% Concurrency Across Die
  1:45 - The Two Pillars: Combinational Logic vs Sequential Registers
  2:45 - Anatomy of a D Flip-Flop: Clocks, Setup, & Hold Time
  3:45 - Architectural Checkpoint: Can Gates Store Memory Without a Clock?
  4:30 - Synthesizable SystemVerilog & Python Cocotb Verification
  
  📁 Code & Blueprints:
  Repository: https://github.com/Raghuveer22/Hardware-Engineering
  SystemVerilog RTL: rtl/
  Testbenches: labs/

  #HardwareEngineering #SiliconDesign #ComputerArchitecture #Verilog #ASIC #SystemVerilog #GoogleTPU
  ```
* **SEO Tags:** `Hardware Engineering, ASIC design, SystemVerilog tutorial, D Flip Flop, Combinational Logic, Software to Hardware, Google TPU architecture, Computer Architecture, Cocotb`

---

### 2. Lab 00: Parameterized Signed Adder & Saturation Clamping
* **YouTube Title:** *The 100 + 50 = -106 Bug: Why LLMs Need Hardware Saturation Arithmetic*
* **Alternative Title:** *How 1 Broken Bit Destroys AI: Signed Two's Complement & Silicon Saturation*
* **Thumbnail Concept:**
  * **Visual:** Close-up of the circular Two's Complement Speedometer dial. The needle has swung past +127 into the red danger zone, showing large red text: `-106`. Beside it, a gleaming spring-loaded clamp barrier is dropping into place.
  * **Text Hook:** `+100 + 50 = -106?!` (White & Red Warning).
* **YouTube Description:**
  ```markdown
  In 8-bit quantized neural networks (INT8), standard binary addition hides a deadly trap. When attention activations add past +127, sign-bit wraparound corrupts positive weights into extreme negative values: +100 + +50 = -106!
  
  In this visual deep-dive, we build an 8-bit signed adder from scratch: from 1-bit Full Adder logic gates (XOR, AND, OR), to ripple-carry propagation delays, the Two's Complement Speedometer dial, and spring-loaded hardware saturation clamping.

  ⏱️ Chapters & Timestamps:
  0:00 - The PyTorch Hook: INT8 Overflow Logit Bug
  0:50 - First Principles: Anatomy of a 1-Bit Full Adder
  1:50 - Cascading Bit Slices: 8-Bit Ripple Carry Chain & Propagation Delay
  2:45 - Inside the Silicon: Two's Complement Speedometer Wheel
  3:25 - Deploying the Hardware Saturation Clamp Barrier (+127)
  3:50 - Architectural Checkpoint: The Negative Overflow Challenge (-100 + -50)
  4:35 - Synthesizable SystemVerilog RTL (rtl/adder.sv) & Cocotb Verification

  #AIHardware #TwoComplement #DigitalLogic #Verilog #Cocotb #ComputerEngineering #TensorCores
  ```
* **SEO Tags:** `Signed integer overflow, Twos complement, Full Adder schematic, Ripple Carry Adder, Saturation arithmetic, AI Silicon, Fixed point arithmetic, RTL design`

---

### 3. Lab 01: Parameterized Signed Multiplier (INT8) & Wallace Tree
* **YouTube Title:** *The O(N²) Silicon Area Monster: Why Multipliers Consume 90% of AI Chips*
* **Alternative Title:** *How Silicon Multiplies: 64 AND Gates, Baugh-Wooley, & Wallace Trees*
* **Thumbnail Concept:**
  * **Visual:** An 8x8 glowing matrix of 64 AND gate points on a chip die, with a visual scale comparison showing a tiny green Adder box (42 gates) vs a gigantic red Multiplier block (456 gates).
  * **Text Hook:** `THE O(N²) SILICON MONSTER` (Gold & Red).
* **YouTube Description:**
  ```markdown
  Generating a single token in modern LLMs requires over 60 million multiplications in less than 5 milliseconds. But while adders scale linearly in silicon area O(N), multipliers scale quadratically O(N²)!
  
  Explore how silicon multiplies bits: pen-and-paper shift-and-add, the 64-AND-gate partial product grid, the negative sign-bit trap solved by the Baugh-Wooley algorithm, and Wallace-Tree Carry-Save Adder (CSA) compression that cuts gate latency from O(N) to O(log N).

  ⏱️ Chapters & Timestamps:
  0:00 - The GEMM Scaling Crisis: 60M Multiplies per Token
  0:50 - Binary Long-Multiplication & 2N Bit Growth
  1:50 - Inside Silicon: 64 Bit-Level AND Gates & Baugh-Wooley Signed Trap
  2:50 - Wallace-Tree Reduction: 3:2 CSA Compression in O(log N)
  3:50 - Architectural Checkpoint: Why -128 × -128 Needs 16 Bits
  4:35 - Synthesizable RTL (rtl/multiplier_int8.sv) & Pre-Silicon Verification

  #MachineLearningHardware #WallaceTree #BoothMultiplier #SystemVerilog #TensorCore #ChipDesign
  ```
* **SEO Tags:** `Wallace Tree multiplier, Binary multiplication hardware, Baugh Wooley algorithm, Carry Save Adder, GEMM acceleration, Tensor Core silicon, INT8 quantization`

---

### 4. Lab 02: Accumulator Headroom & The MAC Unit
* **YouTube Title:** *Accumulator Headroom Math: Why 16-Bit Multipliers Need 32-Bit Accumulators*
* **Alternative Title:** *The Zero-Extension Disaster: Designing the Pipelined MAC Unit*
* **Thumbnail Concept:**
  * **Visual:** A transparent silicon accumulator tank bursting open with glowing cyan liquid pouring over the top at "DROP 3", contrasted with a massive 32-bit tank with green headroom space.
  * **Text Hook:** `16-BIT REGISTER OVERFLOW!` (Red & Cyan).
* **YouTube Description:**
  ```markdown
  Every artificial neural network reduces to Multiply-Accumulate (MAC) units. But when multiplying two 8-bit numbers produces 16 bits, how wide must the accumulator register be when summing K=4096 dot products?
  
  See why 16-bit accumulators overflow on just the 3rd product, how log2(K) dictates bit growth headroom, and the fatal difference between Zero-Extension (which corrupts -5 into +65,531) and Sign-Extension in synthesizable SystemVerilog.

  ⏱️ Chapters & Timestamps:
  0:00 - The Dot-Product Accumulation Crisis in Neural Networks
  0:50 - The Bursting 16-Bit Register Capacity Tank
  1:50 - Sign-Extension vs. Zero-Extension Hardware Disaster
  2:50 - Inside the MAC Datapath: 32-Bit Fluid Accumulation Gauge
  3:50 - Architectural Checkpoint: Maximum Accumulation Length (K)
  4:30 - Synthesizable RTL (rtl/mac_unit.sv) & Cocotb Verification

  #MACUnit #ComputerArchitecture #DigitalDesign #FPGA #ASIC #DotProduct #HardwareAI
  ```
* **SEO Tags:** `MAC unit architecture, Accumulator bit growth, Sign extension vs zero extension, Multiply Accumulate, Deep learning accelerator, Digital arithmetic`

---

### 5. Lab 03: Weight-Stationary Processing Element (PE)
* **YouTube Title:** *The 1,000x Memory Energy Wall: Inside the Weight-Stationary PE*
* **Alternative Title:** *Why Google TPUs Don't Move Weights: Spatial Silicon Computing*
* **Thumbnail Concept:**
  * **Visual:** Energy bar chart comparing DRAM (giant red bar: 200 pJ) vs MAC arithmetic (tiny green dot: 0.2 pJ). Overlay of a golden Weight-Stationary PE cell with horizontal cyan activations and vertical green partial sums.
  * **Text Hook:** `THE 1,000x ENERGY WALL` (Red & Gold).
* **YouTube Description:**
  ```markdown
  In modern computer science, we analyze algorithmic Big-O complexity. But in silicon physics, wire distance and energy dissipation dictate everything. Reading one byte from DRAM takes 200 picojoules; computing an INT8 MAC takes 0.2 picojoules: a 1,000x energy penalty!
  
  This video breaks down the architecture of the Weight-Stationary Processing Element (PE): why weights are locked into local flip-flops once, how activations stream horizontally, sums accumulate vertically, and how neighbor-only wiring enables 1+ GHz tensor engines.

  ⏱️ Chapters & Timestamps:
  0:00 - The Von Neumann Bottleneck: CPUs Stalled on Memory
  0:50 - Physical Silicon Limits: The 1,000x Memory Energy Wall
  1:50 - Inside the Weight-Stationary Processing Element
  2:50 - Dual-Phase Operation: Preload vs Streaming Execution
  3:55 - Architectural Checkpoint: Calculating DRAM Energy Savings
  4:40 - Synthesizable RTL (rtl/pe.sv) & Waveform Verification

  #GoogleTPU #MemoryWall #SystolicArray #HardwareArchitecture #Semiconductors #DeepLearning
  ```
* **SEO Tags:** `Weight stationary PE, Von Neumann bottleneck, Memory wall AI, Google TPU architecture, Processing Element datapath, Systolic computing, AI chips`

---

### 6. Lab 04: The 2D Systolic Array Matrix Multiplier
* **YouTube Title:** *Inside the Google TPU: 2D Systolic Wavefronts & Activation Skewing*
* **Alternative Title:** *How Systolic Arrays Compute Matrix Math 100x Faster Than CPUs*
* **Thumbnail Concept:**
  * **Visual:** High-contrast 2x2 PE systolic grid with diagonal green wavefront lines rippling across cells, showing concrete numbers [1, 2] entering and partial sums [19, 22] flowing out.
  * **Text Hook:** `GOOGLE TPU SILICON WAVEFRONT` (Neon Cyan & Green).
* **YouTube Description:**
  ```markdown
  How do Google TPUs and NVIDIA Tensor Cores multiply massive matrices without choking memory buses? The answer is Spatial Systolic Computing.
  
  Trace the 2D Systolic Wavefront clock cycle by clock cycle: understand why simultaneous input entry produces corrupted garbage, how D Flip-Flop activation skew registers restore mathematical harmony, and verify a complete 2x2 matrix dot product using real numbers.

  ⏱️ Chapters & Timestamps:
  0:00 - From PyTorch to Silicon: Why LLMs Demand Custom Hardware
  0:50 - CPU vs GPU vs TPU: The 1,000x Physical Memory Energy Wall
  1:45 - Inside the Weight-Stationary PE Datapath
  2:40 - The Activation Skewing Paradox & The 2D Wavefront (Cycles T0..T4)
  4:05 - Architectural Checkpoints & Mathematical Challenge
  4:50 - Pre-Silicon Verification (rtl/systolic_array.sv) & TPU Scale

  #GoogleTPU #SystolicArray #HardwareDesign #MatrixMultiplication #TensorCore #Verilog #AIChips
  ```
* **SEO Tags:** `Systolic array tutorial, Google TPU architecture, Activation skewing, 2D wavefront, Matrix multiplication hardware, Tensor Core SystemVerilog`

---

### 7. Lab 05: Hardware Square Root Unit for Scaled Attention
* **YouTube Title:** *Attention Scaling in Silicon: Hardware Digit-by-Digit Square Root*
* **Alternative Title:** *Why Transformers Need Hardware Square Roots (1/sqrt(d_k))*
* **Thumbnail Concept:**
  * **Visual:** PyTorch attention formula `Q @ K.T / sqrt(d_k)` with an arrow pointing to a glowing silicon shift register extracting root bits one by one.
  * **Text Hook:** `WHY ATTENTION REQUIRES SQRT` (Cyan & White).
* **YouTube Description:**
  ```markdown
  In Transformer self-attention, dot products scale with embedding dimension d_k. Without dividing by sqrt(d_k), variance explodes to 128, Softmax saturates into a dead needle, and gradients vanish to zero!
  
  Silicon chips have no math.sqrt() function, and floating-point dividers take 50+ cycles. Discover the Non-Restoring Digit Recurrence Algorithm: an unrolled combinational pipeline that extracts 1 bit of root per stage using pure integer shift-and-subtract operations.

  ⏱️ Chapters & Timestamps:
  0:00 - The Attention Variance Crisis: Softmax Gradient Collapse
  0:50 - The Silicon Dilemma: Why FPUs are Too Slow
  1:45 - The Digit-by-Digit Non-Restoring Algorithm
  2:55 - Cycle Trace: Extracting sqrt(64) = 8 in Silicon
  4:00 - Architectural Checkpoint: Calculating Root for d_k = 128
  4:35 - Synthesizable Silicon RTL (rtl/sqrt.sv) & Cocotb Verification

  #TransformerArchitecture #HardwareSquareRoot #SelfAttention #SystemVerilog #FlashAttention #AI
  ```
* **SEO Tags:** `Non restoring square root, Transformer attention scaling, Hardware sqrt SystemVerilog, Digit recurrence algorithm, Scaled dot product attention`

---

### 8. Lab 06: Safe Softmax & FlashAttention
* **YouTube Title:** *Why Softmax Blows Up: Safe Softmax & FlashAttention in Silicon*
* **Alternative Title:** *Taming the e^50 Explosion: Designing the Hardware Softmax Engine*
* **Thumbnail Concept:**
  * **Visual:** A red exponential curve rocketing off the screen with `e^50 = NaN` warning, alongside a clean green grounded chart showing `Delta = x - max(X) <= 0`.
  * **Text Hook:** `THE e^50 OVERFLOW TRAP` (Red & Green).
* **YouTube Description:**
  ```markdown
  When attention logits reach +50, computing raw exponentials explodes to 5 sextillion—overflowing 64-bit registers and yielding NaN.
  
  Learn how Safe Softmax mathematically clamps exponents by subtracting the running maximum (x_i - max(X)), inspect the 3-Pass Silicon Datapath with a Q0.8 lookup ROM, and discover the FlashAttention breakthrough: Online Softmax that tiles compute into SRAM without materializing N×N matrices in DRAM.

  ⏱️ Chapters & Timestamps:
  0:00 - The Softmax Numerical Explosion in Transformers
  0:50 - The Safe Softmax Mathematical Invariant (Δ_i ≤ 0)
  1:45 - The 3-Pass Silicon Datapath Architecture
  2:55 - The FlashAttention Breakthrough: Online Softmax Tiling
  4:00 - Architectural Checkpoint: The 3-Logit Challenge
  4:40 - Synthesizable Silicon RTL (rtl/softmax.sv) & Cocotb Verification

  #FlashAttention #Softmax #DeepLearningHardware #TransformerHardware #ASIC #SystemVerilog
  ```
* **SEO Tags:** `Safe Softmax hardware, FlashAttention architecture, Online Softmax algorithm, Exponential LUT, Transformer ASIC, Numerical stability AI`

---

### 9. Lab 07: Fast Reciprocal Square Root (RSQRT) for RMSNorm
* **YouTube Title:** *LLaMA-3 RMSNorm: Fast Reciprocal Square Root (1/sqrt(x)) in Silicon*
* **Alternative Title:** *Zero Dividers: How Hardware Computes 1/sqrt(x) in 4 Nanoseconds*
* **Thumbnail Concept:**
  * **Visual:** Exploding red vectors outside a glowing green unit circle snapping sharply onto the unit circumference, with the Newton-Raphson hardware formula below.
  * **Text Hook:** `4.6ns FAST RSQRT` (Green & Cyan).
* **YouTube Description:**
  ```markdown
  Why did LLaMA 3, Mistral, and Gemma abandon LayerNorm in favor of RMSNorm? Because Root Mean Square Normalization eliminates mean computation—but still demands computing 1 / sqrt(x).
  
  In software, division takes 40 clock cycles. In custom silicon, we compute 1 / sqrt(x) in 4.6 nanoseconds using ZERO dividers! Discover the hybrid architecture: a 32-entry Seed ROM providing a coarse initial guess, refined to <0.8% error by a single Newton-Raphson multiplier iteration in Q8.8 fixed point.

  ⏱️ Chapters & Timestamps:
  0:00 - The LLaMA 3 RMSNorm Revolution: Eliminating Division Loops
  0:50 - Visualizing RMSNorm: Snapping Vectors onto the Unit Circle
  1:45 - Hybrid Silicon Architecture: Seed ROM + Newton-Raphson
  2:55 - Precision Convergence Trace: 1 / sqrt(4.0) = 0.5
  4:00 - Architectural Checkpoint: The Q8.8 Binary Fixed-Point Format
  4:35 - Synthesizable RTL (rtl/rsqrt.sv) & Verification

  #RMSNorm #LLaMA3 #FastInverseSquareRoot #NewtonRaphson #AIHardware #SystemVerilog #ASIC
  ```
* **SEO Tags:** `RMSNorm hardware, Fast inverse square root, Newton Raphson silicon, LLaMA 3 architecture, Reciprocal square root Verilog, Hardware normalization`

---

### 10. Lab 08: Exponential SFU for SwiGLU / SiLU Activations
* **YouTube Title:** *SwiGLU & SiLU Activation: The Base-2 Exponentiation Silicon Trick*
* **Alternative Title:** *How AI Chips Compute e^x in 3 Nanoseconds (Barrel Shifter + ROM)*
* **Thumbnail Concept:**
  * **Visual:** A neon laser beam slicing a binary register into Cyan (Integer `2^I` barrel shift) and Purple (Fraction `2^F` lookup ROM), with `e^x = 2^I * 2^F` glowing above.
  * **Text Hook:** `THE BASE-2 EXPONENTIAL TRICK` (Neon Purple & Cyan).
* **YouTube Description:**
  ```markdown
  Over 60% of all FLOPs in modern LLMs (LLaMA 3, Gemma, Mistral) occur in non-linear SwiGLU Feed-Forward Networks. But evaluating e^x using Taylor series expansion requires dozens of multipliers and massive latency.
  
  Uncover the elegant Base-2 Silicon Trick: converting e^x to 2^(x · log2(e)), laser-slicing the fixed-point number into an integer I and fraction F. 2^I is a free barrel bit-shift (0 gates), and 2^F is a tiny 16-entry lookup ROM! Celebrate the completion of the full 10-lab Hardware AI Acceleration curriculum.

  ⏱️ Chapters & Timestamps:
  0:00 - The SwiGLU / SiLU Challenge in Frontier LLMs
  0:50 - The Base-2 Silicon Secret: Laser-Slicing into 2^I × 2^F
  1:50 - Combinational Exponential SFU Datapath
  3:00 - Real Number Walkthrough: Computing e^(1.0) = 2.718
  4:05 - Architectural Checkpoint: Negative Exponents & Arithmetic Right Shift
  4:40 - Synthesizable Silicon RTL (rtl/exp2_sfu.sv) & Full Tapeout Celebration!

  #SwiGLU #SiLU #SpecialFunctionUnit #BarrelShifter #LLaMA3 #AIHardware #Semiconductors #ASIC
  ```
* **SEO Tags:** `SwiGLU hardware acceleration, Exponential SFU, Base 2 exponentiation trick, Barrel shifter Verilog, SiLU activation ASIC, LLM hardware design`
