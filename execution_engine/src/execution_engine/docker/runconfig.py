import dataclasses

from common.languages import LanguageInfo
from common.schemas import SubmissionCreate


@dataclasses.dataclass
class RunConfig:
    tmp_dir: str
    cpu: int
    language: LanguageInfo
    origin_request: SubmissionCreate
