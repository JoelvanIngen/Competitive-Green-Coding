// deserialiser.h

#pragma once

#include <stdbool.h>

bool try_deserialise_single_int(int *val);

int deserialise_single_int();

bool try_deserialise_array(int *array, int *size)

int *deserialise_array();
