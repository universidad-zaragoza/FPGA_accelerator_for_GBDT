#include <stdio.h>
#include "stdint.h"
#include "xtime_l.h"
#include "platform.h"
#include "xil_printf.h"

/* Datasets
 * 
 * SELECT ONLY ONE OF THE FOLLOWING:
 *   - IP_data.h  --> Indian Pines Corrected dataset
 *   - KSC_data.h --> Kennedy Space Center dataset
 *   - PU_data.h  --> Pavia University dataset
 *   - SV_data.h  --> Salinas Valley dataset
 * 
 * Some of the data structures on these files are very big. Depending on the
 * memory of your device, you will probably need to use a subset of the "pixel"
 * structure. Each pixel must be complete, but you can use any number of pixels
 * to perform the inference.
 * 
 */
#include "IP_data.h"
//#include "KSC_data.h"
//#include "PU_data.h"
//#include "SV_data.h"

// NUMBER OF LOOPS TO MEASURE POWER
#define LOOPS 10

/* Accuracy
 * 
 * To measure execution time and power consumption it is recommended to
 * deactivate the accuracy measurements.
 * 
 * SELECT ONLY ONE OF THE FOLLOWING:
 *   - GET_ACCURACY 1 --> If you want to get accuracy results
 *   - GET_ACCURACY 0 --> If you do not want to get accuracy results
 * SELECT ONLY ONE OF THE FOLLOWING:
 *   - ACCURACY_VERBOSITY 1 --> Will show each pixel prediction
 *   - ACCURACY_VERBOSITY 0 --> Will only show final accuracy (Top 1)
 */
#define GET_ACCURACY 1
//#define GET_ACCURACY 0
#define ACCURACY_VERBOSITY 1
//#define ACCURACY_VERBOSITY 0

/* These macros extract the corresponding value from the node
 * 
 * Non-leaf node representation:
 * |31     -     24|23    -     8|7      -      1|     0     |
 * |- num_feature -|- cmp_value -|- right_child -|- is_leaf -|
 * 
 * Leaf node representation:
 * |31    -     16|15    -     2|        1       |     0     |
 * |- pred_value -|- next_tree -|- is_last_tree -|- is_leaf -|
 *
 * Note that:
 *   - class_end = is_last_tree and is_leaf
 *   - next_tree is an absolute address while right_child is relative
 *   - the left child of a non-leaf node is always in the next address
 * 
 */
#define IS_LEAF(x)     ((x & 0x00000001) == 0x00000001)
#define PRED_VALUE(x)  ((x & 0xffff0000) >> 16)
#define NEXT_TREE(x)   ((x & 0x0000fffc) >> 2)
#define NUM_FEATURE(x) ((x & 0xff000000) >> 24)
#define CMP_VALUE(x)   ((x & 0x00ffff00) >> 8)
#define RIGHT_CHILD(x) ((x & 0x000000fe) >> 1)
#define CLASS_END(x)   ((x & 0x00000003) == 0x00000003)

/* Performs the prediction of one pixel for the trees of one class
 * 
 * @param class - The structure with all the trees of the class
 * @param pixel - The input pixel to perform the prediction
 * 
 * @return prediction - The cumulative prediction of all trees
 * 
 */
int predict(u32 class[], u32 pixel[]){
    int prediction = 0.0;
    int curr_addr = 0;
    int end = 0;
    while(!end){
        if(IS_LEAF(class[curr_addr])){ // Leaf node
            prediction += (int16_t)PRED_VALUE(class[curr_addr]);
            if(CLASS_END(class[curr_addr])){
                end = 1;
            } else{
                curr_addr = NEXT_TREE(class[curr_addr]);
            }
        } else{ // Non leaf node
            if(pixel[NUM_FEATURE(class[curr_addr])]
                   <= CMP_VALUE(class[curr_addr])){ // Left child
                curr_addr++;
            } else{ // Right child
                curr_addr += RIGHT_CHILD(class[curr_addr]);
            }
        }
    }
    return prediction;
}

/* Main function
 * 
 * This code is prepared to work on Xilinx SDK.
 * A good idea may be to generate the "helloword" template and copy this code
 * into the "helloword.c" file, so "init_platform()" and "cleanup_platform()"
 * functions will be generated into the "platform.c" file.
 * 
 * To compile and execute this code directly in your processor you will need to
 * remove the "platform.h" and "xil_printf.h" includes, and also remove the
 * "init_platform()" and "cleanup_platform()" calls from the code. You will
 * also need to change the "xtime_l.h" library for the "time.h" library and
 * addapt the timing variables and calls.
 * 
 */
int main(){
    
    int pixels;
    double seconds;
    XTime t_start, t_end;
    
    init_platform();
    
    printf("IMAGE: %s\n", IMAGE_NAME);
    
    if(GET_ACCURACY){ // Do not use this mode to measure time and power
        
        int predictions[NUM_PIXELS] = {0};
        int max_prediction_value;
        int prediction_value;
        int hits = 0;
        
        XTime_GetTime(&t_start);
        for(int p = 0; p < NUM_PIXELS; p++){
            max_prediction_value = 0.0;
            for(int c = 0; c < NUM_CLASSES; c++){
                prediction_value = predict(class[c], pixel[p]);
                if(prediction_value > max_prediction_value){
                    max_prediction_value = prediction_value;
                    predictions[p] = c;
                }
            }
            if(predictions[p] == label[p]){
                hits++;
            }
            if(ACCURACY_VERBOSITY){
                printf("PIXEL %d, PRED %d, LABEL %d\n",
                       p, predictions[p], label[p]);
            }
        }
        XTime_GetTime(&t_end);
        pixels = NUM_PIXELS;
        
        printf("ACCURACY: %f\n", (double)hits / NUM_PIXELS);
        
    } else{
        
        printf("--- START ---\n"); // Now you can start the power measurements
        
        XTime_GetTime(&t_start);
        for(int l = 0; l < LOOPS; l++){
            for(int p = 0; p < NUM_PIXELS; p++){
                for(int c = 0; c < NUM_CLASSES; c++){
                    predict(class[c], pixel[p]);
                }
            }
        }
        XTime_GetTime(&t_end);
        pixels = NUM_PIXELS * LOOPS;
    }
    
    seconds = (double)(t_end - t_start) / COUNTS_PER_SECOND;
    printf("PIXELS PER SECOND: %f\n", pixels / seconds);
    
    cleanup_platform();
    return 0;
}

