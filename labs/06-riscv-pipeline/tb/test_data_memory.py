
import cocotb
from cocotb.triggers import Timer


async def settle():
    await Timer(1, unit="ns")


async def tick(dut):
    dut.clk.value = 0
    await Timer(5, unit="ns")
    dut.clk.value = 1
    await Timer(5, unit="ns")
    dut.clk.value = 0
    await settle()


async def initialize(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    dut.mem_read.value = 0
    dut.mem_write.value = 0
    dut.address.value = 0
    dut.write_data.value = 0
    dut.funct3.value = 0

    await tick(dut)

    dut.rst.value = 0
    await settle()


async def store(dut, address, value, funct3):
    dut.mem_read.value = 0
    dut.mem_write.value = 1
    dut.address.value = address
    dut.write_data.value = value
    dut.funct3.value = funct3

    await settle()
    assert int(dut.alignment_error.value) == 0
    assert int(dut.access_error.value) == 0

    await tick(dut)
    dut.mem_write.value = 0
    await settle()


async def load(dut, address, funct3):
    dut.mem_write.value = 0
    dut.mem_read.value = 1
    dut.address.value = address
    dut.funct3.value = funct3

    await settle()
    assert int(dut.alignment_error.value) == 0
    assert int(dut.access_error.value) == 0

    return int(dut.read_data.value)


@cocotb.test()
async def test_word_store_load(dut):
    await initialize(dut)
    await store(dut, 0, 0x12345678, 0b010)
    assert await load(dut, 0, 0b010) == 0x12345678


@cocotb.test()
async def test_byte_store_load(dut):
    await initialize(dut)
    await store(dut, 16, 0xAB, 0b000)
    assert await load(dut, 16, 0b100) == 0xAB


@cocotb.test()
async def test_halfword_store_load(dut):
    await initialize(dut)
    await store(dut, 32, 0x1234, 0b001)
    assert await load(dut, 32, 0b101) == 0x1234


@cocotb.test()
async def test_signed_byte(dut):
    await initialize(dut)
    await store(dut, 48, 0x80, 0b000)
    assert await load(dut, 48, 0b000) == 0xFFFFFF80


@cocotb.test()
async def test_unsigned_byte(dut):
    await initialize(dut)
    await store(dut, 64, 0xFF, 0b000)
    assert await load(dut, 64, 0b100) == 0xFF


@cocotb.test()
async def test_signed_halfword(dut):
    await initialize(dut)
    await store(dut, 80, 0x8001, 0b001)
    assert await load(dut, 80, 0b001) == 0xFFFF8001


@cocotb.test()
async def test_unsigned_halfword(dut):
    await initialize(dut)
    await store(dut, 96, 0xFFFF, 0b001)
    assert await load(dut, 96, 0b101) == 0xFFFF


@cocotb.test()
async def test_little_endian(dut):
    await initialize(dut)
    await store(dut, 112, 0x12345678, 0b010)

    assert await load(dut, 112, 0b100) == 0x78
    assert await load(dut, 113, 0b100) == 0x56
    assert await load(dut, 114, 0b100) == 0x34
    assert await load(dut, 115, 0b100) == 0x12


@cocotb.test()
async def test_byte_overwrite(dut):
    await initialize(dut)
    await store(dut, 128, 0x11223344, 0b010)
    await store(dut, 129, 0xAA, 0b000)

    assert await load(dut, 128, 0b010) == 0x1122AA44


@cocotb.test()
async def test_misaligned_word(dut):
    await initialize(dut)

    dut.mem_read.value = 1
    dut.address.value = 1
    dut.funct3.value = 0b010

    await settle()

    assert int(dut.alignment_error.value) == 1
    assert int(dut.read_data.value) == 0


@cocotb.test()
async def test_misaligned_halfword(dut):
    await initialize(dut)

    dut.mem_read.value = 1
    dut.address.value = 3
    dut.funct3.value = 0b001

    await settle()

    assert int(dut.alignment_error.value) == 1


@cocotb.test()
async def test_out_of_range(dut):
    await initialize(dut)

    dut.mem_read.value = 1
    dut.address.value = 1024
    dut.funct3.value = 0b010

    await settle()

    assert int(dut.access_error.value) == 1
    assert int(dut.read_data.value) == 0


@cocotb.test()
async def test_invalid_load_function(dut):
    await initialize(dut)

    dut.mem_read.value = 1
    dut.funct3.value = 0b011

    await settle()

    assert int(dut.access_error.value) == 1
    assert int(dut.read_data.value) == 0


@cocotb.test()
async def test_reset_blocks_write(dut):
    await initialize(dut)

    await store(dut, 160, 0xCAFEBABE, 0b010)

    dut.rst.value = 1
    dut.mem_read.value = 0
    dut.mem_write.value = 1
    dut.address.value = 160
    dut.write_data.value = 0
    dut.funct3.value = 0b010

    await tick(dut)

    dut.rst.value = 0
    dut.mem_write.value = 0

    assert await load(dut, 160, 0b010) == 0xCAFEBABE


@cocotb.test()
async def test_multiple_words(dut):
    await initialize(dut)

    values = [
        0x12345678,
        0xABCDEF01,
        0xDEADBEEF,
        0x00000000,
        0xFFFFFFFF,
    ]

    for i, value in enumerate(values):
        await store(dut, 256 + i * 4, value, 0b010)

    for i, value in enumerate(values):
        assert await load(dut, 256 + i * 4, 0b010) == value
