# Functional test for spi_master
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer,RisingEdge,FallingEdge,ClockCycles
from cocotb.result import TestFailure
from cocotb.binary import BinaryValue
import random
from cocotb_coverage.coverage import CoverCross,CoverPoint,coverage_db
from cocotb_coverage import crv 

g_i_W = int(cocotb.top.g_i_W)
g_m_W = int(cocotb.top.g_m_W)
g_o_W = int(cocotb.top.g_o_W)

g_sys_clk = 400000
period_ns = 10**9 / g_sys_clk

class crv_inputs(crv.Randomized):
	def __init__(self,data):
		crv.Randomized.__init__(self)
		self.data = data
		self.add_rand("data",list(range(0,2**(g_i_W-1))))
		# self.add_rand("data",list(range(-2**int(g_i_W/2), 2**int(g_i_W/2),1)))


covered_value = []

full = False
# #Callback function to capture the bin content showing
def notify_full():
	global full
	full = True

# at_least = value is superfluous, just shows how you can determine the amount of times that
# a bin must be hit to considered covered
# actually the bins must go up to 2**8 and also add other coverage criteria regarding other features
# here i just exercize the basic functionality
@CoverPoint("top.i_data",xf = lambda x : x, bins = list(range(0,2**(g_i_W-1))), at_least=1)
def number_cover(x):
	covered_value.append(x)

async def reset(dut,cycles=1):
	dut.i_rst.value = 1
	dut.i_ce.value = 0 
	dut.i_sample.value = 0
	await ClockCycles(dut.i_clk,cycles)
	dut.i_rst.value = 0
	await RisingEdge(dut.i_clk)
	dut._log.info("the core was reset")

@cocotb.test()
async def test(dut):
	"""Check results and coverage for spi_master"""

	cocotb.start_soon(Clock(dut.i_clk, period_ns, units="ns").start())
	await reset(dut,5)	


	moving_lst = []
	moving_avg = []

	inputs = crv_inputs(0)
	inputs.randomize()

	sample = 0
	result = 0

	dut.i_ce.value = 1
	if(inputs.data != 0):
		dut.i_sample.value = BinaryValue(value=inputs.data,bigEndian=False ,n_bits=g_i_W,binaryRepresentation=2)
	else:
		dut.i_sample.value = BinaryValue(value=str(0),bigEndian=False ,n_bits=g_i_W,binaryRepresentation=2)

	while(full != True):
		await RisingEdge(dut.i_clk)

		result = BinaryValue(value=str(dut.o_result.value),binaryRepresentation=2)
		sample = BinaryValue(value=str(dut.i_sample.value),binaryRepresentation=2)
		
		moving_avg.append(result.integer)
		moving_lst.append(sample.integer)
		number_cover(sample.integer)
		coverage_db["top.i_data"].add_threshold_callback(notify_full, 100)
		if(full == True):
			break
		else:
			# inputs.randomize()
			while (inputs.data in covered_value):
				inputs.randomize()
			if(inputs.data != 0):
				dut.i_sample.value = BinaryValue(value=inputs.data,bigEndian=False ,n_bits=g_i_W,binaryRepresentation=2)
			else:
				dut.i_sample.value = BinaryValue(value=str(0),bigEndian=False ,n_bits=g_i_W,binaryRepresentation=2)



	for i in range(3):
		await RisingEdge(dut.i_clk)
		result = BinaryValue(value=str(dut.o_result.value),binaryRepresentation=2)
		moving_avg.append(result.integer)
	
	for i in range(3):
		moving_avg.pop(0)

	for i in range(len(moving_lst)):
		if(i>= 2**g_m_W):
			# pass
			assert not (int(sum(moving_lst[(i-2**g_m_W +1):i+1]) / (2**g_m_W)) != moving_avg[i]),"Different expected to actual read data"
		else:
			assert not (int(sum(moving_lst[0:i+1]) / (2**g_m_W)) != moving_avg[i]),"Different expected to actual read data"

	coverage_db.report_coverage(cocotb.log.info,bins=True)
	coverage_db.export_to_xml(filename="coverage.xml")

		
