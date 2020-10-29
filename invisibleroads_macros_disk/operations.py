import re
import tarfile
from invisibleroads_macros_security import make_random_string
from os import makedirs, remove, unlink
from os.path import exists, islink, join, splitext
from shutil import rmtree
from tempfile import mkdtemp
from zipfile import BadZipfile, ZipFile, ZIP_DEFLATED

from .constants import (
    ARCHIVE_TAR_EXTENSIONS,
    ARCHIVE_ZIP_EXTENSIONS,
    TEMPORARY_FOLDER)
from .exceptions import (
    BadArchiveError,
    FileExtensionError)
from .resolutions import (
    get_relative_path,
    has_extension,
    is_matching_path,
    walk_paths)


class TemporaryStorage(object):

    def __init__(self, base_folder=None):
        self.folder = make_unique_folder(base_folder or TEMPORARY_FOLDER)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        remove_folder(self.folder)


def compress(
        source_folder,
        target_path=None,
        trusted_folders=None,
        excluded_names=None,
        with_link_purgation=True,
        with_link_expansion=False):
    'Compress folder. Specify archive extension in target_path.'
    if not target_path:
        target_path = source_folder + ARCHIVE_ZIP_EXTENSIONS[0]
    arguments = [
        source_folder,
        target_path,
        trusted_folders,
        excluded_names,
        with_link_purgation,
        with_link_expansion,
    ]
    if has_extension(target_path, ARCHIVE_ZIP_EXTENSIONS):
        compress_zip(*arguments)
    elif has_extension(target_path, ARCHIVE_TAR_EXTENSIONS):
        compress_tar(*arguments)
    else:
        archive_extensions = ARCHIVE_ZIP_EXTENSIONS + ARCHIVE_TAR_EXTENSIONS
        raise FileExtensionError({
            'target_path': 'must end in ' + ' or '.join(archive_extensions)})
    return target_path


def compress_zip(source_folder, target_path=None, excluded_paths=None):
    'Compress folder as a zip archive'
    if not target_path:
        target_path = source_folder + ARCHIVE_ZIP_EXTENSIONS[0]
    if not has_extension(target_path, ARCHIVE_ZIP_EXTENSIONS):
        archive_extensions = ARCHIVE_ZIP_EXTENSIONS
        raise FileExtensionError({
            'target_path': 'must end in ' + ' or '.join(archive_extensions)})
    with ZipFile(
        target_path, 'w', ZIP_DEFLATED, allowZip64=True,
    ) as target_file:
        _process_folder(source_folder, excluded_paths, target_file.write)
    return target_path


def compress_tar(source_folder, target_path=None, excluded_paths=None):
    'Compress folder as a tar archive'
    if not target_path:
        target_path = source_folder + ARCHIVE_TAR_EXTENSIONS[0]
    if not has_extension(target_path, ARCHIVE_TAR_EXTENSIONS):
        archive_extensions = ARCHIVE_TAR_EXTENSIONS
        raise FileExtensionError({
            'target_path': 'must end in ' + ' or '.join(archive_extensions)})
    compression_format = splitext(target_path)[1].lstrip('.')
    with tarfile.open(
        target_path, 'w:' + compression_format, dereference=False,
    ) as target_file:
        _process_folder(source_folder, excluded_paths, target_file.add)
    return target_path


def uncompress(source_path, target_folder=None):
    if not exists(source_path):
        raise IOError({'source_path': 'is bad ' + source_path})
    if has_extension(source_path, ARCHIVE_ZIP_EXTENSIONS):
        try:
            source_file = ZipFile(source_path, 'r')
        except BadZipfile:
            raise BadArchiveError({'source_path': 'is unreadable'})
        extension_expression = r'\.zip$'
    elif has_extension(source_path, ARCHIVE_TAR_EXTENSIONS):
        compression_format = splitext(source_path)[1].lstrip('.')
        try:
            source_file = tarfile.open(source_path, 'r:' + compression_format)
        except tarfile.ReadError:
            raise BadArchiveError({'source_path': 'is unreadable'})
        extension_expression = r'\.tar\.%s$' % compression_format
    else:
        archive_extensions = ARCHIVE_ZIP_EXTENSIONS + ARCHIVE_TAR_EXTENSIONS
        raise FileExtensionError({
            'source_path': 'must end in ' + ' or '.join(archive_extensions)})
    if not target_folder:
        target_folder = re.sub(extension_expression, '', source_path)
    source_file.extractall(target_folder)
    source_file.close()
    for path in walk_paths(target_folder):
        if islink(path):
            unlink(path)
    return target_folder


def make_enumerated_folder(base_folder, target_index=1):
    while True:
        target_folder = join(base_folder, str(target_index))
        try:
            makedirs(target_folder)
            break
        except FileExistsError:
            target_index += 1
    return target_folder


def make_random_folder(base_folder, target_length):
    while True:
        target_index = make_random_string(target_length)
        target_folder = join(base_folder, target_index)
        try:
            makedirs(target_folder)
            break
        except FileExistsError:
            target_length += 1
    return target_folder


def make_unique_folder(base_folder=None):
    if base_folder:
        make_folder(base_folder)
    return mkdtemp(dir=base_folder)


def make_folder(folder):
    try:
        makedirs(folder)
    except FileExistsError:
        pass
    return folder


def remove_folder(folder):
    try:
        rmtree(folder)
    except FileNotFoundError:
        pass
    return folder


def remove_path(path):
    try:
        remove(path)
    except FileNotFoundError:
        pass
    return path


def _process_folder(source_folder, excluded_paths, process_path):
    for source_path in walk_paths(source_folder):
        if islink(source_path):
            continue
        if is_matching_path(source_path, excluded_paths or []):
            continue
        target_path = get_relative_path(source_path, source_folder)
        process_path(source_path, target_path)
