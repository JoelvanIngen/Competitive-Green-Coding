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
 */
void wrapper() {
    int *input = deserialise_array();

    int size = input[0];
    input = input[1];

    int target = input[0];
    input = input[1];

    int res = search_array(input, size, target);

    serialise_single_int(res);
}
