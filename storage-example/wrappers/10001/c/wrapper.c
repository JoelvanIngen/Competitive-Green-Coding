// wrapper.c

/**
 * This file is written by exercise authors.
 * It has the following responsibilities:
 *   - Call the correct, existing deserialiser specific for this exercise
 *   - Ready all variables for problem entry (deconstructing structs, etc)
 *   - Call user submission
 *   - Call serialiser
 */

#include "wrapper.h"

#include <stdbool.h>
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
    int *input = NULL;
    int size = 0;
    if (!try_deserialise_array(&input, &size)) return false;

    int target = input[0];
    int *array = &input[1];

    int res = search_array(array, size, target);

    serialise_single_int(res);
    free(input);

    return true;
}
