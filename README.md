# FPGA_accelerator_for_GBDT

This repository contains the GBDT models and the source codes of the accelerator developed and described in the paper "FPGA Accelerator for Gradient Boosting Decision Trees", available on: https://doi.org/10.3390/electronics10030314

*BibTex citation*

    @Article{Alcolea2021FPGAforGBDT,
        AUTHOR         = {Alcolea, Adrián and Resano, Javier},
        TITLE          = {FPGA Accelerator for Gradient Boosting Decision Trees},
        JOURNAL        = {Electronics},
        VOLUME         = {10},
        YEAR           = {2021},
        NUMBER         = {3},
        ARTICLE-NUMBER = {314},
        URL            = {https://www.mdpi.com/2079-9292/10/3/314},
        ISSN           = {2079-9292},
        DOI            = {10.3390/electronics10030314}
    }

## FPGA_VHDL_code_and_data

This directory contains the VHDL codes of the accelerator itself ("src" directory) and some VHDL test files to perform the inference of the test pixels of every analyzed image ("sim" directory).

If you want to execute the VHDL code into an FPGA, then you will need to define your block design along with your communications (we used an AXI stream to send both, the nodes of the trees and the features of the pixels, and then an AXI little to get the prediction results). Analyze the structure of the VHDL test files could help you to better understand the "image.vhd" and the "class.vhd" state machines, which is necessary to know how to send the data.

## embedded_system_c_code_and_data

This directory contains the c program and the formatted data to perform the inference of the test pixels of every analyzed image in the CPU of an embedded device.

## high_performance_processor_python_code_and_data

This directory contains the python code and the original trained models to perform the inference of the test pixels of every analyzed image in a high performance CPU using the LightGBM library.
