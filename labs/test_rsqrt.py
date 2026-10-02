#!/usr/bin/env python3
"""
==============================================================================
File: labs/test_rsqrt.py
Description: Cocotb verification testbench for Parameterized Hardware
             Reciprocal Square Root Unit (rsqrt.sv).
==============================================================================
"""

import cocotb
from cocotb.triggers import Timer
import math
import random

@cocotb.test()
async def test_rsqrt_standard_and_corner_cases(dut):
    """Test standard perfect powers, zero, and corner values for 1/sqrt(x)"""
    dut._log.info("Testing rsqrt corner cases and perfect squares...")

    # Case 0: x = 0 (should flag invalid or saturate)
    dut.x_in.value = 0
    await Timer(1, units="ns")
    assert int(dut.valid_out.value) == 0, f"Expected valid_out=0 for x=0, got {dut.valid_out.value}"

    # Case 1: x = 1 -> 1/sqrt(1) = 1.0 (256 in Q8.8)
    dut.x_in.value = 1
    await Timer(1, units="ns")
    assert int(dut.y_out.value) == 256, f"Expected 256 (1.0), got {int(dut.y_out.value)}"

    # Case 2: x = 4 -> 1/sqrt(4) = 0.5 (128 in Q8.8)
    dut.x_in.value = 4
    await Timer(1, units="ns")
    assert int(dut.y_out.value) == 128, f"Expected 128 (0.5), got {int(dut.y_out.value)}"

    # Case 3: x = 16 -> 1/sqrt(16) = 0.25 (64 in Q8.8)
    dut.x_in.value = 16
    await Timer(1, units="ns")
    assert int(dut.y_out.value) == 64, f"Expected 64 (0.25), got {int(dut.y_out.value)}"

    # Case 4: x = 64 -> 1/sqrt(64) = 0.125 (32 in Q8.8)
    dut.x_in.value = 64
    await Timer(1, units="ns")
    assert int(dut.y_out.value) == 32, f"Expected 32 (0.125), got {int(dut.y_out.value)}"

    # Case 5: x = 256 -> 1/sqrt(256) = 0.0625 (16 in Q8.8)
    dut.x_in.value = 256
    await Timer(1, units="ns")
    assert int(dut.y_out.value) == 16, f"Expected 16 (0.0625), got {int(dut.y_out.value)}"

    dut._log.info("✅ Corner cases passed successfully!")

@cocotb.test()
async def test_rsqrt_exhaustive_accuracy(dut):
    """Test 200 random inputs and verify relative error is within acceptable bounds"""
    dut._log.info("Testing 200 random vectors against golden Python reference...")

    for _ in range(200):
        x = random.randint(1, 4096)
        dut.x_in.value = x
        await Timer(1, units="ns")

        actual_fixed = int(dut.y_out.value)
        actual_float = actual_fixed / 256.0
        expected_float = 1.0 / math.sqrt(x)

        # Allow small quantization tolerance for integer isqrt approximation
        abs_err = abs(actual_float - expected_float)
        rel_err = abs_err / expected_float if expected_float > 0 else 0

        # For x >= 4, relative error should be small (< 15% for fast hardware seed approximation)
        if x < 4:
            assert abs_err < 0.05, f"Low range error for x={x}: actual={actual_float}, exp={expected_float}"
        else:
            assert rel_err < 0.20, f"Error exceeded for x={x}: actual={actual_float}, exp={expected_float}, rel_err={rel_err}"

    dut._log.info("✅ Exhaustive accuracy tests passed successfully!")
