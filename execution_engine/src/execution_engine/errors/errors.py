class BaseEngineException(Exception):
    def __init__(self, msg: str = ""):
        self.msg = msg


class CpuOutOfRangeError(BaseEngineException):
    """
    Docker was assigned a CPU that does not exist on the host system
    """


class CompileFailedError(BaseEngineException):
    """
    User code failed to compile
    """


class RuntimeFailError(BaseEngineException):
    """
    User code failed to run
    """


class ContainerOOMError(BaseEngineException):
    """
    Container ran out of allowed memory
    """


class TestsFailedError(BaseEngineException):
    """
    User code failed one or more tests
    """


class ParseError(BaseEngineException):
    """
    Parsing timing output failed
    """


class UnknownErrorError(BaseEngineException):
    """
    Weird error type that we don't recognise
    """
