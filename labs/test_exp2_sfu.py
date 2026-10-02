#!/usr/bin/env python3
"""
==============================================================================
File: labs/test_exp2_sfu.py
Description: Cocotb verification testbench for Parameterized Hardware
             Exponential SFU (exp2_sfu.sv).
==============================================================================
"""

import cocotb
from cocotb.triggers import Timer
import math
import random

@cocotb.test()
async def test_exp2_base2_mode(dut):
    """Test 2^x mode for integer and fractional powers"""
    dut._log.info("Testing 2^x base-2 mode...")
    dut.mode_e.value = 0 # 2^x mode

    # 2^0 = 1.0 (256 in Q8.8)
    dut.x_in.value = 0
    await Timer(1, units="ns")
    assert int(dut.y_out.value) == 256, f"Expected 256 for 2^0, got {int(dut.y_out.value)}"

    # 2^1 = 2.0 (512 in Q8.8) -> Q4.4 input for 1 is 16 (0x10)
    dut.x_in.value = 16
    await Timer(1, units="ns")
    assert int(dut.y_out.value) == 512, f"Expected 512 for 2^1, got {int(dut.y_out.value)}"

    # 2^2 = 4.0 (1024 in Q8.8) -> Q4.4 input for 2 is 32 (0x20)
    dut.x_in.value = 32
    await Timer(1, units="ns")
    assert int(dut.y_out.value) == 1024, f"Expected 1024 for 2^2, got {int(dut.y_out.value)}"

    # 2^(-1) = 0.5 (128 in Q8.8) -> Q4.4 input for -1 is -16
    dut.x_in.value = -16
    await Timer(1, units="ns")
    assert int(dut.y_out.value) == 128, f"Expected 128 for 2^(-1), got {int(dut.y_out.value)}"

    # 2^(-2) = 0.25 (64 in Q8.8) -> Q4.4 input for -2 is -32
    dut.x_in.value = -32
    await Timer(1, units="ns")
    assert int(dut.y_out.value) == 64, f"Expected 64 for 2^(-2), got {int(dut.y_out.value)}"

    dut._log.info("✅ Base-2 mode tests passed successfully!")

@cocotb.test()
async def test_exp2_base_e_mode(dut):
    """Test e^x mode against math.exp()"""
    dut._log.info("Testing e^x base-e mode...")
    dut.mode_e.value = 1 # e^x mode

    # e^0 = 1.0 (256 in Q8.8)
    dut.x_in.value = 0
    await Timer(1, units="ns")
    assert int(dut.y_out.value) == 256, f"Expected 256 for e^0, got {int(dut.y_out.value)}"

    # e^(1.0) -> input in Q4.4 is 16. math.exp(1.0) ≈ 2.71828 -> in Q8.8 is ~696
    dut.x_in.value = 16
    await Timer(1, units="ns")
    actual_float = int(dut.y_out.value) / 256.0
    expected_float = math.exp(1.0)
    assert abs(actual_float - expected_float) < 0.2, f"Expected ~{expected_float}, got {actual_float}"

    # e^(-1.0) -> input in Q4.4 is -16. math.exp(-1.0) ≈ 0.3678 -> in Q8.8 is ~94
    dut.x_in.value = -16
    await Timer(1, units="ns")
    actual_float = int(dut.y_out.value) / 256.0
    expected_float = math.exp(-1.0)
    assert abs(actual_float - expected_float) < 0.1, f"Expected ~{expected_float}, got {actual_float}"

    dut._log.info("✅ Base-e mode tests passed successfully!")
