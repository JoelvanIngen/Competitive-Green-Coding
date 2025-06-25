from loguru import logger

from execution_engine.errors.errors import TestsFailedError


def grader(input_file: str, expected_file: str, actual_file: str):
    """
    Grades the tests that have been performed by the user program
    :returns: None
    :raises TestsFailedError: if any test fails
    """
    tests_passed = True
    tests_failed_msgs = []

    input_lines = input_file.splitlines()
    expected_lines = expected_file.splitlines()
    actual_lines = actual_file.splitlines()

    if not len(expected_lines) == len(actual_lines):
        logger.info(f"Expected {len(expected_lines)} lines, got {len(actual_lines)} lines")
        raise TestsFailedError("Did not receive all test cases")

    # For _ in range is on purpose here (prevents 150-length line), hence pylint ignore
    for i in range(len(expected_lines)):  # pylint: disable=consider-using-enumerate
        input_line = input_lines[i].strip()
        expected_line = expected_lines[i].strip()
        actual_line = actual_lines[i].strip()

        if not expected_line == actual_line:
            tests_failed_msgs.append(
                f"Test {i}: Input: {input_line}, Expected: {expected_line} but got: {actual_line}"
            )
            tests_passed = False

    if not tests_passed:
        error_msg = "\n".join(tests_failed_msgs)
        raise TestsFailedError("Tests failed:\n" + error_msg)
