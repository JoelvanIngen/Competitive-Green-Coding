// wrapper.c

/**
 * This file is written by exercise authors.
 * It has the following responsibilities:
 *   - Call the correct, existing deserialiser specific for this exercise
 *   - Ready all variables for problem entry (deconstructing structs, etc)
 *   - Call user submission
 *   - Call serialiser
 */

#include <stdlib.h>

#include "deserialiser.h"
#include "serialiser.h"
#include "submission.h"

/**
 * Entrypoint for code testing. Called by main
 *
 * First integer passed should be the size of the array - 1
 * The second integer passed should be the target
 * The rest of the integers should be the array elements
 */
bool wrapper() {
    int *input;
    int *size;
    if (!try_deserialise_array(input, size)) return false;

    int target = input[1];
    int *array = input[2];

    // Size - 2 since the size and target are originally also included in the array
    int res = search_array(array, *size - 2, target);

    serialise_single_int(res);
    free(input);
    free(size)

    return true
}
