#!/usr/bin/env python3
"""
==============================================================================
File: visualizer/generate_trace.py
Description: Simulates the Systolic Array cycle-by-cycle and exports a JSON
             trace containing the exact internal state of every PE, wire,
             and boundary port at every clock cycle.
==============================================================================
"""

import json
import numpy as np
from pathlib import Path

def simulate_and_export_trace(A, W, output_file="trace.json"):
    """
    Simulates a 2D weight-stationary systolic array with activation skewing.
    Exports full cycle-by-cycle register and wire states to JSON.
    """
    ROWS, K_dim = W.shape
    M_batch, K_act = A.shape
    COLS = W.shape[1]

    assert K_dim == K_act, f"Matrix dimension mismatch: A is ({M_batch}x{K_act}), W is ({ROWS}x{COLS})"
    
    C_golden = (A @ W).tolist()

    # Hardware state tracking structures
    # PEs internal registers:
    # pe_weights[r][c], pe_acts[r][c], pe_sums[r][c]
    pe_weights = np.zeros((ROWS, COLS), dtype=int)
    pe_acts = np.zeros((ROWS, COLS), dtype=int)
    pe_sums = np.zeros((ROWS, COLS), dtype=int)

    # Skew delay pipelines for each row: row r has depth r
    skew_pipes = [ [0] * r for r in range(ROWS) ]

    # History of each cycle
    cycles_data = []

    # Phase 1: Weight Loading (takes ROWS cycles)
    # Weights shift down each column from bottom row (ROWS-1) to top row 0
    for load_step in range(ROWS):
        r_load = ROWS - 1 - load_step
        current_weight_inputs = [int(W[r_load, c]) for c in range(COLS)]
        
        # Shift down in hardware: row r takes from row r-1, row 0 takes from input
        new_weights = pe_weights.copy()
        for r in range(ROWS - 1, 0, -1):
            new_weights[r, :] = pe_weights[r - 1, :]
        new_weights[0, :] = current_weight_inputs
        pe_weights = new_weights

        snapshot = {
            "cycle": load_step,
            "phase": "WEIGHT_LOAD",
            "description": f"Loading row {r_load} of weight matrix into column inputs",
            "weight_load_en": 1,
            "en": 0,
            "weights_in": current_weight_inputs,
            "activations_in": [0] * ROWS,
            "act_skewed": [0] * ROWS,
            "pe_grid": [
                [
                    {
                        "r": r,
                        "c": c,
                        "weight": int(pe_weights[r, c]),
                        "act_in": 0,
                        "act_reg": int(pe_acts[r, c]),
                        "sum_in": 0,
                        "sum_reg": int(pe_sums[r, c]),
                        "mac_calc": f"{pe_sums[r,c]} + ({pe_acts[r,c]} * {pe_weights[r,c]})"
                    }
                    for c in range(COLS)
                ]
                for r in range(ROWS)
            ],
            "sum_out_bot": [0] * COLS,
            "activations_out": [0] * ROWS
        }
        cycles_data.append(snapshot)

    # Phase 2: Streaming Activations & Compute
    total_compute_cycles = M_batch + ROWS + COLS + 2
    
    for comp_step in range(total_compute_cycles):
        cycle_idx = ROWS + comp_step
        
        # Raw activations fed this cycle
        if comp_step < M_batch:
            raw_act_in = [int(A[comp_step, r]) for r in range(ROWS)]
        else:
            raw_act_in = [0] * ROWS

        # Compute skew outputs for current cycle
        skewed_act = [0] * ROWS
        skewed_act[0] = raw_act_in[0]
        for r in range(1, ROWS):
            if len(skew_pipes[r]) > 0:
                skewed_act[r] = skew_pipes[r][-1] # output is last stage
            else:
                skewed_act[r] = raw_act_in[r]

        # Interconnect combinational values for this cycle
        # h_act[r][c] enters PE(r,c) from left
        h_act = np.zeros((ROWS, COLS + 1), dtype=int)
        for r in range(ROWS):
            h_act[r, 0] = skewed_act[r]
            for c in range(COLS):
                h_act[r, c + 1] = pe_acts[r, c]

        # v_sum[r][c] enters PE(r,c) from top
        v_sum = np.zeros((ROWS + 1, COLS), dtype=int)
        for c in range(COLS):
            v_sum[0, c] = 0 # Top boundary tied to 0
            for r in range(ROWS):
                v_sum[r + 1, c] = pe_sums[r, c]

        # Calculate what each PE computes this cycle
        pe_snapshot_grid = []
        for r in range(ROWS):
            row_snap = []
            for c in range(COLS):
                ain = int(h_act[r, c])
                sin = int(v_sum[r, c])
                w = int(pe_weights[r, c])
                mac_out = sin + (ain * w)
                row_snap.append({
                    "r": r,
                    "c": c,
                    "weight": w,
                    "act_in": ain,
                    "act_reg": int(pe_acts[r, c]),
                    "sum_in": sin,
                    "sum_reg": int(pe_sums[r, c]),
                    "mac_out": mac_out,
                    "mac_calc": f"{sin} + ({ain} * {w}) = {mac_out}"
                })
            pe_snapshot_grid.append(row_snap)

        snapshot = {
            "cycle": cycle_idx,
            "phase": "COMPUTE",
            "compute_step": comp_step,
            "description": f"Compute cycle {comp_step}: streaming activations and propagating partial sums",
            "weight_load_en": 0,
            "en": 1,
            "weights_in": [0] * COLS,
            "activations_in": raw_act_in,
            "act_skewed": skewed_act,
            "pe_grid": pe_snapshot_grid,
            "sum_out_bot": [int(pe_sums[ROWS - 1, c]) for c in range(COLS)],
            "activations_out": [int(pe_acts[r, COLS - 1]) for r in range(ROWS)]
        }
        cycles_data.append(snapshot)

        # Update sequential registers for NEXT clock edge:
        # 1. Update Skew shift registers
        for r in range(1, ROWS):
            if len(skew_pipes[r]) > 1:
                for d in range(len(skew_pipes[r]) - 1, 0, -1):
                    skew_pipes[r][d] = skew_pipes[r][d - 1]
            if len(skew_pipes[r]) > 0:
                skew_pipes[r][0] = raw_act_in[r]

        # 2. Update PE registers
        new_acts = np.zeros((ROWS, COLS), dtype=int)
        new_sums = np.zeros((ROWS, COLS), dtype=int)
        for r in range(ROWS):
            for c in range(COLS):
                new_acts[r, c] = h_act[r, c]
                new_sums[r, c] = pe_snapshot_grid[r][c]["mac_out"]
        pe_acts = new_acts
        pe_sums = new_sums

    # Full trace structure
    trace_payload = {
        "dimensions": {
            "ROWS": ROWS,
            "COLS": COLS,
            "M_BATCH": M_batch
        },
        "matrices": {
            "A": A.tolist(),
            "W": W.tolist(),
            "C_golden": C_golden
        },
        "cycles": cycles_data
    }

    out_p = Path(output_file)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w") as f:
        json.dump(trace_payload, f, indent=2)

    print(f"✅ Generated simulation trace with {len(cycles_data)} cycles -> {output_file}")
    return trace_payload

if __name__ == "__main__":
    # Default 4x4 matrix
    np.random.seed(42)
    A = np.random.randint(-10, 10, size=(4, 4), dtype=int)
    W = np.random.randint(-10, 10, size=(4, 4), dtype=int)
    
    script_dir = Path(__file__).resolve().parent
    simulate_and_export_trace(A, W, script_dir / "trace.json")
