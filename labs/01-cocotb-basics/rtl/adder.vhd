library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity adder is
	port(
	 a : in std_logic_vector(7 downto 0);
	 b : in std_logic_vector(7 downto 0);
	 result : out std_logic_vector(8 downto 0)
	);
end entity adder;

architecture rtl of adder is
begin
	result <= std_logic_vector(
		unsigned('0' & a)+ unsigned('0' & b)
	);
end architecture rtl;
