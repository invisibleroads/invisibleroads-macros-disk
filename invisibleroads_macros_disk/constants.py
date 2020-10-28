import platform
from os.path import expanduser


TEMPORARY_FOLDER = expanduser('~/.tmp')
ARCHIVE_ZIP_EXTENSIONS = '.zip',
ARCHIVE_TAR_EXTENSIONS = '.tar.gz', '.tar.bz2', '.tar.xz'
IS_WINDOWS = platform.system().lower() == 'windows'
