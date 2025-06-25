// serialiser.c

/** IMPORTANT:
 * IF THIS FILE IS MODIFIED IN ANY WAY,
 * PROPAGATE MODIFICATIONS TO deserialiser.c/.h
 */

/**
 * Contains code to serialise data structures
 * to stdout. Functions from this file are called
 * by the wrapper.
 * This code should always be symmetric with deserialiser.c!
 * > deserialise(serialise(data) == data)
 * - This should either pass, or exit deliberaltely on invalid
 *   input, but can never silently be "false".
 */

#include "serialiser.h"

#include <stdio.h>

/**
 * Pushes newline to stdout and flushes buffer.
 */
void _finalise() {
    fputc('\n', stdout);
    fflush(stdout);
}

/**
 * Writes a single integer to stdout
 */
void serialise_single_int(int num) {
    printf("%i", num);
    _finalise();
}


/**
 * Writes an array of integers to stdout
 * The first integer is the size of the array,
 */
void serialise_array(int *array, int size) {
    if (size <= 0) {
        _finalise();
        return;
    }

    printf("%i", size);
    for (int i = 0; i < size; i++) {
        printf(" %i", array[i]);
    }
    _finalise();
}
