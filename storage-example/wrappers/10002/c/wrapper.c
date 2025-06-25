#include <stdlib.h>
#include <stdbool.h>

#include "deserialiser.h"
#include "serialiser.h"
#include "submission.h"

/**
 * Entrypoint for code testing. Called by main
 *
 * First integer passed should be the size of the array
 * The rest of the integers should be the array elements
 */
bool wrapper() {
    int *input;
    int *size;

    if (!deserialise_array(input, size)) return false;
    int *array = input[1];

    int *res = sort_array(input, size);

    serialise_array(res, size);

    free(array);
    free(input);
    return true;
}