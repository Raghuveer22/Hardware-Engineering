# 🔬 Hardware AI Acceleration Labs Curriculum

Welcome to the hands-on **Hardware AI Acceleration & Pre-Silicon Engineering Labs**.

This curriculum is structured step-by-step for **learning, content creation, and portfolio demonstrations**.

---

## 🗺️ Curriculum Roadmap

```
  ┌─────────────────────────────────────────────────────────────┐
  │ Lab 01: Parameterized Signed Multiplier                     │
  │ • RTL: rtl/multiplier_int8.sv                               │
  │ • Verification: labs/test_multiplier.py                     │
  │ • Schematic: schematics/multiplier_int8.svg                 │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │ Lab 02: Multiply-Accumulate (MAC) Unit                      │
  │ • RTL: rtl/mac_unit.sv                                      │
  │ • Verification: labs/test_mac.py                            │
  │ • Schematic: schematics/mac_unit.svg                        │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │ Lab 03: Weight-Stationary Processing Element (PE)           │
  │ • RTL: rtl/pe.sv                                            │
  │ • Verification: tests/test_pe.py                            │
  │ • Schematic: schematics/pe.svg (48 D-Flip-Flop Registers)   │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │ Lab 04: 2D Systolic Matrix Multiplier                       │
  │ • RTL: rtl/systolic_array.sv                                │
  │ • Verification: tests/test_systolic_array.py vs. NumPy      │
  │ • Interactive Visualizer: visualizer/index.html             │
  └─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Unified Tooling Commands

### 1. Run All Python Testbenches
```bash
source .venv/bin/activate
python labs/run_lab.py --lab all
```

### 2. Run Yosys Logic Synthesis & Export Schematic Images
```bash
python3 synthesis/synthesize.py --top all
```
* Generates gate-level `.svg` and `.png` diagrams inside [`schematics/`](../schematics/).
* Computes exact gate counts, cell types (`$_AND_`, `$_XOR_`, `$_DFFE_`), and register bit-widths.

### 3. Launch Interactive Visualizer
```bash
python3 visualizer/serve.py
```
