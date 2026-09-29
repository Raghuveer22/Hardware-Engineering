// ==============================================================================
// File: rtl/pe.sv
// Module: pe (Processing Element)
// Architecture: Weight-Stationary Systolic Cell
//
// Mental Model:
// - A single compute cell inside Google TPU or NVIDIA Tensor Core.
// - It holds one stationary weight in a register (`weight_reg`).
// - Activations enter from the LEFT and exit to the RIGHT on the next clock tick.
// - Partial sums enter from TOP, add (activation * weight), and exit to BOTTOM.
// ==============================================================================

// timescale: 1ns simulation time unit with 1ps precision
`timescale 1ns/1ps

// Parameterized module: can change bit-widths at compile time
module pe #(
    // Bit width of activations and weights (default INT8 = 8 bits)
    parameter int DATA_WIDTH = 8,
    // Bit width of partial sum accumulator (default INT32 = 32 bits)
    parameter int ACC_WIDTH  = 32
)(
    // Clock signal (synchronizes all flip-flop register updates on rising edge)
    input  logic                         clk,
    // Asynchronous Active-Low Reset (when rst_n == 0, reset all registers to 0)
    input  logic                         rst_n,
    // Enable signal (when high, PE computes and passes data to neighbors)
    input  logic                         en,
    // Weight Load Enable (when high, loads new weight into internal weight_reg)
    input  logic                         weight_load_en,
    
    // Weight Input port (used during the weight configuration phase)
    input  logic signed [DATA_WIDTH-1:0] weight_in,
    // Weight Output port (daisy-chains down the column to pass weights to lower PEs)
    output logic signed [DATA_WIDTH-1:0] weight_out,
    
    // Activation Input from Left neighbor
    input  logic signed [DATA_WIDTH-1:0] a_in,
    // Activation Output registered and sent to Right neighbor
    output logic signed [DATA_WIDTH-1:0] a_out,
    
    // Partial Sum Input from Top neighbor
    input  logic signed [ACC_WIDTH-1:0]  sum_in,
    // Accumulated Partial Sum registered and sent to Bottom neighbor
    output logic signed [ACC_WIDTH-1:0]  sum_out
);

    // Internal Flip-Flop Register: Stores the stationary weight value
    logic signed [DATA_WIDTH-1:0] weight_reg;
    // Internal Flip-Flop Register: Delays activation by 1 clock cycle (Left -> Right)
    logic signed [DATA_WIDTH-1:0] a_reg;
    // Internal Flip-Flop Register: Delays accumulated sum by 1 clock cycle (Top -> Bottom)
    logic signed [ACC_WIDTH-1:0]  sum_reg;

    // Internal wire: holds the output of the combinational MAC arithmetic unit
    logic signed [ACC_WIDTH-1:0] mac_result;

    // Instantiate the combinational MAC unit submodule
    mac_unit #(
        .DATA_WIDTH(DATA_WIDTH),
        .ACC_WIDTH(ACC_WIDTH)
    ) u_mac (
        .a(a_in),              // Connect PE activation input to MAC input 'a'
        .b(weight_reg),        // Connect stationary weight register to MAC input 'b'
        .sum_in(sum_in),       // Connect incoming partial sum to MAC input 'sum_in'
        .sum_out(mac_result)   // Output wire receives (sum_in + a * weight_reg)
    );

    // Sequential Logic Block: Executed on the positive edge (rising tick) of clock or reset
    always_ff @(posedge clk or negedge rst_n) begin
        // If active-low reset is asserted (rst_n == 0)
        if (!rst_n) begin
            // Clear all internal registers to 0
            weight_reg <= '0;
            a_reg      <= '0;
            sum_reg    <= '0;
        end else begin
            // 1. Weight Configuration Phase:
            // When weight_load_en is 1, capture the incoming weight into our register
            if (weight_load_en) begin
                weight_reg <= weight_in;
            end
            
            // 2. Active Compute Phase:
            // When enable is 1, register the activation and the MAC calculation
            if (en) begin
                // Save activation so the right neighbor can receive it on next cycle
                a_reg   <= a_in;
                // Save computed partial sum so bottom neighbor receives it on next cycle
                sum_reg <= mac_result;
            end
        end
    end

    // Assign internal registers to the module output pins:
    // a_out reflects the activation registered in a_reg
    assign a_out      = a_reg;
    // sum_out reflects the accumulated sum in sum_reg
    assign sum_out    = sum_reg;
    // weight_out passes the weight down the column to the next PE
    assign weight_out = weight_reg;

// End of Processing Element module
endmodule
