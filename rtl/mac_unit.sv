// ==============================================================================
// File: rtl/mac_unit.sv
// Module: mac_unit
// Description: Multiply-Accumulate (MAC) Combinational Arithmetic Block
// Equation: sum_out = sum_in + (a * b)
// ==============================================================================

// timescale defines time units and simulation precision: 1ns step, 1ps accuracy
`timescale 1ns/1ps

// Declare module with generic parameters (like C++ template <int DATA_WIDTH = 8, int ACC_WIDTH = 32>)
module mac_unit #(
    // Bit-width of operand inputs (e.g. 8 bits for INT8, range -128 to +127)
    parameter int DATA_WIDTH = 8,
    // Bit-width of accumulated result (e.g. 32 bits to prevent overflow during additions)
    parameter int ACC_WIDTH  = 32
)(
    // Input operand 'a' (Signed integer, DATA_WIDTH bits)
    input  logic signed [DATA_WIDTH-1:0] a,
    // Input operand 'b' (Signed integer, DATA_WIDTH bits)
    input  logic signed [DATA_WIDTH-1:0] b,
    // Previous running sum arriving from upstream (Signed integer, ACC_WIDTH bits)
    input  logic signed [ACC_WIDTH-1:0]  sum_in,
    // New accumulated result output (Signed integer, ACC_WIDTH bits)
    output logic signed [ACC_WIDTH-1:0]  sum_out
);

    // Intermediate wire to hold the product of multiplying two DATA_WIDTH numbers.
    // Multiplying two 8-bit numbers produces up to a 16-bit number (2 * DATA_WIDTH).
    logic signed [(2*DATA_WIDTH)-1:0] mult_product;

    // Continuous assignment: performs signed hardware multiplication (a * b)
    assign mult_product = a * b;

    // Continuous assignment: Sign-extends product to ACC_WIDTH (32-bit) and adds to sum_in.
    // '{{(ACC_WIDTH - 2*DATA_WIDTH){sign_bit}}, product}' replicates the MSB sign bit
    // so that negative numbers stay negative when widening from 16-bit to 32-bit.
    assign sum_out = sum_in + {{ (ACC_WIDTH - (2*DATA_WIDTH)){mult_product[(2*DATA_WIDTH)-1]} }, mult_product};

// End of module definition
endmodule
