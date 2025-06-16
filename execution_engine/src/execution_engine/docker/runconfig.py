import dataclasses

from common.schemas import SubmissionCreate
from common.languages import LanguageInfo


@dataclasses.dataclass
class RunConfig:
    tmp_dir: str
    cpu: int
    language: LanguageInfo
    origin_request: SubmissionCreate
