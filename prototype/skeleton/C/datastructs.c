// datastructs.c

/** IMPORTANT:
 * IF THIS FILE IS MODIFIED IN ANY WAY,
 * PROPAGATE MODIFICATIONS TO SERIALISER AND DESERIALISER
 */

/**
 * Library containing all sorts of data structures that can be used in
 * the exercise
 */

struct IntLinkedListNode {
    int val;
    struct IntLinkedListNode *next;
};
