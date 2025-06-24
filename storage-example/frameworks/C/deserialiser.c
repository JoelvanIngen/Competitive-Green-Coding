// deserialiser.c

/** IMPORTANT:
 * IF THIS FILE IS MODIFIED IN ANY WAY,
 * PROPAGATE MODIFICATIONS TO serialiser.c/.h
 */

/**
 * Contains code to deserialise data structures
 * from stdin. Functions from this file are called
 * by the wrapper.
 * This code should always be symmetric with serialiser.c!
 * > serialise(deserialise(str) == str)
 * - This should either pass, or exit deliberaltely on invalid
 *   input, but can never silently be "false".
 */

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

/**
 * Discards the entire leftover stdint buffer.
 * Not strictly necessary for basic purposes, but should
 * be called to avoid tricky debugging in the future
 */
void _discard_stdin() {
    char c;
    while ((c = getchar()) != '\n' && c != EOF)
        /* Empty */ ;
}

/**
 * Errors, clears stdin and exits
 */
void _error(char *s) {
    fprintf(stderr, s);
    fprintf(stderr, "\n");
    _discard_stdin();
    exit(1);
}

/**
 * Attempts to read an integer and passes success status
 */
bool _try_read_int(int *val) {
    int status = scanf(" %d", val);

    if (status == 1) return true;
    else return false;

    // False for both EOF and non-integer stream.
    // We might want to explicitly check and handle
    // both cases in the future, but there is no
    // need for that yet
}

/**
 * Reads and returns single int from stdin.
 * Errors on failure.
 */
int _read_int() {
    int val;
    if (!_try_read_int(&val)) {
        _error("could not read integer from stdin");
    }
    return val;
}

/**
 * Reads and stores a single integer from stdin in a variable
 * Returns true on success, false on failure
 */
bool try_deserialise_single_int(int *val) {
    return _try_read_int(val);
}

/**
 * Reads and returns a single integer from stdin
 * Discards extra provided integers
 */
int deserialise_single_int() {
    int num = _read_int();
    _discard_stdin();
    return num;
}

/**
 * Reads an array of integers from stdin
 * The first integer passed should be the size of the array
 * The size of the array will also be the first element of the array
 * Returns false on failure, or true on success
 */
int *try_deserialise_array(int *array, int *size) {
    if (!try_deserialise_single_int(size)) return false;

    array = malloc((size + 1) * sizeof(int));

    array[0] = size;

    for (int i = 1; i <= size; i++) {
        array[i] = _read_int()
    }

    return true;
}

/**
 * Reads an array of integers from stdin.
 * The first integer passed should be the size of the array
 * The size of the array will also be the first element of the array,
*/
int *deserialise_array() {
    int size = deserialise_single_int();
    int *array = malloc((size + 1) * sizeof(int));

    array[0] = size;

    for (int i = 1; i <= size; i++) {
        if (!_try_read_int(&array[i])) {
            _error("could not read integer from stdin");
        }
    }

    return array;
}
