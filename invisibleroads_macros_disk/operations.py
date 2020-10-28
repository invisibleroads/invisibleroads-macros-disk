import re
import tarfile
from invisibleroads_macros_security import make_random_string
from os import makedirs, readlink, remove, unlink, walk
from os.path import exists, isdir, islink, join, splitext
from shutil import rmtree
from tempfile import mkdtemp
from zipfile import BadZipfile, ZipFile, ZipInfo, ZIP_DEFLATED

from .constants import (
    ARCHIVE_TAR_EXTENSIONS,
    ARCHIVE_ZIP_EXTENSIONS,
    IS_WINDOWS,
    TEMPORARY_FOLDER)
from .exceptions import (
    BadArchiveError,
    FileExtensionError,
    PathValidationError)
from .resolutions import (
    check_relative_path,
    get_real_path,
    get_relative_path,
    has_extension,
    has_name)


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


def compress_zip(
        source_folder,
        target_path=None,
        trusted_folders=None,
        excluded_names=None,
        with_link_purgation=True,
        with_link_expansion=False):
    'Compress folder as a zip archive'
    if not target_path:
        target_path = source_folder + ARCHIVE_ZIP_EXTENSIONS[0]
    if not has_extension(target_path, ARCHIVE_ZIP_EXTENSIONS):
        archive_extensions = ARCHIVE_ZIP_EXTENSIONS
        raise FileExtensionError({
            'target_path': 'must end in ' + ' or '.join(archive_extensions)})
    if with_link_expansion:
        source_folder = get_real_path(source_folder)

    with ZipFile(
        target_path, 'w', ZIP_DEFLATED, allowZip64=True,
    ) as target_file:

        def add(target_path, source_path):
            if islink(source_path):
                # https://learning-python.com/cgi/showcode.py?name=ziptools/ziptools/ziptools/zipsymlinks.py
                zip_info = ZipInfo(target_path)
                zip_info.create_system = 0 if IS_WINDOWS else 3
                zip_info.external_attr = 0xA1ED0000
                if isdir(source_path):
                    zip_info.external_attr |= 0x10
                target_file.writestr(zip_info, readlink(source_path))
            else:
                target_file.write(source_path, target_path)

        _process_folder(
            source_folder, trusted_folders, excluded_names,
            reject_path=lambda source_path: None,
            accept_path=add,
            with_link_purgation=with_link_purgation,
            with_link_expansion=with_link_expansion)
    return target_path


def compress_tar(
        source_folder,
        target_path=None,
        trusted_folders=None,
        excluded_names=None,
        with_link_purgation=True,
        with_link_expansion=False):
    'Compress folder as a tar archive'
    if not target_path:
        target_path = source_folder + ARCHIVE_TAR_EXTENSIONS[0]
    if not has_extension(target_path, ARCHIVE_TAR_EXTENSIONS):
        archive_extensions = ARCHIVE_TAR_EXTENSIONS
        raise FileExtensionError({
            'target_path': 'must end in ' + ' or '.join(archive_extensions)})
    if with_link_expansion:
        source_folder = get_real_path(source_folder)
    compression_format = splitext(target_path)[1].lstrip('.')
    with tarfile.open(
        target_path,
        'w:' + compression_format,
        dereference=with_link_expansion,
    ) as target_file:

        def add(target_path, source_path):
            target_file.add(source_path, target_path)

        _process_folder(
            source_folder, trusted_folders, excluded_names,
            reject_path=lambda source_path: None,
            accept_path=add,
            with_link_purgation=with_link_purgation,
            with_link_expansion=with_link_expansion)
    return target_path


def uncompress(source_path, target_folder=None, with_link_purgation=True):
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
    if with_link_purgation:
        _process_folder(
            target_folder,
            reject_path=lambda source_path: unlink(source_path),
            accept_path=lambda source_path, target_folder: None,
            with_link_purgation=with_link_purgation,
            with_link_expansion=False)
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


def _process_folder(
        source_folder,
        trusted_folders=None,
        excluded_names=None,
        reject_path=lambda source_path: None,
        accept_path=lambda source_path, target_path: None,
        with_link_purgation=True,
        with_link_expansion=False):
    for root_folder, folders, names in walk(
            source_folder, followlinks=with_link_expansion):
        for source_name in folders + names:
            if has_name(source_name, excluded_names or []):
                continue
            source_path = join(root_folder, source_name)
            if with_link_purgation:
                try:
                    target_path = check_relative_path(
                        source_path, source_folder, trusted_folders)
                except PathValidationError:
                    reject_path(source_path)
                    continue
            else:
                target_path = get_relative_path(source_path, source_folder)
            if with_link_expansion:
                source_path = get_real_path(source_path)
            accept_path(target_path, source_path)
