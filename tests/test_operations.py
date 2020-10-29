from invisibleroads_macros_disk import (
    TemporaryStorage,
    archive_safely,
    archive_tar_safely,
    archive_zip_safely,
    make_enumerated_folder,
    make_random_folder,
    make_unique_folder,
    remove_folder,
    remove_path,
    unarchive_safely,
    ARCHIVE_TAR_EXTENSIONS,
    ARCHIVE_ZIP_EXTENSIONS,
    FileExtensionError)
from invisibleroads_macros_security import ALPHABET
from os.path import basename, exists, islink, join
from pytest import raises
from shutil import make_archive
from tempfile import mkstemp

from conftest import A_FOLDER, B_FOLDER, FILE_CONTENT, FILE_NAME


def test_archive_safely(tmpdir):
    check_archive_functionality(
        archive_safely, tmpdir,
        bad_extension='.x',
        good_extension=ARCHIVE_TAR_EXTENSIONS[0])


def test_archive_zip_safely(tmpdir):
    check_archive_functionality(
        archive_zip_safely, tmpdir,
        bad_extension=ARCHIVE_TAR_EXTENSIONS[0],
        good_extension=ARCHIVE_ZIP_EXTENSIONS[0])


def test_archive_tar_safely(tmpdir):
    check_archive_functionality(
        archive_tar_safely, tmpdir,
        bad_extension=ARCHIVE_ZIP_EXTENSIONS[0],
        good_extension=ARCHIVE_TAR_EXTENSIONS[0])


def test_unarchive_safely(tmpdir):
    with raises(FileExtensionError):
        unarchive_safely(tmpdir.join('x.x').strpath)
    archive_basename = tmpdir.join('b').strpath
    make_archive(archive_basename, 'gztar', B_FOLDER)
    archive_path = archive_basename + '.tar.gz'
    archive_folder = unarchive_safely(archive_path)
    assert islink(join(B_FOLDER, FILE_NAME))
    assert not exists(join(archive_folder, FILE_NAME))


def test_temporary_storage():
    with TemporaryStorage() as storage:
        assert exists(storage.folder)
    assert not exists(storage.folder)


def test_make_enumerated_folder(tmpdir):
    folder = make_enumerated_folder(tmpdir)
    assert basename(folder) == '1'
    folder = make_enumerated_folder(tmpdir)
    assert basename(folder) == '2'


def test_make_random_folder(tmpdir):
    for i in range(len(ALPHABET) + 1):
        folder = make_random_folder(tmpdir, 1)
        assert len(basename(folder)) >= 1


def test_remove_folder():
    temporary_folder = make_unique_folder()
    remove_folder(temporary_folder)
    remove_folder(temporary_folder)


def test_remove_path():
    temporary_path = mkstemp()[1]
    remove_path(temporary_path)
    remove_path(temporary_path)


def check_archive_functionality(
        archive, tmpdir, bad_extension, good_extension):
    source_folder = tmpdir.mkdir('x')
    source_folder.join(FILE_NAME).write(FILE_CONTENT)
    source_folder = source_folder.strpath

    with raises(FileExtensionError):
        archive(source_folder, source_folder + bad_extension)

    archive_path = archive(source_folder)
    archive_folder = unarchive_safely(archive_path)
    assert open(join(archive_folder, FILE_NAME)).read() == FILE_CONTENT

    archive_path = archive(A_FOLDER, tmpdir.join(
        'a' + good_extension).strpath, excluded_paths=['*.txt'])
    archive_folder = unarchive_safely(archive_path)
    assert not exists(join(archive_folder, FILE_NAME))

    archive_path = archive(B_FOLDER, tmpdir.join(
        'b' + good_extension).strpath)
    archive_folder = unarchive_safely(archive_path)
    assert not exists(join(archive_folder, FILE_NAME))
