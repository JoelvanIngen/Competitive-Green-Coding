"""
Basic test that serves the simple purpose of existing

Prevents pytest exit code 5, assures tests are set up correctly
If only this test passes, the code is bugged
If no tests pass, the test environment is bugged
"""


def test_dummy() -> None:
    assert True
