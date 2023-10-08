## Requirements Specification


### 1. SCOPE

1. **Scope**

   This document establishes the requirements for an Intellectual Property (IP) that provides a moving average filter function.
1. **Purpose**
 
   These requirements shall apply to a moving average filter core with a simple interface for inclusion as a component.
1. **Classification**
    
   This document defines the requirements for a hardware design.


### 2. DEFINITIONS

1. **width**

   Width refers to the length in bits of the sample data words.
1. **length**

   Length refers to the number of sample words that are considered using the filter function to produce a specific filter output value.

### 3. APPLICABLE DOCUMENTS 

1. **Government Documents**

   None
1. **Non-government Documents**

   None


### 4. ARCHITECTURAL OVERVIEW

1. **Introduction**

   The moving average filter component shall represent a design written in an HDL (VHDL and/or SystemVerilog) that can easily be incorporateed into a larger design. The core shall include the following features : 
     1. parameterizable moving average filter operation.

No particular interface will be used in the initial phase of this core for communicating with the processor/controller.

1. **System Application**
   
    The moving average filter can be applied to a variety of system configurations. An example use case is to be used to transform data between an upstream producer and a downstream consumer.

### 5. PHYSICAL LAYER

1. ce, input data valid
1. sample, imput data sample
5. result, moving average filter result for specific sample
7. clk, system clock
8. rst, system reset, synchronous active high

### 6. PROTOCOL LAYER

The moving average filter operates on input data samples being averaged with their neighbors and producing a filtered value.

### 7. ROBUSTNESS

Does not apply.

### 8. HARDWARE AND SOFTWARE

1. **Parameterization**

   The moving average filter shall provide for the following parameters used for the definition of the implemented hardware during hardware build:

   | Param. Name | Description |
   | :------: | :------: |
   | g_i_W | sample data width |
   | g_m_W | bits for describing filter length |
   | g_o_W | width of the filter output value |

 

1. **CPU interface**

   No particular CPU interface (data valid interface).


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
