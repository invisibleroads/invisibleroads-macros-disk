from invisibleroads_macros_disk import (
    TemporaryStorage,
    compress,
    compress_zip,
    compress_tar,
    make_enumerated_folder,
    make_random_folder,
    make_unique_folder,
    remove_folder,
    remove_path,
    uncompress,
    ARCHIVE_TAR_EXTENSIONS,
    ARCHIVE_ZIP_EXTENSIONS,
    FileExtensionError)
from invisibleroads_macros_security import ALPHABET
from os.path import basename, exists, islink, join
from pytest import raises
from tempfile import mkstemp

from conftest import (
    A_FOLDER, B_FOLDER, EXAMPLES_FOLDER, FILE_CONTENT, FILE_NAME)


def test_compress(tmpdir):
    check_archive_functionality(
        compress, tmpdir,
        bad_extension='.x',
        good_extension=ARCHIVE_TAR_EXTENSIONS[0])


def test_compress_zip(tmpdir):
    check_archive_functionality(
        compress_zip, tmpdir,
        bad_extension=ARCHIVE_TAR_EXTENSIONS[0],
        good_extension=ARCHIVE_ZIP_EXTENSIONS[0])


def test_compress_tar(tmpdir):
    check_archive_functionality(
        compress_tar, tmpdir,
        bad_extension=ARCHIVE_ZIP_EXTENSIONS[0],
        good_extension=ARCHIVE_TAR_EXTENSIONS[0])


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


def check_archive_functionality(f, tmpdir, bad_extension, good_extension):
    source_folder = tmpdir.mkdir('x')
    source_folder.join(FILE_NAME).write(FILE_CONTENT)
    source_folder = source_folder.strpath

    with raises(FileExtensionError):
        f(source_folder, source_folder + bad_extension)
    archive_path = f(source_folder)
    archive_folder = uncompress(archive_path)
    assert open(join(archive_folder, FILE_NAME)).read() == FILE_CONTENT

    archive_path = f(B_FOLDER, tmpdir.join(
        'b' + good_extension,
    ).strpath, with_link_purgation=False, with_link_expansion=False)
    archive_folder = uncompress(
        archive_path, tmpdir.join('b', '1'), with_link_purgation=False)
    assert islink(join(archive_folder, FILE_NAME))

    '''
    archive_path = f(EXAMPLES_FOLDER, tmpdir.join(
        'examples' + good_extension).strpath, with_link_expansion=True)
    archive_folder = uncompress(archive_path, tmpdir.join('examples', '2'))
    assert not islink(join(archive_folder, 'b', FILE_NAME))

    archive_path = f(B_FOLDER, tmpdir.join('b' + good_extension).strpath)
    archive_folder = uncompress(archive_path, tmpdir.join('b', '1'))
    assert not exists(join(archive_folder, FILE_NAME))

    archive_path = compress_tar(B_FOLDER, tmpdir.join(
        'b' + ARCHIVE_TAR_EXTENSIONS[0],
    ).strpath, trusted_folders=[A_FOLDER], with_link_expansion=True)
    archive_folder = uncompress(archive_path, tmpdir.join('b', '2'))
    assert exists(join(archive_folder, FILE_NAME))
    '''
