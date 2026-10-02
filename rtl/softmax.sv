// ==============================================================================
// File: rtl/softmax.sv
// Description: Parameterized Hardware Softmax Unit (Safe Softmax Architecture)
// Computes: P_i = exp(x_i - max(x)) / sum_j(exp(x_j - max(x)))
//
// Relevance in Transformers & LLMs:
// Softmax converts attention scores into normalized attention probabilities (weights).
// Hardware uses "Safe Softmax" (subtracting max) to prevent exponential overflow.
// ==============================================================================

`timescale 1ns/1ps

module softmax #(
    parameter int NUM_ELEMENTS = 4,   // Number of vector elements (e.g. 4)
    parameter int DATA_WIDTH   = 8,   // Signed input width
    parameter int OUT_WIDTH    = 8    // Unsigned Q0.8 fixed-point probability (0..255 representing 0.0..1.0)
)(
    input  logic signed [DATA_WIDTH-1:0] in_vec [NUM_ELEMENTS],
    output logic        [OUT_WIDTH-1:0]  out_prob[NUM_ELEMENTS]
);

    // 1. Max Search Stage (Numerical Stability: Safe Softmax)
    logic signed [DATA_WIDTH-1:0] max_val;

    always_comb begin
        max_val = in_vec[0];
        for (int i = 1; i < NUM_ELEMENTS; i++) begin
            if (in_vec[i] > max_val) begin
                max_val = in_vec[i];
            end
        end
    end

    // 2. Shift Stage: delta = x_i - max_val (always <= 0)
    logic signed [DATA_WIDTH-1:0] delta [NUM_ELEMENTS];
    always_comb begin
        for (int i = 0; i < NUM_ELEMENTS; i++) begin
            delta[i] = in_vec[i] - max_val;
        end
    end

    // 3. Fixed-Point Exponential Lookup Function: exp(delta) for delta <= 0
    // Returns Q0.8 fixed-point value (0..255)
    function automatic logic [7:0] exp_approx(input logic signed [DATA_WIDTH-1:0] diff);
        logic signed [DATA_WIDTH-1:0] mag;
        begin
            mag = -diff; // Magnitude of negative delta
            case (mag)
                0:  exp_approx = 8'd255; // exp(0) = 1.0 (255/255)
                1:  exp_approx = 8'd155; // exp(-0.5) approx
                2:  exp_approx = 8'd94;  // exp(-1.0) ~ 0.368 -> 94/255
                3:  exp_approx = 8'd57;  // exp(-1.5) ~ 0.223 -> 57/255
                4:  exp_approx = 8'd35;  // exp(-2.0) ~ 0.135 -> 35/255
                5:  exp_approx = 8'd21;  // exp(-2.5) ~ 0.082 -> 21/255
                6:  exp_approx = 8'd13;  // exp(-3.0) ~ 0.050 -> 13/255
                7:  exp_approx = 8'd8;   // exp(-3.5) ~ 0.030 -> 8/255
                8:  exp_approx = 8'd5;   // exp(-4.0) ~ 0.018 -> 5/255
                9:  exp_approx = 8'd3;   // exp(-4.5) ~ 0.011 -> 3/255
                10: exp_approx = 8'd2;   // exp(-5.0) ~ 0.007 -> 2/255
                11: exp_approx = 8'd1;   // exp(-5.5) ~ 0.004 -> 1/255
                default: exp_approx = 8'd0; // Underflow to 0 for large negative deltas
            endcase
        end
    endfunction

    // 4. Exponent Evaluation & Sum Reduction
    logic [7:0]  exp_vals [NUM_ELEMENTS];
    logic [15:0] sum_exp;

    always_comb begin
        sum_exp = '0;
        for (int i = 0; i < NUM_ELEMENTS; i++) begin
            exp_vals[i] = exp_approx(delta[i]);
            sum_exp     = sum_exp + exp_vals[i];
        end
    end

    // 5. Normalization Division: prob[i] = (exp[i] * 255) / sum_exp
    always_comb begin
        for (int i = 0; i < NUM_ELEMENTS; i++) begin
            if (sum_exp > 0) begin
                out_prob[i] = (exp_vals[i] * 255) / sum_exp;
            end else begin
                out_prob[i] = '0;
            end
        end
    end

endmodule
