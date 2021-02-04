# FILES DESCRIPTION

## IP_test.vhd, KSC_test.vhd, PU_test.vhd, SV_test.vhd

These files are VHDL test files for the main entity of the VHDL accelerator in
"../src/image.vhd". Each file corresponds to one of the analyzed hyperspectral
images (IP, KSC, PU and SV).

As they contain every pixel on the test set, these are very big files, so it is
not recommended to try to execute the entire files in vivado (you will probably
receive an out of memory error). It is recommended to comment and uncomment the
pixels by groups and execute the entire test part by part.

After executing each pixel it will also test if the result of the prediction is
correct, so at the end of the execution the signal "pixels" will contain the
total number of executed pixels while the signal "hits" will contain the total
number of hits.

## select_classes.sh

This file is a bash script to easily comment and uncomment groups of pixels on
each test file. As in these files the pixels are grouped by labels (i.e. by
classes), you only need to pass as arguments the number of the class you want
to uncomment and the file name:

    USE: ./select_classes.sh <num_class> <file_name>

As an example, "./select_classes.sh 5 KSC_test.vhd" will keep uncommented all
the pixels of class 5 in the file "KSC_test.vhd". To perform the entire test on
vivado you will need to do this for every class and execute them one by one.

