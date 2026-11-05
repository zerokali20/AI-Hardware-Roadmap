
import random

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
    await Timer(1, unit="ns")


async def initialize(dut):
    dut.clk.value = 0
    dut.rst.value = 1
    dut.reg_write.value = 0
    dut.write_addr.value = 0
    dut.write_data.value = 0
    dut.read_addr1.value = 0
    dut.read_addr2.value = 0
    await tick(dut)
    dut.rst.value = 0


async def write_register(dut, address, value):
    dut.reg_write.value = 1
    dut.write_addr.value = address
    dut.write_data.value = value
    await tick(dut)
    dut.reg_write.value = 0


async def read_register(dut, address, port=1):
    if port == 1:
        dut.read_addr1.value = address
        await settle()
        return int(dut.read_data1.value)

    dut.read_addr2.value = address
    await settle()
    return int(dut.read_data2.value)


@cocotb.test()
async def test_reset(dut):
    await initialize(dut)

    for address in range(32):
        assert await read_register(dut, address) == 0


@cocotb.test()
async def test_single_write(dut):
    await initialize(dut)
    await write_register(dut, 5, 0x12345678)

    assert await read_register(dut, 5) == 0x12345678


@cocotb.test()
async def test_dual_read(dut):
    await initialize(dut)
    await write_register(dut, 3, 0x11111111)
    await write_register(dut, 7, 0x22222222)

    dut.read_addr1.value = 3
    dut.read_addr2.value = 7
    await settle()

    assert int(dut.read_data1.value) == 0x11111111
    assert int(dut.read_data2.value) == 0x22222222


@cocotb.test()
async def test_zero_register(dut):
    await initialize(dut)
    await write_register(dut, 0, 0xFFFFFFFF)

    assert await read_register(dut, 0) == 0


@cocotb.test()
async def test_write_disabled(dut):
    await initialize(dut)
    await write_register(dut, 8, 0xAAAAAAAA)

    dut.reg_write.value = 0
    dut.write_addr.value = 8
    dut.write_data.value = 0x55555555
    await tick(dut)

    assert await read_register(dut, 8) == 0xAAAAAAAA


@cocotb.test()
async def test_overwrite(dut):
    await initialize(dut)

    await write_register(dut, 10, 0x11111111)
    await write_register(dut, 10, 0x22222222)

    assert await read_register(dut, 10) == 0x22222222


@cocotb.test()
async def test_all_registers(dut):
    await initialize(dut)

    for address in range(1, 32):
        await write_register(dut, address, address * 100)

    for address in range(1, 32):
        actual = await read_register(dut, address)
        assert actual == address * 100


@cocotb.test()
async def test_randomized_operations(dut):
    await initialize(dut)

    rng = random.Random(42)
    expected = [0] * 32

    for _ in range(200):
        address = rng.randrange(32)
        value = rng.getrandbits(32)

        await write_register(dut, address, value)

        if address != 0:
            expected[address] = value

        read_address1 = rng.randrange(32)
        read_address2 = rng.randrange(32)

        dut.read_addr1.value = read_address1
        dut.read_addr2.value = read_address2
        await settle()

        assert int(dut.read_data1.value) == expected[read_address1]
        assert int(dut.read_data2.value) == expected[read_address2]


@cocotb.test()
async def test_reset_after_writes(dut):
    await initialize(dut)

    await write_register(dut, 4, 0xDEADBEEF)
    await write_register(dut, 9, 0xCAFEBABE)

    dut.rst.value = 1
    await tick(dut)
    dut.rst.value = 0

    assert await read_register(dut, 4) == 0
    assert await read_register(dut, 9) == 0


@cocotb.test()
async def test_reset_priority(dut):
    await initialize(dut)

    dut.rst.value = 1
    dut.reg_write.value = 1
    dut.write_addr.value = 5
    dut.write_data.value = 0x12345678

    await tick(dut)

    assert await read_register(dut, 5) == 0
