/**
 * @ Author: German Cano Quiveu, germancq
 * @ Create Time: 2019-10-17 16:29:42
 * @ Modified by: Your name
 * @ Modified time: 2020-04-13 21:51:05
 * @ Description:
 */


module KDF_hirose_present #(
    parameter SALT_WIDTH = 64,
    parameter COUNT_WIDTH = 32,
    parameter PSW_WIDTH = 32
)
(
    input clk,
    input rst,
    input [SALT_WIDTH-1:0] salt,
    input [COUNT_WIDTH-1:0] count,
    input [PSW_WIDTH-1:0] user_password,
    output end_signal,
    output [127:0] key_derivated
);

    localparam DATA_WIDTH = SALT_WIDTH + PSW_WIDTH + COUNT_WIDTH;
    
    logic [DATA_WIDTH-1:0] hash_input;
    logic [127:0] hash_output;
    logic hash_end_signal;

    assign hash_input = counter_output == 0 ? {user_password,salt,count} : { {DATA_WIDTH-128{1'b0}}, register_output};

    assign key_derivated = register_output;

    assign end_signal = counter_output == count ? 1 : 0;

    hirose_present_wrapper #(.DATA_WIDTH(DATA_WIDTH)) hash_impl(
        .clk(clk),
        .rst(rst | hash_end_signal),
        .plaintext(hash_input),
        .c(64'h1234567812345678),
        .hash_output(hash_output),
        .end_signal(hash_end_signal)
    );

    
    logic [31:0] counter_output;
    logic counter_up;

    counter #(.DATA_WIDTH(32)) counter_impl(
        .clk(clk),
        .rst(rst),
        .up(hash_end_signal),
        .down(1'b0),
        .din(32'h0),
        .dout(counter_output)
    );

    
    logic [127:0] register_output;

    register #(.DATA_WIDTH(128)) register_data(
        .clk(clk),
        .cl(rst),
        .w(hash_end_signal),
        .din(hash_output),
        .dout(register_output)
    );

    

endmodule : KDF_hirose_present