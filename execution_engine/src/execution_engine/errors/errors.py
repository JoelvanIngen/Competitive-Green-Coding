class CpuOutOfRangeError(Exception):
    """
    Docker was assigned a CPU that does not exist on the host system
    """


class CompileFailedError(Exception):
    """
    User code failed to compile
    """


class RuntimeFailError(Exception):
    """
    User code failed to run
    """


class TestsFailedError(Exception):
    """
    User code failed one or more tests
    """


class UnknownErrorError(Exception):
    """
    Weird error type that we don't recognise
    """


fail_reasons: set[str] = {
    "success",
    "compile",
    "runtime",
}
