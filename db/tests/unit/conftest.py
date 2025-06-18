import os
import shutil
import sys

from db import settings

current_dir = os.path.dirname(os.path.abspath(__file__))
target_path = os.path.normpath(os.path.join(current_dir, '../../../common_python_modules'))

if target_path not in sys.path:
    sys.path.insert(0, target_path)

print(f"Added '{target_path}' to sys.path for pytest.")

storage_path = str(os.path.join(current_dir, "../", settings.DB_HANDLER_STORAGE_PATH))
storage_example_path = str(os.path.join(current_dir, "../../../storage-example"))
if os.path.exists(storage_path):
    shutil.rmtree(storage_path)

shutil.copytree(storage_example_path, storage_path)
