import os

def write_file(data: str, path: str, filename: str) -> None:
    path = os.path.join("/storage", path)
    full_path = os.path.join(path, filename)
    os.makedirs(path, exist_ok=True)
    with open(full_path, "w") as f:
        f.write(data)


def read_file(path: str) -> str:
    path = os.path.join("/storage", path)
    with open(path, "r") as f:
        return f.read()
