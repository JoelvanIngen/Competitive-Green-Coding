from execution_engine.typing.types import LanguageLiteral


class LanguageInfo:
    name: str
    image: str
    file_extension: str
    framework_files: list[str]
    wrapper_files: list[str]
    extra_files: list[str]


class C(LanguageInfo):
    name = "c"
    image = "runner_c"
    file_extension = "c"
    framework_files = [
        "main.c",
        "datastructs.c",
        "datastructs.h",
        "deserialiser.c",
        "deserialiser.h",
        "serialiser.c",
        "serialiser.h",
    ]
    wrapper_files = [
        "submission.h",
        "wrapper.c",
        "wrapper.h",
    ]
    extra_files = ["Makefile"]


language_info: dict[LanguageLiteral, LanguageInfo] = {
    "c": C(),
}
