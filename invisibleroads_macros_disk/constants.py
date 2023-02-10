from platformdirs import user_cache_dir


TEMPORARY_FOLDER = user_cache_dir(
    'invisibleroads-macros-disk', 'invisibleroads')
ARCHIVE_ZIP_EXTENSIONS = '.zip',
ARCHIVE_TAR_EXTENSIONS = '.tar.gz', '.tar.bz2', '.tar.xz'


CHUNK_SIZE_IN_BYTES = 2 ** 13
NAME_LENGTH = 2 ** 4
