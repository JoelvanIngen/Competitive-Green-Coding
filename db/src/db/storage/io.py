import io
import os
import tarfile

from db import settings


def read_file(path: str, filename: str) -> str:
    full_path = os.path.join(settings.DB_HANDLER_STORAGE_PATH, path, filename)
    with open(full_path, "r") as f:
        return f.read()


def read_folder_to_tar(path: str) -> io.BytesIO:
    buff = io.BytesIO()
    with tarfile.open(fileobj=buff, mode="w:gz") as tar:
        tar.add(path, arcname=os.path.basename(path))

    buff.seek(0)
    return buff


def write_file(data: str, path: str, filename: str) -> None:
    full_path = os.path.join(path, filename)
    os.makedirs(path, exist_ok=True)
    with open(full_path, "w") as f:
        f.write(data)


def write_folder_from_tar(data: io.BytesIO, path: str) -> None:
    with tarfile.open(fileobj=data, mode="r:gz") as tar:
        return tar.extractall(path)
