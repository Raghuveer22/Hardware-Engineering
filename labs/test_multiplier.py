"""
==============================================================================
File: labs/test_multiplier.py
Lab 01: Python Verification for 8-bit Signed Multiplier
==============================================================================
"""

import cocotb
from cocotb.triggers import Timer
import random

@cocotb.test()
async def test_multiplier_exhaustive(dut):
    """Test signed corner cases and 200 random vectors vs Python golden multiplication"""
    dut._log.info("🧪 Starting Multiplier Verification...")

    corner_cases = [
        (0, 0), (0, 127), (0, -128),
        (1, 1), (-1, 1), (-1, -1),
        (127, 127),       # Max pos * Max pos = 16129
        (-128, -128),     # Max neg * Max neg = 16384
        (-128, 127),      # Max neg * Max pos = -16256
        (127, -128),
    ]

    for a, b in corner_cases:
        dut.a.value = a
        dut.b.value = b
        await Timer(1, unit="ns")

        expected = a * b
        actual = int(dut.product.value.to_signed())
        assert actual == expected, f"Mismatch ({a} * {b}): Expected {expected}, Got {actual}"

    for _ in range(200):
        a = random.randint(-128, 127)
        b = random.randint(-128, 127)
        dut.a.value = a
        dut.b.value = b
        await Timer(1, unit="ns")

        expected = a * b
        actual = int(dut.product.value.to_signed())
        assert actual == expected, f"Mismatch ({a} * {b}): Expected {expected}, Got {actual}"

    dut._log.info("✅ Multiplier PASSED all 210 test vectors!")
