import cocotb
from cocotb.triggers import Timer
import random

def to_signed(val, bits=8):
    if val >= (1 << (bits - 1)):
        return val - (1 << bits)
    return val

@cocotb.test()
async def test_adder_standard_and_corner_cases(dut):
    """Test signed addition corner cases without saturation (wrap-around)"""
    dut.saturate.value = 0
    
    corner_cases = [
        (0, 0),
        (0, 50),
        (50, 0),
        (0, -50),
        (-50, 0),
        (25, 30),        # 55
        (-25, -30),      # -55
        (50, -20),       # 30
        (-50, 20),       # -30
        (100, 27),       # 127 (max pos)
        (-100, -28),     # -128 (max neg)
        (100, 50),       # 150 -> overflow -> -106
        (-100, -50),     # -150 -> overflow -> +106
    ]

    for a, b in corner_cases:
        dut.a.value = a
        dut.b.value = b
        await Timer(1, unit="ns")
        
        raw_val = int(dut.sum.value.to_signed())
        expected_raw = (a + b)
        # 8-bit wrap-around
        if expected_raw > 127:
            expected_wrap = expected_raw - 256
            expected_overflow = 1
        elif expected_raw < -128:
            expected_wrap = expected_raw + 256
            expected_overflow = 1
        else:
            expected_wrap = expected_raw
            expected_overflow = 0
            
        assert raw_val == expected_wrap, f"Mismatch for {a} + {b}: got {raw_val}, expected {expected_wrap}"
        assert int(dut.overflow.value) == expected_overflow, f"Overflow flag mismatch for {a} + {b}"

@cocotb.test()
async def test_adder_saturation_mode(dut):
    """Test signed addition with saturation enabled (clamping on overflow)"""
    dut.saturate.value = 1

    saturation_cases = [
        (100, 50, 127, 1),       # 150 -> clamped to 127
        (127, 1, 127, 1),        # 128 -> clamped to 127
        (120, 30, 127, 1),       # 150 -> clamped to 127
        (-100, -50, -128, 1),    # -150 -> clamped to -128
        (-128, -1, -128, 1),     # -129 -> clamped to -128
        (50, 50, 100, 0),        # No overflow
        (-40, -40, -80, 0),      # No overflow
    ]

    for a, b, expected_sum, expected_overflow in saturation_cases:
        dut.a.value = a
        dut.b.value = b
        await Timer(1, unit="ns")
        
        actual_sum = int(dut.sum.value.to_signed())
        actual_overflow = int(dut.overflow.value)
        assert actual_sum == expected_sum, f"Sat mismatch for {a} + {b}: got {actual_sum}, expected {expected_sum}"
        assert actual_overflow == expected_overflow, f"Sat overflow flag mismatch for {a} + {b}"

@cocotb.test()
async def test_adder_random_exhaustive(dut):
    """Test 500 random vectors for both standard and saturated modes"""
    for sat in [0, 1]:
        dut.saturate.value = sat
        for _ in range(250):
            a = random.randint(-128, 127)
            b = random.randint(-128, 127)
            dut.a.value = a
            dut.b.value = b
            await Timer(1, unit="ns")
            
            raw_sum = a + b
            if raw_sum > 127:
                exp_over = 1
                exp_sum = 127 if sat else raw_sum - 256
            elif raw_sum < -128:
                exp_over = 1
                exp_sum = -128 if sat else raw_sum + 256
            else:
                exp_over = 0
                exp_sum = raw_sum
                
            actual_sum = int(dut.sum.value.to_signed())
            actual_over = int(dut.overflow.value)
            assert actual_sum == exp_sum, f"Random test failed for {a} + {b} (sat={sat}): got {actual_sum}, exp {exp_sum}"
            assert actual_over == exp_over, f"Overflow flag failed for {a} + {b}"
