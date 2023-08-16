--Implementation of the moving average filter based on equation
-- y[n] = y[n-1] - x[n-N] + x[n], N is the length of the filter, here N = 2**g_m_w

--Use BRAM(single port, read-first) to handle large filters where shift registers
--would not be efficient. Latency =3, Throughput = 1 

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity moving_average is
	generic(
		g_i_W : natural :=6;										--input width
		g_m_w : natural :=4;										--memory address width
		g_o_w : natural :=10);										--output width
	port(						
		i_clk : in std_ulogic;									--system clock
		i_rst : in std_ulogic;									--reset
		i_ce  : in std_ulogic;									--valid data on input
		i_sample : in std_ulogic_vector(g_i_W -1 downto 0);		--incomming samples
		o_result : out std_ulogic_vector(g_o_w -1 downto 0));	--filter result
end moving_average;

architecture rtl of moving_average is
	type mem_type is array(0 to 2**g_m_w -1) of std_ulogic_vector(g_i_W -1 downto 0);
	signal mem : mem_type :=(others => (others => '0'));

	--only need 1 pointer for BRAM-based shift register
	signal r_addr  : unsigned(g_m_w -1 downto 0);		
	--register input sample to align with the latency of the RAM							
	signal r_sample : std_ulogic_vector(g_i_W -1 downto 0) :=(others => '0');
	--data read from the RAM	
	signal r_sample_delN : std_ulogic_vector(g_i_W -1 downto 0) :=(others => '0');
	--register that holds x[n] - x[n-N], 1 extra bit growth due to sub
	signal r_sub : signed(g_i_W downto 0);		
	--register that holds y[n], width should be input width + clog2(N)	to account for bit growth	    				
	signal r_acc : signed(g_o_w -1 downto 0);

	signal r_acc_div : signed(g_o_w -1 downto 0);
begin

	--manage mem pointer when valid data on bus
	mem_pointer : process(i_clk)
	begin
		if(i_rst = '1') then
			r_addr <= (others => '0');
			r_sample <= (others => '0');
		elsif (rising_edge(i_clk)) then
			if(i_ce = '1') then
				r_addr <= r_addr + 1;
				r_sample <= i_sample;
			end if;
		end if;
	end process; -- mem_pointer

	--write input data to BRAM
	write_mem : process(i_clk)
	begin
		if(rising_edge(i_clk)) then
			if(i_ce = '1') then
				mem(to_integer(r_addr)) <= i_sample;
			end if;
		end if;
	end process; -- write_mem

	--read from BRAM
	read_mem : process(i_clk)
	begin
		if(rising_edge(i_clk)) then
			if(i_ce = '1') then
				r_sample_delN <= mem(to_integer(r_addr));
			end if;
		end if;
	end process; -- read_mem

	--perform the moving average filter operation
	mov_avg : process(i_clk)
	begin
		if(i_rst = '1') then
			r_sub <= (others => '0');
			r_acc <= (others => '0');
		elsif(rising_edge(i_clk)) then
			if(i_ce = '1') then
				r_sub <=  resize(signed(r_sample),r_sub'length) - resize(signed(r_sample_delN),r_sub'length);
				r_acc <= r_acc + r_sub; 
			end if;
		end if;
	end process; -- mov_avg

	--divide by N
	r_acc_div <= shift_right(r_acc,g_m_w);
	o_result <= std_ulogic_vector(r_acc_div);
end rtl;