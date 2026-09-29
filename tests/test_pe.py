"""
==============================================================================
File: tests/test_pe.py
Description: Cocotb Unit Testbench for Processing Element (PE)
Validates:
1. Reset functionality (registers cleared to 0)
2. Weight loading sequence
3. Multiply-Accumulate math across positive, negative, and extreme INT8 bounds
==============================================================================
"""

# Import the core Cocotb framework for hardware verification in Python
import cocotb
# Import Clock helper to generate periodic square wave clock pulses
from cocotb.clock import Clock
# Import Triggers: RisingEdge waits for clock edge, Timer waits for physical nanoseconds
from cocotb.triggers import RisingEdge, Timer

# Decorator telling Cocotb that this async function is a test case
@cocotb.test()
async def test_pe_basic_mac(dut):
    """
    Test 1: Basic Multiplication and Accumulation
    Formula: sum_out = sum_in + (a * w)
    """

    # 1. Create a 100MHz clock (period = 10ns) on dut.clk
    clock = Clock(dut.clk, 10, unit="ns")
    # Launch the clock coroutine in the background
    cocotb.start_soon(clock.start())

    # 2. Drive initial default values to all input pins
    dut.rst_n.value = 0          # Assert active-low reset (0 = in reset)
    dut.en.value = 0             # Disable compute
    dut.weight_load_en.value = 0 # Disable weight loading
    dut.weight_in.value = 0      # Weight input = 0
    dut.a_in.value = 0           # Activation input = 0
    dut.sum_in.value = 0         # Sum input = 0

    # 3. Hold reset for 2 full clock cycles
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    # De-assert reset (1 = normal operation)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # 4. STEP 1: Load Weight W = 7
    dut._log.info("Step 1: Loading Weight W = 7")
    dut.weight_load_en.value = 1 # Turn ON weight load mode
    dut.weight_in.value = 7      # Feed value 7 to weight input pin
    await RisingEdge(dut.clk)    # Wait for clock edge to latch weight into weight_reg
    dut.weight_load_en.value = 0 # Turn OFF weight load mode

    # 5. STEP 2: Feed Activation A = 6 and Incoming Sum = 100
    # Expected Math: sum_out = sum_in + (A * W) = 100 + (6 * 7) = 142
    dut._log.info("Step 2: Computing with A = 6, sum_in = 100")
    dut.en.value = 1             # Enable compute mode
    dut.a_in.value = 6           # Set activation pin = 6
    dut.sum_in.value = 100       # Set partial sum pin = 100
    await RisingEdge(dut.clk)    # Wait for clock edge to execute MAC and latch output

    # 6. Settle: wait 1ns to let simulator propagate output wires
    await Timer(1, unit="ns")

    # Read the hardware output wire `sum_out` as a signed integer
    actual_sum = int(dut.sum_out.value.to_signed())
    # Read the hardware output wire `a_out` (activation passed through)
    actual_a   = int(dut.a_out.value.to_signed())

    # Verify that the hardware result matches our expected 142
    assert actual_sum == 142, f"MAC mismatch! Expected 142, got {actual_sum}"
    # Verify that the activation was forwarded correctly
    assert actual_a == 6, f"A_out mismatch! Expected 6, got {actual_a}"

    # Log passing message
    dut._log.info("PASSED: Basic MAC computation verified.")


@cocotb.test()
async def test_pe_signed_extremes(dut):
    """
    Test 2: Signed Edge Cases (Negative numbers and extreme boundary values)
    """

    # 1. Start 10ns clock
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # 2. Reset the hardware registers
    dut.rst_n.value = 0
    dut.en.value = 0
    dut.weight_load_en.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # 3. Define corner case test vectors: (Weight, Activation, Sum_In, Expected_Sum_Out)
    test_cases = [
        (-10, 5, 20, 20 + (-10 * 5)),           # Standard negative: 20 - 50 = -30
        (-128, -1, 0, 0 + (-128 * -1)),         # Minimum INT8 boundary: -128 * -1 = +128
        (127, 127, 1000, 1000 + (127 * 127)),   # Maximum INT8 boundary: 1000 + 16129 = 17129
        (-128, 127, 500, 500 + (-128 * 127)),   # Full dynamic range: 500 - 16256 = -15756
    ]

    # 4. Iterate over each test case
    for w, a, s_in, expected in test_cases:
        # Load the test weight
        dut.weight_load_en.value = 1
        dut.weight_in.value = w
        await RisingEdge(dut.clk)
        dut.weight_load_en.value = 0

        # Feed the activation and partial sum
        dut.en.value = 1
        dut.a_in.value = a
        dut.sum_in.value = s_in
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")

        # Read actual result from hardware
        actual = int(dut.sum_out.value.to_signed())
        dut._log.info(f"Test vector: W={w}, A={a}, sum_in={s_in} => HW Result={actual}, Expected={expected}")

        # Assert hardware matches arithmetic reference
        assert actual == expected, f"Mismatch: expected {expected}, got {actual}"

    # Log success
    dut._log.info("PASSED: All signed edge cases verified successfully.")
