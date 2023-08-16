![example workflow](https://github.com/npatsiatzis/moving_average/actions/workflows/regression_pyuvm.yml/badge.svg)
![example workflow](https://github.com/npatsiatzis/moving_average/actions/workflows/coverage_pyuvm.yml/badge.svg)

### moving-average filter RTL implementation

- run pyuvm testbench
    - $ make
- run unit testing of the pyuvm testbench
    - $  SIM=ghdl pytest -n auto -o log_cli=True --junitxml=test-results.xml --cocotbxml=test-cocotb.xml

