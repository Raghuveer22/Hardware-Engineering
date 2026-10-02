// ==============================================================================
// File: rtl/adder.sv
// Description: Parameterized Signed Hardware Adder with Saturation & Overflow
// Computes: sum = a + b (Signed with optional saturation clipping)
// ==============================================================================

`timescale 1ns/1ps

module adder #(
    parameter int DATA_WIDTH = 8
)(
    input  logic signed [DATA_WIDTH-1:0] a,
    input  logic signed [DATA_WIDTH-1:0] b,
    input  logic                         saturate,  // When 1, clamps on overflow instead of wrapping
    output logic signed [DATA_WIDTH-1:0] sum,
    output logic                         carry_out,
    output logic                         overflow
);

    // Internal full sum with 1 extra bit for carry and overflow detection
    logic signed [DATA_WIDTH:0] raw_sum;
    localparam logic signed [DATA_WIDTH-1:0] MAX_POS = {1'b0, {(DATA_WIDTH-1){1'b1}}}; // e.g. +127 for 8-bit
    localparam logic signed [DATA_WIDTH-1:0] MAX_NEG = {1'b1, {(DATA_WIDTH-1){1'b0}}}; // e.g. -128 for 8-bit

    always_comb begin
        // Perform standard addition with bit extension
        raw_sum = {a[DATA_WIDTH-1], a} + {b[DATA_WIDTH-1], b};

        // Carry out for unsigned representation
        carry_out = raw_sum[DATA_WIDTH];

        // Signed 2's complement overflow condition:
        // Adding two positives yields negative OR adding two negatives yields positive
        overflow = (a[DATA_WIDTH-1] == b[DATA_WIDTH-1]) && (raw_sum[DATA_WIDTH-1] != a[DATA_WIDTH-1]);

        // Output selection: saturated vs standard wrap-around
        if (saturate && overflow) begin
            if (a[DATA_WIDTH-1] == 1'b0) begin
                // Positive overflow -> clamp to MAX positive (+127 for INT8)
                sum = MAX_POS;
            end else begin
                // Negative overflow -> clamp to MAX negative (-128 for INT8)
                sum = MAX_NEG;
            end
        end else begin
            sum = raw_sum[DATA_WIDTH-1:0];
        end
    end

endmodule
