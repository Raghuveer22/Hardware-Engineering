"""
==============================================================================
File: labs/test_mac.py
Lab 02: Python Verification for Multiply-Accumulate (MAC) Unit
==============================================================================
"""

import cocotb
from cocotb.triggers import Timer
import random

@cocotb.test()
async def test_mac_exhaustive(dut):
    """Test MAC combinations: sum_out = sum_in + (a * b)"""
    dut._log.info("🧪 Starting MAC Unit Verification...")

    corner_cases = [
        (0, 0, 0),
        (10, 5, 100),
        (-10, 5, 20),
        (-128, -128, 10000),
        (-128, 127, -500),
        (127, 127, -20000),
    ]

    for a, b, s_in in corner_cases:
        dut.a.value = a
        dut.b.value = b
        dut.sum_in.value = s_in
        await Timer(1, unit="ns")

        expected = s_in + (a * b)
        actual = int(dut.sum_out.value.to_signed())
        assert actual == expected, f"Mismatch ({s_in} + {a}*{b}): Expected {expected}, Got {actual}"

    for _ in range(200):
        a = random.randint(-128, 127)
        b = random.randint(-128, 127)
        s_in = random.randint(-50000, 50000)
        dut.a.value = a
        dut.b.value = b
        dut.sum_in.value = s_in
        await Timer(1, unit="ns")

        expected = s_in + (a * b)
        actual = int(dut.sum_out.value.to_signed())
        assert actual == expected, f"Mismatch ({s_in} + {a}*{b}): Expected {expected}, Got {actual}"

    dut._log.info("✅ MAC Unit PASSED all 206 test vectors!")
