"""
This module will include storage handling, for saving user submitted code.
"""

import os.path

from .storage import load_last_submission_code, load_template_code, store_code, store_template_code, tar_full_framework
from .storage_async import tar_stream_generator

__all__ = ["store_code", "load_last_submission_code", "load_template_code", "tar_stream_generator", "tar_full_framework", "store_template_code"]

from db.config import settings

# Ensure folders exist
framework_dir = os.path.join(settings.DB_HANDLER_STORAGE_PATH, settings.FRAMEWORK_DIR)
if not os.path.exists(framework_dir):
    os.makedirs(framework_dir)

wrappers_dir = os.path.join(settings.DB_HANDLER_STORAGE_PATH, settings.WRAPPER_DIR)
if not os.path.exists(wrappers_dir):
    os.makedirs(wrappers_dir)

submissions_dir = os.path.join(settings.DB_HANDLER_STORAGE_PATH, settings.CODE_SUBMISSION_DIR)
if not os.path.exists(submissions_dir):
    os.makedirs(submissions_dir)
