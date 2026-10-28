import random
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_basic_addition(dut):
	"""Test the adder with 1000 random input combinations."""
	for _ in range (1000):
		a = random.randint(0,255)
		b = random.randint(0,255)
		
		dut.a.value=a
		dut.b.value=b
		await Timer(1,unit="ns")
		
		expected = a+b
		actual = dut.result.value.to_unsigned()

		assert actual == expected, (
			f"Failed: {a} + {b},"
			f"expected {expected}, got {actual}"
		)
