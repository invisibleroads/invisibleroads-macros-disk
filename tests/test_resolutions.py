from invisibleroads_macros_disk import check_absolute_path
from invisibleroads_macros_disk.exceptions import PathValidationError
from os.path import join
from pytest import raises

from conftest import EXAMPLES_FOLDER


def test_check_absolute_path():
    a_folder = join(EXAMPLES_FOLDER, 'a')
    b_folder = join(EXAMPLES_FOLDER, 'b')
    file_name = 'file.txt'

    # Check for an absolute path
    assert check_absolute_path(file_name, a_folder) == join(
        a_folder, file_name)

    # Do not allow linked paths that resolve outside the folder
    with raises(PathValidationError):
        check_absolute_path(file_name, b_folder)

    # Allow linked paths if they resolve inside trusted folders
    assert check_absolute_path(
        file_name, b_folder, trusted_folders=[a_folder]
    ) == join(b_folder, file_name)
