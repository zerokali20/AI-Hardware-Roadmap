library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity alu is
    port (
        a      : in  std_logic_vector(7 downto 0);
        b      : in  std_logic_vector(7 downto 0);
        opcode : in  std_logic_vector(2 downto 0);

        result : out std_logic_vector(7 downto 0);
        zero   : out std_logic;
        carry  : out std_logic
    );
end entity alu;


architecture rtl of alu is

    signal result_internal : std_logic_vector(7 downto 0);
    signal carry_internal  : std_logic;

begin

    process(a, b, opcode)

        variable temp : unsigned(8 downto 0);

    begin

        result_internal <= (others => '0');
        carry_internal  <= '0';

        case opcode is

            -- ADD
            when "000" =>
                temp := unsigned('0' & a) + unsigned('0' & b);

                result_internal <= std_logic_vector(temp(7 downto 0));
                carry_internal  <= temp(8);


            -- SUB
            when "001" =>
                result_internal <= std_logic_vector(
                    unsigned(a) - unsigned(b)
                );


            -- AND
            when "010" =>
                result_internal <= a and b;


            -- OR
            when "011" =>
                result_internal <= a or b;


            -- XOR
            when "100" =>
                result_internal <= a xor b;


            -- Shift Left Logical
            when "101" =>
                result_internal <= std_logic_vector(
                    shift_left(unsigned(a), 1)
                );


            -- Shift Right Logical
            when "110" =>
                result_internal <= std_logic_vector(
                    shift_right(unsigned(a), 1)
                );


            -- Set Less Than
            when "111" =>

                if unsigned(a) < unsigned(b) then
                    result_internal <= "00000001";
                else
                    result_internal <= "00000000";
                end if;


            when others =>
                result_internal <= (others => '0');

        end case;

    end process;


    result <= result_internal;
    carry  <= carry_internal;

    zero <= '1' when result_internal = "00000000"
            else '0';

end architecture rtl;