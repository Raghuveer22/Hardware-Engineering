# Original User Request

## Initial Request — 2026-10-02T18:08:56Z

Comprehensive overhaul of the Hardware AI Acceleration curriculum and animation suite: modernize the educational animations in `animations/` away from static PowerPoint slide presentations into dynamic, kinetic silicon visualizations; expand the technical depth and hardware-software co-design rigor across the lab content; and audit all curriculum documents for flawless markdown, mathematical typography, and diagrammatic formatting.

Working directory: /Users/posamokshith/Downloads/Hardware Engineering
Integrity mode: development

## Requirements

### R1. Dynamic Silicon Animations (Eliminate PowerPoint Aesthetic)
- Overhaul all animation scenes in `animations/` (`scene_lab00_prep.py` through `scene_lab08_exp2_sfu.py`) to eliminate slide-deck presentation cards, static bulleted lists, and static code/metric text boxes.
- Replace static presentations with kinetic hardware visualizations: continuous clock pulses, animated wire signals, moving data packets, weight-stationary register latching, systolic wavefront rippling, and mathematical SFU transformations.
- Maintain seamless integration with `animations/render_all.py` for both preview (`-ql`) and broadcast production rendering.

### R2. Technical Content Depth & Hardware-Software Co-Design Rigor
- Significantly deepen the curriculum content in the lab guides (`labs/slides/`) and narration/learning materials:
  - Deep-dive into physical hardware trade-offs: critical path timing, silicon area ($O(N^2)$ multiplier scaling vs. adder trees), clock cycle latencies, and throughput.
  - Elucidate the pre-silicon memory energy hierarchy: off-chip DRAM vs on-chip SRAM vs local register files, and exact pJ/bit movement costs.
  - Expand mathematical rigor and numerical edge cases: signed two's complement saturation mechanics, 32-bit accumulator headroom proofs, IEEE FP vs fixed-point quantization, LUT interpolation, and RMSNorm/Softmax numerical stability.
  - Bridge every hardware module directly to real-world AI accelerators (Google TPU v1-v5, NVIDIA Tensor Cores, Apple Neural Engine) and ML frameworks (PyTorch, FlashAttention, vLLM).

### R3. Comprehensive Formatting & Document Polish
- Audit and standardize formatting across all lab guides (`labs/slides/*.md`), video scripts, and presentation materials:
  - Enforce clean, properly escaped KaTeX mathematical notation (e.g., inline `$...$` and display blocks `$$...$$`).
  - Standardize code block annotations, language identifiers, and syntax highlighting.
  - Validate and align Markdown tables, GitHub alert callouts (`[!NOTE]`, `[!IMPORTANT]`, `[!TIP]`), and ASCII/Mermaid architectural block diagrams.
  - Ensure all internal cross-links to RTL files (`rtl/*.sv`), Cocotb testbenches (`tests/`, `labs/`), and schematics are valid and properly relative-pathed.

## Acceptance Criteria

### Animation & Rendering Verification
- [ ] All animation scripts in `animations/scene_lab*.py` execute and render cleanly without Python/Manim errors under preview mode (`-ql`).
- [ ] Primary scenes feature continuous kinetic motion, moving data packets, and live register/waveform state changes rather than static bulleted slides.

### Content Depth & Completeness
- [ ] Every lab guide provides rigorous architectural explanations covering datapath structure, timing/cycle behavior, physical resource costs, and real-world ML compiler/hardware context.
- [ ] Numerical edge cases (overflow, rounding, saturation, bitwidth sizing proofs) are explicitly derived and mapped to SystemVerilog RTL implementation.

### Formatting & Structural Integrity
- [ ] Zero broken relative file links, malformed markdown tables, or unrendered KaTeX mathematical expressions across `labs/slides/` and `animations/`.
- [ ] All code snippets compile or correspond faithfully to the actual synthesizable RTL and Cocotb testbenches in the repository.

## Follow-up — 2026-10-02T19:16:44Z

The user has requested to continue. Please resume execution and drive the milestones to completion.

## Follow-up — 2026-10-02T19:24:45Z

USER GUIDANCE AND COURSE-CORRECTION:
1. Milestone 3 Formatting Scope: The user clarifies that "formatting" is NOT for Markdown document linting. It is specifically for the GENERATED RENDERING CONTENT of the Python files in animations/ (i.e. visual layout, typography, element alignment, math rendering, spacing, no text clipping/overlapping in the Manim video frames).
2. Dependency Flow: Once Milestone 2 finishes (deepened technical content, proofs, pJ/bit numbers, hardware architectures in labs/slides/), that in-depth content MUST BE UPDATED directly into the animations folder Python scripts (scene_lab*.py narration, on-screen formulas, and datapath visual depth).
Please update PROJECT.md, milestone definitions, and orchestrator instructions accordingly.
