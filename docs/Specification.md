
## Requirements Specification


### 1. SCOPE

1. **Scope**

   This document establishes the requirements for an Intellectual Property (IP) that provides a fir filter function.
1. **Purpose**
 
   These requirements shall apply to a fir filter core with a simple interface for inclusion as a component.
1. **Classification**
    
   This document defines the requirements for a hardware design.


### 2. DEFINITIONS

1. **Width**

   Number of bits of samples.
2. **Tap**
   
   A FIR's taps are coefficient values. The number of taps is the amount of memory (length) needed to implement the filter.

### 3. APPLICABLE DOCUMENTS 

1. **Government Documents**

   None
1. **Non-government Documents**

   None


### 4. ARCHITECTURAL OVERVIEW

1. **Introduction**

   The fir filter component shall represent a design written in an HDL (VHDL and/or SystemVerilog) that can easily be incorporateed into a larger design.This fir filter shall include the following features : 
     1. Parameterized sample width, number of taps, tap width and tap values.

   The CPU interface in this case is a simple valid interface.

1. **System Application**
   
    The fir filter can be applied to a variety of system configurations. An example use case is to be used to transform data between an upstream producer and a downstream consumer.

### 5. PHYSICAL LAYER

1. en, input data valid
6. i_sample, input data word
7. o_result, fir filter output
7. clk, system clock
8. rst, system reset, synchronous active high

### 6. PROTOCOL LAYER

The fir average filter operates on valid input data samples being averaged with their neighbors and producing a filtered value.

### 7. ROBUSTNESS

Does not apply.

### 8. HARDWARE AND SOFTWARE

1. **Parameterization**

   The fir filter shall provide for the following parameters used for the definition of the implemented hardware during hardware build:

   | Param. Name | Description |
   | :------: | :------: |
   | g_i_w | sample width |
   | g_t_w | tap coefficient width |
   | g_o_w | filter output width |
   | g_taps | number of taps |
   | g_coeff_{a:...}  | coefficient value | 

1. **CPU interface**

   Simple data valid interface.

### 9. PERFORMANCE

1. **Frequency**
1. **Power Dissipation**
1. **Environmental**
 
   Does not apply.
1. **Technology**

   The design shall be adaptable to any technology because the design shall be portable and defined in an HDL.

### 10. TESTABILITY
None required.

### 11. MECHANICAL
Does not apply.
