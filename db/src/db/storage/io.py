import io
import os
import tarfile
from tarfile import TarFile


def read_file(path: str, filename: str) -> str:
    full_path = os.path.abspath(os.path.join(path, filename))
    with open(full_path, "r") as f:
        return f.read()


def read_file_to_tar(tar: TarFile, path: str):
    tar.add(path, arcname=os.path.basename(path))


def read_folder_to_tar(tar: TarFile, path: str):
    path = os.path.abspath(path)
    for filename in os.listdir(path):
        read_file_to_tar(tar, os.path.join(path, filename))


def write_file(data: str, path: str, filename: str) -> None:
    full_path = os.path.abspath(os.path.join(path, filename))
    os.makedirs(path, exist_ok=True)
    with open(full_path, "w") as f:
        f.write(data)


def write_folder_from_tar(data: io.BytesIO, path: str) -> None:
    path = os.path.abspath(path)
    with tarfile.open(fileobj=data, mode="r:gz") as tar:
        return tar.extractall(path)
