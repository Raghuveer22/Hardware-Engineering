// ==============================================================================
// File: cpp_emulation/main.cpp
// Description: Pre-Silicon C++ Cycle-Accurate Hardware Emulator for Systolic Array
//
// Mental Model:
// - Verilator translates SystemVerilog RTL into a C++ class (`Vsystolic_array`).
// - This C++ testbench acts as the virtual host platform.
// - It drives input pins, pulses clock ticks, evaluates combinatorial logic,
//   and checks output results at millions of cycles per second.
// ==============================================================================

// Standard C++ headers for I/O, vectors, integer types, and assertions
#include <iostream>
#include <iomanip>
#include <vector>
#include <cstdint>
#include <cassert>

// Include Verilator-generated C++ header representing our systolic array RTL module
#include "Vsystolic_array.h"
// Include core Verilator runtime library
#include "verilated.h"
// Include Verilator VCD (Value Change Dump) tracer for generating waveform files
#include "verilated_vcd_c.h"

// Required by Verilator runtime for internal simulation time tracking
double sc_time_stamp() {
    return 0;
}

// Systolic Array Dimensions
const int ROWS = 4;    // K dimension (reduction depth)
const int COLS = 4;    // N dimension (output columns)
const int M_BATCH = 4; // M dimension (batch / sequence rows)

// Harness struct encapsulating the hardware instance and clock control
struct EmulationHarness {
    // Pointer to the Verilator C++ hardware instance
    Vsystolic_array* top;
    // Pointer to the waveform dump file object
    VerilatedVcdC* tfp;
    // Simulation timestamp counter in arbitrary time units (ticks)
    uint64_t main_time;

    // Constructor: Initializes hardware instance and sets up waveform tracing
    EmulationHarness() : main_time(0) {
        // 1. Allocate the hardware model in memory
        top = new Vsystolic_array;
        // 2. Enable waveform tracing in Verilator
        Verilated::traceEverOn(true);
        // 3. Allocate VCD tracer
        tfp = new VerilatedVcdC;
        // 4. Attach tracer to hardware top module with trace depth 99
        top->trace(tfp, 99);
        // 5. Open output waveform file
        tfp->open("systolic_emulation.vcd");
    }

    // Destructor: Clean up pointers and close waveform file
    ~EmulationHarness() {
        // Flush and close waveform file
        tfp->close();
        // Free tracer memory
        delete tfp;
        // Free hardware instance memory
        delete top;
    }

    // Advances the hardware by one complete clock cycle (LOW -> HIGH -> LOW)
    void tick() {
        // Set clock to LOW (0)
        top->clk = 0;
        // Evaluate all combinational logic for the LOW phase
        top->eval();
        // Dump signal values to waveform file
        tfp->dump(main_time++);

        // Set clock to HIGH (1) - triggers rising edge flip-flops
        top->clk = 1;
        // Evaluate all sequential and combinational logic for rising edge
        top->eval();
        // Dump updated signal values to waveform file
        tfp->dump(main_time++);
    }

    // Resets the hardware to initial clean state
    void reset() {
        // Assert active-low reset (0 = in reset)
        top->rst_n = 0;
        // Disable compute and weight loading
        top->en = 0;
        top->weight_load_en = 0;
        // Pulse clock 5 times to propagate reset across all registers
        for (int i = 0; i < 5; i++) tick();
        // De-assert reset (1 = normal run)
        top->rst_n = 1;
        // Step 1 clean cycle
        tick();
    }
};

// Main function: Entry point of the C++ pre-silicon emulator
int main(int argc, char** argv) {
    // Pass command line arguments to Verilator runtime
    Verilated::commandArgs(argc, argv);
    
    // Create an instance of our emulation harness
    EmulationHarness sim;

    std::cout << "========================================================\n";
    std::cout << "🚀 Pre-Silicon C++ Hardware Emulator: 4x4 Systolic Array\n";
    std::cout << "========================================================\n\n";

    // 1. Reset the simulated hardware
    sim.reset();

    // 2. Define Test Input Matrices A (4x4) and Weights W (4x4)
    int8_t A[M_BATCH][ROWS] = {
        {  5,  2, -3,  4 },
        {  1, -1,  2,  0 },
        { -2,  3,  1, -4 },
        {  4,  0, -1,  2 }
    };

    int8_t W[ROWS][COLS] = {
        {  2, -1,  3,  1 },
        {  0,  4, -2,  3 },
        { -3,  1,  0, -2 },
        {  1,  2,  4, -1 }
    };

    // Calculate golden software matrix multiplication: C_golden = A * W
    int32_t C_golden[M_BATCH][COLS] = {0};
    for (int i = 0; i < M_BATCH; i++) {
        for (int j = 0; j < COLS; j++) {
            for (int k = 0; k < ROWS; k++) {
                C_golden[i][j] += A[i][k] * W[k][j];
            }
        }
    }

    // 3. Step 1: Load Weights into the systolic array (shifting top to bottom)
    std::cout << "[Step 1] Loading Weights into Array...\n";
    sim.top->weight_load_en = 1; // Enable weight loading
    for (int r = ROWS - 1; r >= 0; r--) {
        for (int c = 0; c < COLS; c++) {
            sim.top->weights_in[c] = W[r][c]; // Place weight on column input port
        }
        sim.tick(); // Advance clock by 1 tick
    }
    sim.top->weight_load_en = 0; // Disable weight loading

    // 4. Step 2: Stream Activations and Simulate Clock Cycles
    std::cout << "[Step 2] Streaming Activations and Simulating Cycles...\n";
    sim.top->en = 1; // Enable compute mode
    for (int c = 0; c < COLS; c++) {
        sim.top->sum_in_top[c] = 0; // Tie top partial sum boundary to 0
    }

    // Total cycles to execute and flush the systolic pipeline
    int total_cycles = M_BATCH + ROWS + COLS + 4;
    // Buffer to record hardware output stream for each column
    std::vector<std::vector<int32_t>> hw_col_stream(COLS, std::vector<int32_t>(total_cycles, 0));

    // Simulation cycle loop
    for (int cycle = 0; cycle < total_cycles; cycle++) {
        // Feed activation row if within matrix bounds, else 0
        for (int r = 0; r < ROWS; r++) {
            sim.top->activations_in[r] = (cycle < M_BATCH) ? A[cycle][r] : 0;
        }

        // Step the hardware by 1 full clock cycle
        sim.tick();

        // Sample output ports at bottom boundary
        for (int c = 0; c < COLS; c++) {
            hw_col_stream[c][cycle] = static_cast<int32_t>(sim.top->sum_out_bot[c]);
        }
    }

    // 5. Reconstruct Result Matrix C from systolic output stream
    int32_t C_hw[M_BATCH][COLS] = {0};
    bool pass = true;

    std::cout << "\n========== VERIFICATION SUMMARY ==========\n";
    std::cout << "Computed Matrix C (HW) vs Golden Reference:\n";
    for (int i = 0; i < M_BATCH; i++) {
        std::cout << "Row " << i << " | HW: [ ";
        for (int c = 0; c < COLS; c++) {
            // Output element C[i, c] emerges at cycle = i + c + ROWS - 1
            int out_cycle = i + c + ROWS - 1;
            C_hw[i][c] = hw_col_stream[c][out_cycle];
            std::cout << std::setw(5) << C_hw[i][c] << " ";
            // Compare with golden software reference
            if (C_hw[i][c] != C_golden[i][c]) {
                pass = false;
            }
        }
        std::cout << "] | Golden: [ ";
        for (int c = 0; c < COLS; c++) {
            std::cout << std::setw(5) << C_golden[i][c] << " ";
        }
        std::cout << "]\n";
    }

    // Check final verification result
    if (pass) {
        std::cout << "\n✅ SUCCESS: C++ Verilator Emulation matched Golden Matrix perfectly!\n";
        std::cout << "Waveform dumped to: systolic_emulation.vcd\n";
        return 0; // Return success exit code
    } else {
        std::cerr << "\n❌ ERROR: Numerical mismatch detected!\n";
        return 1; // Return error exit code
    }
}
