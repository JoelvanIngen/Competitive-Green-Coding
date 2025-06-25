import pytest

from execution_engine.errors.errors import TestsFailedError
from execution_engine.parsers.grader import grader


@pytest.fixture(name="perfect_match")
def perfect_match_fixture():
    return {
        "input": "test1\ntest2",
        "expected": "result1\nresult2",
        "actual": "result1\nresult2"
    }


@pytest.fixture(name="length_mismatch")
def length_mismatch_fixture():
    return {
        "input": "test1\ntest2",
        "expected": "result1\nresult2",
        "actual": "result1"
    }


@pytest.fixture(name="content_mismatch")
def content_mismatch_fixture():
    return {
        "input": "test1\ntest2\ntest3",
        "expected": "result1\nresult2\nresult3",
        "actual": "result1\nwrong2\nresult3"
    }


@pytest.fixture(name="whitespace_variation")
def whitespace_variation_fixture():
    return {
        "input": " test1 \n test2 ",
        "expected": " result1 \n result2 ",
        "actual": "result1\nresult2"  # should pass due to strip()
    }


def test_perfect_match(perfect_match):
    """Test when actual output matches expected exactly"""
    grader(perfect_match["input"], perfect_match["expected"], perfect_match["actual"])
    # No exception should be raised


def test_length_mismatch(length_mismatch):
    """Test when line counts don't match"""
    with pytest.raises(TestsFailedError) as exc_info:
        grader(length_mismatch["input"], length_mismatch["expected"], length_mismatch["actual"])

    assert "Did not receive all test cases" in str(exc_info.value)


@pytest.mark.parametrize("line_num, expected_msg", [
    (1, "Test 1: Input: test2, Expected: result2 but got: wrong2"),
])
def test_content_mismatch(content_mismatch, line_num, expected_msg):
    """Test when some lines don't match"""
    with pytest.raises(TestsFailedError) as exc_info:
        grader(content_mismatch["input"], content_mismatch["expected"], content_mismatch["actual"])

    assert expected_msg in str(exc_info.value)


def test_whitespace_handling(whitespace_variation):
    """Test that whitespace is properly handled with strip()"""
    grader(whitespace_variation["input"], whitespace_variation["expected"], whitespace_variation["actual"])
    # No exception should be raised


def test_empty_inputs():
    """Test with empty inputs"""
    grader("", "", "")  # Should pass
    with pytest.raises(TestsFailedError):
        grader("test", "", "actual")  # Length mismatch
