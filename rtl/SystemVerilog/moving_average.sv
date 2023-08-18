// Implementation of the moving average filter based on equation
//  y[n] = y[n-1] - x[n-N] + x[n], N is the length of the filter, here N = 2**G_M_W

// Use BRAM(single port, read-first) to handle large filters where shift registers
// would not be efficient. Latency =3, Throughput = 1

`default_nettype none

module moving_average
    #(
        parameter int G_I_W = 6,
        parameter int G_M_W = 4,
        parameter int G_O_W = 10
    )

    (
        input logic i_clk,
        input logic i_rst,
        input logic i_ce,
        input logic [G_I_W -1 : 0] i_sample,
        output logic [G_O_W -1 : 0] o_result
    );

    logic [G_I_W - 1 : 0] mem [2**G_M_W];

    // only need 1 pointer for BRAM-based shift register
    logic [G_M_W - 1 : 0] r_addr;
    // register input sample to align with the latency of the BRAM
    logic [G_I_W - 1 : 0] r_sample;
    // data read from the RAM
    logic [G_I_W - 1 : 0] r_sample_delayed;
    // register that holds x[n] - x[n-N], 1 extra bit growth due to sub
    logic  signed [G_I_W : 0] r_sub;
    // register that holds y[n], width should be input width + clog2(N) to account for bit growth
    logic signed [G_O_W - 1 : 0] r_acc;
    logic signed [G_O_W - 1 : 0] r_acc_div;


    always_ff @(posedge i_clk) begin : mem_pointer
        if(i_rst) begin
            r_addr <= '0;
            r_sample <= '0;
        end else begin
            if(i_ce) begin
                r_addr <= r_addr + 1;
                r_sample <= i_sample;
            end
        end
    end


    always_ff @(posedge i_clk) begin : BRAM_write
        if(i_ce) begin
            mem[r_addr] <= i_sample;
        end
    end

    always_ff @(posedge i_clk) begin : BRAM_read
        if(i_ce) begin
            r_sample_delayed <= mem[r_addr];
        end
    end

    always_ff @(posedge i_clk) begin : MA_filter
        if(i_rst) begin
            r_sub <= '0;
            r_acc <= '0;
        end else begin
            if(i_ce) begin
                r_sub <= signed'((G_I_W+1)'(r_sample) - (G_I_W+1)'(r_sample_delayed));
                r_acc <= r_acc + G_O_W'(r_sub);
            end
        end
    end

    assign r_acc_div = r_acc >> G_M_W;
    assign o_result = r_acc_div;
endmodule : moving_average
