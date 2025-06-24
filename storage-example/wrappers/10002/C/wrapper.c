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
void wrapper() {
    int *input = deserialise_array();

    int size = input[0];
    int *array = input[1];

    int *res = sort_array(input, size);

    serialise_array(res, size);
    free(array);
    free(input);
}