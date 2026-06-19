/**
 * @ Author: German Cano Quiveu, germancq
 * @ Create Time: 2020-01-07 12:16:24
 * @ Modified by: Your name
 * @ Modified time: 2020-04-21 14:20:37
 * @ Description:
 */

module KDF_spongent #(
    parameter N = 88,
    parameter c = 80,
    parameter r = 8,
    parameter R = 45,
    parameter lCounter_initial_state = 6'h05,
    parameter lCounter_feedback_coeff = 7'h61,
    parameter SALT_WIDTH = 64,
    parameter COUNT_WIDTH = 32,
    parameter PSW_WIDTH = 80
)
(
    input clk,
    input rst,
    input [SALT_WIDTH-1:0] salt,
    input [COUNT_WIDTH-1:0] count,
    input [PSW_WIDTH-1:0] user_password,
    output end_signal,
    output [N-1:0] key_derivated
);

    localparam DATA_WIDTH = SALT_WIDTH + COUNT_WIDTH + PSW_WIDTH;
    
    logic [DATA_WIDTH-1:0] hash_input;
    logic [N-1:0] hash_output;
    logic hash_end_signal;
    logic rst_hash;

    assign hash_input = counter_output == 0 ? {user_password,salt,count} : register_output;

    assign key_derivated = register_output;

    assign end_signal = counter_output == count ? 1 : 0;

    spongent #(.DATA_WIDTH(DATA_WIDTH),
               .N(N),
               .c(c),
               .r(r),
               .R(R),
               .lCounter_feedback_coeff(lCounter_feedback_coeff),
               .lCounter_initial_state(lCounter_initial_state)
    )hash_impl(
        .clk(clk),
        .rst(rst | rst_hash),
        .msg(hash_input),
        .hash(hash_output),
        .end_hash(hash_end_signal)
    );

    
    logic [COUNT_WIDTH-1:0] counter_output;
    logic counter_up;

    counter #(.DATA_WIDTH(COUNT_WIDTH)) counter_impl(
        .clk(clk),
        .rst(rst),
        .up(~hash_end_signal && rst_hash),
        .down(1'b0),
        .din({COUNT_WIDTH{1'b0}}),
        .dout(counter_output)
    );

    
    
     logic [N-1:0] register_output;
     register #(.DATA_WIDTH(N)) register_data(
        .clk(clk),
        .cl(rst),
        .w(hash_end_signal),
        .din(hash_output),
        .dout(register_output)
    );

    always_ff @(posedge clk) begin
        if(hash_end_signal) begin
            rst_hash <= 1;
        end
        else begin
            rst_hash <= 0;
        end
    end
    
    

endmodule : KDF_spongent