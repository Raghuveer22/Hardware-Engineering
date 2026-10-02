// ==============================================================================
// File: rtl/sqrt.sv
// Description: Parameterized Hardware Square Root Unit (Digit-by-Digit Algorithm)
// Computes: root = floor(sqrt(radicand)), remainder = radicand - (root^2)
//
// Relevance in AI/Transformers:
// Used to compute the 1 / sqrt(d_k) scaling factor in Scaled Dot-Product Attention:
// Attention(Q, K, V) = Softmax( (Q * K^T) / sqrt(d_k) ) * V
// ==============================================================================

`timescale 1ns/1ps

module sqrt #(
    parameter int RADICAND_WIDTH = 16,                         // Input width (e.g., 16 bits for 0..65535)
    parameter int ROOT_WIDTH     = (RADICAND_WIDTH + 1) / 2    // Output root width (8 bits for 0..255)
)(
    input  logic [RADICAND_WIDTH-1:0] radicand,
    output logic [ROOT_WIDTH-1:0]     root,
    output logic [RADICAND_WIDTH-1:0] remainder
);

    // Combinational digit-by-digit non-restoring / shift-and-subtract square root algorithm
    logic [RADICAND_WIDTH+1:0] rem_reg;
    logic [ROOT_WIDTH-1:0]     root_reg;
    logic [RADICAND_WIDTH+1:0] test_val;

    always_comb begin
        rem_reg  = '0;
        root_reg = '0;

        // Iterate through bit pairs from MSB to LSB
        for (int i = ROOT_WIDTH - 1; i >= 0; i--) begin
            // Shift remainder left by 2 bits and bring down next 2 bits of radicand
            rem_reg = (rem_reg << 2) | ((radicand >> (2 * i)) & 2'b11);

            // Candidate trial value: (root * 4 + 1)
            test_val = {root_reg, 2'b01};

            if (rem_reg >= test_val) begin
                rem_reg  = rem_reg - test_val;
                root_reg = (root_reg << 1) | 1'b1;
            end else begin
                root_reg = (root_reg << 1) | 1'b0;
            end
        end

        root      = root_reg;
        remainder = rem_reg[RADICAND_WIDTH-1:0];
    end

endmodule
