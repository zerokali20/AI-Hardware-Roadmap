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
@cocotb.test()
async def test_edge_cases(dut):
	"""Test important boundary and overflow cases."""
	
	test_cases=[
		(0,0),
		(0,1),
		(1,0),
		(1,1),
		(127,1),
		(128,128),
		(254,1),
		(255,0),
		(0,255),
		(255,1),
		(255,255),
	]

	for a,b in test_cases:
		dut.a.value=a
		dut.b.value=b

		await Timer(1,unit="ns")

		expected = a+b
		actual = dut.result.value.to_unsigned()

		assert actual == expected, (
			f"Edge case failed: {a}+ {b}, "
			f"expected {expected}, got {actual}"
		)

