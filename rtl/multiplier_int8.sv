// ==============================================================================
// File: rtl/multiplier_int8.sv
// Description: Parameterized Signed Hardware Multiplier
// Computes: product = a * b (Signed 8-bit * 8-bit = Signed 16-bit)
// ==============================================================================

`timescale 1ns/1ps

module multiplier_int8 #(
    parameter int DATA_WIDTH = 8,
    parameter int PROD_WIDTH = 2 * DATA_WIDTH // 16 bits for 8x8
)(
    input  logic signed [DATA_WIDTH-1:0] a,
    input  logic signed [DATA_WIDTH-1:0] b,
    output logic signed [PROD_WIDTH-1:0] product
);

    // Combinational signed multiplication
    assign product = a * b;

endmodule
