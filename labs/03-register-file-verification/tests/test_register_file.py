import cocotb
import random

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


class RegisterFileModel:
    """Python reference model for the 8 x 8-bit register file."""

    def __init__(self):
        self.registers = [0] * 8

    def reset(self):
        """Clear all registers."""
        self.registers = [0] * 8

    def write(self, address, value):
        """Write an 8-bit value to a register."""
        self.registers[address] = value & 0xFF

    def read(self, address):
        """Read a register value."""
        return self.registers[address]


async def reset_dut(dut):
    """Reset the register file."""

    dut.write_enable.value = 0
    dut.write_addr.value = 0
    dut.write_data.value = 0

    dut.reset.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.reset.value = 0

async def write_register(dut, address, value):
    """Write a value into a register."""
    
    dut.reset.value=0
    dut.write_addr.value = address
    dut.write_data.value = value
    dut.write_enable.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    dut.write_enable.value = 0


async def check_register(dut, address, expected):
    """Read one register through both read ports and check its value."""

    dut.read_addr1.value = address
    dut.read_addr2.value = address

    await Timer(1, unit="ns")

    read1 = dut.read_data1.value.to_unsigned()
    read2 = dut.read_data2.value.to_unsigned()

    assert read1 == expected, (
        f"Port 1: register {address}, "
        f"expected {expected}, got {read1}"
    )

    assert read2 == expected, (
        f"Port 2: register {address}, "
        f"expected {expected}, got {read2}"
    )

async def compare_with_model(dut, model):
    """Compare every hardware register against the Python model."""

    for address in range(8):

        dut.read_addr1.value = address

        await Timer(1, unit="ns")

        actual = dut.read_data1.value.to_unsigned()
        expected = model.read(address)

        assert actual == expected, (
            f"Register {address} mismatch: "
            f"expected {expected}, got {actual}"
        )


@cocotb.test()
async def test_basic_write_and_read(dut):
    """Write one register and read it through both read ports."""

    # Start a 10 ns clock
    cocotb.start_soon(
        Clock(dut.clk, 10, unit="ns").start()
    )

    # Initial values
    dut.write_enable.value = 0
    dut.write_addr.value = 0
    dut.write_data.value = 0
    dut.read_addr1.value = 0
    dut.read_addr2.value = 0

    # Reset register file
    await reset_dut(dut)

    # Write value 42 into register 3
    dut.write_addr.value = 3
    dut.write_data.value = 42
    dut.write_enable.value = 1

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    # Disable writing
    dut.write_enable.value = 0

    # Read register 3 using both ports
    dut.read_addr1.value = 3
    dut.read_addr2.value = 3

    await Timer(1, unit="ns")

    read1 = dut.read_data1.value.to_unsigned()
    read2 = dut.read_data2.value.to_unsigned()

    assert read1 == 42, (
        f"Read port 1 expected 42, got {read1}"
    )

    assert read2 == 42, (
        f"Read port 2 expected 42, got {read2}"
    )


@cocotb.test()
async def test_reset_clears_registers(dut):
    """Verify that reset clears previously stored register values."""

    # Start clock
    cocotb.start_soon(
        Clock(dut.clk, 10, unit="ns").start()
    )

    # Initialize every DUT input
    dut.reset.value = 0
    dut.write_enable.value = 0
    dut.write_addr.value = 0
    dut.write_data.value = 0
    dut.read_addr1.value = 0
    dut.read_addr2.value = 0

    # Start from a known state
    await reset_dut(dut)

    # Write non-zero values
    await write_register(dut, 1, 25)
    await write_register(dut, 3, 100)
    await write_register(dut, 7, 255)

    # Confirm values were actually written
    await check_register(dut, 1, 25)
    await check_register(dut, 3, 100)
    await check_register(dut, 7, 255)

    # Reset again
    await reset_dut(dut)

    # Reset must clear every register
    for address in range(8):
        await check_register(dut, address, 0)


@cocotb.test()
async def test_write_enable(dut):
    """Verify that write_enable controls whether a write occurs."""

    cocotb.start_soon(
        Clock(dut.clk, 10, unit="ns").start()
    )

    # Initialize inputs
    dut.reset.value = 0
    dut.write_enable.value = 0
    dut.write_addr.value = 0
    dut.write_data.value = 0
    dut.read_addr1.value = 0
    dut.read_addr2.value = 0

    await reset_dut(dut)

    # Write 55 into register 4 normally
    await write_register(dut, 4, 55)
    await check_register(dut, 4, 55)

    # Try to overwrite register 4 while write_enable = 0
    dut.write_addr.value = 4
    dut.write_data.value = 200
    dut.write_enable.value = 0

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    # Register 4 must still contain 55
    await check_register(dut, 4, 55)


@cocotb.test()
async def test_all_registers(dut):
    """Write unique values to all registers and verify them."""

    cocotb.start_soon(
        Clock(dut.clk, 10, unit="ns").start()
    )

    dut.reset.value = 0
    dut.write_enable.value = 0
    dut.write_addr.value = 0
    dut.write_data.value = 0
    dut.read_addr1.value = 0
    dut.read_addr2.value = 0

    await reset_dut(dut)

    values = [
        11,
        22,
        33,
        44,
        55,
        66,
        77,
        88,
    ]

    # Fill the entire register file
    for address in range(8):
        await write_register(
            dut,
            address,
            values[address]
        )

    # Check every register
    for address in range(8):
        await check_register(
            dut,
            address,
            values[address]
        )



@cocotb.test()
async def test_register_overwrite(dut):
    """Verify repeated writes to the same register."""

    cocotb.start_soon(
        Clock(dut.clk, 10, unit="ns").start()
    )

    dut.reset.value = 0
    dut.write_enable.value = 0
    dut.write_addr.value = 0
    dut.write_data.value = 0
    dut.read_addr1.value = 0
    dut.read_addr2.value = 0

    await reset_dut(dut)

    # First value
    await write_register(dut, 5, 40)
    await check_register(dut, 5, 40)

    # First overwrite
    await write_register(dut, 5, 150)
    await check_register(dut, 5, 150)

    # Second overwrite
    await write_register(dut, 5, 255)
    await check_register(dut, 5, 255)

    # Overwrite with zero
    await write_register(dut, 5, 0)
    await check_register(dut, 5, 0)



@cocotb.test()
async def test_reference_model(dut):
    """Verify hardware state against a Python reference model."""

    cocotb.start_soon(
        Clock(dut.clk, 10, unit="ns").start()
    )

    dut.reset.value = 0
    dut.write_enable.value = 0
    dut.write_addr.value = 0
    dut.write_data.value = 0
    dut.read_addr1.value = 0
    dut.read_addr2.value = 0

    model = RegisterFileModel()

    # Reset hardware and model
    await reset_dut(dut)
    model.reset()

    await compare_with_model(dut, model)

    # Write R2
    await write_register(dut, 2, 42)
    model.write(2, 42)

    await compare_with_model(dut, model)

    # Write R5
    await write_register(dut, 5, 200)
    model.write(5, 200)

    await compare_with_model(dut, model)

    # Overwrite R2
    await write_register(dut, 2, 100)
    model.write(2, 100)

    await compare_with_model(dut, model)

    # Write R7
    await write_register(dut, 7, 255)
    model.write(7, 255)

    await compare_with_model(dut, model)

    # Reset everything again
    await reset_dut(dut)
    model.reset()

    await compare_with_model(dut, model)


@cocotb.test()
async def test_random_stateful_operations(dut):
    """Run randomized writes, disabled writes, reads, and resets."""

    cocotb.start_soon(
        Clock(dut.clk, 10, unit="ns").start()
    )

    dut.reset.value = 0
    dut.write_enable.value = 0
    dut.write_addr.value = 0
    dut.write_data.value = 0
    dut.read_addr1.value = 0
    dut.read_addr2.value = 0

    model = RegisterFileModel()

    await reset_dut(dut)
    model.reset()

    for _ in range(1000):

        operation = random.choice([
            "write",
            "disabled_write",
            "read",
            "reset",
        ])

        if operation == "write":

            address = random.randint(0, 7)
            value = random.randint(0, 255)

            await write_register(dut, address, value)
            model.write(address, value)

        elif operation == "disabled_write":

            address = random.randint(0, 7)
            value = random.randint(0, 255)

            dut.write_addr.value = address
            dut.write_data.value = value
            dut.write_enable.value = 0

            await RisingEdge(dut.clk)
            await Timer(1, unit="ns")

            # Model intentionally remains unchanged.

        elif operation == "read":

            address1 = random.randint(0, 7)
            address2 = random.randint(0, 7)

            dut.read_addr1.value = address1
            dut.read_addr2.value = address2

            await Timer(1, unit="ns")

            actual1 = dut.read_data1.value.to_unsigned()
            actual2 = dut.read_data2.value.to_unsigned()

            assert actual1 == model.read(address1), (
                f"Port 1 mismatch at R{address1}: "
                f"expected {model.read(address1)}, got {actual1}"
            )

            assert actual2 == model.read(address2), (
                f"Port 2 mismatch at R{address2}: "
                f"expected {model.read(address2)}, got {actual2}"
            )

        elif operation == "reset":

            await reset_dut(dut)
            model.reset()

        # Check complete hardware state after every operation
        await compare_with_model(dut, model)


@cocotb.test()
async def test_waveform_demo(dut):
    """Short sequence for register-file waveform inspection."""

    cocotb.start_soon(
        Clock(dut.clk, 10, unit="ns").start()
    )

    dut.reset.value = 0
    dut.write_enable.value = 0
    dut.write_addr.value = 0
    dut.write_data.value = 0
    dut.read_addr1.value = 0
    dut.read_addr2.value = 0

    # Reset
    await reset_dut(dut)

    # Write R1 = 25
    await write_register(dut, 1, 25)

    # Write R3 = 100
    await write_register(dut, 3, 100)

    # Read R1 and R3 simultaneously
    dut.read_addr1.value = 1
    dut.read_addr2.value = 3
    await Timer(5, unit="ns")

    assert dut.read_data1.value.to_unsigned() == 25
    assert dut.read_data2.value.to_unsigned() == 100

    # Overwrite R1
    await write_register(dut, 1, 200)

    dut.read_addr1.value = 1
    await Timer(5, unit="ns")

    assert dut.read_data1.value.to_unsigned() == 200

    # Reset again
    await reset_dut(dut)

    dut.read_addr1.value = 1
    dut.read_addr2.value = 3
    await Timer(5, unit="ns")

    assert dut.read_data1.value.to_unsigned() == 0
    assert dut.read_data2.value.to_unsigned() == 0
