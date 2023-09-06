![example workflow](https://github.com/npatsiatzis/moving_average/actions/workflows/verilator_regression.yml/badge.svg)

### moving-average filter RTL implementation


-- Verilator tb for functional verification, adapted from the work of Norbet Kremeris (https://www.itsembedded.com/dhd/verilator_4/). Added coverage class for the input and output interfaces,sequence class, coverage-based end-of-test condition and coverage-driven test generation
- run sim
    - $ make sim
- Achieve full point coverage for output
- open waveform with gtkwave
    - $ make waves
- lint test
    - $make lint
