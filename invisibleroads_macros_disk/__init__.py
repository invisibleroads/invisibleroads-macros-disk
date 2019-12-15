from os import makedirs, remove
from os.path import exists, expanduser
from shutil import rmtree
from tempfile import mkdtemp


TEMPORARY_FOLDER = expanduser('~/.tmp')


class TemporaryStorage(object):

    def __init__(self, parent_folder=None):
        self.folder = make_unique_folder(parent_folder or TEMPORARY_FOLDER)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        remove_folder(self.folder)


def make_folder(folder):
    if exists(folder):
        return
    makedirs(folder)
    return folder


def make_unique_folder(parent_folder=None):
    if parent_folder:
        make_folder(parent_folder)
    return mkdtemp(dir=parent_folder)


def remove_folder(folder):
    if exists(folder):
        rmtree(folder)
    return folder


def remove_path(path):
    if exists(path):
        remove(path)
    return path
