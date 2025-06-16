import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
target_path = os.path.normpath(os.path.join(current_dir, '../../../common_python_modules'))

if target_path not in sys.path:
    sys.path.insert(0, target_path)

print(f"Added '{target_path}' to sys.path for pytest.")
