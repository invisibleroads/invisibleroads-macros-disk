import re
import tarfile
from invisibleroads_macros_security import make_random_string
from os import makedirs, remove
from os.path import isdir, islink, join, splitext
from shutil import rmtree
from zipfile import BadZipfile, ZipFile, ZIP_DEFLATED

from .constants import (
    ARCHIVE_TAR_EXTENSIONS,
    ARCHIVE_ZIP_EXTENSIONS,
    NAME_LENGTH,
    TEMPORARY_FOLDER)
from .exceptions import (
    BadArchiveError,
    FileExtensionError,
    InvisibleRoadsMacrosDiskError)
from .resolutions import (
    get_relative_path,
    has_extension,
    is_matching_path,
    walk_paths)


class TemporaryStorage(object):

    def __init__(
            self, base_folder=TEMPORARY_FOLDER, name_length=NAME_LENGTH,
            with_fixed_length=False):
        self.folder = make_random_folder(
            base_folder, name_length, with_fixed_length)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        remove_folder(self.folder)


def archive_safely(source_folder, target_path=None, excluded_paths=None):
    'Archive without symbolic links. Specify archive extension in target_path.'
    if not target_path:
        target_path = source_folder + ARCHIVE_ZIP_EXTENSIONS[0]
    arguments = source_folder, target_path, excluded_paths
    if has_extension(target_path, ARCHIVE_ZIP_EXTENSIONS):
        archive_zip_safely(*arguments)
    elif has_extension(target_path, ARCHIVE_TAR_EXTENSIONS):
        archive_tar_safely(*arguments)
    else:
        archive_extensions = ARCHIVE_ZIP_EXTENSIONS + ARCHIVE_TAR_EXTENSIONS
        raise FileExtensionError({
            'target_path': 'must end in ' + ' or '.join(archive_extensions)})
    return target_path


def archive_zip_safely(source_folder, target_path=None, excluded_paths=None):
    'Archive folder as a zip archive without symbolic links'
    if not target_path:
        target_path = source_folder + ARCHIVE_ZIP_EXTENSIONS[0]
    if not has_extension(target_path, ARCHIVE_ZIP_EXTENSIONS):
        archive_extensions = ARCHIVE_ZIP_EXTENSIONS
        raise FileExtensionError({
            'target_path': 'must end in ' + ' or '.join(archive_extensions)})
    with ZipFile(
        target_path, 'w', ZIP_DEFLATED, allowZip64=True,
    ) as target_file:
        _compress_folder(source_folder, excluded_paths, target_file.write)
    return target_path


def archive_tar_safely(source_folder, target_path=None, excluded_paths=None):
    'Archive folder as a tar archive without symbolic links'
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
        _compress_folder(source_folder, excluded_paths, target_file.add)
    return target_path


def unarchive_safely(source_path, target_folder=None):
    'Unarchive folder without symbolic links'
    if has_extension(source_path, ARCHIVE_ZIP_EXTENSIONS):
        try:
            source_file = ZipFile(source_path, 'r')
        except BadZipfile:
            raise BadArchiveError({'source_path': 'is unreadable'})
        extension_expression = r'\.zip$'
        items = [_ for _ in source_file.infolist() if (
            _.external_attr >> 28) != 0xA]
    elif has_extension(source_path, ARCHIVE_TAR_EXTENSIONS):
        compression_format = splitext(source_path)[1].lstrip('.')
        try:
            source_file = tarfile.open(source_path, 'r:' + compression_format)
        except tarfile.ReadError:
            raise BadArchiveError({'source_path': 'is unreadable'})
        extension_expression = r'\.tar\.%s$' % compression_format
        items = [_ for _ in source_file.getmembers() if not _.issym()]
    else:
        archive_extensions = ARCHIVE_ZIP_EXTENSIONS + ARCHIVE_TAR_EXTENSIONS
        raise FileExtensionError({
            'source_path': 'must end in ' + ' or '.join(archive_extensions)})
    if not target_folder:
        target_folder = re.sub(extension_expression, '', source_path)
    for item in items:
        source_file.extract(item, target_folder)
    source_file.close()
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


def make_random_folder(
        base_folder=TEMPORARY_FOLDER, name_length=NAME_LENGTH,
        with_fixed_length=False):
    while True:
        folder_name = make_random_string(name_length)
        folder = join(base_folder, folder_name)
        try:
            makedirs(folder)
            break
        except FileExistsError:
            if with_fixed_length:
                raise InvisibleRoadsMacrosDiskError(
                    f'could not make random folder in {base_folder}')
            name_length += 1
    return folder


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


def _compress_folder(source_folder, excluded_paths, compress_path):
    for source_path in walk_paths(source_folder):
        if isdir(source_path) or islink(source_path):
            continue
        if is_matching_path(source_path, excluded_paths or []):
            continue
        target_path = get_relative_path(source_path, source_folder)
        compress_path(source_path, target_path)


make_unique_folder = make_random_folder
