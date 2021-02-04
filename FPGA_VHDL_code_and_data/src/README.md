# FILES DESCRIPTION

## image.vhd

This file contains the entity "image", the main entity of the accelerator
design. It must be instantiated with the number of classes and features of the
correspondent hyperspectral image to analyze. There are some comments in the
"generic" description to help with that, but it is not needed to use them, the
actual values will be taken from the instantiation (in a test bench or in the
main comunication entity of your design).

To measure power it is useful to generate an infinite loop, you can easily do
it following the coments at the end of the file, inside "S_ARGMAX" state.

## class.vhd

This file contains the entity "class", wich corresponds to the manager of the
execution of the trees of one class.

## active_demux.vhd, comparator_2_32b.vhd, comparator_16_32b.vhd, counter.vhd,
## mux.vhd, ram.vhd, reg.vhd

These files are the used components.

## types.vhd

This file implements the function "log_2" used to get the number of bits needed
to generate a signal capable of address a number of elements (like the number
address bits needed in a memory with N addresses).

