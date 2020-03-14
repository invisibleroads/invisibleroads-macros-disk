from os.path import abspath, expanduser, join, realpath, relpath

from .exceptions import PathValidationError


def check_absolute_path(path, parent_folder, trusted_folders=None):
    absolute_path = get_absolute_path(join(parent_folder, path))
    absolute_folder = get_absolute_path(parent_folder)

    real_path = get_real_path(absolute_path)
    real_folder = get_real_path(absolute_folder)

    for trusted_folder in trusted_folders or []:
        if real_path.startswith(get_real_path(trusted_folder)):
            break
    else:
        if relpath(real_path, real_folder).startswith('..'):
            raise PathValidationError('%s is not in %s' % (
                real_path, real_folder))

    return absolute_path


def get_absolute_path(path):
    return abspath(expanduser(path))


def get_real_path(path):
    return realpath(expanduser(path))
