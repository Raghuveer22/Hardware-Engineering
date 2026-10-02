import cocotb
from cocotb.triggers import Timer
import math
import random

@cocotb.test()
async def test_sqrt_perfect_squares(dut):
    """Test perfect squares from 0 up to 255^2 = 65025"""
    test_roots = [0, 1, 2, 3, 4, 8, 10, 16, 25, 32, 64, 100, 128, 200, 255]
    
    for r in test_roots:
        radicand = r * r
        dut.radicand.value = radicand
        await Timer(1, unit="ns")
        
        act_root = int(dut.root.value)
        act_rem = int(dut.remainder.value)
        
        assert act_root == r, f"Root mismatch for radicand {radicand}: got {act_root}, expected {r}"
        assert act_rem == 0, f"Remainder mismatch for perfect square {radicand}: got {act_rem}, expected 0"

@cocotb.test()
async def test_sqrt_non_perfect_squares_and_corners(dut):
    """Test corner cases (0, 1, 65535) and non-perfect squares"""
    corner_cases = [0, 1, 2, 3, 5, 7, 8, 15, 63, 65, 127, 255, 1000, 4095, 65534, 65535]
    
    for val in corner_cases:
        dut.radicand.value = val
        await Timer(1, unit="ns")
        
        expected_root = math.isqrt(val)
        expected_rem = val - (expected_root ** 2)
        
        act_root = int(dut.root.value)
        act_rem = int(dut.remainder.value)
        
        assert act_root == expected_root, f"Failed for val={val}: got root={act_root}, exp={expected_root}"
        assert act_rem == expected_rem, f"Failed remainder for val={val}: got rem={act_rem}, exp={expected_rem}"

@cocotb.test()
async def test_sqrt_random_exhaustive(dut):
    """Test 500 random 16-bit values against Python math.isqrt()"""
    for _ in range(500):
        val = random.randint(0, 65535)
        dut.radicand.value = val
        await Timer(1, unit="ns")
        
        expected_root = math.isqrt(val)
        expected_rem = val - (expected_root ** 2)
        
        act_root = int(dut.root.value)
        act_rem = int(dut.remainder.value)
        
        assert act_root == expected_root, f"Random test failed for {val}: root got {act_root}, exp {expected_root}"
        assert act_rem == expected_rem, f"Random test failed for {val}: rem got {act_rem}, exp {expected_rem}"
