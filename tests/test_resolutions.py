from os.path import join

from invisibleroads_macros_disk import (
    check_absolute_path,
    check_path,
    check_relative_path,
    get_asset_path,
    get_file_hash,
    has_extension,
    is_matching_path,
    is_path_in_folder)
from invisibleroads_macros_disk.exceptions import PathValidationError
from pytest import raises

from conftest import A_FOLDER, B_FOLDER, FILE_NAME


def test_has_extension():
    assert has_extension('a.txt', ['.txt'])
    assert not has_extension('a.zip', ['.txt'])


def test_is_matching_path():
    assert is_matching_path('a.txt', ['*.txt'])
    assert not is_matching_path('a.zip', ['*.txt'])


def test_is_path_in_folder():
    assert is_path_in_folder(join(A_FOLDER, FILE_NAME), A_FOLDER)
    assert not is_path_in_folder(join(A_FOLDER, FILE_NAME), B_FOLDER)


def test_check_relative_path():
    path = join(A_FOLDER, FILE_NAME)
    assert check_relative_path(path, A_FOLDER) == FILE_NAME


def test_check_absolute_path():
    path = join(A_FOLDER, FILE_NAME)
    assert check_absolute_path(path, A_FOLDER) == path


def test_check_path():
    path = join(B_FOLDER, FILE_NAME)

    # Do not allow linked paths that resolve outside the folder
    with raises(PathValidationError):
        check_path(path, B_FOLDER)
    with raises(PathValidationError):
        check_path(path, B_FOLDER, trusted_folders=[B_FOLDER])

    # Allow linked paths if they resolve inside trusted folders
    check_path(path, B_FOLDER, trusted_folders=[A_FOLDER])


def test_get_file_hash():
    assert get_file_hash(join(A_FOLDER, FILE_NAME)).startswith('e')


def test_get_asset_path():
    package_name = 'invisibleroads_macros_disk'
    assert get_asset_path(package_name + ':__init__.py') == __import__(
        package_name).__file__
    assert get_asset_path('README.md') == 'README.md'
