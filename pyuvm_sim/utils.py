from cocotb.triggers import Timer,RisingEdge,ClockCycles
from cocotb.queue import QueueEmpty, Queue
import cocotb
import enum
import random
from cocotb_coverage import crv 
from cocotb_coverage.coverage import CoverCross,CoverPoint,coverage_db
from pyuvm import utility_classes
from cocotb.binary import BinaryValue


class AverageBfm(metaclass=utility_classes.Singleton):
    def __init__(self):
        self.dut = cocotb.top
        self.driver_queue = Queue(maxsize=1)
        self.data_mon_queue = Queue(maxsize=0)
        self.result_mon_queue = Queue(maxsize=0)

    async def send_data(self, data):
        await self.driver_queue.put(data)

    async def get_data(self):
        data = await self.data_mon_queue.get()
        return data

    async def get_result(self):
        result = await self.result_mon_queue.get()
        return result

    async def reset(self):
        await RisingEdge(self.dut.i_clk)
        self.dut.i_rst.value = 1
        self.dut.i_ce.value = 0
        self.dut.i_sample.value = 0
        await ClockCycles(self.dut.i_clk,5)
        self.dut.i_rst.value = 0
        await RisingEdge(self.dut.i_clk)

    async def driver_bfm(self):
        while True:
            try:
                (i_ce,i_sample) = self.driver_queue.get_nowait()
                self.dut.i_ce.value = i_ce
                self.dut.i_sample.value = i_sample
                
            except QueueEmpty:
                pass
            
            await RisingEdge(self.dut.i_clk)

    async def data_mon_bfm(self):
        await RisingEdge(self.dut.i_ce)
        while True:
            data = self.dut.i_sample.value
            # sample = BinaryValue(value=str(data),binaryRepresentation=2)
            # self.data_mon_queue.put_nowait(sample.integer)
            self.data_mon_queue.put_nowait(data)
            await RisingEdge(self.dut.i_clk)


    async def result_mon_bfm(self):
        await RisingEdge(self.dut.i_ce)
        
        await RisingEdge(self.dut.i_clk)    # to start capturing from the correct result
        await RisingEdge(self.dut.i_clk)
        await RisingEdge(self.dut.i_clk)
        while True:
            # result = BinaryValue(value=str(self.dut.o_result.value),binaryRepresentation=2)
            result = self.dut.o_result.value
            self.result_mon_queue.put_nowait(result)
            # self.result_mon_queue.put_nowait(result.integer)
            await RisingEdge(self.dut.i_clk)


    def start_bfm(self):
        cocotb.start_soon(self.driver_bfm())
        cocotb.start_soon(self.data_mon_bfm())
        cocotb.start_soon(self.result_mon_bfm())