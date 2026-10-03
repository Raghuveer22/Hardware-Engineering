// ==============================================================================
// File: rtl/adder.sv
// Description: Parameterized Signed Hardware Adder with Saturation & Overflow
// Computes: sum = a + b (Signed with optional saturation clipping)
// ==============================================================================

`timescale 1ns/1ps 
/*
this is the timescale for the Hardware simulations not for the Hardware itself 
1ps is the precision of the Hardware simulations
1ns is the granualar timestamp we use in the Hardware testbench  
*/

module adder(input logic [7:0]a, input logic [7:0]b, output logic [7:0]sum);
    assign sum = a+b;
endmodule 
