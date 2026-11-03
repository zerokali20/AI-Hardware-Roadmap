library ieee;
use ieee.std_logic_1164.all;

entity rv32i_decoder is
    port (
        instruction : in  std_logic_vector(31 downto 0);

        opcode       : out std_logic_vector(6 downto 0);
        rd           : out std_logic_vector(4 downto 0);
        funct3       : out std_logic_vector(2 downto 0);
        rs1          : out std_logic_vector(4 downto 0);
        rs2          : out std_logic_vector(4 downto 0);
        funct7       : out std_logic_vector(6 downto 0);

        immediate    : out std_logic_vector(31 downto 0)
    );
end entity rv32i_decoder;


architecture rtl of rv32i_decoder is
begin

    ----------------------------------------------------------------
    -- Common instruction fields
    ----------------------------------------------------------------

    opcode <= instruction(6 downto 0);

    rd <= instruction(11 downto 7);

    funct3 <= instruction(14 downto 12);

    rs1 <= instruction(19 downto 15);

    rs2 <= instruction(24 downto 20);

    funct7 <= instruction(31 downto 25);


    ----------------------------------------------------------------
    -- Immediate decoder
    ----------------------------------------------------------------
    --
    -- At the current stage of Lab 04, we decode I-type
    -- immediates only.
    --
    -- Supported opcode groups:
    --
    -- 0010011 : I-type arithmetic
    --           ADDI, SLTI, SLTIU, XORI, ORI, ANDI,
    --           SLLI, SRLI, SRAI
    --
    -- 0000011 : Load instructions
    --           LB, LH, LW, LBU, LHU
    --
    -- 1100111 : JALR
    --
    ----------------------------------------------------------------

    process(instruction)
    begin

        -- Default immediate value
        immediate <= (others => '0');

        case instruction(6 downto 0) is

            --------------------------------------------------------
            -- I-type arithmetic
            --------------------------------------------------------

            when "0010011" =>

                -- Sign extend instruction[31:20]
                -- from 12 bits to 32 bits.

                immediate <=
                    (31 downto 12 => instruction(31))
                    & instruction(31 downto 20);


            --------------------------------------------------------
            -- I-type loads
            --------------------------------------------------------

            when "0000011" =>

                immediate <=
                    (31 downto 12 => instruction(31))
                    & instruction(31 downto 20);


            --------------------------------------------------------
            -- JALR
            --------------------------------------------------------

            when "1100111" =>

                immediate <=
                    (31 downto 12 => instruction(31))
                    & instruction(31 downto 20);

            --------------------------------------------------------
            -- S-type stores
            --------------------------------------------------------

            when "0100011" =>

                immediate <=
                    (31 downto 12 => instruction(31))
                    & instruction(31 downto 25)
                    & instruction(11 downto 7);

            --------------------------------------------------------
            -- B-type branches
            --------------------------------------------------------

            when "1100011" =>

                immediate <=
                    (31 downto 13 => instruction(31))
                    & instruction(31)
                    & instruction(7)
                    & instruction(30 downto 25)
                    & instruction(11 downto 8)
                    & '0';

            --------------------------------------------------------
            -- Other instruction formats
            --------------------------------------------------------

            when others =>

                immediate <= (others => '0');

        end case;

    end process;

end architecture rtl;