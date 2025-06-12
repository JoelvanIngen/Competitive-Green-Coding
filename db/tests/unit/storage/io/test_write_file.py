import os

import pytest
from pytest_mock import MockerFixture

from db.storage.io import write_file


@pytest.fixture(name="payload1")
def payload1_fixture() -> str:
    return "blabla"


@pytest.fixture(name="path1")
def path1_fixture() -> str:
    return "dir1/dir2"


@pytest.fixture(name="name1")
def name1_fixture() -> str:
    return "test.txt"


@pytest.fixture(name="root")
def root_fixture() -> str:
    return "/storage"


def test_empty_file_success(mocker: MockerFixture, root: str, path1: str, name1: str) -> None:
    mock_makedirs = mocker.patch("os.makedirs")
    mock_open = mocker.mock_open()
    mocker.patch("builtins.open", mock_open)

    write_file('', path1, name1)
    full_path = os.path.join(root, path1, name1)
    dir_path = os.path.join(root, path1)

    mock_makedirs.assert_called_once_with(dir_path, exist_ok=True)
    mock_open.assert_called_once_with(full_path, "w")
    mock_open().write.assert_called_once_with("")


def test_fixed_payload_success(mocker: MockerFixture, root, path1, name1, payload1: str) -> None:
    mock_makedirs = mocker.patch("os.makedirs")
    mock_open = mocker.mock_open()
    mocker.patch("builtins.open", mock_open)

    write_file(payload1, path1, name1)

    full_path = os.path.join(root, path1, name1)
    dir_path = os.path.join(root, path1)

    mock_makedirs.assert_called_once_with(dir_path, exist_ok=True)
    mock_open.assert_called_once_with(full_path, "w")
    mock_open().write.assert_called_once_with(payload1)
