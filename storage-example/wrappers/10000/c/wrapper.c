// wrapper.c

/**
 * This file is written by exercise authors.
 * It has the following responsibilities:
 *   - Call the correct, existing deserialiser specific for this exercise
 *   - Ready all variables for problem entry (deconstructing structs, etc)
 *   - Call user submission
 *   - Call serialiser
 */

#include "deserialiser.h"
#include "serialiser.h"
#include "submission.h"

/**
 * Entrypoint for code testing. Called by main
 */
void wrapper() {
    int input = deserialise_single_int();
    int res = add_one(input);
    serialise_single_int(res);
}
