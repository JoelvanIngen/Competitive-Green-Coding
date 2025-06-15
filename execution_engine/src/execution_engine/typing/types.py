from typing import Literal

StatusType = Literal[
    "success",  # Yay
    "failed",  # Tests failed
    "mem_limit_exceeded",  # Used too much memory
    "timeout",  # Ran out of time and was terminated
    # In case we decide to implement keyword checking to prevent scary keywords
    "security_violation",
    "compile_error",  # Couldn't compile user's code
    "runtime_error",  # User's code failed (segfaults, etc)
    "internal_error",  # Blanket error for everything unexpected (not user's fault)
]

LanguageLiteral = Literal[
    "c",
    "python",
]
