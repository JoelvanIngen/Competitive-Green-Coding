from dataclasses import dataclass
from enum import Enum


class LanguageInfo:
    name: str
    image: str
    file_extension: str


class Language(str, Enum):
    """Available languages"""

    C = "c"
    PYTHON = "python"

    @property
    def info(self) -> LanguageInfo:
        return language_info[self]


@dataclass(frozen=True)
class C(LanguageInfo):
    name = "c"
    image = "gcc:14.3"
    file_extension = "c"


@dataclass(frozen=True)
class Python(LanguageInfo):
    name = "python"
    image = "python:3.12-slim"
    file_extension = "py"


language_info: dict[Language, LanguageInfo] = {
    Language.C: C(),
    Language.PYTHON: Python(),
}
