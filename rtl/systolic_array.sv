// ==============================================================================
// File: rtl/systolic_array.sv
// Module: systolic_array
// Description: Parameterized 2D Weight-Stationary Systolic Array (ROWS x COLS)
//
// Mental Model:
// - A 2D grid of PEs (e.g. 4x4 = 16 PEs).
// - Input matrix A streams in from the LEFT boundary (rows 0..3).
// - Weights matrix W are loaded in advance and stay stationary in each PE.
// - Result matrix C streams out from the BOTTOM boundary (cols 0..3).
// - Built-in skew registers ensure row 0 starts on cycle 0, row 1 delayed by 1,
//   row 2 delayed by 2, etc., so wavefronts synchronize automatically.
// ==============================================================================

// timescale: 1ns simulation time unit with 1ps precision
`timescale 1ns/1ps

// Module declaration with configurable parameters
module systolic_array #(
    // Number of rows in PE grid (corresponds to reduction dimension K)
    parameter int ROWS        = 4,
    // Number of columns in PE grid (corresponds to output feature dimension N)
    parameter int COLS        = 4,
    // Precision of operands (default 8-bit signed integer)
    parameter int DATA_WIDTH  = 8,
    // Precision of accumulator (default 32-bit signed integer)
    parameter int ACC_WIDTH   = 32
)(
    // Global Clock signal
    input  logic                                  clk,
    // Global Active-Low Reset (0 = reset, 1 = normal run)
    input  logic                                  rst_n,
    // Global Compute Enable signal
    input  logic                                  en,
    // Global Weight Load Enable signal
    input  logic                                  weight_load_en,

    // Weight inputs: 1 input port per column (weights shift down from top row to bottom row)
    input  logic signed [DATA_WIDTH-1:0]          weights_in   [COLS],

    // Activation inputs: 1 input port per row (un-skewed raw vector fed from host)
    input  logic signed [DATA_WIDTH-1:0]          activations_in [ROWS],

    // Partial sum inputs at top boundary (tied to 0 for standard GEMM C = A*W)
    input  logic signed [ACC_WIDTH-1:0]           sum_in_top   [COLS],

    // Final accumulated output results emerging from bottom boundary
    output logic signed [ACC_WIDTH-1:0]           sum_out_bot  [COLS],

    // Activation passthrough at right boundary (for monitoring / cascading chips)
    output logic signed [DATA_WIDTH-1:0]          activations_out [ROWS]
);

    // --------------------------------------------------------------------------
    // SKEWING REGISTERS FOR ACTIVATIONS
    // To align the diagonal wavefront in a systolic array:
    // Row 0 needs 0 cycles delay
    // Row 1 needs 1 cycle delay
    // Row r needs r cycles delay
    // --------------------------------------------------------------------------
    // Array of wires holding the skewed activation signals for each row
    logic signed [DATA_WIDTH-1:0] act_skewed [ROWS];

    // Generate loop creating hardware delay pipelines for each row
    generate
        for (genvar r = 0; r < ROWS; r++) begin : gen_act_skew
            // Row 0 has 0 delay stages: pass through directly
            if (r == 0) begin : gen_row0_direct
                assign act_skewed[0] = activations_in[0];
            end else begin : gen_row_delay_pipeline
                // Create a shift register of depth 'r' for row 'r'
                logic signed [DATA_WIDTH-1:0] delay_pipe [r];

                // Sequential process: shift activation data by 1 step every clock edge
                always_ff @(posedge clk or negedge rst_n) begin
                    if (!rst_n) begin
                        // Clear pipeline on reset
                        for (int d = 0; d < r; d++) begin
                            delay_pipe[d] <= '0;
                        end
                    end else if (en) begin
                        // Load newest input into stage 0
                        delay_pipe[0] <= activations_in[r];
                        // Shift previous values forward
                        for (int d = 1; d < r; d++) begin
                            delay_pipe[d] <= delay_pipe[d-1];
                        end
                    end
                end

                // Connect the end of the delay pipeline to act_skewed[r]
                assign act_skewed[r] = delay_pipe[r-1];
            end
        end
    endgenerate

    // --------------------------------------------------------------------------
    // INTERNAL 2D GRID INTERCONNECT WIRES
    // --------------------------------------------------------------------------
    // Horizontal wires carrying activations: [ROWS][COLS+1]
    // Index [r][c] is the input to PE(r,c); Index [r][c+1] is the output of PE(r,c)
    logic signed [DATA_WIDTH-1:0] h_act [ROWS][COLS+1];

    // Vertical wires carrying partial sums: [ROWS+1][COLS]
    // Index [r][c] is the top input to PE(r,c); Index [r+1][c] is bottom output of PE(r,c)
    logic signed [ACC_WIDTH-1:0]  v_sum [ROWS+1][COLS];

    // Vertical wires for shifting weights during configuration: [ROWS+1][COLS]
    logic signed [DATA_WIDTH-1:0] v_weight [ROWS+1][COLS];

    // --------------------------------------------------------------------------
    // BOUNDARY HOOKUPS
    // Connect external module pins to the boundary of the internal wire grid
    // --------------------------------------------------------------------------
    generate
        // Left & Right boundaries for activations
        for (genvar r = 0; r < ROWS; r++) begin : gen_boundary_act
            // Connect skewed inputs to leftmost column (column 0)
            assign h_act[r][0]          = act_skewed[r];
            // Connect rightmost column outputs to module external pins
            assign activations_out[r]   = h_act[r][COLS];
        end

        // Top & Bottom boundaries for partial sums and weight shifting
        for (genvar c = 0; c < COLS; c++) begin : gen_boundary_sum_weight
            // Connect top partial sum inputs (tied to 0) to row 0
            assign v_sum[0][c]          = sum_in_top[c];
            // Connect bottom partial sum outputs from row ROWS to module pins
            assign sum_out_bot[c]       = v_sum[ROWS][c];
            // Connect external weight inputs to row 0 for shifting
            assign v_weight[0][c]       = weights_in[c];
        end
    endgenerate

    // --------------------------------------------------------------------------
    // 2D PROCESSING ELEMENT (PE) GRID INSTANTIATION
    // --------------------------------------------------------------------------
    generate
        // Iterate through all rows (r = 0 .. ROWS-1)
        for (genvar r = 0; r < ROWS; r++) begin : gen_pe_rows
            // Iterate through all columns (c = 0 .. COLS-1)
            for (genvar c = 0; c < COLS; c++) begin : gen_pe_cols
                // Instantiate a single PE at coordinate (r, c)
                pe #(
                    .DATA_WIDTH(DATA_WIDTH),
                    .ACC_WIDTH(ACC_WIDTH)
                ) u_pe (
                    .clk            (clk),
                    .rst_n          (rst_n),
                    .en             (en),
                    .weight_load_en (weight_load_en),
                    
                    // Vertical weight shifting (Top neighbor -> PE -> Bottom neighbor)
                    .weight_in      (v_weight[r][c]),
                    .weight_out     (v_weight[r+1][c]),
                    
                    // Horizontal activation propagation (Left neighbor -> PE -> Right neighbor)
                    .a_in           (h_act[r][c]),
                    .a_out          (h_act[r][c+1]),
                    
                    // Vertical partial sum accumulation (Top neighbor -> PE -> Bottom neighbor)
                    .sum_in         (v_sum[r][c]),
                    .sum_out        (v_sum[r+1][c])
                );
            end
        end
    endgenerate

// End of Systolic Array module
endmodule
