library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity register_file is
    port (
        clk          : in  std_logic;
        reset        : in  std_logic;
        write_enable : in  std_logic;

        write_addr   : in  std_logic_vector(2 downto 0);
        write_data   : in  std_logic_vector(7 downto 0);

        read_addr1   : in  std_logic_vector(2 downto 0);
        read_addr2   : in  std_logic_vector(2 downto 0);

        read_data1   : out std_logic_vector(7 downto 0);
        read_data2   : out std_logic_vector(7 downto 0)
    );
end entity register_file;


architecture rtl of register_file is

    type register_array is array (0 to 7)
        of std_logic_vector(7 downto 0);

    signal registers : register_array :=
        (others => (others => '0'));

begin

    -- Synchronous write and reset
    process(clk)
    begin
        if rising_edge(clk) then

            if reset = '1' then
                registers <= (others => (others => '0'));

            elsif write_enable = '1' then
                registers(to_integer(unsigned(write_addr)))
                    <= write_data;

            end if;

        end if;
    end process;


    -- Asynchronous read ports
    read_data1 <= registers(
        to_integer(unsigned(read_addr1))
    );

    read_data2 <= registers(
        to_integer(unsigned(read_addr2))
    );

end architecture rtl;
