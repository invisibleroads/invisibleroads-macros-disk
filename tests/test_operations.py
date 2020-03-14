from invisibleroads_macros_disk import (
    TemporaryStorage,
    make_unique_folder,
    remove_folder,
    remove_path)
from os.path import exists
from tempfile import mkstemp


def test_temporary_storage():
    with TemporaryStorage() as storage:
        assert exists(storage.folder)
    assert not exists(storage.folder)


def test_remove_folder():
    temporary_folder = make_unique_folder()
    remove_folder(temporary_folder)
    remove_folder(temporary_folder)


def test_remove_path():
    temporary_path = mkstemp()[1]
    remove_path(temporary_path)
    remove_path(temporary_path)
