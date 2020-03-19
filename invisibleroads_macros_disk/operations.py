from invisibleroads_macros_security import make_random_string
from os import makedirs, remove
from os.path import expanduser, join
from shutil import rmtree
from tempfile import mkdtemp


TEMPORARY_FOLDER = expanduser('~/.tmp')


class TemporaryStorage(object):

    def __init__(self, base_folder=None):
        self.folder = make_unique_folder(base_folder or TEMPORARY_FOLDER)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        remove_folder(self.folder)


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
            pass
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
