import dataclasses

from execution_engine.docker.languages import LanguageInfo
from execution_engine.models import ExecuteRequest


@dataclasses.dataclass
class RunConfig:
    tmp_dir: str
    cpu: int
    language: LanguageInfo
    origin_request: ExecuteRequest
