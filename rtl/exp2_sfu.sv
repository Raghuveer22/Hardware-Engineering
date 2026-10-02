// ==============================================================================
// File: rtl/exp2_sfu.sv
// Description: Parameterized Hardware Exponential Special Function Unit (SFU)
// Computes: y = e^x or y = 2^x in Q8.8 Fixed-Point Format
//
// Hardware Architecture:
// 1. Mode Selector:
//    - mode_e = 1 -> Compute e^x by pre-scaling: u = x * log2(e) ≈ x * 1.442695 (Q4.4)
//    - mode_e = 0 -> Compute 2^x directly: u = x
// 2. Integer / Fractional Decomposition:
//    - Integer part (I) controls bit-shifting: y = 2^F * 2^I
//    - Fractional part (F in [0, 1)) evaluated via high-speed 16-entry seed LUT
// 3. Barrel Shifter & Range Clamping:
//    - Dynamic left/right shift for fast single-cycle throughput
//
// Relevance in LLMs & AI Accelerators:
// Essential for Softmax Attention, Cross-Entropy Loss, and SwiGLU / SiLU Activations:
//   SiLU(x) = x / (1 + exp(-x))
// ==============================================================================

`timescale 1ns/1ps

module exp2_sfu #(
    parameter int IN_WIDTH  = 8,   // Signed Q4.4 input (-8.0 to +7.9375)
    parameter int OUT_WIDTH = 16   // Unsigned Q8.8 output (0.0 to 255.996)
)(
    input  logic signed [IN_WIDTH-1:0]  x_in,       // Input in signed Q4.4 format
    input  logic                        mode_e,     // 1 = e^x, 0 = 2^x
    output logic        [OUT_WIDTH-1:0] y_out,      // Output in unsigned Q8.8 format
    output logic                        overflow    // Overflow flag (when result exceeds Q8.8)
);

    // log2(e) ≈ 1.442695 in Q4.4 fixed-point is round(1.442695 * 16) = 23 (23/16 = 1.4375)
    localparam logic signed [7:0] LOG2_E_Q4_4 = 8'sd23;

    // Step 1: Base Conversion Scaling
    logic signed [15:0] scaled_u;
    logic signed [7:0]  u_q4_4;

    always_comb begin
        if (mode_e) begin
            scaled_u = (16'(x_in) * 16'(LOG2_E_Q4_4)) >>> 4; // Multiply and rescale by /16
            u_q4_4   = scaled_u[7:0];
        end else begin
            u_q4_4   = x_in;
        end
    end

    // Step 2: Split into Integer (I) and Fractional (F) components
    // In Q4.4: u = I + F/16
    logic signed [3:0] int_part;
    logic        [3:0] frac_part;

    always_comb begin
        int_part  = u_q4_4[7:4];
        frac_part = u_q4_4[3:0]; // 0/16 .. 15/16
    end

    // Step 3: Fast 16-entry Fractional Lookup Table for 2^(F/16) in Q0.8 (256 = 1.0, 511 ≈ 1.996)
    function automatic logic [8:0] get_2_power_frac(input logic [3:0] frac);
        case (frac)
            4'd0:  get_2_power_frac = 9'd256; // 2^(0/16)  = 1.0000 -> 256
            4'd1:  get_2_power_frac = 9'd267; // 2^(1/16)  ≈ 1.0443 -> 267
            4'd2:  get_2_power_frac = 9'd279; // 2^(2/16)  ≈ 1.0905 -> 279
            4'd3:  get_2_power_frac = 9'd292; // 2^(3/16)  ≈ 1.1388 -> 292
            4'd4:  get_2_power_frac = 9'd304; // 2^(4/16)  ≈ 1.1892 -> 304
            4'd5:  get_2_power_frac = 9'd318; // 2^(5/16)  ≈ 1.2419 -> 318
            4'd6:  get_2_power_frac = 9'd332; // 2^(6/16)  ≈ 1.2968 -> 332
            4'd7:  get_2_power_frac = 9'd347; // 2^(7/16)  ≈ 1.3543 -> 347
            4'd8:  get_2_power_frac = 9'd362; // 2^(8/16)  ≈ 1.4142 -> 362
            4'd9:  get_2_power_frac = 9'd378; // 2^(9/16)  ≈ 1.4768 -> 378
            4'd10: get_2_power_frac = 9'd395; // 2^(10/16) ≈ 1.5422 -> 395
            4'd11: get_2_power_frac = 9'd412; // 2^(11/16) ≈ 1.6105 -> 412
            4'd12: get_2_power_frac = 9'd431; // 2^(12/16) ≈ 1.6818 -> 431
            4'd13: get_2_power_frac = 9'd450; // 2^(13/16) ≈ 1.7562 -> 450
            4'd14: get_2_power_frac = 9'd470; // 2^(14/16) ≈ 1.8340 -> 470
            4'd15: get_2_power_frac = 9'd491; // 2^(15/16) ≈ 1.9152 -> 491
            default: get_2_power_frac = 9'd256;
        endcase
    endfunction

    // Step 4: Shifter & Output Formatting
    logic [8:0] frac_lut_val;
    always_comb begin
        frac_lut_val = get_2_power_frac(frac_part);
        overflow     = 1'b0;

        if (int_part < -8) begin
            y_out    = 16'd0; // Underflow to 0
        end else if (int_part < 0) begin
            // Right shift by negative exponent: 2^F >> |int_part|
            y_out    = 16'(frac_lut_val >> (-int_part));
        end else if (int_part == 0) begin
            y_out    = 16'(frac_lut_val); // Exact Q8.8 value
        end else if (int_part < 7) begin
            // Left shift: 2^F << int_part
            logic [23:0] shifted;
            shifted  = 24'(frac_lut_val) << int_part;
            if (shifted > 24'hFFFF) begin
                y_out    = 16'hFFFF;
                overflow = 1'b1;
            end else begin
                y_out    = shifted[15:0];
            end
        end else begin
            // Exceeds Q8.8 range (overflow)
            y_out    = 16'hFFFF;
            overflow = 1'b1;
        end
    end

endmodule
