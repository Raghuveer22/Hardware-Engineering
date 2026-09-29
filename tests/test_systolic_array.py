"""
==============================================================================
File: tests/test_systolic_array.py
Description: Full 2D Systolic Array Matrix Multiplication Verification Testbench
Validates:
1. Matrix multiplication C = A x W against NumPy golden reference
2. Column-based weight shifting sequence
3. Multi-cycle systolic pipeline timing and result matrix extraction
==============================================================================
"""

# Import Cocotb core module
import cocotb
# Import Clock generator
from cocotb.clock import Clock
# Import simulation triggers: RisingEdge for clock ticks, Timer for delay
from cocotb.triggers import RisingEdge, Timer
# Import NumPy for generating random matrices and calculating golden reference
import numpy as np

# Define dimensions of our systolic array grid
ROWS = 4    # Corresponds to matrix reduction dimension K = 4
COLS = 4    # Corresponds to output matrix column dimension N = 4
M_BATCH = 4 # Number of activation input vectors (Batch / Sequence length M = 4)

# Define the Cocotb test coroutine
@cocotb.test()
async def test_systolic_gemm_4x4(dut):
    """
    Test Case: Complete 4x4 INT8 Matrix Multiplication C = A @ W
    """

    # --------------------------------------------------------------------------
    # 1. SETUP CLOCK & INITIAL RESET
    # --------------------------------------------------------------------------
    # Instantiate a 10ns clock (100 MHz)
    clock = Clock(dut.clk, 10, unit="ns")
    # Start the clock running in background
    cocotb.start_soon(clock.start())

    # Assert active-low reset (0 = reset)
    dut.rst_n.value = 0
    # Disable compute and weight loading
    dut.en.value = 0
    dut.weight_load_en.value = 0
    
    # Initialize all boundary inputs to 0
    for c in range(COLS):
        dut.weights_in[c].value = 0
        dut.sum_in_top[c].value = 0
    for r in range(ROWS):
        dut.activations_in[r].value = 0

    # Hold reset for 2 clock ticks
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    # De-assert reset (1 = normal run mode)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # --------------------------------------------------------------------------
    # 2. GENERATE GOLDEN REFERENCE DATA WITH NUMPY
    # --------------------------------------------------------------------------
    # Set fixed seed for reproducibility
    np.random.seed(42)
    # Generate random matrix A (4x4) with numbers between -20 and +20
    A = np.random.randint(-20, 20, size=(M_BATCH, ROWS), dtype=np.int32)
    # Generate random weight matrix W (4x4)
    W = np.random.randint(-20, 20, size=(ROWS, COLS), dtype=np.int32)
    # Compute the golden answer C = A @ W using NumPy matrix multiplication
    C_golden = A @ W

    # Print input tensors and expected result to console log
    dut._log.info("========== INPUT MATRIX A ==========\n" + str(A))
    dut._log.info("========== WEIGHT MATRIX W ==========\n" + str(W))
    dut._log.info("========== GOLDEN OUTPUT C = A @ W ==========\n" + str(C_golden))

    # --------------------------------------------------------------------------
    # 3. LOAD WEIGHT MATRIX W INTO THE HARDWARE ARRAY
    # We shift weights down each column, starting from bottom row (ROWS-1) to top (0)
    # --------------------------------------------------------------------------
    dut._log.info(">>> Loading weights into Systolic Array...")
    # Enable weight loading mode
    dut.weight_load_en.value = 1
    # Iterate from bottom row 3 down to top row 0
    for r in range(ROWS - 1, -1, -1):
        # Place weight element W[r, c] onto each column's input port
        for c in range(COLS):
            dut.weights_in[c].value = int(W[r, c])
        # Pulse clock by 1 cycle to shift weights down 1 row
        await RisingEdge(dut.clk)
    # Disable weight loading mode (weights are now locked in each PE's weight_reg)
    dut.weight_load_en.value = 0

    # --------------------------------------------------------------------------
    # 4. STREAM ACTIVATIONS & COMPUTE
    # --------------------------------------------------------------------------
    dut._log.info(">>> Streaming activations and computing...")
    # Enable array computation
    dut.en.value = 1
    # Tie top partial sum inputs to 0 (since GEMM starts accumulation from 0)
    for c in range(COLS):
        dut.sum_in_top[c].value = 0

    # Calculate total clock cycles needed to flush the entire pipeline
    total_cycles = M_BATCH + ROWS + COLS + 4
    # Buffer to record hardware output values at each column over time
    hw_outputs = [[] for _ in range(COLS)]

    # Step through simulation clock cycles
    for cycle in range(total_cycles):
        # If we still have input vectors in matrix A, feed vector A[cycle, :]
        if cycle < M_BATCH:
            for k in range(ROWS):
                dut.activations_in[k].value = int(A[cycle, k])
        else:
            # After feeding all rows of A, drive 0 into inputs
            for k in range(ROWS):
                dut.activations_in[k].value = 0

        # Wait for rising edge of clock
        await RisingEdge(dut.clk)
        # Settle for 1ns
        await Timer(1, unit="ns")

        # Sample the output wire from the bottom of each column
        for c in range(COLS):
            val = int(dut.sum_out_bot[c].value.to_signed())
            hw_outputs[c].append(val)

    # --------------------------------------------------------------------------
    # 5. EXTRACT AND RECONSTRUCT OUTPUT MATRIX C
    # Due to systolic propagation:
    # Result element C[i, c] emerges at exact cycle: i + c + (ROWS - 1)
    # --------------------------------------------------------------------------
    # Initialize empty 4x4 matrix for hardware results
    C_hw = np.zeros((M_BATCH, COLS), dtype=np.int32)
    for i in range(M_BATCH):
        for c in range(COLS):
            # Calculate the cycle at which C[i, c] exited the bottom boundary
            out_cycle = i + c + ROWS - 1
            # Retrieve the value recorded at that cycle
            C_hw[i, c] = hw_outputs[c][out_cycle]

    # Print reconstructed hardware matrix
    dut._log.info("========== HARDWARE OUTPUT C_hw ==========\n" + str(C_hw))

    # --------------------------------------------------------------------------
    # 6. VERIFICATION & ASSERTION
    # --------------------------------------------------------------------------
    # Calculate difference between hardware output and NumPy golden model
    diff = np.abs(C_hw - C_golden)
    dut._log.info(f"Max Absolute Error: {np.max(diff)}")

    # Assert that hardware output is 100% bit-accurate with NumPy
    assert np.array_equal(C_hw, C_golden), (
        f"Hardware output does not match Golden model!\n"
        f"HW Output:\n{C_hw}\n"
        f"Golden:\n{C_golden}\n"
        f"Diff:\n{diff}"
    )

    # Log celebration message
    dut._log.info("🎉 SUCCESS: Systolic Array hardware output matches NumPy Golden Model 100% bit-accurately!")
