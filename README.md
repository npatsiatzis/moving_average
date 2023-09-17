![example workflow](https://github.com/npatsiatzis/moving_average/actions/workflows/regression.yml/badge.svg)
![example workflow](https://github.com/npatsiatzis/moving_average/actions/workflows/coverage.yml/badge.svg)
![example workflow](https://github.com/npatsiatzis/moving_average/actions/workflows/regression_pyuvm.yml/badge.svg)
![example workflow](https://github.com/npatsiatzis/moving_average/actions/workflows/coverage_pyuvm.yml/badge.svg)
![example workflow](https://github.com/npatsiatzis/moving_average/actions/workflows/formal.yml/badge.svg)
![example workflow](https://github.com/npatsiatzis/moving_average/actions/workflows/verilator_regression.yml/badge.svg)
[![codecov](https://codecov.io/gh/npatsiatzis/moving_average/graph/badge.svg?token=413OMOMIEO)](https://codecov.io/gh/npatsiatzis/moving_average)

### moving-average filter RTL implementation

-- RTL code in:
- [VHDL](https://github.com/npatsiatzis/moving_average/tree/main/rtl/VHDL)
- [SystemVerilog](https://github.com/npatsiatzis/moving_average/tree/main/rtl/SystemVerilog)

-- Functional verification with methodologies:
- [cocotb](https://github.com/npatsiatzis/moving_average/tree/main/cocotb_sim)
- [pyuvm](https://github.com/npatsiatzis/moving_average/tree/main/pyuvm_sim)
- [verilator](https://github.com/npatsiatzis/moving_average/tree/main/verilator_sim)


| Folder | Description |
| ------ | ------ |
| [rtl/SystemVerilog](https://github.com/npatsiatzis/moving_average/tree/main/rtl/SystemVerilog) | SV RTL implementation files |
| [rtl/VHDL](https://github.com/npatsiatzis/moving_average/tree/main/rtl/VHDL) | VHDL RTL implementation files |
| [cocotb_sim](https://github.com/npatsiatzis/moving_average/tree/main/cocotb_sim) | Functional Verification with CoCoTB (Python-based) |
| [pyuvm_sim](https://github.com/npatsiatzis/moving_average/tree/main/pyuvm_sim) | Functional Verification with pyUVM (Python impl. of UVM standard) |
| [verilator_sim](https://github.com/npatsiatzis/moving_average/tree/main/verilator_sim) | Functional Verification with Verilator (C++ based) |
| [formal](https://github.com/npatsiatzis/moving_average/tree/main/formal) | Formal Verification using  PSL properties and [YoysHQ/sby](https://github.com/YosysHQ/oss-cad-suite-build) |


This is the <!-- tree view of the strcture of the repo.
<pre>
<font size = "2">
.
├── <font size = "4"><b><a href="https://github.com/npatsiatzis/moving_average/tree/main/rtl">rtl</a></b> </font>
│   ├── <font size = "4"><a href="https://github.com/npatsiatzis/moving_average/tree/main/rtl/SystemVerilog">SystemVerilog</a> </font>
│   │   └── SV files
│   └── <font size = "4"><a href="https://github.com/npatsiatzis/moving_average/tree/main/rtl/VHDL">VHDL</a> </font>
│       └── VHD files
├── <font size = "4"><b><a href="https://github.com/npatsiatzis/moving_average/tree/main/cocotb_sim">cocotb_sim</a></b></font>
│   ├── Makefile
│   └── python files
├── <font size = "4"><b><a 
 href="https://github.com/npatsiatzis/moving_average/tree/main/pyuvm_sim">pyuvm_sim</a></b></font>
│   ├── Makefile
│   └── python files
├── <font size = "4"><b><a href="https://github.com/npatsiatzis/moving_average/tree/main/verilator_sim">verilator_sim</a></b></font>
│   ├── Makefile
│   └── verilator tb
└── <font size = "4"><b><a href="https://github.com/npatsiatzis/fifo_synchronous/tree/main/formal">formal</a></b></font>
    ├── Makefile
    └── PSL properties file, scripts
</pre> -->