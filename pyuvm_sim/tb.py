from cocotb.triggers import Timer, RisingEdge, ClockCycles
from cocotb_coverage import crv
from cocotb.clock import Clock
from cocotb.queue import QueueEmpty, QueueFull, Queue
from cocotb_coverage.coverage import CoverCross,CoverPoint,coverage_db
from pyuvm import *
import random
import cocotb
import pyuvm
from utils import AverageBfm
from cocotb_coverage.coverage import CoverCross,CoverPoint,coverage_db
from cocotb.binary import BinaryValue
import numpy as np

g_i_W = int(cocotb.top.g_i_W)
g_m_W = int(cocotb.top.g_m_W)
g_o_W = int(cocotb.top.g_o_W)


g_sys_clk = 400000
period_ns = 10**9 / g_sys_clk


covered_values = []


# at_least = value is superfluous, just shows how you can determine the amount of times that
# a bin must be hit to considered covered
@CoverPoint("top.data",xf = lambda x : x.data,bins = list(range(0,2**(g_i_W-1))),at_least=1)
def number_cover(dut):
    pass

class crv_inputs(crv.Randomized):
    def __init__(self,data):
        crv.Randomized.__init__(self)
        self.data = data
        self.add_rand("data",list(range(0,2**(g_i_W-1))))

# Sequence item
class SeqItem(uvm_sequence_item):

    def __init__(self, name,data):
        super().__init__(name)
        self.i_crv = crv_inputs(data)
        self.ce = 1

    def randomize_operands(self):
        self.i_crv.randomize()


# Sequence that generates items coverage-based
# Until we have covered the whole input space
class RandomSeq(uvm_sequence):
    async def body(self):
        while len(covered_values) != 2**(g_i_W-1):
            data_tr = SeqItem("data_tr",None)
            await self.start_item(data_tr)
            data_tr.randomize_operands()
            while(data_tr.i_crv.data in covered_values):
                data_tr.randomize_operands()
            covered_values.append(data_tr.i_crv.data)

            number_cover(data_tr.i_crv)
            await self.finish_item(data_tr)

# A virtual sequence that starts other sequences
# The sequencer that starts the non-virtual sequences 
# Is not virtual here, but an actual sequencer handle
# That we retrieve from the config. db
class TestAllSeq(uvm_sequence):

    async def body(self):
        seqr = ConfigDB().get(None, "", "SEQR")
        random = RandomSeq("random")
        await random.start(seqr)
 
class Driver(uvm_driver):

    def start_of_simulation_phase(self):
        self.bfm = AverageBfm()

    async def launch_tb(self):
        await self.bfm.reset()
        self.bfm.start_bfm()

    async def run_phase(self):
        await self.launch_tb()
        while True:
            data = await self.seq_item_port.get_next_item()
            if(data != 0):
                sample = BinaryValue(value=data.i_crv.data,bigEndian=False ,n_bits=g_i_W,binaryRepresentation=2)
            else:
                sample = BinaryValue(value=str(0),bigEndian=False ,n_bits=g_i_W,binaryRepresentation=2)
            await self.bfm.send_data((data.ce,sample.integer))
            self.seq_item_port.item_done()


class Coverage(uvm_subscriber):

    def end_of_elaboration_phase(self):
        self.cvg = set()

    def write(self, data):
        if((int(data)) not in self.cvg):
            self.cvg.add(int(data))

    def report_phase(self):
        try:
            disable_errors = ConfigDB().get(
                self, "", "DISABLE_COVERAGE_ERRORS")
        except UVMConfigItemNotFound:
            disable_errors = False
        if not disable_errors:
            if len(set(covered_values) - self.cvg) > 0:
                self.logger.error(
                    f"Functional coverage error. Missed: {set(covered_values)-self.cvg}")   
                assert False
            else:
                self.logger.info("Covered all input space ({})".format(len(self.cvg)))
                assert True


class Scoreboard(uvm_component):
    def __init__(self,name,parent):
        super().__init__(name,parent)
        self.idx =0 


    def build_phase(self):
        self.data_fifo = uvm_tlm_analysis_fifo("data_fifo", self)
        self.result_fifo = uvm_tlm_analysis_fifo("result_fifo", self)
        self.data_get_port = uvm_get_port("data_get_port", self)
        self.result_get_port = uvm_get_port("result_get_port", self)
        self.data_export = self.data_fifo.analysis_export
        self.result_export = self.result_fifo.analysis_export


    def connect_phase(self):
        self.data_get_port.connect(self.data_fifo.get_export)
        self.result_get_port.connect(self.result_fifo.get_export)

    def check_phase(self):
        passed = True
        idx = 0
        moving_lst = []
        moving_avg = []

        try:
            self.errors = ConfigDB().get(self, "", "CREATE_ERRORS")
        except UVMConfigItemNotFound:
            self.errors = False

        # HOW MANY ITERATIONS THIS RUNS HAS TO DO WITH THE "DRAIN TIME"
        # WE LET FOR THE LAST TRANSACTION TO FINISH
        while self.result_get_port.can_get():
            _, actual_result = self.result_get_port.try_get()
            data_success, data = self.data_get_port.try_get()

            sample = BinaryValue(value=str(data),binaryRepresentation=2)
            moving_lst.append(sample.integer)
            result = BinaryValue(value=str(actual_result),binaryRepresentation=2)
            moving_avg.append(result.integer)

            if not data_success:
                self.logger.critical(f"result {actual_result} had no command")
            else:

                if(idx >= 2**g_m_W):
                    if(int(sum(moving_lst[(idx-2**g_m_W +1):idx+1]) / (2**g_m_W)) == moving_avg[idx]):
                        self.logger.info("PASSED")
                    else:
                        self.logger.error("FAILED, mov_lst {}, mov_avg {}".format(int(sum(moving_lst[(idx-2**g_m_W +1):idx+1]) / (2**g_m_W)),moving_avg[idx]))
                        passed = False
                idx += 1
                self.logger.info("idx is {}".format(idx))
        assert passed

class Monitor(uvm_component):
    def __init__(self, name, parent, method_name):
        super().__init__(name, parent)
        self.method_name = method_name

    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)
        self.bfm = AverageBfm()
        self.get_method = getattr(self.bfm, self.method_name)

    async def run_phase(self):
        while True:
            datum = await self.get_method()
            self.logger.debug(f"MONITORED {datum}")
            self.ap.write(datum)


class Env(uvm_env):

    def build_phase(self):
        self.seqr = uvm_sequencer("seqr", self)
        ConfigDB().set(None, "*", "SEQR", self.seqr)
        self.driver = Driver.create("driver", self)
        self.result_mon = Monitor("result_mon", self, "get_result")
        self.data_mon = Monitor("data_mon", self, "get_data")
        self.coverage = Coverage("coverage", self)
        self.scoreboard = Scoreboard("scoreboard", self)

    def connect_phase(self):
        self.driver.seq_item_port.connect(self.seqr.seq_item_export)
        self.data_mon.ap.connect(self.scoreboard.data_export)
        self.data_mon.ap.connect(self.coverage.analysis_export)
        self.result_mon.ap.connect(self.scoreboard.result_export)


@pyuvm.test()
class Test(uvm_test):
    """Test moving average filter with random data"""
    """Constrained random test generation for sample values"""
    """Test generation ends when required coverage of input values is achieved"""
    def build_phase(self):
        self.env = Env("env", self)

    def end_of_elaboration_phase(self):
        self.test_all = TestAllSeq.create("test_all")

    async def run_phase(self):
        self.raise_objection()
        cocotb.start_soon(Clock(cocotb.top.i_clk, period_ns, units="ns").start())
        # Start/Execute the virtual sequence
        # When no sequencer handle is provided in start method of a sequence
        # Then start() just executes the relevant body() method
        await self.test_all.start()
        await ClockCycles(cocotb.top.i_clk, 50)  # TO DO LAST TRANSACTION

        coverage_db.report_coverage(cocotb.log.info,bins=True)
        coverage_db.export_to_xml(filename="coverage.xml")
        self.drop_objection()

