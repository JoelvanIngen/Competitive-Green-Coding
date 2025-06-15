import enum

from execution_engine.models import StatusType


class DockerStatus(enum.Enum):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    MEM_LIMIT_EXCEEDED = "mem_limit_exceeded"
    INTERNAL_ERROR = "internal_error"

    def to_status_t(self) -> StatusType:
        match self:
            case self.TIMEOUT:
                return "timeout"
            case self.MEM_LIMIT_EXCEEDED:
                return "mem_limit_exceeded"
            case self.INTERNAL_ERROR:
                return "internal_error"
            case self.SUCCESS:
                return "success"
            case _:
                # Not possible
                return "internal_error"
