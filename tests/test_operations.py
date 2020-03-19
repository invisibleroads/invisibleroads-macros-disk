from invisibleroads_macros_disk import (
    TemporaryStorage,
    make_enumerated_folder,
    make_random_folder,
    make_unique_folder,
    remove_folder,
    remove_path)
from os.path import basename, exists
from tempfile import mkstemp


def test_temporary_storage():
    with TemporaryStorage() as storage:
        assert exists(storage.folder)
    assert not exists(storage.folder)


def test_make_enumerated_folder(tmpdir):
    folder = make_enumerated_folder(tmpdir)
    assert basename(folder) == '1'


def test_make_random_folder(tmpdir):
    folder = make_random_folder(tmpdir, 10)
    assert len(basename(folder)) == 10


def test_remove_folder():
    temporary_folder = make_unique_folder()
    remove_folder(temporary_folder)
    remove_folder(temporary_folder)


def test_remove_path():
    temporary_path = mkstemp()[1]
    remove_path(temporary_path)
    remove_path(temporary_path)
