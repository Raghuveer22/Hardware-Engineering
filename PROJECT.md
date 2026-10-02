# Project: Hardware AI Acceleration Curriculum & Animation Suite Overhaul

## Architecture
The repository consists of four interconnected layers:
1. **Synthesizable RTL Core (`rtl/`)**: Hardware designs for deep learning compute primitives parameterized in SystemVerilog (Signed Adder with Saturation, INT8 Multiplier, MAC Unit, Weight-Stationary Processing Element, 2D Systolic Array, Restoring Sqrt Unit, Safe Softmax, Reciprocal Sqrt SFU, Exponential Base-2 SFU).
2. **Pre-Silicon Verification Suite (`tests/`, `labs/`)**: Python Cocotb testbenches executing against Icarus Verilog simulation with randomized vectors, signed two's complement corner cases, and numerical error assertions.
3. **Hardware-Software Co-Design Curriculum (`labs/slides/`)**: Pedagogical and technical lab guides detailing microarchitectures, critical path timing, silicon area footprints, pre-silicon memory energy hierarchies (pJ/bit), formal mathematical proofs, and industry accelerator mappings (Google TPU v1-v5, NVIDIA Tensor Cores, Apple Neural Engine, PyTorch Triton, vLLM).
4. **Kinetic Silicon Animation Suite (`animations/`)**: Manim Community v0.21.0 video generation framework featuring modular standard-cell components (`KineticClock`, `LiveOscilloscope`, `SiliconWire`, `LaserPacketStream`, `SiliconCameraRig`, `BitRegister`, arithmetic dials, and accumulator tanks) executed via `animations/render_all.py`.

---

## Feature Inventory

Every feature discovered in the survey phase is recorded below and assigned to a milestone:

| # | Feature | Description | Milestone | Source |
|---|---|---|---|---|
| F01 | Scene 00-Prep Kinetic Modernization | Replace static slides with live PC stepping vs concurrent gate array; D-FF transmission gates and master/slave latches | M1 | Survey Anim |
| F02 | Scene 00 Saturation Kinetic Modernization | Live 8-bit ripple adder datapath with sign flip to -106; active 3:1 saturation MUX clamping with screen shake | M1 | Survey Anim |
| F03 | Scene 01 Multiplier Kinetic Modernization | Expanding silicon die footprint with thermal glow; active 64-bus AND matrix; Wallace tree Carry-Save reduction dots | M1 | Survey Anim |
| F04 | Scene 02 MAC Unit Kinetic Modernization | Laser sign-extension duplication vs zero-extension spike; cracking liquid tank widget on overflow | M1 | Survey Anim |
| F05 | Scene 03 PE Kinetic Modernization | Physical silicon energy floorplan (200 pJ DRAM vs 0.2 pJ MAC); metallic weight lock and orthogonal streaming | M1 | Survey Anim |
| F06 | Scene 04 Systolic Array Modernization | Physical unskewed collision demo on 2x2 grid (red clash); skewed wavefront diagonal rippling; live oscilloscope | M1 | Survey Anim |
| F07 | Scene 05 Sqrt Kinetic Modernization | Softmax variance collapse visual; unrolled 8-stage digit-recurrence pipeline with shift-subtract slices | M1 | Survey Anim |
| F08 | Scene 06 Softmax Kinetic Modernization | Dynamic rocket overflow; 3-pass hardware streaming pipeline; FlashAttention on-chip SRAM tiling | M1 | Survey Anim |
| F09 | Scene 07 RSQRT Kinetic Modernization | Unit circle activation projection; 32-entry seed ROM lookup; Newton-Raphson multiplier iteration error plunge | M1 | Survey Anim |
| F10 | Scene 08 Exp2 SFU Modernization | Laser bit-slicer into integer/fraction; dynamic barrel shifter crossbar; full-chip accelerator core visual | M1 | Survey Anim |
| F11 | Preview Mode CLI Compatibility | Ensure all scenes render cleanly with `animations/render_all.py --low` (`-ql`) with 0 errors | M1 | Survey Anim |
| F12 | Lab 00-Prep Co-Design Depth | Add pJ/bit memory energy hierarchy table; flip-flop setup/hold/metastability equations; PCIe/DMA/MMIO mappings | M2 | Survey Curric |
| F13 | Lab 00 Adder Saturation Rigor | Add Two's Complement Overflow proof ($V=C_{in} \oplus C_{out}$); RCA vs CLA vs Kogge-Stone timing/area table; TPU adder trees | M2 | Survey Curric |
| F14 | Lab 01 Multiplier Co-Design Rigor | Add $O(N^2)$ silicon scaling proof; Radix-4 Booth encoding; Wallace/Dadda CSA reduction tree; Tensor Core mapping | M2 | Survey Curric |
| F15 | Lab 02 MAC Unit Headroom Proof | Formal proof of 32-bit accumulator headroom ($K \le 131,072$); combinational vs pipelined $F_{max}$; Ampere/Hopper MMA | M2 | Survey Curric |
| F16 | Lab 03 PE Spatial Dataflow Rigor | Add WS vs OS vs IS taxonomy table; DRAM vs SRAM batch energy reduction math; 48 DFF PE budget; Apple ANE mapping | M2 | Survey Curric |
| F17 | Lab 04 Systolic Array Math Rigor | Mathematical proof of wavefront arrival ($T = i+j+ROWS-1$); matrix tiling & SRAM double-buffering; TMA & Triton GEMM | M2 | Survey Curric |
| F18 | Lab 05 Sqrt Variance Proof | Mathematical proof of attention dot-product variance ($\text{Var}(q^T k) = d_k$); vanishing gradient proof; digit recurrence | M2 | Survey Curric |
| F19 | Lab 06 Softmax & FlashAttention Rigor | Proof of softmax shift invariance; FlashAttention-1/2/3 online softmax rescaling derivation; Blackwell warp groups | M2 | Survey Curric |
| F20 | Lab 07 RSQRT & RMSNorm Rigor | Fast Inverse Square Root Newton-Raphson derivation; RMSNorm vs LayerNorm gate comparison; $x=8$ seed gap analysis | M2 | Survey Curric |
| F21 | Lab 08 Exp2 SFU Rigor | Base-2 decomposition error derivation; SwiGLU / SiLU hardware datapath diagram; Q8.8 dynamic range saturation ($x \approx 5.545$) | M2 | Survey Curric |
| F22 | KaTeX Currency Delimiter Escaping | Escape currency dollar signs (`\$50M`, `\$100M`, `\$300k`) in README and guides to prevent false KaTeX math mode triggers | M3 | Spec Miner |
| F23 | Code Block Syntax Standardization | Add `text` language tags to 24 ASCII diagrammatic and architectural code blocks for markdownlint MD040 compliance | M3 | Spec Miner |
| F24 | Relative Link Polish | Upgrade unlinked backtick paths in `SYSTOLIC_ARRAY_VIDEO_SCRIPT.md` to active relative links; verify 115 links | M3 | Spec Miner |
| F25 | Full Test & Render Acceptance | Run all animation renders (`--low`), Cocotb testbenches, and conduct independent forensic audit | M4 | Survey Global |

---

## Milestones

| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| **M1** | Dynamic Silicon Animations Overhaul | `animations/scene_lab00_prep.py` through `animations/scene_lab08_exp2_sfu.py`, `render_all.py` | None | IN_PROGRESS (c32ca710-b184-4f28-8b5d-1a0e40b75df5) |
| **M2** | Technical Depth & Co-Design Rigor | `labs/slides/lab00_prep` through `labs/slides/lab08_exponential_sfu` | None | IN_PROGRESS (a5626f37-5d1e-4261-a559-569e9ca91af7) |
| **M3** | Formatting, KaTeX & Document Polish | `labs/slides/*.md`, `animations/*.md`, `README.md` | None | PLANNED |
| **M4** | E2E Verification & Forensic Integrity Audit | Full suite validation (`render_all.py --low`, Cocotb tests, KaTeX audit, Forensic Auditor) | M1, M2, M3 | PLANNED |

---

## Interface Contracts

### Animations (`animations/`) $\leftrightarrow$ Runner (`animations/render_all.py`)
- Every scene file `scene_lab*.py` must define a primary scene class inheriting from `MovingCameraScene` or `SiliconCameraRig` or `Scene`.
- Command invocation `.venv/bin/python animations/render_all.py --low <lab_id>` must render cleanly with exit code 0.
- All scene animations must use Manim Community v0.21.0 compatible APIs; preview output saved to `media/videos/<stem>/480p15/*.mp4`.

### Lab Slide Guides (`labs/slides/`) $\leftrightarrow$ Hardware RTL (`rtl/`) & Cocotb (`tests/`, `labs/`)
- Every RTL module referenced in `labs/slides/` must match actual port names, parameter defaults (`DATA_WIDTH=8`, `ACC_WIDTH=32`), and synthesis registers in `rtl/*.sv`.
- Relative links from `labs/slides/` to RTL must use `../../rtl/<module>.sv`.
- Relative links from `labs/slides/` to testbenches must use `../<test>.py` (local lab tests) or `../../tests/<test>.py` (global testbenches).
- Mathematical notation must use standard KaTeX `$ ... $` for inline and `$$ ... $$` for display blocks. Currency symbols must be escaped `\$`.

---

## Code Layout

- `animations/`: Animation scene scripts (`scene_lab00_prep.py` to `scene_lab08_exp2_sfu.py`), CLI runner (`render_all.py`), theme configuration (`theme.py`), and standard-cell components (`components/`).
- `labs/slides/`: Markdown curriculum slide guides (`lab00_prep_hardware_thinking_primer.md` through `lab08_exponential_sfu_slides.md`).
- `rtl/`: Synthesizable SystemVerilog modules (`adder.sv`, `multiplier_int8.sv`, `mac_unit.sv`, `pe.sv`, `systolic_array.sv`, `sqrt.sv`, `softmax.sv`, `rsqrt.sv`, `exp2_sfu.sv`).
- `tests/`: Cocotb integration testbenches.
- `labs/`: Lab runner (`run_lab.py`) and lab-specific testbenches.
- `schematics/`: Yosys-synthesized SVG logic schematics.
