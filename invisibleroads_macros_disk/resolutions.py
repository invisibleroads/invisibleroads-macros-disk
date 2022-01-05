import fnmatch
from hashlib import blake2b
from os import walk
from os.path import abspath, expanduser, join, realpath, relpath

from .constants import CHUNK_SIZE_IN_BYTES
from .exceptions import PathValidationError


def has_extension(path, extensions):
    for extension in extensions:
        if path.endswith(extension):
            return True
    return False


def is_matching_path(path, expressions):
    for expression in expressions:
        if fnmatch.fnmatch(path, expression):
            return True
    return False


def is_path_in_folder(path, folder):
    real_path = get_real_path(path)
    real_folder = get_real_path(folder)
    return real_path.startswith(real_folder)


def check_relative_path(path, folder, trusted_folders=None):
    check_path(path, folder, trusted_folders)
    return get_relative_path(path, folder)


def check_absolute_path(path, folder, trusted_folders=None):
    check_path(path, folder, trusted_folders)
    return get_absolute_path(path)


def check_path(path, folder, trusted_folders=None):
    real_path = get_real_path(path)
    for trusted_folder in trusted_folders or []:
        trusted_folder = get_real_path(trusted_folder)
        if real_path.startswith(trusted_folder):
            break
    else:
        real_folder = get_real_path(folder)
        if not real_path.startswith(real_folder):
            raise PathValidationError({
                'path': f'{real_path} is not in {real_folder}'})


def get_relative_path(path, folder):
    return relpath(expanduser(path), expanduser(folder))


def get_absolute_path(path):
    return abspath(expanduser(path))


def get_real_path(path):
    return realpath(expanduser(path))


def walk_paths(folder):
    for root_folder, folders, names in walk(folder):
        for name in folders + names:
            yield join(root_folder, name)


def get_file_hash(path, compute_hash=blake2b):
    with open(path, 'rb') as f:
        file_hash = compute_hash(usedforsecurity=False)
        while chunk := f.read(CHUNK_SIZE_IN_BYTES):
            file_hash.update(chunk)
    return file_hash.hexdigest()
