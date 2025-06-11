import os

from .threading import to_thread

@to_thread
def write_file(data: str, path: str) -> None:
   path = os.path.join("/storage", path)
   with open(path, 'w') as f:
       f.write(data)


@to_thread
def read_file(path: str) -> str:
    path = os.path.join("/storage", path)
    with open(path, 'r') as f:
        return f.read()
