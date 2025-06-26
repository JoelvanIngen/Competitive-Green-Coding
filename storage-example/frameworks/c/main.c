// main.c

/** 
 * Entry point for code submission framework.
 * We can do setup or other preparations here, or start a timer.
 * Calls submission_wrapper.
 */

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#include "wrapper.h"

int main() {
    while (wrapper());
    return 0;
}
