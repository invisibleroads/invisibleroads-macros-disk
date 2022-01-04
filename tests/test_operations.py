import tarfile
from invisibleroads_macros_disk import (
    BadArchiveError,
    FileExtensionError,
    InvisibleRoadsMacrosDiskError,
    TemporaryStorage,
    archive_safely,
    archive_tar_safely,
    archive_zip_safely,
    make_enumerated_folder,
    make_folder,
    make_random_folder,
    remove_folder,
    remove_path,
    unarchive_safely,
    ARCHIVE_TAR_EXTENSIONS,
    ARCHIVE_ZIP_EXTENSIONS)
from invisibleroads_macros_security import ALPHABET
from os.path import basename, exists, join
from pytest import raises
from shutil import make_archive
from tempfile import mkstemp
from zipfile import ZipFile

from conftest import EXAMPLES_FOLDER, FILE_CONTENT, FILE_NAME


def test_archive_safely(tmpdir):
    source_folder = tmpdir.mkdir('x')
    source_folder.join(FILE_NAME).write(FILE_CONTENT)
    source_folder.join(FILE_NAME + '_').write(FILE_CONTENT)
    source_folder = source_folder.strpath

    archive_path = archive_safely(source_folder, excluded_paths=['*.txt'])
    archive_file = ZipFile(archive_path)
    file_paths = archive_file.namelist()
    assert FILE_NAME not in file_paths
    assert FILE_NAME + '_' in file_paths

    archive_path = archive_safely(EXAMPLES_FOLDER, tmpdir.join(
        'examples.tar.gz').strpath)
    archive_file = tarfile.open(archive_path, 'r:gz')
    file_paths = archive_file.getnames()
    assert join('a', FILE_NAME) in file_paths
    assert join('b', FILE_NAME) not in file_paths

    with raises(FileExtensionError):
        archive_safely(source_folder, source_folder + '.x')


def test_archive_zip_safely(tmpdir):
    source_folder = tmpdir.mkdir('x')
    source_folder.join(FILE_NAME).write(FILE_CONTENT)
    source_folder = source_folder.strpath

    archive_path = archive_zip_safely(source_folder)
    archive_file = ZipFile(archive_path)
    assert FILE_NAME in archive_file.namelist()

    with raises(FileExtensionError):
        archive_zip_safely(
            source_folder, source_folder + ARCHIVE_TAR_EXTENSIONS[0])


def test_archive_tar_safely(tmpdir):
    source_folder = tmpdir.mkdir('x')
    source_folder.join(FILE_NAME).write(FILE_CONTENT)
    source_folder = source_folder.strpath

    archive_path = archive_tar_safely(source_folder)
    archive_file = tarfile.open(archive_path)
    assert FILE_NAME in archive_file.getnames()

    with raises(FileExtensionError):
        archive_tar_safely(
            source_folder, source_folder + ARCHIVE_ZIP_EXTENSIONS[0])


def test_unarchive_safely(tmpdir):
    with raises(FileExtensionError):
        unarchive_safely(tmpdir.join('x.x').strpath)
    with raises(BadArchiveError):
        archive_path_object = tmpdir.join('x.zip')
        archive_path_object.write(FILE_CONTENT)
        unarchive_safely(archive_path_object.strpath)
    with raises(BadArchiveError):
        archive_path_object = tmpdir.join('x.tar.gz')
        archive_path_object.write(FILE_CONTENT)
        unarchive_safely(archive_path_object.strpath)

    archive_path = EXAMPLES_FOLDER + '.zip'
    archive_file = ZipFile(archive_path)
    assert 'b/file.txt' in archive_file.namelist()
    archive_folder = unarchive_safely(archive_path, tmpdir.join(
        'examples').strpath)
    assert open(join(archive_folder, 'a', FILE_NAME)).read() == FILE_CONTENT
    assert not exists(join(archive_folder, 'b', FILE_NAME))

    archive_basename = tmpdir.join('examples').strpath
    make_archive(archive_basename, 'gztar', EXAMPLES_FOLDER)
    archive_path = archive_basename + '.tar.gz'
    archive_folder = unarchive_safely(archive_path)
    assert open(join(archive_folder, 'a', FILE_NAME)).read() == FILE_CONTENT
    assert not exists(join(archive_folder, 'b', FILE_NAME))


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
    for x in ALPHABET:
        make_folder(tmpdir.join(x).strpath)
    with raises(InvisibleRoadsMacrosDiskError):
        folder = make_random_folder(tmpdir, 1, with_fixed_length=True)


def test_remove_folder():
    temporary_folder = make_random_folder()
    remove_folder(temporary_folder)
    remove_folder(temporary_folder)


def test_remove_path():
    temporary_path = mkstemp()[1]
    remove_path(temporary_path)
    remove_path(temporary_path)
